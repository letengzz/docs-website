# 静态资源访问

## 静态资源规则

只要静态资源放在类路径下如下⽬录： `/static`、 `/public`、`/resources`、`/META-INF/resources` ，就可以使⽤静态资源⽅式访问： **当前项目根路径/ + 静态资源名**

:::warning 说明

默认情况下， 静态映射是`/**`，可以使用属性 `spring.mvc.static-path-pattern` 属性进行调整，也可以使用 `spring.mvc.resources.static-locations` 配置⾃定义静态资源存放目录。

```yaml
spring:
  mvc:
    static-path-pattern: /res/** #静态资源映射路径，默认/**
  web:
    resources:
      static-locations: [classpath:/hjc/] #静态资源自定义路径，设置有默认路径失效
```

:::

:::danger 注意

自定义资源路径后，默认资源路径失效。

:::

当请求进来，先去找Controller看能不能处理。不能处理的所有请求⼜都交给静态资源处理器。静态资源也找不到则响应404页面。

## 静态资源缓存处理

不管是webjars的静态资源还是普通静态资源，统一都会执行以下这个方法，这个方法最后几行代码就是关于静态资源的缓存处理方式。

![image.png](assets/img202411252228524.png)

静态资源缓存指的是浏览器的缓存行为，浏览器可以将静态资源（js、css、图片、声音、视频）缓存到浏览器中，只要下一次用户访问同样的静态资源直接从缓存中取，不再从服务器中获取，可以降低服务器的压力，提高用户的体验。而这个缓存策略可以在服务器端程序中进行设置，SpringBoot对静态资源缓存的默认策略就是以下这三行代码：

![image.png](assets/img202411252228553.png)

- `registration.setCachePeriod(getSeconds(this.resourceProperties.getCache().getPeriod()));`

  - 设置缓存的过期时间（如果没有指定单位，默认单位是秒）
  - 浏览器会根据响应头中的缓存控制信息决定是否从本地缓存中加载资源，而不是每次都从服务器重新请求。这有助于减少网络流量和提高页面加载速度。
  - 假设配置了静态资源缓存过期时间为 1 小时（3600 秒），那么浏览器在首次请求某个静态资源后，会在接下来的一小时内从本地缓存加载该资源，而不是重新请求服务器。
  - 可以通过application.properties的来修改默认的过期时间，例如：`spring.web.resources.cache.period=3600`或者`spring.web.resources.cache.period=1h`

- `registration.setCacheControl(this.resourceProperties.getCache().getCachecontrol().toHttpCacheControl());`

  - 设置静态资源的 Cache-Control HTTP 响应头，告诉浏览器如何去缓存这些资源。

  - Cache-Control HTTP 响应头 是HTTP响应协议的一部分内容。如下图响应协议的响应头信息中即可看到Cache-Control的字样：

    ![image.png](assets/img202411252220077.png)

  - 常见的 Cache-Control 指令包括：

    - `max-age=<seconds>`：表示响应在多少秒内有效。

    - `public`：表示响应可以被任何缓存机制（如代理服务器）缓存。

    - `private`：表示响应只能被用户的浏览器缓存。

    - `no-cache`：表示在使用缓存的资源之前必须重新发送一次请求进行验证。

    - `no-store`：表示不缓存任何响应的资源。

  - 例如：max-age=3600, public：表示响应在 3600 秒内有效，并且可以被任何缓存机制缓存。

  - 可以通过spring.web.resources.cache.cachecontrol.max-age=3600以及spring.web.resources.cache.cachecontrol.cache-public=true进行重新配置。

- `registration.setUseLastModified(this.resourceProperties.getCache().isUseLastModified());`

  - 设置静态资源在响应时，是否在响应头中添加资源的最后一次修改时间。SpringBoot默认配置的是：在响应头中添加响应资源的最后一次修改时间。

  - 浏览器发送请求时，会将缓存中的资源的最后修改时间和服务器端资源的最后一次修改时间进行比对，如果没有变化，仍然从缓存中获取。

  - 可以通过spring.web.resources.cache.use-last-modified=false来进行重新配置。

根据之前源码分析，得知静态资源缓存相关的配置应该使用`spring.web.resources.cache`：

![image.png](assets/img202411252222971.png)

![image.png](assets/img202411252222857.png)

![image.png](assets/img202411252222258.png)

![image.png](assets/img202411252222357.png)

在application.properties文件中对缓存进行如下的配置：

```properties
# spring.web：
# spring.web.locale: 配置国际化的区域信息
# spring.web.resources: 静态资源策略(staticLocations: 静态资源的路径、addMapping: 是否开启静态资源映射、chain: 静态资源处理链、cache: 缓存规则)

# 静态资源缓存设置
# 1. 设置缓存时间(s) 缓存有效期
spring.web.resources.cache.period=100
# 2. 缓存控制（cachecontrol配置的话，period会失效）
# 缓存详细合并项控制，覆盖period配置：
# 浏览器第一次请求服务器，服务器告诉浏览器此资源缓存7200秒，7200秒以内的所有此资源访问不用发给服务器请求，7200秒以后发请求给服务器
spring.web.resources.cache.cachecontrol.max-age=20
# 3. 是否使用缓存的最后修改时间（默认是：使用）
# 使用资源 last-modified 时间，来对比服务器和浏览器的资源是否相同没有变化。相同返回 304
spring.web.resources.cache.use-last-modified=true
# 4. 是否开启静态资源默认处理方式（默认是：开启）
spring.web.resources.add-mappings=true
server.port=9000
```

:::danger 注意

cachecontrol.max-age配置的话，period会被覆盖。

![image.png](assets/img202411252228805.png)

:::

启动服务器测试：看看是否在20秒内走缓存，20秒之后是不是就不走缓存了！！！

第一次访问：请求服务器

![image.png](assets/img202411252228265.png)

第二次访问：20秒内开启一个新的浏览器窗口，再次访问，发现走了缓存

![image.png](assets/img202411252228750.png)

第三次访问：20秒后开启一个新的浏览器窗口，再次访问，发现重新请求服务器

![image.png](assets/img202411252228929.png)

提示，为什么显示304，这是因为这个配置：`spring.web.resources.cache.use-last-modified=true`

## 欢迎页

SpringBoot 支持静态和模板的欢迎页静态资源路径`classpath:/static`下添加 index.html。

欢迎页规则在 WebMvcAutoConfiguration 中进行了定义：

1. 在**静态资源**目录下找 index.html
2. 没有就在 templates下找index模板页

:::danger 注意

- 不可以配置静态资源的访问前缀，否则导致 index.html不能被默认访问。

- 模板路径`classpath:/templates`下添加index.html，只有static不存在欢迎页才会访问。

- 需要配置thymleaf模板引擎：

  ```xml
  <dependency>
  	<groupId>org.springframework.boot</groupId>
  	<artifactId>spring-boot-starter-thymeleaf</artifactId>
  </dependency>
  ```

:::

![image-20230804205109114](assets/202308042052242.png)

源码分析：在WebMvcAutoConfiguration类中有一个内部类EnableWebMvcConfiguration，这个类中有这样一段代码：

![image.png](assets/img202411252228418.png)

![image.png](assets/img202411252228070.png)

![image.png](assets/img202411252228433.png)

![image.png](assets/img202411252229899.png)

通过以上源码追踪，得出结论：只要请求路径是/\*\*的，会依次去{ "classpath:/META-INF/resources/", "classpath:/resources/", "classpath:/static/", "classpath:/public/" }这四个位置找index.html页面作为欢迎页。

WebMvcAutoConfiguration的生效条件：

![image.png](assets/img202411252228874.png)

上图红框内表示，要求Spring容器中缺失WebMvcConfigurationSupport这个Bean，WebMvcAutoConfiguration才会生效。EnableWebMvcConfiguration的继承结构：

![image.png](assets/img202411252228515.png)

很明显，EnableWebMvcConfiguration就是一个WebMvcConfigurationSupport这样的Bean。

EnableWebMvcConfiguration是WebMvcAutoConfiguration类的内部类。在WebMvcAutoConfiguration进行加载的时候，EnableWebMvcConfiguration这个内部类还没有加载。因此这个时候在容器中还不存在WebMvcConfigurationSupport的Bean，所以WebMvcAutoConfiguration仍然会生效。

以上所说的WebMvcAutoConfiguration类中的内部类EnableWebMvcConfiguration，是用来启用Web MVC默认配置的。

注意区分：WebMvcAutoConfiguration的两个内部类：

- WebMvcAutoConfigurationAdapter作用是用来：修改配置的
- EnableWebMvcConfiguration作用是用来：启用配置的

## Favorites Icon

favicon（也称为“收藏夹图标”或“网站图标”）是大多数现代网页浏览器的默认行为之一。当用户访问一个网站时，浏览器通常会尝试从该网站的根目录下载名为 favicon.ico 的文件，并将其用作标签页的图标。

如果网站没有提供 favicon.ico 文件，浏览器可能会显示一个默认图标，或者根本不显示任何图标。为了确保良好的用户体验，网站开发者通常会在网站的根目录下放置一个 favicon.ico 文件。

favicon.ico 放在静态资源目录下即可。

:::danger 注意

自定义资源路径后，Favicon 功能失效。

![image-20230804205715095](assets/202308042057630.png)

:::

## webjar

自动映射 `/webjars/**`

官方网站：https://www.webjars.org/

```xml
<dependency>
	<groupId>org.webjars</groupId>
    <artifactId>jquery</artifactId>
    <version>3.5.1</version>
</dependency>
```

访问地址：http://localhost:8080/webjars/jquery/3.5.1/jquery.js 后面地址要按照依赖里面的包路径

![image-20230804210209928](assets/202308042102577.png)

## 自定义静态资源规则

自定义静态资源路径、自定义缓存规则

### 配置方式

`spring.mvc`： 静态资源访问前缀路径

`spring.web`：

- 静态资源目录
- 静态资源缓存策略

```properties
# spring.web：
# spring.web.locale: 配置国际化的区域信息
# spring.web.resources: 静态资源策略(staticLocations: 静态资源的路径、addMapping: 是否开启静态资源映射、chain: 静态资源处理链、cache: 缓存规则)

#开启静态资源映射规则
spring.web.resources.add-mappings=true

#设置缓存时间(s)
spring.web.resources.cache.period=3600
##缓存详细合并项控制，覆盖period配置：
## 浏览器第一次请求服务器，服务器告诉浏览器此资源缓存7200秒，7200秒以内的所有此资源访问不用发给服务器请求，7200秒以后发请求给服务器
spring.web.resources.cache.cachecontrol.max-age=7200
#使用资源 last-modified 时间，来对比服务器和浏览器的资源是否相同没有变化。相同返回 304
spring.web.resources.cache.use-last-modified=true


# 共享缓存
spring.web.resources.cache.cachecontrol.cache-public=true
#自定义静态资源文件夹位置
spring.web.resources.static-locations=classpath:/a/,classpath:/b/,classpath:/static/

#spring.mvc
# 自定义webjars路径前缀
spring.mvc.webjars-path-pattern=/wj/**
# 静态资源访问路径前缀
spring.mvc.static-path-pattern=/static/**
```

### 代码方式

容器中只要有一个 WebMvcConfigurer 组件，配置的底层行为都会生效。

**原理**：

1. WebMvcAutoConfiguration 是一个自动配置类，它里面有一个 `EnableWebMvcConfiguration`
2. `EnableWebMvcConfiguration`继承与 `DelegatingWebMvcConfiguration`，这两个都生效
3. `DelegatingWebMvcConfiguration`利用 DI 把容器中 所有 `WebMvcConfigurer `注入进来
4. 别人调用 `DelegatingWebMvcConfiguration` 的方法配置底层规则，而它调用所有 `WebMvcConfigurer`的配置底层方法。

```java
@EnableWebMvc //禁用boot的默认配置
@Configuration //这是一个配置类
public class MyConfig implements WebMvcConfigurer {


    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        //保留以前规则
        WebMvcConfigurer.super.addResourceHandlers(registry);
        //自己写新的规则。
        registry.addResourceHandler("/static/**")
                .addResourceLocations("classpath:/a/","classpath:/b/")
                .setCacheControl(CacheControl.maxAge(1180, TimeUnit.SECONDS));
    }
}
```

或

```java
@Configuration //这是一个配置类,给容器中放一个 WebMvcConfigurer 组件，就能自定义底层
public class MyConfig {


    @Bean
    public WebMvcConfigurer webMvcConfigurer(){
        return new WebMvcConfigurer() {
            @Override
            public void addResourceHandlers(ResourceHandlerRegistry registry) {
                registry.addResourceHandler("/static/**")
                        .addResourceLocations("classpath:/a/", "classpath:/b/")
                        .setCacheControl(CacheControl.maxAge(1180, TimeUnit.SECONDS));
            }
        };
    }
}
```

![image-20230804213433129](assets/202308042134269.png)
