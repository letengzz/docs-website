# 优化案例

本页收录四个真实的 SQL 优化案例：全表扫描、深分页、慢 JOIN、锁等待。每个案例按「问题现象 → EXPLAIN 分析 → 优化方案 → 结果对比」完整呈现，可直接复用到你的业务。

## 案例一：订单列表全表扫描

### 现象

```sql
SELECT * FROM orders WHERE user_id = 1001 ORDER BY created_at DESC LIMIT 20;
```

接口响应 3.2 秒，orders 表 500 万行。

### EXPLAIN

```text
type=ALL, rows=5000000, Extra=Using filesort
```

全表扫描 + 文件排序。

### 优化

```sql
CREATE INDEX idx_user_created ON orders(user_id, created_at);
```

### 结果

```text
优化前：type=ALL, rows=5000000, 耗时 3.2s
优化后：type=ref, rows=50, Extra=Using index condition, 耗时 8ms
```

**关键点**：联合索引同时覆盖 WHERE（user_id）与 ORDER BY（created_at），排序也走索引，去掉 filesort。

## 案例二：后台列表深分页

### 现象

```sql
SELECT * FROM orders ORDER BY id DESC LIMIT 500000, 20;
```

耗时 4.8 秒，翻到后面越来越慢。

### 分析

`OFFSET 500000` 需要扫描并丢弃 50 万行。

### 优化（延迟关联）

```sql
SELECT o.* FROM orders o
JOIN (
    SELECT id FROM orders ORDER BY id DESC LIMIT 500000, 20
) t ON t.id = o.id;
```

### 结果

```text
优化前：4.8s
优化后：0.9s（内层覆盖索引，外层 20 行回表）
```

进一步优化：管理端改为游标分页 `WHERE id < ? ORDER BY id DESC LIMIT 20`，耗时降至 5ms。

## 案例三：JOIN 被驱动表无索引

### 现象

```sql
SELECT o.id, u.name FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.created_at >= '2026-08-01';
```

耗时 8.5 秒。

### EXPLAIN

```text
o: type=range（created_at 有索引）
u: type=ALL, rows=2000000    ← 每行 o 都要全表扫 u
```

### 优化

users.id 是主键，理论上应走 eq_ref。检查发现：`o.user_id` 是 VARCHAR、`u.id` 是 BIGINT，**类型不一致导致索引失效**。

```sql
-- 统一类型（字段类型改为一致），再补统计
ALTER TABLE orders MODIFY user_id BIGINT NOT NULL;
ANALYZE TABLE orders, users;
```

### 结果

```text
优化前：u type=ALL, 8.5s
优化后：u type=eq_ref, 90ms
```

**关键点**：连接字段类型/字符集不一致会让索引失效——先查类型，别只加索引。

## 案例四：长事务拖垮写入

### 现象

业务反馈：每天 10:00 后所有写入超时，数据库 CPU 不高但锁等待告警。

### 分析

```sql
SELECT trx_id, trx_state, trx_started,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS age
FROM information_schema.innodb_trx
ORDER BY age DESC LIMIT 5;
```

发现一个跑了 45 分钟的**空闲事务**：程序在事务里调用了第三方接口，未 commit。

### 优化

1. KILL 长事务，恢复写入。
2. 代码修复：网络请求移出事务。
3. 设置事务超时兜底：`innodb_lock_wait_timeout=10`、连接池事务超时。
4. 加监控：长事务告警（> 60s）。

### 结果

```text
锁等待清零，写入恢复正常；此后长事务告警提前发现同类问题。
```

## 优化记录模板

```text
日期：2026-08-29
SQL 指纹：SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT 20
现象：3.2s，接口 P95 超时
EXPLAIN：type=ALL, rows=5000000, filesort
根因：缺联合索引
方案：CREATE INDEX idx_user_created ...
结果：8ms，rows=50
回归：写入 QPS 无下降，EXPLAIN 确认 type=ref
```

## 易错点与最佳实践

::: danger 案例中的教训
1. 案例一：排序字段也要进索引，别只给 WHERE 建索引。
2. 案例二：管理端深分页要用延迟关联或游标，OFFSET 不是不能用但要限深。
3. 案例三：先查**类型与字符集**，再谈索引；字段类型不一致是隐性杀手。
4. 案例四：慢 SQL 之外还要监控**长事务**，很多“慢”其实是“等”。
:::

## 验证方式

1. 在测试库复现案例一，记录优化前后 EXPLAIN 与耗时。
2. 用 100 万行数据验证案例二的深分页优化。
3. 人为构造类型不一致 JOIN，验证索引失效与修复。

## 参考资料

- 本专题其余章节：[SQL 优化目录](../index.md)
- MySQL 优化案例（官方博客）：https://dev.mysql.com/blog-archive/
- 《高性能 MySQL》优化案例章节
