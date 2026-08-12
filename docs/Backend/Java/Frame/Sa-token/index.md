# Sa-Token

轻量级 java 权限认证框架。

官网：https://sa-token.cc/

## 导入依赖

Sa-token部分：

```xml
<!-- Sa-Token 权限认证，在线文档：https://sa-token.cc -->
<dependency>
	<groupId>cn.dev33</groupId>
    <artifactId>sa-token-spring-boot3-starter</artifactId>
    <version>1.38.0</version>
</dependency>
<!-- Sa-Token 整合 Redis （使用 jackson 序列化方式） -->
<dependency>
    <groupId>cn.dev33</groupId>
    <artifactId>sa-token-redis-jackson</artifactId>
    <version>1.38.0</version>
</dependency>
<!-- Sa-Token 整合 SpringAOP 实现注解鉴权 -->
<dependency>
    <groupId>cn.dev33</groupId>
    <artifactId>sa-token-spring-aop</artifactId>
	<version>1.38.0</version>
</dependency>
```

其他部分：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.7</version>
</dependency>
<dependency>
    <groupId>io.springboot.plugin</groupId>
    <artifactId>captcha-spring-boot-starter</artifactId>
    <version>2.2.3</version>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
    <optional>true</optional>
</dependency>
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
    <version>4.4.0</version>
</dependency>

<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <optional>true</optional>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

## 配置

```yaml
############## Sa-Token 配置 (文档: https://sa-token.cc) ##############
sa-token: 
    # token 名称（同时也是 cookie 名称）
    token-name: satoken
    # token 有效期（单位：秒） 默认30天，-1 代表永久有效
    timeout: 2592000
    # token 最低活跃频率（单位：秒），如果 token 超过此时间没有访问系统就会被冻结，默认-1 代表不限制，永不冻结
    active-timeout: -1
    # 是否允许同一账号多地同时登录 （为 true 时允许一起登录, 为 false 时新登录挤掉旧登录）
    is-concurrent: true
    # 在多人登录同一账号时，是否共用一个 token （为 true 时所有登录共用一个 token, 为 false 时每次登录新建一个 token）
    is-share: true
    # token 风格（默认可取值：uuid、simple-uuid、random-32、random-64、random-128、tik）
    token-style: uuid
    # 是否输出操作日志 
    is-log: true
```

## 登录

官方教程：https://sa-token.cc/doc.html#/use/login-auth?id=%e7%99%bb%e5%bd%95%e8%ae%a4%e8%af%81

```java
// 会话登录：参数填写要登录的账号id，建议的数据类型：long | int | String， 不可以传入复杂类型，如：User、Admin 等等
StpUtil.login(Object id);  
```

## 密码加密

官方教程：https://sa-token.cc/doc.html#/up/password-secure?id=%e5%af%86%e7%a0%81%e5%8a%a0%e5%af%86

```java
// md5加密 
SaSecureUtil.md5("123456");

// sha1加密 
SaSecureUtil.sha1("123456");

// sha256加密 
SaSecureUtil.sha256("123456");
```

## 登出

官方教程：https://sa-token.cc/doc.html#/use/login-auth?id=_2%e3%80%81%e7%99%bb%e5%bd%95%e4%b8%8e%e6%b3%a8%e9%94%80

```java
// 当前会话注销登录
StpUtil.logout();

// 获取当前会话是否已经登录，返回true=已登录，false=未登录
StpUtil.isLogin();

// 检验当前会话是否已经登录, 如果未登录，则抛出异常：`NotLoginException`
StpUtil.checkLogin();
```

## 权限

官方教程：https://sa-token.cc/doc.html#/use/jur-auth?id=%e6%9d%83%e9%99%90%e8%ae%a4%e8%af%81

```java
@Slf4j
@Component    // 保证此类被 SpringBoot 扫描，完成 Sa-Token 的自定义权限验证扩展 查询出的结果自动放到redis中，不整合redis会放到内存中
public class AuthComponent implements StpInterface {
    @Resource
    private StringRedisTemplate stringRedisTemplate;


    @Resource
    private ObjectMapper objectMapper;

    @Override //本次登录查询一次，会话期间不重复查询
    public List<String> getPermissionList(Object loginId, String loginType) {
        //每次现场调，查询数据库，数据库压力比较大
        String permissionList = stringRedisTemplate.opsForValue().get("permissionList:" + loginId);
        List<String> list = new ArrayList<>();
        if (permissionList != null && permissionList.isBlank()) {
            try {
                list = objectMapper.readValue(permissionList, new TypeReference<List<String>>() {
                });
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        } else {
            //去resource表中根据角色、部门等查询出所有菜单、按钮、文件、数据的权限标识
            list = Arrays.asList("order.create", "order.delete", "order.update");

            try {
                stringRedisTemplate.opsForValue().set("permissionList:" + loginId, objectMapper.writeValueAsString(list));
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        }
        log.info("获取权限列表：{}", list);
        return list;
    }

    @Override
    public List<String> getRoleList(Object loginId, String loginType) {
        //每次现场调，查询数据库，数据库压力比较大
        String roleList = stringRedisTemplate.opsForValue().get("roleList:" + loginId);
        List<String> list = new ArrayList<>();
        if (roleList != null && roleList.isBlank()) {
            try {
                list = objectMapper.readValue(roleList, new TypeReference<List<String>>() {
                });
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        } else {
            //去resource表中根据角色、部门等查询出所有菜单、按钮、文件、数据的权限标识
            list = Arrays.asList("admin", "user");
            try {
                stringRedisTemplate.opsForValue().set("roleList:" + loginId, objectMapper.writeValueAsString(list));
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        }
        log.info("获取角色列表：{}", list);
        return list;
    }
}
```

```java
@Operation(summary = "创建订单")
@GetMapping("/create/order")
public SaResult createOrder() {
    //编码式
    //查看所有权限
    List<String> allPermission = StpUtil.getPermissionList();
    boolean b = StpUtil.hasPermission("order.create");
    if (b) {
       return SaResult.ok("创建订单成功");
     }
    return SaResult.error("没有权限");
}
```

使用注解：

官方教程：https://sa-token.cc/doc.html#/use/at-check?id=%e6%b3%a8%e8%a7%a3%e9%89%b4%e6%9d%83

1. 注册拦截器：

   ```java
   @Configuration
   public class SaTokenConfigure implements WebMvcConfigurer {
       // 注册 Sa-Token 拦截器，打开注解式鉴权功能 
       @Override
       public void addInterceptors(InterceptorRegistry registry) {
           // 注册 Sa-Token 拦截器，打开注解式鉴权功能 
           registry.addInterceptor(new SaInterceptor()).addPathPatterns("/**");    
       }
   }
   ```

2. 使用注解：

   ```java
   @SaCheckLogin // 验证登录
   @Operation(summary = "创建订单")
   @GetMapping("/create/order")
   public SaResult createOrder() {
       //编码式
       //查看所有权限
       List<String> allPermission = StpUtil.getPermissionList();
       boolean b = StpUtil.hasPermission("order.create");
       if (b) {
          return SaResult.ok("创建订单成功");
        }
       return SaResult.error("没有权限");
   }
   ```

   
