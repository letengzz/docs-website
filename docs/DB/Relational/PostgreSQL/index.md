# PostgreSQL

<p style="text-align:center;"><img src="./assets/postgresql-logo.png" style="zoom:75%;" /></p>

PostgreSQL（常称 PG）是功能最强大的开源关系型数据库之一：完整 ACID、丰富类型（JSONB/数组/地理）、全文检索、分区表与强大扩展生态。本专题覆盖概述、安装、SQL 基础、高级特性、索引、备份恢复、性能调优与实战。

本专题默认基于 **PostgreSQL 18**（2025 年 9 月发布，当前稳定版 18.6），涉及版本差异时在文中标注。

- [PostgreSQL 概述](Overview/index.md)
- [安装与配置](Install/index.md)
- [SQL 基础](SqlBasic/index.md)
- [高级特性](Advanced/index.md)
- [索引详解](Index/index.md)
- [备份与恢复](BackupRestore/index.md)
- [性能调优](Performance/index.md)
- [实战：博客系统数据库](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

::: tip 与「向量数据库深入」专题的分工（第 135 天补充）
PG 通过 `pgvector` 扩展提供向量类型与近邻检索（HNSW / IVFFlat 两种索引），因此「用不用 PG 存向量」
是选型阶段的常见问题。分工是：**本专题讲 PG 自身**（SQL、高级特性、索引详解、备份恢复、性能调优，
以及 pgvector 的安装与建索引写法），[向量数据库深入](../../VectorDatabase/index.md) 讲**向量检索的引擎侧机制**——
HNSW 的三参数各自换到什么、量化能省多少内存、带过滤条件的检索为什么会让召回崩（选择性悬崖）、
pgvector 的迭代扫描怎么开、内存与容量怎么按三段做预算。

判据一句话：**「数据已经在 PG 里、能不能不引新组件」看本专题；「引了之后参数怎么定、容量怎么算」看那边。**
把选型问题当机制问题处理（或反过来）是本库最常见的一次误判——选型错了要换组件，调参错了只需改配置，
两者的成本差一个数量级。
:::
