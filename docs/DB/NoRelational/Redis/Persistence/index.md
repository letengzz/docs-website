# Redis 持久化 RDB / AOF

Redis 数据默认在内存中，重启会丢失；持久化用于把数据保存到磁盘，重启后恢复。

## RDB 快照

RDB 把某个时间点的全量数据压缩保存到 `dump.rdb`。

### 触发方式

```shell
# 手动触发（阻塞）
SAVE

# 手动触发（后台异步，推荐）
BGSAVE
```

配置文件自动触发：

```txt [redis.conf]
save 900 1        # 900 秒内至少 1 次修改
save 300 10       # 300 秒内至少 10 次修改
save 60 10000     # 60 秒内至少 10000 次修改
```

### 优点与缺点

| 优点 | 缺点 |
| --- | --- |
| 文件紧凑，适合备份与迁移 | 快照间隔内数据可能丢失 |
| 恢复速度快 | 全量快照对大数据量有性能开销 |
| 对 Redis 性能影响小（BGSAVE） | 不适合高可靠性场景 |

## AOF 追加日志

AOF 记录每次写命令，恢复时重放日志。

```txt [redis.conf]
appendonly yes
appendfsync everysec
```

### appendfsync 策略

| 策略 | 说明 | 可靠性 |
| --- | --- | --- |
| `always` | 每条命令都刷盘 | 最可靠，性能最差 |
| `everysec` | 每秒刷盘一次 | 折中，最多丢 1 秒数据，**推荐** |
| `no` | 交给操作系统刷盘 | 性能最好，可能丢较多数据 |

### AOF 重写

AOF 文件会持续膨胀，需要重写压缩：

```shell
BGREWRITEAOF
```

```txt [redis.conf]
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

## 混合持久化（推荐）

Redis 4.0+ 支持混合持久化：AOF 文件头部是 RDB 快照，尾部是增量命令，兼顾恢复速度和数据完整性。

```txt [redis.conf]
aof-use-rdb-preamble yes
```

## RDB vs AOF 对比

| 维度 | RDB | AOF |
| --- | --- | --- |
| 数据完整性 | 可能丢最后一次快照后的数据 | everysec 最多丢 1 秒 |
| 文件大小 | 小 | 大（重写后可控） |
| 恢复速度 | 快 | 慢 |
| 对性能影响 | BGSAVE 影响小 | everysec 影响小 |
| 适用 | 备份、主从初始化 | 高可靠性场景 |

::: tip
生产环境推荐 **AOF（everysec）+ 混合持久化 + 定期 RDB 备份** 组合；重要数据再叠加主从复制。
:::

## 恢复流程

1. 停止 Redis。
2. 确保 `appendonly.aof` / `dump.rdb` 在配置的 `dir` 目录下。
3. 启动 Redis，启动时自动加载恢复。
4. 用 `redis-cli info persistence` 确认加载状态。

::: danger 注意
1. AOF 文件损坏时 Redis 可能拒绝启动，可先备份再用 `redis-check-aof` 修复。
2. 不要同时依赖「主从」代替持久化：从库重启同样需要源数据。
3. 定期演练「备份 → 恢复到新实例」，确认备份可用。
:::

## 验证方式

```shell
redis-cli
CONFIG GET appendonly
CONFIG GET appendfsync
INFO persistence
```

`INFO persistence` 中 `rdb_last_bgsave_status:ok`、`aof_last_write_status:ok` 表示正常。
