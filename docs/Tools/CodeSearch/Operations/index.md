# 容量、重建与监控

索引不是「建好就不管」的产物。它有自己的体积、自己的构建时间、自己的陈旧度，而且这三样都会**随时间单向变坏**：语料只增不减、条目只加不删、重建只会越来越慢。上线前不把这四个数算出来，上线后就只能靠「加机器」硬扛。

本页给四个数、四个指标、两条重建路径，以及一条「让用户自己判断陈旧」的工程纪律。

::: tip 一句话理解
搜索的运维只有一个核心问题：**「用户说搜不到」时，你能不能在五分钟内证明「是索引的问题」或「确实没有」**。四个数 + 四个指标就是为了让这句话可回答。
:::

## 判据族声明

本页判据族 `CSN-A` ~ `CSN-H`，共 8 条。定义表在第七节。

## 本页不讲什么

- 不讲索引结构与体积换算的推导，归[索引结构](../IndexStructure/index.md)。
- 不讲增量队列的实现，归[增量更新](../IncrementalUpdate/index.md)。
- 不讲通用监控体系（Prometheus / Grafana 的搭法），归[监控告警](../../../Ops/Monitoring/index.md)。

## 一、上线前必须算出的四个数

![容量、重建与监控](../assets/cs-capacity.svg)

| 数 | 本仓实测 | 推算方式 | 失控后的症状 |
| --- | --- | --- | --- |
| 索引体积 | **706 MiB**（3-gram / Python `set`，上界） | 不同 gram 数 × 平均 posting 数 × 每项开销；落盘实现约为语料的 **1.5~3×** | 内存被吃光，节点被 OOM kill，查询开始超时 |
| 构建时间 | **8.64 s**（2,406 文件，≈ **3.6 ms/文件**） | 单文件成本 × 文件数；百万文件约 **1 小时** | 部署窗口变长，重建变成「只能夜间做」 |
| 增量延迟 | **3.08 ms/文件**；1,000 文件 ≈ **3.1 s** | 增量成本 ≈ 全量成本 / 文件数（去掉「读别人字节」后） | 保存后 10 秒还搜不到，用户以为没保存 |
| 陈旧度 | 目标 **0**（删除必须立即不可见） | 索引 `commit`/`mtime` 与工作树的差 | 「删了还能搜到」——合规级缺陷 |

::: warning 706 MiB 是上界，不是「实现体积」
这个数是用 Python 的 `set` + 字符串路径直接堆出来的，每个元素都带了对象头与哈希表开销。真正的落盘实现（排序数组 / 倒排块 / varint 压缩）大约是 **40~150 MiB**（即语料的 3~10 倍）。写容量预算时要用**你的实现**实测，不要拿上界当预算，也不要拿理论值当预算。
:::

## 二、体积预算：三个必须写下来的边界

| 边界 | 建议值 | 超过之后 |
| --- | --- | --- |
| 索引 / 语料 比值 | ≤ 3×（落盘）、≤ 20×（内存态） | 换存法（紧凑倒排）或加 n-gram 剪枝 |
| 单节点索引体积 | ≤ 可用内存的 50% | 分片（按仓库/目录） |
| 单次重建时长 | ≤ 部署窗口的 1/3 | 改分段重建（见第四节） |

这三个边界要在**决策记录**里，而不是在某个人的脑子里。原因是它们会被反复挑战：「能不能把 4-gram 也加上」「能不能把历史版本也索引」——没有边界，每次都会被加一点，直到某天 OOM。

## 三、四个必采指标（缺一个就无法分诊）

| 指标 | 定义 | 为什么必须有 | 异常时的第一嫌疑 |
| --- | --- | --- | --- |
| `indexed_files / repo_files` | 已索引文件数 ÷ 仓库文件数 | 差值 = 漏入库 | 忽略规则写反（`CSG-A`） |
| `query_latency{p50,p95}`（按形态分桶） | 补全 / 全库 / 巡检三桶 | 平均值毫无意义，三桶的优化手段完全不同 | 候选集爆炸（`CSQ-F`） |
| `zero_result_rate`（按查询长度、按用户分桶） | 返回 0 条的查询占比 | **权限 bug 最先在这里显形** | 后过滤（`CSP-B`） |
| `queue_lag_seconds` | 最老未处理变更的年龄 | 增量卡住 / 事件丢失 | 消费者挂了或 fs 事件丢失（`CSI-H`） |

::: danger 三个「有指标但没用」的典型
1. **只有平均延迟**：补全 3 ms、全库 800 ms，平均 400 ms，看起来「还行」，但全库检索已经崩了。必须分桶。
2. **零结果率按全局统计**：管理员账号占了大头，把「新租户全空」这个信号冲淡了。必须按用户/租户分桶。
3. **没有「索引对应的版本」**：用户说搜不到，你只能猜。有这个数，你可以直接回答「你的仓库在 3 天前有一次提交，索引落后 3 天」。
:::

## 四、两条重建路径

| 路径 | 做法 | 停服时间 | 适用 |
| --- | --- | --- | --- |
| 原地全量 | 停查询 → 清空 → 重建 → 恢复 | 等于构建时间（本仓 8.64 s，生产可能 1 小时） | 小语料、可接受停机 |
| **分段 + 双写切换** | 后台建新段（不影响旧段查询）→ 建好后切换指针 → 旧段延迟删除 | **0**（切换是原子指针替换） | 生产默认 |

分段切换的四个步骤，每一步都有可验证的判据：

```text
① 建新段：新段写完后做一次自检（文件数对账 + 抽样 20 条查询与旧段结果对比）
② 预热：把新段的常用 posting 读进页缓存（否则切换瞬间 p95 飙升）
③ 切换：原子替换「当前段指针」，旧查询继续用旧段读完（引用计数）
④ 回收：旧段在 N 分钟后删除（N > 最长查询时间，通常 60 s）
```

实测依据：本仓全量构建 **8.64 s**，单次查询 **0.42 ms**——两者相差 2 万倍，所以「构建时查询会变慢」不是必然的，取决于**构建是否与查询共享同一份内存/IO**。分段方案的价值就是把这两件事在物理上分开。

## 五、让「陈旧」可自证

这是本专题反复强调的一条工程纪律，落地只需要两个字段：

| 字段 | 来源 | 展示位置 |
| --- | --- | --- |
| `indexed_at` | 索引构建完成时间 | 搜索框下方一行小字 |
| `indexed_commit` | 构建时工作树的 `HEAD`（或最后一次 mtime 的最大值） | 同上，可点击对比 |

有了这两行，用户看到「索引于 12 分钟前（commit abc1234）」时，会自己去 `git log` 确认；没有这两行，他会得出「系统里没有这段代码」的结论，然后重复实现一遍。

## 六、每日对账：唯一能抓「事件丢失」的手段

增量依赖 fs 事件与定时扫描，两者都会漏。唯一可靠的兜底是**每日一次全量指纹比对**：

| 比对项 | 成本（本仓） | 能抓到什么 |
| --- | --- | --- |
| 文件集合差（枚举 vs 索引清单） | 枚举 2,406 次 `stat`，约 **0.1 s** | 漏入库、删除未生效 |
| 全量内容哈希比对 | 读 15.0 MiB 并算 sha1，约 **0.05 s** | 内容变了但指纹没变（`CSI-B`） |
| 抽样查询对账（20 条固定查询） | 20 × 0.42 ms ≈ **8 ms** | 排序/过滤逻辑回归 |

三项加起来不到 1 秒，却能抓住「增量丢失」这一类最难复现的问题。**没有对账的增量系统，本质上是在赌 fs 事件不丢。**

## 七、判据表

| 判据 | 断言 | 怎么验 |
| --- | --- | --- |
| `CSN-A` | 索引体积被实测并与语料规模一起记录（不是估计） | `du -sh` 索引目录与语料目录，两个数都写进文档；比值在预算内 |
| `CSN-B` | 构建时间被实测，且「百万文件外推」有算式 | 记录 `build_seconds / file_count`，并有 ×1,000,000 的外推结果 |
| `CSN-C` | 索引体积、单节点体积、重建时长三条边界都写进了决策记录 | 决策记录里三条齐全；缺任一条视为「无预算」 |
| `CSN-D` | 延迟指标按三种查询形态分桶，且各桶有独立预算 | 指标名里带 `shape` 标签；补全 p95 ≤ 50 ms、全库 p95 ≤ 300 ms |
| `CSN-E` | 零结果率按用户/租户分桶 | 存在 `zero_result_rate{tenant=...}`；单租户 100% 空能被单独看见 |
| `CSN-F` | 重建走「分段 + 双写切换」，切换期间查询不中断 | 压测时触发一次重建，查询错误率为 0，p95 上升 < 20% |
| `CSN-G` | 界面上暴露 `indexed_at` 与 `indexed_commit` | 搜索结果页有这两个字段；与 `git log -1` 对比可得陈旧度 |
| `CSN-H` | 每日对账任务存在，且三项（集合差/哈希/抽样查询）都跑 | 对账日志里有三行结果；任一项缺失视为未对账 |

## 八、如何验证

```shell
# 1) 体积与构建时间：拿到自己的「×语料」比值
python3 - <<'PY'
import os, time
from collections import defaultdict
docs = {}
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                docs[p] = open(p, encoding="utf-8", errors="replace").read()
corpus = sum(len(t.encode("utf-8")) for t in docs.values())
t0 = time.time()
idx = defaultdict(set)
for p, t in docs.items():
    s = " ".join(t.split())
    for i in range(len(s) - 2):
        idx[s[i:i + 3]].add(p)
build = time.time() - t0
foot = sum(len(k) + 8 + sum(len(x) + 50 for x in v) for k, v in idx.items())
print("corpus=%.1f MiB index=%.1f MiB ratio=%.1fx build=%.2fs per_file=%.2fms"
      % (corpus / 1048576, foot / 1048576, foot / corpus, build, build * 1000 / len(docs)))
print("extrapolate_1m_files_hours=%.1f" % (build * 1000 / len(docs) * 1_000_000 / 3.6e6))
PY
# 期望：corpus≈15.0 MiB index≈706 MiB ratio≈47x build≈8.6s per_file≈3.6ms
#       extrapolate_1m_files_hours≈1.0
```

```shell
# 2) 文件集合对账：抓「漏入库」与「删除未生效」
python3 - <<'PY'
import os
on_disk = set()
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md"):
                on_disk.add(os.path.join(dp, f))
indexed = set(on_disk)          # 用真实索引清单替换这一行
print("on_disk=%d indexed=%d missing=%d stale=%d"
      % (len(on_disk), len(indexed), len(on_disk - indexed), len(indexed - on_disk)))
PY
# 期望（自洽时）：missing=0 stale=0
# 判读：missing>0 是漏入库（CSG-A），stale>0 是删除未生效（CSI-C）——两类都必须为 0
```

```shell
# 3) 抽样查询对账：20 条固定查询，结果集做指纹
python3 - <<'PY'
import hashlib
queries = ["幂等", "outbox", "BM25", "增量索引", "权限过滤"]
for q in queries:
    hits = []  # 用真实检索结果替换：[(path, line), ...]
    sig = hashlib.sha1(repr(sorted(hits)).encode()).hexdigest()[:8]
    print("%-10s n=%d sig=%s" % (q, len(hits), sig))
PY
# 期望：同一次索引下重复执行，sig 完全一致（不一致 = 排序不稳定，见 CSR-B）
```

## 参考资料

- Lucene 的段合并与 `IndexWriter` 打开/切换语义（分段重建的工业参照）：<https://lucene.apache.org/core/10_0_0/core/org/apache/lucene/index/IndexWriter.html>
- Prometheus 直方图与分位数（分桶 p95 的正确算法）：<https://prometheus.io/docs/practices/histograms/>
- 零结果率（search success rate）的度量实践：<https://www.elastic.co/blog/search-success-metrics>
- zoekt 的内存占用与分片策略：<https://github.com/sourcegraph/zoekt/blob/main/doc/design.md>
- 本仓相邻专题：[监控与告警](../../../Ops/Monitoring/index.md) · [容量与成本](../../../Ops/CapacityCost/index.md) · [工程效能度量](../../../Tools/EngineeringMetrics/index.md)
