# List / Set / ZSet

## List 列表

List 是有序、可重复的字符串列表，常用作队列和最新列表。

```shell
LPUSH queue task1        # 从左侧压入
RPUSH queue task2 task3  # 从右侧压入
LRANGE queue 0 -1        # 全部
LLEN queue               # 3
LPOP queue               # 弹出左侧
RPOP queue               # 弹出右侧
LINDEX queue 0           # 按下标取值
LSET queue 0 newtask     # 修改
LREM queue 1 task2       # 删除指定数量元素
```

阻塞弹出（适合消息队列）：

```shell
BLPOP queue 5       # 5 秒内等待左侧元素
BRPOP queue 5
```

::: tip
`LPUSH + BRPOP` 可以组成简单的生产者消费者队列；要求更高的场景用 Stream。
:::

## Set 集合

Set 是无序、**不可重复**的集合，适合标签、去重、共同关注。

```shell
SADD tags:post:1 java redis   # 添加
SADD tags:post:1 java         # 重复返回 0
SMEMBERS tags:post:1
SISMEMBER tags:post:1 java    # 1
SCARD tags:post:1             # 数量
SREM tags:post:1 java         # 删除

# 集合运算
SINTER set1 set2              # 交集（共同关注）
SUNION set1 set2              # 并集
SDIFF set1 set2               # 差集
```

随机取：

```shell
SPOP set1             # 随机弹出
SRANDMEMBER set1 3    # 随机取 3 个不弹出
```

## ZSet 有序集合

ZSet 每个元素带一个 score（分数），按分数排序，适合排行榜、延时队列。

```shell
ZADD leaderboard 100 zhangsan
ZADD leaderboard 90 lisi 95 wangwu

ZRANGE leaderboard 0 -1              # 按分数升序
ZREVRANGE leaderboard 0 -1           # 按分数降序（排行榜）
ZRANGE leaderboard 0 -1 WITHSCORES
ZSCORE leaderboard zhangsan          # 100
ZINCRBY leaderboard 5 zhangsan       # 分数 +5
ZRANK leaderboard zhangsan           # 升序排名
ZREVRANK leaderboard zhangsan        # 降序排名
ZCARD leaderboard                    # 成员数
ZREM leaderboard lisi                # 删除
ZREMRANGEBYSCORE leaderboard 0 50    # 按分数范围删除
```

### 排行榜示例

```shell
# 用户得分
ZADD rank:game 1200 user:1001
ZADD rank:game 1500 user:1002

# 取前 10 名
ZREVRANGE rank:game 0 9 WITHSCORES
```

## 数据结构对比

| 类型 | 有序 | 可重复 | 典型场景 |
| --- | --- | --- | --- |
| List | 是（按插入序） | 是 | 队列、最新消息 |
| Set | 否 | 否 | 标签、去重、交集 |
| ZSet | 是（按 score） | 否 | 排行榜、延时队列 |

::: danger 注意
1. `LRANGE` / `SMEMBERS` 在数据量大时会阻塞，大 key 用 `SCAN` 分批处理。
2. ZSet 的 score 用整数或小数均可，但注意浮点精度。
3. 不要让单个 List/Set/ZSet 无限增长，要配合 TTL、上限裁剪（`LTRIM`）或定时清理。
:::

## 验证方式

```shell
redis-cli
LPUSH q a b c
LRANGE q 0 -1
SADD s1 a b c
SMEMBERS s1
ZADD z 10 a 20 b
ZREVRANGE z 0 -1 WITHSCORES
```

核对列表顺序、集合去重、分数排序是否符合预期。
