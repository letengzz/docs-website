# 写放大：WAL 里 96% 是整页副本

「写放大」这个词常被用来形容 LSM 树的合并，但在关系库里它有另一个更日常的来源：**整页写（full page writes，FPI）**。一次逻辑上的行更新，在 WAL 里可能被记成「整张 8 KB 页的副本」——写入的字节数是行数据的上百倍。

这一页回答：FPI 什么时候发生、占 WAL 多少、关掉或压缩它有什么代价、以及这笔账怎么算到复制与备份上。

![写放大的三个来源与 FPI 触发条件](../assets/pt-writeamp.svg)

本页判据族 `TPA-A` ~ `TPA-H`，共 8 条。定义表见文末「本页判据」一节。

## 一、写放大的四个来源

| 来源 | 何时发生 | 放大倍数 | 本机实测 |
| --- | --- | --- | --- |
| **WAL 记录本身** | 每次修改 | 约 1.1~1.3 倍（行数据 + 头） | 60 B/记录（无 FPI 时） |
| **整页写（FPI）** | 检查点后**第一次**修改某页 | 8 KB / 页 = 页内任意一行修改的 10~1000 倍 | 882~1,177 B/记录（含 FPI） |
| **数据页落盘** | 检查点/后台写 | 1 倍（但随机写） | 每 30 秒 1,020~2,417 页 |
| **双写缓冲（MySQL）** | 每次页刷盘 | 2 倍（先写 doublewrite 再写数据文件） | `innodb_doublewrite = ON`（默认） |

PG 没有 doublewrite，它用 FPI 解决同一个问题（**部分写坏页**）：检查点之后第一次修改某页时，把这页的**完整副本**写进 WAL，这样崩溃恢复时即使数据文件里的页只写了一半，也能用 WAL 里的整页副本覆盖。

## 二、本机实测：FPI 占 WAL 的 95%~96%

台架：PostgreSQL 18.6，`pgbench -N -c 8 -j 4`（纯更新，每事务 3 条 `UPDATE`），15 秒，`shared_buffers=128MB`，`checkpoint_timeout=30s`。

| 配置 | TPS | WAL 总量 | FPI 张数 | FPI 原始体积 | FPI 占比 | 记录数 | 每记录字节 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `full_page_writes=on`（重启后第一段） | 3,292.1 | 263.0 MB | 30,973 | ≈254 MB | **96%** | 223,472 | 1,177 B |
| `full_page_writes=on`（同一进程后续） | 3,007.2 | 174.3 MB | 20,152 | ≈165 MB | **95%** | 197,567 | 882 B |
| `full_page_writes=on` + `wal_compression=zstd` | **3,504.6** | **32.5 MB** | 27,143 | ≈222 MB（压缩前） | — | 232,249 | **140 B** |
| `full_page_writes=off` | 3,441.6 | **14.0 MB** | 0 | 0 | 0% | 233,297 | **60 B** |

四行读数，四个结论：

1. **FPI 是 WAL 的绝对主体**：263 MB 里有 254 MB 是整页副本。真正描述「改了什么」的记录只占 4%。
2. **重启后第一段 FPI 最多**：因为缓冲池是空的，每一页的第一次修改都算「检查点后首改」。这也是**「重启后 WAL 暴涨、复制延迟飙升」**的成因——不是数据变了，是 FPI 变多了。
3. **`wal_compression=zstd` 把 222 MB 的整页副本压成约 24 MB**（32.5 MB 总 WAL 减去非 FPI 部分的估计），压缩比接近 **9:1**。原因是页内大量空间是空槽与重复模式。TPS 同时从 3,007 涨到 3,505（**+16.5%**），因为写的字节少了。
4. **关掉 FPI 的收益最大但不该关**：WAL 从 174 MB 降到 14.0 MB（**12.5 倍**），TPS +14.5%，代价是**断电时可能留下无法恢复的坏页**。

::: danger 不要为了省 WAL 关掉 `full_page_writes`
关掉之后，一次部分写（torn page）就可能让数据文件里出现「半新半旧」的页，`pg_checksums` 能发现但无法修复，只能从备份恢复。正确做法是**开压缩**（`wal_compression=zstd`，PG 15+ 支持，PG 18 默认仍为 `off`），而不是关整页写。
:::

## 三、压缩的代价：CPU 与兼容性

| 项 | `pglz` | `lz4` | `zstd` |
| --- | --- | --- | --- |
| PG 版本 | 9.5+ | 15+ | 15+ |
| 压缩率（本机 FPI 场景） | 一般 | 较好 | **约 9:1** |
| CPU 开销 | 高（内置算法慢） | 低 | 中（可调级别） |
| 编译依赖 | 无 | 需 `--with-lz4` | 需 `--with-zstd` |

```sql
-- 查看当前值与是否支持
SHOW wal_compression;
SELECT name, setting, boot_val FROM pg_settings WHERE name = 'wal_compression';
-- 设成 zstd（reload 生效，无需重启）
ALTER SYSTEM SET wal_compression = 'zstd';
SELECT pg_reload_conf();
```

::: warning 压缩是「用 CPU 换 WAL」，不是免费午餐
本机 TPS 涨了 16.5%，是因为这台机器的 CPU 有富余、瓶颈在写。**CPU 已经打满的库开压缩会变慢**。判断方法：开之前先看 `pg_stat_statements` 的总执行时间与 CPU 使用率，若 CPU 已 > 70%，先解决 CPU 再谈压缩。
:::

## 四、这笔账要算到复制与备份上

按实测的「每 15 秒 174.3 MB WAL」换算：

| 场景 | WAL 速率 | 一天 | 一条流复制链路带宽 |
| --- | --- | --- | --- |
| `fpw=on`，无压缩 | 11.6 MB/s | **1.0 TB** | 11.6 MB/s（约 93 Mbps） |
| `fpw=on` + `zstd` | 2.2 MB/s | **187 GB** | 2.2 MB/s（约 18 Mbps） |
| `fpw=off` | 0.9 MB/s | 80 GB | 0.9 MB/s |

这张表解释了三个常见现象：

1. **复制延迟周期性飙高**：主库检查点一密集，FPI 就多，WAL 生成速率瞬间翻倍，备库重放跟不上。
2. **云数据库的「WAL 流量」账单**：跨可用区复制按流量计费时，FPI 是主要成本项。
3. **增量备份体积远超数据变化量**：一天只改了 5 GB 数据，WAL 归档却是 1 TB。

```sql
-- 每天的实际 WAL 生成量与 FPI 比例
SELECT date_trunc('hour', now()) AS 采样时刻,
       pg_size_pretty(wal_bytes) AS wal, wal_fpi, wal_records,
       round(100.0 * wal_fpi * 8192 / nullif(wal_bytes, 0), 1) AS fpi_pct
FROM pg_stat_wal;
-- 注意：pg_stat_wal 是累计值，跨天要自己差分或用监控系统落库
```

## 五、MySQL 的对照：双写缓冲 + redo

MySQL 的写放大路径与 PG 不同（本机 `mysql:8.4` → 8.4.11 实测默认值）：

| 项 | PG 18.6 | MySQL 8.4.11 |
| --- | --- | --- |
| 防部分写机制 | 整页写（FPI） | **双写缓冲** `innodb_doublewrite = ON` |
| 日志 | WAL（16 MB/段） | redo log（`innodb_redo_log_capacity` 默认 **100 MB**） |
| 页大小 | 8 KB | **16 KB** |
| 刷盘方式 | `fsync` / `O_DIRECT`（由 OS 决定） | `innodb_flush_method = O_DIRECT`（默认） |
| 提交持久性 | `synchronous_commit = on` | `innodb_flush_log_at_trx_commit = 1` + `sync_binlog = 1` |

两种机制解决同一个问题，代价形态不同：

- **PG 的 FPI 是「按需写整页」**：只在检查点后首改时写，代价随检查点频率变化。
- **MySQL 的双写是「每次刷页都写两遍」**：稳定的 2 倍写放大，与检查点频率无关。

::: tip 换算时要分清「日志放大」与「数据放大」
PG 的 FPI 放大的是**日志**（WAL），数据文件只写一次；MySQL 的 doublewrite 放大的是**数据写**（同一页写两处）。所以 PG 的优化方向是「减少检查点频率 / 开压缩」，MySQL 的方向是「接受 2 倍写，把 `innodb_flush_method` 设成 `O_DIRECT` 避免再叠一层页缓存」。
:::

## 六、还有一处常被忽略的放大：表膨胀

写放大不只发生在日志层。本机实测（10 万行、14 MB 表，一次全表 `UPDATE`）：

| 时刻 | 表大小 | 死元组 | 说明 |
| --- | --- | --- | --- |
| 初始 | 14 MB | 0 | `VACUUM ANALYZE` 后 |
| 全表更新后 | **27 MB（1.93 倍）** | 100,000 | 每行都产生一个新版本 |
| 63 秒后（autovacuum 清理完） | 27 MB | 0 | 空间被标记可复用，**文件没变小** |
| `VACUUM FULL` 后 | **13 MB** | 0 | 重写整表才真正回收 |

一次「改一遍所有行」的操作，在磁盘上留下 **1.93 倍**的痕迹，而且**不会自己缩回去**。高频全表更新的表（计数、状态位）必须配 `fillfactor`（如 70~80）与 per-table autovacuum，见[维护参数](../Maintenance/index.md)。

## 七、验证

```sql
-- 1) FPI 占比（超过 80% 说明检查点太频繁或写入太分散）
SELECT wal_fpi, wal_records,
       pg_size_pretty(wal_bytes) AS wal,
       round(100.0 * wal_fpi * 8192 / nullif(wal_bytes, 0), 1) AS fpi_pct
FROM pg_stat_wal;
```

```sql
-- 2) 压缩是否生效
SHOW wal_compression;
-- 预期：zstd / lz4（off 说明没开）
```

```sql
-- 3) 膨胀率（死元组占比）
SELECT relname,
       n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
       pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC LIMIT 10;
-- 预期：dead_pct < 20%；长期高于 30% 的表要单独设 autovacuum
```

## 本页判据

| 编号 | 判据 | 看什么现象 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `TPA-A` | 知道 FPI 占比 | 有 `wal_fpi × 8192 / wal_bytes` 的读数 | 采一次 `pg_stat_wal` 并算比例 |
| `TPA-B` | `full_page_writes` 保持开启 | 配置里没有为了省 WAL 关掉它 | 改回 `on`，用压缩替代 |
| `TPA-C` | 写密集型库开了 `wal_compression` | `SHOW wal_compression` 不是 `off` | 设 `zstd`，并核对 CPU 余量 |
| `TPA-D` | WAL 速率有日账单 | 能给出「每天生成多少 WAL、复制要多少带宽」 | 用速率 × 86400 估算并写进容量表 |
| `TPA-E` | 重启后 WAL 暴涨有预案 | 监控里能看到「重启后 FPI 上升」 | 重启安排在低峰，或提前扩容复制链路 |
| `TPA-F` | 高频更新表有 `fillfactor` | 状态位/计数表设了 70~80 | `ALTER TABLE ... SET (fillfactor=80)` 后重建 |
| `TPA-G` | 膨胀率在监控里 | 有 `n_dead_tup / (n_live_tup + n_dead_tup)` 指标 | 加到监控大盘，阈值 20% |
| `TPA-H` | 不把双写与 FPI 混为一谈 | 报表/文档里区分「日志放大」与「数据写放大」 | 按第五节对照表改写口径 |

## 参考资料

- PostgreSQL 18 · `full_page_writes`：<https://www.postgresql.org/docs/18/runtime-config-wal.html#GUC-FULL-PAGE-WRITES>
- PostgreSQL 18 · `wal_compression`：<https://www.postgresql.org/docs/18/runtime-config-wal.html#GUC-WAL-COMPRESSION>
- PostgreSQL 18 · `pg_stat_wal`：<https://www.postgresql.org/docs/18/monitoring-stats.html#MONITORING-PG-STAT-WAL-VIEW>
- MySQL 8.4 · 双写缓冲：<https://dev.mysql.com/doc/refman/8.4/en/innodb-doublewrite-buffer.html>
- MySQL 8.4 · `innodb_redo_log_capacity`：<https://dev.mysql.com/doc/refman/8.4/en/innodb-parameters.html#sysvar_innodb_redo_log_capacity>
- PostgreSQL 18 · `fillfactor`：<https://www.postgresql.org/docs/18/sql-createtable.html#SQL-CREATETABLE-STORAGE-PARAMETERS>
