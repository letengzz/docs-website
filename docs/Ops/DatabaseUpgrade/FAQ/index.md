# 常见问题与分诊

升级这件事的问题几乎都能归到五类：**连不上、写不进、追不上、跑得慢、退不回**。本页按症状分诊，每条给出「先看什么读数」和「第一步做什么」，避免在窗口里靠猜。

## 一、分诊表

| 症状 | 先看这个读数 | 最可能的根因 | 第一步 |
| --- | --- | --- | --- |
| 应用连不上新库 | 服务端日志的认证错误 | 认证插件/密码加密方式不匹配 | 查 `pg_hba.conf` / `mysql.user.plugin` |
| 写入报 `duplicate key` | 序列 `last_value` vs 表内 `max(id)` | 序列没 `setval` | 立刻修序列（在放开写之前） |
| 写入报「列不存在」 | `information_schema.columns` | DDL 没同步（逻辑复制只搬行） | 目标端补列 |
| 复制延迟一直涨 | `pg_replication_slots` 的 `lag_bytes` | apply worker 已退出（结构/数据冲突） | 看目标端日志找 `ERROR` |
| 复制延迟归零但行数不对 | 双向 `EXCEPT` 比对 | 曾有断链后跳过/覆盖 | 定位差异行，决定补还是回退 |
| 某条查询突然变慢 | `EXPLAIN (ANALYZE, BUFFERS)` | 统计信息缺失 / 索引没迁 / 计划变化 | 先 `ANALYZE`，再比对访问方式 |
| 旧库磁盘持续增长 | `pg_replication_slots` 的 `restart_lsn` | 复制槽没删，WAL 永不回收 | 删槽（确认切换完成后） |
| `pg_upgrade` 报 `could not access file` | 扩展清单 | 扩展没为目标版本安装 | 先在新版本上 `CREATE EXTENSION` |
| 想回退但旧库起不来 | 升级方式（`--link` / 原地） | 已经过了不可回滚点 | 按备份恢复，走 RTO 流程 |
| 窗口超时 | 三段耗时对照 | 全量搬运比估算慢（索引/大对象） | 决定「继续 / 放弃 / 分两次」 |

## 二、连不上：三个层次

```text
① 网络层：telnet host 5432 / 3306 通不通
② 认证层：服务端日志有没有 "password authentication failed" / "Access denied"
③ 权限层：连上了但 select 报 permission denied
```

| 层次 | 升级后才出现的典型原因 |
| --- | --- |
| 认证 | MySQL 8.4 关闭 `mysql_native_password`；PG 从 md5 迁 SCRAM 后旧密码失效 |
| 认证 | 新实例的 `pg_hba.conf` 里没有应用网段 |
| 权限 | 只迁了数据、没迁角色与 `GRANT`（`pg_dump` 不带全局对象，需 `pg_dumpall --globals-only`） |

::: danger 权限是最容易漏的「非数据」
`pg_dump -d shop` 只导这个库的对象与数据，**不导角色**。恢复完的新库上，业务账号可能根本不存在，或者存在但没有权限。

正确做法：升级前单独导出全局对象。

```shell
pg_dumpall --globals-only -f globals.sql     # 角色、表空间、密码
pg_dumpall --roles-only   -f roles.sql       # 只要角色
```
:::

## 三、写不进：序列与约束

序列错位的形态极其固定：

```text
ERROR:  duplicate key value violates unique constraint "orders_pkey"
DETAIL:  Key (id)=(1) already exists.
```

`DETAIL` 里的 `(1)` 就是信号——说明序列还在起点。修法见 [逻辑复制迁移](LogicalMigration/index.md) 第四节，注意**每个序列都要修**，包括那些「业务上很少用」的。

约束类问题次之：`NOT NULL` 在新版本上更严格、`CHECK` 在 MySQL 8.0.16 之前不生效而在之后生效（老库里的脏数据会在升级后暴露）。这类问题**只能在预检阶段用数据扫描提前发现**：

```sql
-- 升级前：找出会被新约束拒绝的数据（示例：负数金额）
select count(*) from orders where amount < 0;
```

## 四、追不上：三种断链

| 断链类型 | 日志特征 | 能否自愈 |
| --- | --- | --- |
| 结构不一致 | `missing replicated column` | ✅ 补列即自愈（实测 3 秒内追平） |
| 数据冲突 | `duplicate key value violates unique constraint` | ❌ 必须人工处理冲突行 |
| 对象缺失 | `relation "xxx" does not exist` | ✅ 建表/建序列即自愈 |

判断「有没有在跑」只看一个字段：

```sql
select subname, pid, received_lsn from pg_stat_subscription;
-- pid 为 NULL = apply worker 没在跑（正在 5 秒一次的重试循环里）
```

::: warning 延迟指标可能是「假安静」
没有新写入时，槽积压不会增长，延迟曲线平得像正常。此时「复制已经停了」这件事**只有 `pid` 和 `active` 两个字段能反映**。所以升级期间必须给这两项配告警，而不是只盯延迟。
:::

## 五、跑得慢：先排除统计信息

升级后「变慢」的第一嫌疑不是新版本，而是**没有统计信息**：

```sql
-- 看最近一次 analyze 时间
select relname, last_analyze, last_autoanalyze, n_live_tup
from pg_stat_user_tables order by n_live_tup desc limit 10;
```

`last_analyze` 为空 = 从来没分析过。此时任何计划比对都没有意义。

排除之后，按「访问方式是否变化」判断，而不是按耗时：

| 现象 | 判断 |
| --- | --- |
| 访问方式与升级前一致，只是慢 | 缓存冷 / 参数不同（`shared_buffers`、`work_mem`） |
| 访问方式从 Index 变 Seq | 统计信息缺失或索引缺失 |
| 访问方式没变但 rows 估算差很多 | 统计目标（`default_statistics_target`）或数据分布变化 |

## 六、退不回：认清不可回滚点

```text
MySQL 8.4 原地升级：新版本第一次成功启动 → 不能回 8.0
PostgreSQL --link：文件被接管 → 旧集群起不来
任何新库已有业务写入 → 回退 = 丢数据或反向同步
```

退不回的处置只有两条：**从备份恢复**（RTO 见演练读数）或 **在新库上修**。前者要提前演练，后者要提前准备「修」的能力（日志、连接、可回滚的代码开关）。

## 七、窗口超时怎么办

窗口进行到一半发现时间不够，只有三个选项，且必须在**停写之前**就想好触发条件：

| 选项 | 代价 | 适用 |
| --- | --- | --- |
| 继续（延长窗口） | 停写时间超预算，业务受损 | 只差几分钟、且已确认无数据问题 |
| 放弃并放开旧库写 | 本次白做，下次重来 | 还在停写区间内（零损失） |
| 切到「半成品」新库 | 最危险 | 不建议；除非新库已验证可用 |

::: danger 「先切过去再慢慢修」是最坏的选择
它的隐含假设是「新库上的问题都能在线修」。而升级期的问题（序列、DDL、权限、计划）恰好都是**需要停机或需要谨慎操作**的那一类。窗口不够就放弃，比带病上线便宜得多。
:::

## 八、十条窗口前自查

1. 备份存在，且**恢复演练过**（有时间记录）。
2. `--check` / `checkForServerUpgrade` 的 error 全清。
3. 切换脚本、验证脚本、回退脚本都在手边，且演练跑过。
4. 每个序列的修法都写成了可执行 SQL（不是「记得修序列」）。
5. 目标端表结构与源端逐列一致（用 `pg_dump -s` 建，不手写）。
6. 旧库的复制槽清单已列出，切换后要删哪些写明了。
7. DNS TTL 已调低，连接池重启方式已确认。
8. 观测面板打开：延迟、槽积压、连接数、5xx、慢查询。
9. 谁执行、谁验证、谁有权喊停，三个人都在线。
10. 回退判据是**阈值**，不是「感觉不对」。

## 九、本页判据

| 编号 | 判据 | 看什么现象 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `UGQ-A` | 排障从「读数」开始，不是从「重启」开始 | 排障记录的第一行是查询 | 按第一节分诊表走 |
| `UGQ-B` | 全局对象（角色/权限）单独迁移 | `pg_dumpall --globals-only` 有记录 | 补导出导入 |
| `UGQ-C` | 序列修复是脚本，不是口头约定 | 可执行 SQL | 写成 `setval` 循环 |
| `UGQ-D` | 复制健康看 `pid` / `active` | 告警规则里有两项 | 补告警 |
| `UGQ-E` | 「变慢」先查统计信息 | `last_analyze` 读数 | `vacuumdb --analyze` |
| `UGQ-F` | 不可回滚点写进了升级单 | 升级单回退节 | 按第六节补 |
| `UGQ-G` | 窗口超时有预设的三个选项 | 升级单有触发条件 | 提前定阈值 |
| `UGQ-H` | 窗口前十条自查逐条打勾 | 自查清单 | 缺项不进窗口 |

## 参考资料

- PostgreSQL 18 Documentation: `pg_stat_subscription`、`pg_stat_user_tables`、`pg_dumpall`
- PostgreSQL 18 Documentation: *Authentication Methods*（SCRAM / md5 废弃）
- MySQL 8.4 Reference Manual: *Access Control*、`CHECK` 约束的生效版本
- 本仓库：[变更管理的高危变更判据](../../ChangeManagement/HighRiskChange/index.md)、[逻辑复制迁移](LogicalMigration/index.md)
