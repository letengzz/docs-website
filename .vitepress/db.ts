export const DBOverview = [
  {
    text: "数据库概述",
    link: "/docs/DB/Overview/index.md",
  },
];
export const NoRelational = [];
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
    ],
  },
];
