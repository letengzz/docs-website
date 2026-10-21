# 增量更新与索引一致性

增量更新最容易被当成一个性能问题：「全量太慢，所以做增量」。但它真正的难点是**正确性**：你怎么知道「这个文件没变」？你怎么知道「这个文件已经没了」？这两个问题的答案如果错了，索引不会报错，只会**静默地少一点东西**——而搜索的信任度就是从这一点点缺失开始崩的。

本页把增量拆成三种状态：全量、真增量、伪增量，并用本仓实测把「伪增量」的漏检方式钉死。

::: tip 一句话理解
增量的判据不是「快了多少倍」，而是「**改动之后，索引与工作树在多少秒内一致，且这个一致是可证明的**」。做不到第二条，就老老实实全量。
:::

## 判据族声明

本页判据族 `CSI-A` ~ `CSI-H`，共 8 条。定义表在第六节。

## 本页不讲什么

- 不讲 n-gram 的具体结构与体积，归[索引结构](../IndexStructure/index.md)。
- 不讲分块边界与坐标维护，归[入库与解析](../IngestPipeline/index.md)。
- 不讲重建、双写切换与容量，归[容量与运维](../Operations/index.md)。

## 一、三种状态：全量、真增量、伪增量

![增量的三种状态：全量、增量、以及漏检](../assets/cs-incremental.svg)

| 状态 | 判定依据 | 本仓实测成本 | 正确性 | 适用 |
| --- | --- | --- | --- | --- |
| 全量重建 | 无（每次都重扫） | **7.41~8.64 s / 2,406 文件** | 一定正确 | 夜间对账、结构变更后 |
| 真增量 | **内容哈希**（sha1/sha256） | **136.49 ms / 单文件**（87,340 B）；平均 **3.08 ms/文件** | 正确（下界是读字节的 I/O） | 保存即刷新 |
| 伪增量 | `mtime + size` | 通常 < 1 ms | **会漏检** | 只适合「大文件、低频改动」的场景，且必须配兜底 |

两条读法：

1. **全量与增量的差距是 54 倍**（8.64 s vs 136.49 ms），但这个对比是拿「最大的单篇」做的。按**平均**算，单文件 3.08 ms，1,000 个文件变更约 **3.1 s**——也就是说，**批量变更时增量并不比全量快多少**，它省的是「读别人字节」这件事，不是「读自己字节」。
2. **增量的下界是 I/O**：要判断内容有没有变，最可靠的办法是读一遍字节算哈希。任何「不读字节就判断没变」的方案，都是在赌文件系统给的元数据，而元数据可以被完美伪造。

## 二、伪增量为什么一定会漏：三种常见伪造

`mtime + size` 的假设是「内容变了，mtime 就会变」。这个假设在下面三种情况下**同时失效**：

| 场景 | 命令/操作 | size | mtime | 结果 |
| --- | --- | --- | --- | --- |
| 回滚到旧版本 | `git checkout -- file` | 可能相同 | **被 git 设为提交时间或当前时间**，但若原文件 mtime 恰好相同（同一秒内）则无变化 | 漏检 |
| 保留时间戳复制 | `cp -p` / `rsync -t` / `tar -x`（默认保留 mtime） | 可能相同 | **被显式还原** | **必漏** |
| 同长度改写 | 把「的」替换成「与」、把 `1` 改成 `2` | **完全相同** | 通常变，但若在同一秒内完成且文件系统时间精度是 1 s | 可能漏 |

本机实测的第三条最直观：取一篇 3,005 字节的文档，把其中一个「的」换成「与」——**字节数仍是 3,005，但 sha1 变了**。如果指纹是 `(size, mtime)`，这次改动在「同一秒内完成」的前提下就会被判为「没变」。

::: danger 三种「以为改了其实没改」的现场
1. **编辑器的「保存」写临时文件再 rename**：`mtime` 会更新，这条没问题；但**某些 IDE 的自动保存在文件未变更时不写盘**，于是你以为的「刚保存」其实什么都没发生——这不是索引的错，但用户会把账算在搜索上。处置：索引侧必须能报「最后一次索引时间」，让用户自己判断。
2. **`git checkout` 到另一个分支**：批量替换文件，size 与 mtime 都可能与旧值相同（尤其是 `git` 的 `core.checkStat` 配置下）。处置：把 `HEAD` 的 commit id 也纳入「是否需要全量」的判断。
3. **网络文件系统（NFS / SMB）的时间精度**：通常是 **1 秒**甚至 **2 秒**。同一秒内的两次修改，`mtime` 完全一样。处置：`mtime` 只作为「快速排除」的第一道，**不能作为最终判据**。
:::

正确的做法是**两级判定**：

```python
# 两级判定：先用元数据快速排除，再用内容哈希确认
import hashlib
import os

def needs_reindex(path, prev):
    """prev: {"size": int, "mtime_ns": int, "sha1": str} 或 None"""
    if prev is None:
        return True
    st = os.stat(path)
    # 第一级：元数据不同 → 一定需要重算
    if st.st_size != prev["size"] or st.st_mtime_ns != prev["mtime_ns"]:
        return True
    # 第二级：元数据相同 → 仍需哈希确认（成本是读一遍字节）
    h = hashlib.sha1(open(path, "rb").read()).hexdigest()
    return h != prev["sha1"]
```

第二级看起来「白读一遍」，但它把漏检概率从「取决于文件系统与工具」降到 **0**。如果你要省掉它，就必须接受「搜不到昨天改的那句」这个 bug 会周期性地出现，且**无法复现**。

## 三、删除与重命名：索引不知道文件没了

这是比漏检更严重的一类：**索引里存在一个工作树里已经不存在的文档**。

实测：删掉一篇文档后，它在 3-gram 索引里仍占 **4,614 组 posting**（即 4,614 个不同的 gram 的 posting 列表里都有它）。查询这些 gram 时，它照旧出现在结果里，点进去是 404。

| 操作 | 朴素实现的行为 | 后果 |
| --- | --- | --- |
| 删除文件 | 只从「文件清单」里删 | 孤儿 posting 永久残留，查询返回死链 |
| 重命名 | 视为「删除 + 新增」但只做了新增 | 新旧路径**同时**命中，用户点旧路径 404 |
| 移动目录 | 同上 | 一整批孤儿 |

三种处置，按可靠性排序：

1. **墓碑 + 定期压缩（推荐）**：删除时只写一条 `deleted(doc_id, ts)` 记录；查询出口按 `doc_id` 反查存活表，命中墓碑就丢弃；压缩任务定期把墓碑对应的 posting 真正清掉。优点是删除是 O(1)，查询侧只多一次内存查表。
2. **写时复制整段**：删除时重建受影响的段。代价与段大小成正比，适合小段。
3. **查询时校验文件存在**：最省事，但每个候选都要 `stat` 一次，候选多时会把延迟打回线性扫描的水平（判据 `CSI-G` 明确禁止在热路径上这么做）。

::: warning 「删除可见性」不是显示问题，是数据问题
在企业环境里，「删掉的文档还能被搜到」等于**数据没有被真正删除**。合规审计问的是「删除请求后多久不再可检索」，答案必须是「立即」（墓碑在写入路径上同步生效），而不是「等下次重建」。
:::

## 四、一致性的三种语义，选一种并写下来

「索引与工作树一致」这句话必须先定义清楚是哪一种：

| 语义 | 含义 | 实现代价 | 适用 |
| --- | --- | --- | --- |
| **最终一致** | 变更后 N 秒内（或下一次重建后）一致 | 最低 | 夜间构建的仓库搜索 |
| **读己之写** | 用户自己刚改的内容，他自己的下一次查询一定能看到 | 中（写入时触发该文件的增量） | 编辑器内搜索、知识库 |
| **强一致** | 任何查询都反映写入瞬间的状态 | 高（需要事务或版本号） | 几乎不适用于搜索 |

本仓的实战取「读己之写」：保存文件 → 触发该文件的增量（3.08 ms 量级）→ 下一次查询必中。这条语义可以用一个判据把它变成可测的：

```text
写入一份新文档（含唯一标记串）→ 立即查询该标记 → 必须命中，且命中位置的行号正确
```

## 五、增量队列：把「要不要重建」变成一个可以观测的队列

工程上最稳的结构不是「保存时同步重建」，而是**变更队列 + 单消费者**：

| 组件 | 职责 | 关键点 |
| --- | --- | --- |
| 变更探测 | 定时扫 mtime / 监听 fs 事件 | fs 事件会丢（inotify 队列溢出、macOS FSEvents 合并），必须配定时补偿扫描 |
| 队列 | 存 `(path, op)` | 同路径多次变更要合并（否则一次保存触发 30 次重建） |
| 消费者 | 串行重建单文件 posting | 串行保证同一文件的删旧写新不交错 |
| 对账 | 每日一次全量指纹比对 | 抓「事件丢了」与「哈希冲突」这两类残余 |

实测支撑：单文件 136.49 ms 的重建成本，意味着**消费者串行也能跟上人手的编辑速度**（一个人不可能每秒保存 7 次以上）。但如果队列里堆了 1,000 个文件，串行要 3.1 s——这时的正确做法不是并行，而是**合并成一次小批量重建**。

## 六、判据表

| 判据 | 断言 | 怎么验 |
| --- | --- | --- |
| `CSI-A` | 索引的变更判定包含内容哈希，不是只有 `mtime+size` | 读索引器的 `needs_reindex` 实现，存在哈希比较分支；或用一个「改内容 + 还原 mtime」的文件实测能检出 |
| `CSI-B` | 「改一个字符、字节数不变、mtime 还原」的场景能被检出 | 造 3,005 B 文件 → 改一个汉字 → `touch -r` 还原 mtime → 触发增量，索引内容应更新 |
| `CSI-C` | 删除文件后，该文件不再出现在任何查询结果里（墓碑同步生效） | 删一篇文档 → 立刻查它独有的句子 → 0 命中；再查它独有的长串 → 0 命中 |
| `CSI-D` | 重命名后旧路径不再命中、新路径命中 | `git mv a.md b.md` → 用旧路径前缀过滤查询 → 0 命中；用新路径 → 命中 |
| `CSI-E` | 一致性语义被显式写下来（最终一致 / 读己之写 / 强一致），且与实测相符 | 文档里有语义声明；按该语义写的验收用例全绿 |
| `CSI-F` | 有墓碑压缩机制，且压缩前后查询结果集完全一致 | 压缩前后各跑同一组 20 个查询，结果集（路径+行号）逐项相同 |
| `CSI-G` | 查询热路径上不做逐候选的文件存在性检查 | 抓一次查询的系统调用，`stat` 次数 < 候选数的 10% |
| `CSI-H` | 增量队列有积压指标，且能报出「最老未处理变更的年龄」 | 指标里存在 `queue_lag_seconds`；人为塞 500 个变更，该指标应上升并能回落到 0 |

## 七、如何验证

```shell
# 1) 全量 vs 单文件增量：拿到自己的 54× 这个数
python3 - <<'PY'
import os, re, time
from collections import defaultdict
docs = {}
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                docs[p] = open(p, encoding="utf-8", errors="replace").read()

def build():
    idx, t0 = defaultdict(set), time.time()
    for p, t in docs.items():
        s = " ".join(t.split())
        for i in range(len(s) - 2):
            idx[s[i:i + 3]].add(p)
    return idx, time.time() - t0

idx, full = build()
p0 = max(docs, key=lambda p: len(docs[p]))
t0 = time.time()
for g in [k for k, v in idx.items() if p0 in v]:
    idx[g].discard(p0)
s = " ".join((docs[p0] + " 追加一段测试文本").split())
for i in range(len(s) - 2):
    idx[s[i:i + 3]].add(p0)
inc = (time.time() - t0) * 1000
print("full=%.2fs inc_single=%.2fms file_bytes=%d ratio=%.0fx"
      % (full, inc, len(docs[p0]), full * 1000 / inc))
print("per_file_ms=%.2f thousand_files_s=%.1f" % (full * 1000 / len(docs), full * 1000 / len(docs)))
PY
# 期望：full≈7.4~8.6s inc_single≈136ms file_bytes=87340 ratio≈54x
#       per_file_ms≈3.1 thousand_files_s≈3.1
```

```shell
# 2) 「字节数不变但内容变了」：mtime+size 指纹的漏检点
python3 - <<'PY'
import hashlib
a = "这是一段用于测试的文本，包含几个常见汉字。".encode("utf-8")
b = a.replace("的".encode("utf-8"), "与".encode("utf-8"))
print("size_a=%d size_b=%d size_same=%s sha_changed=%s"
      % (len(a), len(b), len(a) == len(b), hashlib.sha1(a).hexdigest() != hashlib.sha1(b).hexdigest()))
PY
# 期望：size_a=size_b=... size_same=True sha_changed=True
# 判读：(size, mtime) 相同不代表内容相同 —— 这就是 CSI-B 要堵的洞
```

```shell
# 3) 删除后的孤儿 posting：数一数有多少组还指着它
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
victim = next(p for p in docs if p.endswith("index.md"))
before = sum(1 for v in idx.values() if victim in v)
del docs[victim]
after = sum(1 for v in idx.values() if victim in v)
print("victim=%s postings_before=%d postings_after=%d" % (victim, before, after))
PY
# 期望：postings_before=postings_after（数百~数千组，取决于文件大小）
# 判读：删了文件索引完全不知道 —— 必须靠墓碑 + 反查存活表（CSI-C）
```

## 参考资料

- `stat` 的 `st_mtime_ns` 精度与各文件系统的实际分辨率（NFS 通常 1 s）：<https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/sys_stat.h.html>
- `git` 的 `core.checkStat` / `core.trustctime`（为什么 checkout 后 mtime 不可靠）：<https://git-scm.com/docs/git-config#Documentation/git-config.txt-corecheckStat>
- `cp -p` / `rsync -t` 的时间戳保留语义：<https://download.samba.org/pub/rsync/rsync.1>
- inotify 的队列溢出与事件丢失（`IN_Q_OVERFLOW`）：<https://man7.org/linux/man-pages/man7/inotify.7.html>
- FSEvents 的事件合并行为（macOS）：<https://developer.apple.com/documentation/coreservices/file_system_events>
- zoekt 的增量索引与删除处理：<https://github.com/sourcegraph/zoekt/blob/main/doc/design.md>
- 本仓相邻专题：[全文检索的索引更新](../../../DB/FullTextSearch/IndexUpdate/index.md) · [缓存与索引的一致性](../../../Backend/DistributedCache/index.md)
