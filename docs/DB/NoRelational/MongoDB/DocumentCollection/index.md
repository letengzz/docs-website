# 文档与集合

理解 MongoDB 的数据组织：**数据库（Database）→ 集合（Collection）→ 文档（Document）**。文档是 BSON 对象，集合是文档的容器，无需预定义结构。

## 三级结构

```text
Database（数据库）
└── Collection（集合）
    └── Document（文档）
        └── Field（字段）
```

## 数据库操作

```javascript [mongosh]
use mydb                // 切换/创建数据库
show dbs                // 查看数据库
db.dropDatabase()       // 删除当前数据库
```

注意：数据库在第一次写入数据时才真正创建。

## 集合操作

```javascript [mongosh]
db.createCollection("users")   // 显式创建
db.users.insertOne({name: "张三"})  // 隐式创建（推荐）
show collections
db.users.drop()
```

集合命名规则：

1. 不能为空字符串。
2. 不能包含 `$`、`.` 或空字符。
3. 不要以 `system.` 开头（系统保留）。

## 文档（BSON）

```javascript [mongosh]
db.users.insertOne({
  name: "张三",
  age: 25,
  tags: ["java", "mongo"],
  address: { city: "上海", zip: "200000" },
  createdAt: new Date()
})
```

常用 BSON 类型：

| 类型 | 示例 |
| --- | --- |
| ObjectId | `ObjectId("...")` |
| String / Number | `"abc"` / `42` |
| Boolean | `true` |
| Date | `new Date()` |
| Array | `[1, 2, 3]` |
| Embedded Document | `{city: "上海"}` |
| Null | `null` |

## _id 主键

每个文档必须有一个唯一 `_id`：

1. 不指定时自动生成 `ObjectId`（12 字节：时间戳 + 机器 + 进程 + 自增）。
2. 可以自定义 `_id`（字符串、数字等）。
3. `_id` 默认索引且唯一，不能修改。

```javascript [mongosh]
db.orders.insertOne({ _id: "order-1001", total: 99.9 })
```

## 内嵌 vs 引用

| 关系 | 建议 |
| --- | --- |
| 一对一（地址、配置） | 内嵌文档 |
| 一对多（订单 → 明细） | 内嵌数组 |
| 多对多 / 独立生命周期 | 引用 + $lookup |

## 易错点

::: danger 常见错误
1. 以为集合必须建好才能插入：MongoDB 首条插入自动建集合。
2. `use db` 后以为数据库已创建：没有数据时 `show dbs` 不显示。
3. 文档字段名含 `.` 或 `$`：查询/更新会出问题，避免使用。
4. `_id` 重复插入：抛 `E11000 duplicate key error`。
5. 数组无限增长：内嵌数组文档有 16MB 单文档限制，大列表用独立集合。
6. 用字符串存日期：无法用日期索引和范围查询，用 BSON Date。
:::

## 验证方式

1. `db.users.insertOne({...})` 后 `db.users.find()` 查看。
2. `db.users.stats()` 查看集合统计。
3. 尝试插入重复 `_id`，观察 `E11000` 报错。

## 参考资料

- 文档模型：https://www.mongodb.com/docs/manual/core/document/
- BSON 类型：https://www.mongodb.com/docs/manual/reference/bson-types/
- 集合：https://www.mongodb.com/docs/manual/core/databases-and-collections/
