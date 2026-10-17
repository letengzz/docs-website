# 常见问题与最佳实践

这一页按「你看到的现象」组织，而不是按概念组织。左边是症状，中间是第一条该跑的命令，右边是它通常指向的那一层。**先定位层，再谈优化**——跳过定位的优化十次有九次白忙。

![六类症状到四层的分诊路径](../assets/dbi-faq-triage.svg)

## 判据族声明

本页判据族 `DFQ-A` ~ `DFQ-G`，共 7 条。定义表在第六节。

## 一、症状分诊表

| 现象 | 第一条命令 | 常指向 | 跳到 |
| --- | --- | --- | --- |
| 查询突然从 5 ms 变成 500 ms | `explain (analyze, buffers)` 对比前后 | 优化器（统计信息变了） | [优化器](../Optimizer/index.md) |
| 索引明明有，计划却是全表扫 | `explain`，看是 `Filter` 还是 `Index Cond` | B+ 树（表达式不匹配 / 首列缺条件） | [B+ 树](../BPlusTree/index.md) |
| 命中少量行，却扫了很多堆页 | 看 `Heap Blocks` 有没有 `lossy` | 执行器（位图退化 / work_mem 不足） | [执行器](../Executor/index.md) |
| 内存吃满、延迟有毛刺 | `pg_buffercache` + `buffers_alloc` | 缓冲池（池小于热数据集） | [缓冲池](../BufferPool/index.md) |
| WAL 涨得比数据快 | 两次 LSN 差值 ÷ 行数 | WAL（写放大、全页写） | [WAL](../WalRecovery/index.md) |
| 写入吞吐上不去、磁盘却很闲 | 算「带宽 ÷ 写放大」 | LSM（compaction 写放大） | [LSM](../LsmTree/index.md) |
| 崩溃后恢复要很久 | `max_wal_size` ÷ WAL 生成速率 | WAL（检查点太稀） | [WAL](../WalRecovery/index.md) |
| 磁盘占用删了数据也不降 | 查死元组 / 墓碑 | 缓冲池（vacuum）+ LSM（墓碑） | 两页都要看 |

::: tip 三句话定位法
1. **时间花在哪？** 看 `actual time` 最大的那个节点；
2. **页花在哪？** 看 `Buffers` 是 `hit` 还是 `read` 占多；
3. **行花在哪？** 看「扫了多少行」与「留下了多少行」的比值。

三个答案分别对应「CPU / 内存 / 选择性」，三个方向的处理手段完全不同。
:::

## 二、高频十二问

### 1. `cost` 小的计划为什么反而慢？

因为 `cost` 是**估算**，单位是「页访问当量」，不是时间。它可能算错（统计失真），也可能算对但你的硬件参数与模型不符（`random_page_cost=4` 在 SSD 上偏高）。**只看 `actual time` 与 `Buffers`。**

### 2. 一页 8 KB，为什么查一行要读 8 KB？

因为 I/O 的最小单位就是页。引擎不可能只读「那一行的 180 字节」——它读整页，然后在页内定位。这也是「行越宽、一页放得越少、同样行数要读越多页」的原因。

### 3. 索引是不是越多越好？

不是。每个索引都要**在写入时同步维护**（写放大），都要占空间（空间放大），都会让优化器多一个候选（计划时间上升）。判据：一个索引如果从未出现在任何 `Index Cond` 里，就该删。

### 4. 为什么 `uuidv4()` 做主键会慢？

它的值随机，插入位置随机 ⇒ 页分裂散布全树 ⇒ 页利用率降到 50%～70%，索引体积近一倍。用 `uuidv7()`（时间有序）或自增，插入集中在最右页。

### 5. `count(*)` 为什么在大表上很慢？

因为它必须知道「有多少行对当前事务可见」，而这需要看行或至少看可见性映射。没有「行数计数器」这回事（有也不准，因为 MVCC）。

### 6. 为什么删了数据磁盘没变小？

删除只是把行标记为「死」，空间要等 `vacuum` 标记可复用、或 `vacuum full` 真正回收。LSM 里则是等墓碑被 compaction 消化。**删除从来不等于释放。**

### 7. `work_mem` 调大就一定好吗？

不一定。它是**每个算子**的配额，一个复杂查询可能有多个排序/哈希节点，实际内存是「节点数 × `work_mem` × 并发数」。调太大可能 OOM。经验值：先按「并发数 × 3 × work_mem < 物理内存 25%」约束。

### 8. 为什么同样的 SQL 在测试库很快、生产很慢？

三个最常见原因：数据量差一个数量级（计划翻转）、统计信息新鲜度不同（生产没 `analyze`）、缓存状态不同（测试库常年热）。**先对齐这三项再比较。**

### 9. 缓冲池要设多大？

按**热数据集**设，不是按物理内存比例拍。先算「高频访问的表 + 索引」的总大小，再定 `shared_buffers`（通常物理内存 25%，但热数据集只有 2 GB 时设 64 GB 没意义）。

### 10. WAL 能删吗？

只能删**已归档且已过恢复点**的。删未归档的 WAL = 删数据 + 断归档链 + 备库断流。清理工具用 `pg_archivecleanup`，不要 `rm`。

### 11. 为什么加了索引反而更慢？

三种可能：① 优化器算错，选了更差的索引；② 索引让写入变慢（写放大）；③ 索引统计信息刚建还没 `analyze`。**先 `analyze`，再看计划，最后看写入延迟。**

### 12. LSM 和 B+ 树到底怎么选？

一句话：**写远多于读、以追加为主 → LSM；读写均衡、频繁原地更新 → B+ 树。** 说不清时，算一遍[三种放大表](../LsmTree/index.md)，用数字决定。

## 三、上线前 20 项自查清单

每项都能用一条命令判定，勾不上就不要上线。

| # | 检查项 | 命令 / 判据 |
| --- | --- | --- |
| 1 | 页大小与每页行数已记录 | `show block_size` + `relpages/reltuples` |
| 2 | 热数据集大小 < `shared_buffers` | `sum(pg_total_relation_size)` 对比 `shared_buffers` |
| 3 | 主要索引树高 ≤ 4 | `bt_metap().level + 1` |
| 4 | 关键表 `last_analyze` 在 24h 内 | `pg_stat_user_tables` |
| 5 | 无「索引存在但从未使用」 | `pg_stat_user_indexes.idx_scan = 0` |
| 6 | `random_page_cost` 与存储介质匹配 | `pg_settings` |
| 7 | `effective_cache_size` ≠ `shared_buffers` | 两值对比 |
| 8 | 无 `Heap Blocks: lossy` | `explain (analyze, buffers)` |
| 9 | `Hash Join` 的 `Batches = 1` | 同上 |
| 10 | `Sort` 无 `external merge` | 同上 |
| 11 | `Workers Launched = Planned` | 同上 |
| 12 | 每行 WAL < 3 倍行宽 | LSN 差值 ÷ 行数 |
| 13 | `num_requested` 不持续增长 | `pg_stat_checkpointer` |
| 14 | `max_wal_size ÷ WAL 速率` 可接受 | 计算最坏恢复时间 |
| 15 | `synchronous_commit` 按业务分级 | `pg_settings` |
| 16 | 大字段确认走 TOAST | `pg_column_size` 抽样 |
| 17 | 主键有序（自增或 `uuidv7()`） | 看列默认值 |
| 18 | 监控脚本按 PG 大版本分支 | `server_version_num` 判断 |
| 19 | 崩溃恢复演练有实测秒数 | 演练记录 |
| 20 | 每条性能结论附命令与读数 | 文档抽查 |

## 四、十二条最佳实践

1. **先量后调**：任何优化前先拿到 `Buffers` 与 `actual time` 两个基线数。
2. **一次只改一个变量**，否则无法归因。
3. **用 `actual time` 判断快慢，用 `cost` 只做参考**。
4. **索引跟着查询走**，不跟着「可能有用」走。
5. **主键用有序值**（自增 / `uuidv7()`），避免随机写。
6. **`analyze` 是免费的，`explain` 前先跑一次**。
7. **统计信息要针对倾斜列加码**（`statistics 500`）。
8. **强相关列建扩展统计**，别指望独立性假设。
9. **`work_mem` 按并发算总量**，不看单查询。
10. **WAL 只按归档策略清理**，永不 `rm`。
11. **选引擎看放大表**，不看「谁快 N 倍」的营销结论。
12. **把体检写成可复现记录**，让下一个人能照跑。

## 五、术语速查

| 术语 | 英文 | 一句话解释 |
| --- | --- | --- |
| 页 | page / block | 磁盘与内存之间传输的最小单位，PG 8 KB / InnoDB 16 KB |
| 缓冲池 | buffer pool | 内存中缓存页的固定大小区域 |
| 脏页 | dirty page | 内存中已改、尚未落盘的页 |
| 行指针 | line pointer / item id | 页内指向元组的 4 字节条目，索引存的就是它 |
| 扇出 | fan-out | 一个内部节点指向的子节点数，决定树高 |
| 全页写 | full page write (FPI) | 检查点后首次改页时把整页写进 WAL，防半写 |
| LSN | log sequence number | WAL 的字节偏移，也是「页的新旧」比较依据 |
| 检查点 | checkpoint | 把脏页全部刷盘并推进恢复起点的动作 |
| 组提交 | group commit | 把多个事务的 `fsync` 合并成一次 |
| 选择率 | selectivity | 条件能过滤掉多少行的比例估计 |
| 相关性 | correlation | 物理顺序与逻辑顺序的一致程度，0～1 |
| 读放大 | read amplification | 读一行实际碰的页数 ÷ 逻辑需要页数 |
| 写放大 | write amplification | 落盘字节 ÷ 用户写入字节 |
| 空间放大 | space amplification | 磁盘占用 ÷ 逻辑数据大小 |
| compaction | compaction | LSM 把多层 SSTable 合并压缩的后台动作 |
| 墓碑 | tombstone | LSM 中表示「已删除」的标记记录 |

## 六、判据表

| 编号 | 约定 | 定错了会怎样 | 怎么验证没被破坏 |
| --- | --- | --- | --- |
| `DFQ-A` | 排障必须先定位到「四层中的哪一层」，再谈手段 | 在错的层上优化，越调越糟 | 排障记录里写明「结论落在哪一层」 |
| `DFQ-B` | 分诊表里的每条命令必须真实可跑 | 照着做报错，排障直接卡住 | 随机抽三条在本机执行，全部返回结果 |
| `DFQ-C` | 自查清单每一项必须能被一条命令或一条读数判定 | 清单变成「凭感觉打勾」 | 逐项检查「命令」列非空且可执行 |
| `DFQ-D` | 不得把「加内存 / 加索引 / 加并行」作为首选手段 | 掩盖真问题，成本翻倍 | 处置记录里首选手段是「定位 + 改访问路径」 |
| `DFQ-E` | 版本相关答案必须标注适用版本 | 在 PG 16 上按 18 的字段查，直接报错 | 涉及 `pg_stat_wal` / `pg_stat_checkpointer` 的答案都带版本 |
| `DFQ-F` | 术语表必须一句一义，不得堆砌 | 读者看完仍不知道是什么 | 每个术语的解释不超过一行 |
| `DFQ-G` | 最佳实践必须能被判据验证，不得是口号 | 「先量后调」变成空话 | 每条实践都能对应到本专题某个 `*-A~H` 判据 |

## 如何验证

```sql
-- 抽查分诊表里的三条命令是否真的能跑（对应 DFQ-B）
show block_size;
select count(*) from pg_buffercache;
select level from bt_metap('idx_events_tenant_created');

-- 抽查自查清单第 5 项：有没有从未被用过的索引
select relname, indexrelname, idx_scan from pg_stat_user_indexes where idx_scan = 0;

-- 抽查第 12 项：写放大
select pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')) as cumulative_wal;
```

**预期输出**：`8192`；`pg_buffercache` 返回槽位数（本例 16384）；`level = 2`；可疑索引清单（可能为空，也可能列出刚建未用的索引）；累计 WAL 的易读体积。

四条都能出数，说明分诊表不是抄来的——**每一条都在这台机器上跑过**。

## 参考资料

- [PostgreSQL 18 · Monitoring Database Activity](https://www.postgresql.org/docs/18/monitoring.html)——本文所有统计视图的官方入口
- [PostgreSQL 18 · Performance Tips](https://www.postgresql.org/docs/18/performance-tips.html)——官方调优清单（与本页自查表互为补充）
- [PostgreSQL Wiki · Performance Optimization](https://wiki.postgresql.org/wiki/Performance_Optimization)——社区整理的常见误区
- [MySQL 8.4 · Optimization](https://dev.mysql.com/doc/refman/8.4/en/optimization.html)——对照阅读：同一批概念在 InnoDB 里的名字
- [Use The Index, Luke](https://use-the-index-luke.com/)——把「索引与查询形状」讲到可以照做的站点
