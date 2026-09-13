# Elasticsearch

<p style="text-align:center;"><img src="./assets/elasticsearch-logo.png" style="zoom:75%;" /></p>

Elasticsearch（简称 ES）是基于 Apache Lucene 的**分布式搜索与分析引擎**，提供全文检索、结构化查询、聚合分析和近实时（NRT）能力，是日志分析（ELK）、商品搜索、向量检索等场景的基础设施。本专题面向需要在项目中落地 ES 的后端与数据工程师，从概念到集群运维完整走一遍。

:::info 当前版本（2026-09 核对）
主线为 **Elasticsearch 9.5.3**（2026-09-03 发布）；9.0 于 2025-04-15 发布，8.x 处于维护期（升级到 9.x 前需先升到最后一个 8.x 小版本）。Java API Client 与 RestHighLevelClient（8.0 已移除）等历史客户端差异见各页说明。
:::

## 目录

- [ES 概述与安装](Overview/index.md)
- [索引与映射（Index & Mapping）](IndexMapping/index.md)
- [查询 DSL（Query DSL）](QueryDSL/index.md)
- [聚合分析（Aggregations）](Aggregation/index.md)
- [中文分词与 IK 分析器](ChineseAnalyzer/index.md)
- [集群架构与高可用](Cluster/index.md)
- [实战：商品搜索服务](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [MongoDB](../MongoDB/index.md)：同为文档型存储，选型对比见概述页
- [Redis](../Redis/index.md)：缓存层常与 ES 组合使用
- [MySQL](../../Relational/MySQL/index.md)：ES 常作为 MySQL 的「搜索外挂」，同步方案见实战页
- [SQL 优化](../../Relational/SQLOptimization/index.md)：数据库侧的检索优化，与 ES 侧互补
