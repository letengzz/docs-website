# 消息队列对比总结

选型没有“最好”，只有“最合适”。本页把主流 MQ 放在同一张表里对比，并给出按场景的选型结论，方便把前面几篇的知识沉淀成决策依据。

## 主流产品横向对比

| 维度 | Kafka | RabbitMQ | RocketMQ | Pulsar |
| --- | --- | --- | --- | --- |
| 当前稳定版（2026-08） | 4.3.x | 4.3.x | 5.x | 4.x |
| 开发语言 | Scala/Java | Erlang | Java | Java |
| 消息模型 | Topic + Partition + Log | Exchange + Queue | Topic + Queue | Topic + Partition，存算分离 |
| 路由能力 | 弱（仅 Topic） | 强（direct/topic/fanout/headers） | 中（Tag + 过滤） | 弱 |
| 单机吞吐 | 极高（十万~百万级/秒） | 中（数万/秒） | 高（十万级/秒） | 高 |
| 消息延迟 | 毫秒级（吞吐优先） | 微秒~毫秒级 | 毫秒级 | 毫秒级 |
| 顺序保证 | 分区内有序 | 单队列有序 | 队列内有序 | 分区内有序 |
| 可靠投递 | 幂等生产者 + ISR 副本 | Publisher Confirms + Quorum 队列 | 事务消息 + 同步刷盘 | 副本 + 确认 |
| 消费回溯 | 强（按 offset 重放） | 弱（消费即删） | 中（时间/位点） | 强 |
| 延迟/死信消息 | 需要自行实现 | 原生 TTL + 死信交换机 | 原生定时/事务消息 | 需要自行实现 |
| 运维复杂度 | 高（KRaft 控制器、磁盘规划） | 中（Erlang 集群） | 中 | 高（BookKeeper） |
| 生态 | Flink/Spark/Hadoop 全家桶 | 多语言客户端广 | 阿里系组件全 | 多租户、云原生 |
| 典型场景 | 日志、事件流、大数据管道 | 业务解耦、任务分发 | 电商交易、金融 | 大规模多租户、云上 |

## 双雄定位

### Kafka：日志流式平台

**优势**：吞吐天花板高、分区内严格有序、可回溯重放、与大数据生态无缝集成；4.2 起 Share Groups 补上了点对点消费能力。

**代价**：路由能力弱、延迟消息/死信要自己搭、集群运维成本高、小消息量时“杀鸡用牛刀”。

### RabbitMQ：灵活的路由枢纽

**优势**：Exchange 路由模型灵活、TTL/死信/延迟插件开箱即用、客户端成熟、单机延迟低、运维相对轻。

**代价**：吞吐上限低于 Kafka、消费即删不可回溯、集群强一致与网络分区处理需要经验。

## 场景选型速查

| 你的诉求 | 推荐 | 为什么 |
| --- | --- | --- |
| 埋点、日志、审计数据聚合 | Kafka | 高吞吐 + 顺序写 + 可重放 |
| 订单支付、库存、积分解耦 | RocketMQ / RabbitMQ | 可靠性、事务消息、灵活路由 |
| 任务队列、通知、延迟消息 | RabbitMQ | 死信 + TTL 生态成熟 |
| 事件驱动架构、微服务事件总线 | Kafka | 事件流天然有序、可追溯 |
| 数据同步到数仓/搜索 | Kafka | Connect 生态 + 流计算无缝衔接 |
| 团队只有 MySQL + Redis，消息量小 | Redis Stream | 零新增组件，但只能做轻量场景 |
| 云上 Serverless 集成 | SQS / SNS / Kafka 云托管 | 免运维、按量付费 |
| 金融级事务消息 | RocketMQ | 事务消息、同步双写能力成熟 |

## 常见迁移与共存

### Kafka 与 RabbitMQ 共存

很多公司两条线并行：

```text
在线业务解耦（订单、通知）   → RabbitMQ（路由灵活、延迟消息）
离线数据管道（日志、数仓）   → Kafka（高吞吐、可回溯）
```

### 从 RabbitMQ 迁 Kafka

1. 先确认业务不需要复杂路由与原生死信。
2. 用 Kafka 4.2+ 的 Share Groups 模拟点对点队列。
3. 消费端统一改为「手动提交 offset + 幂等消费」，避免迁移后重复消费。
4. 采用双写/双读灰度：新旧 MQ 并行一段时间，校验数据一致后切换。

### 从 Redis Pub/Sub 升级

如果业务已出现“消费者离线丢消息”问题，说明该从 Redis 升级到正式 MQ 了（参考 [Redis 发布订阅与事务](../../../DB/NoRelational/Redis/PubSubTransaction/index.md) 中的局限说明）。

## 决策清单

::: tip 选型打分表
按 1~5 分给以下维度打分，总分最高者胜出：
1. 峰值吞吐是否满足未来 2 年增长
2. 路由/延迟/死信能力是否开箱即用
3. 可靠性机制是否达到业务要求
4. 团队是否有运维与排障经验
5. 与现有技术栈（大数据、微服务、云）的集成成本
:::

::: warning 常见误区
1. “RabbitMQ 慢所以不选”——多数业务消息量下 RabbitMQ 完全够用，且路由能力更省事。
2. “Kafka 一定不丢消息”——`acks=0`、副本数 1 照样丢，可靠性靠配置不靠产品名。
3. “MQ 能解决所有异步问题”——顺序、幂等、积压、监控仍需自己设计。
:::

## 验证方式

1. 用生产/消费 Demo 实测两种 MQ 的端到端延迟与吞吐（见 [Kafka 入门](../Kafka/index.md)、[RabbitMQ 入门](../RabbitMQ/index.md)）。
2. 对照选型打分表，写出目标场景的得分与结论。
3. 结合团队现状做一次小规模试点（1 个业务 + 1 个 Topic/Exchange），再决定全面推广。

## 参考资料

- Kafka vs RabbitMQ（官方博客）：https://developer.confluent.io/learn/kafka-vs-rabbitmq/
- RocketMQ 与 Kafka 对比：https://rocketmq.apache.org/docs/rmq-vs-kafka/
- Pulsar vs Kafka：https://pulsar.apache.org/blog/2023/10/16/technical-notes-beyond-the-shades-of-gray/
- 消息中间件选型思考（阿里云）：https://help.aliyun.com/document_detail/119517.html
