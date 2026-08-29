# Spring Cloud

Spring Cloud 是构建在 Spring Boot 之上的**微服务开发套件**：它把注册中心、配置中心、网关、负载均衡、熔断限流、消息驱动等分布式基础设施统一封装成一套可插拔的启动器，让开发者用“写普通 Spring 应用”的方式搭建微服务。本页是专题入口，先讲整体架构与核心组件，再给出与本库其他专题的衔接。

## 为什么需要 Spring Cloud

微服务把单体拆成多个服务后，出现了一批“分布式共性问题”：

| 问题 | 传统单体 | 微服务 |
| --- | --- | --- |
| 服务地址发现 | 本地调用即可 | 服务实例动态变化，需要注册中心 |
| 配置管理 | 一个配置文件 | 每个服务一套配置，需要配置中心 |
| 请求入口 | 网关即应用 | 需要统一网关做路由、鉴权、限流 |
| 服务间调用 | 直接方法调用 | 需要 HTTP/RPC + 负载均衡 + 重试 |
| 故障隔离 | 进程内异常 | 需要熔断、限流、降级 |
| 数据一致性 | 本地事务 | 需要分布式事务（SAGA/TCC） |

Spring Cloud 就是把这些问题的解决方案标准化：**“约定优于配置”**，通过注解和自动配置开箱即用。

## 核心组件与生态

| 组件 | 作用 | 主流实现 |
| --- | --- | --- |
| 服务注册与发现 | 服务实例登记、健康检查、客户端发现 | Nacos、Eureka、Consul |
| 配置中心 | 配置集中管理、动态刷新 | Nacos Config、Spring Cloud Config |
| API 网关 | 统一入口：路由、鉴权、限流、日志 | Spring Cloud Gateway |
| 负载均衡 | 客户端侧负载均衡 | Spring Cloud LoadBalancer |
| 熔断降级 | 故障隔离、快速失败、兜底 | Resilience4j、Sentinel |
| 消息驱动 | 用统一 API 对接 MQ，屏蔽 Kafka/RabbitMQ 差异 | Spring Cloud Stream |
| 链路追踪 | 跨服务调用链观测 | Micrometer Tracing + Zipkin |
| 分布式事务 | 跨服务事务一致性 | Seata（AT/TCC/SAGA） |

## 消息驱动：Spring Cloud Stream

微服务间大量使用**事件驱动**协作（订单创建 → 库存扣减 → 通知用户）。Spring Cloud Stream 提供统一的 **Binder（绑定器）** 抽象：

```text
应用代码（@StreamListener / Function）→ Binder → Kafka / RabbitMQ
```

好处是业务代码不直接依赖某个 MQ 的客户端 API，切换 MQ 时只改 binder 依赖与配置。消息驱动的基础概念（Topic/Queue、可靠投递、消费幂等、积压排查）见 [消息队列专题](../../../MessageQueue/index.md)。

```yaml [application.yml]
spring:
  cloud:
    stream:
      bindings:
        order-in-0:
          destination: orders        # 对应 Kafka Topic / RabbitMQ Exchange
          group: inventory-group     # 消费组
        order-out-0:
          destination: orders
```

```java
// Spring Cloud Stream 函数式风格：处理订单事件
@Bean
public Consumer<String> orderIn() {
    return message -> {
        // 幂等处理 + 业务逻辑，处理失败抛异常触发重试/死信
        System.out.println("收到订单事件: " + message);
    };
}
```

## 快速体验

```shell
# 1. 通过 start.spring.io 创建项目，依赖选择：Nacos Discovery、Gateway、Spring Cloud Stream
# 2. 启动本地 Kafka（见消息队列专题的 Kafka 快速启动）
# 3. 在 application.yml 配置 binder：spring.cloud.stream.binder.kafka.brokers=localhost:9092
# 4. 启动两个服务实例，观察注册中心显示两个实例并互相发现
```

验证方式：

1. 打开 Nacos 控制台，确认两个服务实例都注册成功且健康。
2. 向 `orders` Topic 发送消息，确认消费者收到事件（消息驱动链路打通）。
3. 停掉一个实例，确认注册中心自动摘除、网关请求仍能转发到存活实例。

## 易错点

::: danger 微服务消息驱动常见坑
1. **消费组缺失**：不配置 `group` 时，多个实例各自成为独立组，同一消息被重复消费。
2. **自动确认导致丢消息**：消费失败要抛异常或显式 reject，让消息进入重试/死信，而不是静默吞掉。
3. **网关与注册中心版本不匹配**：Spring Cloud 版本要按 Release Train（如 2025.x）与 Spring Boot 版本对齐。
4. **直接调用内网服务不经过注册中心**：服务间调用必须用客户端负载均衡（`@LoadBalanced` 或 OpenFeign），否则无法感知实例变化。
:::

## 进阶路线

本页是 Spring Cloud 的入口。更深入的专题（注册中心、配置中心、网关、熔断限流、链路追踪、分布式事务）已在微服务专题中系统建设，可结合以下内容建立完整体系：

- [微服务专题](../../../Microservices/index.md)：注册中心、网关、熔断限流、链路追踪、分布式事务完整体系
- [消息队列专题](../../../MessageQueue/index.md)：事件驱动与消息可靠性的基础
- [Spring Boot 通用指南](../SpringBoot/Common/index.md)：每个微服务都是 Spring Boot 应用
- [Java 并发专题](../../JavaSE/Multithreading/index.md)：异步与线程池在服务间的使用

## 参考资料

- Spring Cloud 官方文档：https://docs.spring.io/spring-cloud/reference/
- Spring Cloud Stream 参考文档：https://docs.spring.io/spring-cloud-stream/reference/
- Spring Cloud Gateway 文档：https://docs.spring.io/spring-cloud-gateway/reference/
- Spring Cloud 版本发布计划：https://spring.io/projects/spring-cloud#support
