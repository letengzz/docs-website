# Spring Boot 配置与 Profile

Spring Boot 的配置体系解决「同一个应用在不同环境用不同配置」的问题：优先级、外部化配置、类型安全绑定和多环境 Profile。

::: info 适用版本
本节为 Spring Boot 通用指南，配置方式在 2.x/3.x/4.x 间基本兼容；示例基于 4.1.x。
:::

## 配置文件格式

两种格式等价，推荐 YAML（可读性好、支持嵌套）：

```properties [application.properties]
server.port=8080
spring.application.name=demo
app.name=示例应用
```

```yaml [application.yml]
server:
  port: 8080
spring:
  application:
    name: demo
app:
  name: 示例应用
```

## 读取配置

### @Value 注入

```java [HelloController.java]
@RestController
public class HelloController {
    @Value("${app.name:默认名称}")
    private String appName;

    @GetMapping("/name")
    public String name() {
        return appName;
    }
}
```

### @ConfigurationProperties 类型安全绑定

推荐把一组配置绑定到 POJO，编译期就能发现拼写错误：

```yaml [application.yml]
app:
  name: 示例应用
  version: 1.0.0
  authors:
    - 张三
    - 李四
```

```java [AppProperties.java]
package com.example.demo.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.List;

@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;
    private String version;
    private List<String> authors = List.of();

    // getter / setter
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }
    public List<String> getAuthors() { return authors; }
    public void setAuthors(List<String> authors) { this.authors = authors; }
}
```

启用绑定：

```java [DemoApplication.java]
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import com.example.demo.config.AppProperties;

@SpringBootApplication
@EnableConfigurationProperties(AppProperties.class)
public class DemoApplication {
    // ...
}
```

## 配置优先级

Spring Boot 的配置来源按优先级从高到低（高优先级覆盖低优先级）：

1. 命令行参数（`java -jar app.jar --server.port=9090`）。
2. `SPRING_APPLICATION_JSON` 环境变量。
3. 系统环境变量。
4. `application-{profile}.yml`（Profile 专用配置）。
5. `application.yml`（主配置）。
6. 默认值（`@Value` 中的默认值等）。

生产环境常用环境变量或 `--spring.config.additional-location` 注入配置，避免把密码写进代码库。

## Profile 多环境

按环境拆分文件：

```text
application.yml              # 公共配置
application-dev.yml          # 开发环境
application-test.yml         # 测试环境
application-prod.yml         # 生产环境
```

激活方式：

```shell
java -jar app.jar --spring.profiles.active=prod
```

```yaml [application-prod.yml]
server:
  port: 8080
spring:
  datasource:
    url: jdbc:mysql://prod-db:3306/app
    username: ${DB_USER}
    password: ${DB_PASSWORD}
```

代码中可以用 `@Profile` 控制 Bean 只在指定环境加载：

```java
@Service
@Profile("prod")
public class ProdPaymentService implements PaymentService {
    // 只在 prod 环境生效
}
```

## 随机值与占位符

```yaml
app:
  token: ${APP_TOKEN:default-token}
  port: ${random.int[1024,65535]}
```

`${VAR:default}` 表示读取环境变量 `VAR`，不存在时用默认值，适合容器化部署。

## 敏感信息处理

1. 密码不要写死在 `application.yml`，用环境变量注入。
2. 使用 Spring Vault 或云厂商的密钥管理（KMS）保存密钥。
3. `.env` 类文件加入 `.gitignore`。

## 易错点

::: danger 常见错误
1. YAML 缩进错误（Tab 与空格混用），启动报 `document root must not be empty` 或解析失败。
2. `@ConfigurationProperties` 忘记 `@EnableConfigurationProperties` 或忘记 getter/setter，绑定后全是 null。
3. 生产环境把密码写进 `application.yml` 并提交 Git。
4. 激活了 `prod` Profile 但没有对应文件，应用仍使用默认配置，行为与预期不符。
5. 环境变量名大小写不敏感导致混乱，建议统一用大写并加前缀。
6. `spring.profiles.active` 与 `spring.profiles.default` 混淆，前者是显式激活，后者是兜底。
:::

## 验证方式

1. 访问 `/name` 接口，返回 `app.name` 配置的值。
2. 用 `--server.port=9090` 启动，确认端口变成 9090（命令行优先级最高）。
3. `--spring.profiles.active=dev` 启动后，`/name` 读取 `application-dev.yml` 的值。
4. 把 `app.version` 写错为 `app.versionx`，`@ConfigurationProperties` 启动时能发现未知字段（开启 `ignoreUnknownFields=false` 时）。
5. 生产环境用环境变量 `APP_TOKEN` 注入，未设置时使用默认值。

## 配置的加载顺序与刷新边界（第 188 天补充）

本页讲的是"单进程内怎么读到配置"。当配置来自**配置中心**时，多出两个问题：优先级怎么排、改了什么时候生效。完整机制见 [配置管理与动态配置](../../../../../../Ops/ConfigManagement/index.md)，这里只留四条能直接用的结论：

1. **优先级**：配置中心的 `PropertySource` 默认排在本地 `application.yml` 之后（更高），所以"本地写了但没生效"通常是正常的；反过来，**环境变量仍然能盖掉配置中心**（`PropertySource` 顺序在 Spring Boot 里是 `systemEnvironment` 高于大多数 `bootstrap`/`config` 源），这就是"中心里改了半天不生效"的最常见原因。
2. **三种写法的刷新行为不同**：`@Value` 依赖所在 bean 是否重建（普通 bean 不会重建，值不变）；`@ConfigurationProperties` 会重新绑定；`@RefreshScope` 会销毁重建该 bean（代价最大）。
3. **有一类配置改了没用**：连接池大小、线程池核心数、服务端口这类"构造期决定"的参数，热更新不生效，只能重启——验收要读运行时的真实值，不要读配置文件。
4. **生效延迟**：服务端缓存窗口（实测 ≤100 ms）+ 客户端轮询周期（默认 30 s，实测挂 29.51 s）之和，不是"立刻"。

对应的验证方式：给应用加一个只读端点，返回**进程里真实生效的值**（读的是注入后的字段，不是文件），再配合配置中心的历史版本号做对照。

## 参考资料

- Spring Boot 外部化配置：https://docs.spring.io/spring-boot/how-to/properties-and-configuration.html
- 配置绑定：https://docs.spring.io/spring-boot/reference/features/external-config.html
- YAML 语法：https://yaml.org/
