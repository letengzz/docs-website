# 优雅使用枚举

在项目中，有限的状态有很多，可以使用枚举来表示来将表示的类型更明显。

创建枚举类：

```java [com.hjc.demo.enume.UserStatusEnum]
@Getter
public enum UserStatusEnum {
    //0:启用 1:禁用 2:删除 3:锁定
    ENABLE(0, "启用"),
    DISABLE(1, "禁用"),
    DELETE(2, "删除"),
    LOCK(3, "锁定");


    private int code;
    private String message;

    UserStatusEnum(Integer code, String message) {
        this.code = code;
        this.message = message;
    }
}
```

创建实体类：

```java [com.hjc.demo.entity.SysUser]
@Data
public class SysUser {
    private Long id;
    private String username;
    private String nickname;
    //0:启用 1:禁用 2:删除 3:锁定
    private UserStatusEnum status;
}
```

默认JSON处理返回的是枚举名：

```java [com.hjc.demo.controller.TestController]
@RestController
@Slf4j
@RequestMapping("/test")
public class TestController {
    @GetMapping("/getUser")
    public SysUser getUser(){
        SysUser sysUser = new SysUser();
        sysUser.setId(1L);
        sysUser.setUsername("admin");
        sysUser.setNickname("管理员");
        sysUser.setStatus(UserStatusEnum.ENABLE);
        return sysUser;
    }


    @PostMapping("/saveUser")
    private SysUser saveUser(@RequestBody SysUser userJson){
        System.out.println("保存的用户：" + userJson);
        System.out.println("用户状态：" + userJson.getStatus());
        return userJson;
    }
}
```

## 使用注解处理

调整JSON处理返回：

```java
@Getter
@JsonFormat(shape = JsonFormat.Shape.OBJECT)
public enum UserStatusEnum {
    //0:启用 1:禁用 2:删除 3:锁定
    ENABLE(0, "启用"),
    DISABLE(1, "禁用"),
    DELETE(2, "删除"),
    LOCK(3, "锁定");

    @JsonValue
    private int code;
    private String message;

    UserStatusEnum(Integer code, String message) {
        this.code = code;
        this.message = message;
    }
}
```

## 统一处理

```java
public class UserStatusEnumSerializer extends JsonSerializer<UserStatusEnum> {
    @Override
    public void serialize(UserStatusEnum userStatusEnum, JsonGenerator jsonGenerator, SerializerProvider serializerProvider) throws IOException {
        jsonGenerator.writeString(userStatusEnum.getCode()+"");
    }
}
```

```java
@Configuration
public class JacksonConfiguration {

    //定义转换规则
    @Bean
    public Jackson2ObjectMapperBuilderCustomizer jackson2ObjectMapperBuilderCustomizer() {
        return builder -> {
            //Serializer：后端写给前端：枚举变为code
            //Deserializer：前端写给后端：code变为枚举
            builder.serializerByType(UserStatusEnum.class, new UserStatusEnumSerializer());
        };
    }
}
```
