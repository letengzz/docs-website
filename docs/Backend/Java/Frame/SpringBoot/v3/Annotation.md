# SpringBoot 常用注解

SpringBoot摒弃XML配置方式，改为**全注解驱动**

## @SpringBootApplication注解

Spring Boot的主入口程序被`@SpringBootApplication`注解标注，可见这个注解的重要性，查看它的源码：

![](assets/img202411172040344.png)

可以看出这个注解属于**组合注解**。拥有`@SpringBootConfiguration`、`@EnableAutoConfiguration`、`@ComponentScan`的功能。

## 组件注册

### @Configuration、@SpringBootConfiguration

@Configuration声明当前类是⼀个配置类，@SpringBootConfiguration声明当前类是⼀个SpringBoot配置类，用来代替传统的xml配置文件。也就是说主入口中的方法可以被`@Bean`注解标注，被`@Bean`注解的标注的方法会被Spring容器自动调用，并且将该方法的返回对象纳入IoC容器的管理。这个`配置类`也可以称为`源`，起源的意思，SpringBoot从这个配置类开始加载项目中所有的bean。

**属性**：

- proxyBeanMethods：

  - true：@Configuration声明的类产生Cglib代理对象

    保证每个@Bean方法被调用多少次返回的组件都是单实例的

  - false ：@Configuration声明的类产生普通对象

    每个@Bean方法被调用多少次返回的组件都是新创建的

**实体类**：

> Pet

```java
public class Pet {
    private String name;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
```

> User

```java
public class User {
    private String name;
    private Integer age;
    private Pet pet;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public Pet getPet() {
        return pet;
    }

    public void setPet(Pet pet) {
        this.pet = pet;
    }
}
```

**配置类**：

```java
@Configuration(proxyBeanMethods = true)  //这是一个配置类，替代了以前的配置文件，配置类本身也是容器中的组件
//@SpringBootConfiguration
public class MyConfig {

    /**
     * 组件默认是单实例的
     * @return
     */
    @Bean("user")  //替代以前的Bean标签，组件在容器中的名字默认就是方法名，可以直接修改注解的值
    public User user(){
        User zhangsan = new User();
        zhangsan.setName("张三");
        zhangsan.setAge(23);
        zhangsan.setPet(tomPet());
        return zhangsan;
    }

    @Bean("tom")
    public Pet tomPet(){
        Pet tom = new Pet();
        tom.setName("Tom");
        return tom;
    }
}
```

**启动类**：

```java
@SpringBootApplication
public class SpringbootAnnotationApplication {

	public static void main(String[] args) {
		ConfigurableApplicationContext context = SpringApplication.run(SpringbootAnnotationApplication.class, args);
		//注解测试
		Pet tom01 = context.getBean("tom", Pet.class);
		Pet tom02 = context.getBean("tom", Pet.class);
		System.out.println("多次获得bean :" + (tom01 == tom02));
		MyConfig myConfig = context.getBean(MyConfig.class);
		System.out.println(myConfig);
		User user01 = myConfig.user();
		User user02 = myConfig.user();
		System.out.println("是否保持调⽤⽅法单例" + (user01 == user02));
		System.out.println("⽤户的宠物是否为容器中的宠物 : " + (user01.getPet()
				== tom01));
	}
}
```

**运行结果**：

![image-20230730141309431](assets/202307301413901.png)

### @Bean、@Scope

@Bean：在容器中产生对象，相当于如下xml配置，默认对象名等于方法名

```xml
<bean id="user01" class="com.hjc.demo.entity.User">
	<property name="name" value="zhangsan"></property>
	<property name="age" value="18"></property>
</bean>
```

---

@Scope：@Scope与@Bean一起用在方法上时，表示该方法生成的实例的范围。

@Scope默认是单例模式(singleton)，即：`@Scope("singleton")`

![image-20230730154145369](assets/202307301541651.png)

```java
@Bean("tom")
@Scope("singleton")
public Pet tomPet(){
	Pet tom = new Pet();
    tom.setName("Tom");
    return tom;
}
```

### @Controller、 @Service、@Repository、@Component

![image-20230730150507898](assets/202307301505317.png)

### @Import

给容器创建指定类型的对象，默认组件名为全类名，**⼀般用于导入其他配置类**

```java
public class JdbcConfig {
}
```

```java
@Configuration(proxyBeanMethods = true)
@Import(JdbcConfig.class)
public class MyConfig {
}
```

```java
@SpringBootApplication
public class MainApplication {
	public static void main(String[] args) {
		ConfigurableApplicationContext run = SpringApplication.run(MainApp
lication.class,args);
		// import测试
        Arrays.stream(run.getBeanNamesForType(JdbcConfig.class))
            .forEach((name) -> {
				System.out.println(name);
        });
	}
}
```

![image-20230730155344809](assets/202307301553311.png)

### @ComponentScan

作用：启动组件扫描功能(设置spring注解搜索的包)。

代替spring框架xml文件中这个配置：

```xml
<context:component-scan base-package="com.hjc.demo"/>
```

因此被`@SpringBootApplication`注解标注之后，会启动组件扫描功能，扫描的包是**主入口程序所在包及子包**，因此如果一个bean要纳入IoC容器的管理则必须放到主入口程序所在包及子包下。放到主入口程序所在包之外的话，扫描不到。

### @ImportResource

导入xml配置文件

> beans.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">

    <bean id="zhangsan" class="com.hjc.demo.entity.User">
        <property name="name" value="zhangsan"></property>
        <property name="age" value="18"></property>
    </bean>
    <bean id="lisi" class="com.hjc.demo.entity.Pet">
        <property name="name" value="tomcat"></property>
    </bean>
</beans>
```

```java
//配置类
@ImportResource("classpath:beans.xml")
public class MyConfig {
}
```

```java
@SpringBootApplication
public class SpringbootAnnotationApplication {

	public static void main(String[] args) {
		ConfigurableApplicationContext context = SpringApplication.run(SpringbootAnnotationApplication.class, args);
		// ImportResource测试
		System.out.println(context.containsBean("zhangsan"));
		System.out.println(context.containsBean("lisi"));
	}
}
```

![image-20230730172351954](assets/202307301724382.png)

## 条件注解

### @ConditionalOnXxx

**@Conditional注解**可以作用在创建Bean的类或者方法上，给Spring容器是否加载此bean，添加额外的约束或者判断。如果Conditional指定的**条件成立**，则触发指定行为，进行组件注入，执行相应的功能。

- **@ConditionalOnClass**：如果类路径中存在这个类，则触发指定行为
- **@ConditionalOnMissingClass**：如果类路径中不存在这个类，则触发指定行为
- **@ConditionalOnMissingBean**：如果容器中不存在这个Bean(组件)，则触发指定行为
- **@ConditionalOnBean(value=组件类型，name=组件名字)**：判断容器中是否有这个类型的组件，并且名字是指定的值，如果容器中存在这个Bean(组件)，则触发指定行为
- **@ConditionalOnRepositoryType**：当特定类型的spring Data JPA启用的时候，则触发指定行为
- **@ConditionalOnDefaultWebSecurity**
- **@ConditionalOnSingleCandidate**
- **@ConditionalOnWebApplication**：只有运行在 web 应用里才会加载这个 bean
- **@ConditionalOnWarDeployment**
- **@ConditionalOnJndi**
- **@ConditionalOnResource**
- **@ConditionalOnExpression**：当表达式为true的时候，才会实例化一个Bean
- **@ConditionalOnEnabledResourceChain**
- **@ConditionalOnNotWebApplication**：不是web应用
- **@ConditionalOnProperty**：application.properties 或 application.yml 文件中 mybean.enable 为 true 才会加载 MyCondition 这个 Bean，如果没有匹配上也会加载，因为 matchIfMissing = true，默认值是 false。
- **@ConditionalOnCloudPlatform**：只有运行在指定的云平台上才加载指定的 bean，CloudPlatform 是 `org.springframework.boot.cloud` 下一个 enum 类型的类
- **@ConditionalOnMissingFilterBean**
- **@ConditionalOnInitializedRestarter**
- **@ConditionalOnGraphQlSchema**
- **@ConditionalOnJava**：只有运行指定版本的 Java 才会加载 Bean

**例**：

- 如果存在`JdbcConfig`这个类，给容器中放一个`Pet`组件，名tom

  ```java
  @Bean("tom")
  @ConditionalOnClass(name = "com.hjc.demo.config.JdbcConfig")
  public Pet tomPet(){
  	Pet tom = new Pet();
      tom.setName("Tom");
      return tom;
  }
  ```

- 如果存在`JdbcConfig`这个类，给容器中放一个`Pet`组件，名jerry

  ```java
  @Bean("jerry")
  @ConditionalOnMissingClass(value = "com.hjc.demo.config.JdbcConfig")
  public Pet JerryPet(){
  	Pet jerry = new Pet();
      jerry.setName("Jerry");
  	return jerry;
  }
  ```

- ```java
  @SpringBootApplication
  public class SpringbootAnnotationApplication {

  	public static void main(String[] args) {
  		ConfigurableApplicationContext context = SpringApplication.run(SpringbootAnnotationApplication.class, args);

  		for (String s:context.getBeanNamesForType(Pet.class)){
  			System.out.println(s);
  		}
  	}
  }
  ```text

当`@ConditionOnXxx`放在类级别上，如果注解判断生效，则整个配置类才生效；放在方法级别，单独对这个方法进行注解判断。

```java
@SpringBootConfiguration
@ConditionalOnBean(value = User.class)  //放在类级别上，如果注解判断生效，则整个配置类才生效
public class MyConfig2 {
    @Bean("tom")
    @ConditionalOnClass(name = "com.hjc.demo.config.JdbcConfig")  //放在方法级别，单独对这个方法进行注解判断
    public Pet tomPet(){
        Pet tom = new Pet();
        tom.setName("Tom");
        return tom;
    }
}
```text

## 属性绑定

将容器中任意**组件（Bean）的属性值**和**配置文件**的配置项的值**进行绑定**：

1. **给容器中注册组件（@Component、@Bean）**
2. 使用**@ConfigurationProperties 声明组件和配置文件的哪些配置项进行绑定**

### @ConfigurationProperties

声明组件的属性和配置文件哪些前缀开始项进行绑定。

Properties读取参数类，加入核心容器的方案：

1. 直接加入 `@Component` 注解，即可加入到核心容器中 (饿汉式)。
2. 后续加入使用 `@EnableConfigurationProperties` 配置 (懒汉式)。

```java
@Component
@ConfigurationProperties(prefix = "admin")
public class Admin {
    private Integer id;
    private String name;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "Admin{" +
                "id=" + id +
                ", name='" + name + '\'' +
                '}';
    }
}
```text

> application.properties

```properties
admin.id=123
admin.name="李华"
```text

> SpringbootAnnotationApplication

```java
@SpringBootApplication
public class SpringbootAnnotationApplication {

	public static void main(String[] args) {
		Admin admin = context.getBean(Admin.class);
		System.out.println("admin = " + admin);
	}
}
```text

![image-20230730220336087](assets/202307302203804.png)

### @EnableConfigurationProperties

快速注册注解。

SpringBoot默认只扫描自己主程序所在的包。如果导入第三方包，即使组件上标注了 `@Component`、`@ConfigurationProperties` 注解，也没用。因为组件都扫描不进来，此时使用`@EnableConfigurationProperties`注解就可以快速进行属性绑定并把组件注册进容器。

**例**：

```java
@ConfigurationProperties(prefix = "admin")
public class Admin {
    private Integer id;
    private String name;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "Admin{" +
                "id=" + id +
                ", name='" + name + '\'' +
                '}';
    }
}
```text

> MyConfig

```java
/**
 * 1. 开启组件的属性绑定
 * 2. 默认会把这个组件自己放到容器中
 * @author hjc
 */
@EnableConfigurationProperties(Admin.class)  //导入第三方写好的组件进行属性绑定
//SpringBoot 默认只扫描自己主程序所在的包。如果导入第三方包，即使组件上标注了 @Commponent、@ConfigurationProperties 注解，也没用。因为组件都扫描不进来
@SpringBootConfiguration
public class MyConfig {
}
```text

> application.properties

```properties
admin.id=123
admin.name="李华"
```text

> SpringbootAnnotationApplication

```java
@SpringBootApplication
public class SpringbootAnnotationApplication {

	public static void main(String[] args) {
		Admin admin = context.getBean(Admin.class);
		System.out.println("admin = " + admin);
	}
}
```text

![image-20230730220336087](assets/202307302203804-174384486129315.png)

该注解表示`启用自动配置`。

Spring Boot 会根据你引入的依赖自动为你配置好一系列的 Bean，无需手动编写复杂的配置代码。

例如：如果你在SpringBoot项目中进行了如下配置：

```properties
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.datasource.url=jdbc:mysql://localhost:3306/springboot
spring.datasource.username=root
spring.datasource.password=123456
```text

并且在依赖中引入了`mybatis依赖`/`mybatis启动器`，那么SpringBoot框架将为你自动化配置以下bean：

- **SqlSessionFactory**: MyBatis的核心工厂SqlSessionFactory会被自动配置。这个工厂负责创建SqlSession实例，后者用来执行映射文件中的SQL语句。
- **TransactionManager**: DataSourceTransactionManager会被自动配置来管理与数据源相关的事务。
```
