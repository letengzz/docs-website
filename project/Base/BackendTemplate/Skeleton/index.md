# 骨架与目录结构（第 69 天 · 步骤 ①）

本页交付第一个**可运行**的骨架：多模块 Maven 工程、启动类、配置文件。目标是"拉下代码就能跑起来"，这是后续所有模块的基座。

![多模块骨架](../assets/skeleton-tree.svg)

## 工程结构

```text
backend-template/
├─ pom.xml                        # 聚合 POM：模块列表 + 依赖版本管理（dependencyManagement）
├─ template-common/               # 无 Web 依赖的基础模块
│  ├─ pom.xml
│  └─ src/main/java/com/example/template/common/
│     ├─ result/Result.java
│     ├─ result/ErrorCode.java
│     └─ exception/BizException.java
├─ template-data/
├─ template-security/
├─ template-web/
├─ template-application/          # 唯一可启动模块
│  ├─ pom.xml
│  └─ src/main/
│     ├─ java/com/example/template/TemplateApplication.java
│     └─ resources/
│        ├─ application.yml
│        ├─ application-dev.yml
│        └─ application-prod.yml
├─ docker/
├─ scripts/
└─ docs/
```

## 根 POM（聚合与版本管理）

```xml [pom.xml]
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <!-- Spring Boot 4.1.x 为当前稳定版（2026-06 发布，基于 Spring Framework 7） -->
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.1.1</version>
    <relativePath/>
  </parent>

  <groupId>com.example</groupId>
  <artifactId>backend-template</artifactId>
  <version>1.0.0</version>
  <packaging>pom</packaging>

  <modules>
    <module>template-common</module>
    <module>template-data</module>
    <module>template-security</module>
    <module>template-web</module>
    <module>template-application</module>
  </modules>

  <properties>
    <java.version>25</java.version>
    <mybatis-plus.version>3.5.9</mybatis-plus.version>
    <springdoc.version>2.8.9</springdoc.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <!-- 各子模块版本统一在此声明 -->
      <dependency>
        <groupId>com.example</groupId>
        <artifactId>template-common</artifactId>
        <version>${project.version}</version>
      </dependency>
      <dependency>
        <groupId>com.example</groupId>
        <artifactId>template-data</artifactId>
        <version>${project.version}</version>
      </dependency>
      <dependency>
        <groupId>com.example</groupId>
        <artifactId>template-security</artifactId>
        <version>${project.version}</version>
      </dependency>
      <dependency>
        <groupId>com.example</groupId>
        <artifactId>template-web</artifactId>
        <version>${project.version}</version>
      </dependency>
    </dependencies>
  </dependencyManagement>
</project>
```

::: danger 版本号写法的三个坑
1. **子模块重复声明 `<version>` 与父版本**：应由 `dependencyManagement` 统一管理，否则升级版本要改 N 处，漏一处就出现版本不一致。
2. **父 POM 用 `<relativePath/>` 指向空**：这表示"父 POM 只从仓库解析"，如果本地私服没有该版本会直接失败；内网环境建议先把父 POM 部署到私服，或显式指向本地路径。
3. **`java.version` 与本地 JDK 不一致**：模板要求 JDK 25（Spring Boot 4.x 最低 Java 17、推荐 25），用 17 编译出的产物在部分特性上行为不同，团队要统一 JDK。
:::

## 启动模块 POM

```xml [template-application/pom.xml]
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>com.example</groupId>
    <artifactId>backend-template</artifactId>
    <version>1.0.0</version>
  </parent>

  <artifactId>template-application</artifactId>

  <dependencies>
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>template-web</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-test</artifactId>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <finalName>${project.artifactId}-${project.version}</finalName>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
        <configuration>
          <mainClass>com.example.template.TemplateApplication</mainClass>
        </configuration>
        <executions>
          <!-- 让 /actuator/info 能读到构建信息 -->
          <execution>
            <goals>
              <goal>build-info</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>
```

## 启动类

```java [template-application/src/main/java/com/example/template/TemplateApplication.java]
package com.example.template;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 模板启动类。
 * scanBasePackages 指向 com.example.template，覆盖 common/data/security/web 各模块。
 */
@SpringBootApplication(scanBasePackages = "com.example.template")
public class TemplateApplication {

    public static void main(String[] args) {
        SpringApplication.run(TemplateApplication.class, args);
    }
}
```

::: warning 多模块下扫描不到 Bean 是最常见的问题
子模块的包路径如果不是启动类的子包（例如启动类在 `com.example.template`，而某模块在 `com.example` 下），默认扫描会漏掉。模板统一约定：**所有模块的根包都为 `com.example.template.*`**，并在启动类显式写出 `scanBasePackages`，双保险。
:::

## 配置文件

```yaml [template-application/src/main/resources/application.yml]
server:
  port: 8080
  shutdown: graceful          # 优雅停机，避免 kill 时丢请求

spring:
  application:
    name: backend-template
  profiles:
    active: ${APP_PROFILE:dev} # 环境变量优先，默认 dev
  jackson:
    default-property-inclusion: non_null   # 空字段不输出，减小响应体
    time-zone: Asia/Shanghai

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: when-authorized

logging:
  level:
    root: info
    com.example.template: debug
  pattern:
    console: "%d{HH:mm:ss.SSS} %-5level [%X{traceId:-}] %logger{36} - %msg%n"
```

```yaml [template-application/src/main/resources/application-dev.yml]
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/template?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: ${DB_USER:root}
    password: ${DB_PASSWORD:root}
```

::: danger 配置文件的三条红线
1. **密码写死在仓库里**：必须用 `${DB_PASSWORD}` 这类环境变量占位，仓库里只放占位符。
2. **生产开启 debug 日志**：`logging.level.root: debug` 在生产会拖慢性能并可能打印敏感数据，生产用 `info`。
3. **`spring.profiles.active` 硬编码**：硬编码成 `prod` 会导致本地也连生产库，必须用 `${APP_PROFILE:dev}` 形式。
:::

## 验证方式

```shell
# 1. 编译打包（跳过测试先验证骨架）
mvn -q clean package -DskipTests
ls template-application/target/template-application-1.0.0.jar

# 2. 启动（默认 dev Profile）
java -jar template-application/target/template-application-1.0.0.jar
```

预期输出（关键行）：

```text
2026-09-14 08:20:11.512 INFO  [           ] c.e.template.TemplateApplication - Starting TemplateApplication using Java 25
2026-09-14 08:20:13.884 INFO  [           ] o.s.b.w.embedded.tomcat.TomcatWebServer - Tomcat started on port 8080 (http)
2026-09-14 08:20:13.902 INFO  [           ] c.e.template.TemplateApplication - Started TemplateApplication in 3.2 seconds
```

```shell
# 3. 确认端口与进程正常
curl -i -s http://localhost:8080/actuator/health
# 预期：HTTP/1.1 200，body 含 {"status":"UP"}
```

收尾确认：打包成功、日志出现 `Started TemplateApplication`、健康端点返回 200。

## 参考资料

- Spring Boot 官方文档：[Build Systems / Maven 多模块](https://docs.spring.io/spring-boot/maven-plugin/index.html)
- 相关文档：[需求与架构设计](../Architecture/index.md) / [统一响应与全局异常](../CommonResponse/index.md)
