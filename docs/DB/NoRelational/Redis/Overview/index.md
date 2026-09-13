# Redis 概述

Redis（Remote Dictionary Server）是一个开源的高性能**内存键值数据库**，常被用作缓存、消息队列和轻量存储，是 Web 应用中最常用的 NoSQL 组件之一。

## Redis 是什么

- 数据存储在**内存**中，读写速度极快（单实例可达十万级 QPS）。
- 以 **key-value** 为基本模型，value 支持多种数据结构。
- 支持持久化、过期时间、发布订阅、事务、Lua 脚本等能力。
- 默认端口：`6379`。

## 核心特性

1. 数据结构丰富：String、Hash、List、Set、ZSet、Stream、Bitmap、HyperLogLog、Geo。
2. 高性能：基于内存 + 事件驱动模型；Redis 6.0 起引入 I/O 多线程，8.x 进一步优化吞吐与延迟。
3. 原子操作：`INCR`、`SETNX` 等命令天然原子，适合计数器和分布式锁。
4. 持久化：RDB 快照与 AOF 日志，可配置混合持久化。
5. 高可用：主从复制、哨兵（Sentinel）、集群（Cluster）。
6. TTL：每个 key 可设置过期时间，适合缓存场景。

## 版本现状（2026 年 9 月核对）

Redis 采用 `MAJOR.MINOR.PATCH` 版本结构，官方把每个版本分为 **Standard**（标准支持，下一个小版本发布后再提供 6 个月修复）与 **Extended**（扩展支持，自发布起 5 年）两类：

| 版本 | 支持类型 | 状态 | EOL |
| --- | --- | --- | --- |
| Redis 8.10 | Standard | GA，**当前最新稳定版** | 待官方公布 |
| Redis 8.8 | Standard | GA（2026 年 Q2） | 待官方公布 |
| Redis 8.6 | Standard | GA（2026 年 2 月，最新补丁 8.6.2） | 待官方公布 |
| Redis 8.4 | Standard | GA | 待官方公布 |
| Redis 8.2 | Extended | GA | 2030-09-01 |
| Redis 8.0 | Standard | GA | 2026-12-01 |
| Redis 7.4 / 7.2 | Extended | 存量项目常见 | 2029-12-01 |
| Redis 6.2 | Extended | 仅存量项目使用 | 2027-04-01 |

::: tip
新项目推荐直接使用 **Redis 8.10**；要求长期稳定支持时选 **8.2**（Extended，支持到 2030-09-01）；7.x 存量项目升级前先做兼容性测试。完整的版本对比与升级路径见[版本演进与升级迁移](../Advanced/VersionMigration/index.md)。
:::

Redis 8 的许可为三选一：RSALv2、SSPLv1 或 AGPLv3，使用前请确认是否符合自身业务的许可要求。

## 与 Memcached 对比

| 特性 | Redis | Memcached |
| --- | --- | --- |
| 数据结构 | 丰富（字符串/哈希/列表等） | 仅字符串 |
| 持久化 | RDB / AOF | 不支持 |
| 高可用 | 主从/哨兵/集群 | 不支持（需外部方案） |
| 应用场景 | 缓存 + 消息 + 存储 | 纯缓存 |

## 应用场景

- **缓存**：热点数据、页面缓存、会话缓存。
- **排行榜**：ZSet 天然支持排序。
- **计数器**：点赞数、访问量、限流计数。
- **分布式锁**：`SETNX` + 过期时间。
- **消息队列**：List 或 Stream。
- **布隆过滤器**：防止缓存穿透。

## Redis 基本架构

![Redis 基本架构](./assets/redis-architecture.svg)

客户端通过 Redis 协议（RESP）连接服务端；服务端在内存中维护数据结构，并按配置把数据持久化到磁盘，同时支持主从复制。

## 学习路径

1. 安装与配置
2. 通用命令与五种常用数据结构
3. 过期与淘汰策略
4. 持久化 RDB / AOF
5. 发布订阅、事务与 Lua
6. **进阶部分**：[主从复制](../Advanced/Replication/index.md) → [哨兵高可用](../Advanced/Sentinel/index.md) → [缓存设计](../Advanced/CacheDesign/index.md) → [缓存防护](../Advanced/CacheProtection/index.md) → [性能调优](../Advanced/Performance/index.md) → [实战：高可用缓存集群](../Advanced/Practice/index.md)

## 相关链接

- Redis 官方文档：https://redis.io/docs/latest/
- Redis 命令参考：https://redis.io/docs/latest/commands/
- Redis 版本与支持周期：https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt
- Docker 镜像：https://hub.docker.com/_/redis
- RedisInsight 官方 GUI：[数据库客户端专题](../../../../Tools/DatabaseClients/RedisInsight/index.md)
- 进阶专题入口：[Redis 进阶](../Advanced/index.md)
