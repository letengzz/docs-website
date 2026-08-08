# Redis 发布订阅与事务

## 发布订阅（Pub/Sub）

发布订阅用于「一个消息、多个订阅者」的广播场景。

```shell
# 订阅者 1
SUBSCRIBE news

# 订阅者 2
SUBSCRIBE news

# 发布者
PUBLISH news "hello world"
```

模式订阅（按前缀匹配）：

```shell
PSUBSCRIBE news:*
PUBLISH news:sport "score 2:1"
```

取消订阅：

```shell
UNSUBSCRIBE news
PUNSUBSCRIBE news:*
```

::: danger 注意
1. Pub/Sub 消息**不持久化**：订阅者不在线时消息直接丢失。
2. 订阅者收到消息前必须先订阅，先发后订收不到。
3. 需要可靠消息队列时使用 **Stream** 或外部 MQ（Kafka、RabbitMQ）。
:::

## 事务（MULTI / EXEC）

Redis 事务把多条命令打包，按顺序执行：

```shell
MULTI
SET account:1 900
SET account:2 1100
EXEC
```

放弃事务：

```shell
MULTI
SET a 1
DISCARD
```

### WATCH 乐观锁

`WATCH` 监控 key，如果事务执行前 key 被其他客户端修改，事务放弃：

```shell
WATCH stock:1001
GET stock:1001
MULTI
DECR stock:1001
EXEC        # 若期间被修改，返回 nil，需要重试
```

::: danger 注意
1. Redis 事务**不支持回滚**：命令语法错误会导致整个事务失败；运行时错误（如对字符串做 INCR）只跳过出错命令，其余照常执行。
2. 事务中的命令是「排队后一次性执行」，不会被打断，但没有传统数据库的隔离级别概念。
:::

## Pipeline 管道

Pipeline 把多条命令一次发送、一次收取响应，减少网络往返：

```shell
redis-cli --pipe < commands.txt
```

示例（`commands.txt`）：

```text
SET a 1
SET b 2
INCR a
```

::: tip
Pipeline 提升的是**网络效率**，不是原子性；需要原子执行多条命令时用 Lua 脚本。
:::

## Lua 脚本

Lua 脚本整体原子执行，适合分布式锁释放、限流等场景：

```shell
EVAL "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" 1 lock token
```

这是释放分布式锁的标准写法：先校验持有者，再删除，避免误删。

## 验证方式

开两个 `redis-cli` 窗口：

```shell
# 窗口 1：订阅
SUBSCRIBE news

# 窗口 2：发布
PUBLISH news "hi"
```

窗口 1 应实时收到消息；事务用 `MULTI / EXEC` 验证批量执行结果。
