# Spring Security 认证

认证是网站的第一步，用户需要登录之后才能进入，使用SpringSecurity实现用户登录。

系统认证是为了保护系统的隐私数据与资源，用户的身份合法方可访问该系统的资源。

**认证**：用户认证就是判断一个用户的身份是否合法的过程。

**常见的用户身份认证方式**：

- 用户名密码登录

- 二维码登录

- 手机短信登录

- 指纹认证

- 人脸识别

- 等等...

## 基于内存验证

### 配置登录

基于内存的配置，也就是说直接以代码的形式配置网站的用户和密码，配置方式非常简单，只需要在Security配置类中注册一个Bean即可：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

    @Bean   //UserDetailsService就是获取用户信息的服务
    public UserDetailsService userDetailsService() {
      	//每一个UserDetails就代表一个用户信息，其中包含用户的用户名和密码以及角色
        UserDetails user = User.withDefaultPasswordEncoder()
                .username("user")
                .password("password")
                .roles("USER")  //角色目前我们不需要关心，随便写就行，后面会专门讲解
                .build();
        UserDetails admin = User.withDefaultPasswordEncoder()
                .username("admin")
                .password("password")
                .roles("ADMIN", "USER")
                .build();
        return new InMemoryUserDetailsManager(user, admin);
      	//创建一个基于内存的用户信息管理器作为UserDetailsService
    }
}
```

配置完成后就可以前往登录界面，进行登录操作了：

![img](assets/tSGxZmv6jUDMy95.png)

登录成功后，就可以访问到之前的界面了：

![image-20230920183027051](assets/202309201830297.png)

并且为了防止会话固定问题，在登录之后，JSESSIONID会得到重新分配：

![image-20230703192441811](https://s2.loli.net/2023/07/03/mQpWZMljCt2XTd7.png)

### 退出登录

当退出时，也可以直接访问：http://localhost:8080/logout 地址，会进入到一个退出登录界面：

![image-20230920183136259](assets/202309201831588.png)

退出登录后需要重新登录才能访问网站。

可以发现，在有了SpringSecurity之后，网站的登录验证模块相当于直接被接管了，因此，从现在开始，网站不需要再自己编写登录模块了，这里我可以直接去掉，只留下主页面。

### 密码加密

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

![image-20230702152216162](assets/img202402241612376.png)

### CSRF防护

SpringSecurity自带了csrf防护，需求我们在POST请求中携带页面中的csrfToken才可以，否则一律进行拦截操作：

![image-20230920185515712](assets/202309201855228.png)

可以将其嵌入到页面中，随便找一个地方添加以下内容：

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

实际上现在的浏览器已经很安全了，完全不需要使用自带的csrf防护，后面可以通过配置关闭csrf防护。

> 从Spring Security 4.0开始，默认情况下会启用CSRF保护，以防止CSRF攻击应用程序，Spring Security CSRF会针对PATCH，POST，PUT和DELETE方法的请求（不仅仅只是登陆请求，这里指的是任何请求路径）进行防护，而这里的登陆表单正好是一个POST类型的请求。在默认配置下，无论是否登陆，页面中只要发起了PATCH，POST，PUT和DELETE请求一定会被拒绝，并返回**403错误**，需要在请求的时候加入csrfToken才行，也就是"83421936-b84b-44e3-be47-58bb2c14571a"，正是csrfToken，如果提交的是表单类型的数据，那么表单中必须包含此Token字符串，键名称为"\_csrf"；如果是JSON数据格式发送的，那么就需要在请求头中包含此Token字符串。

## 基于数据库验证

官方默认提供了可以直接使用的用户和权限表设计，根本不需要来建表，直接在Navicat中执行以下查询：

```sql
create table users(username varchar(50) not null primary key,password varchar(500) not null,enabled boolean not null);
create table authorities (username varchar(50) not null,authority varchar(50) not null,constraint fk_authorities_users foreign key(username) references users(username));
create unique index ix_auth_username on authorities (username,authority);
```

添加Mybatis-plus和MySQL相关的依赖：

```xml
<dependency>
	<groupId>com.mysql</groupId>
	<artifactId>mysql-connector-j</artifactId>
</dependency>
<dependency>
	<groupId>com.baomidou</groupId>
	<artifactId>mybatis-plus-boot-starter</artifactId>
	<version>3.5.5</version>
</dependency>
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
</dependency>
<dependency>
    <groupId>com.alibaba.fastjson2</groupId>
    <artifactId>fastjson2</artifactId>
    <version>2.0.43</version>
</dependency>
```

配置数据源：

> src/main/resources/application.yaml

```yaml
# MySQL 数据源
spring:
  datasource:
    username: root
    password: 123123
    url: jdbc:mysql://localhost:3306/spring-security
    driver-class-name: com.mysql.cj.jdbc.Driver
#SQL日志
mybatis-plus:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

编写配置类：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

    @Bean
    PasswordEncoder passwordEncoder(){
        return new BCryptPasswordEncoder();
    }

    @Bean
    public UserDetailsService userDetailsService(DataSource dataSource,
                                                 PasswordEncoder encoder) {
        JdbcUserDetailsManager manager = new JdbcUserDetailsManager(dataSource);
      	//仅首次启动时创建一个新的用户用于测试，后续无需创建
   			manager.createUser(User.withUsername("user")
                      .password(encoder.encode("password")).roles("USER").build());
        return manager;
    }
}
```

启动后，可以看到两张表中已经自动添加好对应的数据了：

![image-20230920192814847](assets/202309202211543.png)

直接进行登录，使用方式和之前是完全一样的：

![image-20230702181211157](assets/202309202211352.png)

当下次需要快速创建一个用户登录的应用程序时，直接使用这种方式就能快速完成了。

无论是InMemoryUserDetailsManager还是JdbcUserDetailsManager，都是实现自UserDetailsManager接口，这个接口中有着一套完整的增删改查操作，方便直接对用户进行处理：

```java
public interface UserDetailsManager extends UserDetailsService {

  //创建一个新的用户
	void createUser(UserDetails user);

  //更新用户信息
	void updateUser(UserDetails user);

  //删除用户
	void deleteUser(String username);

  //修改用户密码
	void changePassword(String oldPassword, String newPassword);

  //判断是否存在指定用户
	boolean userExists(String username);
}
```

通过使用UserDetailsManager对象，就能快速执行用户相关的管理操作，比如可以直接在网站上添加一个快速重置密码的接口：

1. 首先需要配置一下JdbcUserDetailsManager，为其添加一个AuthenticationManager用于原密码的校验：

   ```java
   @Configuration
   @EnableWebSecurity
   public class SecurityConfiguration {

       ...

       //手动创建一个AuthenticationManager用于处理密码校验
       private AuthenticationManager authenticationManager(UserDetailsManager manager,
                                                           PasswordEncoder encoder){
           DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
           provider.setUserDetailsService(manager);
           provider.setPasswordEncoder(encoder);
           return new ProviderManager(provider);
       }

       @Bean
       public UserDetailsManager userDetailsService(DataSource dataSource,
                                                    PasswordEncoder encoder) throws Exception {
           JdbcUserDetailsManager manager = new JdbcUserDetailsManager(dataSource);
         	//为UserDetailsManager设置AuthenticationManager即可开启重置密码的时的校验
           manager.setAuthenticationManager(authenticationManager(manager, encoder));
           return manager;
       }
   }
   ```

2. 编写一个快速重置密码的接口：

   ```java
   @Resource
   private UserDetailsManager manager;

   @Resource
   private PasswordEncoder encoder;

   @ResponseBody
   @PostMapping("/change-password")
   public JSONObject changePassword(@RequestParam String oldPassword,
                                    @RequestParam String newPassword) {
       manager.changePassword(oldPassword, encoder.encode(newPassword));
       JSONObject object = new JSONObject();
       object.put("success", true);
       return object;
   }
   ```

3. 在主界面中添加一个重置密码的操作：

   ```html
   <!DOCTYPE html>
   <html lang="en">
     <head>
       <meta charset="UTF-8" />
       <title>首页</title>
       <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
     </head>
     <body>
       <div>
         <label>
           修改密码：
           <input type="text" id="oldPassword" placeholder="旧密码" />
           <input type="text" id="newPassword" placeholder="新密码" />
           <input
             type="text"
             th:id="${_csrf.getParameterName()}"
             th:value="${_csrf.token}"
             hidden
           />
         </label>
         <button onclick="change()">修改密码</button>
       </div>
     </body>
   </html>

   <script>
     function change() {
       const oldPassword = document.getElementById('oldPassword').value
       const newPassword = document.getElementById('newPassword').value
       const csrf = document.getElementById('_csrf').value
       axios
         .post(
           '/change-password',
           {
             oldPassword: oldPassword,
             newPassword: newPassword,
             _csrf: csrf,
           },
           {
             headers: {
               'Content-Type': 'application/x-www-form-urlencoded',
             },
           },
         )
         .then(({ data }) => {
           alert(data.success ? '密码修改成功' : '密码修改失败，请检查原密码是否正确')
         })
     }
   </script>
   ```

这样就可以在首页进行修改密码操作了：

![image-20240212101910122](assets/img202402241612104.png)

当然，这种方式的权限校验虽然能够直接使用数据库，但是存在一定的局限性，只适合快速搭建Demo使用，不适合实际生产环境下编写。

## 自定义验证

有些时候，数据库可能并不会像SpringSecurity默认的那样进行设计，而是采用自定义的表结构，这种情况下，上面两种方式就很难进行验证了，此时需要编写自定义验证，来应对各种任意变化的情况。

既然需要自定义，那么就需要自行实现UserDetailsService或是功能更完善的UserDetailsManager接口。

### 准备工作

创建数据库表并插入测试数据

```sql
-- 创建数据库
CREATE DATABASE `security-demo`;
USE `security-demo`;

-- 创建用户表
CREATE TABLE `user`(
	`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	`username` VARCHAR(50) DEFAULT NULL ,
	`password` VARCHAR(500) DEFAULT NULL,
	`enabled` BOOLEAN NOT NULL
);
-- 唯一索引
CREATE UNIQUE INDEX `user_username_uindex` ON `user`(`username`);

-- 插入用户数据(密码是 "password" )
INSERT INTO `user` (`username`, `password`, `enabled`) VALUES
('admin', '{bcrypt}$2a$10$GRLdNijSQMUvl/au9ofL.eDwmoohzzS7.rmNSJZ.0FxO/BTk76klW', TRUE),
('Helen', '{bcrypt}$2a$10$GRLdNijSQMUvl/au9ofL.eDwmoohzzS7.rmNSJZ.0FxO/BTk76klW', TRUE),
('Tom', '{bcrypt}$2a$10$GRLdNijSQMUvl/au9ofL.eDwmoohzzS7.rmNSJZ.0FxO/BTk76klW', TRUE);
```

添加Mybatis-plus和MySQL相关的依赖：

```xml
<dependency>
	<groupId>com.mysql</groupId>
	<artifactId>mysql-connector-j</artifactId>
</dependency>
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.5</version>
</dependency>
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
</dependency>
<dependency>
    <groupId>com.alibaba.fastjson2</groupId>
    <artifactId>fastjson2</artifactId>
    <version>2.0.43</version>
</dependency>
```

配置数据源：

> src/main/resources/application.yaml

```yaml
# MySQL 数据源
spring:
  datasource:
    username: root
    password: 123123
    url: jdbc:mysql://localhost:3306/security-demo
    driver-class-name: com.mysql.cj.jdbc.Driver
#SQL日志
mybatis-plus:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

创建实体类：

> src/main/java/com/hjc/demo/entity/User.java

```java
@Data
public class User {
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private String username;

    private String password;

    private Boolean enabled;
}
```

创建Mapper接口：

> src/main/java/com/hjc/demo/mapper/UserMapper.java

```java
@Mapper
public interface UserMapper extends BaseMapper<User> {
}
```

> src/main/resources/mapper/UserMapper.xml

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.hjc.demo.mapper.UserMapper">

</mapper>
```

创建Service 接口及实现类：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService extends IService<User> {
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
}
```

创建Controller：

> src/main/java/com/hjc/demo/controller/UserController.java

```java
@RestController
@RequestMapping("/user")
public class UserController {

    @Resource
    public UserService userService;

    @GetMapping("/list")
    public List<User> getList(){
        return userService.list();
    }
}
```

启动并访问：http://localhost:8080/user/list

![image-20240212141018383](assets/img202402241612365.png)

### 实现 UserDetailsService

可以直接选择UserDetailsService进行实现：

```java
@Service
public class AuthorizeService implements UserDetailsService {

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        return null;
    }
}
```

实现这个`loadUserByUsername`方法，表示在验证的时候通过自定义的方式，根据给定的用户名查询用户，并封装为`UserDetails`对象返回，然后由SpringSecurity将返回的对象与用户登录的信息进行核验，基本流程实际上跟之前是一样的，只是现在由自己来提供用户查询方式。

完善Service从数据库中进行查询：

```java
@Service
public class AuthorizeService implements UserDetailsService {

    @Resource
    private UserMapper mapper;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        Account account = mapper.findAccountByName(username);
        if(account == null)
            throw new UsernameNotFoundException("用户名或密码错误");
        return User
                .withUsername(username)
                .password(account.getPassword())
                .build();
    }
}
```

这样，就通过自定义的方式实现了数据库信息查询，并完成用户登录操作。

![image-20240212142358194](assets/img202402241613027.png)

### 实现 DBUserDetailsManager

也可以选择DBUserDetailsManager进行实现：

```java
@Component
public class DBUserDetailsManager implements UserDetailsManager, UserDetailsPasswordService {

    @Resource
    private UserMapper mapper;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("username", username);
        User user = mapper.selectOne(queryWrapper);
        if (user == null) {
            throw new UsernameNotFoundException(username);
        } else {
            Collection<GrantedAuthority> authorities = new ArrayList<>();
            return new org.springframework.security.core.userdetails.User(
                    user.getUsername(),
                    user.getPassword(),
                    user.getEnabled(),
                    true, //用户账号是否过期
                    true, //用户凭证是否过期
                    true, //用户是否未被锁定
                    authorities); //权限列表
        }
    }

    @Override
    public UserDetails updatePassword(UserDetails user, String newPassword) {
        return null;
    }

    @Override
    public void createUser(UserDetails user) {

    }

    @Override
    public void updateUser(UserDetails user) {

    }

    @Override
    public void deleteUser(String username) {

    }

    @Override
    public void changePassword(String oldPassword, String newPassword) {

    }

    @Override
    public boolean userExists(String username) {
        return false;
    }
}
```

这样，就通过自定义的方式实现了数据库信息查询，并完成用户登录操作。

![image-20240212142358194](assets/img202402241613461.png)

### 用户认证流程

- 程序启动时：
  - 创建`DBUserDetailsManager`类，实现接口 UserDetailsManager, UserDetailsPasswordService
  - 在应用程序中初始化这个类的对象
- 校验用户时：
  - SpringSecurity自动使用`DBUserDetailsManager`的`loadUserByUsername`方法从`数据库中`获取User对象
  - 在`UsernamePasswordAuthenticationFilter`过滤器中的`attemptAuthentication`方法中将用户输入的用户名密码和从数据库中获取到的用户信息进行比较，进行用户认证
