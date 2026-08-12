# SpringBoot 基本操作及特性

## 配置文件

SpringBoot 集中化管理配置，配置文件为`application.properties`或`application.yaml`，配置基本都有默认值。

properties 配置多以后难阅读和修改，**层级结构辨识度不高**。推荐使用[Yaml](../../../Others/Configurationfile/yaml.md)来作为配置文件进行集中化管理配置。

**所有配置**： https://docs.spring.io/spring-boot/docs/current/reference/html/application-properties.html#appendix.application-properties

```java
@Component
@ConfigurationProperties(prefix = "person") //和配置文件person前缀的所有配置进行绑定
@Data //使用Lombok 自动生成JavaBean属性的getter/setter
//@NoArgsConstructor //使用Lombok 自动生成无参构造器
//@AllArgsConstructor //使用Lombok 自动生成全参构造器
public class Person {
    private String name;
    private Integer age;
    private Date birthDay;
    private Boolean like;
    private Child child; //嵌套对象
    private List<Dog> dogs; //数组（里面是对象）
    private Map<String,Cat> cats; //表示Map
}

@Data
public class Dog {
    private String name;
    private Integer age;
}

@Data
public class Child {
    private String name;
    private Integer age;
    private Date birthDay;
    private List<String> text; //数组
}

@Data
public class Cat {
    private String name;
    private Integer age;
}
```

properties表示：

```properties
person.name=张三
person.age=18
person.birthDay=2010/10/12 12:12:12
person.like=true
person.child.name=李四
person.child.age=12
person.child.birthDay=2018/10/12
person.child.text[0]=abc
person.child.text[1]=def
person.dogs[0].name=小黑
person.dogs[0].age=3
person.dogs[1].name=小白
person.dogs[1].age=2
person.cats.c1.name=小蓝
person.cats.c1.age=3
person.cats.c2.name=小灰
person.cats.c2.age=2
```

yaml表示：

```yaml
person:
  name: 张三
  age: 18
  birthDay: 2010/10/10 12:12:12
  like: true
  child:
    name: 李四
    age: 20
    birthDay: 2018/10/10
    text: ['abc', 'def']
  dogs:
    - name: 小黑
      age: 3
    - name: 小白
      age: 2
  cats:
    c1:
      name: 小蓝
      age: 3
    c2: { name: 小绿, age: 2 } #对象也可用{}表示
```

## 自定义Bean配置

**步骤**：

1. [`@Configuration`](Annotation.md) 编写一个配置类
2. 在配置类中，自定义方法给容器中注册组件。配合[`@Bean`](Annotation.md)
3. 或使用[`@Import`](Annotation.md) 导入第三方的组件

## 自定义 banner

类路径添加banner.txt或设置spring.banner.location就可以定制 banner

banner制作网站：

- 支持中文、英文：https://www.bootschool.net/ascii
- 只支持英文：http://patorjk.com/software/taag/
- 只支持图片：https://www.degraeve.com/img2txt.php

**默认样式**：

![image-20230723221830441](assets/202307232218044.png)

**修改后的样式**：

![image-20230723222054877](assets/202307232220269.png)

**banner相关设置**：

```yaml
server:
  port: 8080
spring:
  application:
    name: basic_characteristics
  banner:
    # 设置banner编码 默认为UTF-8
    charset: UTF-8
    # 设置banner地址 默认为 classpath:banner.txt
    location: classpath:banner.txt
  main:
    # banner 模式：off取消banner、log日志输出、console控制台输出 默认为console
    banner-mode: console
```

## 自定义 SpringApplication

```java
@SpringBootApplication //主程序类
public class BasicCharacteristicsApplication {

    public static void main(String[] args) {
        //SpringApplication：Boot应用的核心API入口
//        SpringApplication.run(BasicCharacteristicsApplication.class, args);
        //1. 自定义SpringApplication的底层设置
        SpringApplication application = new SpringApplication(BasicCharacteristicsApplication.class);
        //todo 调整SpringApplication的参数
//        application.setDefaultProperties();
        //todo 配置文件优先级高于程序化调整的优先级
        application.setBannerMode(Banner.Mode.CONSOLE);
        //2.运行SpringApplication
        application.run(args);
    }
}
```

## FluentBuilder API

SpringBoot 支持流式控制：

```java
@SpringBootApplication //主程序类
public class BasicCharacteristicsApplication {

    public static void main(String[] args) {
        //Builder方式构建SpringApplication：通过FluentAPI进行设置
        new SpringApplicationBuilder()
                .main(BasicCharacteristicsApplication.class)
                .sources(BasicCharacteristicsApplication.class)
                .bannerMode(Banner.Mode.CONSOLE)
                .run(args);
    }
}
```

## 环境隔离 Profiles

环境隔离能力；快速切换开发、测试、生产环境

**步骤**：

1. **标识环境**：指定哪些组件、配置在哪个环境生效
2. **切换环境**：标识的环境对应的所有组件和配置就应该生效

**使用场景**：

- **生效的环境** = **激活的环境/默认环境** + **包含的环境**
- 基础的配置`mybatis`、`log`、`xxx`：写到**包含的环境中**
- 需要动态切换变化的 `db`、`redis`：写到**激活的环境中**

### 指定环境

Spring Profiles 提供一种**隔离配置**的方式，使其仅在**特定环境**生效

任何`@Component`， `@Configuration` 或 `@ConfigurationProperties` 可以使用 `@Profile` 标记，来指定何时被加载(**容器中的组件**都可以被 `@Profile`标记)

**操作步骤**：

- 区分环境：dev(开发环境)、test(测试环境)、prod(生产环境)
- 通过`@Profile`指定每个组件在哪个环境下生效 (**默认环境：default**)
- 默认只有激活指定的环境，组件才会生效

:::danger 注意

不标记 `@Profile`在任何环境都会生效，标记了其他的环境，就只能在该环境下使用。

:::

```java
@Component
@Profile({"dev","test"})  //在dev、test下都会生效
@Data
public class Sheep {
    private Long id;
    private String name;
    private Integer age;
}
```

```java
@Component
@Profile("prod")  //在prod下都会生效
@Data
public class Sheep {
    private Long id;
    private String name;
    private Integer age;
}
```

或在配置类中配置环境：

```java
@Configuration
@Profile("prod") //只有指定环境被激活整个类的所有配置才能生效
public class MyConfig {
    @Profile("prod")
    @Bean
    public Sheep sheep(){
        return new Sheep();
    }
    @Profile({"dev","test"})
    @Bean
    public Pig pig(){
        return new Pig();
    }

}
```

### 环境激活

**配置激活指定环境**(可激活多个环境)：

- 使用配置文件激活：

  ```properties
  # 激活指定的一个或多个环境
  spring.profiles.active=prod,test
  ```

  ```yaml
  # 激活指定的一个或多个环境
  spring:
    profiles:
      active: prod,test
  ```

- 使用命令行激活：`java -jar xxx.jar --spring.profiles.active=dev,test`

  ```bash
  --spring.profiles.active=dev,test
  ```

  ![image-20230731153801127](assets/202307311538829.png)

- 修改默认环境(不推荐，推荐使用激活方式激活指定环境)：

  ```properties
  # 指定默认环境
  spring.profiles.default=test
  ```

  ```yaml
  # 指定默认环境
  spring:
    profiles:
      default: test
  ```

### 环境包含

`spring.profiles.active` 和`spring.profiles.default` 只能用到 **无 profile 的文件**中，如果在application-dev.yaml中编写就是**无效的**

可以额外添加生效文件，而不是激活替换：

```properties
# 包含指定环境，不管激活哪个环境，总是要生效的环境
spring.profiles.include[0]=common
spring.profiles.include[1]=local
```

```yaml
# 包含指定环境，不管激活哪个环境，总是要生效的环境
spring:
  profiles:
    include:
      - common
      - local
```

### Profile 分组

创建prod组，指定包含db和mq配置：

```properties
# 环境分组
spring.profiles.group.prod[0]=db
spring.profiles.group.prod[1]=mq
```

```yaml
# 环境分组
spring:
  profiles:
    group:
      prod:
        - db
        - mq
```

使用`--spring.profiles.active=prod` ，就会激活prod，db，mq配置文件

### Profile 配置文件

`application-{profile}.properties/yaml`可以作为**指定环境的配置文件**，同样使用 `spring.profiles.active`激活环境。

:::danger 注意

- 激活环境，**配置**就会生效。最终生效的所有**配置**是

  - application.properties为主配置文件，任何情况下都生效
  - `application-{profile}.properties`指定环境配置文件，激活指定环境生效

- 在有profile的文件中编写激活环境配置无效，只能写在主配置(`application.properties`)上

- 项目的所有的生效配置项= 激活环境配置文件的所有项 + 主配置文件和激活文件不冲突的所有项

  **主配置和激活的配置都生效，优先以激活的配置为准**(如果发生了配置冲突，以激活的环境配置文件为准)。即：profile优先级 > application.properties/yaml

:::

**新建配置文件**：

![image-20230731160523085](assets/202307311605147.png)

**指定环境**：

![image-20230731160607753](assets/202307311606634.png)

### Environment

SpringBoot框架在启动的时候会将系统配置，环境信息全部封装到Environment对象中，如果要获取这些环境信息，可以调用Environment接口的方法。

在Spring Boot中，Environment接口提供了访问应用程序环境信息的方法，比如活动配置文件、系统环境变量、命令行参数等。

Environment接口由Spring框架提供，Spring Boot应用程序通常会使用Spring提供的实现类AbstractEnvironment及其子类来实现具体的环境功能。

Environment对象封装的主要数据包括：

1. Active Profiles: 当前激活的配置文件列表。Spring Boot允许应用程序定义不同的环境配置文件（如开发环境、测试环境和生产环境），通过激活不同的配置文件来改变应用程序的行为。
2. System Properties: 系统属性，通常是操作系统级别的属性，比如操作系统名称、Java版本等。
3. System Environment Variables: 系统环境变量，这些变量通常是由操作系统提供的，可以在启动应用程序时设置特定的值。
4. Command Line Arguments: 应用程序启动时传递给主方法的命令行参数。
5. Property Sources: Environment还包含了一个PropertySource列表，这个列表包含了从不同来源加载的所有属性。PropertySource可以来自多种地方，比如配置文件、系统属性、环境变量等。

在Spring Boot中，可以通过注入Environment来获取上述信息：

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

@Component
public class SomeBean {

    @Autowired
    private Environment environment;

    public void doSome(){
        // 直接使用这个环境对象，来获取环境信息，配置信息等。
        String[] activeProfiles = environment.getActiveProfiles();
        for (String activeProfile : activeProfiles) {
            System.out.println(activeProfile);
        }

        // 获取配置信息
        String street = environment.getProperty("app.xyz.addr.street");
        System.out.println(street);
    }
}
```

通过这种方式，你可以根据环境的不同灵活地配置你的应用程序。Environment是一个非常有用的工具，它可以帮助你管理各种类型的配置信息，并根据不同的运行时条件做出相应的调整。

## 外部化配置

SpringBoot 使用 **配置优先级** + **外部配置**。 简化配置更新、简化运维，**快速修改配置**，并应**用最新配置**。

外部化配置是指将**配置信息**存储在**应用程序代码**之外的地方。这样**配置信息**可以独立于代码进行管理。这样方便了配置的修改，并且修改后不需要重新编译代码，也不需要重新部署项目。只需要给`jar`应用所在的文件夹放一个`application.properties/yaml`最新配置文件，重启项目就能自动应用最新配置。

**外部化配置的优势**：

1. **灵活性**：配置文件可以独立于应用程序部署，这使得可以根据运行环境的不同来调整配置，而无需修改代码。
2. **易于维护**：配置变更不需要重新构建和部署应用程序，降低了维护成本。
3. **安全性**：敏感信息如数据库密码、API密钥等可以存储在外部，并且可以限制谁有权限访问这些配置信息。
4. **共享性**：多实例或多服务可以共享相同的配置信息，减少重复配置的工作量。
5. **版本控制**：配置文件可以存放在版本控制系统中，便于跟踪历史版本和回滚配置。

总之，外部化配置使得配置更加灵活、安全、易于管理和共享，是现代云原生应用中非常推荐的做法

### 配置优先级

Spring Boot 允许将**配置外部化**，以便可以在不同的环境中使用相同的应用程序代码。

可以使用各种**外部配置源**，包括Java Properties文件、YAML文件、环境变量和命令行参数。

`@Value`可以获取值，也可以用`@ConfigurationProperties`将所有属性绑定到java object中

**SpringBoot 属性源加载顺序**(后面的会覆盖前面的值，由低到高，高优先级配置覆盖低优先级)：

1. **默认属性**：通过`SpringApplication.setDefaultProperties`指定的

   ![image-20230731163124644](assets/202307311631548.png)

   ![image-20230731163747240](assets/202307311637056.png)

2. **`@PropertySource`指定加载的配置**：需要写在`@Configuration`类上才可生效

   ![image-20230731164041191](assets/202307311640348.png)

3. **配置文件**：application.properties/yml等

   ![image-20230731164102458](assets/202307311641483.png)

4. **RandomValuePropertySource支持的`random.`配置**：`@Value("${random.int}")`

5. **OS 环境变量**

6. **Java 系统属性**：`System.getProperties()`

7. **JNDI 属性**：来自java:comp/env

8. **ServletContext 初始化参数**

9. **ServletConfig 初始化参数**

10. **SPRING_APPLICATION_JSON属性**：内置在环境变量或系统属性中的 JSON

11. **命令行参数**

12. **测试属性**：`@SpringBootTest`进行测试时指定的属性

13. **测试类`@TestPropertySource`注解**

14. **Devtools 设置的全局属性**：`$HOME/.config/spring-boot`

---

**配置常见的优先级顺序**：命令行> 配置文件> springapplication配置

**配置文件优先级**(**后面覆盖前面**)：

1. **jar 包内**的application.properties/yml
2. **jar 包内**的application-{profile}.properties/yml
3. **jar 包外**的application.properties/yml
4. **jar 包外**的application-{profile}.properties/yml

:::warning 说明

- 用一种格式的配置文件，如果.properties和.yml同时存在,则.properties优先

- 包外 > 包内； 同级情况：profile配置 > application配置

:::

**所有参数均可由命令行传入，使用**`--参数项=参数值`**，将会被添加到环境变量中，并优先于**配置文件。

**比如**`java -jar app.jar --name="Spring"`**,可以使用**`@Value("${name}")`**获取**

**例**：

- **包内**： application.yaml `server.port=8000`
- **包内**： application-dev.yaml `server.port=8999`
- **包外**： application.yaml `server.port=9000`
- **包外**： application-prod.yaml `server.port=9001`

启动端口：命令行 > `9001` > `9000` > `8999` > `8000`

![image-20230731181114407](assets/202307311811663.png)

![image-20230731182454166](assets/202307311824752.png)

### 外部配置

SpringBoot 应用启动时会自动寻找`application.properties`和`application.yaml`位置，进行加载。

**顺序(后面覆盖前面)**：

类路径(内部)：

1. 类根路径
1. 类下/config包

![image-20230731190506501](assets/202307311907117.png)

当前路径(项目所在的位置)：

1. 当前路径
1. 当前下/config子目录
1. /config目录的直接子目录

![image-20230731190704408](assets/202307311907584.png)

**最终效果**：优先级由高到低，前面覆盖后面

- 命令行 > 包外config直接子目录 > 包外config目录 > 包外根目录 > 包内目录
- 同级比较：
  - profile配置 > 默认配置
  - properties配置 > yaml配置

![未命名绘图](assets/202307311849800.png)

规律：

- 最外层的最优先

- 命令行 > 所有
- 包外 > 包内
- config目录 > 根目录
- profile > application

配置不同就都生效(互补)，配置相同高优先级覆盖低优先级

### 导入配置

使用`spring.config.import`可以导入额外配置

```properties
# 导入指定的配置
spring.config.import=my.properties
# my.properties内部的配置 导入配置的优先级低于配置文件的优先级
my.property=value
```

```yaml
# 导入指定的配置
spring:
  config:
    import: my.yaml
# my.yaml 内部的配置 导入配置的优先级低于配置文件的优先级
my:
  prop: 你好世界
```

无论以上写法的先后顺序，my.properties的值总是优先于直接在文件中编写的my.property。

### 属性占位符

配置文件中可以使用 `${name:default}`形式取出之前配置过的值。

```properties
app.name=MyApp
app.description=${app.name} is a Spring Boot application written by ${username:Unknown}
```

```java
@RestController
@Slf4j
public class HelloController {

    //未取到值默认值为:后面的值
    @Value("${app.description:haha}")
    private String description;

    @RequestMapping("/app")
    public String app(){
        return description;
    }
}
```

![image-20230731194346976](assets/202307311943068.png)

## 日志配置

Spring使用commons-logging作为内部日志，但底层日志实现是开放的。可对接其他日志框架。

SpringBoot 支持 jul、log4j2、logback(默认使用logback)，同时提供了默认的控制台输出配置，也可以配置输出为文件。

**规范**：项目开发不要编写`System.out.println()`，应该用**日志**记录信息

![image-20230728190802970](assets/202307281909164.png)

**SpringBoot默认配置日志**：

1. 每个`starter`场景，都会导入一个核心场景`spring-boot-starter`

2. 核心场景引入了日志的所用功能`spring-boot-starter-logging`

3. 默认使用了`logback + slf4j` 组合作为默认底层日志

4. **日志是系统一启动就要用**，`xxxAutoConfiguration`是系统启动好了以后放好的组件，后来用的。

5. 日志是利用**监听器机制**配置好的 (ApplicationListener)。

6. 日志所有的配置都可以通过修改配置文件实现 (以`logging`开始的所有配置)。

### 日志格式

```shell
2023-07-28T19:50:00.161+08:00  INFO 1904 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2023-07-28T19:50:00.161+08:00  INFO 1904 --- [           main] o.apache.catalina.core.StandardEngine    : Starting Servlet engine: [Apache Tomcat/10.1.11]
```

默认输出格式：

- 时间和日期：毫秒级精度
- 日志级别：ERROR, WARN, INFO, DEBUG, or TRACE
- 进程 ID
- ---： 消息分割符
- 线程名： 使用[]包含
- Logger 名： 通常是产生日志的**类名**
- 消息： 日志记录的内容

:::danger 注意

logback 没有FATAL级别，对应的是ERROR

:::

**默认值**：参照：`spring-boot`包`additional-spring-configuration-metadata.json`文件

![image-20230728220359165](assets/202307282204665.png)

**默认输出格式值**：`%clr(%d{${LOG_DATEFORMAT_PATTERN:-yyyy-MM-dd'T'HH:mm:ss.SSSXXX}}){faint} %clr(${LOG_LEVEL_PATTERN:-%5p}) %clr(${PID:- }){magenta} %clr(---){faint} %clr([%15.15t]){faint} %clr(%-40.40logger{39}){cyan} %clr(:){faint} %m%n${LOG_EXCEPTION_CONVERSION_WORD:-%wEx}`

![image-20230728220459524](assets/202307282205476.png)

可修改为：`'%d{yyyy-MM-dd HH:mm:ss.SSS} %-5level [%thread] %logger{15} ===> %msg%n'`

```yaml
logging:
  pattern:
    console: '%d{yyyy-MM-dd HH:mm:ss.SSS} %-5level [%thread] %logger{15} ===> %msg%n'
```

```properties
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss.SSS} %-5level [%thread] %logger{15} ===> %msg%n
```

![image-20230728222253827](assets/202307282222497.png)

**修改日志日期格式**：

```yaml
logging:
  pattern:
    dateformat: 'yyyy-MM-dd HH:mm:ss'
```

```properties
logging.pattern.dateformat=yyyy-MM-dd HH:mm:ss
```

![image-20230728223416064](assets/202307282234326.png)

### 记录日志

```java
@RestController
public class HelloController {
    Logger logger = LoggerFactory.getLogger(getClass());
    @RequestMapping("/hello")
    public String hello(String a,String b) {
        logger.info("Hello, Spring Boot!");
        // 打印参数写法
        logger.info("参数a:{} ,参数b:{}",a,b);
        return "Hello, Spring Boot!";
    }
}
```

![image-20230729230747738](assets/202307292307016.png)

**使用Lombok的`@Slf4j`注解**：

```java
@RestController
@Slf4j
public class HelloController {
    @RequestMapping("/hello")
    public String hello() {
        log.info("Hello, Spring Boot!");
        // 打印参数写法
        log.info("参数a:{} ,参数b:{}",a,b);
        return "Hello, Spring Boot!";
    }
}
```

![image-20230729230858920](assets/202307292309525.png)

### 日志级别

日志级别由低到高：ALL < TRACE < DEBUG < INFO < WARN < ERROR < FATAL < OFF

- ALL：打印所有日志
- TRACE：追踪框架详细流程日志(一般不使用)
- DEBUG：开发调试细节日志
- INFO：关键、感兴趣信息日志
- WARN：警告但不是错误的信息日志，比如：版本过时
- ERROR：业务错误日志，比如出现各种异常
- FATAL：致命错误日志，比如jvm系统崩溃
- OFF：关闭所有日志记录

:::warning 说明

- 只会打印指定级别及以上级别的日志

- 不指定级别的所有类，都使用root指定的级别作为默认级别
- SpringBoot日志**默认级别是** **INFO**
- TRACE和DEBUG不能打印，会有安全问题(测试时可以使用DEBUG 生产环境关闭)

:::

**修改日志级别**：

1. 在application.properties/yaml中配置`logging.level.<logger-name>=<level>`指定日志级别

   ```properties
   # 精确调整某个包下的日志级别
   logging.level.com.hjc.demo.controller: warn
   ```

   ```yaml
   # 精确调整某个包下的日志级别
   logging:
     level:
       com.hjc.demo.controller: warn
   ```

2. level可取值范围：`TRACE, DEBUG, INFO, WARN, ERROR, FATAL, or OFF`，定义在 `LogLevel`类中

   ![image-20230729231009569](assets/202307292310097.png)

3. root 的logger-name叫root，可以配置`logging.level.root=warn`，代表所有未指定日志级别都使用 root 的 warn 级别

   ```properties
   # 默认所有日志没有精确指定级别就使用root的默认级别
   logging.level.root=debug
   ```

   ```yaml
   # 默认所有日志没有精确指定级别就使用root的默认级别
   logging:
     level:
       root: debug
   ```

### 丰富启动日志

```shell
trace=true
debug=true
```

这两个配置项主要影响Spring Boot框架本身的启动日志和跟踪信息，不影响你在应用程序中编写的日志记录。

- debug=true：启用Spring Boot的调试模式，增加启动日志的详细程度并显示自动配置报告。
- trace=true：启用Spring Boot的启动跟踪，生成包含启动信息的详细跟踪文件，内容是包含debug=true输出的内容的。

以上两个配置在SpringBoot框架启动完成之后，不再有任何作用。

### 日志分组

SpringBoot 支持将相关的logger分组在一起，统一配置。

SpringBoot 预定义两个组：

![image-20230729232203090](assets/202307292322037.png)

**例**：Tomcat 相关的日志统一设置

```properties
logging.group.tomcat=org.apache.catalina,org.apache.coyote,org.apache.tomcat
logging.level.tomcat=trace
```

```yaml
logging:
  group:
    tomcat: org.apache.catalina,org.apache.coyote,org.apache.tomcat
  level:
    # Tomcat 相关的日志统一设置
    tomcat: trace
```

### 文件输出

SpringBoot **默认只把日志写在控制台**，如果想额外记录到文件，可以在application.properties/yaml中添加`logging.file.name` or `logging.file.path`配置项。

![image-20230729235206099](assets/202307292352935.png)

:::warning 说明

- 如果只指定 `logging.file.name`：

  - 只指定文件名，会生成到当前项目位置上。

    ![image-20230729234147244](assets/202307292341024.png)

  - 指定 路径+文件名，会生成到指定位置的指定文件。

    ![image-20230729234052533](assets/202307292340108.png)

- 如果只指定 `logging.file.path`，日志文件默认名为：`spring.log`。

  ![image-20230729234253244](assets/202307292342287.png)

- 如果两个配置都同时存在，以`logging.file.name`为准(推荐直接使用`logging.file.name`)。

```properties
# 指定日志文件的路径
logging.file.path=D:\\spring-log
# 指定日志文件的名
logging.file.name=D://spring-log/demo.log
```

```yaml
logging:
  file:
    # 指定日志文件的路径
    # path: D:\\
    # 指定日志文件的名
    name: D://demo.log
```

:::

### 文件归档与滚动切割

**归档**：每天的日志单独存到一个文档中。

**切割**：每个文件10MB，超过大小切割成另外一个文件。

---

每天的日志应该独立分割出来存档。如果使用logback(SpringBoot 默认整合)，可以通过application.properties/yaml文件指定日志滚动规则。
如果是其他日志系统，需要自行配置 (添加log4j2.xml或log4j2-spring.xml)。

**支持的滚动规则设置**：

![image-20230730001649966](assets/202307300016371.png)

```properties
# 文件归档与滚动切割
logging.logback.rollingpolicy.clean-history-on-start=false
logging.logback.rollingpolicy.file-name-pattern=${LOG_FILE}.%d{yyyy-MM-dd}.%i.gz
logging.logback.rollingpolicy.max-file-size=1KB
logging.logback.rollingpolicy.total-size-cap=0B
logging.logback.rollingpolicy.max-history=7
```

```yaml
logging:
  # 文件归档与滚动切割
  logback:
    rollingpolicy:
      clean-history-on-start: false
      file-name-pattern: ${LOG_FILE}.%d{yyyy-MM-dd}.%i.gz
      max-file-size: 1KB
      total-size-cap: 0B
      max-history: 7
```

### 自定义配置

如需对接**专业日志系统**，也只需要把 logback 记录的**日志**灌倒 **kafka**之类的中间件，都是日志框架自己的配置，**修改配置文件即可**

**可以自定义日志配置**：

![image-20230730010826600](assets/202307300108185.png)

**推荐**：在日志配置中使用`-spring` 变量(例如，`logback-spring.xml` 而不是 `logback.xml`)。如果使用标准配置文件，spring 无法完全控制日志初始化。

:::warning 说明

实际生成中的日志，都是按照日志级别，分别存放到每个文件夹中的，配置文件需要添加配置。

:::

### 切换日志组合

根据**Maven就近原则**切换日志组合：原本的`spring-boot-starter-web`会导入 `spring-boot-starter` 进来，所以直接在pom导入 `spring-boot-starter` 项目就会直接导入到`spring-boot-starter-web`的，此时导的 `spring-boot-starter` 排除了默认的logging配置，用自己logging：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-logging</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-log4j2</artifactId>
</dependency>
```

log4j2支持yaml和json格式的配置文件：

![image-20230730012645555](assets/202307300126702.png)

**第三方框架**：排除掉框架的默认日志，参考 `spring-boot-starter` 排除了默认的logging配置

## 时间格式统一

可以在相应的类的属性上使用 `@JsonFormat`注解来实现时间格式的统一：

```java
@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
@DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
private Date createTime;
```

也可以在 application.yaml文件中指定：

```yaml
spring:
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: GMT+8
```
