# 默认效果

**默认配置**：

1. 包含了 ContentNegotiatingViewResolver 和 BeanNameViewResolver 组件，**方便视图解析**

   - ContentNegotiatingViewResolver 自动根据HTTP请求头中Accept字段来选择合适的视图技术渲染响应。
   - BeanNameViewResolver 的作用是根据视图名称找到视图View对象。

2. **默认的静态资源处理机制**： 静态资源放在 static 文件夹下即可直接访问
3. **自动注册**了 `Converter`，`GenericConverter`，`Formatter`组件，适配常见**数据类型转换**和**格式化需求**
   - Converter：转换器，做类型转换的，例如表单提交了用户数据，将表单数据转换成User对象。
   - Formatter：格式化器，做数据格式化的，例如将Java中的日期类型对象格式化为特定格式的日期字符串。或者将用户提交的日期字符串，转换为Java中的日期对象。
4. **支持** **HttpMessageConverters**，可以**方便返回JSON等数据类型**：内置了很多的HTTP消息转换器。例如：MappingJackson2HttpMessageConverter可以将json转换成java对象，也可以将java对象转换为json字符串。
5. **注册** MessageCodesResolver，方便**国际化**及错误消息处理：SpringBoot会自动注册一个默认的**消息代码解析器**。帮助你在表单验证出错时生成一些特殊的代码。这些代码让你能够更精确地定位问题，并提供更友好的错误提示。
6. **支持 静态** index.html：Spring Boot 会自动处理位于项目静态资源目录下的 index.html 文件，使其成为应用程序的默认主页
7. **自动使用**ConfigurableWebBindingInitializer，实现**消息处理、数据绑定、类型转化、数据校验**等功能：指定默认使用哪个转换器，默认使用哪个格式化器。

:::warning 说明

- 如果想保持boot mvc 的默认配置，并且自定义更多的 mvc 配置，如：interceptors，formatters，view controllers 等。可以使用`@Configuration`注解添加一个 WebMvcConfigurer 类型的配置类，并不要标注 `@EnableWebMvc`
- 如果想保持 boot mvc 的默认配置，但要自定义核心组件实例，比如：RequestMappingHandlerMapping，RequestMappingHandlerAdapter 或 ExceptionHandlerExceptionResolver，给容器中放一个WebMvcRegistrations 组件即可
- 如果想全面接管 Spring MVC，`@Configuration` 标注一个配置类，并加上 `@EnableWebMvc`注解，实现 WebMvcConfigurer 接口

![image-20230801152505058](assets/202308011526218.png)

:::

**推荐方式**：给容器中写一个配置类`@Configuration`实现 `WebMvcConfigurer`但是不要标注 `@EnableWebMvc`注解，实现手自一体的效果。
