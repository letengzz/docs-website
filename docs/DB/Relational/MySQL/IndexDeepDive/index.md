# MySQL 索引深入

<p style="text-align:center;"><img src="./assets/mysql-logo.png" style="zoom:75%;" /></p>

在掌握索引基础（见 [索引与性能优化](../IndexPerformance/index.md)）之后，本专题深入 **InnoDB 存储引擎层**：B+ 树页结构、联合索引与最左前缀、索引失效全集、覆盖索引与索引下推、排序优化、索引设计与维护，并通过实战案例把方法论落地。

版本说明：默认基于 **MySQL 8.4 LTS**，涉及 9.x 新特性（如 9.7 LTS 的 Hypergraph 优化器）时单独标注；MySQL 8.0 已于 2026 年 4 月停止维护。

- [B+ 树原理](BTree/index.md)
- [联合索引与最左前缀](CompositeIndex/index.md)
- [索引失效场景全集](IndexFailure/index.md)
- [覆盖索引与索引下推](CoveringIndex/index.md)
- [排序与分组优化](SortGroup/index.md)
- [索引设计方法论](Design/index.md)
- [实战：慢查询优化案例](CaseStudy/index.md)
- [常见问题与最佳实践](FAQ/index.md)
