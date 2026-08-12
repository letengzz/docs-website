# Web新特性

## Problemdetails

RFC 7807: https://www.rfc-editor.org/rfc/rfc7807

**错误信息**返回新格式

**原理**：

```java
@Configuration(proxyBeanMethods = false)
//配置过一个属性 spring.mvc.problemdetails.enabled=true
@ConditionalOnProperty(prefix = "spring.mvc.problemdetails", name = "enabled", havingValue = "true")
static class ProblemDetailsErrorHandlingConfiguration {

    @Bean
    @ConditionalOnMissingBean(ResponseEntityExceptionHandler.class)
    ProblemDetailsExceptionHandler problemDetailsExceptionHandler() {
        return new ProblemDetailsExceptionHandler();
    }

}
```

1. `ProblemDetailsExceptionHandler `是一个 `@ControllerAdvice`**集中处理系统异常**
2. 处理以下异常。如果系统出现以下异常，会被SpringBoot支持以 `RFC 7807`规范方式返回错误数据

```java
@ExceptionHandler({
    //请求方式不支持
	HttpRequestMethodNotSupportedException.class, 
    //媒体类型不支持
	HttpMediaTypeNotSupportedException.class,
	HttpMediaTypeNotAcceptableException.class,
	MissingPathVariableException.class,
	MissingServletRequestParameterException.class,
	MissingServletRequestPartException.class,
	ServletRequestBindingException.class,
	MethodArgumentNotValidException.class,
	NoHandlerFoundException.class,
	AsyncRequestTimeoutException.class,
	ErrorResponseException.class,
	ConversionNotSupportedException.class,
	TypeMismatchException.class,
	HttpMessageNotReadableException.class,
	HttpMessageNotWritableException.class,
	BindException.class
})
```

**例**：

1. problemdetails 默认是关闭的

   ```properties
   # problemdetails 默认是关闭的
   spring.mvc.problemdetails.enabled=false
   ```

2. 默认响应错误的json。状态码 405：

   > {
   >  "timestamp": "2023-04-18T11:13:05.515+00:00",
   >  "status": 405,
   >  "error": "Method Not Allowed",
   >  "trace": "org.springframework.web.HttpRequestMethodNotSupportedException: Request method 'POST' is not supported\r\n\tat org.springframework.web.servlet.mvc.method.RequestMappingInfoHandlerMapping.handleNoMatch(RequestMappingInfoHandlerMapping.java:265)\r\n\tat org.springframework.web.servlet.handler.AbstractHandlerMethodMapping.lookupHandlerMethod(AbstractHandlerMethodMapping.java:441)\r\n\tat org.springframework.web.servlet.handler.AbstractHandlerMethodMapping.getHandlerInternal(AbstractHandlerMethodMapping.java:382)\r\n\tat org.springframework.web.servlet.mvc.method.RequestMappingInfoHandlerMapping.getHandlerInternal(RequestMappingInfoHandlerMapping.java:126)\r\n\tat org.springframework.web.servlet.mvc.method.RequestMappingInfoHandlerMapping.getHandlerInternal(RequestMappingInfoHandlerMapping.java:68)\r\n\tat org.springframework.web.servlet.handler.AbstractHandlerMapping.getHandler(AbstractHandlerMapping.java:505)\r\n\tat org.springframework.web.servlet.DispatcherServlet.getHandler(DispatcherServlet.java:1275)\r\n\tat org.springframework.web.servlet.DispatcherServlet.doDispatch(DispatcherServlet.java:1057)\r\n\tat org.springframework.web.servlet.DispatcherServlet.doService(DispatcherServlet.java:974)\r\n\tat org.springframework.web.servlet.FrameworkServlet.processRequest(FrameworkServlet.java:1011)\r\n\tat org.springframework.web.servlet.FrameworkServlet.doPost(FrameworkServlet.java:914)\r\n\tat jakarta.servlet.http.HttpServlet.service(HttpServlet.java:563)\r\n\tat org.springframework.web.servlet.FrameworkServlet.service(FrameworkServlet.java:885)\r\n\tat jakarta.servlet.http.HttpServlet.service(HttpServlet.java:631)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:205)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:149)\r\n\tat org.apache.tomcat.websocket.server.WsFilter.doFilter(WsFilter.java:53)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:174)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:149)\r\n\tat org.springframework.web.filter.RequestContextFilter.doFilterInternal(RequestContextFilter.java:100)\r\n\tat org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:116)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:174)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:149)\r\n\tat org.springframework.web.filter.FormContentFilter.doFilterInternal(FormContentFilter.java:93)\r\n\tat org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:116)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:174)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:149)\r\n\tat org.springframework.web.filter.CharacterEncodingFilter.doFilterInternal(CharacterEncodingFilter.java:201)\r\n\tat org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:116)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:174)\r\n\tat org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:149)\r\n\tat org.apache.catalina.core.StandardWrapperValve.invoke(StandardWrapperValve.java:166)\r\n\tat org.apache.catalina.core.StandardContextValve.invoke(StandardContextValve.java:90)\r\n\tat org.apache.catalina.authenticator.AuthenticatorBase.invoke(AuthenticatorBase.java:493)\r\n\tat org.apache.catalina.core.StandardHostValve.invoke(StandardHostValve.java:115)\r\n\tat org.apache.catalina.valves.ErrorReportValve.invoke(ErrorReportValve.java:93)\r\n\tat org.apache.catalina.core.StandardEngineValve.invoke(StandardEngineValve.java:74)\r\n\tat org.apache.catalina.connector.CoyoteAdapter.service(CoyoteAdapter.java:341)\r\n\tat org.apache.coyote.http11.Http11Processor.service(Http11Processor.java:390)\r\n\tat org.apache.coyote.AbstractProcessorLight.process(AbstractProcessorLight.java:63)\r\n\tat org.apache.coyote.AbstractProtocol$ConnectionHandler.process(AbstractProtocol.java:894)\r\n\tat org.apache.tomcat.util.net.NioEndpoint$SocketProcessor.doRun(NioEndpoint.java:1741)\r\n\tat org.apache.tomcat.util.net.SocketProcessorBase.run(SocketProcessorBase.java:52)\r\n\tat org.apache.tomcat.util.threads.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1191)\r\n\tat org.apache.tomcat.util.threads.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:659)\r\n\tat org.apache.tomcat.util.threads.TaskThread$WrappingRunnable.run(TaskThread.java:61)\r\n\tat java.base/java.lang.Thread.run(Thread.java:833)\r\n",
   >  "message": "Method 'POST' is not supported.",
   >  "path": "/list"
   > }

3. 开启ProblemDetails返回, 使用新的MediaType：

   ```properties
   spring.mvc.problemdetails.enabled=true
   ```

   ```yaml
   spring:
     mvc:
       problemdetails:
         enabled: true
   ```

4. 新的错误返回格式：

   使用新的类型：`Content-Type: application/problem+json`+ 额外扩展返回

   ```json
   {
       "type": "about:blank",
       "title": "Method Not Allowed",
       "status": 405,
       "detail": "Method 'POST' is not supported.",
       "instance": "/list"
   }
   ```

## 函数式Web

`SpringMVC 5.2` 以后 允许使用**函数式**的方式(函数式接口)，**定义Web的请求处理流程**。

**Web请求处理的方式**：

1. `@Controller` + `@RequestMapping`：**耦合式** （**路由**、**业务**耦合）
2. **函数式Web**：分离式（路由、业务分离）

**函数式核心类**：

- **RouterFunction**：定义路由信息。发送什么请求，谁来处理
- **RequestPredicate**：定义请求：请求谓语。请求方式(GET、POST)、请求参数
- **ServerRequest**：封装请求完整数据
- **ServerResponse**：封装响应完整数据

**例**：

1. **场景**：User RESTful - CRUD

   - GET /user/1  获取1号用户

   - GET /users   获取所有用户

   - POST /user  **请求体**携带JSON，新增一个用户

   - PUT /user/1 **请求体**携带JSON，修改1号用户

   - DELETE /user/1 **删除**1号用户 

2. 容器中放入一个Bean：类型是`RouterFunction<ServerResponse>`：

   ```java
   import org.springframework.context.annotation.Bean;
   import org.springframework.context.annotation.Configuration;
   import org.springframework.http.MediaType;
   import org.springframework.web.servlet.function.RequestPredicate;
   import org.springframework.web.servlet.function.RouterFunction;
   import org.springframework.web.servlet.function.ServerResponse;
   
   import static org.springframework.web.servlet.function.RequestPredicates.accept;
   import static org.springframework.web.servlet.function.RouterFunctions.route;
   
   @Configuration(proxyBeanMethods = false)
   public class MyRoutingConfiguration {
   
       private static final RequestPredicate ACCEPT_JSON = accept(MediaType.APPLICATION_JSON);
   
       @Bean
       public RouterFunction<ServerResponse> routerFunction(MyUserHandler userHandler) {
           //链式调用
           return Rouroute()  //开始定义路由信息
                   .GET("/user/{id}", ACCEPT_JSON, userHandler::getUser)
                   .GET("/{user}/customers", ACCEPT_JSON, userHandler::getUserCustomers)
                   .DELETE("/{user}", ACCEPT_JSON, userHandler::deleteUser)
                   .build();
       }
   
   }
   ```

3. 给每个业务定义一个自己的Handler：

   ```java
   import org.springframework.stereotype.Component;
   import org.springframework.web.servlet.function.ServerRequest;
   import org.springframework.web.servlet.function.ServerResponse;
   /**
   * 专门处理User有关的业务
   */
   @Component
   public class MyUserHandler {
   
       public ServerResponse getUser(ServerRequest request) {
           ...
           return ServerResponse.ok().build();
       }
   
       public ServerResponse getUserCustomers(ServerRequest request) {
           ...
           return ServerResponse.ok().build();
       }
   
       public ServerResponse deleteUser(ServerRequest request) {
           ...
           return ServerResponse.ok().build();
       }
   
   }
   ```

