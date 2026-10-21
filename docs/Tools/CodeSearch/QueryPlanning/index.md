# 查询规划：解析、候选集与正则

查询规划要做的事只有一件：**把用户那句可能写错、可能带前缀、可能是正则的输入，变成一次「读尽量少的字节」的执行计划**。它决定了延迟预算能不能守住，也决定了「验真」这一步是不是在做无用功。

这一页的重点不是语法设计，而是三个执行层面的决定：候选集怎么取、验真怎么验、超时怎么收。

::: tip 一句话理解
查询执行永远是两段：**索引给候选（宁多勿少），验真给答案（宁准勿快）**。把两段合成一段，要么慢（全库扫描），要么错（候选直接当答案）。
:::

## 判据族声明

本页判据族 `CSQ-A` ~ `CSQ-H`，共 8 条。定义表在第六节。

## 本页不讲什么

- 不讲索引怎么写、n 取多少，归[索引结构](../IndexStructure/index.md)。
- 不讲候选之间怎么排序，归[结果排序](../Ranking/index.md)。
- 不讲权限怎么参与召回，归[权限过滤](../PermissionFilter/index.md)。

## 一、候选集漏斗

![从 2406 篇到 10 条：候选集漏斗](../assets/cs-candidates.svg)

实测的三次查询（本仓语料）：

| 查询 | n-gram 交集 | 验真后 | 倍数 | 总耗时 |
| --- | --- | --- | --- | --- |
| 「幂等键」 | **129** | **129** | 1.00× | **0.42 ms** |
| `idempotency` | **68** | **35** | **1.94×** | 3.13 ms |
| 「重新索引」 | **3** | **3** | 1.00× | 0.02 ms |

三个读法：

1. **候选集可能远大于答案**（`idempotency` 是 1.94 倍），因为 gram 交集只保证「都出现过」，不保证「按序相邻」。所以验真不是可选项。
2. **候选集也可能恰好等于答案**（中文 3 字查询），此时验真是纯成本——但它仍然必须做，因为同一个执行计划要服务所有查询。
3. **耗时的主要部分不是取交集，是读候选块**。`idempotency` 的取交集 + 验真共 3.13 ms，其中验真 0.34 ms（本机单次读数），数量级上的开销来自「把 35 个块读出来」。

## 二、取交集：顺序很重要

同一个查询要交多个 gram 的 posting 列表，**从最小的开始交**，代价差一个数量级：

```text
错误顺序：'的' (2309 篇) ∩ '幂等' (394 篇) ∩ ...
          → 第一步就得到 2309 个候选，后面几步都在这个集合上做
正确顺序：'幂等' (394 篇) → 再交其它
          → 第一步就只有 394 个候选
```

实测支撑：本仓 3-gram 里覆盖率最高的是 `' ##'`（2,309/2,406，**96.0%**），而 `'幂等键'` 这种串的交集只有 129。如果按词典序取交集，第一个 gram 就可能是 `' ##'`，等于把候选集定在全库。

::: danger 三个让候选集「悄悄变成全库」的写法
1. **按用户输入顺序取交集**：用户先敲 `的`，后敲 `幂等`，如果按顺序交，第一个就是高频 gram。
2. **把 `OR` 查询当成 `AND` 用同一个漏斗**：`a OR b` 的候选是并集，天然巨大；它的正确做法是「两路分别取候选，各自排序后归并」，而不是先并集再验真。
3. **前缀过滤放在验真之后**：`path:docs/Tools/` 这类过滤如果能下推到候选阶段，代价接近 0（实测本仓 192 篇 Tools 文档的前缀+关键词线性扫描只要 **0.5 ms**）；放到验真之后就变成「先读几百个块，再丢掉大部分」。
:::

## 三、验真：三件事必须在这里做完

| 事 | 为什么必须在验真做 | 本仓读数 |
| --- | --- | --- |
| 子串确认 | gram 交集是超集 | `idempotency` 68 → 35 |
| 大小写归一 | 索引里存的是归一化后的字符流 | 区分大小写查 `Outbox` **25** 篇，忽略大小写 **89** 篇（差 **72%**） |
| Unicode 归一（NFKC） | 全角/半角、兼容字符 | 本仓含全角字母数字的文档 **1** 篇；NFKC 后 token 数变化 **0.006%** |

第二行的量级值得单独说：**「默认区分大小写」会静默丢掉 72% 的召回**。用户查 `outbox` 时他想的是「这个概念」，不是「这个大小写形态」。代码搜索通常有两种模式：

| 模式 | 何时启用 | 实现 |
| --- | --- | --- |
| 不敏感（默认） | 普通关键词 | 索引侧存 `casefold()` 后的流，验真时把查询也 `casefold()` |
| 敏感（显式） | 用户勾选「区分大小写」或用了正则 | 索引侧额外存原始流，或验真时回到原文字节 |

注意 `casefold()` 而不是 `lower()`：前者对 `ß`、`İ` 这类字符的处理才是「大小写不敏感」的正确语义。本仓的全角字符极少（1 篇），但**用户的仓库里不一定**——`NFKC` 归一是廉价保险。

## 四、正则：两条路，与一条拒绝服务通道

用户想用正则时，有两条实现路线：

| 路线 | 做法 | 延迟 | 适用 |
| --- | --- | --- | --- |
| 索引预筛 + 逐候选匹配 | 从正则里抽一个字面量片段（`ERR_\d+` → `ERR_`）去取候选，再对候选跑正则 | 候选少时快 | **默认**：绝大多数正则都含字面量 |
| 纯扫描 | 直接对全库跑正则 | 5.7 ms（本仓 15 MiB） | 正则里没有可用字面量（如 `^\s*$`） |

第一条路的关键是「从正则里抽字面量」：`ERR_(\d+)` 能抽出 `ERR_`，`(foo|bar)` 只能抽出 `foo`/`bar` 两路，而 `.*` 什么都抽不出。抽不出时**必须降级到扫描**，而不是返回空（这与[索引结构](../IndexStructure/index.md)第三节里「丢弃高频 gram」的降级是同一条纪律）。

第二条纪律是**超时**。用户输入的正则是一条天然的拒绝服务通道：

```python
import re, time
t0 = time.time()
re.search(r"(a+)+b", "a" * 22 + "c")     # 灾难性回溯
print("%.1f ms" % ((time.time() - t0) * 1000))
```

实测：**396.7 ms** 只为匹配 23 个字符（20 个 `a` 时是 103.6 ms）。把 `22` 换成 `30`，这段正则会跑几分钟——而它是用户从网上抄来的一条「查找重复字母」的规则。

| 防护 | 做法 | 代价 |
| --- | --- | --- |
| 超时（必须有） | 每次匹配设置 deadline（如 100 ms），超时即中止并返回「查询太复杂」 | 需要可中断的匹配器 |
| 长度上限 | 正则长度 > 500 字符直接拒绝 | 几乎无 |
| 换引擎 | 用 RE2 / Rust `regex` 这类**线性时间**引擎（不支持反向引用与环视） | 语法子集变小，需在 UI 里说明 |
| 预编译缓存 | 同一正则编译结果缓存 | 无 |

::: warning 超时不是「优化」，是「正确性」
没有超时的正则匹配会让**单个用户的一次查询**占满一个 worker。表现是「偶尔整个搜索卡住几秒」，而监控上看不到任何异常——因为那个请求最后还成功了，只是慢。判据 `CSQ-G` 要求超时必须存在且可观测（日志里有 `timeout=true`）。
:::

## 五、截断与分页：offset 是一个陷阱

两个必须显式设计的截断点：

| 截断点 | 默认值 | 为什么必须 | 怎么暴露给用户 |
| --- | --- | --- | --- |
| 候选集上限 | 50,000 | 防止一个 `OR` 查询把内存打满 | 返回 `candidates_truncated=true` |
| 返回条数上限 | 50 / 页 | 排序成本与条数成正比 | 显示「仅显示前 50 条，共约 N 条」 |

分页不要用 `OFFSET`：`OFFSET 10000` 意味着「先算完前 10,050 条再丢掉 10,000 条」，在排序成本高的场景下会退化成秒级。正确做法是**游标**：把上一页最后一条的 `(score, doc_id, line)` 编码进游标，下一页从「严格小于该键」的位置继续。

```text
offset 分页：page_size × page_no 的排序成本
游标分页：   page_size 的排序成本（与页号无关）
```

## 六、判据表

| 判据 | 断言 | 怎么验 |
| --- | --- | --- |
| `CSQ-A` | 候选集取交集时按 posting 长度升序，不按用户输入顺序 | 读执行计划日志，第一个被求交的 gram 是该查询中 posting 最短的 |
| `CSQ-B` | 候选集与验真结果分开上报（两个数都在日志里） | 查询日志有 `candidates=N verified=M` 两个字段；随机取 10 条查询，`M ≤ N` 恒成立 |
| `CSQ-C` | 默认大小写不敏感，且敏感模式是显式开关 | 查 `outbox` 与 `Outbox` 结果集相同；勾选「区分大小写」后结果集变小 |
| `CSQ-D` | 验真只读候选块，不读全库 | 一次查询的读取字节数 ÷ 语料总字节数 < 5% |
| `CSQ-E` | 路径/语言/符号等前缀过滤下推到候选阶段 | 带 `path:` 过滤的查询，候选数显著小于不带时（同关键词对比） |
| `CSQ-F` | 候选集有上限且截断被显式标记 | 构造一个 `OR` 大查询，返回里 `candidates_truncated=true` |
| `CSQ-G` | 正则匹配有超时，且超时事件可观测 | 提交 `(a+)+b` 配 30 个 `a`，应在 100 ms 内返回「查询太复杂」而不是挂住；日志有 `timeout=true` |
| `CSQ-H` | 分页用游标而非 `OFFSET`，第 N 页成本与 N 无关 | 取第 1 页与第 100 页的耗时，差值 < 20% |

## 七、如何验证

```shell
# 1) 候选集与答案的倍数关系：决定「验真」是不是必需
python3 - <<'PY'
import os
from collections import defaultdict
docs = {}
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                docs[p] = open(p, encoding="utf-8", errors="replace").read()
idx = defaultdict(set)
for p, t in docs.items():
    s = " ".join(t.split())
    for i in range(len(s) - 2):
        idx[s[i:i + 3]].add(p)
for q in ("幂等键", "idempotency", "重新索引"):
    sets = [idx.get(q[i:i + 3], set()) for i in range(len(q) - 2)]
    cand = set.intersection(*sets) if all(sets) else set()
    hits = [p for p in cand if q in docs[p]]
    print("%-12s cand=%d hits=%d ratio=%.2f" % (q, len(cand), len(hits), len(cand) / max(1, len(hits))))
PY
# 期望：幂等键 cand=129 hits=129 ratio=1.00
#       idempotency cand=68 hits=35 ratio=1.94   ← 验真必需
#       重新索引 cand=3 hits=3 ratio=1.00
```

```shell
# 2) 大小写：默认敏感会丢多少召回
python3 - <<'PY'
import os
docs = {}
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                docs[p] = open(p, encoding="utf-8", errors="replace").read()
cs = sum(1 for t in docs.values() if "Outbox" in t)
ci = sum(1 for t in docs.values() if "outbox" in t.lower())
print("case_sensitive=%d case_insensitive=%d loss=%.0f%%" % (cs, ci, 100 * (ci - cs) / max(1, ci)))
PY
# 期望：case_sensitive=25 case_insensitive=89 loss=72%
# 判读：默认区分大小写 = 静默丢掉七成召回（CSQ-C）
```

```shell
# 3) 正则的灾难性回溯：为什么超时是必须的
python3 - <<'PY'
import re, time
for k in (18, 20, 22):
    t0 = time.time()
    re.search(r"(a+)+b", "a" * k + "c")
    print("n=%d %.1f ms" % (k, (time.time() - t0) * 1000))
PY
# 期望：n=18 25.6 ms / n=20 103.6 ms / n=22 396.7 ms（每加 2 个字符约 ×4）
# 判读：这是「用户输入」而非「代码缺陷」，只能靠 deadline 兜底（CSQ-G）
```

## 参考资料

- RE2 语法（不支持反向引用与环视，因此保证线性时间）：<https://github.com/google/re2/wiki/Syntax>
- Rust `regex` crate 的时间复杂度保证：<https://docs.rs/regex/latest/regex/#untrusted-input>
- 灾难性回溯（ReDoS）的成因与案例：<https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS>
- Unicode `casefold` 与 `lower` 的差异（`ß` / `İ`）：<https://docs.python.org/3/library/stdtypes.html#str.casefold>
- Sourcegraph 的查询语法（前缀过滤如何映射到执行计划）：<https://sourcegraph.com/docs/code-search/queries>
- 本仓相邻专题：[Elasticsearch 查询 DSL](../../../DB/NoRelational/Elasticsearch/QueryDSL/index.md) · [全文检索的性能](../../../DB/FullTextSearch/Performance/index.md)
