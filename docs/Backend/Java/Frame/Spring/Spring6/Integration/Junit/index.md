# 单元测试：JUnit

在之前的测试方法中，几乎都能看到以下的两行代码：

```java
ApplicationContext context = new ClassPathXmlApplicationContext("xxx.xml");
Xxxx xxx = context.getBean(Xxxx.class);
```

这两行代码的作用是创建Spring容器，最终获取到对象，但是每次测试都需要重复编写。针对上述问题，需要的是程序能自动帮我们创建容器。Spring提供了一个运行器，可以读取配置文件（或注解）来创建容器。只需要告诉它配置文件位置就可以通过Spring整合JUnit可以使程序创建spring容器。

## 整合JUnit5

1. **搭建子模块并引入依赖**：

   ```xml
   <dependencies>
       <!--spring context依赖-->
       <!--当你引入Spring Context依赖之后，表示将Spring的基础依赖引入了-->
       <dependency>
           <groupId>org.springframework</groupId>
           <artifactId>spring-context</artifactId>
           <version>6.0.10</version>
       </dependency>

       <!--spring对junit的支持相关依赖-->
       <dependency>
           <groupId>org.springframework</groupId>
           <artifactId>spring-test</artifactId>
           <version>6.0.10</version>
       </dependency>

       <!--junit5测试-->
       <dependency>
           <groupId>org.junit.jupiter</groupId>
           <artifactId>junit-jupiter-api</artifactId>
           <version>5.9.0</version>
       </dependency>

       <!--log4j2的依赖-->
       <dependency>
           <groupId>org.apache.logging.log4j</groupId>
           <artifactId>log4j-core</artifactId>
           <version>2.19.0</version>
       </dependency>
       <dependency>
           <groupId>org.apache.logging.log4j</groupId>
           <artifactId>log4j-slf4j2-impl</artifactId>
           <version>2.19.0</version>
       </dependency>
   </dependencies>
   ```

2. **添加配置文件**：

   ```xml [beans.xml]
   <?xml version="1.0" encoding="UTF-8"?>
   <beans xmlns="http://www.springframework.org/schema/beans"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:context="http://www.springframework.org/schema/context"
          xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd
                              http://www.springframework.org/schema/context http://www.springframework.org/schema/context/spring-context.xsd">
       <context:component-scan base-package="com.hjc.demo"/>
   </beans>
   ```

3. **添加日志文件**：

   ```xml [log4j2.xml]
   <?xml version="1.0" encoding="UTF-8"?>
   <configuration>
       <loggers>
           <!--
               level指定日志级别，从低到高的优先级：
                   TRACE < DEBUG < INFO < WARN < ERROR < FATAL
                   trace：追踪，是最低的日志级别，相当于追踪程序的执行
                   debug：调试，一般在开发中，都将其设置为最低的日志级别
                   info：信息，输出重要的信息，使用较多
                   warn：警告，输出警告的信息
                   error：错误，输出错误信息
                   fatal：严重错误
           -->
           <root level="DEBUG">
               <appender-ref ref="spring6log"/>
               <appender-ref ref="RollingFile"/>
               <appender-ref ref="log"/>
           </root>
       </loggers>

       <appenders>
           <!--输出日志信息到控制台-->
           <console name="spring6log" target="SYSTEM_OUT">
               <!--控制日志输出的格式-->
               <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss SSS} [%t] %-3level %logger{1024} - %msg%n"/>
           </console>

           <!--文件会打印出所有信息，这个log每次运行程序会自动清空，由append属性决定，适合临时测试用-->
           <File name="log" fileName="d:/spring6_log/test.log" append="false">
               <PatternLayout pattern="%d{HH:mm:ss.SSS} %-5level %class{36} %L %M - %msg%xEx%n"/>
           </File>

           <!-- 这个会打印出所有的信息，
               每次大小超过size，
               则这size大小的日志会自动存入按年份-月份建立的文件夹下面并进行压缩，
               作为存档-->
           <RollingFile name="RollingFile" fileName="d:/spring6_log/app.log"
                        filePattern="log/$${date:yyyy-MM}/app-%d{MM-dd-yyyy}-%i.log.gz">
               <PatternLayout pattern="%d{yyyy-MM-dd 'at' HH:mm:ss z} %-5level %class{36} %L %M - %msg%xEx%n"/>
               <SizeBasedTriggeringPolicy size="50MB"/>
               <!-- DefaultRolloverStrategy属性如不设置，
               则默认为最多同一文件夹下7个文件，这里设置了20 -->
               <DefaultRolloverStrategy max="20"/>
           </RollingFile>
       </appenders>
   </configuration>
   ```

4. **添加java类**：

   ```java
   import org.springframework.stereotype.Component;

   @Component
   public class User {

       public User() {
           System.out.println("run user");
       }
   }
   ```

5. **测试**：

   ```java
   import org.junit.jupiter.api.Test;
   import org.junit.jupiter.api.extension.ExtendWith;
   import org.springframework.beans.factory.annotation.Autowired;
   import org.springframework.test.context.ContextConfiguration;
   import org.springframework.test.context.junit.jupiter.SpringExtension;
   import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;

   //两种方式均可
   //方式一
   //@ExtendWith(SpringExtension.class)
   //@ContextConfiguration("classpath:beans.xml")
   //方式二
   @SpringJUnitConfig(locations = "classpath:beans.xml")
   public class SpringJUnit5Test {

       @Autowired
       private User user;

       @Test
       public void testUser(){
           System.out.println(user);
       }
   }
   ```

## 整合JUnit4

使用Junit 4 时，方法同整合[Junit 5](#整合JUnit5)

需要变动：

1. 依赖：

   ```xml
   <!-- junit测试 -->
   <dependency>
       <groupId>junit</groupId>
       <artifactId>junit</artifactId>
       <version>4.12</version>
   </dependency>
   ```

2. 测试：

   ```java
   import org.junit.Test;
   import org.junit.runner.RunWith;
   import org.springframework.beans.factory.annotation.Autowired;
   import org.springframework.test.context.ContextConfiguration;
   import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

   @RunWith(SpringJUnit4ClassRunner.class)
   @ContextConfiguration("classpath:beans.xml")
   public class SpringJUnit4Test {

       @Autowired
       private User user;

       @Test
       public void testUser(){
           System.out.println(user);
       }
   }
   ```
