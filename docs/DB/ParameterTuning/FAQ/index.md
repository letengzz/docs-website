# 常见问题与症状分诊

参数调优的问题大多不是「不知道参数含义」，而是**症状指向了错误的参数**：内存不够时去加缓冲池、IO 抖动时去调 `work_mem`、表膨胀时去加索引。这一页把十类症状整理成分诊表，再列十问、五条错误建议与一份上线自查。

![症状分诊：从现象反查参数](../assets/pt-faq.svg)

本页判据族 `TPQ-A` ~ `TPQ-H`，共 8 条。定义表见文末「本页判据」一节。

## 一、症状分诊表

先按「最先看到的异常」定位，再看「下一步查什么」。

| # | 症状 | 最可能的原因 | 先查这个 | 对应页 |
| --- | --- | --- | --- | --- |
| 1 | 命中率低但延迟正常 | 页缓存兜住了，不是问题 | `free -h` 的 `available` | [内存预算](../MemoryBudget/index.md) |
| 2 | 命中率高但延迟高 | 瓶颈不在存储层（CPU/锁/网络） | `pg_stat_activity` 的 `wait_event` | [并发参数](../Concurrency/index.md) |
| 3 | 大查询偶发慢十倍 | 排序落盘 + 磁盘抖动 | `EXPLAIN` 的 `Sort Method` | [work_mem](../WorkMem/index.md) |
| 4 | 每秒写入不高但 WAL 涨得飞快 | FPI（检查点后首改） | `wal_fpi` | [写放大](../WriteAmplification/index.md) |
| 5 | 每天固定时刻 IO 尖峰 | 检查点或备份撞在一起 | `log_checkpoints` 时间戳 | [检查点节奏](../Checkpoint/index.md) |
| 6 | 重启后复制延迟飙升 | 缓冲池空 → FPI 暴涨 | 主库 `wal_bytes` 每秒增量 | [写放大](../WriteAmplification/index.md) |
| 7 | 并发一上内存就满 | `work_mem × 连接 × 并行` | 容器 RSS 峰值 | [work_mem](../WorkMem/index.md) |
| 8 | 表只增不减 | autovacuum 阈值太松 / 长事务 | `n_dead_tup`、`xact_start` | [维护参数](../Maintenance/index.md) |
| 9 | 执行计划突然变差 | 统计信息过期或采样不足 | `last_autoanalyze` | [维护参数](../Maintenance/index.md) |
| 10 | 改完参数「没感觉」 | 单次读数落在噪声带里 | 同配置 5 次的极差 | [压测驱动的调参](../BenchmarkLoop/index.md) |

## 二、十个高频问题

### Q1：`shared_buffers` 到底设 25% 还是 70%？

PG 设 **25%**（专用）/ **15%~20%**（容器、混部）；MySQL 可以到 **50%~70%**。差别的原因是：PG 依赖操作系统页缓存做第二层缓存，给缓冲池太多会把页缓存挤掉；MySQL 用 `O_DIRECT` 绕过页缓存，所以缓冲池要自己扛。本机实测 PG 把缓冲池放大 4 倍，命中率涨 15 个百分点、TPS 不变，就是「第二层缓存兜住了」的证据。

### Q2：`work_mem` 能设 1 GB 吗？

能，但先算这笔账：`1 GB × 活跃并发 32 × (1+并行 3) = 128 GB`。**参数是全局的，查询是局部的**。正确做法是全局给一个小值（16~64 MB），个别报表语句用 `SET LOCAL work_mem='1GB'`。

### Q3：为什么我调大 `work_mem`，查询没变快？

因为瓶颈不在排序落盘。本机实测：1 MB 与 96 MB 的 `work_mem`，耗时 3,338 ms 与 3,914 ms（后者反而更慢）；切换到内存排序（128 MB）后也只快 **6.2%**，而这个差值落在噪声带内（同配置极差 23.6%）。**`work_mem` 的收益是「不写盘」，不是「更快」**——用 `temp_bytes` 验证，别用耗时。

### Q4：`full_page_writes` 能关吗？

不能。关掉后 WAL 小 12.5 倍、TPS 涨 14.5%，但一次部分写（torn page）就可能留下无法恢复的坏页。**要省 WAL 应该开 `wal_compression=zstd`**：本机实测 222 MB 的整页副本被压到约 24 MB（约 9:1），WAL 总量从 174 MB 降到 32.5 MB。

### Q5：`max_wal_size` 设多大？

按「期望检查点间隔 × 实测 WAL 速率 × 1.5」算。本机 9.4 MB/s、期望 15 分钟 → `15×60×9.4×1.5 ≈ 12.7 GB`，取 8~16 GB。**同时要写下最坏恢复时间**（`distance ÷ 重放速率`），别让恢复时间超过 SLA。

### Q6：`effective_cache_size` 改了没反应？

它只影响**优化器的成本估算**，不占内存、不改运行时行为。本机实测从 64 MB 改到 4 GB，索引扫描成本只从 59,173 降到 57,917（**−2.1%**），计划没变。**判断它有没有用，看 `EXPLAIN` 的计划有没有变**；计划没变就等于没改。

### Q7：为什么 `Workers Planned: 4` 但 `Workers Launched: 3`？

因为 `max_worker_processes`（默认 8）是总池，autovacuum、逻辑复制、后台 worker 都从这里取。公式：`max_worker_processes ≥ max_parallel_workers + autovacuum_max_workers + 4`（+4 给异步 IO worker 与后台任务）。

### Q8：`VACUUM` 跑了，表还是那么大？

`VACUUM` 只把空间标记为可复用，**不缩文件**。本机实测：10 万行表全表更新后 27 MB，autovacuum 清理完仍是 27 MB（死元组归零），`VACUUM FULL` 后回到 13 MB。要缩文件只能用 `VACUUM FULL`（`ACCESS EXCLUSIVE` 锁）或 `pg_repack`。

### Q9：autovacuum 明明在跑，死元组却不降？

长事务挡住了。一个 `idle in transaction` 8 小时的连接会让这 8 小时的死元组全部无法回收。查：

```sql
SELECT pid, state, now() - xact_start AS age, left(query,40)
FROM pg_stat_activity WHERE xact_start IS NOT NULL ORDER BY xact_start LIMIT 5;
```

`age` 超过几分钟的都要处理（`pg_terminate_backend` 前先确认业务）。

### Q10：调完参怎么向别人证明有效？

**用确定性指标做主线，用延迟做辅证**。确定性指标（`temp_bytes`、`wal_bytes`、`Sort Method`、`n_dead_tup`）一次测量就够，可复核；延迟与吞吐必须给「中位数 + 区间 + 噪声带」。本机同配置五次的 TPS 极差是 **23.6%**，任何小于这个幅度的「提升」都不能当结论。

## 三、五条错误建议（网上常见，别照做）

::: danger 这五条不要照做
1. **「`shared_buffers` 设成内存的 70%」**：那是 MySQL 的经验值。PG 设 70% 会把页缓存挤掉，本机实测多给的缓冲池一点吞吐都没换来。
2. **「`work_mem` 调到 256 MB 让大查询快起来」**：单条查询只快 6.2%，而 100 连接 × 3 并行的上界是 76.8 GB。**先按预算反推，再对个别语句放大。**
3. **「关掉 `full_page_writes` 省 WAL」**：省下的是 WAL，赔上的是崩溃可恢复性。正确做法是开 `wal_compression`。
4. **「`random_page_cost` 设成 1.0 让优化器多用索引」**：SSD 上 1.1 是合理起点，但设 1.0 会让优化器在**大范围扫描**时也选索引，反而更慢。**改完必须看执行计划与实测耗时**。
5. **「把所有参数一次性调成网上的推荐值」**：多变量同时动，读数变化无法归因；而且别人的机器规格、负载、版本都和你不同。**一次只动一个，并留下 A/B/A 记录。**
:::

## 四、上线自查十二项

| # | 检查项 | 命令 / 判据 | 通过标准 |
| --- | --- | --- | --- |
| 1 | 参数已生效 | `SELECT name, setting, pending_restart FROM pg_settings` | 无 `pending_restart = t` |
| 2 | 内存上界不超物理内存 | 预算表算式 | 最坏情况 ≤ 物理内存 × 80% |
| 3 | 缓冲池占比合理 | `shared_buffers` / 物理内存 | 15%~30% |
| 4 | 大查询不落盘 | `EXPLAIN` 的 `Sort Method` | 关键查询为 `quicksort`/`Memory` |
| 5 | 临时文件增长受控 | `pg_stat_database.temp_bytes` | 报表期间零增长 |
| 6 | 检查点不按量触发 | `pg_stat_checkpointer.num_requested` | 一小时内不增长 |
| 7 | WAL 体积有预算 | `pg_stat_wal.wal_bytes` 日增量 | 与归档/复制带宽匹配 |
| 8 | 并行真启动 | `EXPLAIN ANALYZE` 的 `Workers Launched` | 等于 `Planned` |
| 9 | 大表有 per-table autovacuum | `pg_class.reloptions` | 千万行表均有覆盖 |
| 10 | 膨胀率受控 | `n_dead_tup / (live + dead)` | < 20% |
| 11 | 无长事务 | `pg_stat_activity.xact_start` | 无超过 5 分钟的 |
| 12 | 有回滚条件 | 调参单 | 每个参数都有「改回去」的触发条件 |

## 五、一张「别再调了」的清单

有些问题**不是参数能解决的**，硬调只会掩盖症状：

| 现象 | 参数救不了，该做什么 |
| --- | --- |
| 单表 20 亿行、查询扫全表 | 分区 / 归档 / 改数据模型（见[表分区与归档](../../PartitionArchival/index.md)） |
| 索引缺失导致全表扫 | 建索引（见[SQL 优化](../../Relational/SQLOptimization/index.md)） |
| 应用开了 800 个连接且大多 `idle` | 上连接池，不是加 `max_connections` |
| 单机 CPU 打满 | 读写分离 / 加副本 / 换机器 |
| 云盘 IOPS 到顶 | 换盘型或加缓存层，参数只能缓解 |
| 事务里有外部调用（HTTP/RPC） | 改事务边界，参数完全无效 |

## 本页判据

| 编号 | 判据 | 看什么现象 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `TPQ-A` | 症状能对上分诊表 | 现象能落到十类之一，并指向具体页 | 先把现象量化（分位、速率、占比），再定位 |
| `TPQ-B` | 不把命中率当结论 | 结论里没有「命中率提升所以更快」 | 换成延迟/吞吐/物理读字节 |
| `TPQ-C` | `work_mem` 用落盘量验证 | 有 `temp_bytes` 前后值 | 补采样 |
| `TPQ-D` | WAL 优化用压缩而非关闭 | `full_page_writes` 保持 `on` | 改回 `on` 并开 `wal_compression` |
| `TPQ-E` | 检查点区分按时/按量 | 有 `num_requested` 读数 | 补 `pg_stat_checkpointer` 采集 |
| `TPQ-F` | 膨胀问题先查长事务 | 有 `xact_start` 最老的会话 | 先处理长事务，再谈 `VACUUM FULL` |
| `TPQ-G` | 结论带噪声带 | 报告里有噪声幅度与区间 | 补同配置多次读数 |
| `TPQ-H` | 能识别「参数救不了」的场景 | 有第六节这类清单 | 补清单，避免无效调参 |

## 参考资料

- PostgreSQL 18 · 服务器配置：<https://www.postgresql.org/docs/18/runtime-config.html>
- PostgreSQL Wiki · Tuning Your PostgreSQL Server：<https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server>
- PostgreSQL 18 · 监控统计视图总览：<https://www.postgresql.org/docs/18/monitoring-stats.html>
- MySQL 8.4 · InnoDB 参数：<https://dev.mysql.com/doc/refman/8.4/en/innodb-parameters.html>
- PostgreSQL 18 · `pg_stat_activity`：<https://www.postgresql.org/docs/18/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW>
