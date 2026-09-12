# 会话 (session)

用户认证通过后，为了避免用户的每次操作都进行认证可将用户的信息保存在会话中。会话就是系统为了保持当前用户的登录状态所提供的机制，**常见的有基于session方式、基于token方式**等。

## 基于session的认证方式

它的交互流程是，用户认证成功后，在服务端生成用户相关的数据保存在session(当前会话)中，发给客户端的sesssion_id 存放到 cookie 中，这样用户客户端请求时带上 session_id 就可以验证服务器端是否存在 session 数据，以此完成用户的合法校验，当用户退出系统或session过期销毁时,客户端的session_id也就无效了。

## 基于token的认证方式

它的交互流程是，用户认证成功后，服务端生成一个token发给客户端，客户端可以放到 cookie 或 localStorage等存储中，每次请求时带上 token，服务端收到token通过验证后即可确认用户身份。可以使用Redis 存储用户信息（分布式中**共享session**）。

基于session的认证方式由Servlet规范定制，服务端要存储session信息需要占用内存资源，客户端需要支持cookie；基于token的方式则一般不需要服务端存储token，并且不限制客户端的存储方式。**如今移动互联网时代更多类型的客户端需要接入系统，系统多是采用前后端分离的架构进行实现，所以基于token的方式更适合**。

## 两种方式对比

| 维度 | 基于 Session | 基于 Token（JWT 等） |
| --- | --- | --- |
| 状态存储 | 服务端（内存 / Redis） | 客户端持有，服务端无状态校验 |
| 注销即时性 | 删除会话即失效 | 需额外机制（短过期 / 吊销 / 版本号） |
| 横向扩展 | 需共享会话存储 | 天然无状态，易扩展 |
| 客户端限制 | 依赖 Cookie | 不限制（App、小程序均可用） |
| 安全关注点 | 会话固定、Cookie 属性、CSRF | 令牌泄露、算法与密钥、过期时间 |

概念层面的完整对比与选择建议见 [认证与授权 · 会话与 Cookie](../../../../../../Auth/Session/index.md) 与 [JWT 深入](../../../../../../Auth/Jwt/index.md)。

## Spring Security 6 中的会话相关配置要点

1. **会话创建策略**：`SessionCreationPolicy` 可选 `IF_REQUIRED` / `STATELESS` / `ALWAYS` / `NEVER`；前后端分离使用 JWT 时通常设为 `STATELESS`。
2. **会话并发控制**：限制同一账号同时在线数量，超限时可踢掉最早或最晚的会话。
3. **会话固定防护**：登录成功后更换会话 ID（框架默认已处理，需确认未被关闭）。
4. **会话共享**：多实例部署时引入集中式会话存储（如 Spring Session + Redis），否则会出现"换一台机器就掉线"。

```java [无状态与有状态的配置差异（示意）]
// 前后端分离 + JWT：不创建会话
http.sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));

// 传统 Web：使用会话并限制并发登录数
http.sessionManagement(session -> session
        .maximumSessions(1)                 // 同一账号最多 1 个会话
        .maxSessionsPreventsLogin(false));  // false = 新登录踢掉旧会话
```

::: danger 会话相关的三个高频问题
1. **多实例未共享会话**：负载均衡切换实例后登录态丢失。
2. **配置为 `STATELESS` 却仍依赖 Session**：表现为登录成功后立刻被判定未认证。
3. **登录后未更换会话 ID**：存在会话固定攻击风险。
:::

## 验证方式

1. 登录后查看响应头，确认 `Set-Cookie` 带有 `HttpOnly`、`Secure`、`SameSite` 属性。
2. 记录登录前后的会话 ID，确认登录成功后发生变化（防会话固定）。
3. 把并发登录限制设为 1，用同一账号在两个浏览器登录，确认旧会话被踢出（或新登录被阻止，取决于配置）。
4. 若使用 JWT，确认服务端未创建会话（`STATELESS`），并验证注销与刷新链路。

## 相关专题

- [认证与授权 · 会话与 Cookie](../../../../../../Auth/Session/index.md)：语言中立的会话方案对比
- [认证与授权 · JWT 深入](../../../../../../Auth/Jwt/index.md)：令牌方案与吊销机制
- [Spring Security 6 · 认证](../Authentication/index.md)、[授权](../Authorization/index.md)

## 参考资料

- Spring Security 官方文档 · 会话管理：https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html
- OWASP · Session Management Cheat Sheet：https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
