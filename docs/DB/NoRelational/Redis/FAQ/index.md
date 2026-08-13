# Redis 常见问题与最佳实践

## 连接问题

1. `Could not connect to Redis`：服务未启动、端口错误、防火墙拦截。

```shell
redis-cli ping
ss -lntp | grep 6379
```

2. `NOAUTH Authentication required`：需要认证。

```shell
redis-cli -a '密码'
```

3. 连接超时：检查 `timeout` 配置、网络质量、慢命令占用。

## 缓存三大问题

### 缓存穿透

请求的数据缓存和数据库都不存在。

解决：

1. 缓存空值，TTL 设短（如 60 秒）。
2. 布隆过滤器拦截。
3. 接口参数校验。

### 缓存击穿

热点 key 过期瞬间，大量请求直击数据库。

解决：

1. 热点 key 加长 TTL 或逻辑过期。
2. 互斥锁重建缓存。

### 缓存雪崩

大量 key 同时过期，请求集中打到数据库。

解决：

1. TTL 加随机值。
2. 多级缓存 + 限流降级。

## 大 Key 与热 Key

### 大 Key

单个 key 的 value 过大（如大 List、大 Hash、大 String）。

危害：阻塞删除、网络拥塞、内存不均。

发现：

```shell
redis-cli --bigkeys
```

处理：

- 拆分：按业务维度拆分多个 key。
- 压缩：大文本压缩后存储。
- 删除用 `UNLINK`（异步）或 `LTRIM` 分批裁剪。

### 热 Key

某个 key 被超高并发访问，单节点压力大。

处理：

- 本地缓存（多级缓存）。
- 复制多份热 key（`key:1`、`key:2`）分散读压力。
- Redis Cluster 下合理设计 key 分布。

## 内存与淘汰

```shell
INFO memory
CONFIG GET maxmemory
CONFIG GET maxmemory-policy
```

内存持续增长时优先排查：未设置 TTL 的 key、大 key、AOF 膨胀。

## 持久化与备份

```shell
BGSAVE
redis-cli --rdb /backup/redis-$(date +%F).rdb
```

建议：

1. AOF `everysec` + 混合持久化。
2. 定期备份并演练恢复。
3. 重要场景叠加主从复制。

## 主从与高可用

- 主从复制：数据热备、读写分离。
- 哨兵（Sentinel）：自动故障转移。
- Cluster：数据分片 + 高可用。

```txt [redis.conf]
# 从库配置
replicaof 10.0.0.1 6379
replica-read-only yes
```

## 安全加固

1. 设置强密码 `requirepass`。
2. 只监听内网 `bind`。
3. 禁用危险命令（`rename-command`）。
4. 不开放公网 6379。
5. 及时升级版本修复漏洞。

## 监控命令

```shell
redis-cli info            # 内存、连接、命中率
redis-cli --stat          # 实时状态
redis-cli --bigkeys       # 大 key 扫描
redis-cli slowlog get 10  # 慢查询
redis-cli monitor         # 打印所有命令（生产慎用，有性能开销）
```

## 最佳实践清单

1. 所有缓存 key 设置合理 TTL。
2. key 命名规范：`业务:模块:ID`，如 `user:1001`。
3. 用 Hash 存对象，用 ZSet 做排行榜。
4. 分布式锁用 `SET NX EX` + Lua 释放。
5. 生产禁用 `KEYS`、`FLUSHALL`、`MONITOR`。
6. 定期巡检大 key、热 key、内存增长。
7. 重要数据不要只依赖 Redis，Redis 是缓存不是唯一数据源。

## 相关链接

- Redis 官方文档：https://redis.io/docs/
- 命令参考：https://redis.io/docs/latest/commands/
