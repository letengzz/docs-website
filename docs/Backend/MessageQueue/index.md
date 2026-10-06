# 消息队列

<p style="text-align:center;"><img src="./assets/mq-logo.png" alt="消息队列" style="zoom:75%;" /></p>

消息队列（Message Queue，MQ）是分布式系统中用于**异步解耦、流量削峰、数据分发**的中间件。本专题覆盖 Kafka 与 RabbitMQ 两大主流产品，以及可靠投递、消费幂等、集群部署等生产级话题。

- [概念与选型](Overview/index.md)
- [Kafka 概述与深入（架构 / 生产者 / 消费者 / 副本 / 可靠性 / 集群 / 实战）](Kafka/index.md)
- [RabbitMQ 入门](RabbitMQ/index.md)
- [可靠投递](Reliability/index.md)
- [消费幂等](Idempotency/index.md)
- [集群部署](Cluster/index.md)
- [对比总结](Comparison/index.md)
- [常见问题与最佳实践](FAQ/index.md)

::: tip 相关文档
微服务里“用统一 API 接 MQ”的编程模型（Spring Cloud Stream：函数式收发、消费组、分区、重试与 DLQ）见 [Spring Cloud 专题：消息驱动](../SpringCloud/Stream/index.md)。

工作流引擎产生的外部副作用（审批通过后发通知、清缓存、同步检索）也走同一条路：**在引擎事务内只写一行本地事件，事务外异步消费，消费端必须幂等**。为什么不能把发通知直接写在流程监听器里、为什么要给事件做幂等键，见 [工作流与规则引擎 · 与业务系统集成](../WorkflowEngine/Integration/index.md)——那边讲「引擎事务边界怎么划」，本专题讲「消息怎么保证不丢不重」。
:::

::: info 版本提示（2026-09 核对）
Kafka 当前稳定版为 **4.3.1**（2026-06-25 发布），4.0 起**只支持 KRaft 模式**，ZooKeeper 已移除；3.9.x 是 ZooKeeper 模式的最后一代，本库保留其说明并标注「仅存量集群使用」。Kafka 详细内容见 [Kafka 概述](Kafka/index.md) 与 [版本演进与迁移](Kafka/Version/index.md)。
:::
