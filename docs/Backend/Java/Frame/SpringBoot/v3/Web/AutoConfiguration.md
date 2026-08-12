# SpringMVC自动配置

SpringBoot 大多场景都无需自定义配置，包括：

- 内容协商视图解析器和BeanName视图解析器
- 静态资源 (包括webjars)
- 自动注册 `Converter，GenericConverter，Formatter `
- 支持 `HttpMessageConverters`
- 自动注册 `MessageCodesResolver` (国际化用)
- 静态index.html 页支持
- 自定义 `Favicon`
- 自动使用 `ConfigurableWebBindingInitializer` (DataBinder负责将请求数据绑定到JavaBean上)

**不用`@EnableWebMvc`注解。使用** `@Configuration` **+** `WebMvcConfigurer` **自定义规则**

**声明** `WebMvcRegistrations` **改变默认底层组件**

**使用** `@EnableWebMvc`+`@Configuration`+`DelegatingWebMvcConfiguration` 全面接管SpringMVC

## 自动配置过程

1. 整合web场景：

   ```xml
   <dependency>
       <groupId>org.springframework.boot</groupId>
   	<artifactId>spring-boot-starter-web</artifactId>
   </dependency>
   ```

2. 引入了 `autoconfigure`功能

   ```xml
   <dependency>
     <groupId>org.springframework.boot</groupId>
     <artifactId>spring-boot-starter</artifactId>
     <version>3.3.5</version>
     <scope>compile</scope>
   </dependency>
   ```

   spring-boot-starter会传递引入一个spring-boot-autoconfigure包：

   ```xml
   <dependency>
     <groupId>org.springframework.boot</groupId>
     <artifactId>spring-boot-autoconfigure</artifactId>
     <version>3.3.5</version>
     <scope>compile</scope>
   </dependency>
   ```

3. 从入口程序开始：入口程序被`@SpringBootApplication`注解标注。

   ```java
   @SpringBootApplication
   public class WebApplication {

       public static void main(String[] args) {
           SpringApplication.run(WebApplication.class, args);
       }
   }
   ```

4. `@SpringBootApplication`注解被`@EnableAutoConfiguration`注解标注。表示启用自动配置。

5. `@EnableAutoConfiguration`注解使用`@Import(AutoConfigurationImportSelector.class)`批量导入组件

   AutoConfigurationImportSelector底层实现步骤具体：

   ![image.png](assets/img202411252109113.png)

   ![image.png](assets/img202411252109257.png)

   ![image.png](assets/img202411252109426.png)

   ![image.png](assets/img202411252109345.png)

6. 加载 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 文件中配置的所有组件

7. 所有自动配置类：

   > org.springframework.boot.autoconfigure.web.client.RestTemplateAutoConfiguration
   > org.springframework.boot.autoconfigure.web.embedded.EmbeddedWebServerFactoryCustomizerAutoConfiguration
   > ====以下是响应式web场景和现在的没关系======
   > org.springframework.boot.autoconfigure.web.reactive.HttpHandlerAutoConfiguration
   > org.springframework.boot.autoconfigure.web.reactive.ReactiveMultipartAutoConfiguration
   > org.springframework.boot.autoconfigure.web.reactive.ReactiveWebServerFactoryAutoConfiguration
   > org.springframework.boot.autoconfigure.web.reactive.WebFluxAutoConfiguration
   > org.springframework.boot.autoconfigure.web.reactive.WebSessionIdResolverAutoConfiguration
   > org.springframework.boot.autoconfigure.web.reactive.error.ErrorWebFluxAutoConfiguration
   > org.springframework.boot.autoconfigure.web.reactive.function.client.ClientHttpConnectorAutoConfiguration
   > org.springframework.boot.autoconfigure.web.reactive.function.client.WebClientAutoConfiguration
   > ================以上没关系=================
   > org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration
   > org.springframework.boot.autoconfigure.web.servlet.ServletWebServerFactoryAutoConfiguration
   > org.springframework.boot.autoconfigure.web.servlet.error.ErrorMvcAutoConfiguration
   > org.springframework.boot.autoconfigure.web.servlet.HttpEncodingAutoConfiguration
   > org.springframework.boot.autoconfigure.web.servlet.MultipartAutoConfiguration
   > org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration

8. 绑定了配置文件的一堆配置项：

   1. SpringMVC的所有配置 `spring.mvc`
   2. Web场景通用配置 `spring.web`
   3. 文件上传配置 `spring.servlet.multipart`
   4. 服务器的配置 `server`: 比如：编码方式

## Web配置

在自动配置列表中找到web自动配置相关的类：

![image.png](assets/img202411252123043.png)

以下就是web自动配置类列表：

```java
org.springframework.boot.autoconfigure.web.client.RestTemplateAutoConfiguration
org.springframework.boot.autoconfigure.web.embedded.EmbeddedWebServerFactoryCustomizerAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.ServletWebServerFactoryAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.error.ErrorMvcAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.HttpEncodingAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.MultipartAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration
```

通过web自动配置类的源码可以逆推web配置的prefix：

1. WebMvcAutoConfiguration

   ![image.png](assets/img202411252128302.png)

   ![image.png](assets/img202411252128835.png)

   ![image.png](https://cdn.nlark.com/yuque/0/2024/png/21376908/1729847268539-715a377a-ecb9-48fc-ad58-9194d23b7cdf.png?x-oss-process=image%2Fformat%2Cwebp)

2. MultipartAutoConfiguration：

   ![image.png](assets/img202411252128566.png)

   ![image.png](assets/img202411252129369.png)

3. HttpEncodingAutoConfiguration：

   ![image.png](assets/img202411252129852.png)

   ![image.png](assets/img202411252129717.png)

4. ErrorMvcAutoConfiguration

5. ServletWebServerFactoryAutoConfiguration

6. DispatcherServletAutoConfiguration

7. EmbeddedWebServerFactoryCustomizerAutoConfiguration

8. RestTemplateAutoConfiguration

通过查看源码，得知，web开发时，在application.properties配置文件中可以配置的前缀是：

```properties
# SpringMVC相关配置
spring.mvc.

# web开发通用配置
spring.web.

# 文件上传配置
spring.servlet.multipart.

# 服务器配置
server.
```
