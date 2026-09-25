# SQL 优化

<p style="text-align:center;"><img src="./assets/sqlopt-logo.png" alt="SQL 优化" style="zoom:75%;" /></p>

SQL 优化是通过**执行计划分析、索引设计、SQL 改写**等手段让查询更快更稳的方法论。本专题以 MySQL 8.4 LTS 为主，覆盖执行计划、索引原理、慢查询定位、分页与 JOIN 优化、锁与事务影响，以及真实优化案例。

- [SQL 优化概述](Overview/index.md)
- [执行计划](ExplainPlan/index.md)
- [索引原理与失效场景](IndexPrinciple/index.md)
- [慢查询定位与分析](SlowQuery/index.md)
- [分页优化](Pagination/index.md)
- [JOIN 优化](JoinOptimization/index.md)
- [锁与事务对查询的影响](LockTransaction/index.md)
- [优化案例](CaseStudy/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 与分库分表的分工

本专题解决的是**单机内的查询优化**：让一条 SQL 在单库单表上跑得更快。当优化已经把单机榨干（索引、执行计划、锁粒度都到位）却仍然装不下或写不进时，才轮到[分库分表](../Sharding/index.md)——那是把数据**分散到多个库表**的水平扩展方案，代价是永久失去跨分片 JOIN、全局排序与唯一约束。

判据很简单：**能用索引解决的，不要用分片解决**。分片之后本专题的手段依然有效，而且会变得更关键——每个分片都是一台独立的单机，落在单个分片上的查询仍要用执行计划和索引去调。

- [分库分表 · 概述与决策](../Sharding/Overview/index.md)：容量评估换算与「要不要拆」的决策树，明确单机优化的边界在哪
- [分库分表 · 跨分片查询](../Sharding/CrossShard/index.md)：深分页、JOIN、聚合在分片后的改写方式
