# 常见问题与最佳实践

这一页收集的是「动手时真的会卡住」的十二个问题。每个问题给结论、给量级、给判据编号，不给模棱两可的建议。

::: tip 一句话理解
这一页的所有答案都可以用同一把尺子检验：**「这个决定会不会让某些查询静默地搜不到？」** 会，就要有判据；不会，就随便。
:::

## 判据族声明

本页判据族 `CSF-A` ~ `CSF-H`，共 8 条。定义表在第八节。

## 一、语料规模：15 MiB 到底要不要上索引

**结论：不要。** 实测本仓 15.0 MiB / 2,406 篇，全库线性扫描找「幂等」只要 **5.7 ms**。任何索引的维护成本（构建 8.64 s + 增量 + 删除一致性 + 权限）都比这 5.7 ms 贵。

分界线不在「多少 MB」，而在**四个需求**中出现了几个：

| 需求 | 只有这一个 | 两个以上 |
| --- | --- | --- |
| 补全（每键 ≤ 50 ms） | 小语料扫描也能做到 | 需要索引 |
| 相关性排序 | 做不到（没有全局 idf） | 需要索引 |
| 权限过滤 | 逐文档判断，扫描更简单 | 需要索引 |
| 跨仓 / 跨分支 / 跨历史 | `git grep` 够用 | 需要索引 |

判据 `CSF-A`：决策记录里必须写出「语料规模 + 命中的需求条目数」，缺任一项视为凭感觉。

## 二、为什么不直接用 FTS5 / Elasticsearch

可以，而且大多数情况应该用。它们解决不了的是**三件很小但很硬的事**：

| 需求 | FTS5 | Elasticsearch | 自建 n-gram |
| --- | --- | --- | --- |
| 中文不分词、任意子串 | 需 `trigram` tokenizer（3.34+） | 需自定义 analyzer | 天然支持 |
| `文件:行:列` 精确坐标 | 支持（`offsets` 需开启） | 支持（`offsets` 需 `term_vector`） | 天然支持 |
| 单文件 3 ms 级增量 | 支持（行级） | 刷新间隔内不实时（默认 1 s） | 天然支持 |
| 索引体积可控（3× 语料内） | 支持 | 较难（段合并 + 副本） | 需自己实现压缩 |

**建议**：先用 FTS5 的 `trigram` tokenizer 做原型（一条 SQL 就能查子串），只有在「体积/延迟/权限」三项里至少一项不达标时才自建。判据 `CSF-B`。

## 三、中文为什么不能分词

因为**代码与中文技术文档里的「词」不是自然语言词**。实测本仓：用 `split()` 分词后，查「幂等」只命中 **41** 篇，而子串匹配命中 **394** 篇——**召回少 89.6%**。

原因：本仓 344,347 个含中文的 token **平均 16.8 字符、最长 512 字符**，词表里绝大多数条目是「一整句话」。分词器再准也没用，因为你分的是「句子」。

| 方案 | 召回 | 体积 | 建议 |
| --- | --- | --- | --- |
| 空白分词 | 41/394 | 最小 | **不要用** |
| 中文分词器（jieba 等） | 视词表而定，「幂等键」可能被切成「幂等/键」 | 中 | 可以，但要处理未登录词（`OutboxPublisher`） |
| 2-gram + 3-gram | **394/394** | 大（实测 431/706 MiB） | **默认** |
| 子串扫描 | 394/394 | 0 | 小语料首选 |

## 四、索引体积 47× 语料，正常吗

**不正常，但可解释。** 706 MiB 是 Python `set` 的口径（每个元素带对象头 + 哈希表），是**上界**。落盘实现通常 **1.5~3×** 语料（本仓约 25~45 MiB）。

| 存法 | 每 (gram, doc) 对开销 | 15 MiB 语料估算 |
| --- | --- | --- |
| Python `set` | ~250 B | **706 MiB**（实测） |
| 平铺 `array('I')` + 偏移 | 4 B | ~110 MiB |
| 倒排块 + varint | 1~2 B | ~40~70 MiB |

判据 `CSF-C`：容量预算必须用**你的实现**实测，而不是引用别人的数字。

## 五、删了还能搜到，怎么修

三层，缺一不可：

1. **写入侧**：删除时同步写墓碑 `deleted(doc_id, ts)`（毫秒级）。
2. **查询侧**：结果出口按 `doc_id` 反查存活表，命中墓碑即丢弃。
3. **后台**：定期压缩，把墓碑对应的 posting 真正清掉。

实测：一篇文档在 3-gram 索引里占 **4,614 组** posting，靠「重建」让删除生效意味着在这 8.64 s（生产可能几十分钟）里它一直可搜。判据 `CSF-D`。

## 六、加了向量检索，精确查询反而变差

因为融合把精确命中稀释了。RRF 只看名次：词法只有 1 条结果（rank 1，1/61），语义有 50 条（rank 1 也是 1/61），两者并列。

修法是**两段式**：完全匹配先置顶并标记 `exact`，剩余位置再融合。另外，命中「标识符特征」的查询（`ERR_`、`_`、全大写、点号）应直接把语义权重设为 0。

判据 `CSF-E`；详见[语义检索与混合排序](../SemanticSearch/index.md)第四节。

## 七、大小写：默认敏感还是不敏感

**默认不敏感。** 实测查 `Outbox` 区分大小写命中 **25** 篇，忽略大小写 **89** 篇——差 **72%**。用户查 `outbox` 时想的是概念，不是大小写形态。

实现上用 `casefold()` 而不是 `lower()`（`ß`、`İ` 的处理不同）。需要精确匹配时（正则、`区分大小写` 开关）再走原始流。判据 `CSF-F`。

## 八、多仓库 / 多分支怎么索引

| 维度 | 方案 | 代价 |
| --- | --- | --- |
| 多仓库 | 每仓一个段，查询时按 `repo:` 过滤；跨仓查询合并 top-k | 归并阶段的兜底排序必须重做（见[排序](../Ranking/index.md)第四节） |
| 多分支 | **只索引默认分支 + 当前分支**，其余按需构建 | 分支数 × 体积；「按需」意味着首次查询慢 |
| 全历史 | 单独建「历史索引」（`git log -p` 的产物），与工作树索引分开 | 体积是工作树的 5~20 倍；只能按 commit 查询 |

一条纪律：**不同维度的语料不要混在同一个 posting 列表里**。混了之后，任何「只看某个分支」的查询都要靠后过滤，而后果与权限后过滤一样——结果变空。

## 九、为什么第一页全是同一篇文档

因为没有做「按文档聚合」。本仓 p99 单篇 **27,022 B**、最大 **87,340 B**，一篇长文命中同一关键词几十次，排序后自然霸屏。

处置：同一 `doc_id` 在同一页最多 N 条（建议 3），其余折叠为「该文档还有 47 处命中」。判据 `CSR-E`。

## 十、索引落后多久算正常

取决于一致性语义，必须写下来：

| 语义 | 正常落后 | 怎么自证 |
| --- | --- | --- |
| 最终一致 | 一个构建周期（如 1 小时） | 界面显示 `indexed_at` |
| 读己之写 | 保存后 ≤ 2 s | 保存后立刻查询能命中 |
| 强一致 | 0（搜索不适用） | —— |

「落后」本身不是缺陷，**不可见**才是。判据 `CSF-G`。

## 十一、能不能用 `git` 历史做搜索

可以，但要接受三个代价：体积（工作树的 5~20 倍）、构建时间（按 commit 展开，不是按文件）、以及「删除的文件依然存在」——历史索引里它们**应该**存在，所以墓碑机制在那一边不适用，要换成「按 commit 过滤」。

实践建议：历史检索用 `git log -S` / `git grep <commit>` 就够，除非你要做「跨 5 年、跨 20 个仓库的考古」。判据 `CSF-H`。

## 十二、候选 68 却只命中 35，是 bug 吗

不是，是 n-gram 的固有性质：gram 交集只保证「都出现过」，不保证「按序相邻」。`idempotency` 的 9 个 gram 可以分散在 `idempotent` 与 `encryption` 里，各自命中不同位置。

所以**验真不是可选项**。反过来，如果候选 129、命中 129（如「幂等键」），说明 gram 覆盖了整个查询——这是最好的情况，不是巧合。

## 十三、判据表

| 判据 | 断言 | 怎么验 |
| --- | --- | --- |
| `CSF-A` | 是否上索引有书面依据：语料规模 + 命中的需求条目数 | 决策记录含「2,406 篇 / 15.0 MiB」与四个需求中命中的项数 |
| `CSF-B` | 选型对比里包含「为什么不用现成方案」 | 有 FTS5 / ES / 自建三方对比表，且写清体积、坐标、增量三项读数 |
| `CSF-C` | 容量预算用的是自己实现的实测值 | 预算里的体积数是本项目 `du -sh` 出来的，不是引用值 |
| `CSF-D` | 删除有三层（墓碑/反查/压缩）且立即不可见 | 删文件后立即查询 0 命中；压缩前后结果集一致 |
| `CSF-E` | 精确命中置顶，语义不稀释 it | 查标识符时首条结果含该串；开关语义后首条不变 |
| `CSF-F` | 默认大小写不敏感，敏感是显式开关 | `outbox` 与 `Outbox` 结果同；勾选后不同 |
| `CSF-G` | 一致性语义被写下，且界面上有 `indexed_at` | 文档有语义声明；界面有索引时间 |
| `CSF-H` | 历史检索与工作树检索分开（不混在同一 posting 列表） | 两套索引目录/前缀独立；跨维查询靠合并而非过滤 |

## 十四、如何验证

```shell
# 1) 十二问里最常被踩的两条：分词召回、大小写召回
python3 - <<'PY'
import os
docs = {}
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                docs[p] = open(p, encoding="utf-8", errors="replace").read()
q = "幂等"
print("ws=%d sub=%d" % (sum(1 for t in docs.values() if q in t.split()),
                       sum(1 for t in docs.values() if q in t)))
print("case_sensitive=%d case_insensitive=%d"
      % (sum(1 for t in docs.values() if "Outbox" in t),
         sum(1 for t in docs.values() if "outbox" in t.lower())))
PY
# 期望：ws=41 sub=394 / case_sensitive=25 case_insensitive=89
```

```shell
# 2) 现成方案够不够用：FTS5 trigram 一条 SQL 验证子串能力
python3 - <<'PY'
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("create virtual table t using fts5(body, tokenize='trigram')")
con.execute("insert into t values ('outbox 与 OutboxPublisher 的关系')")
for q in ("boxPub", "outbox", "BOX", "关系"):
    n = con.execute("select count(*) from t where t match ?", (q,)).fetchone()[0]
    print("MATCH %-8s hits=%d" % (q, n))
print("LIKE  %-8s hits=%d" % ("关系", con.execute(
    "select count(*) from t where body like '%关系%'").fetchone()[0]))
PY
# 期望：MATCH boxPub=1 / outbox=1 / BOX=1 / 关系=0
#       LIKE  关系=1
# 判读：trigram MATCH 要求查询 ≥ 3 字符，两字中文词会返回 0（不是没收录）；
#       这类查询必须走 LIKE / GLOB（FTS5 trigram 让它们也走索引）——CSX-G 的由来
```

```shell
# 3) 删除可见性：墓碑生效的最小复现（用文件存在性模拟墓碑）
python3 - <<'PY'
import os
files = {p for base in ("docs", "project") for dp, _, fs in os.walk(base)
         for f in fs if f.endswith(".md") for p in [os.path.join(dp, f)]}
target = sorted(files)[0]
alive = lambda p: os.path.exists(p)          # 墓碑 = 不存在
print("before=%s" % alive(target))
os.rename(target, target + ".bak")           # 模拟删除
print("after=%s（查询出口按 alive() 过滤，即不会返回）" % alive(target))
os.rename(target + ".bak", target)
PY
# 期望：before=True / after=False
# 判读：删除可见性的实现成本只有一次 exists/内存查表；不做是设计缺失，不是性能问题（CSF-D）
```

## 参考资料

- SQLite FTS5 `trigram` tokenizer 的能力与限制：<https://sqlite.org/fts5.html#the_trigram_tokenizer>
- Elasticsearch 的 `index.refresh_interval`（为什么「写完不能立刻搜到」）：<https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html>
- `git log -S` / `-G`（历史检索的两种语义）：<https://git-scm.com/docs/git-log#Documentation/git-log.txt--Sltstringgt>
- Unicode `casefold` 与语言相关的特殊折叠：<https://www.unicode.org/Public/UCD/latest/ucd/CaseFolding.txt>
- 本仓相邻专题：[全文检索系统](../../../DB/FullTextSearch/index.md) · [Git 与版本控制](../../../Tools/VersionControl/Git/index.md) · [IDE 与编辑器](../../../Tools/IDE/Overview/index.md)
