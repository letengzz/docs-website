# 锁与事务对查询的影响

查询慢不一定是指标问题，也可能是**锁等待**：事务没提交、行锁没释放，后面的查询只能排队。本页讲清楚 InnoDB 锁类型、MVCC 与事务隔离级别对查询的影响，以及锁等待与死锁的排查。

## 事务与 MVCC

InnoDB 通过 **MVCC（多版本并发控制）** 让读不阻塞写、写不阻塞读：

| 概念 | 说明 |
| --- | --- |
| undo log | 记录旧版本，支撑回滚与一致性读 |
| read view | 决定事务能看到哪些版本 |
| 一致性非锁定读 | 普通 SELECT 不加锁，读快照 |

因此“查询慢”通常不是被其他事务的锁阻塞（普通读），而是：

1. 扫描本身慢（索引问题）。
2. 当前读（`FOR UPDATE` / `LOCK IN SHARE MODE`）遇到锁等待。
3. 长事务持有锁，阻塞其他事务的写。

## InnoDB 锁类型

| 锁 | 说明 |
| --- | --- |
| 共享锁（S） | `LOCK IN SHARE MODE`，可并发读，阻止写 |
| 排他锁（X） | `FOR UPDATE` / 写操作，独占 |
| 行锁 | 锁定具体索引记录 |
| 间隙锁 | 锁定范围间隙，防幻读 |
| 临键锁 | 记录锁 + 间隙锁（RR 默认） |
| 意向锁 | 表级意向，表示事务准备加行锁 |
| 表锁 | 如 DDL 时 |

## 锁等待的排查

```sql
-- 查看当前事务
SELECT * FROM information_schema.innodb_trx\G

-- 查看锁等待（sys 视图最直观）
SELECT * FROM sys.innodb_lock_waits\G

-- 查看被阻塞的语句
SELECT * FROM performance_schema.events_statements_current\G
```

典型场景：

```text
事务 A：UPDATE orders SET status='PAID' WHERE id=100;  （未提交）
事务 B：UPDATE orders SET status='SHIPPED' WHERE id=100;  ← 等待 A 提交
```

处理：

1. 找到持有锁的事务（`trx_state`、`trx_started`）。
2. 确认它是否“僵死”（空闲事务没提交）。
3. 业务上缩短事务：查询与更新分开，减少锁持有时间。
4. 必要时 `KILL` 长事务（评估影响后）。

## 死锁

死锁是两个事务互相持有对方需要的锁：

```text
事务 A：UPDATE t1 ... → 等 t2 的锁
事务 B：UPDATE t2 ... → 等 t1 的锁
```

InnoDB 会自动检测并回滚**代价较小的事务**，报错：

```text
ERROR 1213 (40001): Deadlock found when trying to get lock
```

排查：

```sql
SHOW ENGINE INNODB STATUS\G
-- 查看 LATEST DETECTED DEADLOCK 段：两个事务的语句与持有的锁
```

::: danger 死锁预防
1. 多表更新按**相同顺序**加锁（A→B→C）。
2. 事务尽量短：不把查询/远程调用放进事务。
3. 使用索引：无索引更新会锁全表/大量间隙。
4. 应用侧处理 1213：捕获后重试（指数退避）。
5. 批量更新分批执行，避免大范围锁。
:::

## 事务隔离级别与查询

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 默认 |
| --- | --- | --- | --- | --- |
| READ UNCOMMITTED | 可能 | 可能 | 可能 | - |
| READ COMMITTED | 否 | 可能 | 可能 | - |
| REPEATABLE READ | 否 | 否 | 否（MVCC+临键锁） | MySQL 默认 |
| SERIALIZABLE | 否 | 否 | 否 | - |

```sql
-- 查看/设置
SELECT @@transaction_isolation;
SET SESSION transaction_isolation = 'READ-COMMITTED';
```

高并发写场景可评估 `READ-COMMITTED`（减少间隙锁），但要在业务确认一致性语义后。

## 长事务的影响

```sql
-- 找到运行超过 60 秒的事务
SELECT trx_id, trx_state, trx_started,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS age_sec
FROM information_schema.innodb_trx
WHERE TIMESTAMPDIFF(SECOND, trx_started, NOW()) > 60;
```

长事务带来的问题：

1. undo log 无法清理，版本链变长 → 查询变慢。
2. 持有锁阻塞写入。
3. 影响缓存与整体性能。

## 易错点与最佳实践

::: danger 常见错误
1. **事务里做网络请求/远程调用**：锁持有时间变成秒级，全站等待。
2. **SELECT 忘记提交事务**：程序里开了事务不 commit，长事务挂一天。
3. **批量 UPDATE 不设 LIMIT**：一次更新 100 万行，锁与 undo 暴涨；分批。
4. **无索引条件更新**：`UPDATE ... WHERE status='X'` 无索引 → 锁全表。
5. **把死锁当 bug 死磕**：应用层重试才是正确解法，死锁会正常偶发。
6. **隔离级别盲目调低**：REPEATABLE READ 是默认安全选项，改动要评估。
:::

::: tip 最佳实践
1. 事务保持最小：只包含必要 DML，查询放事务外。
2. 更新条件走索引，缩小锁范围。
3. 多表操作固定加锁顺序。
4. 监控长事务与锁等待，接告警（见 [监控告警](../../../../Ops/Monitoring/index.md)）。
5. 应用层统一处理 1213 死锁重试。
:::

## 验证方式

1. 开两个会话模拟行锁等待，用 `sys.innodb_lock_waits` 定位到持锁事务。
2. 构造死锁（A→B、B→A），确认 InnoDB 报 1213 并回滚一个事务。
3. 开启一个 2 分钟空事务，用 `information_schema.innodb_trx` 找到它并 KILL。

## 参考资料

- InnoDB 锁机制：https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html
- 死锁检测：https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlock-detection.html
- 事务隔离级别：https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html
- sys.innodb_lock_waits：https://dev.mysql.com/doc/refman/8.4/en/sys-innodb-lock-waits.html

## 相关专题

- [分布式事务](../../../../Backend/Microservices/DistributedTransaction/index.md)：跨库/跨服务的锁与一致性取舍（2PC、TCC、SAGA、消息表）
- [一致性基础与事务边界](../../../../Backend/Microservices/DistributedTransaction/Consistency/index.md)：长事务为什么是分布式事务的敌人
- [2PC 与 XA](../../../../Backend/Microservices/DistributedTransaction/TwoPhaseCommit/index.md)：Prepare 阶段长期持锁的代价与 MySQL XA 限制
