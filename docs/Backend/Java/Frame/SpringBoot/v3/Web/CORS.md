# 单体项目跨域问题

:::danger 注意

在微服务架构下，只需在网关层进行跨域处理即可，多重跨域会报错。

:::

## 注解配置

在启动类添加 `@CrossOrigin`注解

```java
@CrossOrigin
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(EnumApplication.class, args);
    }

}
```

## 全局配置

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                // 允许跨域的域名，可以用*代表允许任意域名跨域
                .allowedOrigins("http://localhost:5173")
                // 是否发送Cookie信息
                .allowCredentials(true)
                // 允许的类型
                .allowedMethods("POST", "GET", "PUT", "OPTIONS", "DELETE")
                // 允许的头信息
                .allowedHeaders("*")
                // 暴露出哪些头信息（因为跨域访问默认不能获取全部头信息）
                .exposedHeaders("*");
    }
}
```
