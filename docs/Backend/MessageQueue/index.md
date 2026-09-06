# 消息队列

<p style="text-align:center;"><img src="./assets/mq-logo.png" alt="消息队列" style="zoom:75%;" /></p>

消息队列（Message Queue，MQ）是分布式系统中用于**异步解耦、流量削峰、数据分发**的中间件。本专题覆盖 Kafka 与 RabbitMQ 两大主流产品，以及可靠投递、消费幂等、集群部署等生产级话题。

- [概念与选型](Overview/index.md)
- [Kafka 入门](Kafka/index.md)
- [RabbitMQ 入门](RabbitMQ/index.md)
- [可靠投递](Reliability/index.md)
- [消费幂等](Idempotency/index.md)
- [集群部署](Cluster/index.md)
- [对比总结](Comparison/index.md)
- [常见问题与最佳实践](FAQ/index.md)

::: tip 相关文档
微服务里“用统一 API 接 MQ”的编程模型（Spring Cloud Stream：函数式收发、消费组、分区、重试与 DLQ）见 [Spring Cloud 专题：消息驱动](../SpringCloud/Stream/index.md)。
:::
