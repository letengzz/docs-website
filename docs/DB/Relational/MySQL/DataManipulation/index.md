# 数据增删改查（DML）

DML（Data Manipulation Language）负责数据的插入、修改和删除。

## INSERT 插入数据

```sql
-- 插入单行
INSERT INTO user (username, email, age)
VALUES ('zhangsan', 'zs@example.com', 18);

-- 批量插入
INSERT INTO user (username, email)
VALUES
  ('lisi', 'lisi@example.com'),
  ('wangwu', 'wangwu@example.com');

-- 另一种写法（不推荐，可读性差）
INSERT INTO user SET username = 'zhaoliu', email = 'zl@example.com';
```

插入时忽略重复：

```sql
INSERT IGNORE INTO user (username, email)
VALUES ('zhangsan', 'zs@example.com');
```

存在则更新（upsert）：

```sql
-- 旧写法（MySQL 8.0.20 起 VALUES() 已弃用）
INSERT INTO user (username, email)
VALUES ('zhangsan', 'new@example.com')
ON DUPLICATE KEY UPDATE email = VALUES(email);

-- 新写法（推荐）
INSERT INTO user (username, email)
VALUES ('zhangsan', 'new@example.com') AS new
ON DUPLICATE KEY UPDATE email = new.email;
```

::: danger 注意
`ON DUPLICATE KEY UPDATE` 依赖唯一索引或主键判断冲突；没有唯一约束时会直接插入。
:::

## UPDATE 更新数据

```sql
-- 更新单条
UPDATE user SET age = 19 WHERE username = 'zhangsan';

-- 批量更新
UPDATE user SET age = age + 1 WHERE status = 1;

-- 多表更新（8.0 不推荐，改用子查询）
UPDATE user u
JOIN orders o ON o.user_id = u.id
SET u.status = 0
WHERE o.created_at < '2025-01-01';
```

::: danger 注意
1. `UPDATE` 不写 `WHERE` 会更新**全表**！执行前先 `SELECT` 确认条件命中范围。
2. 更新影响行数可以用 `ROW_COUNT()` 查看。
3. 生产环境的批量更新建议分批执行（如每次 1000 行），避免长时间锁表。
:::

## DELETE 删除数据

```sql
-- 删除指定行
DELETE FROM user WHERE id = 1;

-- 清空表（有事务日志，慢）
DELETE FROM user;

-- 清空表（DDL，不可回滚，重置自增，快）
TRUNCATE TABLE user;
```

::: danger 注意
1. `DELETE` 同样要先确认 `WHERE` 条件。
2. `TRUNCATE` 是 DDL，**不能回滚**，生产环境清表前先备份。
3. 大表删除建议分批：`DELETE FROM user WHERE id < 100000 LIMIT 1000;` 循环执行。
:::

## 事务配合使用

多条写操作需要保持一致时，放进显式事务：

```sql
START TRANSACTION;

INSERT INTO user (username, email) VALUES ('zhangsan', 'zs@example.com');
UPDATE account SET balance = balance - 100 WHERE user_id = 1;

COMMIT;   -- 全部成功提交
-- ROLLBACK;  -- 出错时全部回滚
```

::: tip
1. 单条 SQL 本身是隐式事务；多条 SQL 的一致性必须用显式事务。
2. 事务里不要做耗时的外部调用（HTTP 请求等），长事务会占住连接和锁。
:::

## 验证方式

```sql
-- 查看总数
SELECT COUNT(*) FROM user;

-- 抽查数据
SELECT id, username, email, age FROM user WHERE username = 'zhangsan';

-- 验证更新影响行数
SELECT ROW_COUNT();
```

确认新增、修改、删除的结果符合预期。
