# Spring Security 授权

用户登录后，可能会根据用户当前是身份进行角色划分，比如我们最常用的QQ，一个QQ群里面，有群主、管理员和普通群成员三种角色，其中群主具有最高权限，群主可以管理整个群的任何板块，并且具有解散和升级群的资格，而管理员只有群主的一部分权限，只能用于日常管理，普通群成员则只能进行最基本的聊天操作。

![image-20230704222032360](https://s2.loli.net/2023/07/04/e1IXMRgawYoGvSQ.png)

对于我们来说，用户的一个操作实际上就是在访问我们提供的`接口`(编写的对应访问路径的Servlet），比如登陆，就需要调用`/login`接口，退出登陆就要调用/`logout`接口，而我们之前的图书管理系统中，新增图书、删除图书，所有的操作都有着对应的Servlet来进行处理。因此，从我们开发者的角度来说，决定用户能否使用某个功能，只需要决定用户是否能够访问对应的Servlet即可。

我们可以大致像下面这样进行划分：

- 群主：`/login`、`/logout`、`/chat`、`/edit`、`/delete`、`/upgrade`
- 管理员：`/login`、`/logout`、`/chat`、`/edit`
- 普通群成员：`/login`、`/logout`、`/chat`

也就是说，我们需要做的就是指定哪些请求可以由哪些用户发起。

**授权是用户认证通过后，根据用户的权限来控制用户访问资源的过程。拥有资源的访问权限则正常访问，没有权限则拒绝访问**。

SpringSecurity为我们提供了两种授权方式：

- 基于权限的授权：只要拥有某权限的用户，就可以访问某个路径。
- 基于角色的授权：根据用户属于哪个角色来决定是否可以访问某个路径。

两者只是概念上的不同，实际上使用起来效果差不多。

## 基于角色授权

现在我们希望创建两个角色，普通用户和管理员，普通用户只能访问index页面，而管理员可以访问任何页面。

首先我们需要对数据库中的角色表进行一些修改，添加一个用户角色字段，并创建一个新的用户，Test用户的角色为user，而Admin用户的角色为admin。

接着我们需要配置SpringSecurity，决定哪些角色可以访问哪些页面：

```java
.authorizeHttpRequests(auth -> {
    //静态资源依然全部可以访问
    auth.requestMatchers("/static/**").permitAll();
    //只有具有以下角色的用户才能访问路径"/"
    auth.requestMatchers("/").hasAnyRole("user", "admin");
    //其他所有路径必须角色为admin才能访问
    auth.anyRequest().hasRole("admin");
})
```

接着我们需要稍微修改一下验证逻辑，我们在数据库中的用户表上添加一个新的字段，用于表示角色：

![image-20230704222733082](https://s2.loli.net/2023/07/04/1pkfGS9LrsPtjFx.png)

修改一下对应的实体类：

```java
@Data
public class Account {
    int id;
    String username;
    String password;
    String role;
}
```

现在我们在查询用户时，需要添加其对应的角色：

```java
 @Override
public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
    Account account = mapper.findUserByName(username);
    if(account == null)
        throw new UsernameNotFoundException("用户名或密码错误");
    return User
            .withUsername(username)
            .password(account.getPassword())
            .roles(account.getRole())   //添加角色，一个用户可以有一个或多个角色
            .build();
}
```

这样就可以了，我们重启服务器登录看看：

![image-20230703182321093](https://s2.loli.net/2023/07/03/Zns4Vwb7zPLc6SQ.png)

目前依然是可以正常登录的，但是我们随便访问一个其他的页面，就会被拦截并自动退回到登录界面：

![image-20230704223248124](https://s2.loli.net/2023/07/04/8aoGrM9mpYt6Xie.png)

这是因为我们前面配置的是user角色，那么这个角色只能访问首页，其他的都不行，所以就会被自动拦截掉了。现在我们可以到数据库中对这个用户的角色进行修改，看看修改后是否能够访问到其他页面：

![image-20230704223503682](https://s2.loli.net/2023/07/04/l9YkDaRJdtrmSZj.png)

这样就可以访问其他页面不会被拦截了，不过因为我们没配置这个路径，所以出来的是404页面。

通过使用角色控制页面的访问，我们就可以让某些用户只能访问部分页面。

## 基于权限授权

基于权限的授权与角色类似，需要以`hasAnyAuthority`或`hasAuthority`进行判断：

```java
.authorizeHttpRequests(auth -> {
    //静态资源依然全部可以访问
    auth.requestMatchers("/static/**").permitAll();
    //基于权限和基于角色其实差别并不大，使用方式是相同的
    auth.anyRequest().hasAnyAuthority("page:index");
})
```

实际上权限跟角色相比只是粒度更细，由于使用方式差不多，这里不多做阐述。

## 使用注解权限判断

除了直接配置以外，我们还可以以注解形式直接配置，首先需要在配置类（注意这里是在Mvc的配置类上添加，因为这里只针对Controller进行过滤，所有的Controller是由Mvc配置类进行注册的，如果需要为Service或其他Bean也启用权限判断，则需要在Security的配置类上添加）上开启：

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity   //开启方法安全校验
public class SecurityConfiguration {
	...
}
```

现在我们就可以在我们想要进行权限校验的方法上添加注解了：

```java
@Controller
public class HelloController {
    @PreAuthorize("hasRole('user')")  //直接使用hasRole方法判断是否包含某个角色
    @GetMapping("/")
    public String index(){
        return "index";
    }

    ...
}
```

通过添加`@PreAuthorize`注解，在执行之前判断判断权限，如果没有对应的权限或是对应的角色，将无法访问页面。

这里其实是使用的就是我们之前讲解的SpEL表达式，我们可以直接在这里使用权限判断相关的方法，如果有忘记SpEL如何使用的可以回顾我们的Spring6核心篇。所有可以进行权限判断的方法在`SecurityExpressionRoot`类中有定义，各位小伙伴可以自行前往查看。

同样的还有`@PostAuthorize`注解，但是它是在方法执行之后再进行拦截：

```java
@PostAuthorize("hasRole('user')")
@RequestMapping("/")
public String index(){
    System.out.println("执行了");
    return "index";
}
```

除了Controller以外，只要是由Spring管理的Bean都可以使用注解形式来控制权限，我们可以在任意方法上添加这个注解，只要不具备表达式中指定的访问权限，那么就无法执行方法并且会返回403页面。

```java
@Service
public class UserService {

    @PreAuthorize("hasAnyRole('user')")
    public void test(){
        System.out.println("成功执行");
    }
}
```

与具有相同功能的还有`@Secured`但是它不支持SpEL表达式的权限表示形式，并且需要添加"ROLE_"前缀，这里就不做演示了。

我们还可以使用`@PreFilter`和`@PostFilter`对集合类型的参数或返回值进行过滤。

比如：

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

至此，有关Security的基本功能，我们就全部介绍完毕了，在后面的SpringBoot阶段，我们还会继续深入使用此框架，实现更多高级的功能。