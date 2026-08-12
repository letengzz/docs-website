# 嵌入式容器

**Servlet容器**：管理、运行Servlet组件 (Servlet、Filter、Listener) 的环境，一般指服务器

## 自动配置原理

**SpringBoot 默认嵌入Tomcat作为Servlet容器**。自动配置类是ServletWebServerFactoryAutoConfiguration，EmbeddedWebServerFactoryCustomizerAutoConfiguration

ServletWebServerFactoryAutoConfiguration 自动配置了嵌入式容器场景：

```java
@AutoConfiguration
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
@ConditionalOnClass(ServletRequest.class)
@ConditionalOnWebApplication(type = Type.SERVLET)
@EnableConfigurationProperties(ServerProperties.class)
@Import({ ServletWebServerFactoryAutoConfiguration.BeanPostProcessorsRegistrar.class,
		ServletWebServerFactoryConfiguration.EmbeddedTomcat.class,
		ServletWebServerFactoryConfiguration.EmbeddedJetty.class,
		ServletWebServerFactoryConfiguration.EmbeddedUndertow.class })
public class ServletWebServerFactoryAutoConfiguration {

}
```

绑定了ServerProperties配置类，所有和服务器有关的配置 server：

ServletWebServerFactoryAutoConfiguration 导入了 嵌入式的三大服务器 Tomcat、Jetty、Undertow

![image-20231224163631649](assets/img202312241636902.png)

- 导入 Tomcat、Jetty、Undertow 都有条件注解。系统中有这个类才行 (也就是导了包)

- 默认 Tomcat配置生效。给容器中放 TomcatServletWebServerFactory

- 都给容器中 ServletWebServerFactory放了一个 web服务器工厂 (造web服务器的)

- web服务器工厂 都有一个功能，getWebServer获取web服务器

- TomcatServletWebServerFactory 创建了 tomcat。

ServletWebServerFactory 什么时候会创建 webServer出来。

ServletWebServerApplicationContextioc容器，启动的时候会调用创建web服务器

Spring容器刷新（启动）的时候，会预留一个时机，刷新子容器：`onRefresh()`

`refresh()` 容器刷新 十二大步的刷新子容器会调用 `onRefresh()`；

```java
@Override
protected void onRefresh() {
	super.onRefresh();
	try {
		createWebServer();
	}
	catch (Throwable ex) {
		throw new ApplicationContextException("Unable to start web server", ex);
	}
}
```

Web场景的Spring容器启动，在onRefresh的时候，会调用创建web服务器的方法。
Web服务器的创建是通过WebServerFactory搞定的。容器中又会根据导了什么包条件注解，启动相关的 服务器配置，默认EmbeddedTomcat会给容器中放一个 TomcatServletWebServerFactory，导致项目启动，自动创建出Tomcat。

## 切换容器

切换服务器只需要将默认的Tomcat依赖排除，引入需要的嵌入式容器即可：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <!-- Exclude the Tomcat dependency -->
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<!-- Use Jetty instead -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

## web服务器优化

通过以下源码得知，web服务器的相关配置和ServerProperties有关系：

![image.png](assets/img202411202028531.webp)

查看ServerProperties源码：得知web服务器的配置都是以server开头的。

![image.png](assets/img202411202028483.webp)

ServerProperties源码：通过源码得知，如果要对tomcat服务器进行配置，前缀为：server.tomcat。如果要对jetty服务器进行配置，前缀为：server.jetty。

![image.png](assets/img202411202029759.webp)

![image.png](assets/img202411202029184.webp)

在以后的开发中关于tomcat服务器的常见优化配置有：

```properties
# 这个参数决定了 Tomcat 在接收请求时，如果在指定的时间内没有收到完整的请求数据，将会关闭连接。这个超时时间是从客户端发送请求开始计算的。
# 防止长时间占用资源：如果客户端发送请求后，长时间没有发送完所有数据，Tomcat 会在这个超时时间内关闭连接，从而释放资源，避免资源被长时间占用。
server.tomcat.connection-timeout=20000

# 设置 Tomcat 服务器处理请求的最大线程数为 200。
# 如果超过这个数量的请求同时到达，Tomcat 会将多余的请求放入一个等待队列中。
# 如果等待队列也满了（由 server.tomcat.accept-count 配置），新的请求将被拒绝，通常会返回一个“503 Service Unavailable”错误。
server.tomcat.max-threads=200

# 用来设置等待队列的最大容量
server.tomcat.accept-count=100

# 设置 Tomcat 服务器在空闲时至少保持 10 个线程处于活动状态，以便快速响应新的请求。
server.tomcat.min-spare-threads=10

# 允许 Tomcat 服务器在关闭后立即重新绑定相同的地址和端口，即使该端口还在 TIME_WAIT 状态
# 当一个网络连接关闭时，操作系统会将该连接的端口保持在 TIME_WAIT 状态一段时间（通常是 2-4 分钟），以确保所有未完成的数据包都能被正确处理。在这段时间内，该端口不能被其他进程绑定。
server.tomcat.address-reuse-enabled=true

# 设置 Tomcat 服务器绑定到所有可用的网络接口，使其可以从任何网络地址访问。
server.tomcat.bind-address=0.0.0.0

# 设置 Tomcat 服务器使用 HTTP/1.1 协议处理请求。
server.tomcat.protocol=HTTP/1.1

# 设置 Tomcat 服务器的会话(session)超时时间为 30 分钟。具体来说，如果用户在 30 分钟内没有与应用进行任何交互，其会话将被自动注销。
server.tomcat.session-timeout=30

# 设置 Tomcat 服务器的静态资源缓存时间为 3600 秒（即 1 小时），这意味着浏览器会在 1 小时内缓存这些静态资源，减少重复请求。
server.tomcat.resource-cache-period=3600

# 解决get请求乱码。对请求行url进行编码。
server.tomcat.uri-encoding=UTF-8

# 设置 Tomcat 服务器的基础目录为当前工作目录（. 表示当前目录）。这个配置指定了 Tomcat 服务器的工作目录，包括日志文件、临时文件和其他运行时生成的文件的存放位置。 生产环境中可能需要重新配置。
server.tomcat.basedir=.
```
