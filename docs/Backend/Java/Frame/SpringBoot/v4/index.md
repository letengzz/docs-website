# Spring Boot 4.x（当前稳定版）

Spring Boot 4.x 是基于 Spring Framework 7 的新一代版本，是 2026 年当前稳定版。本节只讲「4.x 有什么新东西、怎么从 3.x 升级」；通用用法请参考「Spring Boot 通用指南」。

::: info 版本现状（2026-08 核对）
Spring Boot 4.0 于 2025-11 发布，4.1 于 2026-06 发布，为当前稳定版。最低支持 Java 17，**推荐 Java 25 LTS**。Spring Boot 3.5.x 的 OSS 支持已于 2026-06-30 结束。
:::

## 4.x 新特性

| 特性 | 说明 |
| --- | --- |
| Spring Framework 7 | 底层框架升级，模块化与性能提升 |
| Java 25 一流支持 | 虚拟线程等新特性的完整支持 |
| Jackson 3 | 默认 JSON 库从 Jackson 2 升级为 Jackson 3 |
| 模块化 Starter | 部分起步依赖拆分与重组，依赖更清晰 |
| 可观测性增强 | Micrometer/OpenTelemetry 集成更完善 |
| OAuth2 与安全改进 | Spring Security 7 配套升级 |

## 与 3.x 的主要差异

1. **Java 版本**：3.x 最低 Java 17；4.x 最低 Java 17、推荐 Java 25。
2. **JSON 库**：3.x 默认 Jackson 2，4.x 默认 Jackson 3，序列化 API 有调整。
3. **依赖组织**：部分 starter 的坐标或自动配置类变化，升级后需要清理失效 import。
4. **配置项**：少数 `spring.*` 配置项被移除或改名，启动时会有提示。
5. **安全**：Spring Security 7 引入，部分配置 DSL 调整。

## 升级到 4.x 的步骤

1. 升级 JDK 到 17+（推荐 25），先保证项目在 Java 25 下编译通过。
2. 使用 Spring Boot 官方升级工具或 `spring-boot-migrator` 分析项目。
3. 逐个替换失效的依赖坐标与 import。
4. 升级测试库（JUnit、Mockito、Testcontainers 等）到兼容版本。
5. 在分支上跑全量测试，重点验证 JSON 序列化、安全配置、数据访问。
6. 灰度发布，观察日志与监控指标。

::: tip 升级建议
3.5.x 已停止 OSS 支持，存量项目应规划升级；但不要原地大改，先在分支验证再灰度。
:::

## 通用指南入口

Spring Boot 的通用知识点已抽离到「通用指南」：

- [Spring Boot 概述与版本](../Common/Overview/index.md)
- [项目搭建](../Common/CreateProject/index.md)
- [配置与 Profile](../Common/Configuration/index.md)
- [Web 开发](../Common/Web/index.md)
- [数据访问](../Common/DataAccess/index.md)
- [REST API](../Common/RestAPI/index.md)
- [异常处理](../Common/Exception/index.md)
- [测试](../Common/Testing/index.md)
- [部署](../Common/Deploy/index.md)
- [常见问题与最佳实践](../Common/FAQ/index.md)

## 验证方式

1. `java -version` 确认 JDK 17+。
2. `mvn spring-boot:run` 启动后访问 `/actuator/health` 返回 `UP`。
3. 从 3.x 升级后跑一遍 `mvn test` 全量测试。
4. 用接口冒烟测试确认 JSON 序列化与安全配置正常。

## 参考资料

- Spring Boot 4.0 发布公告：https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now
- Spring Boot 升级指南：https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
- Spring Boot 支持时间表：https://endoflife.date/spring-boot
