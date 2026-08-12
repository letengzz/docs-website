# Spring Security 构建入门程序

**官方代码示例**：[GitHub - spring-projects/spring-security-samples](https://github.com/spring-projects/spring-security-samples/tree/main)

**环境要求**：

- JDK：Java17
- Maven：3.9.5
- SpringBoot：3.2.2

## 构建项目

使用Spring Initializr 创建项目，并选择Spring Web、Spring Security、Thymeleaf依赖：

![image-20240211180735335](assets/img202402121754129.png)

创建完成后查看依赖：

```xml
	<dependencies>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-security</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-thymeleaf</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-web</artifactId>
		</dependency>
        <!-- thymeleaf针对于spring security 兼容性的依赖 -->
		<dependency>
			<groupId>org.thymeleaf.extras</groupId>
			<artifactId>thymeleaf-extras-springsecurity6</artifactId>
		</dependency>

		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.security</groupId>
			<artifactId>spring-security-test</artifactId>
			<scope>test</scope>
		</dependency>
	</dependencies>
```

创建页面：

> src/main/resources/templates/index.html

```html
<html xmlns:th="https://www.thymeleaf.org">
  <head>
    <title>Hello Security!</title>
  </head>
  <body>
    <h1>Hello Security</h1>
    <!--通过使用@{/logout}，Thymeleaf将自动处理生成正确的URL，以适应当前的上下文路径。
这样，无论应用程序部署在哪个上下文路径下，生成的URL都能正确地指向注销功能。-->
    <a th:href="@{/logout}">Log Out</a>
  </body>
</html>
```

创建Controller：

```java
@Controller
public class IndexController {
    @RequestMapping(value = "/")
    public String index(){
        return "index";
    }
}
```

## 运行项目

当运行起来访问，会自动跳转到默认登陆页面，在运行的时候校验了用户是否已经进行了用户身份认证(默认情况下，会自动生成登陆页，并把url地址重定向到login登陆页)，如果没有进行身份认证。

![image-20230920181714958](assets/img202402121754725.png)

默认用户名 `user` 密码在控制台中，每次重启都会重新生成

![image-20240211190943354](assets/img202402121754080.png)

访问并输入用户名和密码：http://localhost:8080/

![image-20240211191305237](assets/img202402121754604.png)

点击`Log Out`退出到登录页面：

![image-20240211191423240](assets/img202402121754186.png)

## 退出登录

当退出时，也可以直接访问：http://localhost:8080/logout 地址，会进入到一个退出登录界面：

![image-20230920183136259](assets/202309201831588.png)

退出登录后需要重新登录才能访问网站。

## 常见问题

页面样式bootstrap.min.css是一个CDN地址，需要通过科学上网的方式访问

![image-20231130152247055](assets/img202402121754104.png)

否则你的登录页会加载很久，并且看到的页面是这样的（登录按钮没有样式文件渲染，但是不影响登录功能的执行）

![image-20231130152345471](assets/img202402121755684.png)

## Spring Security默认做了什么

- 保护应用程序URL，要求对应用程序的任何交互进行身份验证。
- 程序启动时生成一个默认用户“user”。
- 生成一个默认的随机密码，并将此密码记录在控制台上。
- 生成默认的登录表单和注销页面。
- 提供基于表单的登录和注销流程。
- 对于Web请求，重定向到登录页面；
- 对于服务请求，返回401未经授权。
- 处理跨站请求伪造（CSRF）攻击。
- 处理会话劫持攻击。
- 写入Strict-Transport-Security以确保HTTPS。
- 写入X-Content-Type-Options以处理嗅探攻击。
- 写入Cache Control头来保护经过身份验证的资源。
- 写入X-Frame-Options以处理点击劫持攻击。
