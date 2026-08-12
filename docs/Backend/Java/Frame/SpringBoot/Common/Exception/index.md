# Spring Boot 异常处理

异常处理的目标是：业务错误有明确状态码和可读信息、系统错误不泄露内部细节、校验错误统一格式。本节使用 Spring 6+ 的 `ProblemDetail`（RFC 7807）方案。

::: info 适用版本
本节为 Spring Boot 通用指南（3.x/4.x）。`ProblemDetail` 从 Spring Framework 6 起内置。
:::

## 默认行为

不写任何异常处理器时：

- 未捕获异常返回 500，响应体是 Whitelabel Error Page（或 JSON 错误信息）。
- 参数校验失败返回 400。
- 404 返回标准错误页。

问题：错误信息不统一、内部异常可能泄露堆栈、调用方难以解析。

## 业务异常

先定义一个业务异常基类：

```java [BusinessException.java]
package com.example.demo.exception;

public class BusinessException extends RuntimeException {
    private final int code;

    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }

    public int getCode() {
        return code;
    }
}
```

业务代码抛出：

```java
if (userRepository.existsByEmail(email)) {
    throw new BusinessException(1001, "邮箱已存在");
}
```

## 全局异常处理器

```java [GlobalExceptionHandler.java]
package com.example.demo.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.net.URI;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ProblemDetail handleBusiness(BusinessException ex) {
        ProblemDetail detail = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, ex.getMessage());
        detail.setTitle("业务处理失败");
        detail.setProperty("code", ex.getCode());
        return detail;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail detail = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, "参数校验失败");
        detail.setProperty("errors", ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(e -> e.getField() + ": " + e.getDefaultMessage())
                .toList());
        return detail;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleUnknown(Exception ex) {
        // 记录完整堆栈，但响应只给通用信息
        ProblemDetail detail = ProblemDetail.forStatusAndDetail(
                HttpStatus.INTERNAL_SERVER_ERROR, "服务器内部错误");
        detail.setTitle("系统错误");
        return detail;
    }
}
```

`ProblemDetail` 响应示例：

```json
{
  "type": "about:blank",
  "title": "业务处理失败",
  "status": 400,
  "detail": "邮箱已存在",
  "code": 1001
}
```

## 处理 404 与资源不存在

```java
@ExceptionHandler(NoSuchElementException.class)
public ProblemDetail handleNotFound(NoSuchElementException ex) {
    return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, "资源不存在");
}
```

## 记录日志

异常必须留痕，方便排查：

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleUnknown(Exception ex) {
        log.error("未处理异常", ex);
        return ProblemDetail.forStatusAndDetail(
                HttpStatus.INTERNAL_SERVER_ERROR, "服务器内部错误");
    }
}
```

## 常见异常映射

| 异常 | 建议状态码 |
| --- | --- |
| 参数校验失败 | 400 Bad Request |
| 未登录/凭证失效 | 401 Unauthorized |
| 无权限 | 403 Forbidden |
| 资源不存在 | 404 Not Found |
| 资源冲突（重复创建） | 409 Conflict |
| 业务规则失败 | 400 或 422 Unprocessable Entity |
| 兜底异常 | 500 Internal Server Error |

## 易错点

::: danger 常见错误
1. 兜底处理器直接 `return ex.getMessage()`，把 SQL、堆栈等内部信息暴露给调用方。
2. `@RestControllerAdvice` 与 `@ControllerAdvice` 混淆，返回对象被当成视图。
3. 忘记处理 `MethodArgumentNotValidException`，校验错误还是默认格式。
4. 一个异常被多个 `@ExceptionHandler` 匹配时按最具体优先，子类处理器写错层级会失效。
5. 事务方法内 catch 了异常却没有重抛，异常处理器收不到，事务也不回滚。
6. 每个 Controller 各写一套 try/catch，重复且容易漏。
:::

## 验证方式

1. `curl -X POST /api/users -H "Content-Type: application/json" -d '{"name":"","email":"bad"}'` 返回 400 和字段错误列表。
2. 创建重复邮箱返回 400，`code` 为 1001。
3. 查询不存在的用户返回 404。
4. 故意在 Service 抛 `RuntimeException`，响应 500 且不包含堆栈，控制台有完整日志。
5. 用接口文档/Postman 验证所有错误场景的响应结构一致。

## 参考资料

- RFC 7807 Problem Details：https://www.rfc-editor.org/rfc/rfc7807
- Spring 错误处理：https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html
- Spring Boot 错误处理：https://docs.spring.io/spring-boot/reference/web/servlet.html#web.servlet.spring-mvc.error-handling
