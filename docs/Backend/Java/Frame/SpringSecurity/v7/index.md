# Spring Security 7

Spring Security 7.x 是**当前主线版本**（对应 Spring Boot 4.x 与 Spring Framework 7）。它延续了 6.x 的 `SecurityFilterChain` Bean 配置模型，同时移除了更多历史遗留 API，是**新项目的默认选择**。

::: tip 与 6.x 的关系
7.x 不是在 6.x 上"换了一套用法"，而是**在 6.x 的配置模型上继续收敛**：过滤链 Bean、`@EnableMethodSecurity`、`AuthenticationManager` 等核心模型保持一致。因此 6.x 的大量内容（认证流程、授权注解、过滤器链原理）在 7.x 中仍然适用。
:::

## 版本与对应关系

| 项 | 版本 | 说明 |
| --- | --- | --- |
| Spring Security | 7.1.x（当前 7.1.1，2026-08-20） | 本页主线版本 |
| Spring Boot | 4.x（当前 4.1.1） | 版本由 Spring Boot 依赖管理统一决定 |
| JDK | 以 Spring Boot 4 要求为准 | 升级前先确认 JDK 版本 |
| 命名空间 | `jakarta.*` | 不再兼容 `javax.*` |

## 从 6.x 迁移到 7.x 的检查清单

1. **先升级 Spring Boot**：Spring Security 版本跟随 Spring Boot 依赖管理，不要单独指定。
2. **清理已废弃 API**：6.x 中标记为 `deprecated` 的配置与工具类在 7.x 中可能已移除；编译报错是最好的迁移清单。
3. **回归四条鉴权路径**：登录、注销、令牌刷新、越权拦截（见 [认证与授权 · 安全最佳实践](../../../../Auth/Security/index.md)）。
4. **验证 OAuth2 链路**：客户端与资源服务器配置、JWKS 校验、令牌内省是否仍按预期工作。
5. **验证第三方登录**：OIDC/SAML 登录、会话与登出是否正常。
6. **保留回滚**：保留 6.x 分支与配置，升级到预发验证通过后再合入主干。

::: danger 升级期的三个高危动作
1. 与业务功能发布同时进行，出问题无法归因。
2. 只跑单元测试，不做真机/联调的登录与越权验证。
3. 升级后直接删除旧配置与旧分支，失去回滚能力。
:::

## 内容组织说明

7.x 与 6.x 在**概念与配置模型上高度一致**，因此实现细节当前复用 [Spring Security 6](../v6/index.md) 的页面；本页只记录版本状态、迁移要点与差异。后续如出现 7.x 独有的配置项与实践，会在本页持续补充，**不会改写 6.x 的内容**。

## 验证方式

1. 用 `mvn dependency:tree`（或 Gradle 对应命令）确认 Spring Security 实际版本为 7.x。
2. 用未认证、非法令牌、越权三条用例验证鉴权行为。
3. 走完一次完整的登录 → 刷新 → 注销流程，确认令牌与会话状态符合设计。
4. 检查日志中是否出现已废弃 API 的警告，清理后再上线。

## 相关专题

- [Spring Security 6（上一代主线）](../v6/index.md)
- [Spring Security 5（存档，仅存量）](../v5/index.md)
- [认证与授权专题](../../../../Auth/index.md)：语言中立的协议与架构知识
- [版本与兼容矩阵](../../../../Auth/Version/index.md)：OAuth 2.1 与 Spring Security 版本对照

## 参考资料

- Spring Security 官方文档：https://docs.spring.io/spring-security/reference/
- Spring Security 版本支持说明：https://spring.io/projects/spring-security#support
- Spring Boot 版本支持：https://spring.io/projects/spring-boot#support
