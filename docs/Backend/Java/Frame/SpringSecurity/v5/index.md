# Spring Security 5（存档）

::: danger 维护状态声明
本页内容**仅面向存量项目**。Spring Security 5.x 对应 **Spring Boot 2.x**（`javax.*` 命名空间），新项目请使用 [Spring Security 7](../v7/index.md)；升级路径见 [Spring Security 6](../v6/index.md) 与 [版本与兼容矩阵](../../../../Auth/Version/index.md)。旧版本内容在本库中**保留、不删除、不覆盖**。
:::

## 5.x 的典型写法与差异

| 维度 | Spring Security 5.x | Spring Security 6.x / 7.x |
| --- | --- | --- |
| 命名空间 | `javax.servlet.*` | `jakarta.servlet.*` |
| 配置方式 | 常见 `WebSecurityConfigurerAdapter` 子类 | 基于 `SecurityFilterChain` Bean（适配器已废弃） |
| 方法授权 | `@EnableGlobalMethodSecurity` | `@EnableMethodSecurity` |
| 与 Spring Boot | 2.x | 6.x 配 3.x；7.x 配 4.x |
| 状态 | **仅存量项目使用** | 当前与上一代主线 |

## 存量项目维护建议

1. **冻结依赖版本**：避免传递依赖被意外升级导致运行时错误。
2. **补齐监控与审计**：登录失败率、鉴权失败（401/403）数量与分布要可见。
3. **优先做协议治理**：如仍在用隐式/密码模式或对称签名，先按 [OAuth 2.1 与 OIDC](../../../../Auth/Oauth2/index.md) 的思路整改。
4. **排期升级**：升级到 6.x 需要处理命名空间与配置写法迁移，建议与 Spring Boot 3 升级合并进行。

## 验证方式

1. 记录当前 Spring Boot 与 Spring Security 版本，确认对应关系与本页表格一致。
2. 检查配置类是否仍继承 `WebSecurityConfigurerAdapter`（是 → 属于 5.x 写法）。
3. 检查项目是否仍有 `javax.servlet` 依赖（是 → 尚未迁移到 6.x/7.x）。
4. 用未认证、非法令牌、越权三条用例验证现有鉴权行为，作为升级前的基线。

## 相关专题

- [Spring Security 6](../v6/index.md)：上一代主线（Spring Boot 3.x）
- [Spring Security 7](../v7/index.md)：当前主线（Spring Boot 4.x）
- [认证与授权 · 版本与兼容矩阵](../../../../Auth/Version/index.md)：框架与协议版本对照

## 参考资料

- Spring Security 5.8 参考文档：https://docs.spring.io/spring-security/reference/5.8/
- Spring Boot 2.x 升级到 3.x 的迁移说明：https://spring.io/blog/2022/11/24/spring-boot-3-0-migration-guide
