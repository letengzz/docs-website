# OAuth 2

OAuth2：开放标准的授权协议。用于在不暴露用户凭证的情况下进行身份验证和授权。

## OAuth2 流程

首先要有用户的数据，有一个资源服务器负责管理用户数据，需要有一个客户应用需要访问用户应用。给资源服务器暴露用户数据称为API ，客户应用通过API访问资源服务器来返回用户的数据。

![image-20240227205942188](assets/img202402272059017.png)

如果来恶意用户应用访问资源服务器并且没有认证和校验，那么恶意客户也能访问到用户数据。就需要一种机制来保护用户的数据。

![image-20240227210002261](assets/img202402272100586.png)

业界实践是提前给客户应用颁发一个Access Token，表示用户应用被授权可以访问用户数据，当访问用户数据时，给出Access Token。客户端应用每次发送的请求，都要携带Access Token( 一般在请求头中携带)。

![image-20240227210113309](assets/img202402272101071.png)

接下来，资源服务器会取出请求中的Access Token并校验Access Token确认客户应用有访问用户数据的权限，校验通过后，资源服务器返回用户数据。

![image-20240227210139302](assets/img202402272101857.png)

这个机制可以工作的前提是必须提前给客户应用颁发Access Token，需要颁发Access Token的角色，这个角色就是授权服务器

授权服务器负责生成Access Token 并给客户应用颁发Access Token，客户应用带上Access Token访问用户数据。

![image-20240227210248379](assets/img202402272102785.png)

资源服务器会从请求中取出Access Token 并且校验Access Token具有访问用户数据的权限校验成功就会给客户应用了。

![image-20240227210402452](assets/img202402272104767.png)

在真实流程中，在颁发Token前要征询用户同意

![image-20240227210426020](assets/img202402272104475.png)

如果用户同意授权服务器颁发token ，授权服务器会生成一个Access Token 并将token 颁发给客户应用

![image-20240227210455072](assets/img202402272105629.png)

OAuth 2.0标准化了Access Token的请求和响应部分， OAuth2.0的细节在[RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749) (OAuth 2.0授权框架)中描述。

**OAuth2 最简向导：**[The Simplest Guide To OAuth 2.0](https://darutk.medium.com/the-simplest-guide-to-oauth-2-0-8c71bd9a15bb)

## OAuth2 角色

OAuth 2协议包含以下角色：

1. 资源所有者(`Resource Owner`)：即用户，资源的拥有人，想要通过客户应用访问资源服务器上的资源。
2. 客户应用(`Client`)：通常是一个Web或者无线应用，它需要访问用户的受保护资源。客户应用和资源服务器之间可以是两个完全不同的应用程序系统也可以是微服务中的两个微服务。
3. 资源服务器 (`Resource Server`)：存储受保护资源的服务器或定义了可以访问到资源的API，接收并验证客户端的访问令牌，以决定是否授权访问资源。
4. 授权服务器 (`Authorization Server`)：负责验证资源所有者的身份并向客户端颁发访问令牌。

![image-20231222124053994](assets/img202402272027866.png)

## OAuth2 使用场景

### 开放系统间授权

#### 社交登录

在传统的身份验证中，用户需要提供用户名和密码，还有很多网站登录时，允许使用第三方网站的身份，这称为"第三方登录"。所谓第三方登录，实质就是 OAuth 授权。用户想要登录 A 网站，A 网站让用户提供第三方网站的数据，证明自己的身份。获取第三方网站的身份数据，就需要 OAuth 授权。

![image-20231222131233025](assets/img202402272027683.png)

#### 开放API

例如云冲印服务的实现：资源拥有者在云存储服务上存储照片，通过云冲印服务来在线冲印照片需要云存储服务授权给云冲印服务。此时需要授权服务器给云冲印颁发一个令牌，云冲印服务携带着令牌就可以访问云存储服务的照片。

![image-20231222131118611](assets/img202402272027145.png)

### 现代微服务安全

#### 单块应用安全

由于应用程序服务器通常情况下都是单体应用部署到一台服务器中，所以在登录的过程中通常使用用户名和密码的方式来校验用户名和密码是否正确，如果正确的话，会存储一个session，给客户端返回一个携带sessionid 的Cookie，这个Cookie会存储在浏览器中。下一次登录时，会自动将请求中携带着Cookie去访问服务器，通过过滤器判断Cookie的Sessionid的用户信息，如果能够获取就是合法登录的可以访问业务，如果没有获取到就可能是没有登录或登录过期的，就不能访问业务

![image-20231222152734546](assets/img202402272028436.png)

#### 微服务安全

在微服务架构下，不是之前的单体应用了，面临着拆分粒度很小，每个项目都会拆分成多个微服务，微服务之间需要认证和授权。此外，前端的应用程序变得多种多样了，不是简单的基于浏览器的应用，因此，单体应用这种传统的方式就不能满足需求，使用OAuth2就可以解决该问题。

![image-20231222152557861](assets/img202402272028208.png)

### 企业内部应用认证授权

企业内部应用认证授权，包含：

- **单点登录** (`SSO`、`Single Sign On`)

- **身份识别与访问管理** (`IAM`、`Identity and Access Management` )

## OAuth2 四种授权模式

RFC6749：[RFC 6749 - The OAuth 2.0 Authorization Framework (ietf.org)](https://datatracker.ietf.org/doc/html/rfc6749)

阮一峰：[OAuth 2.0 的四种方式 - 阮一峰的网络日志 (ruanyifeng.com)](https://www.ruanyifeng.com/blog/2019/04/oauth-grant-types.html)

---

四种模式：

- **授权码** (`authorization-code`)
- **隐藏式** (`implicit`)
- **密码式** (`password`)
- **客户端凭证** (`client credentials`)

### 授权码

**授权码 (`authorization code`)，指的是第三方应用先申请一个授权码，然后再用该码获取令牌**

这种方式是最常用，最复杂，也是最安全的，它适用于那些有后端的 Web 应用。授权码通过前端传送，令牌则是储存在后端，而且所有与资源服务器的通信都在后端完成。这样的前后端分离，可以避免令牌泄漏。

![image-20231220180422742](assets/img202402272030332.png)

注册客户应用：客户应用如果想要访问资源服务器需要有凭证，需要在授权服务器上注册客户应用。注册后会**获取到一个ClientID和ClientSecrets**

![image-20231222203153125](assets/img202402272030328.png)

### 隐藏式

**隐藏式 (`implicit`)，也叫简化模式，有些 Web 应用是纯前端应用，没有后端。这时就不能用上面的方式了，必须将令牌储存在前端**

RFC 6749 规定了这种方式，允许直接向前端颁发令牌。这种方式没有授权码这个中间步骤，所以称为隐藏式。这种方式把令牌直接传给前端，是很不安全的。因此，只能用于一些安全要求不高的场景，并且令牌的有效期必须非常短，通常就是会话期间（session）有效，浏览器关掉，令牌就失效了。

![image-20231220185958063](assets/img202402272030752.png)

![image-20231222203218334](assets/img202402272031230.png)

> https://a.com/callback#token=ACCESS_TOKEN
> 将访问令牌包含在URL锚点中的好处：锚点在HTTP请求中不会发送到服务器，减少了泄漏令牌的风险。

### 密码式

**密码式 (`Resource Owner Password Credentials`)：如果你高度信任某个应用，RFC 6749 也允许用户把用户名和密码，直接告诉该应用。该应用就使用你的密码，申请令牌**

这种方式需要用户给出自己的用户名/密码，显然风险很大，因此只适用于其他授权方式都无法采用的情况，而且必须是用户高度信任的应用。

![image-20231220190152888](assets/img202402272031424.png)

![image-20231222203240921](assets/img202402272031895.png)

### 凭证式

**凭证式 (`client credentials`)：也叫客户端模式，适用于没有前端的命令行应用，即在命令行下请求令牌**

这种方式给出的令牌，是针对第三方应用的，而不是针对用户的，即有可能多个用户共享同一个令牌。

![image-20231220185958063](assets/img202402272032692.png)

![image-20231222203259785](assets/img202402272032779.png)

## 授权类型的选择

从开始节点进入流程，判断访问令牌拥有人是谁，如果是机器的话就选择凭证式，如果是用户时，看客户应用的类型，如果是Web应用就选择授权码模式，如果是原生App或单页应用如果是第一方应用(都属于一个企业的或同一个系统内部的)选择密码模式，如果是第三方应用，原生选择授权码，单页应用选择隐藏式

![image-20231223020052999](assets/img202402272032885.png)

## Spring中的实现

[OAuth2 :: Spring Security](https://docs.spring.io/spring-security/reference/servlet/oauth2/index.html)

**Spring Security**

- 客户应用 (`OAuth2 Client`)：OAuth2客户端功能中包含OAuth2 Login
- 资源服务器 (`OAuth2 Resource Server`)

**Spring**

- 授权服务器 (`Spring Authorization Server`)：它是在Spring Security之上的一个单独的项目。

**相关依赖**：

```xml
<!-- 资源服务器 -->
<dependency>
	<groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>

<!-- 客户应用 -->
<dependency>
	<groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-starter-oauth2-client</artifactId>
</dependency>

<!-- 授权服务器 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-authorization-server</artifactId>
</dependency>
```

## 授权登录的实现思路

使用OAuth2 Login

![image-20231223164128030](assets/img202402282259426.png)

## GitHub社交登录

### 登录流程

1. **A 网站让用户跳转到 GitHub，并携带参数ClientID 以及 Redirection URI。**
2. GitHub 要求用户登录，然后询问用户"A 网站要求获取用户信息的权限，你是否同意？"
3. 用户同意，GitHub 就会重定向回 A 网站，同时发回一个授权码。
4. **A 网站使用授权码，向 GitHub 请求令牌。**
5. GitHub 返回令牌.
6. **A 网站使用令牌，向 GitHub 请求用户数据。**
7. GitHub返回用户数据
8. **A 网站使用 GitHub用户数据登录**

![image-20231223203225688](assets/img202402282302176.png)

### 创建应用

**注册客户应用：**

登录GitHub，在开发者设置中找到OAuth Apps，创建一个application，为客户应用创建访问GitHub的凭据：

![image-20230510154255157](assets/img202402282305358.png)

填写应用信息：`默认的重定向URI模板为{baseUrl}/login/oauth2/code/{registrationId}`。registrationId是ClientRegistration的唯一标识符。

![image-20231221000906168](assets/img202402282311969.png)

获取应用程序id，生成应用程序密钥：

![image-20240228231246355](assets/img202402282312690.png)

### 创建测试项目

创建一个springboot项目oauth2-login-demo，创建时引入如下依赖

![image-20240228231909467](assets/img202402282319935.png)

示例代码参考：[spring-security-samples/servlet/spring-boot/java/oauth2/login at 6.2.x · spring-projects/spring-security-samples (github.com)](https://github.com/spring-projects/spring-security-samples/tree/6.2.x/servlet/spring-boot/java/oauth2/login)

### 配置OAuth客户端属性

application.yml：

```properties
spring:
  security:
    oauth2:
      client:
        registration:
          github:
            client-id: 06146d02b8b57824a934
            client-secret: 65069dcfd21288d79730613b6a93ebf4f84780ae
#            redirectUri: http://localhost:8200/login/oauth2/code/github
```

### 创建Controller

```java
@Controller
public class IndexController {

    @GetMapping("/")
    public String index(
            Model model,
            @RegisteredOAuth2AuthorizedClient OAuth2AuthorizedClient authorizedClient,
            @AuthenticationPrincipal OAuth2User oauth2User) {
        model.addAttribute("userName", oauth2User.getName());
        model.addAttribute("clientName", authorizedClient.getClientRegistration().getClientName());
        model.addAttribute("userAttributes", oauth2User.getAttributes());
        return "index";
    }
}
```

### 创建html页面

resources/templates/index.html

```html
<!DOCTYPE html>
<html
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:th="https://www.thymeleaf.org"
  xmlns:sec="https://www.thymeleaf.org/thymeleaf-extras-springsecurity5"
>
  <head>
    <title>Spring Security - OAuth 2.0 Login</title>
    <meta charset="utf-8" />
  </head>
  <body>
    <div style="float: right" th:fragment="logout" sec:authorize="isAuthenticated()">
      <div style="float:left">
        <span style="font-weight:bold">User: </span><span sec:authentication="name"></span>
      </div>
      <div style="float:none">&nbsp;</div>
      <div style="float:right">
        <form action="#" th:action="@{/logout}" method="post">
          <input type="submit" value="Logout" />
        </form>
      </div>
    </div>
    <h1>OAuth 2.0 Login with Spring Security</h1>
    <div>
      You are successfully logged in
      <span style="font-weight:bold" th:text="${userName}"></span> via the OAuth 2.0 Client
      <span style="font-weight:bold" th:text="${clientName}"></span>
    </div>
    <div>&nbsp;</div>
    <div>
      <span style="font-weight:bold">User Attributes:</span>
      <ul>
        <li th:each="userAttribute : ${userAttributes}">
          <span style="font-weight:bold" th:text="${userAttribute.key}"></span>:
          <span th:text="${userAttribute.value}"></span>
        </li>
      </ul>
    </div>
  </body>
</html>
```

### 启动应用程序

- 启动程序并访问localhost:8080。浏览器将被重定向到默认的自动生成的登录页面，该页面显示了一个用于GitHub登录的链接。
- 点击GitHub链接，浏览器将被重定向到GitHub进行身份验证。
- 使用GitHub账户凭据进行身份验证后，用户会看到授权页面，询问用户是否允许或拒绝客户应用访问GitHub上的用户数据。点击允许以授权OAuth客户端访问用户的基本个人资料信息。
- 此时，OAuth客户端访问GitHub的获取用户信息的接口获取基本个人资料信息，并建立一个已认证的会话。

### CommonOAuth2Provider

CommonOAuth2Provider是一个预定义的通用OAuth2Provider，为一些知名资源服务API提供商（如Google、GitHub、Facebook）预定义了一组默认的属性。

例如，**授权URI、令牌URI和用户信息URI**通常不经常变化。因此，提供默认值以减少所需的配置。

因此，当配置GitHub客户端时，只需要提供client-id和client-secret属性。

```java
GITHUB {
    public ClientRegistration.Builder getBuilder(String registrationId) {
        ClientRegistration.Builder builder = this.getBuilder(
        registrationId,
        ClientAuthenticationMethod.CLIENT_SECRET_BASIC,

        //授权回调地址(GitHub向客户应用发送回调请求，并携带授权码)
		"{baseUrl}/{action}/oauth2/code/{registrationId}");
        builder.scope(new String[]{"read:user"});
        //授权页面
        builder.authorizationUri("https://github.com/login/oauth/authorize");
        //客户应用使用授权码，向 GitHub 请求令牌
        builder.tokenUri("https://github.com/login/oauth/access_token");
        //客户应用使用令牌向GitHub请求用户数据
        builder.userInfoUri("https://api.github.com/user");
        //username属性显示GitHub中获取的哪个属性的信息
        builder.userNameAttributeName("id");
        //登录页面超链接的文本
        builder.clientName("GitHub");
        return builder;
    }
},
```
