# Spring Security 其他配置

## 默认配置

在SecurityConfiguration中添加如下配置：

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    //authorizeRequests()：开启授权保护
    //anyRequest()：对所有请求开启授权保护
    //authenticated()：已认证请求会自动被授权
    http
        .authorizeRequests(authorize ->
                           authorize
                           .anyRequest() //对所有请求开启授权保护
                           .authenticated() //已认证的请求会被自动授权
                          )
        .formLogin(withDefaults())//使用表单授权方式
        //.formLogin().permitAll()  //允许表单登录 permit：允许
        .httpBasic(withDefaults());//使用基本授权方式
    return http.build();
}
```

## 密码加密

密码加密一般使用散列函数，又称散列算法，哈希函数，这些函数都是单向函数 (从明文到密文，反之不行)

**常用的散列算法**：MD5和SHA

Spring Security提供多种密码加密方案，基本上都实现了PasswordEncoder接口，官方推荐使用BCryptPasswordEncoder

**官方文档：**[Password Storage :: Spring Security](https://docs.spring.io/spring-security/reference/features/authentication/password-storage.html)

### 密码加密方式

#### 明文密码

最初，密码以明文形式存储在数据库中。但是恶意用户可能会通过SQL注入等手段获取到明文密码，或者程序员将数据库数据泄露的情况也可能发生。

---

#### Hash算法

Spring Security的`PasswordEncoder`接口用于对密码进行**单向转换**，从而将密码安全地存储。对密码单向转换需要用到**哈希算法**，例如MD5、SHA-256、SHA-512等，哈希算法是单向的，**只能加密，不能解密**。

因此，**数据库中存储的是单向转换后的密码**，Spring Security在进行用户身份验证时需要将用户输入的密码进行单向转换，然后与数据库的密码进行比较。

因此，如果发生数据泄露，只有密码的单向哈希会被暴露。由于哈希是单向的，并且在给定哈希的情况下只能通过**暴力破解的方式猜测密码**。

---

#### 彩虹表

恶意用户创建称为**彩虹表**的查找表。

彩虹表就是一个庞大的、针对各种可能的字母组合预先生成的哈希值集合，有了它可以快速破解各类密码。越是复杂的密码，需要的彩虹表就越大，主流的彩虹表都是100G以上，目前主要的算法有LM, NTLM, MD5, SHA1, MYSQLSHA1, HALFLMCHALL, NTLMCHALL, ORACLE-SYSTEM, MD5-HALF。

---

#### 加盐密码

为了减轻彩虹表的效果，开发人员开始使用加盐密码。不再只使用密码作为哈希函数的输入，而是为每个用户的密码生成随机字节（称为盐）。盐和用户的密码将一起经过哈希函数运算，生成一个唯一的哈希。盐将以明文形式与用户的密码一起存储。然后，当用户尝试进行身份验证时，盐和用户输入的密码一起经过哈希函数运算，再与存储的密码进行比较。唯一的盐意味着彩虹表不再有效，因为对于每个盐和密码的组合，哈希都是不同的。

---

#### 自适应单向函数

随着硬件的不断发展，加盐哈希也不再安全。原因是，计算机可以每秒执行数十亿次哈希计算。这意味着可以轻松地破解每个密码。

现在，开发人员开始使用自适应单向函数来存储密码。使用自适应单向函数验证密码时，**故意占用资源（故意使用大量的CPU、内存或其他资源）**。自适应单向函数允许配置一个“**工作因子**”，随着硬件的改进而增加。我们建议将“工作因子”调整到系统中验证密码需要约一秒钟的时间。这种权衡是为了**让攻击者难以破解密码**。

自适应单向函数包括bcrypt、PBKDF2、scrypt和argon2。

---

### PasswordEncoder

#### BCryptPasswordEncoder

使用广泛支持的bcrypt算法来对密码进行哈希。为了增加对密码破解的抵抗力，bcrypt故意设计得较慢。和其他自适应单向函数一样，应该调整其参数，使其在您的系统上验证一个密码大约需要1秒的时间。BCryptPasswordEncoder的默认实现使用强度10。建议您在自己的系统上调整和测试强度参数，以便验证密码时大约需要1秒的时间。

#### Argon2PasswordEncoder

使用Argon2算法对密码进行哈希处理。Argon2是密码哈希比赛的获胜者。为了防止在自定义硬件上进行密码破解，Argon2是一种故意缓慢的算法，需要大量内存。与其他自适应单向函数一样，它应该在您的系统上调整为大约1秒来验证一个密码。当前的Argon2PasswordEncoder实现需要使用BouncyCastle库。

#### Pbkdf2PasswordEncoder

使用PBKDF2算法对密码进行哈希处理。为了防止密码破解，PBKDF2是一种故意缓慢的算法。与其他自适应单向函数一样，它应该在您的系统上调整为大约1秒来验证一个密码。当需要FIPS认证时，这种算法是一个很好的选择。

![image-20230421184645177](assets/img202402141725392.png)

#### SCryptPasswordEncoder

使用scrypt算法对密码进行哈希处理。为了防止在自定义硬件上进行密码破解，scrypt是一种故意缓慢的算法，需要大量内存。与其他自适应单向函数一样，它应该在您的系统上调整为大约1秒来验证一个密码。

### 密码加密测试

在测试类中编写一个测试方法

```java
@Test
void testPassword() {

    // 工作因子，默认值是10，最小值是4，最大值是31，值越大运算速度越慢
    PasswordEncoder encoder = new BCryptPasswordEncoder(4);
    //明文："password"
    //密文：result，即使明文密码相同，每次生成的密文也不一致
    String result = encoder.encode("password");
    System.out.println(result);

    //密码校验
    Assert.isTrue(encoder.matches("password", result), "密码不一致");
}
```

### DelegatingPasswordEncoder

表中存储的密码形式：`{bcrypt}`$2a$10$GRLdNijSQMUvl/au9ofL.eDwmoohzzS7.rmNSJZ.0FxO/BTk76klW

通过如下源码可以知道：可以通过`{bcrypt}`前缀动态获取和密码的形式类型一致的PasswordEncoder对象

目的：方便随时做密码策略的升级，兼容数据库中的老版本密码策略生成的密码

![image-20231209011827867](assets/img202402141727236.png)

### 指定加密方式

在配置用户信息的时候，报了黄标，实际上这种方式存储密码并不安全：

![image-20230920183415087](assets/202309201834683.png)

SpringSecurity的密码校验不推荐直接使用原文进行比较，而是使用加密算法将密码进行加密 (进行Hash处理，此过程是不可逆的，无法解密)，最后将用户提供的密码以同样的方式加密后与密文进行比较。用户提供的密码属于隐私信息，直接明文存储并不好，而且如果数据库内容被窃取，那么所有用户的密码将全部泄露，这是不希望看到的结果，需要一种既能隐藏用户密码也能完成认证的机制，而Hash处理就是一种很好的解决方案，通过将用户的密码进行Hash值计算，计算出来的结果一般是单向的，无法还原为原文，如果需要验证是否与此密码一致，那么需要以同样的方式加密再比较两个Hash值是否一致，这样就很好的保证了用户密码的安全性。

在配置用户信息的时候，可以使用官方提供的BCrypt加密工具：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

  	//这里将BCryptPasswordEncoder直接注册为Bean，Security会自动进行选择
    @Bean
    public PasswordEncoder passwordEncoder(){
        return new BCryptPasswordEncoder();
    }

    @Bean
    public UserDetailsService userDetailsService(PasswordEncoder encoder) {
        UserDetails user = User
                .withUsername("user")
                .password(encoder.encode("password"))   //这里将密码进行加密后存储
                .roles("USER")
                .build();
      	System.out.println(encoder.encode("password"));  //一会观察一下加密出来之后的密码长啥样
        UserDetails admin = User
                .withUsername("admin")
                .password(encoder.encode("password"))   //这里将密码进行加密后存储
                .roles("ADMIN", "USER")
                .build();
        return new InMemoryUserDetailsManager(user, admin);
    }
}
```

这样，存储的密码就是更加安全的密码了：

![image-20230702152150157](assets/202309201839213.png)

![image-20230702152216162](assets/img202402241742501.png)

## CSRF防护

从Spring Security 4.0开始，默认情况下Spring Security会启用CSRF攻击防御保护，以防止CSRF攻击应用程序，Spring Security CSRF会针对PATCH，POST，PUT和DELETE方法的请求（不仅仅只是登陆请求，这里指的是任何请求路径）进行防护，而这里的登陆表单正好是一个POST类型的请求。在默认配置下，无论是否登陆，页面中只要发起了PATCH，POST，PUT和DELETE请求一定会被拒绝，并返回**403错误**，需要在请求的时候加入csrfToken才行，也就是"83421936-b84b-44e3-be47-58bb2c14571a"，正是csrfToken，如果提交的是表单类型的数据，那么表单中必须包含此Token字符串，键名称为"\_csrf"；如果是JSON数据格式发送的，那么就需要在请求头中包含此Token字符串。

默认情况下开启了csrf的功能，需要在POST请求中携带页面中的csrfToken才可以，否则一律进行拦截操作：

![image-20230920185515712](assets/202309201855228.png)

实际上现在的浏览器已经很安全了，完全不需要使用自带的csrf防护。

### 添加字段

将请求参数中必须有一个隐藏的`_csrf`字段可以将其嵌入到页面中：

```html
<input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
```

接着在axios发起请求时，携带这个input的value值：

```js
function pay() {
    const account = document.getElementById("account").value
    const csrf = document.getElementById("_csrf").value
    axios.post('/mvc/pay', {
        account: account,
        _csrf: csrf   //携带此信息即可，否则会被拦截
    }, {
      ...
```

如果遇到那种需要再form表单中提交的情况，也可以直接像下面这样给塞到表单里：

```html
<form action="/xxxx" method="post">
  ...
  <input type="text" th:name="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
  ...
</form>
```

### 关闭CSRF防护

可以通过配置关闭csrf防护：

在filterChain方法中添加如下代码，关闭csrf攻击防御

```java
@Configuration
@EnableWebSecurity   //开启WebSecurity相关功能
public class SecurityConfiguration {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        //authorizeRequests()：开启授权保护
        //anyRequest()：对所有请求开启授权保护
        //authenticated()：已认证请求会自动被授权
        return http.authorizeHttpRequests(authorize ->
                        authorize.anyRequest() //对所有请求开启授权保护
                                .authenticated()) //已认证的请求会被自动授权
                .formLogin(withDefaults())//使用表单授权方式
                .httpBasic(withDefaults())//使用基本授权方式
				//关闭csrf攻击防御
                .csrf(conf -> {
                    conf.disable();   //此方法可以直接关闭全部的csrf校验，一步到位
                    conf.ignoringRequestMatchers("/xxx/**");   //此方法可以根据情况忽略某些地址的csrf校验
                })
                .build();
    }
}
```

## 跨域

### 手动实现跨域

使用过滤器来解决跨域：

```java
/**
 * 跨域配置过滤器，仅处理跨域，添加跨域响应头
 */
@Component
@Order(-102) //优先级高于过滤器链
public class AjaxCorsFilter extends HttpFilter {
    @Value("${spring.web.cors.origin}")
    String origin;

    @Value("${spring.web.cors.credentials}")
    boolean credentials;

    @Value("${spring.web.cors.methods}")
    String methods;

    @Override
    protected void doFilter(HttpServletRequest request, HttpServletResponse response, FilterChain chain) throws IOException, ServletException {
        this.addCorsHeader(request, response);
        chain.doFilter(request, response);
    }

    /**
     * 添加所有跨域相关响应头
     * @param request 请求
     * @param response 响应
     */
    private void addCorsHeader(HttpServletRequest request, HttpServletResponse response) {
        response.addHeader("Access-Control-Allow-Origin", this.resolveOrigin(request));
        response.addHeader("Access-Control-Allow-Methods", this.resolveMethod());
        response.addHeader("Access-Control-Allow-Headers", "Authorization, Content-Type");
        if(credentials) {
            response.addHeader("Access-Control-Allow-Credentials", "true");
        }
    }

    /**
     * 解析配置文件中的请求方法
     * @return 解析得到的请求头值
     */
    private String resolveMethod(){
        return methods.equals("*") ? "GET, HEAD, POST, PUT, DELETE, OPTIONS, TRACE, PATCH" : methods;
    }

    /**
     * 解析配置文件中的请求原始站点
     * @param request 请求
     * @return 解析得到的请求头值
     */
    private String resolveOrigin(HttpServletRequest request){
        return origin.equals("*") ? request.getHeader("Origin") : origin;
    }
}
```

> application.yaml

```yaml
spring:
  security:
    filter:
      order: -100
  web:
    cors:
      origin: '*'
      credentials: false
      methods: '*'
```

## 自定义登录界面

虽然SpringSecurity提供了一个登录界面，但是很多情况下往往都是使用自定义的登录界面，这个时候就需要进行更多的配置了。

下载好模版将其中的两个页面和资源文件放到resource路径下：

![image-20240214203737155](assets/img202402241548026.png)

设置静态资源访问路径：

```yaml
spring:
  mvc:
    static-path-pattern: /static/**
```

配置对应页面的Controller控制器：

```java
@Controller
public class HelloController {
    @GetMapping("/")
    public String index(){
        return "index";
    }

    @GetMapping("/login")
    public String login(){
        return "login";
    }
}
```

在登录之后，就可以展示前端模版页面了：

![image-20240214203653899](assets/img202402241550384.png)

不过现在依然是默认进入到SpringSecurity默认的登录界面，需要配置自定义的登录界面，将前端模版中的登录页面作为SpringSecurity的默认登录界面。

```java
@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

  	...

	//如果你学习过SpringSecurity 5.X版本，可能会发现新版本的配置方式完全不一样
    //新版本全部采用lambda形式进行配置，无法再使用之前的and()方法进行连接了
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                //以下是验证请求拦截和放行配置
                .authorizeHttpRequests(auth -> {
                    auth.anyRequest().authenticated();    //将所有请求全部拦截，一律需要验证
                })
                //以下是表单登录相关配置
                .formLogin(conf -> {
                    conf.loginPage("/login"); //将登录页设置为我们自己的登录页面
                    conf.failureUrl("/login?error"); //登录失败的返回地址
                    conf.loginProcessingUrl("/doLogin"); //登录表单提交的地址，可以自定义
                    conf.defaultSuccessUrl("/");   //登录成功后跳转的页面
                    conf.permitAll();    //将登录相关的地址放行，否则未登录的用户连登录界面都进不去
                  	//用户名和密码的表单字段名称，不过默认就是这个，可以不配置，除非有特殊需求
                    conf.usernameParameter("username");
                    conf.passwordParameter("password");
                })
                .build();
    }
}
```

需要配置登陆页面的地址和登陆请求发送的地址，这里登陆页面填写为`/login`，登陆请求地址为`/doLogin`，登陆页面我们刚刚已经自己编写Controller来实现了，登陆请求提交处理由SpringSecurity提供，只需要写路径就可以了。现在访问我们的网站，就可以进入到自定义的登录界面了：

![image-20240214204242509](assets/img202402241551070.png)

但是页面只有一个纯文本，这是因为在获取静态资源的时候，所有的静态资源默认情况下也会被拦截，因此全部被302重定向到登录页面，这显然是不对的：

![image-20230703184641792](assets/img202402241551907.png)

因此，需要将所有的静态资源也给放行，否则登录界面都没法正常展示：

```java
.authorizeHttpRequests(auth -> {
      auth.requestMatchers("/static/**").permitAll();   //将所有的静态资源放行，一定要添加在全部请求拦截之前
      auth.anyRequest().authenticated();    //将所有请求全部拦截，一律需要验证
})
```

更改静态资源路径：

![image-20240214204903953](assets/img202402241551010.png)

再次访问网站，就可以看到正常显示的登录界面了：

![image-20230703185027927](assets/img202402241551037.png)

因此，在编写项目过程中发现有302的情况，一定要先检查是否因为没有放行导致被SpringSecurity给拦截。

接着配置登录操作，这里只需要配置一下登录的地址和登录按钮即可，当然，跟之前一样，要把CSRF的输入框也加上：

```html
<form action="doLogin" method="post">
  ...
  <input type="text" name="username" placeholder="Email Address" class="ad-input" />
  ...
  <input type="password" name="password" placeholder="Password" class="ad-input" />
  ...
  <input type="text" th:name="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
  <div class="ad-auth-btn">
    <button type="submit" class="ad-btn ad-login-member">Login</button>
  </div>
  ...
</form>
```

接着就可以尝试进行登录操作了：

![image-20230703185916404](assets/img202402241552038.png)

可以看到，现在可以成功地登录到主页了。

退出登录也是同样的操作，只需要稍微进行一下配置就可以实现，首先继续完善配置类：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

    ...

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                ...
                //以下是退出登录相关配置
                .logout(conf -> {
                    conf.logoutUrl("/doLogout");   //退出登录地址，跟上面一样可自定义
                    conf.logoutSuccessUrl("/login");  //退出登录成功后跳转的地址，这里设置为登录界面
                    conf.permitAll();
                })
                .build();
    }
}
```

接着修改页面中的退出登录按钮：

```html
<li>
  <form action="doLogout" method="post">
    <input type="text" th:name="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
    <button type="submit"><i class="fas fa-sign-out-alt"></i> logout</button>
  </form>
</li>
```

现在点击右上角的退出按钮就可以退出了：

![image-20230703190714519](assets/img202402241552802.png)

现在无论提交什么请求都需要Csrf校验，有些太麻烦了，实际上现在浏览器已经很安全了，没必要防御到这种程度，可以直接在配置中关闭csrf校验：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

   	...

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                ...
                //以下是csrf相关配置
                .csrf(conf -> {
                    conf.disable();   //此方法可以直接关闭全部的csrf校验，一步到位
                    conf.ignoringRequestMatchers("/xxx/**");   //此方法可以根据情况忽略某些地址的csrf校验
                })
                .build();
    }
}
```

这样，就不需要再往页面中嵌入CSRF相关的输入框了，发送请求时也不会进行校验，至此，就完成了简单的自定义登录界面配置。

## 记住我功能

记住我功能可以在登陆之后的一段时间内，无需再次输入账号和密码进行登陆，相当于服务端已经记住当前用户，再次访问时就可以免登陆进入，这是一个非常常用的功能。

使用本地Cookie存储的方式实现了记住我功能，但是这种方式并不安全，同时在代码编写上也比较麻烦。

SpringSecurity提供了一种优秀的实现，它为每个已经登陆的浏览器分配一个携带Token的Cookie，并且此Cookie默认会被保留14天，只要我们不清理浏览器的Cookie，那么下次携带此Cookie访问服务器将无需登陆，直接继续使用之前登陆的身份，这样显然比之前的写法更加简便。并且我们需要进行简单配置，即可开启记住我功能：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

    ...

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                ...
                .rememberMe(conf -> {
                    conf.alwaysRemember(false);  //这里不要开启始终记住，我们需要配置为用户自行勾选
                    conf.rememberMeParameter("remember-me");   //记住我表单字段，默认就是这个，可以不配置
                    conf.rememberMeCookieName("xxxx");  //记住我设置的Cookie名字，也可以自定义，不过没必要
                })
                .build();
    }
}
```

配置完成后，需要修改一下前端页面中的表单，将记住我勾选框也作为表单的一部分进行提交：

```html
<div class="ad-checkbox">
  <label>
    <input type="checkbox" name="remember-me" class="ad-checkbox" />
    <span>Remember Me</span>
  </label>
</div>
```

接着来尝试勾选记住我选项进行登录：

![image-20230704211415804](assets/3wOt7CldbFP8yHz.png)

此时提交的表单中就已经包含记住我字段了，会发现，服务端返回给了一个记住我专属的Cookie信息：

![image-20230704211611369](assets/NB129h7IKRycXvL.png)

这个Cookie信息的过期时间并不是仅会话，而是默认保存一段时间，因此，关闭浏览器后下次再次访问网站时，就不需要再次进行登录操作了，而是直接继续上一次的登录状态。

当然，由于记住我信息是存放在内存中的，需要保证服务器一直处于运行状态，如果关闭服务器的话，记住我信息会全部丢失，因此，如果希望记住我能够一直持久化保存，就需要进一步进行配置。我们需要创建一个基于JDBC的TokenRepository实现：

```java
@Bean
public PersistentTokenRepository tokenRepository(DataSource dataSource){
    JdbcTokenRepositoryImpl repository = new JdbcTokenRepositoryImpl();
  	//在启动时自动在数据库中创建存储记住我信息的表，仅第一次需要，后续不需要
    repository.setCreateTableOnStartup(true);
    repository.setDataSource(dataSource);
    return repository;
}
```

然后添加此仓库：

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http,PersistentTokenRepository repository) throws Exception {
        return http
                .rememberMe(conf -> {
                    conf.alwaysRemember(false);  //这里不要开启始终记住，需要配置为用户自行勾选
                    conf.rememberMeParameter("remember-me");
                    conf.tokenRepository(repository);      //设置刚刚的记住我持久化存储库
                    conf.tokenValiditySeconds(3600 * 7);   //设置记住我有效时间为7天
                })
                .build();
    }
```

这样，就成功配置了数据库持久化存储记住我信息，即使重启服务器也不会导致数据丢失。当登录之后，数据库中会自动记录相关的信息：

![img202402241555985](assets/img202402241555985-174384601893140.png)

这样，网站的登录系统就更加完善了。

## 用户认证信息

在Spring Security框架中，SecurityContextHolder、SecurityContext、Authentication、Principal和Credential是一些与身份验证和授权相关的重要概念。它们之间的关系如下：

1. SecurityContextHolder：SecurityContextHolder 是 Spring Security 存储已认证用户详细信息的地方。
2. SecurityContext：SecurityContext 是从 SecurityContextHolder 获取的内容，包含当前已认证用户的 Authentication 信息。
3. Authentication：Authentication 表示用户的身份认证信息。它包含了用户的Principal、Credential和Authority信息。
4. Principal：表示用户的身份标识。它通常是一个表示用户的实体对象 (UserDetails)，例如用户名。Principal可以通过Authentication对象的getPrincipal()方法获取。
5. Credentials：表示用户的凭证信息，例如密码、证书或其他认证凭据。Credential可以通过Authentication对象的getCredentials()方法获取。
6. GrantedAuthority：表示用户被授予的权限

总结起来，SecurityContextHolder用于管理当前线程的安全上下文，存储已认证用户的详细信息，其中包含了SecurityContext对象，该对象包含了Authentication对象，后者表示用户的身份验证信息，包括Principal（用户的身份标识）和Credential（用户的凭证信息）。

![img202402241742176](assets/img202402241742176-174384603352642.png)

在Controller中获取用户信息：

> IndexController

```java
@RestController
public class IndexController {

    @GetMapping("/")
    public Map index(){

        System.out.println("index controller");

        SecurityContext context = SecurityContextHolder.getContext();//存储认证对象的上下文
        Authentication authentication = context.getAuthentication();//认证对象
        String username = authentication.getName();//用户名
        Object principal =authentication.getPrincipal();//身份 定义认证的而用户，如果用户使用用户名和密码方式登录，principal通常就是一个UserDetails
        Object credentials = authentication.getCredentials();//凭证(脱敏) 登录凭证，一般就是指密码。当用户登录成功之后，登录凭证会被自动擦除，以方式泄露。
        Collection<? extends GrantedAuthority> authorities = authentication.getAuthorities();//权限

        System.out.println(username);
        System.out.println(principal);
        System.out.println(credentials);
        System.out.println(authorities);

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", 0);
        result.put("data", username);

        return result;
    }
}
```

在Spring中该对象已经被注册到容器中，可以直接获取该对象：

```java
@RestController
public class CurrentLoginUserInfoController {

    /**
     * 从当前请求对象中获取
     */
    @GetMapping("/getLoginUserInfo")
    public Principal getLoginUserInfo(Principal principle){
            return principle;
    }
    /**
     *从当前请求对象中获取
     */
    @GetMapping("/getLoginUserInfo1")
    public Authentication getLoginUserInfo1(Authentication authentication){
        return authentication;
    }

    /**
     * 从SecurityContextHolder获取
     * @return
     */
    @GetMapping("/getLoginUserInfo2")
    public Authentication getLoginUserInfo(){
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        return authentication;
    }
}
```

## 会话并发处理

后登录的账号会使先登录的账号失效

**实现处理器接口**：

实现接口SessionInformationExpiredStrategy

```java
public class MySessionInformationExpiredStrategy implements SessionInformationExpiredStrategy {
    @Override
    public void onExpiredSessionDetected(SessionInformationExpiredEvent event) throws IOException, ServletException {

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", -1);
        result.put("message", "该账号已从其他设备登录");

        //转换成json字符串
        String json = JSON.toJSONString(result);

        HttpServletResponse response = event.getResponse();
        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    }
}
```

**SecurityFilterChain配置**：

```java
//会话管理
http.sessionManagement(session -> {
    session
        .maximumSessions(1) //设置会话的最大数量为1，即同一账号只能同时登录一个设备
        .expiredSessionStrategy(new MySessionInformationExpiredStrategy());
});
```

当使用无状态的JWT方案时，不需要维护Session (JWT控制)，所以需要将会话处理为无状态：

```java
http.sessionManagement(session -> {
	session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
});
```
