# Spring Security 构建入门程序

- 基于 [Spring Security 专题](../../../index.md) 项目搭建！

首先导入SpringSecurity的相关依赖 (它不仅仅是一个模块，可以根据需求导入需要的模块)，常用的是以下两个(版本同 `spring-webmvc`版本)：

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-web</artifactId>
    <version>6.1.1</version>
</dependency>
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-config</artifactId>
    <version>6.1.1</version>
</dependency>
```

配置SpringSecurity初始化器：

```java
public class SecurityInitializer extends AbstractSecurityWebApplicationInitializer {
    //不用重写任何内容
  	//这里实际上会自动注册一个Filter，SpringSecurity底层就是依靠N个过滤器实现的
}
```

创建一个配置类用于配置SpringSecurity：

```java
@Configuration
@EnableWebSecurity   //开启WebSecurity相关功能
public class SecurityConfiguration {

}
```

在根容器中添加此配置文件即可：

```java
@Override
protected Class<?>[] getRootConfigClasses() {
    return new Class[]{MainConfiguration.class, SecurityConfiguration.class};
}
```

这样，SpringSecurity的配置就完成了，再次运行项目，会发现无法进入的我们的页面中，无论访问哪个页面，都会进入到SpringSecurity为我们提供的一个默认登录页面。

![image-20230920181714958](assets/img202402241614941.png)

至此，项目环境搭建完成。
