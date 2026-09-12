# Spring Security

Spring Security 是 Spring 生态的**认证与授权框架**：提供过滤器链、方法级授权、密码加密、CSRF 防护，以及 OAuth2 / OIDC 的客户端与资源服务器实现。本主题按**大版本目录**组织，旧版本内容保留并标注状态，不做覆盖。

## 版本目录

| 版本 | 对应 Spring Boot | 状态 | 入口 |
| --- | --- | --- | --- |
| Spring Security 7.x | Spring Boot 4.x | **当前主线** | [Spring Security 7](v7/index.md) |
| Spring Security 6.x | Spring Boot 3.x | 上一代，仍在大量使用 | [Spring Security 6](v6/index.md) |
| Spring Security 5.x | Spring Boot 2.x | **仅存量项目使用** | [Spring Security 5（存档）](v5/index.md) |

::: info 版本约定
新项目请使用 **7.x**；6.x 项目可按官方迁移说明升级；5.x 内容仅用于维护既有系统，本库保留其说明并标注「仅存量」，不删除、不覆盖。版本状态与通用升级流程见 [认证与授权 · 版本与兼容矩阵](../../../Auth/Version/index.md)。
:::

## 先学什么

认证授权涉及的概念（会话与令牌、OAuth 2.1 与 OIDC、权限模型、网关鉴权、安全加固）与具体框架无关，建议先读语言中立的专题：

- [认证与授权专题](../../../Auth/index.md)：Session / JWT / OAuth 2.1 / SSO / 权限模型 / 安全实践
- [会话与 Cookie](../../../Auth/Session/index.md)、[JWT 深入](../../../Auth/Jwt/index.md)
- [OAuth 2.1 与 OIDC](../../../Auth/Oauth2/index.md)、[权限模型](../../../Auth/Authorization/index.md)
- [服务端落地](../../../Auth/Implementation/index.md)：网关与服务双层鉴权

再回到本主题看具体实现（过滤器链、注解、配置写法）。

## 参考资料

- Spring Security 官方文档：https://docs.spring.io/spring-security/reference/
- Spring Security 版本支持说明：https://spring.io/projects/spring-security#support
