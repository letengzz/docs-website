# 增删改查（CRUD）

MongoDB 的 CRUD 用 JavaScript 风格的 mongosh 语法：`insert`、`find`、`update`、`delete`。这一篇覆盖最常用的命令与查询操作符。

## 插入

```javascript [mongosh]
db.users.insertOne({ name: "张三", age: 25 })
db.users.insertMany([
  { name: "李四", age: 30 },
  { name: "王五", age: 22, tags: ["dev"] }
])
```

## 查询 find

```javascript [mongosh]
db.users.find()                          // 全部
db.users.find({ age: 25 })               // 等值
db.users.findOne({ name: "张三" })
db.users.find({ age: { $gt: 20 } })      // 大于
db.users.find({ name: /^张/ })           // 正则
```

### 常用查询操作符

| 操作符 | 含义 | 示例 |
| --- | --- | --- |
| `$gt` / `$gte` / `$lt` / `$lte` | 比较 | `{age: {$gte: 18}}` |
| `$in` / `$nin` | 在/不在集合内 | `{age: {$in: [20, 30]}}` |
| `$ne` | 不等于 | `{status: {$ne: "x"}}` |
| `$exists` | 字段是否存在 | `{email: {$exists: true}}` |
| `$regex` | 正则匹配 | `{name: {$regex: "^张"}}` |
| `$and` / `$or` | 逻辑 | `{$or: [{a:1},{b:1}]}` |

## 投影、排序、分页

```javascript [mongosh]
// 只返回 name 和 age（1 显示，0 隐藏）
db.users.find({}, { name: 1, age: 1, _id: 0 })

// 排序 age 升序
db.users.find().sort({ age: 1 })

// 分页：第 2 页，每页 10 条
db.users.find().sort({ age: 1 }).skip(10).limit(10)
```

## 更新

```javascript [mongosh]
// 更新单条
db.users.updateOne(
  { name: "张三" },
  { $set: { age: 26 } }
)

// 更新多条
db.users.updateMany(
  { age: { $lt: 18 } },
  { $set: { status: "minor" } }
)

// 存在则更新，不存在则插入
db.users.updateOne(
  { name: "赵六" },
  { $set: { age: 28 } },
  { upsert: true }
)
```

### 更新操作符

| 操作符 | 作用 |
| --- | --- |
| `$set` | 设置字段 |
| `$inc` | 数值自增 |
| `$unset` | 删除字段 |
| `$push` / `$addToSet` | 数组追加 |
| `$pull` | 数组移除 |
| `$rename` | 字段改名 |

## 删除

```javascript [mongosh]
db.users.deleteOne({ name: "王五" })
db.users.deleteMany({ status: "minor" })
db.users.deleteMany({})      // 清空集合（保留索引）
```

## 返回结果

```text
insertOne  → { acknowledged: true, insertedId: ... }
updateOne  → { acknowledged: true, matchedCount: 1, modifiedCount: 1 }
deleteOne  → { acknowledged: true, deletedCount: 1 }
```

## 易错点

::: danger 常见错误
1. `updateOne` 不带 `$set`：整个文档会被替换（`db.c.updateOne({a:1},{b:2})` 会丢字段）。
2. `find` 返回游标不是结果数组：用 `toArray()` 或遍历。
3. `skip` 大分页性能差：深分页用 `_id` 或排序字段游标。
4. 更新不匹配的过滤条件：matchedCount 为 0，检查字段名与类型。
5. 字符串数字混用：`{age: "25"}` 与 `{age: 25}` 不匹配，类型敏感。
6. 忘记 `$inc` 的原子性：`read-then-write` 在多客户端下会丢更新，用 `$inc`。
:::

## 验证方式

1. 插入测试数据后执行各查询，观察返回结果。
2. 用 `explain("executionStats")` 查看查询是否走索引（见索引篇）。
3. 尝试 `updateOne` 不带 `$set`，确认文档被整体替换。

## 参考资料

- CRUD 教程：https://www.mongodb.com/docs/manual/crud/
- 查询操作符：https://www.mongodb.com/docs/manual/reference/operator/query/
- 更新操作符：https://www.mongodb.com/docs/manual/reference/operator/update/
