# Spring

本目录按**大版本**组织：每一代独立成目录，旧版本**不删除、不覆盖**，只在页首标注维护状态。新项目一律从当前主线读起。

## 版本索引与状态

| 目录 | 面向版本 | JDK 基线 | 维护状态（2026-10 核对） | 什么时候读 |
| --- | --- | --- | --- | --- |
| [Spring 5](Spring5/index.md) | Spring Framework 5.3 | JDK 8+ | **仅存量项目使用**：5.3 线 OSS 维护已于 2024-08-31 结束（企业支持至 2029-06），文档不再随上游更新 | 维护老项目、读旧代码 |
| [Spring 6](Spring6/index.md) | Spring Framework 6.x | JDK 17+ | **仅存量项目参考**：6.2 为第 6 代最后一条特性线，OSS 支持已于 2026-06-30 结束；主线自 2025-11 迁到 7.0 | 6.x 存量项目升级前的对照 |
| Spring 7（暂不单建目录） | Spring Framework 7.0 | JDK 17+ | **当前主线**：新项目应以此为目标 | 新项目；内容并入 6.x 页面，版本差异在页内标注 |

::: warning 版本目录的三条约定
1. **新内容面向最新主线**，并在页内用 `:::info` 写清适用版本；
2. **旧版本目录保留原样**，只补「维护状态」与「与新版差异」，不改写旧正文——改写会让存量项目查到的用法与它手上的版本对不上；
3. **小版本（6.1.x、6.2.x）不单独建目录**，差异写在页内表格里；只有**大版本**（5 → 6 → 7）才分目录。
:::

同一套约定在库内其它技术栈上的落地：[Vue 2 / Vue 3](../../../../Frontend/Frame/Vue/index.md)、[Spring Security 5/6/7](../../../Auth/Version/index.md)、[Spring Cloud 2020/2022](../../../SpringCloud/index.md)、[MySQL 5.7 / 8.4](../../../../DB/SchemaEvolution/index.md)。

## 相关专题

- [设计模式](../../../DesignPatterns/index.md)：IoC、AOP 与 Spring 内部的单例/代理/工厂模式
- [Spring Boot（版本总览）](../SpringBoot/index.md)：基于 Spring 的快速开发框架
- [Spring Cloud 完整专题](../../../SpringCloud/index.md)：在 Spring Boot 之上解决服务发现、配置、网关、熔断等分布式问题
