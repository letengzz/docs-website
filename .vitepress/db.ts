export const DBOverview = [
  {
    text: "数据库概述",
    link: "/docs/DB/Overview/index.md",
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
    ],
  },
];
