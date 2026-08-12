# Spring Boot 配置与 Profile

Spring Boot 的配置体系解决「同一个应用在不同环境用不同配置」的问题：优先级、外部化配置、类型安全绑定和多环境 Profile。

::: info 适用版本
本节基于 Spring Boot 4.1.x，配置方式与 3.x 兼容（`application.properties` / `application.yml`）。
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

## 参考资料

- Spring Boot 外部化配置：https://docs.spring.io/spring-boot/how-to/properties-and-configuration.html
- 配置绑定：https://docs.spring.io/spring-boot/reference/features/external-config.html
- YAML 语法：https://yaml.org/
