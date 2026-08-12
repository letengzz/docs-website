## 数据校验：Validation

![image-20221218154808754](assets/202307161405225.png)

### Spring Validation概述

![image-20221206220207266](assets/202307161405347.png)

在开发中，经常遇到参数校验的需求，比如用户注册的时候，要校验用户名不能为空、用户名长度不超过20个字符、手机号是合法的手机号格式等等。如果使用普通方式，会把校验的代码和真正的业务处理逻辑耦合在一起，而且如果未来要新增一种校验逻辑也需要在修改多个地方。而spring validation允许通过注解的方式来定义对象校验规则，把校验和业务逻辑分离开，让代码编写更加方便。Spring Validation其实就是对Hibernate Validator进一步的封装，方便在Spring中使用。

**在Spring中有多种校验的方式**：

- 通过实现`org.springframework.validation.Validator`接口，在代码中调用

- 按照Bean Validation方式来进行校验，即通过注解的方式

- 基于方法实现校验

- 实现自定义校验

### 通过Validator接口实现

1. 创建子模块并导入依赖：

   ```xml
   <dependencies>
       <dependency>
           <groupId>org.hibernate.validator</groupId>
           <artifactId>hibernate-validator</artifactId>
           <version>7.0.5.Final</version>
       </dependency>

       <dependency>
           <groupId>org.glassfish</groupId>
           <artifactId>jakarta.el</artifactId>
           <version>4.0.1</version>
       </dependency>
   </dependencies>
   ```

2. 创建实体类，定义属性和方法：

```java
public class Person {
    private String name;
    private int age;

    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public int getAge() {
        return age;
    }
    public void setAge(int age) {
        this.age = age;
    }
}
```

3. 创建类实现Validator接口，实现接口方法指定校验规则：

   ```java
   public class PersonValidator implements Validator {

       /**
        * todo 用来表示此校验用在哪个类型上
        * @param clazz the {@link Class} that this {@link Validator} is
        * being asked if it can {@link #validate(Object, Errors) validate}
        * @return
        */
       @Override
       public boolean supports(Class<?> clazz) {
           return Person.class.equals(clazz);
       }

       /**
        * todo 设置校验逻辑的地点
        * @param object the object that is to be validated
        * @param errors contextual state about the validation process
        */
       @Override
       public void validate(Object object, Errors errors) {
           //ValidationUtils，是Spring封装的校验工具类，帮助快速实现校验。
           //todo name不能为空
           ValidationUtils.rejectIfEmpty(errors, "name", "name.empty","name is null");
           //todo age 不能小于0 不能大于200
           Person p = (Person) object;
           if (p.getAge() < 0) {
               errors.rejectValue("age", "age.value.error","error value < 0");
           } else if (p.getAge() > 110) {
               errors.rejectValue("age", "age.value.error","error value too old");
           }
       }
   }
   ```

4. 测试：

   ```java
   import org.springframework.validation.BindingResult;
   import org.springframework.validation.DataBinder;

   public class Main {

       public static void main(String[] args) {
           //创建person对象
           Person person = new Person();
           person.setName("lucy");
           person.setAge(-1);

           // 创建Person对应的DataBinder
           DataBinder binder = new DataBinder(person);

           // 设置校验
           binder.setValidator(new PersonValidator());

           // 由于Person对象中的属性为空，所以校验不通过
           binder.validate();

           //输出结果
           BindingResult results = binder.getBindingResult();
           System.out.println(results.getAllErrors());
       }
   }
   ```

   ![image-20230716152610738](assets/202307161526581.png)

### Bean Validation注解实现

使用Bean Validation校验方式，就是如何将Bean Validation需要使用的`javax.validation.ValidatorFactory` 和`javax.validation.Validator`注入到容器中。spring默认有一个实现类LocalValidatorFactoryBean，它实现了上面Bean Validation中的接口，并且也实现了`org.springframework.validation.Validator`接口。

**常用注解**

- `@NotNull`：限制必须不为null
- `@NotEmpty`：只作用于字符串类型，字符串不为空，并且长度不为0
- `@NotBlank`：只作用于字符串类型，字符串不为空，并且`trim()`后不为空串
- `@DecimalMax(value)`：限制必须为一个不大于指定值的数字
- `@DecimalMin(value)`：限制必须为一个不小于指定值的数字
- `@Max(value)`：限制必须为一个不大于指定值的数字
- `@Min(value)`：限制必须为一个不小于指定值的数字
- `@Pattern(value)`：限制必须符合指定的正则表达式
- `@Size(max,min)`：限制字符长度必须在min到max之间
- `@Email`：验证注解的元素值是Email，也可以通过正则表达式和flag指定自定义的email格式

---

1. 创建配置类，配置LocalValidatorFactoryBean：

   ```java
   @Configuration
   @ComponentScan("com.hjc.demo.entity")
   public class ValidationConfig {

       @Bean
       public LocalValidatorFactoryBean validator() {
           return new LocalValidatorFactoryBean();
       }
   }
   ```

2. 创建实体类，使用注解定义校验规则：

   ```java
   import jakarta.validation.constraints.Max;
   import jakarta.validation.constraints.Min;
   import jakarta.validation.constraints.NotNull;

   public class User {

       @NotNull
       private String name;

       @Min(0)
       @Max(120)
       private int age;

       public String getName() {
           return name;
       }
       public void setName(String name) {
           this.name = name;
       }
       public int getAge() {
           return age;
       }
       public void setAge(int age) {
           this.age = age;
       }
   }
   ```

3. 使用两种不同的校验器实现：

   1. 使用`jakarta.validation.Validator`校验：

      ```java
      import jakarta.validation.ConstraintViolation;
      import jakarta.validation.Validator;
      import org.springframework.beans.factory.annotation.Autowired;
      import org.springframework.stereotype.Service;
      import java.util.Set;

      @Service
      public class MyService1 {

          @Autowired
          private Validator validator;

          public  boolean validator(User user){
              Set<ConstraintViolation<User>> sets =  validator.validate(user);
              return sets.isEmpty();
          }

      }
      ```

   2. 使用`org.springframework.validation.Validator`校验：

      ```java
      import org.springframework.beans.factory.annotation.Autowired;
      import org.springframework.stereotype.Service;
      import org.springframework.validation.BindException;
      import org.springframework.validation.Validator;

      @Service
      public class MyService2 {

          @Autowired
          private Validator validator;

          public boolean validaPersonByValidator(User user) {
              BindException bindException = new BindException(user, user.getName());
              validator.validate(user, bindException);
              return bindException.hasErrors();
          }
      }
      ```

4. 测试：

   ```java
   import org.junit.jupiter.api.Test;
   import org.springframework.context.ApplicationContext;
   import org.springframework.context.annotation.AnnotationConfigApplicationContext;

   public class ValidationTest {
       @Test
       void testBeanValidation1() {
           ApplicationContext context = new AnnotationConfigApplicationContext(ValidationConfig.class);
           MyService1 myService = context.getBean(MyService1.class);
           User user = new User();
           user.setAge(-1);
           boolean validator = myService.validator(user);
           System.out.println("校验结果(校验通过true 不通过false)：" + validator);
       }

       @Test
       public void testMyService2() {
           ApplicationContext context = new AnnotationConfigApplicationContext(ValidationConfig.class);
           MyService2 myService = context.getBean(MyService2.class);
           User user = new User();
           user.setName("lucy");
           user.setAge(130);
           user.setAge(-1);
           boolean validator = myService.validaPersonByValidator(user);
           System.out.println("校验结果(校验通过false 不通过true)："+validator);
       }
   }
   ```

### 基于方法实现校验

1. 创建配置类，配置MethodValidationPostProcessor：

   ```java
   import org.springframework.context.annotation.Bean;
   import org.springframework.context.annotation.ComponentScan;
   import org.springframework.context.annotation.Configuration;
   import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;
   import org.springframework.validation.beanvalidation.MethodValidationPostProcessor;

   @Configuration
   @ComponentScan("com.hjc.demo")
   public class ValidationConfig {

       @Bean
       public MethodValidationPostProcessor validationPostProcessor() {
           return new MethodValidationPostProcessor();
       }
   }
   ```

2. 创建实体类，使用注解设置校验规则：

   ```java
   import jakarta.validation.constraints.*;

   public class Admin {
       @NotNull
       private String name;

       @Min(0)
       @Max(120)
       private int age;

       @Pattern(regexp = "^1(3|4|5|7|8)\\d{9}$", message = "手机号码格式错误")
       @NotBlank(message = "手机号码不能为空")
       private String phone;

       public String getName() {
           return name;
       }

       public void setName(String name) {
           this.name = name;
       }

       public int getAge() {
           return age;
       }

       public void setAge(int age) {
           this.age = age;
       }

       public String getPhone() {
           return phone;
       }

       public void setPhone(String phone) {
           this.phone = phone;
       }
   }
   ```

3. 定义Service类，通过注解操作对象：

   ```java
   import jakarta.validation.Valid;
   import jakarta.validation.constraints.NotNull;
   import org.springframework.stereotype.Service;
   import org.springframework.validation.annotation.Validated;

   @Service
   @Validated
   public class MyService {
       public String testParams(@NotNull @Valid Admin admin) {
           return admin.toString();
       }
   }
   ```

4. 测试：

   ```java
   import org.junit.jupiter.api.Test;
   import org.springframework.context.ApplicationContext;
   import org.springframework.context.annotation.AnnotationConfigApplicationContext;

   public class ValidationTest {

       @Test
       void testMethod() {
           ApplicationContext context = new AnnotationConfigApplicationContext(ValidationConfig.class);
           MyService myService = context.getBean(MyService.class);
           Admin admin = new Admin();
           admin.setAge(-1);
           myService.testParams(admin);
       }
   }
   ```

   ![image-20230716155126275](assets/202307161551578.png)

### 实现自定义校验

1. 自定义校验注解(参照了`@NotNull`)：

   ```java
   import jakarta.validation.Constraint;
   import jakarta.validation.Payload;
   import java.lang.annotation.*;

   @Target({ElementType.METHOD, ElementType.FIELD, ElementType.ANNOTATION_TYPE, ElementType.CONSTRUCTOR, ElementType.PARAMETER})
   @Retention(RetentionPolicy.RUNTIME)
   @Documented
   @Constraint(validatedBy = {CannotBlankValidator.class}) //指定校验器类
   public @interface CannotBlank {
       //默认错误消息
       String message() default "不能包含空格";

       //分组
       Class<?>[] groups() default {};

       //负载
       Class<? extends Payload>[] payload() default {};

       //指定多个时使用
       @Target({ElementType.METHOD, ElementType.FIELD, ElementType.ANNOTATION_TYPE, ElementType.CONSTRUCTOR, ElementType.PARAMETER, ElementType.TYPE_USE})
       @Retention(RetentionPolicy.RUNTIME)
       @Documented
       @interface List {
           CannotBlank[] value();
       }
   }
   ```

2. 编写校验类：

   ```java
   import jakarta.validation.ConstraintValidator;
   import jakarta.validation.ConstraintValidatorContext;

   public class CannotBlankValidator implements ConstraintValidator<CannotBlank, String> {

           @Override
           public void initialize(CannotBlank constraintAnnotation) {
           }


           @Override
           public boolean isValid(String value, ConstraintValidatorContext context) {
                   //null时不进行校验
                   if (value != null && value.contains(" ")) {
                           //获取默认提示信息
                           String defaultConstraintMessageTemplate = context.getDefaultConstraintMessageTemplate();
                           System.out.println("default message :" + defaultConstraintMessageTemplate);
                           //禁用默认提示信息
                           context.disableDefaultConstraintViolation();
                           //设置提示语
                           context.buildConstraintViolationWithTemplate("can not contains blank").addConstraintViolation();
                           return false;
                   }
                   return true;
           }
   }
   ```

3. 创建实体类，使用自定义注解设置校验规则：

   ```java
   public class Message {

       @CannotBlank
       private String msgName;

       public String getMsgName() {
           return msgName;
       }

       public void setMsgName(String msgName) {
           this.msgName = msgName;
       }
   }
   ```

4. 定义Service类，通过注解操作对象：

   ```java
   @Service
   @Validated
   public class MsgService {
       public String testParams(@NotNull @Valid Message msg) {
           return msg.toString();
       }
   }

   ```

5. 测试：

   ```java
   import org.junit.jupiter.api.Test;
   import org.springframework.context.ApplicationContext;
   import org.springframework.context.annotation.AnnotationConfigApplicationContext;

   public class ValidationTest {

       @Test
       void testCustomAnnotation() {
           ApplicationContext context = new AnnotationConfigApplicationContext(ValidationConfig.class);
           MsgService msgService = context.getBean(MsgService.class);
           Message message = new Message();
           message.setMsgName("nihao a a a");
           msgService.testParams(message);
       }
   }
   ```

   ![image-20230716160453559](assets/202307161607017.png)
