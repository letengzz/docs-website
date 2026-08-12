# WebMvcAutoConfiguration原理

SpringBoot启动默认加载 xxxAutoConfiguration 类（自动配置类）

SpringMVC功能的自动配置类 WebMvcAutoConfiguration生效。

## 生效条件

- `@AutoConfiguration(after = { DispatcherServletAutoConfiguration.class, TaskExecutionAutoConfiguration.class,ValidationAutoConfiguration.class })`：WebMvcAutoConfiguration**自动配置类加载顺序在以上自动配置类加载后加载**。

- `@ConditionalOnWebApplication(type = Type.SERVLET)`：**WebMvcAutoConfiguration自动配置类**只在servlet环境中生效。

- `@ConditionalOnClass({ Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class })`：类路径中必须存在Servlet.classDispatcherServlet.classWebMvcConfigurer.class，**WebMvcAutoConfiguration自动配置类才会生效**。

- `@ConditionalOnMissingBean(WebMvcConfigurationSupport.class)`：类路径中不存在WebMvcConfigurationSupport.class时WebMvcAutoConfiguration自动配置类才会生效。

  :::danger 注意

  当使用`@EnableWebMvc`注解后，类路径中就会注册一个WebMvcConfigurationSupport这样的bean。

  :::

- `@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE + 10)` 不重要：指定WebMvcAutoConfiguration自动配置类的加载顺序

- `@ImportRuntimeHints(WebResourcesRuntimeHints.class)` 不重要：运行时引入WebResourcesRuntimeHints这个类，这个类的作用是给JVM或者其他组件提示信息的，提示一下系统应该如何处理类和资源。

总结来说，WebMvcAutoConfiguration类将在以下条件下生效：

1. 应用程序是一个Servlet类型的Web应用；
2. 环境中有Servlet、DispatcherServlet和WebMvcConfigurer类；
3. 容器中没有WebMvcConfigurationSupport的bean。

如果这些条件都满足的话，那么这个自动配置类就会被激活，并进行相应的自动配置工作。

```java
@AutoConfiguration(after = { DispatcherServletAutoConfiguration.class, TaskExecutionAutoConfiguration.class,ValidationAutoConfiguration.class }) //在这些自动配置之后
@ConditionalOnWebApplication(type = Type.SERVLET) //如果是web应用就生效，类型：SERVLET
@ConditionalOnClass({ Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class })
@ConditionalOnMissingBean(WebMvcConfigurationSupport.class) //容器中没有这个Bean，才生效。默认就是没有
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE + 10)//优先级
@ImportRuntimeHints(WebResourcesRuntimeHints.class)
public class WebMvcAutoConfiguration {
}
```

## 效果

1. 放了两个Filter：

   1. `HiddenHttpMethodFilter`：页面表单提交Rest请求(GET、POST、PUT、DELETE)

      ```java
      @Bean
      @ConditionalOnMissingBean(HiddenHttpMethodFilter.class)
      @ConditionalOnProperty(prefix = "spring.mvc.hiddenmethod.filter", name = "enabled")
      public OrderedHiddenHttpMethodFilter hiddenHttpMethodFilter() {
          return new OrderedHiddenHttpMethodFilter();
      }
      ```

   1. `FormContentFilter`： 表单内容Filter，GET(数据放URL后面)、POST(数据放请求体)请求可以携带数据，PUT、DELETE 的请求体数据会被忽略

      OrderedFormContentFilter 是 Spring Boot 中用于处理 HTTP 请求的一个过滤器，特别是针对 PUT 和 DELETE 请求。这个过滤器的主要作用是在处理 PUT 和 DELETE 请求时，确保如果请求体中有表单格式的数据，这些数据会被正确解析并可用。

      ```java
      @Bean
      @ConditionalOnMissingBean(FormContentFilter.class)
      @ConditionalOnProperty(prefix = "spring.mvc.formcontent.filter", name = "enabled", matchIfMissing = true)
      public OrderedFormContentFilter formContentFilter() {
          return new OrderedFormContentFilter();
      }
      ```

1. 给容器中放了`WebMvcConfigurer`组件：给SpringMVC添加各种定制功能

   ```java
   @Configuration(proxyBeanMethods = false)
   @Import(EnableWebMvcConfiguration.class) //额外导入了其他配置
   @EnableConfigurationProperties({ WebMvcProperties.class, WebProperties.class })
   @Order(0)
   public static class WebMvcAutoConfigurationAdapter implements WebMvcConfigurer, ServletContextAware{        //实现了WebMvcConfigurer
   }
   ```

   SpringBoot在这个类WebMvcAutoConfigurationAdapter中进行了一系列的Spring MVC相关配置：

   1. 所有的功能最终会和配置文件进行绑定
   1. WebMvcProperties： `spring.mvc`配置文件
   1. WebProperties： `spring.web`配置文件

   开发中要对Spring MVC的相关配置进行修改，可以编写一个类继承WebMvcAutoConfigurationAdatper，然后重写对应的方法即可。

   因此，通过对WebMvcAutoConfigurationAdapter类中的方法进行重写来修改Web MVC的默认配置

## WebMvcConfigurer接口

这个接口不是SpringBoot框架提供的，是Spring MVC提供的，在Spring框架4.3版本中引入的。这个接口的作用主要是允许开发者通过实现这个接口来定制Spring MVC的行为。
在这个接口中提供了很多方法，需要改变Spring MVC的哪个行为，则重写对应的方法即可，下面是这个接口中所有的方法，以及每个方法对应的Spring MVC行为的解释：

```java
public interface WebMvcConfigurer {
    // 用于定制 Spring MVC 如何匹配请求路径到控制器
    default void configurePathMatch(PathMatchConfigurer configurer) {}
    // 用于定制 Spring MVC 的内容协商策略，以确定如何根据请求的内容类型来选择合适的处理方法或返回数据格式
    default void configureContentNegotiation(ContentNegotiationConfigurer configurer) {}
    // 用于定制 Spring MVC 处理异步请求的方式
    default void configureAsyncSupport(AsyncSupportConfigurer configurer) {}
    // 用于定制是否将某些静态资源请求转发WEB容器默认的Servlet处理
    default void configureDefaultServletHandling(DefaultServletHandlerConfigurer configurer) {}
    // 用于定制 Spring MVC 解析视图的方式，以确定如何将控制器返回的视图名称转换为实际的视图资源。
    default void configureViewResolvers(ViewResolverRegistry registry) {}
    // 用于定制 Spring MVC 如何处理 HTTP 请求和响应的数据格式，包括 JSON、XML 等内容类型的转换
    default void configureMessageConverters(List<HttpMessageConverter<?>> converters) {}
    // 用于定制 Spring MVC 如何处理控制器方法中发生的异常，并提供相应的错误处理逻辑。
    default void configureHandlerExceptionResolvers(List<HandlerExceptionResolver> resolvers) {}

    // 用于定制 Spring MVC 如何处理数据的格式化和解析，例如日期、数值等类型的对象的输入和输出格式。
    default void addFormatters(FormatterRegistry registry) {}
    // 用于定制 Spring MVC 如何使用拦截器来处理请求和响应，包括在请求进入控制器之前和之后执行特定的操作。
    default void addInterceptors(InterceptorRegistry registry) {}
    // 用于定制 Spring MVC 如何处理静态资源（如 CSS、JavaScript、图片等文件）的请求。
    default void addResourceHandlers(ResourceHandlerRegistry registry) {}
    // 用于定制 Spring MVC 如何处理跨域请求，确保应用程序可以正确地响应来自不同域名的 AJAX 请求或其他跨域请求。
    default void addCorsMappings(CorsRegistry registry) {}
    // 用于快速定义简单的 URL 到视图的映射，而无需编写完整的控制器类和方法。
    default void addViewControllers(ViewControllerRegistry registry) {}
    // 用于定制 Spring MVC 如何解析控制器方法中的参数，包括如何从请求中获取并转换参数值。
    default void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {}
    // 用于定制 Spring MVC 如何处理控制器方法的返回值，包括如何将返回值转换为实际的 HTTP 响应。
    default void addReturnValueHandlers(List<HandlerMethodReturnValueHandler> handlers) {}

    // 用于定制 Spring MVC 如何处理 HTTP 请求和响应的数据格式，允许你添加或调整默认的消息转换器，以支持特定的数据格式。
    default void extendMessageConverters(List<HttpMessageConverter<?>> converters) {}
    // 用于定制 Spring MVC 如何处理控制器方法中抛出的异常，允许你添加额外的异常处理逻辑。
    default void extendHandlerExceptionResolvers(List<HandlerExceptionResolver> resolvers) {}
}
```

提供了配置SpringMVC底层的所有组件入口：

![img](assets/202308011535530.png)

## WebMvcAutoConfigurationAdapter

WebMvcConfigurer接口的实现类WebMvcAutoConfigurationAdapter。

WebMvcAutoConfigurationAdapter是Spring Boot框架提供的，实现了Spring MVC中的WebMvcConfigurer接口，对Spring MVC的所有行为进行了默认的配置：

![image.png](assets/img202411252205808.png)

可以看到，该类上有一个注解`@EnableConfigurationProperties({ WebMvcProperties.class, WebProperties.class })`，该注解负责启用配置属性。会将配置文件application.properties或application.yml中的配置传递到该类中。因此可以通过application.properties或application.yml配置文件来改变Spring Boot对SpringMVC的默认配置。WebMvcProperties和WebProperties源码：

![image.png](assets/img202411252205904.png)

![image.png](assets/img202411252205068.png)

通过以上源码得知要改变SpringBoot对SpringMVC的默认配置，需要在配置文件中使用以下前缀的配置：

- spring.mvc：主要用于配置 Spring MVC 的相关行为，例如路径匹配、视图解析、静态资源处理等
- spring.web：通常用于配置一些通用的 Web 层设置，如资源处理、安全性配置等。

## 静态资源规则源码

web站点中的静态资源指的是：js、css、图片等。

WebMvcAutoConfigurationAdapter源码：

```java
@Override
public void addResourceHandlers(ResourceHandlerRegistry registry) {

    // 检查 resourceProperties 中的 addMappings 属性是否为 false。如果为 false，则表示不启用默认的静态资源映射处理。
    // 在application.properties配置文件中进行`spring.web.resources.add-mappings=false`配置，可以将其设置为false。
    // 当然，如果没有配置的话，默认值是true。
    if (!this.resourceProperties.isAddMappings()) {
        logger.debug("Default resource handling disabled");
        return;
    }

    // 配置 WebJars 的静态资源处理。
    // this.mvcProperties.getWebjarsPathPattern()的执行结果是：/webjars/**
    // 也就是说，如果请求路径是 http://localhost:8080/webjars/** ，则自动去类路径下的 /META-INF/resources/webjars/ 目录中找静态资源。
    // 如果要改变这个默认的配置，需要在application.properties文件中进行这样的配置：`spring.mvc.webjars-path-pattern=...`
    addResourceHandler(registry, this.mvcProperties.getWebjarsPathPattern(),
            "classpath:/META-INF/resources/webjars/");

    // 配置普通静态资源处理
    // this.mvcProperties.getStaticPathPattern()的执行结果是：/**
    // this.resourceProperties.getStaticLocations()的执行结果是：{ "classpath:/META-INF/resources/","classpath:/resources/", "classpath:/static/", "classpath:/public/" }
    // 也就是说，如果请求路径是：http://localhost:8080/**，根据控制器方法优先原则，会先去找合适的控制器方法，如果没有合适的控制器方法，静态资源处理才会生效，则自动去类路径下的/META-INF/resources/、/resources/、/static/、/public/ 4个位置找。
    // 如果要改变这个默认的配置，需要在application.properties中进行如下的两个配置：
    // 配置URL：spring.mvc.static-path-pattern=...
    // 配置物理路径：spring.web.resources.static-locations=...,...,...,...
    addResourceHandler(registry, this.mvcProperties.getStaticPathPattern(), (registration) -> {
        registration.addResourceLocations(this.resourceProperties.getStaticLocations());
        if (this.servletContext != null) {
            ServletContextResource resource = new ServletContextResource(this.servletContext, SERVLET_LOCATION);
            registration.addResourceLocations(resource);
        }
    });
}
```

**规则**：

1. 访问： `/webjars/**`路径就去 `classpath:/META-INF/resources/webjars/`下找资源：

   - maven 导入依赖

     官方网站：https://www.webjars.org/

     ```xml
     <dependency>
     	<groupId>org.webjars</groupId>
         <artifactId>jquery</artifactId>
         <version>3.5.1</version>
     </dependency>
     ```

1. 访问： `/**`路径就去 静态资源默认的四个位置找资源：

   1. `classpath:/META-INF/resources/`
   1. `classpath:/resources/`
   1. `classpath:/static/`
   1. `classpath:/public/`

1. **静态资源默认都有缓存规则的设置**：

   1. 所有缓存的设置，直接通过**配置文件**： `spring.web`
   1. cachePeriod： 缓存周期。 默认没有，以s(秒)为单位
   1. cacheControl： **HTTP缓存**控制 ([https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Caching](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Caching#概览))
   1. **useLastModified**：是否使用最后一次修改。配合HTTP Cache规则

如果浏览器访问了一个静态资源 `index.js`，如果服务这个资源没有发生变化，下次访问的时候就可以直接让浏览器用缓存中的东西，而不用给服务器发请求。

```java
registration.setCachePeriod(getSeconds(this.resourceProperties.getCache().getPeriod()));
registration.setCacheControl(this.resourceProperties.getCache().getCachecontrol().toHttpCacheControl());
registration.setUseLastModified(this.resourceProperties.getCache().isUseLastModified());
```

## EnableWebMvcConfiguration 源码

```java
//SpringBoot 给容器中放 WebMvcConfigurationSupport 组件。
//如果自己放了 WebMvcConfigurationSupport 组件，Boot的WebMvcAutoConfiguration都会失效。
@Configuration(proxyBeanMethods = false)
@EnableConfigurationProperties(WebProperties.class)
public static class EnableWebMvcConfiguration extends DelegatingWebMvcConfiguration implements ResourceLoaderAware
{
}
```

`HandlerMapping`： 根据请求路径 ` /a` 找那个handler能处理请求

1. `WelcomePageHandlerMapping`： 访问 `/**`路径下的所有请求，都在以前静态资源路径下找，欢迎页也一样(`classpath:/META-INF/resources/`、`classpath:/resources/`、`classpath:/static/`、`classpath:/public/`)
1. 找`index.html`：只要静态资源的位置有一个 `index.html`页面，项目启动默认访问

源码分析：

在SpringBoot框架的WebMvcAutoConfiguration类中提供了一个内部类：WebMvcAutoConfigurationAdapter

![image.png](assets/img202411252205067.png)

WebMvcAutoConfiguration类的内部类EnableWebMvcConfiguration，这个类继承了DelegatingWebMvcConfiguration（Delegating是委派的意思。）

![image.png](assets/img202411252206195.png)

DelegatingWebMvcConfiguration中的setConfigurers()方法用来设置配置。而配置参数是一个List集合，这个List集合中存放的是WebMvcConfigurer接口的实例，并且可以看到这个方法上面使用了@Autowired进行了自动注入，这也就是说为什么只要是IoC容器中的组件就能生效的原因。

再次进入到this.configurers.addWebMvcConfigurers(configurers);方法中进一步查看源码：

![image.png](assets/img202411252205128.png)

对于WebMvcConfigurerComposite类的代码来说，它是一个非常典型的组合模式。

组合模式的关键点：

1. 组合多个 WebMvcConfigurer 实例：WebMvcConfigurerComposite 通过 delegates 列表组合了多个 WebMvcConfigurer 实例。
2. 统一接口：WebMvcConfigurerComposite 实现了 WebMvcConfigurer 接口，因此可以像一个单一的 WebMvcConfigurer 一样被使用。
3. 代理调用：在实现 WebMvcConfigurer 接口的方法时，WebMvcConfigurerComposite 会遍历 delegates 列表，调用每个 WebMvcConfigurer 实例的相应方法。

总结：WebMvcConfigurerComposite 主要采用了组合模式的思想，将多个 WebMvcConfigurer 实例组合在一起，形成一个整体。

## WebMvcConfigurationSupport

提供了很多的默认设置。判断系统中是否有相应的类：如果有，就加入相应的`HttpMessageConverter`

```java
jackson2Present = ClassUtils.isPresent("com.fasterxml.jackson.databind.ObjectMapper", classLoader) &&
				ClassUtils.isPresent("com.fasterxml.jackson.core.JsonGenerator", classLoader);
jackson2XmlPresent = ClassUtils.isPresent("com.fasterxml.jackson.dataformat.xml.XmlMapper", classLoader);
jackson2SmilePresent = ClassUtils.isPresent("com.fasterxml.jackson.dataformat.smile.SmileFactory", classLoader);
```
