# Spring Boot REST API

本节把「接口设计 + 参数校验 + 统一响应 + 分页 + 接口文档」串起来，给出一个可落地的 REST API 写法。

::: info 适用版本
本节为 Spring Boot 通用指南，示例基于 4.1.x；校验使用 `spring-boot-starter-validation`，接口文档使用 springdoc-openapi。
:::

## 接口设计规范

| 资源 | 方法 | 路径 | 语义 |
| --- | --- | --- | --- |
| 用户列表 | GET | `/api/users` | 查询（支持分页） |
| 用户详情 | GET | `/api/users/{id}` | 查询单个 |
| 创建用户 | POST | `/api/users` | 新增 |
| 更新用户 | PUT | `/api/users/{id}` | 全量更新 |
| 部分更新 | PATCH | `/api/users/{id}` | 部分更新 |
| 删除用户 | DELETE | `/api/users/{id}` | 删除 |

使用名词复数表示资源，HTTP 方法表示动作。

## DTO 与校验

不要直接把实体暴露给前端，用 DTO 隔离：

```java [UserCreateRequest.java]
package com.example.demo.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record UserCreateRequest(
        @NotBlank(message = "姓名不能为空")
        @Size(max = 50, message = "姓名最长 50 个字符")
        String name,

        @NotBlank(message = "邮箱不能为空")
        @Email(message = "邮箱格式不正确")
        String email
) {}
```

常用校验注解：

| 注解 | 作用 |
| --- | --- |
| `@NotBlank` | 字符串不能为 null/空/纯空格 |
| `@NotNull` | 不能为 null |
| `@Size(min,max)` | 长度/集合大小 |
| `@Min` / `@Max` | 数值范围 |
| `@Email` | 邮箱格式 |
| `@Pattern` | 正则校验 |
| `@Positive` | 正数 |

## Controller 写法

```java [UserController.java]
package com.example.demo.controller;

import com.example.demo.dto.UserCreateRequest;
import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public Page<User> page(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return userService.page(page, size);
    }

    @GetMapping("/{id}")
    public User detail(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User create(@Valid @RequestBody UserCreateRequest request) {
        return userService.create(request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

`@Valid` 触发 DTO 校验，校验失败由异常处理器统一返回。

## 分页

Service 层返回 `Page`：

```java
public Page<User> page(int page, int size) {
    return userRepository.findAll(PageRequest.of(page - 1, size, Sort.by("id").descending()));
}
```

响应示例：

```json
{
  "content": [{"id": 2, "name": "李四"}],
  "totalElements": 2,
  "totalPages": 1,
  "number": 0,
  "size": 10
}
```

## 统一响应（可选）

团队可以约定统一包装（如 `{code, message, data}`），但注意这会让 REST 语义变弱；更推荐直接用 HTTP 状态码 + `ProblemDetail` 表达错误（见「异常处理」篇）。两种风格二选一，不要混用。

## 接口文档：springdoc-openapi

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>3.0.0</version>
</dependency>
```

启动后访问：

- Swagger UI：http://localhost:8080/swagger-ui.html
- OpenAPI JSON：http://localhost:8080/v3/api-docs

给接口补充说明：

```java
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "用户管理")
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Operation(summary = "创建用户")
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User create(@Valid @RequestBody UserCreateRequest request) {
        return userService.create(request);
    }
}
```

生产环境注意关闭或鉴权 Swagger UI。

## 易错点

::: danger 常见错误
1. 直接返回 `User` 实体，密码等敏感字段泄露；应使用 DTO。
2. 忘记 `@Valid`，校验注解完全不生效。
3. `@RequestBody` 缺失或 JSON 字段名不匹配，反序列化后全是 null。
4. 更新接口用 PUT 却只更新部分字段，语义混乱；全量用 PUT，部分用 PATCH。
5. 分页 `page` 从 1 开始传，Spring Data 从 0 开始，忘了减 1 导致第一页数据取不到。
6. 生产暴露 Swagger UI 且无鉴权。
:::

## 验证方式

1. `curl http://localhost:8080/api/users?page=1&size=10` 返回分页 JSON。
2. `curl -X POST http://localhost:8080/api/users -H "Content-Type: application/json" -d '{"name":"","email":"bad"}'` 返回 400 和校验错误信息。
3. `curl -X DELETE http://localhost:8080/api/users/1 -i` 返回 204。
4. 打开 `/swagger-ui.html`，能看到接口列表和参数说明。
5. 用 Postman/Apifox 完整走一遍增删改查。

## 参考资料

- REST 规范：https://restfulapi.net/
- Bean Validation：https://jakarta.ee/specifications/bean-validation/
- springdoc-openapi：https://springdoc.org/
- Spring Data 分页：https://docs.spring.io/spring-data/jpa/reference/repositories/core-domain-events.html
