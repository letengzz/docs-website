# String 与 Hash

String 是 Redis 最基础的数据结构，Hash 适合存储对象，两者都是缓存场景的主力。

## String 字符串

### 基本读写

```shell
SET name zhangsan
GET name            # "zhangsan"
SET name lisi       # 覆盖
GETSET name wangwu  # 返回旧值并设置新值
MSET a 1 b 2
MGET a b            # 1, 2
STRLEN name
APPEND name '@test'
```

### 过期与占位

```shell
SET token abc123 EX 600        # 600 秒过期
SET lock 1 NX EX 30            # 不存在才设置，用作分布式锁
SETNX name zhangsan            # 不存在才设置，返回 1/0
SETEX name 60 zhangsan         # 等价 SET + EXPIRE
```

### 计数

```shell
SET visits 100
INCR visits            # 101
INCRBY visits 10       # 111
DECR visits            # 110
DECRBY visits 5        # 105
```

::: tip
`INCR` 是原子操作，多个进程并发执行不会丢计数，适合点赞数、访问量、限流计数。
:::

### 应用场景

| 场景 | 命令组合 |
| --- | --- |
| 缓存 | `SET key value EX 3600` |
| 分布式锁 | `SET lock 1 NX EX 30` + `DEL`（配合 Lua 释放） |
| 计数器 | `INCR` / `INCRBY` |
| 验证码 | `SET code 123456 EX 60` |

::: danger 注意
1. 单个 String 最大 512MB，但大 value 会拖慢网络与内存，超过几十 KB 建议考虑拆分或换存储。
2. 分布式锁释放时必须校验值后再删除，防止误删他人锁（用 Lua 保证原子）。
:::

## Hash 哈希

Hash 以 field-value 形式存储，适合表示对象。

```shell
HSET user:1001 name zhangsan age 18
HGET user:1001 name          # zhangsan
HGETALL user:1001
HMGET user:1001 name age
HEXISTS user:1001 age        # 1
HLEN user:1001               # 2
HINCRBY user:1001 age 1      # 19
HDEL user:1001 age
HKEYS user:1001
HVALS user:1001
```

批量设置：

```shell
HMSET user:1002 name lisi city beijing
```

::: tip
对象优先用 Hash 而不是拼字符串：可以单独读写某个字段，节省带宽。
:::

### 应用场景

| 场景 | 说明 |
| --- | --- |
| 用户信息缓存 | `user:{id}` 存姓名、年龄等字段 |
| 购物车 | `cart:{userId}` 的商品 ID → 数量 |
| 配置项 | 按模块分组存储配置 |

::: danger 注意
1. `HGETALL` 在 field 很多时会阻塞，大 Hash 用 `HSCAN` 分批读取。
2. field 不要设计成无限增长（如时间戳当 field），否则 Hash 会退化成大 key。
:::

## 验证方式

```shell
redis-cli
SET name zhangsan
GET name
HSET user:1 name zhangsan age 18
HGETALL user:1
```

逐条核对返回值即可。
