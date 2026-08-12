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

## 基于内存认证

基于内存验证方式的权限校验存在一定的局限性，只适合快速搭建Demo使用，不适合实际生产环境下编写。

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
                .roles("USER")  //角色前面加上ROLE_ 变成权限
                .build();
        UserDetails admin = User.withDefaultPasswordEncoder()
                .username("admin")
                .password("password")
                .roles("ADMIN", "USER")
                .build();
        //return new InMemoryUserDetailsManager(user, admin);
      	//创建一个基于内存的用户信息管理器作为UserDetailsService
        InMemoryUserDetailsManager userDetailsManager = new InMemoryUserDetailsManager();
        userDetailsManager.createUser(user);
        userDetailsManager.createUser(admin);
        return userDetailsManager;
    }
}
```

配置完成后就可以前往登录界面，进行登录操作了：

![image-20230702144938540](assets/img202402121758311.png)

登录成功后，就可以访问到之前的界面了：

![image-20230920183027051](assets/202309201830297.png)

并且为了防止会话固定问题，在登录之后，JSESSIONID会得到重新分配：

![image-20230703192441811](assets/img202402121758823.png)

### 用户相关操作

InMemoryUserDetailsManager 实现自 UserDetailsManager 接口，这个接口中有着一套完整的增删改查操作，方便直接对用户进行处理：

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

通过使用UserDetailsManager对象，就能快速执行用户相关的管理操作(增加用户、删除用户、修改用户)。

#### 准备工作

添加依赖：

```xml
<dependency>
	<groupId>com.alibaba.fastjson2</groupId>
	<artifactId>fastjson2</artifactId>
	<version>2.0.43</version>
</dependency>
```

#### 增加用户

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
    void addUser(String username, String password);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsService userDetailsService;
    @Override
    public void addUser(String username, String password) {
        UserDetailsManager manager = (UserDetailsManager) userDetailsService;
        manager.createUser(User.withDefaultPasswordEncoder()
                .username(username)
                .password(password)
                .roles("ADMIN", "USER")
                .build());
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/add")
    @ResponseBody
    public JSONObject add(@RequestParam String username,
                          @RequestParam String password) {
        userService.addUser(username, password);
        JSONObject object = new JSONObject();
        object.put("success", true);
        return object;
    }

}
```

添加添加用户页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户相关操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        新建用户：
        <input type="text" id="username" placeholder="账号" />
        <input type="password" id="password" placeholder="密码" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="add()">新建用户</button>
    </div>
  </body>
</html>

<script>
  function add() {
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/add',
        {
          username: username,
          password: password,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '添加用户成功' : '添加用户失败')
      })
  }
</script>
```

访问 http://localhost:8080/user/index 添加用户：

![image-20240213182427288](assets/img202402141710798.png)

使用该新建账号登录，发现登录成功。

#### 删除用户

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
    void delUser(String username);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsService userDetailsService;

    @Override
    public void delUser(String username) {
        UserDetailsManager manager = (UserDetailsManager) userDetailsService;
        manager.deleteUser(username);
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/del")
    @ResponseBody
    public JSONObject del(@RequestParam String username) {
        userService.delUser(username);
        JSONObject object = new JSONObject();
        object.put("success", true);
        return object;
    }

}
```

添加删除用户页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        删除用户：
        <input type="text" id="delname" placeholder="账号" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="delUser()">删除用户</button>
    </div>
  </body>
</html>

<script>
  function delUser() {
    const username = document.getElementById('delname').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/del',
        {
          username: username,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '删除用户成功' : '删除用户失败')
      })
  }
</script>
```

#### 更新用户

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
    boolean  updateUser(String username, String password);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsService userDetailsService;

    @Override
    public boolean updateUser(String username, String password) {
        UserDetailsManager manager = (UserDetailsManager) userDetailsService;
        try {
            manager.updateUser(
                    User.withDefaultPasswordEncoder()
                            .username(username) //自定义用户名
                            .password(password) //自定义密码
                            .roles("USER")  //自定义角色
                            .build()
            );
        } catch (Exception e) {
            return false;
        }
        return true;
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/update")
    @ResponseBody
    public JSONObject update(@RequestParam String username,
                             @RequestParam String password) {

        JSONObject object = new JSONObject();
        if (userService.updateUser(username, password)) {
            object.put("success", true);
        }else {
            object.put("success", false);
        }
        return object;
    }
}
```

添加更新用户页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        修改用户：
        <input type="text" id="updateName" placeholder="用户名" />
        <input type="text" id="updatePassword" placeholder="新密码" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="update()">修改用户信息</button>
    </div>
  </body>
</html>

<script>
  function update() {
    const username = document.getElementById('updateName').value
    const password = document.getElementById('updatePassword').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/update',
        {
          username: username,
          password: password,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '修改用户成功' : '修改用户失败')
      })
  }
</script>
```

#### 重置用户密码

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
	void  updatePass( String oldPassword,String newPassword);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsService userDetailsService;

    @Override
    public void updatePass(String oldPassword, String newPassword) {
        UserDetailsManager manager = (UserDetailsManager) userDetailsService;
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        manager.changePassword(oldPassword, "{bcrypt}" + encoder.encode(newPassword));
    }

}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/updatePass")
    @ResponseBody
    public JSONObject updatePass(@RequestParam String oldPassword,
                                 @RequestParam String newPassword) {

        userService.updatePass(oldPassword, newPassword);
        JSONObject object = new JSONObject();
        object.put("success", true);
        return object;
    }

}
```

添加重置用户密码页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        修改用户密码：
        <input type="text" id="oldPassword" placeholder="旧密码" />
        <input type="text" id="newPassword" placeholder="新密码" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="updatePass()">修改用户密码</button>
    </div>
  </body>
</html>

<script>
  function updatePass() {
    const oldPassword = document.getElementById('oldPassword').value
    const newPassword = document.getElementById('newPassword').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/updatePass',
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
        alert(data.success ? '更新用户密码成功' : '更新用户密码失败')
      })
  }
</script>
```

#### 判断是否存在指定用户

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
    boolean existsUser(String username);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsService userDetailsService;

    @Override
    public boolean existsUser(String username) {
        UserDetailsManager manager = (UserDetailsManager) userDetailsService;
        return manager.userExists(username);
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/exists")
    @ResponseBody
    public JSONObject exists(@RequestParam String username) {
        JSONObject object = new JSONObject();
        if (userService.existsUser(username)) {
            object.put("success", true);
        }else {
            object.put("success", false);
        }
        return object;
    }

}
```

添加判断用户存在页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>新建用户</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        判断用户是否存在：
        <input type="text" id="existsUsername" placeholder="账号" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="existsUser()">判断用户是否存在</button>
    </div>
  </body>
</html>

<script>
  function existsUser() {
    const existsUsername = document.getElementById('existsUsername').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/exists',
        {
          username: existsUsername,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '该用户存在' : '该用户不存在')
      })
  }
</script>
```

## 基于数据库验证

基于数据库验证方式权限校验虽然能够直接使用数据库，但是存在一定的局限性，只适合快速搭建Demo使用，不适合实际生产环境下编写。

### 配置登录

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

![ ](assets/202309202211352.png)

当下次需要快速创建一个用户登录的应用程序时，直接使用这种方式就能快速完成了。

### 用户相关操作

JdbcUserDetailsManager 实现自 UserDetailsManager 接口，这个接口中有着一套完整的增删改查操作，方便直接对用户进行处理：

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

通过使用 UserDetailsManager 对象，就能快速执行用户相关的管理操作(增加用户、删除用户、修改用户)。

#### 准备工作

需要配置一下JdbcUserDetailsManager，为其添加一个AuthenticationManager 用于原密码的校验：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

    @Bean
    PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    //手动创建一个AuthenticationManager用于处理密码校验
    private AuthenticationManager authenticationManager(UserDetailsManager manager,
                                                        PasswordEncoder encoder) {
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

#### 增加用户

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
    void addUser(String username, String password);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsManager manager;

    @Resource
    private PasswordEncoder encoder;

    @Override
    public void addUser(String username, String password) {
        manager.createUser(User.withUsername(username)
                .password(encoder.encode(password)).roles("USER").build());
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/add")
    @ResponseBody
    public JSONObject add(@RequestParam String username,
                          @RequestParam String password) {
        userService.addUser(username, password);
        JSONObject object = new JSONObject();
        object.put("success", true);
        return object;
    }

}
```

添加添加用户页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户相关操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        新建用户：
        <input type="text" id="username" placeholder="账号" />
        <input type="password" id="password" placeholder="密码" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="add()">新建用户</button>
    </div>
  </body>
</html>

<script>
  function add() {
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/add',
        {
          username: username,
          password: password,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '添加用户成功' : '添加用户失败')
      })
  }
</script>
```

访问 http://localhost:8080/user/index 添加用户：

![image-20240213182427288](assets/img202402141711500.png)

使用该新建账号登录，发现登录成功。

#### 删除用户

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
    void delUser(String username);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsManager manager;

    @Override
    public void delUser(String username) {
        manager.deleteUser(username);
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/del")
    @ResponseBody
    public JSONObject del(@RequestParam String username) {
        userService.delUser(username);
        JSONObject object = new JSONObject();
        object.put("success", true);
        return object;
    }

}
```

添加删除用户页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户相关操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        删除用户：
        <input type="text" id="delname" placeholder="账号" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="delUser()">删除用户</button>
    </div>
  </body>
</html>

<script>
  function delUser() {
    const username = document.getElementById('delname').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/del',
        {
          username: username,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '删除用户成功' : '删除用户失败')
      })
  }
</script>
```

#### 更新用户

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
    boolean  updateUser(String username, String password);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsManager manager;

    @Resource
    private PasswordEncoder encoder;

    @Override
    public boolean updateUser(String username, String password) {
        try {
            manager.updateUser(User.withUsername(username)
                    .password(encoder.encode(password))
                    .authorities("ROLE_ADMIN")
                    .build());
        } catch (Exception e) {
            return false;
        }
        return true;
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/update")
    @ResponseBody
    public JSONObject update(@RequestParam String username,
                             @RequestParam String password) {

        JSONObject object = new JSONObject();
        if (userService.updateUser(username, password)) {
            object.put("success", true);
        }else {
            object.put("success", false);
        }
        return object;
    }
}
```

添加更新用户页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户相关操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        修改用户：
        <input type="text" id="updateName" placeholder="用户名" />
        <input type="text" id="updatePassword" placeholder="新密码" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="update()">修改用户信息</button>
    </div>
  </body>
</html>

<script>
  function update() {
    const username = document.getElementById('updateName').value
    const password = document.getElementById('updatePassword').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/update',
        {
          username: username,
          password: password,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '修改用户成功' : '修改用户失败')
      })
  }
</script>
```

#### 重置用户密码

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
	void  updatePass( String oldPassword,String newPassword);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsManager manager;

    @Resource
    private PasswordEncoder encoder;

    @Override
    public void updatePass(String oldPassword, String newPassword) {
        manager.changePassword(oldPassword, encoder.encode(newPassword));
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }
    @PostMapping("/updatePass")
    @ResponseBody
    public JSONObject updatePass(@RequestParam String oldPassword,
                                 @RequestParam String newPassword) {

        userService.updatePass(oldPassword, newPassword);
        JSONObject object = new JSONObject();
        object.put("success", true);
        return object;
    }
}
```

添加重置用户密码页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户相关操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        修改用户密码：
        <input type="text" id="oldPassword" placeholder="旧密码" />
        <input type="text" id="newPassword" placeholder="新密码" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="updatePass()">修改用户密码</button>
    </div>
  </body>
</html>

<script>
  function updatePass() {
    const oldPassword = document.getElementById('oldPassword').value
    const newPassword = document.getElementById('newPassword').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/updatePass',
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
        alert(data.success ? '更新用户密码成功' : '更新用户密码失败')
      })
  }
</script>
```

#### 判断是否存在指定用户

编写接口：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService {
    boolean existsUser(String username);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserDetailsManager manager;

    @Resource
    private PasswordEncoder encoder;

    @Override
    public boolean existsUser(String username) {
        return manager.userExists(username);
    }
}
```

创建Controller：

```java
@Controller
@RequestMapping("/user")
public class UserController {
    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    @PostMapping("/exists")
    @ResponseBody
    public JSONObject exists(@RequestParam String username) {
        JSONObject object = new JSONObject();
        if (userService.existsUser(username)) {
            object.put("success", true);
        }else {
            object.put("success", false);
        }
        return object;
    }

}
```

添加判断用户存在页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>新建用户</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        判断用户是否存在：
        <input type="text" id="existsUsername" placeholder="账号" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="existsUser()">判断用户是否存在</button>
    </div>
  </body>
</html>

<script>
  function existsUser() {
    const existsUsername = document.getElementById('existsUsername').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/exists',
        {
          username: existsUsername,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '该用户存在' : '该用户不存在')
      })
  }
</script>
```

## 自定义验证

有些时候，数据库可能并不会像SpringSecurity默认的那样进行设计，而是采用自定义的表结构，这种情况下，上面两种方式就很难进行验证了，此时需要编写自定义验证，来应对各种任意变化的情况。

既然需要自定义，那么就需要自行实现UserDetailsService或是功能更完善的UserDetailsManager接口及实现类。

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

![image-20240212141018383](assets/img202402121757905.png)

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

![image-20240212142358194](assets/img202402121757467.png)

### 实现 DBUserDetailsManager

可以选择DBUserDetailsManager进行实现：

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

![image-20240212142358194](assets/img202402121757083.png)

#### 添加用户

Service 添加方法：

> src/main/java/com/hjc/demo/service/UserService.java

```java
public interface UserService extends IService<User> {
    void saveUserDetails(String username, String password);
}
```

> src/main/java/com/hjc/demo/service/impl/UserServiceImpl.java

```java
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper,User> implements UserService {
    @Resource
    private DBUserDetailsManager dbUserDetailsManager;

    @Override
    public void saveUserDetails(String username, String password) {
        UserDetails userDetails = org.springframework.security.core.userdetails.User
                .withDefaultPasswordEncoder()
                .username(username) //自定义用户名
                .password(password) //自定义密码
                .build();
        dbUserDetailsManager.createUser(userDetails);
    }
}
```

> src/main/java/com/hjc/demo/controller/UserController.java

```java
@Controller
@RequestMapping("/user")
public class UserController {

    @Resource
    public UserService userService;

    @RequestMapping("/index")
    public String index() {
        return "user";
    }

    /**
     * 添加用户
     * @param user 用户信息
     */
    @PostMapping("/add")
    @ResponseBody
    public JSONObject add(@RequestParam String username,
                      @RequestParam String password){
        userService.saveUserDetails(username,password);
        JSONObject object = new JSONObject();
        object.put("success", true);
        return object;
    }
}
```

修改配置DBUserDetailsManager中添加方法：

```java
@Component
public class DBUserDetailsManager implements UserDetailsManager, UserDetailsPasswordService {

    @Resource
    private UserMapper mapper;

	...

    @Override
    public void createUser(UserDetails userDetails) {
        User user = new User();
        user.setUsername(userDetails.getUsername());
        user.setPassword(userDetails.getPassword());
        user.setEnabled(userDetails.isEnabled());
        mapper.insert(user);
    }

    ...
}
```

添加添加用户页面：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>用户相关操作</title>
    <script src="https://unpkg.com/axios@1.1.2/dist/axios.min.js"></script>
  </head>
  <body>
    <div>
      <label>
        新建用户：
        <input type="text" id="username" placeholder="账号" />
        <input type="password" id="password" placeholder="密码" />
        <input type="text" th:id="${_csrf.getParameterName()}" th:value="${_csrf.token}" hidden />
      </label>
      <button onclick="add()">新建用户</button>
    </div>
  </body>
</html>

<script>
  function add() {
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value
    const csrf = document.getElementById('_csrf').value
    axios
      .post(
        '/user/add',
        {
          username: username,
          password: password,
          _csrf: csrf,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      )
      .then(({ data }) => {
        alert(data.success ? '添加用户成功' : '添加用户失败')
      })
  }
</script>
```

访问 http://localhost:8080/user/index 添加用户：

![image-20240213182427288](assets/img202402141711068.png)

退出登录并使用`zhangsan`账号进行登录，发现可以登录成功。

### 用户认证流程

- 程序启动时：
  - 创建`DBUserDetailsManager`类，实现接口 UserDetailsManager, UserDetailsPasswordService
  - 在应用程序中初始化这个类的对象
- 校验用户时：
  - SpringSecurity自动使用`DBUserDetailsManager`的`loadUserByUsername`方法从**数据库中**获取User对象
  - 在`UsernamePasswordAuthenticationFilter`过滤器中的`attemptAuthentication`方法中将用户输入的用户名密码和从数据库中获取到的用户信息进行比较，进行用户认证

## 前后端分离

在前后端分离的架构中，前端向后端发起请求，后端给前端返回的需要是JSON数据，所以在用户认证流程中，需要将用户登录成功或失败的JSON数据返回给前端，再由前端根据返回的JSON数据进行处理。

### 用户认证流程

在SecurityFilterChain过滤器链中的UsernamePasswordAuthenticationFilter 专门处理用户认证流程的过滤器。这个过滤器首先先接收用户在浏览器中输入的用户名和密码，然后再用这个用户名和密码生成一个UsernamePasswordAuthenticationToken对象，把这个对象交给AuthenticationManager去做用户认证工作，当认证成功，经过一系列的处理最终到达：AuthenticationSuccessHandler(**处理用户认证成功之后返回信息的类**)，同样用户认证失败会到达：AuthenticationFailureHandler(**处理用户认证失败之后返回信息的类**)

![usernamepasswordauthenticationfilter](assets/img202402241103853.png)

### 引入fastjson

引入处理JSON工具类：FastJSON2

```xml
<dependency>
    <groupId>com.alibaba.fastjson2</groupId>
    <artifactId>fastjson2</artifactId>
    <version>2.0.37</version>
</dependency>
```

### 认证成功响应

**成功结果处理**：

```java
public class MyAuthenticationSuccessHandler implements AuthenticationSuccessHandler {
    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws IOException, ServletException {

        //获取用户身份信息
        Object principal = authentication.getPrincipal();

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", 0);
        result.put("message", "登录成功");
        result.put("data", principal);

        //转换成json字符串
        String json = JSON.toJSONString(result);

        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    }
}
```

**SecurityFilterChain配置**：

```java
form.successHandler(new MyAuthenticationSuccessHandler()) //认证成功时的处理
```

### 认证失败响应

**失败结果处理**：

```java
public class MyAuthenticationFailureHandler implements AuthenticationFailureHandler {

    @Override
    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response, AuthenticationException exception) throws IOException, ServletException {

        //获取错误信息
        String localizedMessage = exception.getLocalizedMessage();

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", -1);
//        result.put("message", localizedMessage);
        if(exception instanceof BadCredentialsException){
            result.put("message", "密码不正确");
        }else if(exception instanceof DisabledException){
            result.put("message", "账号被禁用");
        }else if(exception instanceof UsernameNotFoundException){
            result.put("message", "用户名不存在");
        }else if(exception instanceof CredentialsExpiredException){
            result.put("message", "密码已过期");
        }else if(exception instanceof AccountExpiredException){
            result.put("message", "账号已过期");
        }else if(exception instanceof LockedException){
            result.put("message", "账号被锁定");
        }else{
            result.put("message", "未知异常");
        }

        //转换成json字符串
        String json = JSON.toJSONString(result);

        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    }
}
```

**SecurityFilterChain配置**：

```java
form.failureHandler(new MyAuthenticationFailureHandler()) //认证失败时的处理
```

### 注销响应

**注销结果处理**：

```java
public class MyLogoutSuccessHandler implements LogoutSuccessHandler {

    @Override
    public void onLogoutSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws IOException, ServletException {

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", 0);
        result.put("message", "注销成功");

        //转换成json字符串
        String json = JSON.toJSONString(result);

        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    }
}
```

**SecurityFilterChain配置**：

```java
http.logout(logout -> {
    logout.logoutSuccessHandler(new MyLogoutSuccessHandler()); //注销成功时的处理
});
```

### 请求未认证的接口

当访问一个需要认证之后才能访问的接口的时候，Spring Security会使用`AuthenticationEntryPoint`将用户请求跳转到登录页面，要求用户提供登录凭证。

官方说明：[Servlet Authentication Architecture :: Spring Security](https://docs.spring.io/spring-security/reference/servlet/authentication/architecture.html)

**实现AuthenticationEntryPoint接口**：

这里也希望系统**返回json结果**，因此我们定义类实现AuthenticationEntryPoint接口：

```java
public class MyAuthenticationEntryPoint implements AuthenticationEntryPoint {
    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException) throws IOException, ServletException {

        //获取错误信息
        //String localizedMessage = authException.getLocalizedMessage();

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", -1);
        result.put("message", "需要登录");

        //转换成json字符串
        String json = JSON.toJSONString(result);

        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    }
}
```

**SecurityFilterChain配置**：

```java
//错误处理
http.exceptionHandling(exception  -> {
    exception.authenticationEntryPoint(new MyAuthenticationEntryPoint());//请求未认证的接口
});
```

### 跨域

跨域全称是跨域资源共享(`Cross-Origin Resources Sharing`，`CORS`)，它是浏览器的保护机制，只允许网页请求统一域名下的服务，同一域名指=>协议、域名、端口号都要保持一致，如果有一项不同，那么就是跨域请求。在前后端分离的项目中，需要解决跨域的问题。

在SpringSecurity中解决跨域在配置文件中添加如下配置：

```java
//跨域
http.cors(withDefaults());
```
