# Spring MVC

Spring MVC 是 Spring 的 **Web 层框架**：基于 MVC（Model-View-Controller）模式，把请求处理拆分为控制器（Controller）、模型（Model）与视图（View），并内置了路由、参数绑定、校验、拦截器、异常处理等能力。它是 Spring Boot Web 应用（`spring-boot-starter-web`）的底层实现。

## 核心概念

| 概念 | 职责 |
| --- | --- |
| DispatcherServlet | 前端控制器，统一接收请求并分发 |
| HandlerMapping | 根据 URL 找到对应的 Controller 方法 |
| HandlerAdapter | 适配并执行 Controller 方法 |
| Controller | 业务入口，返回 ModelAndView / JSON |
| ViewResolver | 根据视图名解析模板 |
| Interceptor | 请求前/后拦截（如登录校验） |
| @ControllerAdvice | 全局异常处理 |

## 一次请求的完整流程

```text
请求 → DispatcherServlet
  → HandlerMapping 找到处理方法
  → Interceptor preHandle（鉴权等）
  → HandlerAdapter 调用 Controller
  → 返回 ModelAndView / @ResponseBody JSON
  → Interceptor postHandle / afterCompletion
  → ViewResolver 渲染视图
```

## 快速示例

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    @GetMapping("/{id}")
    public Order getOrder(@PathVariable Long id) {
        return orderService.findById(id);
    }
}
```

## 常用注解

| 注解 | 用途 |
| --- | --- |
| `@RestController` / `@Controller` | 声明控制器 |
| `@RequestMapping` / `@GetMapping` 等 | 路由映射 |
| `@RequestParam` / `@PathVariable` | 参数绑定 |
| `@RequestBody` / `@ResponseBody` | JSON 序列化 |
| `@Valid` + `@Validated` | 参数校验 |
| `@ExceptionHandler` | 局部异常处理 |
| `@ControllerAdvice` | 全局异常处理 |

## 与设计模式的联系

Spring MVC 大量使用设计模式：

- **前端控制器（DispatcherServlet）**：统一请求入口。
- **适配器（HandlerAdapter）**：适配不同风格的 Controller。
- **责任链（Interceptor）**：请求拦截链。
- **策略（HandlerMapping/ViewResolver）**：可替换的路由与视图解析策略。
- **模板方法**：框架回调骨架（如 `WebMvcConfigurer`）。

设计模式系统性讲解见 [设计模式专题](../../../DesignPatterns/index.md) 与 [框架中的应用](../../../DesignPatterns/FrameworkUsage/index.md)。

## 常见问题

1. **404 排查**：URL 与 `@RequestMapping` 不匹配、静态资源路径、`@PathVariable` 参数缺失。
2. **JSON 循环引用**：实体双向关联序列化死循环，用 `@JsonIgnoreProperties` 或 DTO。
3. **参数校验不生效**：类上加 `@Validated`，方法参数加 `@Valid`。
4. **拦截器不生效**：确认注册到 `WebMvcConfigurer.addInterceptors` 且路径匹配。
5. **异步请求**：`DeferredResult` / `@Async` 配合超时与异常处理。

::: danger 易错点
1. Controller 里写业务逻辑：Controller 只做编排，业务放 Service。
2. 返回实体直接暴露数据库结构：用 DTO 隔离。
3. 全局异常处理缺失：未捕获异常返回 500 默认页，不利于排障。
4. 拦截器顺序与排除路径混乱：明确登录/白名单路径。
:::

## 验证方式

1. 启动 Spring Boot Web 应用，`GET /api/orders/1` 返回 JSON。
2. 访问不存在的 URL，确认返回 404 与统一错误结构。
3. 给接口加拦截器，验证未带 Token 的请求被拦截。

## 参考资料

- Spring MVC 文档：https://docs.spring.io/spring-framework/reference/web.html
- Spring Boot Web：https://docs.spring.io/spring-boot/reference/web/index.html
- 设计模式在 Spring 中的应用：https://docs.spring.io/spring-framework/reference/core/aop.html
