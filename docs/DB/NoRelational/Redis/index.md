# Redis

<p style="text-align:center;"><img src="./assets/redis-logo.png" style="zoom:75%;" /></p>

Redis（Remote Dictionary Server）是一个开源的高性能**内存键值数据库**，常被用作缓存、消息队列与轻量存储。本主题分「基础」与「进阶」两部分：基础讲单个 Redis 进程怎么用，进阶讲一组 Redis 实例怎么在生产环境稳定跑。

## 基础部分

- [Redis 概述](Overview/index.md)
- [安装与配置](Install/index.md)
- [通用命令](Command/index.md)
- [String 与 Hash](StringHash/index.md)
- [List / Set / ZSet](ListSetZSet/index.md)
- [过期与淘汰策略](ExpireEvict/index.md)
- [持久化 RDB / AOF](Persistence/index.md)
- [发布订阅与事务](PubSubTransaction/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 进阶部分

- [Redis 进阶导览](Advanced/index.md)
- [主从复制](Advanced/Replication/index.md)
- [哨兵高可用](Advanced/Sentinel/index.md)
- [Cluster 分片集群](Advanced/Cluster/index.md)
- [缓存设计](Advanced/CacheDesign/index.md)
- [缓存防护](Advanced/CacheProtection/index.md)
- [分布式锁与 Lua](Advanced/DistributedLock/index.md)
- [性能调优](Advanced/Performance/index.md)
- [版本演进与升级迁移](Advanced/VersionMigration/index.md)
- [实战：高可用缓存集群](Advanced/Practice/index.md)
- [进阶常见问题](Advanced/FAQ/index.md)

## 相关链接

- Redis 官方文档：https://redis.io/docs/latest/
- Redis 命令参考：https://redis.io/docs/latest/commands/
- Redis 版本与支持周期：https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt
- Docker 镜像：https://hub.docker.com/_/redis
- RedisInsight 官方 GUI：[数据库客户端专题](../../../Tools/DatabaseClients/RedisInsight/index.md)
