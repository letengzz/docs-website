# 全面接管SpringMVC

SpringBoot 默认配置好了 SpringMVC 的所有常用特性。

如果需要全面接管SpringMVC的所有配置并禁用默认配置，仅需要编写一个WebMvcConfigurer配置类，并标注 `@EnableWebMvc` 即可

**全手动模式**：

- @EnableWebMvc : 禁用默认配置
- WebMvcConfigurer组件：定义MVC的底层行为

## WebMvcAutoConfiguration 自动配置规则

SpringMVC自动配置场景配置了如下所有默认行为：**WebMvcAutoConfigurationweb场景的自动配置类**

1. 支持RESTful的filter：HiddenHttpMethodFilter
2. 支持非POST请求，请求体携带数据：FormContentFilter
3. 导入EnableWebMvcConfiguration：
   1. RequestMappingHandlerAdapter
   2. WelcomePageHandlerMapping： 欢迎页功能支持（模板引擎目录、静态资源目录放index.html），项目访问/ 就默认展示这个页面.
   3. RequestMappingHandlerMapping：找每个请求由谁处理的映射关系
   4. ExceptionHandlerExceptionResolver：默认的异常解析器 
   5. LocaleResolver：国际化解析器
   6. ThemeResolver：主题解析器
   7. FlashMapManager：临时数据共享
   8. FormattingConversionService： 数据格式化 、类型转化
   9. Validator： 数据校验JSR303提供的数据校验功能
   10. WebBindingInitializer：请求参数的封装与绑定
   11. ContentNegotiationManager：内容协商管理器
4. WebMvcAutoConfigurationAdapter配置生效，它是一个WebMvcConfigurer，定义mvc底层组件
   1. 定义好 WebMvcConfigurer 底层组件默认功能
   2. 视图解析器：InternalResourceViewResolver
   3. 视图解析器：BeanNameViewResolver,视图名（controller方法的返回值字符串）就是组件名
   4. 内容协商解析器：ContentNegotiatingViewResolver
   5. 请求上下文过滤器：RequestContextFilter: 任意位置直接获取当前请求
   6. 静态资源链规则
   7. ProblemDetailsExceptionHandler：错误详情，SpringMVC内部场景异常被它捕获
5. 定义了MVC默认的底层行为: WebMvcConfigurer

## @EnableWebMvc 禁用默认行为

`@EnableWebMVC` 禁用了 Mvc的自动配置、WebMvcConfigurer 定义SpringMVC底层组件的功能类

1. @EnableWebMvc给容器中导入 DelegatingWebMvcConfiguration组件，是 WebMvcConfigurationSupport
2. WebMvcAutoConfiguration有一个核心的条件注解，@ConditionalOnMissingBean(WebMvcConfigurationSupport.class)，容器中没有WebMvcConfigurationSupport，WebMvcAutoConfiguration才生效
3. @EnableWebMvc 导入 WebMvcConfigurationSupport 导致 WebMvcAutoConfiguration 失效。导致禁用了默认行为

## WebMvcConfigurer 功能

定义扩展SpringMVC底层功能。

| 提供方法                           | 核心参数                                | 功能                                                         | 默认                                                         |
| ---------------------------------- | --------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| addFormatters                      | FormatterRegistry                       | 格式化器：支持属性上@NumberFormat和@DatetimeFormat的数据类型转换 | GenericConversionService                                     |
| getValidator                       | 无                                      | 数据校验：校验 Controller 上使用@Valid标注的参数合法性。需要导入starter-validator | 无                                                           |
| addInterceptors                    | InterceptorRegistry                     | 拦截器：拦截收到的所有请求                                   | 无                                                           |
| configureContentNegotiation        | ContentNegotiationConfigurer            | 内容协商：支持多种数据格式返回。需要配合支持这种类型的HttpMessageConverter | 支持 json                                                    |
| configureMessageConverters         | `List<HttpMessageConverter<?>>`         | 消息转换器：标注@ResponseBody的返回值会利用MessageConverter直接写出去 | 8 个，支持byte，string,multipart,resource，json              |
| addViewControllers                 | ViewControllerRegistry                  | 视图映射：直接将请求路径与物理视图映射。用于无 java 业务逻辑的直接视图页渲染 | 无 `<mvc:view-controller>`                                   |
| configureViewResolvers             | ViewResolverRegistry                    | 视图解析器：逻辑视图转为物理视图                             | ViewResolverComposite                                        |
| addResourceHandlers                | ResourceHandlerRegistry                 | 静态资源处理：静态资源路径映射、缓存控制                     | ResourceHandlerRegistry                                      |
| configureDefaultServletHandling    | DefaultServletHandlerConfigurer         | 默认 Servlet：可以覆盖 Tomcat 的DefaultServlet。让DispatcherServlet拦截/ | 无                                                           |
| configurePathMatch                 | PathMatchConfigurer                     | 路径匹配：自定义 URL 路径匹配。可以自动为所有路径加上指定前缀，比如 /api | 无                                                           |
| configureAsyncSupport              | AsyncSupportConfigurer                  | 异步支持                                                     | TaskExecutionAutoConfiguration                               |
| addCorsMappings                    | CorsRegistry                            | 跨域                                                         | 无                                                           |
| addArgumentResolvers               | `List<HandlerMethodArgumentResolver>`   | 参数解析器                                                   | mvc 默认提供                                                 |
| addReturnValueHandlers             | `List<HandlerMethodReturnValueHandler>` | 返回值解析器                                                 | mvc 默认提供                                                 |
| configureHandlerExceptionResolvers | `List<HandlerExceptionResolver>`        | 异常处理器                                                   | 默认 3 个 ExceptionHandlerExceptionResolver ResponseStatusExceptionResolver DefaultHandlerExceptionResolver |
| getMessageCodesResolver            | 无                                      | 消息码解析器：国际化使用                                     | 无                                                           |
