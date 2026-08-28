# 索引优化

索引让 MongoDB 查询避免全表扫描。常用类型：**单字段、复合、唯一、TTL、文本**。判断索引是否生效靠 `explain`。

## 创建索引

```javascript [mongosh]
// 单字段（1 升序，-1 降序）
db.users.createIndex({ age: 1 })

// 复合索引（先 name 后 age）
db.users.createIndex({ name: 1, age: -1 })

// 唯一索引
db.users.createIndex({ email: 1 }, { unique: true })

// TTL 索引：createdAt 超过 7 天自动删除
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 604800 })

// 文本索引（字段或通配）
db.articles.createIndex({ title: "text", content: "text" })
```

## 查看索引

```javascript [mongosh]
db.users.getIndexes()
```

## 复合索引设计原则

1. 等值条件放前面，排序/范围条件放后面。
2. 字段顺序影响索引选择，按查询模式设计。
3. 索引不是越多越好，写放大 + 磁盘占用。

## 用 explain 验证

```javascript [mongosh]
db.users.find({ age: { $gt: 20 } }).explain("executionStats")
```

关注字段：

| 字段 | 含义 |
| --- | --- |
| `stage` | `IXSCAN` 走索引，`COLLSCAN` 全表扫 |
| `totalDocsExamined` | 扫描文档数 |
| `totalKeysExamined` | 扫描索引项数 |
| `executionTimeMillis` | 执行耗时 |

## 索引失效场景

1. 字段上做运算：`{ $expr: { $gt: [{ $add: ["$a", 1] }, 10] } }` 无法用 a 的索引。
2. 正则以 `^` 开头的锚定表达式：`^张` 可用，`张$` 不用。
3. 复合索引左前缀原则被破坏：查询没用到第一个字段。
4. 字段类型混乱：字符串与数字混存。
5. `$or` 子句没有各自索引。

## TTL 与过期清理

```javascript [mongosh]
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })
```

后台任务每 60 秒扫描一次，删除过期文档；适合会话、验证码等数据。

## 易错点

::: danger 常见错误
1. 全表数据量小就不建索引：数据增长后查询突然变慢。
2. 每个字段都建索引：写性能下降、磁盘翻倍，按查询模式建。
3. 复合索引字段顺序反了：命中率低。
4. 唯一索引冲突：插入重复值直接报错，先在测试库验证。
5. `explain` 看 `stage: COLLSCAN` 就以为“能用”：必须 `IXSCAN`。
6. TTL 索引字段是字符串日期：必须是 BSON Date 类型才生效。
:::

## 验证方式

1. 建索引前后各执行一次 `explain("executionStats")`，对比 `IXSCAN` 与耗时。
2. 插入重复 email 验证唯一索引。
3. 插入带 `createdAt` 的文档，观察 TTL 索引过期删除。

## 参考资料

- 索引：https://www.mongodb.com/docs/manual/indexes/
- 复合索引：https://www.mongodb.com/docs/manual/core/index-compound/
- explain 输出：https://www.mongodb.com/docs/manual/reference/explain-results/
