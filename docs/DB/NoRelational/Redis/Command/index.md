# Redis 通用命令

无论哪种数据结构，key 本身的操作命令是通用的。

## Key 基本操作

```shell
SET name zhangsan
GET name

EXISTS name          # 1
TYPE name            # string
DEL name             # 删除，返回删除数量
UNLINK name          # 异步删除，大 key 推荐
```

## 过期时间

```shell
SET code 123456 EX 60        # 60 秒后过期
EXPIRE name 60               # 给已有 key 设置过期
PEXPIRE name 60000           # 毫秒
TTL name                     # 剩余秒数，-1 永不过期，-2 不存在
PTTL name                    # 剩余毫秒
PERSIST name                 # 取消过期
```

::: tip
缓存场景给每个 key 设置 TTL 是基本要求，避免内存无限增长。
:::

## 查找 Key

```shell
KEYS user:*       # 全量匹配，生产禁止
SCAN 0 MATCH user:* COUNT 100
```

::: danger 注意
`KEYS` 会阻塞 Redis 遍历所有 key，**生产环境禁止使用**；必须用 `SCAN` 游标式遍历。
:::

## 其他常用命令

| 命令 | 作用 |
| --- | --- |
| `SELECT index` | 切换数据库（0~15），默认 0 |
| `DBSIZE` | 当前库 key 数量 |
| `RANDOMKEY` | 随机返回一个 key |
| `RENAME key newkey` | 重命名 |
| `MOVE key db` | 移动到其他库 |
| `FLUSHDB` | 清空当前库（危险） |
| `FLUSHALL` | 清空所有库（危险） |

```shell
DBSIZE
SELECT 1
SET name zhangsan
SELECT 0
```

## 批量与原子性说明

`MSET` / `MGET` 用于字符串批量操作；`DEL` 支持多个 key：

```shell
DEL name code token
```

::: danger 注意
1. `FLUSHDB` / `FLUSHALL` 不可恢复，生产环境执行前必须确认并备份。
2. 多个命令组合不是原子的；需要原子性时使用事务、Lua 或带语义的单命令。
:::

## 验证方式

```shell
redis-cli
SET demo hello
EXISTS demo          # 1
EXPIRE demo 30
TTL demo             # 剩余秒数
DEL demo
```

逐条执行并核对返回值即可。
