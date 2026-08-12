# 参数校验

在项目里面，很有可能用户发送的数据存在一些问题，所以需要对前端传入的参数做一个简单的校验，**避免出现脏数据和业务逻辑错误以及绕过前端传入非法数据**。如果每个接口单独写校验逻辑的话，需要在controller层做逻辑判断。参数较少时，还勉强能够接受，如果参数和接口较多，无形中加重了工作量，也多了很多重复代码。所以引入注解式参数校验很有必要。

SpringBoot提供了很方便的接口校验框架来解决上述问题。

## 导入依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

该依赖会引入：

1. JSR303规范：jakarta.validation-api
2. hibernate校验：hibernate-validator

## 使用注解完成接口校验

直接使用注解完成全部接口的校验：

```java
@Validated   //首先在Controller上开启接口校验
@Controller
public class TestController {

    ...

    @ResponseBody
    @PostMapping("/submit")
    public String submit(@Length(min = 3,message = "少于3位") String username,  //使用@Length注解判断长度，message自定义提示信息
                         @Length(min = 10) String password){
        System.out.println(username.substring(3));
        System.out.println(password.substring(2, 10));
        return "请求成功!";
    }
}
```

效果：

![image-20240417230841348](assets/img202404172308444.png)

## 对象类型校验

对于对象类型接收前端发送的表单数据的，可以校验参数中的每个属性进行验证。

两种方式表示需要验证的对象：

1. 在参数上添加`@Valid`注解表示需要验证 (Java提供)
2. 在参数上添加`@Validated`注解表示需要验证 (Spring提供)

```java
@ResponseBody
@PostMapping("/submit")
//public String submit(@Valid Account account){
public String submit(@Validated Account account){ System.out.println(account.getUsername().substring(3));
    System.out.println(account.getPassword().substring(2, 10));
    return "请求成功!";
}
```

```java
@Data
public class Account {
    @Length(min = 3)   //只需要在对应的字段上添加校验的注解即可
    String username;
    @Length(min = 10)
    String password;
}
```

## 常用注解

![](assets/img202404172339378.png)

相关注解参考源码：

- jakarta.validation-api：jakarta.validation.constraints

  ![image-20240801215813741](assets/img202408012158952.png)

- hibernate-validator：org.hibernate.validator.constraints

  ![image-20240801215959810](assets/img202408012200438.png)

## 获取校验结果

只需要在参数后面添加BindingResult就可以获取完整的校验结果。

:::danger 注意

- 当多个参数时，每一个参数后接一个BindingResult返回对象来返回校验结果。

- 一旦添加BindingResult就需要手动处理错误。

  **原理**：一旦写了BindingResult，所有错误信息会被封装在BindingResult中，不会抛异常

```java
@ResponseBody
@PostMapping("/submit")  //在参数上添加@Valid注解表示需要验证
public String submit(@Valid Account account, BindingResult bindingResult) {
    //判断是否发生校验错误
    if (bindingResult.hasErrors()) {
        HashMap<String, String> errors = new HashMap<>();
        //获取所有的错误信息
        bindingResult.getFieldErrors().forEach((fieldError) -> {
            //获取发生错误的字段名
            String field = fieldError.getField();
            //获取错误信息
            String message = fieldError.getDefaultMessage();
            errors.put(field, message);
        });
        return errors.toString();
    }
    return "请求成功!";
}
```

:::

## 异常捕获器的作用

### MissingServletRequestParameterException

加了`@RequestParam`注解，但是接口调用时没有传指定的参数（注意：是没有传，而不是传了，但是值是null）。

### MethodArgumentNotValidException

当校验的参数放在对象中，接口的请求方式是post请求，用`@Valid` `@RequestBody`方式接受参数时，如果报错，会被该捕获器捕获。

### BindException

当校验参数写在类中，接口请求方式是get请求时，报错会被该捕获器捕获。

### ConstraintViolationException

传了值，但是不符合要求。`@NotNull(message = "最大值不能为空")`、`@Min(value = 10,message = "参数必须大于10")`，要求传非null值，且值必须大于10，否则会返回错误信息。经过测试，当校验参数直接写在接口上，而不是写在类中，报错会被该捕获器捕获。

## 全局异常捕获

自定义接口响应类：

```java
@Data
public class ResponseVO<T> implements Serializable {
    // 状态码: 0-成功，其他-失败
    private final Integer code;
    // 返回信息
    private final String message;
    //返回值
    private final T data;
    //是否成功
    private final Boolean success;
    // 成功返回
    public static <T> ResponseVO<T> success(T data) {
        return new ResponseVO<>(data);
    }
    // 失败返回
    public static <T> ResponseVO<T> error(Integer code, String message, T data) {
        return new ResponseVO<>(code, message, data);
    }
    public ResponseVO(T data) {
        this.code = ResponseConstant.SUCCESS_CODE;
        this.message = ResponseConstant.OK;
        this.data = data;
        this.success = true;
    }
    public ResponseVO(Integer code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.success = code == ResponseConstant.SUCCESS_CODE;
    }
}
```

自定义常量类：

```java
public class ResponseConstant {
    public static final String OK = "OK";
    public static final String ERROR = "error";
    public static final int SUCCESS_CODE = 200;
    public static final int ERROR_CODE = 500;
    public static final String ERROR_MESSAGE = "操作失败！！";
}
```

全局异常捕获：

```java
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {
	//捕获器1
    @ExceptionHandler(value = {MissingServletRequestParameterException.class})
    public ResponseVO<String> handleMissingServletRequestParameterException(MissingServletRequestParameterException ex) {
        if (log.isErrorEnabled()) {
            log.error(ex.getMessage(), ex);
        }
        return ResponseVO.error(ResponseConstant.ERROR_CODE, String.format("缺少必要参数[%s]", ex.getParameterName()), "");
    }
    //捕获器2
    @ExceptionHandler(value = {MethodArgumentNotValidException.class})
    public ResponseVO<String> handleMethodArgumentNotValidException(MethodArgumentNotValidException ex) {
        if (log.isErrorEnabled()) {
            log.error(ex.getMessage(), ex);
        }
        BindingResult result = ex.getBindingResult();
        HashMap<String, String> errorMap = new HashMap<>();
        for (FieldError fieldError : result.getFieldErrors()) {
            errorMap.put(fieldError.getField(), fieldError.getDefaultMessage());
        }
        return ResponseVO.error(ResponseConstant.ERROR_CODE, ResponseConstant.ERROR_MESSAGE,String.valueOf(errorMap));
    }
    //捕获器3
    @ExceptionHandler(value = {BindException.class})
    public ResponseVO<String> handleBindException(BindException ex) {
        if (log.isErrorEnabled()) {
            log.error(ex.getMessage(), ex);
        }
        BindingResult result = ex.getBindingResult();
        HashMap<String, String> errorMap = new HashMap<>();
        for (FieldError fieldError : result.getFieldErrors()) {
            errorMap.put(fieldError.getField(), fieldError.getDefaultMessage());
        }
        return ResponseVO.error(ResponseConstant.ERROR_CODE, ResponseConstant.ERROR_MESSAGE,String.valueOf(errorMap));
    }
    //捕获器4
    @ExceptionHandler(value = {ConstraintViolationException.class})
    public ResponseVO<String> handleConstraintViolationException(ConstraintViolationException ex) {
        if (log.isErrorEnabled()) {
            log.error(ex.getMessage(), ex);
        }
        Optional<ConstraintViolation<?>> first = ex.getConstraintViolations().stream().findFirst();
        return ResponseVO.error(ResponseConstant.ERROR_CODE, first.isPresent() ? first.get().getMessage() : ResponseConstant.ERROR_MESSAGE, "");
    }
    //其他所有异常捕获器
    @ExceptionHandler(Exception.class)
    public ResponseVO<String> otherErrorDispose(Exception e) {
        // 打印错误日志
        log.error("错误代码({}),错误信息({})", ResponseConstant.ERROR_CODE, e.getMessage());
        e.printStackTrace();
        return ResponseVO.error(ResponseConstant.ERROR_CODE, ResponseConstant.ERROR_MESSAGE, e.getMessage());
    }
}
```

## 配置异常消息

可以配合Spring的消息机制，对错误信息做成定制化、国际化。

配置消息文件：

```yaml [application.yaml]
# 配置基本消息名
spring:
  messages:
    basename: i18n/message
```

消息文件中配置提示代码：

![image-20240801223611175](assets/img202408012236078.png)

```properties [i18n/message.properties]
username.not3=用户名不能低于3
password.not10=密码不能低于10
```

```properties [i18n/message_en_US.properties]
username.not3=username length not 3
password.not10=username length not 10
```

## 自定义校验注解

添加注解：

```java [com.hjc.demo.constraints.UniqueUser]
@Documented
@Constraint(
        validatedBy = {UniqueUserConstraintValidator.class} // 指定校验器
)
@Target({ElementType.METHOD, ElementType.FIELD, ElementType.ANNOTATION_TYPE, ElementType.CONSTRUCTOR, ElementType.PARAMETER, ElementType.TYPE_USE})
@Retention(RetentionPolicy.RUNTIME)
public @interface UniqueUser {
    // 禁止的用户名
    String[] baned() default {};

    String message() default "{jakarta.validation.constraints.NotEmpty.message}";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
```

添加自定义校验器：

```java [com.hjc.demo.constraints.validator.UniqueUserConstraintValidator]
/**
 * UniqueUser注解的验证器 负责校验@UniqueUser注解的String类型字段
 * @author hjc
 */
@Component
@Scope("prototype") //每次用的时候都创建一个新的实例。防止私有变量线程安全问题
public class UniqueUserConstraintValidator implements ConstraintValidator<UniqueUser, String>{

    //模拟已存在用户
    List<String> names = Arrays.asList("张三三", "李四四", "王五五");
    private String[] baned;
    //初始化，用于获取注解标注的信息
    @Override
    public void initialize(UniqueUser constraintAnnotation) {
        //获取注解中的信息
        baned = constraintAnnotation.baned();
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext constraintValidatorContext) {
        //统计写的用户名是否在指定的黑名单中
        long count = Arrays.stream(baned).filter(s -> s.equals(value)).count();
        return !names.contains(value) && count == 0L;
    }
}
```

使用：

```java
@Data
public class Account {
    @UniqueUser(message = "用户名已存在",baned = {"admin", "username"}) //自定义注解
    String username;
}
```

## 分组校验

尽量不要使用分组校验。
