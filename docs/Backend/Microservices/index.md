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

## 相关专题与分工

- [JMeter 压力测试](../../Tools/TestingTools/JMeter/index.md)：本专题讲**服务拆分、注册与配置中心、网关、熔断限流降级、链路追踪与分布式事务**这些治理与通信问题——即「服务怎么拆、拆完怎么协作」；这些设计到底扛不扛得住流量，最后要落到压测上验证，JMeter 页给**压测脚本怎么写、报告怎么判读、容量拐点怎么定位**。两者是「设计」与「验证」的关系：拆完服务不等于容量就够，容量验证的落点在压测工具页。

## 实现侧对照：Java 与 Go 的分工

本专题讲的是**通用方法论**（服务拆分、注册发现、配置中心、链路追踪）。同样的方法论在两套技术栈里的落地形态差异很大，理解差异才能在选型时做出判断——而不是「团队会什么就用什么」。

| 能力 | Java（Spring Cloud 生态） | Go（gRPC + 治理框架） |
| --- | --- | --- |
| **服务间协议** | OpenFeign + JSON（HTTP/1.1 为主） | **gRPC + Protobuf**（HTTP/2 多路复用） |
| **接口契约** | 靠 Java 接口 + 文档，运行时发现不一致 | **proto 编译期约束**，改了必有编译错误 |
| **注册中心** | Nacos / Eureka / Consul | etcd / Nacos / K8s Service |
| **并发模型** | 一请求一线程（或虚拟线程） | 一请求一 goroutine，`context` 传递取消 |
| **超时机制** | `feign` / `RestTemplate` 分别配置 | **`context.WithTimeout` 逐跳递减** |
| **熔断限流** | Sentinel / Resilience4j | go-zero 内置、Kratos 中间件 |
| **配置热更** | Nacos 监听 + `@RefreshScope` | `conf` 监听 + etcd watch |
| **启动开销** | JVM 冷启动 1~10 s，常驻 200~800 MB | 启动 < 100 ms，常驻 20~50 MB |
| **线上诊断** | Arthas / JFR（能力强、无需改代码） | pprof / trace（**必须提前注册端点**） |

::: tip 选型判据（不是「哪个更好」）
- **面向高频核心链路、要求部署密度与扩容速度** → Go 侧。
- **业务逻辑复杂、需要大量成熟中间件与生态** → Java 侧。
- **组织上两种并存** → 用 **gRPC + proto 作为跨语言契约**，让两边都能消费同一份接口定义。这也是「多语言微服务」能成立的前提。

本专题的 Go 实现细节见 [Go 微服务](../GoMicroservices/index.md)：协议层（[gRPC 与 Protobuf](../GoMicroservices/GRPC/index.md)）、治理层（[注册发现到可观测](../GoMicroservices/Governance/index.md)）、工程实践（[实战：订单服务](../GoMicroservices/Practice/index.md)）。
:::

::: warning 说明：治理能力只应在一个层次实现
这是跨语言微服务最容易出的事故：**应用层（框架）与基础设施层（服务网格）同时开了熔断**，两层阈值互不知情。抖动时双重熔断会把健康实例也踢掉，表现为「服务大面积不可用，但每个实例单独测都是好的」。

原则：**要么在应用层做（框架 / 中间件），要么在基础设施层做（Istio 之类）**。同时开两层时，必须把其中一层的阈值调到几乎不会触发。
:::

