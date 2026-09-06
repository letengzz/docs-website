# 常见问题与最佳实践

本章汇总 Spring Cloud 落地过程中的高频问题，按「启动与版本 → 注册发现 → 服务调用 → 网关 → 配置 → 熔断 → 可观测性」组织，每个问题给原因与可执行的处理步骤。

## 版本与启动

### 启动报错：无法解析 `spring-cloud-starter-*`

**原因**：没有引入 `spring-cloud-dependencies` BOM，或 BOM 版本写错。

**处理**：

```xml [pom.xml]
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>2025.1.2</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### `NoClassDefFoundError` / `NoSuchMethodError`（版本错配）

**原因**：Spring Cloud Train 与 Spring Boot 大版本不匹配，或本地 Maven 仓库缓存了旧组件。

**处理**：

1. 用 `mvn dependency:tree -Dincludes=org.springframework.cloud` 查看实际版本。
2. 对照官方版本表核对 Train 与 Boot 版本。
3. 清掉本模块缓存重新构建（`mvn clean`，必要时删除本地仓库对应目录后重新下载）。

### 提示 `Minimum supported Java version is 17`

Spring Cloud 2022.0+（Spring Boot 3+）要求 JDK 17；确认 `JAVA_HOME`、IDE 项目 SDK、Maven `toolchains` 三者一致。

## 注册发现

### 服务列表为空

1. 检查 `spring.application.name` 是否配置（没有它无法确定服务名）。
2. 检查 `spring.cloud.nacos.discovery.server-addr` 拼写与端口。
3. 控制台看 Nacos「服务列表」，两侧命名空间是否一致。

### 实例反复掉线 / 状态不健康

Nacos 2.x/3.x 客户端走 gRPC（9848/9849），只放行 8848 会导致心跳异常。Docker 部署时把三个端口都映射出来，并在安全组放行。

### 注册中心挂了对业务的影响

客户端有本地缓存，实例列表已获取时仍可短时调用。**不要**在请求路径上每次实时访问注册中心；生产建议注册中心集群 + 客户端缓存兜底。

## 服务调用

### Feign 调用报 `No instances available for stock-service`

依次排查：

1. stock-service 是否真的注册成功（Nacos 服务列表）。
2. `@FeignClient(name = ...)` 与注册的服务名是否完全一致。
3. 是否引入 `spring-cloud-starter-loadbalancer`（2020.0 后不再自动带）。

### Feign 接口 404

对比拼接路径：`@FeignClient(path)` + 方法注解路径，必须与服务端 `@RequestMapping` + `@GetMapping` 拼接结果一致。多级前缀时用网关 `StripPrefix` 与 Feign `path` 时最容易算错。

### 超时与重试配置

```yaml [application.yml]
spring:
  cloud:
    openfeign:
      client:
        config:
          default:
            connect-timeout: 2000
            read-timeout: 5000
```

重试要放在**调用边界**（Feign 层或 Resilience4j Retry），不要每层都重试，否则放大流量。

## 网关

### 网关启动后路由不生效

最常见原因是**混入 `spring-boot-starter-web`**，应用以 SERVLET 模式启动而非 WebFlux。网关模块删除 web starter，只保留 gateway starter（自带 WebFlux + Netty）。

### 如何给下游透传用户信息

用 `GlobalFilter` 校验 JWT 后把用户 ID 写入请求头（`exchange.mutate()`），下游 Feign/Controller 从请求头读取；不要把用户对象塞进 URL。

### 网关跨域处理

在网关统一配置 CORS；若下游再配一遍，预检请求会被处理两次产生冲突。

## 配置中心

### 配置改了不生效

1. Bean 是否加 `@RefreshScope`（`@Value` 依赖 Bean 要重建才会拿新值）。
2. Nacos 控制台修改后是否点击**发布**（只保存不发布不会推送）。
3. `spring.config.import` 的 Data ID 是否与实际发布的完全一致（含后缀）。

### SCA 2025.x 找不到 `bootstrap.yml`

bootstrap 支持已移除，改用：

```yaml [application.yml]
spring:
  config:
    import: nacos:order-service-dev.yaml
```

## 熔断与降级

### fallback 不执行

1. OpenFeign 需要 `spring.cloud.openfeign.circuitbreaker.enabled=true`。
2. fallback 类需被 Spring 管理（`@Component`）并实现 Feign 接口。
3. fallback 方法签名要与原方法一致（含参数顺序），或使用 `fallbackFactory`。

### 熔断器被业务异常误触发

用 `ignoreExceptions` 排除可预期的业务异常（如参数错误、库存不足），熔断只针对**基础设施/下游不可用类错误**。

### 怎么判断当前熔断状态

暴露 actuator：

```yaml [application.yml]
management:
  endpoints:
    web:
      exposure:
        include: health,circuitbreakers
```

访问 `/actuator/circuitbreakers` 查看各实例状态，并把熔断打开接成告警。

## 可观测性与链路

### 日志里没有 traceId

确认 `logging.pattern.level` 已包含 `%X{traceId:-}`，且引入 `micrometer-tracing-bridge-otel`（Sleuth 在 2024.0 已退役）。

### Zipkin 里链路断成几段

通常是**线程池/异步**导致上下文丢失，或某服务没配导出。排查：把采样率临时调 1.0，逐个服务验证 `traceparent` 请求头是否传递。

### 存储成本高

采样率从 `1.0` 降到 `0.05~0.1`；只对需要完整追踪的链路（如压测）临时全量。

## 综合最佳实践清单

::: tip 生产落地清单
1. **版本即资产**：用一个父 POM 集中维护 Spring Cloud/SCA/Boot 版本，禁止子模块各自写版本。
2. **依赖最小化**：用哪个组件加哪个 starter，网关不加 web、普通服务不加 gateway。
3. **配置进中心**：业务开关、限流阈值、路由规则尽量配置中心化，保留最小本地启动配置。
4. **调用边界治理**：超时、重试、熔断统一在 Feign/服务边界配置，并互相配合不打架。
5. **安全默认开**：Nacos 改默认密码、网关校验 JWT、配置中心敏感信息加密。
6. **可观测性三件套**：指标（Prometheus）+ 日志（traceId）+ 链路（Zipkin/SkyWalking）一起上，缺一个都难排障。
7. **全链路压测**：上线前用压测验证熔断阈值、限流容量与数据库连接池上限。
:::

## 相关专题衔接

- 方法论与拆分：[微服务专题](../../Microservices/index.md)
- 消息队列与可靠性：[消息队列专题](../../MessageQueue/index.md)
- Spring Boot 基础：[Spring Boot 通用指南](../../Java/Frame/SpringBoot/Common/index.md)
- 网络与协议基础：[网络编程专题](../../NetworkProgramming/index.md)

## 参考资料

- Spring Cloud Reference：https://docs.spring.io/spring-cloud/reference/
- Spring Cloud 版本支持：https://endoflife.date/spring-cloud
- Spring Cloud Alibaba：https://sca.aliyun.com/docs/2025.x/overview/overview/
- Nacos：https://nacos.io/docs/latest/
