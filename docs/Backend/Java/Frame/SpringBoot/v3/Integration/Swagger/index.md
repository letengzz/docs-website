# SpringBoot 整合 Swagger

## OpenAPI 3 与 Swagger

**OpenAPI规范** (OpenAPI Specification 简称OAS) 是Linux基金会的一个项目，试图通过定义一种用来描述API格式或API定义的语言，来规范RESTful服务开发过程，目前版本是V3.0，并且已经发布并开源在github上。

**官方网站**：https://github.com/OAI/OpenAPI-Specification

---

Swagger是全球最大的OpenAPI规范 (OAS) API开发工具框架，遵循 OpenAPI 规范。用于生成、描述、调用和可视化 RESTful 风格的 Web 服务。

Swagger 可以快速**生成实时接口文档**，方便前后端开发人员进行协调沟通，依据接口文档进行开发。

**优点**：

1. 及时性 (接口变更后，能够及时准确地通知相关前后端开发人员)

2. 规范性 (并且保证接口的规范性，如接口的地址，请求方式，参数及响应格式和错误信息)

3. 一致性 (接口信息一致，不会出现因开发人员拿到的文档版本不一致，而出现分歧)

4. 可测性 (直接在接口文档上进行测试，以方便理解业务)

**官方网站**： https://swagger.io/
**官方文档**：https://springdoc.org/

## OpenAPI 3 架构

![image.png](assets/img202312240109155.png)

## 整合 Swagger

Spring Boot 可以集成Swagger，Swaager根据Controller类中的注解生成接口文档 。

**操作步骤**：

- 导入依赖：

  ```xml
  <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
      <version>2.3.0</version>
  </dependency>
  ```

- 配置：

  ```properties [application.properties]
  # /api-docs endpoint custom path 默认 /v3/api-docs
  springdoc.api-docs.path=/api-docs
  
  # swagger 相关配置在  springdoc.swagger-ui
  # swagger-ui custom path
  springdoc.swagger-ui.path=/swagger-ui.html
  
  springdoc.show-actuator=true
  ```

  ```yaml [application.yaml]
  springdoc:
    # /api-docs endpoint custom path 默认 /v3/api-docs
    api-docs.path: /api-docs
    # swagger 相关配置在  springdoc.swagger-ui
    # swagger-ui custom path
    swagger-ui.path: /swagger-ui.html
    show-actuator: true
    default-flat-param-object: true
  ```

## 集成Knife4j

knife4j是为Java MVC框架集成Swagger生成Api文档的增强解决方案。

文档地址：https://doc.xiaominfo.com/

**操作步骤**：

1. 调整启动类：

   ```java
   Environment env = application.getEnvironment();
           log.info("\n----------------------------------------------------------\n\t" +
                           "应用 '{}' 运行成功! 访问连接:\n\t" +
                           "Swagger文档: \t\thttp://{}:{}{}/doc.html\n\t" +
                           "----------------------------------------------------------",
                   env.getProperty("spring.application.name"),
                   InetAddress.getLocalHost().getHostAddress(),
                   env.getProperty("server.port"),
                   env.getProperty("server.servlet.context-path") != null ? env.getProperty("server.servlet.context-path") : "" );
   ```

2. 创建spring boot项目并导入knife4j的依赖：

   ```xml
   <dependency>
       <groupId>com.github.xiaoymin</groupId>
       <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
       <version>4.3.0</version>
   </dependency>
   ```

3. 属性的配置，如：作者、版本等可以在配置类中进行实现：

   ```java
   @Configuration
   public class Knife4jConfig {
   
       @Bean
       public OpenAPI springShopOpenAPI() {
           return new OpenAPI()
                   // 接口文档标题
                   .info(new Info().title("一个API接口文档")
                           // 接口文档简介
                           .description("这是基于Knife4j OpenApi3的测试接口文档")
                           // 接口文档版本
                           .version("1.0版本")
                           // 开发者联系方式
                           .contact(new Contact().name("hjc")
                                   .email("000000000@qq.com")))
                   .externalDocs(new ExternalDocumentation()
                           .description("SpringBoot3测试knife4j")
                           .url("http://127.0.0.1:8888"));
       }
   
   }
   ```

   也可以在yml配置文件中进行一些knife4j信息的配置：

   ```yaml
   #springdoc相关配置
   springdoc:
     default-flat-param-object: true
     swagger-ui:
       #自定义swagger前端请求路径，输入http：127.0.0.1:8080/swagger-ui.html会自动重定向到swagger页面
       path: /swagger-ui.html
       tags-sorter: alpha
       operations-sorter: alpha
     api-docs:
       path: /v3/api-docs #swagger后端请求地址
       enabled: true #是否开启文档功能
     group-configs:
       - group: 'com.hjc.demo'
         paths-to-match: '/**'
         packages-to-scan: com.example.springboot3knife4j #按包路径匹配:一般到启动类的包名
   
   #knife4j相关配置 可以不用改
   knife4j:
     enable: true #开启knife4j，无需添加@EnableKnife4j注解
     setting:
       language: zh_cn #中文
     #开启Swagger的Basic认证功能,默认是false
   #  basic:
   #    enable: true
   # Basic认证用户名
   #    username: hjc
   # Basic认证密码
   #    password: 123456
   ```

## 使用

### 常用注解

在Java类中添加Swagger的注解即可生成Swagger接口，常用Swagger注解：

![image-20231224005519126](assets/img202312240055116.png)

:::warning

- `@Tag(name="")` 注解用于对接口进行分类，相同`Tag`的接口会放在同一个菜单。

- `@Operation(summary="")`用于对接口进行描述。

- `@Parameter(description="")`用于对HTTP请求参数进行描述

- `@Schema(desctipion="")`注解用于描述作为接口参数或者返回值的实体类的数据结构。

:::

### Docket 配置

如果有多个Docket，配置：

```java
  @Bean
  public GroupedOpenApi publicApi() {
      return GroupedOpenApi.builder()
              .group("springshop-public")
              .pathsToMatch("/public/**")
              .build();
  }
  @Bean
  public GroupedOpenApi adminApi() {
      return GroupedOpenApi.builder()
              .group("springshop-admin")
              .pathsToMatch("/admin/**")
              .addMethodFilter(method -> method.isAnnotationPresent(Admin.class))
              .build();
  }
```

如果只有一个Docket，可以配置：

```properties
springdoc.packagesToScan=package1, package2
springdoc.pathsToMatch=/v1, /api/balance/**
```

### OpenAPI配置

```java
@Bean
public OpenAPI springShopOpenAPI() {
	return new OpenAPI()
    	      .info(new Info().title("SpringShop API")   // 接口文档标题
                  .description("Spring shop sample application") // 接口文档简介
                  .version("v0.0.1") // 接口文档版本
                  .license(new License().name("Apache 2.0").url("http://springdoc.org"))
                  .contact(new Contact().name("hjc")
                                .email("2020885569@qq.com"))) // 开发者联系方式
              .externalDocs(new ExternalDocumentation()
                  .description("SpringShop Wiki Documentation")
                  .url("https://springshop.wiki.github.org/docs"));
}
```

## Springfox 迁移

### 注解变化

![image-20231224010724087](assets/img202312240107498.png)

### Docket配置

#### 以前写法

```java
@Bean
public Docket publicApi() {
    return new Docket(DocumentationType.SWAGGER_2)
              .select()
              .apis(RequestHandlerSelectors.basePackage("org.github.springshop.web.public"))
              .paths(PathSelectors.regex("/public.*"))
              .build()
              .groupName("springshop-public")
              .apiInfo(apiInfo());
}

@Bean
public Docket adminApi() {
    return new Docket(DocumentationType.SWAGGER_2)
              .select()
              .apis(RequestHandlerSelectors.basePackage("org.github.springshop.web.admin"))
              .paths(PathSelectors.regex("/admin.*"))
              .apis(RequestHandlerSelectors.withMethodAnnotation(Admin.class))
              .build()
              .groupName("springshop-admin")
              .apiInfo(apiInfo());
}
```

#### 新写法

```java
@Bean
public GroupedOpenApi publicApi() {
    return GroupedOpenApi.builder()
              .group("springshop-public")
              .pathsToMatch("/public/**")
              .build();
}
@Bean
public GroupedOpenApi adminApi() {
    return GroupedOpenApi.builder()
              .group("springshop-admin")
              .pathsToMatch("/admin/**")
              .addOpenApiMethodFilter(method -> method.isAnnotationPresent(Admin.class))
              .build();
}
```

### 添加OpenAPI组件

```java
@Bean
public OpenAPI springShopOpenAPI() {
    return new OpenAPI()
              .info(new Info().title("SpringShop API")
              .description("Spring shop sample application")
              .version("v0.0.1")
              .license(new License().name("Apache 2.0").url("http://springdoc.org")))
              .externalDocs(new ExternalDocumentation()
              .description("SpringShop Wiki Documentation")
              .url("https://springshop.wiki.github.org/docs"));
}
```
