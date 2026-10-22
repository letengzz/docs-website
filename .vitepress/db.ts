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
export const ClickHouse = [
  {
    text: "ClickHouse",
    link: "/docs/DB/ClickHouse/index.md",
    items: [
      { text: "列式存储与 ClickHouse 概述", link: "/docs/DB/ClickHouse/Overview/index.md" },
      { text: "MergeTree 引擎", link: "/docs/DB/ClickHouse/MergeTree/index.md" },
      { text: "分区与索引", link: "/docs/DB/ClickHouse/PartitionIndex/index.md" },
      { text: "数据类型与 SQL 基础", link: "/docs/DB/ClickHouse/SqlBasic/index.md" },
      { text: "物化视图与预聚合", link: "/docs/DB/ClickHouse/MaterializedView/index.md" },
      { text: "副本与分片", link: "/docs/DB/ClickHouse/Cluster/index.md" },
      { text: "实战：用户行为分析", link: "/docs/DB/ClickHouse/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/ClickHouse/FAQ/index.md" },
    ],
  },
];
export const Neo4j = [
  {
    text: "图数据库 Neo4j",
    link: "/docs/DB/Neo4j/index.md",
    items: [
      { text: "图模型与 Neo4j 概述", link: "/docs/DB/Neo4j/Overview/index.md" },
      { text: "安装与快速上手", link: "/docs/DB/Neo4j/Install/index.md" },
      { text: "Cypher 查询语言", link: "/docs/DB/Neo4j/Cypher/index.md" },
      { text: "索引与约束", link: "/docs/DB/Neo4j/IndexConstraint/index.md" },
      { text: "图算法与 GDS", link: "/docs/DB/Neo4j/GDS/index.md" },
      { text: "架构与集群", link: "/docs/DB/Neo4j/Cluster/index.md" },
      { text: "应用集成", link: "/docs/DB/Neo4j/Integration/index.md" },
      { text: "实战：社交关注图谱", link: "/docs/DB/Neo4j/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/Neo4j/FAQ/index.md" },
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
export const Middleware = [
  {
    text: "数据库中间件",
    link: "/docs/DB/Middleware/index.md",
    items: [
      { text: "中间件全景与选型", link: "/docs/DB/Middleware/Overview/index.md" },
      { text: "读写分离工程化", link: "/docs/DB/Middleware/ReadWriteSplit/index.md" },
      { text: "影子库与全链路压测", link: "/docs/DB/Middleware/ShadowDatabase/index.md" },
      { text: "代理形态与运维", link: "/docs/DB/Middleware/ProxyMode/index.md" },
      { text: "连接治理", link: "/docs/DB/Middleware/ConnectionGovernance/index.md" },
      { text: "中间件视角的分布式事务", link: "/docs/DB/Middleware/DistributedTransaction/index.md" },
      { text: "实战：为订单服务接入中间件", link: "/docs/DB/Middleware/Practice/index.md" },
      { text: "常见问题与排错", link: "/docs/DB/Middleware/FAQ/index.md" },
    ],
  },
];
export const CDC = [
  {
    text: "数据同步与 CDC",
    link: "/docs/DB/CDC/index.md",
    items: [
      { text: "同步全景与选型", link: "/docs/DB/CDC/Overview/index.md" },
      { text: "binlog 与 CDC 原理", link: "/docs/DB/CDC/Binlog/index.md" },
      { text: "Debezium", link: "/docs/DB/CDC/Debezium/index.md" },
      { text: "Canal 与 Maxwell", link: "/docs/DB/CDC/Canal/index.md" },
      { text: "Flink CDC", link: "/docs/DB/CDC/FlinkCDC/index.md" },
      { text: "一致性保障", link: "/docs/DB/CDC/Consistency/index.md" },
      { text: "生产运维", link: "/docs/DB/CDC/Ops/index.md" },
      { text: "实战：博客平台 MySQL → ES 检索同步", link: "/docs/DB/CDC/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/CDC/FAQ/index.md" },
    ],
  },
];
export const DataWarehouse = [
  {
    text: "数仓建模",
    link: "/docs/DB/DataWarehouse/index.md",
    items: [
      { text: "概述：数仓全景与四种建模方法论", link: "/docs/DB/DataWarehouse/Overview/index.md" },
      { text: "分层设计", link: "/docs/DB/DataWarehouse/Layering/index.md" },
      { text: "维度建模", link: "/docs/DB/DataWarehouse/DimensionalModeling/index.md" },
      { text: "事实表与维度表设计", link: "/docs/DB/DataWarehouse/FactAndDimension/index.md" },
      { text: "缓慢变化维与拉链表", link: "/docs/DB/DataWarehouse/SCD/index.md" },
      { text: "粒度与聚合设计", link: "/docs/DB/DataWarehouse/Grain/index.md" },
      { text: "数据质量、血缘与调度", link: "/docs/DB/DataWarehouse/Quality/index.md" },
      { text: "实战：电商订单域数仓", link: "/docs/DB/DataWarehouse/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/DataWarehouse/FAQ/index.md" },
    ],
  },
];
export const VectorDatabase = [
  {
    text: "向量数据库深入",
    link: "/docs/DB/VectorDatabase/index.md",
    items: [
      { text: "概述：向量检索的四条边界", link: "/docs/DB/VectorDatabase/Overview/index.md" },
      { text: "HNSW 原理深入", link: "/docs/DB/VectorDatabase/HNSW/index.md" },
      { text: "索引算法全景", link: "/docs/DB/VectorDatabase/IndexAlgorithms/index.md" },
      { text: "量化深入", link: "/docs/DB/VectorDatabase/Quantization/index.md" },
      { text: "过滤与元数据检索", link: "/docs/DB/VectorDatabase/Filtering/index.md" },
      { text: "混合检索", link: "/docs/DB/VectorDatabase/HybridSearch/index.md" },
      { text: "运维与容量", link: "/docs/DB/VectorDatabase/Operations/index.md" },
      { text: "实战：企业知识库检索链路", link: "/docs/DB/VectorDatabase/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/VectorDatabase/FAQ/index.md" },
    ],
  },
];
export const BigData = [
  {
    text: "大数据生态",
    link: "/docs/DB/BigData/index.md",
    items: [
      { text: "概述：大数据栈的四层与四条主线", link: "/docs/DB/BigData/Overview/index.md" },
      { text: "Hadoop：HDFS 与 YARN", link: "/docs/DB/BigData/Hadoop/index.md" },
      { text: "Hive：数仓 SQL 层", link: "/docs/DB/BigData/Hive/index.md" },
      { text: "Spark：批与微批引擎", link: "/docs/DB/BigData/Spark/index.md" },
      { text: "Flink：有状态流处理", link: "/docs/DB/BigData/Flink/index.md" },
      { text: "生态组件：消息、湖表与调度", link: "/docs/DB/BigData/Ecosystem/index.md" },
      { text: "选型与架构决策", link: "/docs/DB/BigData/Selection/index.md" },
      { text: "实战：从 binlog 到实时看板", link: "/docs/DB/BigData/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/BigData/FAQ/index.md" },
    ],
  },
];
export const DataGovernance = [
  {
    text: "数据治理入门",
    link: "/docs/DB/DataGovernance/index.md",
    items: [
      { text: "概述：数据治理的四条边界", link: "/docs/DB/DataGovernance/Overview/index.md" },
      { text: "元数据与资产目录", link: "/docs/DB/DataGovernance/Metadata/index.md" },
      { text: "数据血缘与影响分析", link: "/docs/DB/DataGovernance/Lineage/index.md" },
      { text: "数据质量规则与闭环", link: "/docs/DB/DataGovernance/DataQuality/index.md" },
      { text: "数据标准与主数据", link: "/docs/DB/DataGovernance/StandardsMasterData/index.md" },
      { text: "组织、角色与流程", link: "/docs/DB/DataGovernance/OrgAndProcess/index.md" },
      { text: "实战：五个源系统到一个治理体系", link: "/docs/DB/DataGovernance/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/DataGovernance/FAQ/index.md" },
    ],
  },
];

export const PartitionArchival = [
  {
    text: "分区分表与冷热分离",
    link: "/docs/DB/PartitionArchival/index.md",
    items: [
      { text: "总览：四层结构与五个必失点", link: "/docs/DB/PartitionArchival/Overview/index.md" },
      { text: "分区策略：分区键与粒度", link: "/docs/DB/PartitionArchival/PartitionStrategy/index.md" },
      { text: "分区维护：ATTACH、DETACH 与默认分区", link: "/docs/DB/PartitionArchival/PartitionOps/index.md" },
      { text: "跨分区查询：裁剪为什么没生效", link: "/docs/DB/PartitionArchival/CrossPartition/index.md" },
      { text: "冷热分层：四档存储与成本账", link: "/docs/DB/PartitionArchival/HotColdTiering/index.md" },
      { text: "在线归档：不停机搬走一段历史", link: "/docs/DB/PartitionArchival/OnlineArchive/index.md" },
      { text: "保留策略与合规删除", link: "/docs/DB/PartitionArchival/RetentionCompliance/index.md" },
      { text: "实战：审计日志的 13 个月", link: "/docs/DB/PartitionArchival/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/DB/PartitionArchival/FAQ/index.md" },
    ],
  },
];

export const DatabaseInternals = [
  {
    text: "数据库内核与存储引擎",
    link: "/docs/DB/DatabaseInternals/index.md",
    items: [
      { text: "概述：一次查询的一生与三种放大", link: "/docs/DB/DatabaseInternals/Overview/index.md" },
      { text: "页与缓冲池", link: "/docs/DB/DatabaseInternals/BufferPool/index.md" },
      { text: "B+ 树：三层树怎么撑住一亿行", link: "/docs/DB/DatabaseInternals/BPlusTree/index.md" },
      { text: "LSM 树：用写放大换写吞吐", link: "/docs/DB/DatabaseInternals/LsmTree/index.md" },
      { text: "WAL 与崩溃恢复", link: "/docs/DB/DatabaseInternals/WalRecovery/index.md" },
      { text: "执行器：算子是流水线还是批处理", link: "/docs/DB/DatabaseInternals/Executor/index.md" },
      { text: "优化器：代价模型为什么会算错", link: "/docs/DB/DatabaseInternals/Optimizer/index.md" },
      { text: "实战：给一条慢查询做内核级体检", link: "/docs/DB/DatabaseInternals/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/DB/DatabaseInternals/FAQ/index.md" },
    ],
  },
];

export const FullTextSearch = [
  {
    text: "全文检索与搜索工程",
    link: "/docs/DB/FullTextSearch/index.md",
    items: [
      { text: "总览：四段结构与五个必失点", link: "/docs/DB/FullTextSearch/Overview/index.md" },
      { text: "文本分析：分词是索引契约", link: "/docs/DB/FullTextSearch/TextAnalysis/index.md" },
      { text: "索引设计：倒排、字段与体积", link: "/docs/DB/FullTextSearch/IndexDesign/index.md" },
      { text: "相关性排序：BM25 与业务加权", link: "/docs/DB/FullTextSearch/Relevance/index.md" },
      { text: "索引更新：写完多久能搜到", link: "/docs/DB/FullTextSearch/IndexUpdate/index.md" },
      { text: "查询理解：纠错、扩展与兜底", link: "/docs/DB/FullTextSearch/QueryUnderstanding/index.md" },
      { text: "召回评估：没有基线就没有改动", link: "/docs/DB/FullTextSearch/Evaluation/index.md" },
      { text: "性能与容量：先量再优化", link: "/docs/DB/FullTextSearch/Performance/index.md" },
      { text: "实战：10 万工单的搜索链路", link: "/docs/DB/FullTextSearch/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/DB/FullTextSearch/FAQ/index.md" },
    ],
  },
];

export const Lakehouse = [
  {
    text: "数据湖与湖仓一体",
    link: "/docs/DB/Lakehouse/index.md",
    items: [
      { text: "总览：四层结构与五个必失点", link: "/docs/DB/Lakehouse/Overview/index.md" },
      { text: "表格式：三种元数据模型", link: "/docs/DB/Lakehouse/TableFormat/index.md" },
      { text: "元数据层与 catalog", link: "/docs/DB/Lakehouse/Metadata/index.md" },
      { text: "提交协议与并发写", link: "/docs/DB/Lakehouse/WritePath/index.md" },
      { text: "增量读：边界与代价", link: "/docs/DB/Lakehouse/IncrementalRead/index.md" },
      { text: "小文件治理", link: "/docs/DB/Lakehouse/SmallFiles/index.md" },
      { text: "时间旅行、保留与孤儿清理", link: "/docs/DB/Lakehouse/Retention/index.md" },
      { text: "引擎接入与 data skipping", link: "/docs/DB/Lakehouse/QueryEngine/index.md" },
      { text: "实战：从 0 搭一个可验收的湖仓", link: "/docs/DB/Lakehouse/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/DB/Lakehouse/FAQ/index.md" },
    ],
  },
];

export const SchemaEvolution = [
  {
    text: "数据库变更与在线 Schema 演进",
    link: "/docs/DB/SchemaEvolution/index.md",
    items: [
      { text: "总览：四类风险与五步流程", link: "/docs/DB/SchemaEvolution/Overview/index.md" },
      { text: "扩展-收缩：拆成三次发布", link: "/docs/DB/SchemaEvolution/ExpandContract/index.md" },
      { text: "重写边界：哪些 DDL 真的重建表", link: "/docs/DB/SchemaEvolution/RewriteBoundary/index.md" },
      { text: "锁与队列：DDL 怎么把读堵死", link: "/docs/DB/SchemaEvolution/LockQueue/index.md" },
      { text: "MySQL 5.7：已停止维护的存量路径", link: "/docs/DB/SchemaEvolution/MySQL57/index.md" },
      { text: "MySQL 8.4：INSTANT 与原子 DDL", link: "/docs/DB/SchemaEvolution/MySQL84/index.md" },
      { text: "数据回填：批次、水位与速率", link: "/docs/DB/SchemaEvolution/Backfill/index.md" },
      { text: "应用兼容：N/N-1 矩阵与回滚边界", link: "/docs/DB/SchemaEvolution/AppSchemaCompat/index.md" },
      { text: "实战：给订单表加一列并回填", link: "/docs/DB/SchemaEvolution/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/DB/SchemaEvolution/FAQ/index.md" },
    ],
  },
];

export const ConnectionPool = [
  {
    text: "连接池与连接生命周期",
    link: "/docs/DB/ConnectionPool/index.md",
    items: [
      { text: "池的内部：一次借用的路径", link: "/docs/DB/ConnectionPool/PoolInternals/index.md" },
      { text: "池大小：从公式到实测膝点", link: "/docs/DB/ConnectionPool/Sizing/index.md" },
      { text: "连接生命周期：五个阀门谁先关", link: "/docs/DB/ConnectionPool/Lifetime/index.md" },
      { text: "事务边界与池：什么时候还、什么时候脏", link: "/docs/DB/ConnectionPool/TransactionBoundary/index.md" },
      { text: "泄漏定位：倒推到那一行没 close", link: "/docs/DB/ConnectionPool/LeakDetection/index.md" },
      { text: "双层池与代理：两层上限一起算", link: "/docs/DB/ConnectionPool/DoubleLayer/index.md" },
      { text: "多数据源与多租户：池的维度", link: "/docs/DB/ConnectionPool/MultiDatasource/index.md" },
      { text: "故障与自愈：重启、切换、连接风暴", link: "/docs/DB/ConnectionPool/FailureRecovery/index.md" },
      { text: "观测与告警：四指标三陷阱", link: "/docs/DB/ConnectionPool/Observability/index.md" },
      { text: "常见问题与分诊", link: "/docs/DB/ConnectionPool/FAQ/index.md" },
    ],
  },
];

export const AccessControl = [
  {
    text: "数据库访问控制与审计",
    link: "/docs/DB/AccessControl/index.md",
    items: [
      { text: "四层结构与五个必失点", link: "/docs/DB/AccessControl/Overview/index.md" },
      { text: "角色、继承与 SET ROLE", link: "/docs/DB/AccessControl/RoleModel/index.md" },
      { text: "最小权限：从 GRANT 到默认权限", link: "/docs/DB/AccessControl/LeastPrivilege/index.md" },
      { text: "行级安全：策略的写法与边界", link: "/docs/DB/AccessControl/RowLevelSecurity/index.md" },
      { text: "越权路径：视图、函数与 search_path", link: "/docs/DB/AccessControl/PrivilegeEscalation/index.md" },
      { text: "审计：三种位置与各自的成本", link: "/docs/DB/AccessControl/AuditTrail/index.md" },
      { text: "权限生命周期：申请、复核与回收", link: "/docs/DB/AccessControl/Lifecycle/index.md" },
      { text: "异常访问检测与处置", link: "/docs/DB/AccessControl/Detection/index.md" },
      { text: "实战：一套可验收的权限基线", link: "/docs/DB/AccessControl/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/DB/AccessControl/FAQ/index.md" },
    ],
  },
];

export const GeoMap = [
  {
    text: "地理信息与地图工程",
    link: "/docs/DB/GeoMap/index.md",
    items: [
      { text: "总览：四个问题、三段链路与五档成熟度", link: "/docs/DB/GeoMap/Overview/index.md" },
      { text: "坐标系与投影：位置到底怎么记", link: "/docs/DB/GeoMap/CRS/index.md" },
      { text: "空间建模与索引：几何类型与 GiST", link: "/docs/DB/GeoMap/Modeling/index.md" },
      { text: "空间查询与距离：从「圈一个范围」到「排序取最近」", link: "/docs/DB/GeoMap/Query/index.md" },
      { text: "瓦片服务与切片：把地图切成可缓存的方块", link: "/docs/DB/GeoMap/Tiles/index.md" },
      { text: "前端渲染与交互：矢量瓦片、图层与命中", link: "/docs/DB/GeoMap/Render/index.md" },
      { text: "地理围栏与轨迹：判定、去抖与抽稀", link: "/docs/DB/GeoMap/GeoFence/index.md" },
      { text: "地图数据合规与离线交付", link: "/docs/DB/GeoMap/Compliance/index.md" },
      { text: "实战：门店选址与配送范围", link: "/docs/DB/GeoMap/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/DB/GeoMap/FAQ/index.md" },
    ],
  },
];
