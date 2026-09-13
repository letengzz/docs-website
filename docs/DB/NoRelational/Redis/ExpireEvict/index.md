# 过期与淘汰策略

## 过期时间

给 key 设置过期时间后，到期自动删除：

```shell
SET code 123456 EX 60
EXPIRE name 30
PEXPIRE name 30000
TTL name
PERSIST name          # 取消过期
```

### 过期删除策略

Redis 采用**惰性删除 + 定期删除**组合：

- 惰性删除：访问 key 时才检查是否过期，过期则删除，节省 CPU。
- 定期删除：后台周期抽样检查并删除过期 key，避免过期 key 长期占用内存。

::: danger 注意
过期删除是**异步且抽样**的，大量 key 同时过期时，删除可能来不及，需配合淘汰策略兜底。
:::

## 内存淘汰策略

当内存达到 `maxmemory` 上限时，按 `maxmemory-policy` 决定如何处理：

```txt [redis.conf]
maxmemory 512mb
maxmemory-policy allkeys-lru
```

| 策略 | 说明 | 适用 |
| --- | --- | --- |
| `noeviction` | 不淘汰，写命令报错（默认） | 不允许丢数据的场景 |
| `allkeys-lru` | 从所有 key 中淘汰最近最少使用 | 通用缓存，推荐 |
| `allkeys-lfu` | 从所有 key 中淘汰最不常使用 | 访问频率差异大的缓存 |
| `allkeys-random` | 随机淘汰 | 冷热不明显的场景 |
| `allkeys-lrm` | 从所有 key 中淘汰**最近最少修改**的（Redis 8.6+） | 更新即代表有价值的写多场景 |
| `volatile-lru` | 只在设置了过期的 key 中淘汰 LRU | 有 TTL 的缓存 |
| `volatile-lfu` | 只在设置了过期的 key 中淘汰 LFU | 有 TTL 的缓存 |
| `volatile-random` | 只在设置了过期的 key 中随机淘汰 | 有 TTL 的缓存 |
| `volatile-ttl` | 淘汰剩余 TTL 最短的 key | 优先淘汰即将过期的 |
| `volatile-lrm` | 只在设置了过期的 key 中淘汰最近最少修改的（Redis 8.6+） | 带 TTL 的写多读少数据 |

::: info LRM 策略（Redis 8.6 新增）
`allkeys-lrm` / `volatile-lrm` 以「**最近修改时间**（least recently modified）」为淘汰依据：越久没有被写入的 key 越先被淘汰。它适合「写入代表数据仍有价值」的场景（如实时采集数据、状态快照），与 LRU（按访问时间）、LFU（按访问频率）互补。
:::

![淘汰策略分类](./assets/eviction-policies.svg)

::: tip
纯缓存场景推荐 `allkeys-lru`；既当缓存又存业务数据时用 `noeviction` 并在业务层控制。
:::

## 查看与设置

```shell
CONFIG GET maxmemory
CONFIG GET maxmemory-policy

# 运行时修改（重启失效）
CONFIG SET maxmemory-policy allkeys-lru
```

持久化到配置文件用：

```txt [redis.conf]
maxmemory-policy allkeys-lru
```

## 缓存常见问题（速览）

和过期机制直接相关的三类问题，本节只给结论，完整方案见[缓存防护](../Advanced/CacheProtection/index.md)：

| 问题 | 成因 | 一句话解法 |
| --- | --- | --- |
| 缓存穿透 | 查的数据缓存与数据库都没有 | 空值短 TTL 缓存 + 布隆过滤器 + 参数校验 |
| 缓存击穿 | 单个热点 key 过期瞬间并发回源 | 互斥锁重建缓存 / 逻辑过期 |
| 缓存雪崩 | 大批 key 同时过期或 Redis 宕机 | TTL 加随机抖动 + 多级缓存 + 限流降级 |

::: danger 注意
1. 过期时间不要写死同一个值，生产环境必须加随机抖动。
2. `CONFIG SET` 只改运行时，重启失效，确认无误后写入 redis.conf。
:::

## 验证方式

```shell
redis-cli
CONFIG GET maxmemory-policy
SET k1 v EX 5
TTL k1
# 等待 5 秒
EXISTS k1            # 0
```

还可以用 `redis-cli --stat` 观察内存变化。

## 相关专题

- [缓存设计](../Advanced/CacheDesign/index.md)：TTL 设计、容量规划与一致性方案
- [缓存防护](../Advanced/CacheProtection/index.md)：穿透/击穿/雪崩/热点 key 的完整解法
- [性能调优](../Advanced/Performance/index.md)：`evicted_keys`、内存碎片率等指标解读
- [Redis 进阶导览](../Advanced/index.md)
