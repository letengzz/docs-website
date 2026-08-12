# Spring Security 其他配置

## 自定义登录界面

虽然SpringSecurity提供了一个登录界面，但是很多情况下往往都是使用自定义的登录界面，这个时候就需要进行更多的配置了。

下载好模版将其中的两个页面和资源文件放到类路径下(配置静态资源)：

![image-20230703180438190](https://s2.loli.net/2023/07/03/hpZs1DLESojHJue.png)

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

![image-20230703182321093](https://s2.loli.net/2023/07/03/Zns4Vwb7zPLc6SQ.png)

不过现在依然是默认进入到SpringSecurity默认的登录界面，现在我们来配置自定义的登录界面，将我们的前端模版中的登录页面作为SpringSecurity的默认登录界面。

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
                    conf.loginPage("/login");   //将登录页设置为我们自己的登录页面
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

![image-20230703184425313](https://s2.loli.net/2023/07/03/c38kewdxtn1j2V6.png)

但是我们发现，我们的页面只有一个纯文本，这是因为在获取静态资源的时候，所有的静态资源默认情况下也会被拦截，因此全部被302重定向到登录页面，这显然是不对的：

![image-20230703184641792](https://s2.loli.net/2023/07/03/6vXlPZprzjJLEeq.png)

因此，现在我们需要将所有的静态资源也给放行，否则登录界面都没法正常展示：

```java
.authorizeHttpRequests(auth -> {
      auth.requestMatchers("/static/**").permitAll();   //将所有的静态资源放行，一定要添加在全部请求拦截之前
      auth.anyRequest().authenticated();    //将所有请求全部拦截，一律需要验证
})
```

再次访问我们的网站，就可以看到正常显示的登录界面了：

![image-20230703185027927](https://s2.loli.net/2023/07/03/LmZbihzD4vYB5GF.png)

因此，如果各位小伙伴后续在编写项目过程中发现有302的情况，一定要先检查是否因为没有放行导致被SpringSecurity给拦截了，别再遇到302一脸懵逼了。

接着我们来配置登录操作，这里我们只需要配置一下登录的地址和登录按钮即可，当然，跟之前一样，要把CSRF的输入框也加上：

```html
<form action="doLogin" method="post">
		...
  <input type="text" name="username" placeholder="Email Address" class="ad-input">
  ...
  <input type="password" name="password" placeholder="Password" class="ad-input">
  ...
  <input type="text" th:name="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden>
  <div class="ad-auth-btn">
     <button type="submit" class="ad-btn ad-login-member">Login</button>
  </div>
	...
</form>
```

接着我们就可以尝试进行登录操作了：

![image-20230703185916404](https://s2.loli.net/2023/07/03/P2LS8uNRQ64WEvT.png)

可以看到，现在我们可以成功地登录到主页了。

退出登录也是同样的操作，我们只需要稍微进行一下配置就可以实现，我们首先继续完善配置类：

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

接着我们来稍微魔改一下页面中的退出登录按钮：

```html
<li>
   <form action="doLogout" method="post">
        <input type="text" th:name="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden>
        <button type="submit">
           <i class="fas fa-sign-out-alt"></i> logout
        </button>
   </form>
</li>
```

现在我们点击右上角的退出按钮就可以退出了：

![image-20230703190714519](https://s2.loli.net/2023/07/03/yM8TOAxYPf3iqFs.png)

不过，可能会有小伙伴觉得，我们现在无论提交什么请求都需要Csrf校验，有些太麻烦了，实际上现在浏览器已经很安全了，没必要防御到这种程度，我们也可以直接在配置中关闭csrf校验：

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

这样，我们就不需要再往页面中嵌入CSRF相关的输入框了，发送请求时也不会进行校验，至此，我们就完成了简单的自定义登录界面配置。

## 记住我功能

我们的网站还有一个重要的功能，就是记住我，也就是说我们可以在登陆之后的一段时间内，无需再次输入账号和密码进行登陆，相当于服务端已经记住当前用户，再次访问时就可以免登陆进入，这是一个非常常用的功能。

使用本地Cookie存储的方式实现了记住我功能，但是这种方式并不安全，同时在代码编写上也比较麻烦。

SpringSecurity为我们提供了一种优秀的实现，它为每个已经登陆的浏览器分配一个携带Token的Cookie，并且此Cookie默认会被保留14天，只要我们不清理浏览器的Cookie，那么下次携带此Cookie访问服务器将无需登陆，直接继续使用之前登陆的身份，这样显然比我们之前的写法更加简便。并且我们需要进行简单配置，即可开启记住我功能：

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

配置完成后，我们需要修改一下前端页面中的表单，将记住我勾选框也作为表单的一部分进行提交：

```html
<div class="ad-checkbox">
    <label>
        <input type="checkbox" name="remember-me" class="ad-checkbox">
        <span>Remember Me</span>
    </label>
</div>
```

接着我们来尝试勾选记住我选项进行登录：

![image-20230704211415804](https://s2.loli.net/2023/07/04/3wOt7CldbFP8yHz.png)

此时提交的表单中就已经包含记住我字段了，我们会发现，服务端返回给我们了一个记住我专属的Cookie信息：

![image-20230704211611369](https://s2.loli.net/2023/07/04/NB129h7IKRycXvL.png)

这个Cookie信息的过期时间并不是仅会话，而是默认保存一段时间，因此，我们关闭浏览器后下次再次访问网站时，就不需要我们再次进行登录操作了，而是直接继续上一次的登录状态。

当然，由于记住我信息是存放在内存中的，我们需要保证服务器一直处于运行状态，如果关闭服务器的话，记住我信息会全部丢失，因此，如果我们希望记住我能够一直持久化保存，我们就需要进一步进行配置。我们需要创建一个基于JDBC的TokenRepository实现：

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
.rememberMe(conf -> {
     conf.rememberMeParameter("remember-me");
     conf.tokenRepository(repository);      //设置刚刚的记住我持久化存储库
     conf.tokenValiditySeconds(3600 * 7);   //设置记住我有效时间为7天
})
```

这样，我们就成功配置了数据库持久化存储记住我信息，即使我们重启服务器也不会导致数据丢失。当我们登录之后，数据库中会自动记录相关的信息：

![image-20230704220701000](https://s2.loli.net/2023/07/04/kIJpuWdiEGqUKBx.png)

这样，我们网站的登录系统就更加完善了。