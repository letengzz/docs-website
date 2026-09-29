# 关系型数据库

关系型数据库以**表**为存储单元，表和表之间通过外键等建立关系，使用 **SQL** 进行查询。

## 核心特点

- 结构化数据模型：数据以行和列存储，结构固定
- ACID 事务：原子性、一致性、隔离性、持久性
- 丰富的查询能力：JOIN、子查询、聚合等
- 强一致性：约束和事务保证数据可靠

## 常见产品

| 数据库 | 特点 |
| --- | --- |
| MySQL | 开源、应用最广，Web 项目首选之一 |
| PostgreSQL | 功能强大、扩展性好，适合复杂查询 |
| Oracle | 企业级老牌数据库 |
| SQL Server | 微软生态 |
| SQLite | 嵌入式轻量数据库 |

## 适用场景

- 电商、金融等对事务一致性要求高的系统
- 需要复杂关联查询的业务系统
- 系统的主体业务数据存储

## 专题文档

- [MySQL](MySQL/index.md)（概述、安装、核心概念、DDL/DML/DQL、事务、索引优化、常见问题）
- [PostgreSQL](PostgreSQL/index.md)（概述、安装、SQL 基础、高级特性、索引、备份恢复、性能调优、实战、常见问题）
- [SQL 优化](SQLOptimization/index.md)（执行计划、索引原理与失效、慢查询、分页与 JOIN 优化、实战案例）
- [分库分表](Sharding/index.md)（该不该拆的决策、分片键设计、分布式 ID 生成、ShardingSphere、跨分片查询与分布式事务、平滑迁移、实战）
- [数据库中间件](../Middleware/index.md)（中间件形态选型、读写分离工程化、影子库与全链路压测、代理运维、连接治理、中间件视角的分布式事务；**属于「加在关系库前面的那一层」，不是某一个数据库**）

::: warning 建表之前先建模
关系型数据库的表结构不是"想到就加"，而是设计出来的。表怎么拆、主键怎么选、索引怎么定，都属于[数据建模](../DataModeling/index.md)的范畴——**先在模型层改，别在生产库上改**。
:::

::: tip 待补充
后续继续补充 Oracle、SQL Server、SQLite 等关系型数据库专题。
:::

## 相关专题与分工

- [WebAssembly · 概述](../../Frontend/WebAssembly/Overview/index.md)：本分类讲**数据库选型、建模与运维**——该用 MySQL 还是 PostgreSQL、表怎么拆、主键怎么选、索引怎么定、备份与迁移怎么做。WebAssembly 专题里提到「把 SQLite 编译成 Wasm 放进浏览器」这一**客户端数据库**场景，属于**引擎的可移植打包**：同一套 SQL 引擎换个运行环境跑，不涉及建模与运维。边界很清晰——要选型、要建模、要运维，看本分类；要让数据库引擎跑到浏览器 / 边缘端，看 WebAssembly 专题。

## 应用侧视角：ORM 与连接池的两个常见误判

本专题讲的是数据库本身（索引、执行计划、事务、锁）。从**应用侧**看，有两个反复出现的误判值得单独说明——它们都会让人把问题归错地方。

### 误判一：把慢查询当成「连接池不够」

| 现象 | 看起来像 | 实际原因 | 判据 |
| --- | --- | --- | --- |
| 接口响应变慢、并发上不去 | 连接池配小了 | **慢查询占住了连接** | 先看 `SHOW PROCESSLIST` / `pg_stat_activity` 的 `Sending data` 与 `state` |
| 偶发 `too many connections` | 池子开太大 | 实例数 × 池大小 > DB 上限 | 按端到端预算算一遍（见下） |
| 每小时固定一批错误 | 网络抖动 | 池里持有已被服务端关闭的连接 | 检查 `pool_recycle` / `ConnMaxLifetime` 是否小于 `wait_timeout` |

**正确顺序：先 `PROCESSLIST` + `EXPLAIN`，再动连接池参数。** 连接池调大只会让更多并发压在同一个慢查询上。

### 误判二：以为 ORM 生成的 SQL「反正差不多」

ORM 会生成什么样的 SQL，取决于**加载策略**与**分页写法**：

| 写法 | 生成的 SQL | 后果 |
| --- | --- | --- |
| `lazy="select"` 访问关联 | **1 + N** 条 | 列表接口按记录数放大查询 |
| `lazy="raise"` + `selectinload` | 1 + 1 条 | 明确可控，**推荐** |
| `LIMIT 20 OFFSET 100000` | 先扫描丢弃 10 万行 | 第 1 页 5 ms、第 5000 页 3 s |
| 游标分页（`WHERE id < last_id LIMIT 20`） | 索引范围顺序读 | 任意页耗时恒定 |

### 端到端连接预算（扩容前必须算）

```text
DB max_connections = 500
├─ 业务服务 4 实例 × (pool_size 20 + max_overflow 10) = 120
├─ 定时任务 2 实例 × (5 + 2) = 14
└─ 运维 / 迁移预留 20
余量 = 346   ✅
```

::: tip 想深入写应用侧的数据层代码
- **Python**：[数据层：SQLAlchemy 2.0 与 Alembic](../../Backend/PythonWeb/DataLayer/index.md)（`expire_on_commit`、`MissingGreenlet`、Alembic 自动生成检测不到的变更）
- **Go**：[实战：订单服务](../../Backend/GoMicroservices/Practice/index.md)（`ConnMaxLifetime` 与「每小时固定一批 500」的因果关系）
- **迁移纪律**：删除列必须三步走（先发「不再读写该列」的代码 → 观察一个发布周期 → 再删列），一次删掉会让灰度中的旧版本直接报错。
:::

