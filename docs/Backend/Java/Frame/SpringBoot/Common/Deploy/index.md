# Spring Boot 部署

部署解决「把 jar 跑起来并稳定运维」的问题：打包、容器化、环境配置、健康检查、日志与优雅停机。

::: info 适用版本
本节为 Spring Boot 通用指南，示例基于 4.1.x + Docker；运行时镜像按项目 JDK 选择（如 Temurin 25）。
:::

## 打包方式

```shell
# 可执行 fat jar（包含内嵌 Tomcat）
mvn package -DskipTests
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

打 war 包（部署到外部 Tomcat）：

1. `pom.xml` 的 `<packaging>war</packaging>`。
2. 启动类继承 `SpringBootServletInitializer` 并重写 `configure`。

现代部署几乎都用 fat jar + 容器，外部 Tomcat 方式已不推荐。

## 生产环境配置

通过环境变量注入，不修改 jar：

```shell
export SPRING_PROFILES_ACTIVE=prod
export DB_URL=jdbc:mysql://db:3306/app
export DB_USER=app
export DB_PASSWORD='安全密码'
java -jar demo.jar --server.port=8080
```

对应 `application-prod.yml` 使用 `${DB_URL}` 等占位符（见「配置与 Profile」篇）。

## Docker 部署

### 多阶段 Dockerfile

```dockerfile [Dockerfile]
FROM maven:3.9-eclipse-temurin-25 AS build
WORKDIR /workspace

COPY pom.xml .
RUN mvn -B dependency:go-offline

COPY src ./src
RUN mvn -B -DskipTests package

FROM eclipse-temurin:25-jre
WORKDIR /app

RUN useradd -r -u 10001 app
COPY --from=build /workspace/target/demo-0.0.1-SNAPSHOT.jar app.jar
USER app

EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
```

`-XX:MaxRAMPercentage=75` 让 JVM 根据容器内存自动设置堆大小，避免内存超限。

### 构建与运行

```shell
docker build -t demo:1.0.0 .
docker run -d --name demo \
  -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=prod \
  -e DB_URL='jdbc:mysql://db:3306/app' \
  -e DB_USER=app \
  -e DB_PASSWORD='安全密码' \
  demo:1.0.0
```

### docker-compose

```yaml [docker-compose.yml]
services:
  app:
    image: demo:1.0.0
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_URL: jdbc:mysql://db:3306/app
      DB_USER: app
      DB_PASSWORD: ${DB_PASSWORD}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: app
    volumes:
      - db-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  db-data:
```

## Actuator 运维端点

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml [application-prod.yml]
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
```

常用端点：

| 端点 | 作用 |
| --- | --- |
| `/actuator/health` | 健康检查（容器/负载均衡探活） |
| `/actuator/info` | 应用信息 |
| `/actuator/metrics` | 指标列表 |
| `/actuator/prometheus` | Prometheus 指标（配合监控） |

生产环境不要把 `health` 的详细信息公开给未授权用户。

## 日志

```yaml [application-prod.yml]
logging:
  file:
    name: /var/log/app/app.log
  level:
    root: info
    com.example.demo: info
```

容器部署建议日志输出到 stdout（默认），由 Docker/Promtail/Filebeat 收集，而不是写文件：

```shell
docker logs -f demo
```

## 优雅停机

```yaml [application.yml]
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

收到停止信号后，Spring 会停止接收新请求，等待进行中的请求完成再退出，避免发版时请求被掐断。

## 反向代理

生产通常在前面加 Nginx：

```nginx [nginx.conf]
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 易错点

::: danger 常见错误
1. `mvn package` 后 jar 无法运行，报「没有主清单属性」：缺少 `spring-boot-maven-plugin`。
2. 容器内 JVM 默认按宿主机内存分配堆，`-Xmx` 不设或设错导致 OOM；用 `-XX:MaxRAMPercentage`。
3. 健康检查用 200 页面而不是 `/actuator/health`，数据库挂了探活仍通过。
4. 生产配置写死数据库密码并打进镜像。
5. 没有优雅停机，发版时请求被强制中断。
6. Actuator 全端点暴露且无鉴权。
:::

## 验证方式

1. `java -jar demo.jar` 启动后 `curl http://localhost:8080/actuator/health` 返回 `UP`。
2. `docker build -t demo:1.0.0 .` 成功，镜像体积合理。
3. `docker compose up -d` 后应用与 MySQL 都健康，接口可访问。
4. 执行 `docker stop demo`，观察日志确认优雅停机流程。
5. 停掉 MySQL，`/actuator/health` 状态变为 `DOWN`，负载均衡能摘除节点。

## 参考资料

- Spring Boot 部署文档：https://docs.spring.io/spring-boot/reference/packaging.html
- Actuator：https://docs.spring.io/spring-boot/reference/actuator/index.html
- Docker 官方 Java 指南：https://docs.docker.com/language/java/
- Nginx：https://nginx.org/en/docs/
