# Spring Cloud

<p style="text-align:center;"><img src="./assets/spring-cloud-logo.png" alt="Spring Cloud" style="zoom:75%;" /></p>

Spring Cloud 是构建在 Spring Boot 之上的**微服务开发套件**：它把服务注册与发现、配置中心、API 网关、负载均衡、熔断限流、消息驱动、链路追踪等分布式基础设施统一封装成「开箱即用」的启动器，让开发者像写普通 Spring 应用一样搭建微服务。本专题从版本选型讲到组件实战，示例基于当前稳定版 **Spring Cloud 2025.1.x（Oakwood，适配 Spring Boot 4.x）**，并保留 2022.0.x~2025.0.x 各 Train 的版本差异说明。

## 目录结构

### 入门

- [Spring Cloud 概述](Overview/index.md)
- [版本选择与演进（Train 对照与状态）](Version/index.md)
- [环境搭建与项目脚手架](Environment/index.md)

### 核心组件

- [服务注册与发现](Discovery/index.md)
- [服务调用：OpenFeign 与负载均衡](OpenFeign/index.md)
- [API 网关：Spring Cloud Gateway](Gateway/index.md)
- [配置中心与动态刷新](ConfigCenter/index.md)
- [熔断限流与降级](CircuitBreaker/index.md)
- [链路追踪与可观测性](Tracing/index.md)
- [消息驱动：Spring Cloud Stream](Stream/index.md)

### 收尾

- [实战：注册中心 + 网关 + 服务调用全链路](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 版本速览

| Spring Cloud Train | 适配 Spring Boot | 状态（2026-09 核对） |
| --- | --- | --- |
| 2025.1.x（Oakwood） | 4.0.x / 4.1.x | 当前稳定版，**推荐使用** |
| 2025.0.x（Northfields） | 3.5.x | OSS 支持已结束（2026-06-30） |
| 2024.0.x（Moorgate） | 3.4.x | OSS 支持已结束 |
| 2023.0.x（Leyton） | 3.2.x / 3.3.x | OSS 支持已结束 |
| 2022.0.x（Kilburn） | 3.0.x / 3.1.x | OSS 支持已结束 |

::: tip 一句话理解
Spring Cloud 是「**微服务共性问题的一揽子解决方案**」：注册中心负责“找到服务”，网关负责“统一入口”，配置中心负责“一处修改、处处生效”，熔断与追踪负责“故障不扩散、问题查得清”。
:::

## 专题衔接

本专题讲 **Spring Cloud 组件的具体用法**；微服务架构的方法论（拆分原则、DDD、部署与治理）见 [微服务专题](../Microservices/index.md)。版本兼容性以官方 Release Train 对照为准，涉及 Spring Cloud Alibaba（Nacos/Sentinel/Seata）时按官方版本映射核对。

## 参考资料

- Spring Cloud 官方项目与文档：https://spring.io/projects/spring-cloud
- Spring Cloud Reference：https://docs.spring.io/spring-cloud/reference/
- Spring Cloud 发布说明：https://github.com/spring-cloud/spring-cloud-release/wiki
- Spring Cloud Alibaba 版本说明：https://sca.aliyun.com/docs/2025.x/overview/version-explain/
- Spring Boot 版本对照（本库）：[Spring Boot 概述与版本](../Java/Frame/SpringBoot/Common/Overview/index.md)
