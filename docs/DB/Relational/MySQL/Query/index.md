# 查询进阶（DQL）

查询是日常开发中使用最频繁的操作，本页覆盖 SELECT 的常用能力。

## SELECT 基础

```sql
-- 查询指定列
SELECT id, username, age FROM user;

-- 查询全部列（开发中避免）
SELECT * FROM user;

-- 去重
SELECT DISTINCT status FROM user;

-- 别名
SELECT username AS name, age + 1 AS next_age FROM user;
```

::: tip
生产环境不要随手写 `SELECT *`：一是返回无用列浪费带宽，二是破坏覆盖索引优化。
:::

## WHERE 条件过滤

```sql
SELECT * FROM user WHERE age >= 18 AND status = 1;
SELECT * FROM user WHERE age BETWEEN 18 AND 30;
SELECT * FROM user WHERE username IN ('zhangsan', 'lisi');
SELECT * FROM user WHERE email LIKE '%example.com';
SELECT * FROM user WHERE age IS NULL;
SELECT * FROM user WHERE age IS NOT NULL AND status IN (0, 1);
```

::: danger 注意
1. 判断空值必须用 `IS NULL` / `IS NOT NULL`，`= NULL` 永远不成立。
2. `LIKE '%xxx'` 前导通配符无法使用索引。
3. `IN` 数量过大时性能下降，可用临时表或分批查询。
:::

## 排序与分页

```sql
-- 多列排序
SELECT * FROM user ORDER BY age DESC, id ASC;

-- 分页：第 3 页，每页 10 条
SELECT * FROM user ORDER BY id LIMIT 20, 10;
```

深分页优化（键集分页）：

```sql
-- 记录上一页最后一条 id，下一页直接带条件
SELECT * FROM user
WHERE id > 100000
ORDER BY id
LIMIT 10;
```

::: tip
`LIMIT 1000000, 10` 会先扫描前 100 万行再丢弃，非常慢；大分页优先用键集分页。
:::

## 聚合与分组

```sql
SELECT
  status,
  COUNT(*)      AS cnt,
  AVG(age)      AS avg_age,
  MAX(age)      AS max_age,
  MIN(age)      AS min_age,
  SUM(age)      AS sum_age,
  GROUP_CONCAT(username) AS names
FROM user
GROUP BY status
HAVING cnt > 1;
```

常用聚合函数：

| 函数 | 作用 |
| --- | --- |
| `COUNT(*)` | 行数 |
| `SUM` | 求和 |
| `AVG` | 平均值 |
| `MAX / MIN` | 最大 / 最小值 |
| `GROUP_CONCAT` | 分组拼接字符串 |

::: danger 注意
`WHERE` 过滤的是行，`HAVING` 过滤的是分组结果；能用 `WHERE` 就不要用 `HAVING`。
:::

## 多表 JOIN

```sql
-- 内连接：两边都匹配
SELECT u.username, o.id AS order_id, o.amount
FROM user u
INNER JOIN orders o ON o.user_id = u.id;

-- 左连接：左表全保留
SELECT u.username, o.id AS order_id
FROM user u
LEFT JOIN orders o ON o.user_id = u.id;
```

| 连接类型 | 含义 |
| --- | --- |
| `INNER JOIN` | 只返回匹配的行 |
| `LEFT JOIN` | 左表全部 + 右表匹配 |
| `RIGHT JOIN` | 右表全部 + 左表匹配 |
| `CROSS JOIN` | 笛卡尔积，慎用 |

::: tip
连接条件字段两侧都要有索引，否则会产生全表扫描。
:::

## 子查询

```sql
-- WHERE 子查询
SELECT * FROM user
WHERE id IN (SELECT user_id FROM orders WHERE amount > 100);

-- 标量子查询
SELECT u.*,
       (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_cnt
FROM user u;

-- FROM 子查询（派生表）
SELECT username, order_cnt
FROM (
  SELECT user_id, COUNT(*) AS order_cnt
  FROM orders
  GROUP BY user_id
) t
JOIN user u ON u.id = t.user_id;
```

## 常用内置函数

```sql
-- 字符串
SELECT CONCAT(username, '@', age) FROM user;
SELECT SUBSTRING(email, 1, 5) FROM user;

-- 数值
SELECT ROUND(amount, 2), CEIL(amount), FLOOR(amount) FROM orders;

-- 日期
SELECT DATE_FORMAT(created_at, '%Y-%m-%d') AS day, COUNT(*)
FROM user
GROUP BY day;

SELECT NOW(), CURDATE(), DATE_ADD(NOW(), INTERVAL 1 DAY), DATEDIFF('2026-08-01', '2026-07-01');

-- 条件
SELECT
  username,
  CASE
    WHEN age < 18 THEN '未成年'
    WHEN age < 60 THEN '成年'
    ELSE '老年'
  END AS age_bucket
FROM user;

SELECT COALESCE(email, '未填写') FROM user;
```

## 验证方式

复杂查询先加 `EXPLAIN` 查看执行计划（详见索引篇）：

```sql
EXPLAIN SELECT u.username, COUNT(o.id)
FROM user u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id;
```

再结合实际数据核对返回结果与预期一致。

## 相关专题

- [SQL 优化](../../SQLOptimization/index.md)：分页、JOIN 与查询改写的最佳实践
- [JOIN 优化](../../SQLOptimization/JoinOptimization/index.md)：连接算法与驱动表优化
