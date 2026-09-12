# 微服务

<p style="text-align:center;"><img src="./assets/microservices-logo.png" alt="微服务" style="zoom:75%;" /></p>

微服务（Microservices）是把单体应用拆分为一组**可独立部署、独立扩展、围绕业务能力组织**的小服务，通过注册中心、网关、配置中心、熔断、链路追踪与分布式事务等基础设施解决分布式带来的新问题。本专题从拆分方法论讲到生产级组件实践。

- [概述与服务拆分](Overview/index.md)
- [注册中心](Registry/index.md)
- [配置中心](ConfigCenter/index.md)
- [API 网关](Gateway/index.md)
- [负载均衡](LoadBalance/index.md)
- [熔断限流与降级](CircuitBreaker/index.md)
- [链路追踪](Tracing/index.md)
- [分布式事务（2PC / TCC / SAGA / Seata / 消息表 共 10 篇）](DistributedTransaction/index.md)
- [实战：订单库存账户微服务](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

::: tip 与 Spring Cloud 的关系
本专题讲微服务架构的**方法论与通用模式**（不绑定某套组件）；基于 Spring Boot/Spring Cloud 的具体落地（Nacos 注册、Gateway、OpenFeign、Resilience4j、Micrometer Tracing 等）见 [Spring Cloud 完整专题](../SpringCloud/index.md)。
:::

::: info 分布式事务专题（2026-09 核对）
[分布式事务](DistributedTransaction/index.md) 已扩展为完整小节：概述与选型、[一致性基础](DistributedTransaction/Consistency/index.md)、[2PC 与 XA](DistributedTransaction/TwoPhaseCommit/index.md)、[TCC](DistributedTransaction/TCC/index.md)、[SAGA](DistributedTransaction/Saga/index.md)、[本地消息表与事务消息](DistributedTransaction/MessageTable/index.md)、[Seata 事务框架](DistributedTransaction/Seata/index.md)、[Seata 1.x 存档（仅存量项目）](DistributedTransaction/Seata/Seata1/index.md)、[实战](DistributedTransaction/Practice/index.md) 与 [常见问题](DistributedTransaction/FAQ/index.md)。主线面向 Seata 2.x（最新发布 2.7.0），1.x 内容保留并标注「仅存量项目使用」。
:::
