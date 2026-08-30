# 常见问题与最佳实践

汇总索引深入使用中的高频问题：失效排查、回表、冗余、维护与版本差异，方便快速查阅。

## 失效类

### 索引明明建了，EXPLAIN 还是全表扫描？

按顺序排查：

1. `key` 是否为 NULL → 看 WHERE 列是否被函数/运算包裹；
2. 列与参数类型是否一致（隐式转换）；
3. 联合索引是否满足最左前缀；
4. 是否有 `OR`/`!=`/`LIKE '%x'` 失效模式；
5. 统计信息是否过期（`ANALYZE TABLE`）；
6. 小表/低选择性时，**全表扫描可能就是最优解**。

### 为什么 `LIKE '%abc'` 不走索引？

前导通配符无法确定索引搜索起点；`'abc%'` 可以。需要中间匹配用全文索引或反向存储。

### `IS NULL` 走索引吗？

取决于数据分布与版本：

- 大量 NULL 且选择性低 → 优化器可能全表扫描；
- 少量 NULL → 8.0 可用 `IS NULL` 范围访问；
- `IS NOT NULL` 通常难以高效用索引。

## 回表类

### 怎么判断查询是否回表？

看 `EXPLAIN` 的 Extra：

| Extra | 含义 |
| --- | --- |
| `Using index` | 覆盖索引，不回表 |
| `Using index condition` | ICP 生效，减少回表 |
| 无标记 | 正常回表 |
| `Using where` | 回表后 Server 层过滤 |

### 回表很慢怎么办？

1. 高频查询把返回列补进索引（覆盖）；
2. 范围条件利用 ICP 先过滤；
3. 大结果集回表用 MRR 优化随机 IO；
4. 实在无法覆盖的大字段，拆表或延迟关联。

## 设计类

### 联合索引列顺序怎么定？

口诀：**等值前、范围后、排序贴合**。

```sql
-- WHERE user_id=? AND status=? ORDER BY created_at
KEY idx (user_id, status, created_at)
```

选择性高的等值列放前面；范围/排序列放后面。

### 索引是不是越多越好？

不是。每个索引都增加：

- 写入维护成本；
- 存储空间；
- 优化器选择成本。

单表超过 15 个索引就要审查冗余与使用率。

### 怎么发现冗余索引？

1. `sys.schema_unused_indexes`：找未使用索引；
2. 检查最左前缀重复：`idx(a)` 被 `idx(a,b)` 覆盖；
3. Percona `pt-duplicate-key-checker` 自动识别。

## 维护类

### 索引膨胀了怎么办？

```sql
-- 8.0 在线重建
ALTER TABLE orders DROP INDEX idx_x, ADD INDEX idx_x (col);

-- 或 OPTIMIZE TABLE（重建表，注意锁与资源）
OPTIMIZE TABLE orders;
```

### 删除索引怕出问题？

用**不可见索引**过渡：

```sql
ALTER TABLE orders ALTER INDEX idx_x INVISIBLE;
-- 观察 1~2 周无性能回退后
ALTER TABLE orders ALTER INDEX idx_x VISIBLE;  -- 或 DROP INDEX
```

### 大表加索引会锁表吗？

8.0 支持在线 DDL：

```sql
ALTER TABLE orders ADD INDEX idx_x (col),
    ALGORITHM=INPLACE, LOCK=NONE;
```

超大表仍建议 gh-ost / pt-osc 工具。

## 版本差异类

### 8.0 / 8.4 / 9.x 有什么索引相关差异？

| 能力 | 版本 |
| --- | --- |
| 降序索引 | 8.0 |
| 不可见索引 | 8.0 |
| 函数索引 | 8.0.13 |
| Skip Scan | 8.0.13 |
| EXPLAIN ANALYZE | 8.0.18 |
| Hypergraph 优化器 | 9.0+（9.7 LTS 默认支持度提升） |

8.0 已 EOL（2026-04），生产优先 8.4 / 9.7 LTS。

## 最佳实践清单

::: tip 索引检查清单
1. 查询是否 EXPLAIN 验证过（key/rows/Extra）？
2. 是否避免函数包裹、类型转换、前通配？
3. 联合索引是否等值前、范围后、排序贴合？
4. 高频查询是否覆盖索引免回表？
5. 是否有冗余/未使用索引待清理？
6. 大表索引变更是否在线执行？
7. 统计信息是否定期 ANALYZE？
8. 删除索引前是否 INVISIBLE 观察？
9. 深分页是否改游标/延迟关联？
10. 优化案例是否沉淀到团队文档？
:::

## 参考资料

- [MySQL 官方：优化与索引](https://dev.mysql.com/doc/refman/8.4/en/optimization-indexes.html)
- [MySQL 8.4 发行说明](https://dev.mysql.com/doc/relnotes/mysql/8.4/en/)
- [MySQL 9.7 发行说明](https://dev.mysql.com/doc/relnotes/mysql/9.7/en/)
