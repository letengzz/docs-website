# SpringBoot3改变 & 新特性

**Spring Boot 3 是一次「破坏性但也最有价值」的大版本：它把整个技术栈从 Java EE 的 `javax.*` 命名空间搬到了 Jakarta EE 的 `jakarta.*`，同时把最低 JDK 提高到 17。** 本页讲清 2.x → 3.x 到底变了什么、哪些是必须改的（不改编译不过）、哪些是改了更好，以及迁移的可执行步骤。

::: warning 版本状态（2026-10 核对）
Spring Boot 3.0 于 2022-11-24 发布，基于 Spring Framework 6.0，**最低 Java 17**；底层基于 Jakarta EE 9 并尽可能兼容 Jakarta EE 10。当前稳定大版本是 **Spring Boot 4.x**（4.0 于 2025-11 发布、4.1 于 2026-06），基于 Spring Framework 7；**3.5.x 的 OSS 支持已于 2026-06-30 结束**。本页面向**存量 3.x 项目**（维护中 / 迁移中），新项目请走 [Spring Boot 4.x](../v4/index.md)。
:::

## 一、2.x → 3.x 的五个必改项

这五项**不改就编译不过或起不来**，是迁移的硬门槛。

| # | 变更 | 2.x 写法 | 3.x 写法 |
| --- | --- | --- | --- |
| 1 | **JDK 基线** | Java 8 / 11 | **Java 17 起**（Spring Framework 6 要求） |
| 2 | **Jakarta 命名空间** | `javax.servlet.*`、`javax.persistence.*`、`javax.validation.*` | `jakarta.servlet.*`、`jakarta.persistence.*`、`jakarta.validation.*` |
| 3 | **自动配置注册文件** | `META-INF/spring.factories` 里的 `org.springframework.boot.autoconfigure.EnableAutoConfiguration=` | `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`，**每行一个全限定类名** |
| 4 | **自动配置类注解** | `@Configuration` + `spring.factories` 登记 | `@AutoConfiguration`（支持 `before` / `after` 排序），并用 imports 文件登记 |
| 5 | **API 与依赖基线** | Servlet 4.0 / Tomcat 9 / Hibernate 5 / Jackson 2.13 | Servlet 5.0+ / Tomcat 10.1（3.2 起）/ Hibernate 6.1+ / Jackson 2.14+ |

```text
第三方 starter / 自研 starter 的迁移清单：

  ┌──────────────────────────────────────────────┐
  │ src/main/resources/META-INF/spring.factories │  ← 删掉 EnableAutoConfiguration 段
  └──────────────────────────────────────────────┘
                      ↓ 改成
  ┌──────────────────────────────────────────────────────────────────┐
  │ src/main/resources/META-INF/spring/                              │
  │   org.springframework.boot.autoconfigure.AutoConfiguration.imports │
  │                                                                  │
  │   com.example.starter.FooAutoConfiguration                        │
  │   com.example.starter.BarAutoConfiguration                         │
  └──────────────────────────────────────────────────────────────────┘
```

::: danger 命名空间替换不能全局无脑替换
`javax.*` 里**有一部分不属于 Jakarta EE**，一起替换会编译不过：

- `javax.crypto.*`、`javax.net.*`、`javax.sql.*`（JDK 自带的 `javax.sql`）→ **仍属 JDK，不要改**；
- `javax.annotation.processing.*`（注解处理器）→ **仍属 JDK，不要改**；
- `javax.persistence.*`、`javax.servlet.*`、`javax.validation.*`、`javax.transaction.*`、`javax.annotation.PostConstruct` / `PreDestroy` → **要改成 `jakarta.*`**。

**正确做法**：先只替换上面「要改」清单里的包名，编译一次；报错的地方逐个判断归属，**不要用一个正则把 `javax.` 全换掉**。
:::

## 二、主要新特性

| 特性 | 讲的是什么 | 关键入口 |
| --- | --- | --- |
| **AOT 与 GraalVM Native Image** | 构建期把 Bean 定义、反射与代理提前算好，产出原生可执行文件（启动毫秒级、内存更低） | `mvn -Pnative native:compile`、`@RegisterReflectionForBinding` |
| **ProblemDetails（RFC 7807 / 9457）** | 统一的机器可读错误响应体（`type` / `title` / `status` / `detail`） | `spring.mvc.problemdetails.enabled=true` |
| **声明式 HTTP 客户端** | 用接口 + `@HttpExchange` 声明调用，替代手写 `RestTemplate` 模板代码 | `HttpServiceProxyFactory` + `RestClient` / `WebClient` 适配器 |
| **可观测性一体化** | Micrometer **Observation API** 统一度量与链路追踪，**Micrometer Tracing 取代 Spring Cloud Sleuth** | `ObservedAspect`、`management.observations.*` |
| **函数式 Web 端点** | 用 `RouterFunction` + `HandlerFunction` 声明路由（WebFlux 早已支持，MVC 侧同样可用） | `RouterFunctions.route()` |
| **记录类（record）友好** | `@ConfigurationProperties` 支持 record 绑定，配置类可以写成不可变值对象 | `@ConfigurationProperties` + record |

::: tip 迁移时最该顺手用上的两个特性
1. **ProblemDetails**：如果现在返回的是自定义的 `{"code":500,"msg":"..."}` 结构，迁移期正好评估要不要切到标准结构——**机器可读的错误体对客户端和网关都更友好**。但它是**破坏性接口变更**，要单独排期，不要和框架迁移混在一起做。
2. **Micrometer Tracing**：Sleuth 已随 Spring Cloud 2022.0 退役，traceId 透传改用 Micrometer Tracing + Bridge（`micrometer-tracing-bridge-brave` 或 `-otel`）。**如果现在没接链路追踪，迁移是补上的最好时机**。
:::

## 三、配置属性的变化

3.0 对一批配置键做了重命名与移除。**不用靠记忆，用官方的迁移器**：

```xml [pom.xml —— 迁移期临时依赖]
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-properties-migrator</artifactId>
  <scope>runtime</scope>
  <optional>true</optional>
</dependency>
```

加上它之后启动应用，控制台会**逐条打印**「你用了已被移除 / 已重命名的属性，应该改成什么」。**确认全部改完之后把它删掉**——它只在迁移期用，留在生产会持续打印告警。

常见的变化方向（**具体键名以启动时打印的迁移提示与官方迁移指南为准**）：

| 方向 | 说明 |
| --- | --- |
| 指标导出器键名收窄 | `management.metrics.export.*` 一类扁平键逐步收窄为「按注册表分组」的形式 |
| Servlet 相关键 | 随 Servlet 5.0 基线调整，旧的 `server.*` 子键有增删 |
| 自动配置开关 | 随第 1 节的 imports 文件变更，`@ConditionalOnXxx` 的判定条件有细微差异 |

## 四、迁移步骤（可执行）

```shell
# ① 先升 JDK，再升框架（顺序反了会同时面对两类错误）
java -version      # 期望 17 或更高（推荐 21 LTS 以上）

# ② 升级父工程与依赖管理
#    pom.xml：把 <parent> 的 spring-boot-starter-parent 版本改成 3.x
#    Gradle：id 'org.springframework.boot' version '3.x.y'

# ③ 先量化 javax 的使用面，再动手
grep -rn "javax\." src/main/java --include=*.java | wc -l
grep -rn "javax\.\(persistence\|servlet\|validation\|transaction\)\." src/main/java | wc -l

# ④ 编译，按报错逐个改（不要无脑全局替换，见第 1 节的注意）
mvn -q -DskipTests compile

# ⑤ 迁移自己的 starter（若有）：spring.factories → imports 文件
ls src/main/resources/META-INF/spring.factories && echo "需要迁移自动配置注册文件"

# ⑥ 打开属性迁移器跑一次，收集属性改名清单
mvn spring-boot:run 2>&1 | grep -i "Property '" | head -30

# ⑦ 全量测试
mvn test
```

**收尾判据（四条必须同时成立）**：

1. `mvn -DskipTests compile` 通过，且 `grep -rn "javax\.\(persistence\|servlet\|validation\|transaction\)" src/main` **无输出**；
2. 应用能启动，启动日志里**没有**来自 `spring-boot-properties-migrator` 的属性提示；
3. `META-INF/spring.factories` 里**不再有** `EnableAutoConfiguration` 段（其他扩展点可以保留）；
4. 全量测试通过，且**至少跑通一条端到端主链路**——编译通过不等于行为一致，见下面的注意。

::: danger 迁移里最容易出的三类「编译通过但运行不对」
1. **序列化行为漂移**：Jackson 与 Hibernate 都是大版本升级，日期格式、`null` 处理、懒加载代理的序列化表现可能与 2.x 不同 → **用接口契约测试兜住**（比对升级前后同一请求的响应体）。
2. **校验注解失效**：`javax.validation` → `jakarta.validation` 时，若只改了 import 却没换校验实现（`spring-boot-starter-validation` 带来的 Hibernate Validator 版本），会出现「注解在、校验不生效」——**表现为接口直接放行非法参数**。
3. **过滤器 / 拦截器顺序变化**：Servlet 5.0 基线下 `Filter` 的注册与顺序语义有细微差异 → 认证、日志这类依赖顺序的组件要单独回归。
:::

## 五、3.x 内部的演进（选版本时看这里）

| 版本 | 值得注意的点 |
| --- | --- |
| 3.0 | Jakarta 基线、JDK 17、AOT、ProblemDetails、声明式 HTTP 客户端 |
| 3.1 | `spring.config.import` 用法更完善、Testcontainers 集成增强 |
| 3.2 | 支持 **Java 21**（虚拟线程：`spring.threads.virtual.enabled=true`）、`RestClient` 引入、可观测性继续完善 |
| 3.3 | 虚拟线程相关配置与 CDS 支持增强 |
| 3.4 / 3.5 | 以稳定性与依赖滚动升级为主；**3.5.x 的 OSS 支持已于 2026-06-30 结束** |

::: tip 存量 3.x 项目的现实选择
如果因为依赖（老版本 Spring Cloud、内部 starter）暂时上不了 4.x，务实的做法是：**升到 3.x 线内最后一个可用版本 + 把技术债记进台账**，并把「JDK 升级」与「Jakarta 迁移」这两件不可逆的事先做完——**它们做完之后，升 4.x 的难度会大幅下降**（4.x 的迁移面主要是 Spring Framework 7 与部分依赖基线，不再有命名空间级别的改动）。
:::

## 六、验证方式

```shell
# ① 命名空间残留
grep -rn "javax\.\(persistence\|servlet\|validation\|transaction\|annotation\.PostConstruct\|annotation\.PreDestroy\)" src/main/java | wc -l   # 期望 0

# ② 自动配置注册文件已迁移
test -f src/main/resources/META-INF/spring.factories && grep -c "EnableAutoConfiguration" src/main/resources/META-INF/spring.factories   # 期望 0 / 文件不存在

# ③ 启动无属性迁移告警
mvn spring-boot:run 2>&1 | grep -ci "properties-migrator\|Property '"   # 期望 0

# ④ 契约回归：升级前后同一请求的响应体一致
curl -s localhost:8080/api/health | sha256sum      # 与升级前的基线对比
```

预期：① 输出 `0`；② 输出 `0`（或文件已删除）；③ 输出 `0`；④ 与基线一致。

## 参考资料

- [Spring Boot 3.0 迁移指南（官方 Wiki）](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
- [Spring Boot 3.0 发布公告](https://spring.io/blog/2022/11/24/spring-boot-3-0-0-available-now)
- [Jakarta EE 平台规范](https://jakarta.ee/specifications/)
- [Spring Boot 4.x（当前稳定版）](../v4/index.md)：新一代版本与升级路径
- [SpringBoot 3.x 目录](./index.md)：本版本其他章节入口
- [Spring Boot 通用指南](../Common/index.md)：与版本无关的通用用法
