# Spring Boot 常见问题与最佳实践

汇总 Spring Boot 开发与部署中最高频的问题，并给出一份生产自查清单。

::: info 适用版本
本文为 Spring Boot 通用 FAQ（3.x/4.x），涉及版本差异时会注明。
:::

## 生产自查清单

- [ ] 使用受支持的 Spring Boot 大版本（当前 4.x），3.5.x OSS 已结束
- [ ] JDK 17+（推荐 25 LTS）
- [ ] 数据库密码通过环境变量/密钥管理注入，不写进代码库
- [ ] 配置了健康检查（`/actuator/health`）并接入探活
- [ ] 生产关闭 `open-in-view`，`ddl-auto` 使用 `validate` 或 `none`
- [ ] 接口使用 DTO，不直接暴露实体
- [ ] 全局异常处理，不向客户端泄露堆栈
- [ ] 日志走 stdout 并接入日志系统
- [ ] 配置优雅停机
- [ ] Actuator 端点最小暴露并加鉴权
- [ ] 容器内 JVM 使用 `-XX:MaxRAMPercentage` 限制内存
- [ ] 有自动化测试和覆盖率检查

## 常见问题

### 1. 启动报「Port 8080 was already in use」

端口被占用。换端口或释放端口：

```shell
netstat -ano | findstr 8080
taskkill /PID <进程号> /F
```

或启动时指定：`java -jar demo.jar --server.port=9090`。

### 2. 接口 404，Controller 明明写了

排查顺序：

1. 启动类是否在包的最外层（`com.example.demo`），Controller 是否在其子包下。
2. 是否用了 `@RestController` 而不是 `@Controller`。
3. 访问路径是否完全匹配（大小写、`/api` 前缀）。
4. 是不是打成 jar 后资源没更新，重新 `mvn clean package`。

### 3. 修改 application.yml 不生效

- 确认文件在 `src/main/resources/` 下且文件名正确（`application.yml` 或 `application-{profile}.yml`）。
- 修改后需要重启（开发热更新可用 spring-boot-devtools，但生产不要依赖）。
- 检查是否有更高优先级配置（环境变量、命令行参数）覆盖。

### 4. 数据库连接失败

```text
Failed to configure a DataSource: 'url' attribute is not specified
```

没引入数据库驱动或没配 `spring.datasource.url`。确认：

1. 引入了 `spring-boot-starter-data-jpa` 和对应驱动（MySQL 用 `mysql-connector-j`）。
2. `application.yml` 中 url/username/password 正确。
3. 数据库服务可达（`telnet 主机 3306` 或直接连客户端验证）。

### 5. JSON 序列化问题：日期格式、循环引用

```yaml [application.yml]
spring:
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: Asia/Shanghai
```

实体间双向关联会循环引用，用 DTO 或 `@JsonIgnore` 解决。

### 6. CORS 跨域报错

见「Web 开发」篇的 CORS 配置。注意：

- `allowedOrigins` 不要与 `allowCredentials(true)` 同时用 `*`。
- 后端跨域配置后，前端请求仍失败时检查浏览器 Network 的 `Access-Control-Allow-Origin` 响应头。

### 7. 从 Spring Boot 3 升级到 4

重点检查：

- Spring Framework 7 基础，Java 17 最低，推荐 Java 25。
- 默认 JSON 库从 Jackson 2 升级为 Jackson 3，包名/API 有变化。
- 部分 starter 模块化调整，检查依赖是否仍然存在。
- 使用 Spring Boot 官方升级工具和 `spring-boot-migrator` 辅助迁移。

存量项目不要原地大改，先在分支验证升级，再灰度发布。

### 8. 容器里 OOM 或被系统杀掉

JVM 默认按宿主机内存计算堆大小，容器内存限制下容易 OOM。使用：

```shell
java -XX:MaxRAMPercentage=75 -jar app.jar
```

并确认 Docker 的 `--memory` 限制与 JVM 配置匹配。

### 9. 时区问题：时间差 8 小时

```yaml [application.yml]
spring:
  jackson:
    time-zone: Asia/Shanghai
```

数据库连接串加 `serverTimezone=Asia/Shanghai`，容器设置 `TZ=Asia/Shanghai`。

## 最佳实践

1. **分层清晰**：Controller → Service → Repository，DTO 隔离。
2. **配置集中**：`@ConfigurationProperties` 绑定配置，避免到处 `@Value`。
3. **事务边界正确**：事务放在 Service 方法上，不在 Controller 开事务。
4. **异步任务**：用 `@Async` + 独立线程池，避免阻塞请求线程。
5. **安全默认**：字段校验、权限控制、防注入（JPA 参数绑定天然防注入）。
6. **监控先行**：上线前接入 Actuator、Prometheus、日志采集。

## 验证方式

1. 对照自查清单逐项确认。
2. `mvn test` 与 `mvn package` 全部通过。
3. 生产环境用 `--spring.profiles.active=prod` 启动，确认读取生产配置。
4. 压测/冒烟测试核心接口，观察健康检查与指标。
5. 演练一次发版：优雅停机、回滚、日志排查全流程。

## 相关专题

- [消息队列专题](../../../../../MessageQueue/index.md)：Spring Boot 集成 Kafka/RabbitMQ 的可靠投递、消费幂等与集群部署
- [Java 并发专题](../../../../../Java/JavaSE/Multithreading/index.md)：`@Async` 异步任务与线程池的底层原理

## 参考资料

- Spring Boot 官方文档：https://docs.spring.io/spring-boot/index.html
- Spring Boot 升级指南：https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
- Spring Boot 支持时间表：https://endoflife.date/spring-boot
