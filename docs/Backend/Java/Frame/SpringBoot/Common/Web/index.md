# Spring Boot Web 开发

Web 开发是 Spring Boot 使用最频繁的场景：接收 HTTP 请求、处理参数、返回 JSON、管理静态资源和跨域。本节覆盖 REST 控制器、参数绑定、CORS 与内嵌服务器配置。

::: info 适用版本
本节为 Spring Boot 通用指南，示例基于 4.1.x + Spring MVC；2.x/3.x 差异见版本目录。
:::

## 控制器基础

```java [UserController.java]
package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/users")
public class UserController {

    // GET /api/users
    @GetMapping
    public List<String> list() {
        return List.of("张三", "李四");
    }

    // GET /api/users/1
    @GetMapping("/{id}")
    public String detail(@PathVariable Long id) {
        return "用户 " + id;
    }

    // GET /api/users/search?keyword=张
    @GetMapping("/search")
    public String search(@RequestParam(defaultValue = "") String keyword) {
        return "搜索：" + keyword;
    }

    // POST /api/users
    @PostMapping
    public String create(@RequestBody User user) {
        return "创建：" + user.getName();
    }
}
```

常用注解：

| 注解 | 作用 |
| --- | --- |
| `@RestController` | `@Controller` + `@ResponseBody`，方法返回值直接写响应体 |
| `@GetMapping` / `@PostMapping` / `@PutMapping` / `@DeleteMapping` | HTTP 方法映射 |
| `@RequestParam` | 查询参数（`?name=x`） |
| `@PathVariable` | 路径参数（`/users/{id}`） |
| `@RequestBody` | 请求体 JSON 反序列化为对象 |
| `@RequestHeader` | 请求头 |
| `@CookieValue` | Cookie |

## 参数绑定

### 查询参数

```java
@GetMapping("/list")
public List<User> list(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int size) {
    // page 默认 1，size 默认 10
    return userService.page(page, size);
}
```

### 简单对象绑定

```java
public record PageQuery(int page, int size, String keyword) {}

@GetMapping("/list")
public List<User> list(PageQuery query) {
    return userService.page(query);
}
```

Spring MVC 会自动把 `?page=1&size=10&keyword=张` 绑定到 record 字段。

## 返回 JSON

默认使用 Jackson 序列化。返回对象、`List`、`Map` 都会自动转 JSON：

```java
@GetMapping("/{id}")
public User detail(@PathVariable Long id) {
    return userService.findById(id);
}
```

```java
public record User(Long id, String name, String email) {}
```

控制 JSON 字段：

```java
import com.fasterxml.jackson.annotation.JsonIgnore;

public record User(
        Long id,
        String name,
        @JsonIgnore String password,
        @JsonProperty("created_at") LocalDateTime createdAt
) {}
```

## 静态资源

把文件放入 `src/main/resources/static/`，直接通过根路径访问：

```text
static/
├─ index.html      # http://localhost:8080/
├─ css/app.css     # http://localhost:8080/css/app.css
└─ js/app.js       # http://localhost:8080/js/app.js
```

前后端分离项目中，静态资源通常交给 Nginx 或对象存储，Spring Boot 只提供 API。

## CORS 跨域

前后端分离时，浏览器会拦截跨域请求。全局配置：

```java [WebConfig.java]
package com.example.demo.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:5173")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .maxAge(3600);
    }
}
```

生产环境 `allowedOrigins` 不要写 `*` 且不开 `allowCredentials(true)`，否则会出安全问题。

## 内嵌服务器配置

```yaml [application.yml]
server:
  port: 8080
  tomcat:
    max-threads: 200
    min-spare-threads: 10
  shutdown: graceful        # 优雅停机
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

切换内嵌服务器（需要时）：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>
```

## 易错点

::: danger 常见错误
1. Controller 用 `@Controller` 而不是 `@RestController`，返回字符串时被当作视图名，页面 404 或白屏。
2. `@PathVariable` 名与路径占位符不一致（`{id}` 与 `Long userId`），报参数缺失。
3. 前端传 JSON 但方法用 `@RequestParam` 接收，`@RequestBody` 才能反序列化请求体。
4. 日期字段默认序列化格式不友好，需配置 `spring.jackson.date-format` 或使用 `@JsonFormat`。
5. CORS 配置了 `*` 又开 `allowCredentials`，浏览器直接报错。
6. 没有开启优雅停机，发版时正在处理的请求被强制中断。
:::

## 验证方式

1. `mvn spring-boot:run` 启动后：
   - `curl http://localhost:8080/api/users` 返回用户列表 JSON。
   - `curl http://localhost:8080/api/users/1` 返回 `用户 1`。
   - `curl -X POST http://localhost:8080/api/users -H "Content-Type: application/json" -d '{"name":"王五"}'` 返回创建结果。
2. 用 `curl -i` 查看响应头 `Content-Type: application/json`。
3. 前端开发服务器（如 http://localhost:5173）请求 API，确认无跨域报错。
4. 把 `index.html` 放入 `static/`，访问根路径能看到页面。

## 参考资料

- Spring MVC 官方文档：https://docs.spring.io/spring-framework/reference/web.html
- Spring Boot Web 应用：https://docs.spring.io/spring-boot/reference/web/index.html
- CORS：https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS
