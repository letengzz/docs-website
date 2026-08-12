# 异常处理

在Controller层如果程序出现了异常，并且这个异常未被捕获，SpringBoot 提供的异常处理机制将生效。
SpringBoot 提供异常处理机制主要是为了提高应用的健壮性和用户体验。它的好处包括：

1. 统一错误响应：可以定义全局异常处理器来统一处理各种异常，确保返回给客户端的错误信息格式一致，便于前端解析。
2. 提升用户体验：能够优雅地处理异常情况，避免直接将技术性错误信息暴露给用户，而是显示更加友好的提示信息。
3. 简化代码：开发者不需要在每个可能抛出异常的方法中重复编写异常处理逻辑，减少冗余代码，使业务代码更加清晰简洁。
4. 增强安全性：通过控制异常信息的输出，防止敏感信息泄露，增加系统的安全性。

官方文档：https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-exceptionhandler.html

## 默认错误处理

默认情况下，Spring Boot提供`/error`处理所有错误的映射

对于机器客户端，它将生成JSON响应，其中包含错误，HTTP状态和异常消息的详细信息。对于浏览器客户端，响应一个"whitelabel"错误视图，以HTML格式呈现相同的数据

![image-20230223110956415](assets/202307312050534.png)

![image-20230223110751895](assets/202307312050313.png)

**错误处理的自动配置**都在`ErrorMvcAutoConfiguration`中，两大核心机制：

1. SpringBoot 会**自适应**处理错误**，**响应页面或JSON数据

2. **SpringMVC的错误处理机制**依然保留，**MVC处理不了**，才会**交给boot进行处理**

![img](assets/202307312059215.png)

发生错误以后，转发给/error路径，SpringBoot在底层写好一个 BasicErrorController的组件，专门处理这个请求：

```java
	@RequestMapping(produces = MediaType.TEXT_HTML_VALUE) //返回HTML
	public ModelAndView errorHtml(HttpServletRequest request, HttpServletResponse response) {
		HttpStatus status = getStatus(request);
		Map<String, Object> model = Collections
			.unmodifiableMap(getErrorAttributes(request, getErrorAttributeOptions(request, MediaType.TEXT_HTML)));
		response.setStatus(status.value());
		ModelAndView modelAndView = resolveErrorView(request, response, status, model);
		return (modelAndView != null) ? modelAndView : new ModelAndView("error", model);
	}

	@RequestMapping  //返回 ResponseEntity, JSON
	public ResponseEntity<Map<String, Object>> error(HttpServletRequest request) {
		HttpStatus status = getStatus(request);
		if (status == HttpStatus.NO_CONTENT) {
			return new ResponseEntity<>(status);
		}
		Map<String, Object> body = getErrorAttributes(request, getErrorAttributeOptions(request, MediaType.ALL));
		return new ResponseEntity<>(body, status);
	}
```

错误页面是这么解析到的：

```java
//1、解析错误的自定义视图地址
ModelAndView modelAndView = resolveErrorView(request, response, status, model);
//2、如果解析不到错误页面的地址，默认的错误页就是 error
return (modelAndView != null) ? modelAndView : new ModelAndView("error", model);
```

容器中专门有一个错误视图解析器：

```java
@Bean
@ConditionalOnBean(DispatcherServlet.class)
@ConditionalOnMissingBean(ErrorViewResolver.class)
DefaultErrorViewResolver conventionErrorViewResolver() {
    return new DefaultErrorViewResolver(this.applicationContext, this.resources);
}
```

SpringBoot解析自定义错误页的默认规则：

```java
	@Override
	public ModelAndView resolveErrorView(HttpServletRequest request, HttpStatus status, Map<String, Object> model) {
		ModelAndView modelAndView = resolve(String.valueOf(status.value()), model);
		if (modelAndView == null && SERIES_VIEWS.containsKey(status.series())) {
			modelAndView = resolve(SERIES_VIEWS.get(status.series()), model);
		}
		return modelAndView;
	}

	private ModelAndView resolve(String viewName, Map<String, Object> model) {
		String errorViewName = "error/" + viewName;
		TemplateAvailabilityProvider provider = this.templateAvailabilityProviders.getProvider(errorViewName,
				this.applicationContext);
		if (provider != null) {
			return new ModelAndView(errorViewName, model);
		}
		return resolveResource(errorViewName, model);
	}

	private ModelAndView resolveResource(String viewName, Map<String, Object> model) {
		for (String location : this.resources.getStaticLocations()) {
			try {
				Resource resource = this.applicationContext.getResource(location);
				resource = resource.createRelative(viewName + ".html");
				if (resource.exists()) {
					return new ModelAndView(new HtmlResourceView(resource), model);
				}
			}
			catch (Exception ex) {
			}
		}
		return null;
	}
```

容器中有一个默认的名为 error 的 view； 提供了默认白页功能：

```java
@Bean(name = "error")
@ConditionalOnMissingBean(name = "error")
public View defaultErrorView() {
    return this.defaultErrorView;
}
```

封装了JSON格式的错误信息：

```java
	@Bean
	@ConditionalOnMissingBean(value = ErrorAttributes.class, search = SearchStrategy.CURRENT)
	public DefaultErrorAttributes errorAttributes() {
		return new DefaultErrorAttributes();
	}
```

规则：**解析一个错误页**

1. 如果发生了500、404、503、403 这些错误

   1. 如果有**模板引擎**，默认在 `classpath:/templates/error/精确码.html`
   1. 如果没有模板引擎，在静态资源文件夹下找 `精确码.html`

1. 如果匹配不到`精确码.html`这些精确的错误页，就去找`5xx.html`，`4xx.html`**模糊匹配**
   1. 如果有模板引擎，默认在 `classpath:/templates/error/5xx.html`
   1. 如果没有模板引擎，在静态资源文件夹下找 `5xx.html`
   1. 如果模板引擎路径`templates`下有 `error.html`页面，就直接渲染

## 错误处理方案

如果SpringMVC没有对应的处理方案，会开启SpringBoot默认的错误处理方案。**如果使用了SpringMVC的错误处理方案，SpringBoot的错误处理方案不生效**。

### SpringMVC的错误处理方案

#### 局部控制

控制器当中编写一个方法，方法使用@ExceptionHandler注解进行标注，凡是这个控制器当中出现了对应的异常，则走这个方法来进行异常的处理。局部生效。

```java
@RestController
public class UserController {

    @GetMapping("/resource/{id}")
    public String getResource(@PathVariable Long id){
        if(id == 1){
            throw new IllegalArgumentException("无效ID：" + id);
        }
        return "ID = " + id;
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public String handler(IllegalArgumentException e){
        return "错误信息：" + e.getMessage();
    }
}
```

再编写一个OtherController，让它也发生IllegalArgumentException异常，通过测试，确实局部生效。

```java
@RestController
public class OtherController {
    @GetMapping("/resource2/{id}")
    public String getResource(@PathVariable Long id){
        if(id == 1){
            throw new IllegalArgumentException("无效ID：" + id);
        }
        return "ID = " + id;
    }
}
```

#### 全局控制

使用`@ControllerAdvice` + `@ExceptionHandler` 进行统一异常处理，凡是任何控制器当中出现了对应的异常，则走这个方法来进行异常的处理，全局生效。

- `@ControllerAdvice`：用于声明处理全局Controller方法异常的类。
- `@ExceptionHandler`：用于声明处理异常的方法，`value`属性用于声明该方法处理的异常类型。
- `@ResponseBody`：表示将方法的返回值作为HTTP的响应体。

不使用模板：

```java
// @ControllerAdvice
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(IllegalArgumentException.class)
    // @ResponseBody
    public String handler(IllegalArgumentException e){
        return "错误信息：" + e.getMessage();
    }
}
```

使用模板：

```java
@ControllerAdvice
public class ErrorController {

    @ExceptionHandler(Exception.class)
    public String error(Exception e, Model model){  //可以直接添加形参来获取异常
        e.printStackTrace();
        model.addAttribute("e", e);
        return "error";
    }
}
```

```html [templates/error.html]
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Title</title>
  </head>
  <body>
    500 - 服务器出现了一个内部错误QAQ
    <div th:text="${e}"></div>
  </body>
</html>
```

添加异常：

```java
@RequestMapping("/index")
public String index(){
    System.out.println("我是处理！");
    if(true) throw new RuntimeException("您的氪金力度不足，无法访问！");
    return "index";
}
```

访问后，发现控制台会输出异常信息，同时页面也是自定义的一个页面。

![image-20230919130750542](assets/202309191308819.png)

### SpringBoot默认错误处理方案

根据boot的错误页面规则，要对其进行自定义页面模板。

**SpringBoot默认的错误处理方案**：

- 如果客户端要的是json，则直接响应json格式的错误信息。
- 如果客户端要的是html页面，则按照下面方案：
  1. 精确错误码文件：去classpath:/templates/error/目录下找404.html500.html等精确错误码.html文件。如果找不到，则去静态资源目录下的/error目录下找。如果还是找不到，才会进入下一步。
  2. 模糊错误码文件：去classpath:/templates/error/目录下找4xx.html5xx.html等模糊错误码.html文件。如果找不到，则去静态资源目录下的/error目录下找。如果还是找不到，才会进入下一步。
  3. 通用错误页面：去找classpath:/templates/error.html如果找不到则进入下一步。
  4. 默认错误处理：如果上述所有步骤都未能找到合适的错误页面，Spring Boot 会使用内置的默认错误处理机制，即 /error 端点。

可以在error/下增加4xx，5xx页面，error/下的4xx，5xx页面会被自动解析。

解析顺序如果发生404错误，先找 404.html，找不到则查找4xx.html，如果都没有找到，就触发白页

![image-20230223112150202](assets/img202403231846413.png)

## 在错误页获取错误信息

Spring Boot 默认会在模型Model中放置以下信息：

- timestamp: 错误发生的时间戳
- status: HTTP 状态码
- error: 错误类型（如 "Not Found"）
- exception: 异常类名
- message: 错误消息
- trace: 堆栈跟踪

在thymeleaf中使用 `${message}`即可取出信息。

:::danger 注意

springboot3.3.5版本默认只向Model对象中绑定了`timestamp`、`status`、`error`。如果要保存`exception`、`message`、`trace`，需要开启以下三个配置：

```properties
server.error.include-stacktrace=always
server.error.include-exception=true
server.error.include-message=always
```

:::

## 前后端分离项目的错误处理方案

统一使用SpringMVC的错误处理方案，定义全局的异常处理机制：`@ControllerAdvice` + `@ExceptionHandler`

返回json格式的错误信息，其它的就不需要管了，因为前端接收到错误信息怎么处理是他自己的事儿。

## 服务器端负责页面渲染的项目错误处理方案

建议使用SpringBoot的错误处理方案：

1. 如果发生的异常是HTTP错误状态码：

   - 建议常见的错误码给定精确错误码.html

   - 建议不常见的错误码给定模糊错误码.html

2. 如果发生的异常不是HTTP错误状态码，而是业务相关异常：
   - 在程序中处理具体的业务异常，自己通过程序来决定跳转到哪个错误页面。
3. 建议提供`classpath:/templates/error.html`来处理通用错误。
