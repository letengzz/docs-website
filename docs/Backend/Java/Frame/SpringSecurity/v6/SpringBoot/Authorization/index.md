# Spring Security 授权

用户登录后，可能会根据用户当前是身份进行角色划分，比如最常用的QQ，一个QQ群里面，有群主、管理员和普通群成员三种角色，其中群主具有最高权限，群主可以管理整个群的任何板块，并且具有解散和升级群的资格，而管理员只有群主的一部分权限，只能用于日常管理，普通群成员则只能进行最基本的聊天操作。

用户的一个操作实际上就是在访问提供的**接口** (编写的对应访问路径的Servlet），比如登陆，就需要调用`/login`接口，退出登陆就要调用/`logout`接口，从开发者的角度来说，决定用户能否使用某个功能，只需要决定用户是否能够访问对应的Servlet即可。

可以大致像下面这样进行划分：

- 群主：`/login`、`/logout`、`/chat`、`/edit`、`/delete`、`/upgrade`
- 管理员：`/login`、`/logout`、`/chat`、`/edit`
- 普通群成员：`/login`、`/logout`、`/chat`

也就是说，需要做的就是指定哪些请求可以由哪些用户发起。

**授权是用户认证通过后，根据用户的权限来控制用户访问资源的过程。拥有资源的访问权限则正常访问，没有权限则拒绝访问**。

Spring Security 提供了两种授权方式：

- **基于权限的授权** (用户-权限-资源)：只要拥有某权限的用户，就可以访问某个路径。例如张三的权限是添加用户、查看用户列表，李四的权限是查看用户列表
- **基于角色的授权** (用户-角色-权限-资源)：根据用户属于哪个角色来决定是否可以访问某个路径。例如 张三是角色是管理员、李四的角色是普通用户，管理员能做所有操作，普通用户只能查看信息

## 基于request的授权

**官方教程**：[Authorize HttpServletRequests :: Spring Security](https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html)

### 基于权限授权

基于权限的授权以`hasAnyAuthority`或`hasAuthority`进行判断，实际上权限跟角色相比只是粒度更细。

**需求：**

- 具有USER_LIST权限的用户可以访问`/user/list`接口
- 具有USER_ADD权限的用户可以访问`/user/add`接口

#### 配置权限

SecurityFilterChain：

```java
//authorizeRequests()：开启授权保护
http.authorizeHttpRequests(auth -> {
    auth.requestMatchers("/static/**").permitAll();   //将所有的静态资源放行，一定要添加在全部请求拦截之前
    //具有USER_LIST权限的用户可以访问/user/list
    auth.requestMatchers("/user/list").hasAuthority("USER_LIST");
    //具有USER_ADD权限的用户可以访问/user/add
    auth.requestMatchers("/user/add").hasAuthority("USER_ADD");
    //auth.requestMatchers("/user/index").hasAnyAuthority("page:index");

    //anyRequest()：对所有请求开启授权保护
    //authenticated()：已认证请求会自动被授权
    auth.anyRequest().authenticated();    //将所有请求全部拦截，一律需要验证
});
```

#### 授予权限

DBUserDetailsManager中的loadUserByUsername方法：

```java
Collection<GrantedAuthority> authorities = new ArrayList<>();
authorities.add(()->"USER_LIST");
authorities.add(()->"USER_ADD");
authorities.add(()->"page:index");
/*authorities.add(new GrantedAuthority() {
    @Override
    public String getAuthority() {
        return "USER_LIST";
    }
});
authorities.add(new GrantedAuthority() {
    @Override
    public String getAuthority() {
        return "USER_ADD";
    }
});*/
```

#### 请求未授权的接口

SecurityFilterChain

```java
//错误处理
http.exceptionHandling(exception  -> {
    exception.authenticationEntryPoint(new MyAuthenticationEntryPoint());//请求未认证的接口
    exception.accessDeniedHandler((request, response, e)->{ //请求未授权的接口

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", -1);
        result.put("message", "没有权限");

        //转换成json字符串
        String json = JSON.toJSONString(result);

        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    });
});
```

### 基于角色授权

通过使用角色控制页面的访问，就可以让某些用户只能访问部分页面。

**需求：**创建两个角色，普通用户和管理员，普通用户只能访问login页面，而管理员可以访问任何页面。

#### 配置角色

SecurityFilterChain

```java
//authorizeRequests()：开启授权保护
http.authorizeHttpRequests(auth -> {
    auth.requestMatchers("/static/**").permitAll();   //将所有的静态资源放行，一定要添加在全部请求拦截之前
    //只有具有以下角色的用户才能访问路径"/login"
    auth.requestMatchers("/login").hasAnyRole("USER", "ADMIN");
    //其他所有路径必须角色为admin才能访问
    auth.anyRequest().hasRole("ADMIN");
});
```

#### 授予角色

DBUserDetailsManager中的loadUserByUsername方法：

```java
return org.springframework.security.core.userdetails.User
        .withUsername(user.getUsername())
        .password(user.getPassword())
        .roles("ADMIN")
        .build();
```

#### 请求未授权的接口

SecurityFilterChain

```java
//错误处理
http.exceptionHandling(exception  -> {
    exception.authenticationEntryPoint(new MyAuthenticationEntryPoint());//请求未认证的接口
    exception.accessDeniedHandler((request, response, e)->{ //请求未授权的接口

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", -1);
        result.put("message", "没有权限");

        //转换成json字符串
        String json = JSON.toJSONString(result);

        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    });
});
```

## 基于方法的授权

**官方教程**：[Method Security :: Spring Security](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)

### 开启方法授权

除了直接配置以外，还可以以注解形式直接配置，首先需要在配置类上开启：

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity   //开启方法安全校验
public class SecurityConfiguration {
	...
}
```

### 基于权限授权

#### 配置权限

在进行权限校验的方法上添加注解：

```java
@Controller
public class HelloController {
    //用户必须有 USER_INDEX 权限 才能访问此方法
    @PreAuthorize("hasAuthority('USER_INDEX')")  //直接使用hasAuthority方法判断是否包含某个权限
    @GetMapping("/")
    public String index(){
        return "index";
    }

    ...
}
```

通过添加`@PreAuthorize`注解，在执行之前判断判断权限，如果没有对应的权限或是对应的角色，将无法访问页面。

同样的还有`@PostAuthorize`注解，但是它是在方法执行之后再进行拦截：

```java
@PostAuthorize("hasAuthority('USER_INDEX')")
@RequestMapping("/")
public String index(){
    System.out.println("执行了");
    return "index";
}
```

除了Controller以外，只要是由Spring管理的Bean都可以使用注解形式来控制权限，可以在任意方法上添加这个注解，只要不具备表达式中指定的访问权限，那么就无法执行方法并且会返回403页面。

```java
@Service
public class UserService {
	//用户必须有 USER_INDEX 权限 才能访问此方法
    @PreAuthorize("hasAuthority('USER_INDEX')")
    public void test(){
        System.out.println("成功执行");
    }
}
```

可以使用`@PreFilter`和`@PostFilter`对集合类型的参数或返回值进行过滤：

```java
@PreFilter("filterObject.equals('lbwnb')")   //filterObject代表集合中每个元素，只要满足条件的元素才会留下
public void test(List<String> list){
    System.out.println("成功执行"+list);
}

```

```java
@RequestMapping("/")
public String index(){
    List<String> list = new LinkedList<>();
    list.add("lbwnb");
    list.add("yyds");
    service.test(list);
    return "index";
}
```

与`@PreFilter`类似的`@PostFilter`这里就不做演示了，它用于处理返回值，使用方法是一样的。

当有多个集合时，需要使用`filterTarget`进行指定：

```java
@PreFilter(value = "filterObject.equals('lbwnb')", filterTarget = "list2")
public void test(List<String> list, List<String> list2){
    System.out.println("成功执行"+list);
}
```

#### 授予权限

DBUserDetailsManager中的loadUserByUsername方法：

```java
Collection<GrantedAuthority> authorities = new ArrayList<>();
authorities.add(()->"USER_LIST");
authorities.add(()->"USER_ADD");
authorities.add(()->"page:index");
/*authorities.add(new GrantedAuthority() {
    @Override
    public String getAuthority() {
        return "USER_LIST";
    }
});
authorities.add(new GrantedAuthority() {
    @Override
    public String getAuthority() {
        return "USER_ADD";
    }
});*/
```

#### 请求未授权的接口

SecurityFilterChain：

```java
//错误处理
http.exceptionHandling(exception  -> {
    exception.authenticationEntryPoint(new MyAuthenticationEntryPoint());//请求未认证的接口
    exception.accessDeniedHandler((request, response, e)->{ //请求未授权的接口

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", -1);
        result.put("message", "没有权限");

        //转换成json字符串
        String json = JSON.toJSONString(result);

        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    });
});
```

### 基于角色授权

#### 配置角色

在进行权限校验的方法上添加注解：

```java
@Controller
public class HelloController {
    @PreAuthorize("hasRole('ADMIN')")  //直接使用hasRole方法判断是否包含某个角色
    //用户必须有 ADMIN 角色 并且 用户名是 admin 才能访问此方法
	//@PreAuthorize("hasRole('ADMIN') and authentication.name == 'admim'")
    @GetMapping("/")
    public String index(){
        return "index";
    }

    ...
}
```

通过添加`@PreAuthorize`注解，在执行之前判断判断权限，如果没有对应的权限或是对应的角色，将无法访问页面。

同样的还有`@PostAuthorize`注解，但是它是在方法执行之后再进行拦截：

```java
@PostAuthorize("hasRole('ADMIN')")
@RequestMapping("/")
public String index(){
    System.out.println("执行了");
    return "index";
}
```

除了Controller以外，只要是由Spring管理的Bean都可以使用注解形式来控制权限，可以在任意方法上添加这个注解，只要不具备表达式中指定的访问权限，那么就无法执行方法并且会返回403页面。

```java
@Service
public class UserService {

    @PreAuthorize("hasAnyRole('ADMIN')")
    public void test(){
        System.out.println("成功执行");
    }
}
```

与具有相同功能的还有`@Secured`但是它不支持SpEL表达式的权限表示形式，并且需要添加"ROLE\_"前缀，这里就不做演示了。

还可以使用`@PreFilter`和`@PostFilter`对集合类型的参数或返回值进行过滤：

```java
@PreFilter("filterObject.equals('lbwnb')")   //filterObject代表集合中每个元素，只要满足条件的元素才会留下
public void test(List<String> list){
    System.out.println("成功执行"+list);
}

```

```java
@RequestMapping("/")
public String index(){
    List<String> list = new LinkedList<>();
    list.add("lbwnb");
    list.add("yyds");
    service.test(list);
    return "index";
}
```

与`@PreFilter`类似的`@PostFilter`这里就不做演示了，它用于处理返回值，使用方法是一样的。

当有多个集合时，需要使用`filterTarget`进行指定：

```java
@PreFilter(value = "filterObject.equals('lbwnb')", filterTarget = "list2")
public void test(List<String> list, List<String> list2){
    System.out.println("成功执行"+list);
}
```

#### 授予角色

DBUserDetailsManager中的loadUserByUsername方法：

```java
return org.springframework.security.core.userdetails.User
        .withUsername(user.getUsername())
        .password(user.getPassword())
        .roles("ADMIN")
        .build();
```

#### 请求未授权的接口

SecurityFilterChain：

```java
//错误处理
http.exceptionHandling(exception  -> {
    exception.authenticationEntryPoint(new MyAuthenticationEntryPoint());//请求未认证的接口
    exception.accessDeniedHandler((request, response, e)->{ //请求未授权的接口

        //创建结果对象
        HashMap result = new HashMap();
        result.put("code", -1);
        result.put("message", "没有权限");

        //转换成json字符串
        String json = JSON.toJSONString(result);

        //返回响应
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().println(json);
    });
});
```

## RBAC 设计方案

RBAC (`Role-Based Access Control`，基于角色的访问控制) 是一种常用的数据库设计方案，它将用户的权限分配和管理与角色相关联。

![img](assets/img202402241719359.jpg)

以下是一个基本的RBAC数据库设计方案的示例：

1. 用户表 (`User table`)：包含用户的基本信息，例如用户名、密码和其他身份验证信息。

   ![image-20240224145907281](assets/img202402241459113.png)

2. 角色表 (`Role table`)：存储所有可能的角色及其描述。

   ![image-20240224150100375](assets/img202402241501653.png)

3. 权限表 (`Permission table`)：定义系统中所有可能的权限。

   ![image-20240224151123934](assets/img202402241511265.png)

4. 用户角色关联表 (`User-Role table`)：将用户与角色关联起来。

   ![image-20240224151306814](assets/img202402241513341.png)

5. 角色权限关联表 (`Role-Permission table`)：将角色与权限关联起来。

   ![image-20240224151421496](assets/img202402241514409.png)

在这个设计方案中，用户可以被分配一个或多个角色，而每个角色又可以具有一个或多个权限。通过对用户角色关联和角色权限关联表进行操作，可以实现灵活的权限管理和访问控制。

当用户尝试访问系统资源时，系统可以根据用户的角色和权限决定是否允许访问。这样的设计方案使得权限管理更加简单和可维护，因为只需调整角色和权限的分配即可，而不需要针对每个用户进行单独的设置。
