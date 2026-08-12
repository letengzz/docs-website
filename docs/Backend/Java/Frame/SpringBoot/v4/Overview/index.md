# Spring Boot 概述与版本

Spring Boot 是 Spring 生态的「开箱即用」框架，通过自动配置（Auto-configuration）和起步依赖（Starter）大幅降低 Spring 应用的搭建成本。本节介绍它解决什么问题、当前版本现状和核心机制。

::: info 适用版本（2026-08 核对）
当前稳定版为 **Spring Boot 4.1.x**（4.0 于 2025-11 发布，4.1 于 2026-06 发布）。Spring Boot 4 基于 Spring Framework 7，最低支持 Java 17，**推荐使用 Java 25 LTS**。Spring Boot 3.5.x 的 OSS 支持已于 2026-06-30 结束，存量项目建议规划升级。
:::

## Spring Boot 解决什么问题

传统 Spring 项目搭建需要手动完成大量重复工作：

1. 引入十几个依赖并手工对齐版本（Spring MVC、Jackson、Tomcat、数据库驱动……）。
2. 编写大量 XML 或 Java 配置（数据源、事务、视图解析器、消息转换器……）。
3. 配置外部 Tomcat、打 war 包、部署。

Spring Boot 用三个机制解决：

| 机制 | 作用 |
| --- | --- |
| 起步依赖（Starter） | 一个依赖引入一组功能（如 `spring-boot-starter-web` 自带 Web 全家桶） |
| 自动配置（Auto-configuration） | 根据 classpath 和配置自动装配 Bean，开箱即用 |
| 内嵌服务器 | 内置 Tomcat/Jetty/Undertow，直接 `java -jar` 运行 |

## 版本演进

| 大版本 | 发布时间 | 基础框架 | 最低 Java | 说明 |
| --- | --- | --- | --- | --- |
| Spring Boot 2.x | 2018-11 | Spring 5 | Java 8 | 长期存量主力，已停止 OSS 支持 |
| Spring Boot 3.x | 2022-11 | Spring 6 | Java 17 | Jakarta EE 9+，`javax` 迁移为 `jakarta` |
| Spring Boot 3.5.x | 2025-05 | Spring 6.2 | Java 17 | 3.x 最后一代，OSS 支持已于 2026-06 结束 |
| Spring Boot 4.x | 2025-11 | Spring 7 | Java 17 | 当前稳定版，推荐 Java 25，默认 Jackson 3 |

## 核心机制

### 自动配置

主启动类上的 `@SpringBootApplication` 组合了三个注解：

```java [DemoApplication.java]
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

- `@SpringBootConfiguration`：标记为配置类。
- `@EnableAutoConfiguration`：开启自动配置。
- `@ComponentScan`：扫描当前包及其子包下的组件。

自动配置遵循「条件装配」：classpath 有 `spring-boot-starter-web` 就自动配置嵌入式 Tomcat 和 Spring MVC；有 `spring-boot-starter-data-jpa` 和数据库驱动就自动配置数据源与 JPA。

### 起步依赖

常用 Starter：

| Starter | 功能 |
| --- | --- |
| `spring-boot-starter-web` | Spring MVC + 内嵌 Tomcat + JSON |
| `spring-boot-starter-data-jpa` | Spring Data JPA + Hibernate |
| `spring-boot-starter-validation` | Bean Validation（校验注解） |
| `spring-boot-starter-security` | Spring Security |
| `spring-boot-starter-actuator` | 健康检查、指标、运维端点 |
| `spring-boot-starter-test` | 测试全家桶（JUnit、AssertJ、Mockito 等） |
| `spring-boot-starter-data-redis` | Redis 客户端 |

## 什么时候用 Spring Boot

适合：

- 绝大多数 Java Web 后端（REST API、后台系统、微服务）。
- 快速原型和企业级项目都适用。
- 与 Spring Cloud、Spring Security、Spring Data 等生态配合。

不适合或需要评估：

- 极简单的脚本类任务（直接用 Java SE 更轻）。
- 已有成熟的非 Spring 技术栈（如 Quarkus、Micronaut），除非团队熟悉 Spring。

## 易错点

::: danger 常见错误
1. 主启动类放在错误的包层级，`@ComponentScan` 扫不到 Controller/Service，接口 404。
2. 混用 `javax.*` 与 `jakarta.*` 依赖，启动时报类冲突（Spring Boot 3+ 必须用 `jakarta`）。
3. 手工管理依赖版本，和 Spring Boot BOM 冲突，出现 NoSuchMethodError。
4. 使用已经停止 OSS 支持的 3.5.x 且不升级，安全补丁缺失。
5. 不知道自动配置的存在，重复手写数据源/事务配置，导致多个 DataSource Bean 冲突。
:::

## 验证方式

1. 访问 https://start.spring.io 生成一个 `Web` 项目并下载。
2. `mvn spring-boot:run` 启动，访问 http://localhost:8080/actuator/health（需引入 actuator）返回 JSON。
3. `mvn package` 后执行 `java -jar target/*.jar`，确认内嵌服务器直接启动。
4. 打开 http://localhost:8080，确认没有 404 白页（默认有错误页）。

## 参考资料

- Spring Boot 官方文档：https://docs.spring.io/spring-boot/index.html
- Spring Initializr：https://start.spring.io/
- Spring Boot 4.0 发布公告：https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now
- Spring Boot 版本支持：https://endoflife.date/spring-boot
