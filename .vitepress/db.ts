export const DBOverview = [
  {
    text: "数据库概述",
    link: "/docs/DB/Overview/index.md",
  },
];
export const DataModeling = [
  {
    text: "数据建模",
    link: "/docs/DB/DataModeling/index.md",
    items: [
      { text: "数据建模概述", link: "/docs/DB/DataModeling/Overview/index.md" },
      { text: "核心概念", link: "/docs/DB/DataModeling/CoreConcepts/index.md" },
      { text: "ER 图与建模步骤", link: "/docs/DB/DataModeling/ERDiagram/index.md" },
      { text: "范式与函数依赖", link: "/docs/DB/DataModeling/Normalization/index.md" },
      { text: "反范式与权衡", link: "/docs/DB/DataModeling/Denormalization/index.md" },
      { text: "设计原则与规范", link: "/docs/DB/DataModeling/DesignPrinciples/index.md" },
      { text: "建模工具选型", link: "/docs/DB/DataModeling/ModelingTools/index.md" },
      { text: "实战：内容社区数据库设计", link: "/docs/DB/DataModeling/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/DataModeling/FAQ/index.md" },
    ],
  },
];

export const NoRelational = [
  {
    text: "非关系型数据库",
    link: "/docs/DB/NoRelational/index.md",
    items: [
      {
        text: "Redis",
        link: "/docs/DB/NoRelational/Redis/index.md",
        collapsed: true,
        items: [
          { text: "Redis 概述", link: "/docs/DB/NoRelational/Redis/Overview/index.md" },
          { text: "安装与配置", link: "/docs/DB/NoRelational/Redis/Install/index.md" },
          { text: "通用命令", link: "/docs/DB/NoRelational/Redis/Command/index.md" },
          { text: "String 与 Hash", link: "/docs/DB/NoRelational/Redis/StringHash/index.md" },
          { text: "List / Set / ZSet", link: "/docs/DB/NoRelational/Redis/ListSetZSet/index.md" },
          { text: "过期与淘汰策略", link: "/docs/DB/NoRelational/Redis/ExpireEvict/index.md" },
          { text: "持久化 RDB / AOF", link: "/docs/DB/NoRelational/Redis/Persistence/index.md" },
          { text: "发布订阅与事务", link: "/docs/DB/NoRelational/Redis/PubSubTransaction/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/DB/NoRelational/Redis/FAQ/index.md" },
          {
            text: "Redis 进阶",
            link: "/docs/DB/NoRelational/Redis/Advanced/index.md",
            collapsed: true,
            items: [
              { text: "Redis 进阶导览", link: "/docs/DB/NoRelational/Redis/Advanced/index.md" },
              { text: "主从复制", link: "/docs/DB/NoRelational/Redis/Advanced/Replication/index.md" },
              { text: "哨兵高可用", link: "/docs/DB/NoRelational/Redis/Advanced/Sentinel/index.md" },
              { text: "Cluster 分片集群", link: "/docs/DB/NoRelational/Redis/Advanced/Cluster/index.md" },
              { text: "缓存设计", link: "/docs/DB/NoRelational/Redis/Advanced/CacheDesign/index.md" },
              { text: "缓存防护", link: "/docs/DB/NoRelational/Redis/Advanced/CacheProtection/index.md" },
              { text: "分布式锁与 Lua", link: "/docs/DB/NoRelational/Redis/Advanced/DistributedLock/index.md" },
              { text: "性能调优", link: "/docs/DB/NoRelational/Redis/Advanced/Performance/index.md" },
              { text: "版本演进与升级迁移", link: "/docs/DB/NoRelational/Redis/Advanced/VersionMigration/index.md" },
              { text: "实战：高可用缓存集群", link: "/docs/DB/NoRelational/Redis/Advanced/Practice/index.md" },
              { text: "进阶常见问题", link: "/docs/DB/NoRelational/Redis/Advanced/FAQ/index.md" },
            ],
          },
        ],
      },
      {
        text: "MongoDB",
        link: "/docs/DB/NoRelational/MongoDB/index.md",
        collapsed: true,
        items: [
          { text: "MongoDB 概述", link: "/docs/DB/NoRelational/MongoDB/Overview/index.md" },
          { text: "安装与连接", link: "/docs/DB/NoRelational/MongoDB/Install/index.md" },
          { text: "文档与集合", link: "/docs/DB/NoRelational/MongoDB/DocumentCollection/index.md" },
          { text: "增删改查（CRUD）", link: "/docs/DB/NoRelational/MongoDB/Crud/index.md" },
          { text: "索引优化", link: "/docs/DB/NoRelational/MongoDB/Index/index.md" },
          { text: "聚合管道", link: "/docs/DB/NoRelational/MongoDB/Aggregation/index.md" },
          { text: "副本集", link: "/docs/DB/NoRelational/MongoDB/ReplicaSet/index.md" },
          { text: "分片集群", link: "/docs/DB/NoRelational/MongoDB/Sharding/index.md" },
          { text: "备份与恢复", link: "/docs/DB/NoRelational/MongoDB/BackupRestore/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/DB/NoRelational/MongoDB/FAQ/index.md" },
        ],
      },
      {
        text: "Elasticsearch",
        link: "/docs/DB/NoRelational/Elasticsearch/index.md",
        collapsed: true,
        items: [
          { text: "ES 概述与安装", link: "/docs/DB/NoRelational/Elasticsearch/Overview/index.md" },
          { text: "索引与映射", link: "/docs/DB/NoRelational/Elasticsearch/IndexMapping/index.md" },
          { text: "查询 DSL", link: "/docs/DB/NoRelational/Elasticsearch/QueryDSL/index.md" },
          { text: "聚合分析", link: "/docs/DB/NoRelational/Elasticsearch/Aggregation/index.md" },
          { text: "中文分词与 IK 分析器", link: "/docs/DB/NoRelational/Elasticsearch/ChineseAnalyzer/index.md" },
          { text: "集群架构与高可用", link: "/docs/DB/NoRelational/Elasticsearch/Cluster/index.md" },
          { text: "实战：商品搜索服务", link: "/docs/DB/NoRelational/Elasticsearch/Practice/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/DB/NoRelational/Elasticsearch/FAQ/index.md" },
        ],
      },
    ],
  },
];
export const SQLOptimization = [
  {
    text: "SQL 优化",
    link: "/docs/DB/Relational/SQLOptimization/index.md",
    collapsed: true,
    items: [
      { text: "SQL 优化概述", link: "/docs/DB/Relational/SQLOptimization/Overview/index.md" },
      { text: "执行计划", link: "/docs/DB/Relational/SQLOptimization/ExplainPlan/index.md" },
      { text: "索引原理与失效场景", link: "/docs/DB/Relational/SQLOptimization/IndexPrinciple/index.md" },
      { text: "慢查询定位与分析", link: "/docs/DB/Relational/SQLOptimization/SlowQuery/index.md" },
      { text: "分页优化", link: "/docs/DB/Relational/SQLOptimization/Pagination/index.md" },
      { text: "JOIN 优化", link: "/docs/DB/Relational/SQLOptimization/JoinOptimization/index.md" },
      { text: "锁与事务对查询的影响", link: "/docs/DB/Relational/SQLOptimization/LockTransaction/index.md" },
      { text: "优化案例", link: "/docs/DB/Relational/SQLOptimization/CaseStudy/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/Relational/SQLOptimization/FAQ/index.md" },
    ],
  },
];
export const Sharding = [
  {
    text: "分库分表",
    link: "/docs/DB/Relational/Sharding/index.md",
    collapsed: true,
    items: [
      { text: "分库分表概述与决策", link: "/docs/DB/Relational/Sharding/Overview/index.md" },
      { text: "拆分策略与分片键设计", link: "/docs/DB/Relational/Sharding/Strategy/index.md" },
      { text: "分布式 ID 生成", link: "/docs/DB/Relational/Sharding/IDGeneration/index.md" },
      { text: "ShardingSphere 主线", link: "/docs/DB/Relational/Sharding/ShardingSphere/index.md" },
      { text: "跨分片查询与分布式事务", link: "/docs/DB/Relational/Sharding/CrossShard/index.md" },
      { text: "平滑迁移：从单库到分片", link: "/docs/DB/Relational/Sharding/Migration/index.md" },
      { text: "实战：订单系统分库分表", link: "/docs/DB/Relational/Sharding/Practice/index.md" },
      { text: "常见问题与排错", link: "/docs/DB/Relational/Sharding/FAQ/index.md" },
    ],
  },
];
export const Relational = [
  {
    text: "关系型数据库",
    link: "/docs/DB/Relational/index.md",
    items: [
      {
        text: "MySQL",
        link: "/docs/DB/Relational/MySQL/index.md",
        collapsed: true,
        items: [
          { text: "MySQL 概述", link: "/docs/DB/Relational/MySQL/Overview/index.md" },
          { text: "安装与配置", link: "/docs/DB/Relational/MySQL/Install/index.md" },
          { text: "核心概念", link: "/docs/DB/Relational/MySQL/BasicConcept/index.md" },
          { text: "库表操作（DDL）", link: "/docs/DB/Relational/MySQL/DatabaseTable/index.md" },
          { text: "数据增删改查（DML）", link: "/docs/DB/Relational/MySQL/DataManipulation/index.md" },
          { text: "查询进阶（DQL）", link: "/docs/DB/Relational/MySQL/Query/index.md" },
          { text: "事务与隔离级别", link: "/docs/DB/Relational/MySQL/Transaction/index.md" },
          { text: "索引与性能优化", link: "/docs/DB/Relational/MySQL/IndexPerformance/index.md" },
          {
            text: "索引深入",
            link: "/docs/DB/Relational/MySQL/IndexDeepDive/index.md",
            collapsed: true,
            items: [
              { text: "B+ 树原理", link: "/docs/DB/Relational/MySQL/IndexDeepDive/BTree/index.md" },
              { text: "联合索引与最左前缀", link: "/docs/DB/Relational/MySQL/IndexDeepDive/CompositeIndex/index.md" },
              { text: "索引失效场景全集", link: "/docs/DB/Relational/MySQL/IndexDeepDive/IndexFailure/index.md" },
              { text: "覆盖索引与索引下推", link: "/docs/DB/Relational/MySQL/IndexDeepDive/CoveringIndex/index.md" },
              { text: "排序与分组优化", link: "/docs/DB/Relational/MySQL/IndexDeepDive/SortGroup/index.md" },
              { text: "索引设计方法论", link: "/docs/DB/Relational/MySQL/IndexDeepDive/Design/index.md" },
              { text: "实战：慢查询优化案例", link: "/docs/DB/Relational/MySQL/IndexDeepDive/CaseStudy/index.md" },
              { text: "常见问题与最佳实践", link: "/docs/DB/Relational/MySQL/IndexDeepDive/FAQ/index.md" },
            ],
          },
          { text: "常见问题与最佳实践", link: "/docs/DB/Relational/MySQL/FAQ/index.md" },
        ],
      },
      {
        text: "PostgreSQL",
        link: "/docs/DB/Relational/PostgreSQL/index.md",
        collapsed: true,
        items: [
          { text: "PostgreSQL 概述", link: "/docs/DB/Relational/PostgreSQL/Overview/index.md" },
          { text: "安装与配置", link: "/docs/DB/Relational/PostgreSQL/Install/index.md" },
          { text: "SQL 基础", link: "/docs/DB/Relational/PostgreSQL/SqlBasic/index.md" },
          { text: "高级特性", link: "/docs/DB/Relational/PostgreSQL/Advanced/index.md" },
          { text: "索引详解", link: "/docs/DB/Relational/PostgreSQL/Index/index.md" },
          { text: "备份与恢复", link: "/docs/DB/Relational/PostgreSQL/BackupRestore/index.md" },
          { text: "性能调优", link: "/docs/DB/Relational/PostgreSQL/Performance/index.md" },
          { text: "实战：博客系统数据库", link: "/docs/DB/Relational/PostgreSQL/Practice/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/DB/Relational/PostgreSQL/FAQ/index.md" },
        ],
      },
      ...SQLOptimization,
      ...Sharding,
    ],
  },
];
export const TimeSeries = [
  {
    text: "时序数据库",
    link: "/docs/DB/TimeSeries/index.md",
    items: [
      { text: "时序数据库概述与选型", link: "/docs/DB/TimeSeries/Overview/index.md" },
      { text: "数据模型", link: "/docs/DB/TimeSeries/DataModel/index.md" },
      { text: "InfluxDB 深入", link: "/docs/DB/TimeSeries/InfluxDB/index.md" },
      { text: "TDengine 深入", link: "/docs/DB/TimeSeries/TDengine/index.md" },
      { text: "查询与降采样", link: "/docs/DB/TimeSeries/Query/index.md" },
      { text: "存储与保留策略", link: "/docs/DB/TimeSeries/Storage/index.md" },
      { text: "实战：设备监控指标平台", link: "/docs/DB/TimeSeries/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/TimeSeries/FAQ/index.md" },
    ],
  },
];
