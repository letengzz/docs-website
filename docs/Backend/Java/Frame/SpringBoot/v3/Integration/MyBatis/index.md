# SpringBoot 整合 MyBatis

[MyBatis](../../../../MyBatis/index.md)

整合mybatis的starter官网地址：https://github.com/mybatis/spring-boot-starter

## 自动配置原理

mybatis-spring-boot-starter导入 spring-boot-starter-jdbc，jdbc是操作数据库的场景。

MyBatisAutoConfiguration：配置了MyBatis的整合流程

mybatis-spring-boot-starter导入 mybatis-spring-boot-autoconfigure（mybatis的自动配置包）默认加载两个自动配置类：

- `org.mybatis.spring.boot.autoconfigure.MybatisLanguageDriverAutoConfiguration`
- `org.mybatis.spring.boot.autoconfigure.MybatisAutoConfiguration`
  - 必须在数据源配置好之后才配置
  - 给容器中SqlSessionFactory组件。创建和数据库的一次会话
  - 给容器中SqlSessionTemplate组件。操作数据库

MyBatis的所有配置绑定在MybatisProperties

每个Mapper接口的代理对象是怎么创建放到容器中。详见@MapperScan原理

利用`@Import(MapperScannerRegistrar.class)`批量给容器中注册组件。解析指定的包路径里面的每一个类，为每一个Mapper接口类，创建Bean定义信息，注册到容器中。

## 操作步骤

1. **导入依赖**：在Spring Boot项目的构建文件 (如pom.xml) 中添加MyBatis和数据库驱动的相关依赖。例如，如果使用MySQL数据库，需要添加MyBatis和MySQL驱动的依赖。
2. **配置数据源**：在`application.properties`或`application.yml`中配置数据库连接信息，包括数据库URL、用户名、密码、mybatis的功能配置等。
3. **创建实体类**：创建与数据库表对应的实体类。
4. **创建Mapper接口**：创建与数据库表交互的Mapper接口 (标准`@Mapper`注解)。
5. **创建Mapper接口SQL实现**： 可以使用mapperxml文件或者注解方式，编写sql映射文件并绑定mapper接口
6. **创建程序启动类**
7. **注解扫描**：在Spring Boot的主应用类上添加`@MapperScan`注解，用于扫描和注册Mapper接口。
8. **使用Mapper接口**：在需要使用数据库操作的地方，通过依赖注入或直接实例化Mapper接口，并调用其中的方法进行数据库操作。

## 导入依赖

可以直接从spring initializr中选择整合MyBatis：

![image-20231224205619772](assets/img202312242056982.png)

也可导入依赖：

```xml
<!-- SpringBoot整合MyBatis -->
<dependency>
	<groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.1</version>
</dependency>
```

## 配置参数

```yaml [application.yaml]
# 配置数据源
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/springboot
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: 123123
    type: com.zaxxer.hikari.HikariDataSource
# 配置mybatis规则、使⽤MyBatisPlus则此项配置⽆效
mybatis:
  # config-location: classpath:mybatis/mybatis-config.xml #全局配置文件位置
  mapper-locations: classpath:mappers/*.xml #sql映射文件位置
  configuration: # 指定mybatis全局配置⽂件中的相关配置项
    auto-mapping-behavior: full
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl
  type-aliases-package: com.hjc.demo.mybatis.pojo # 配置别名
```

当表中的字段名叫做`card_number`，和实体类的属性名`cardNumber`对应不上。解决办法两个：

- **第一种方式：查询语句使用as关键字起别名，让查询结果列名和实体类的属性名对应上。**

  ![](assets/img202411222259883.png)

  再次测试：

  ![](assets/img202411222259070.png)

- **第二种方式：通过配置自动映射**：在`application.properties`配置文件中进行如下配置：

  ```properties
  mybatis.configuration.map-underscore-to-camel-case=true
  ```

  map-underscore-to-camel-case 是一个配置项，主要用于处理数据库字段名与Java对象属性名之间的命名差异。在许多数据库中，字段名通常使用下划线（`_`）分隔单词，例如 first_name 或 last_name。而在Java代码中，变量名通常使用驼峰式命名法（camel case），如 firstName 和 lastName。

当使用MyBatis作为ORM框架时，默认情况下它会将SQL查询结果映射到Java对象的属性上。如果数据库中的字段名与Java对象的属性名不一致，那么就需要手动为每个字段指定相应的属性名，或者使用某种方式来自动转换这些名称。

map-underscore-to-camel-case 这个配置项的作用就是在查询结果映射到Java对象时，自动将下划线分隔的字段名转换成驼峰式命名法。这样可以减少手动映射的工作量，并提高代码的可读性和可维护性。

### 注解模式

```java
@Mapper
public interface CityMapper {

    @Select("select * from city where id=#{id}")
    public City getById(Long id);

    public void insert(City city);

}
```

### 混合模式

- 引入mybatis-starter
- **配置application.yaml中，指定mapper-location位置即可**
- 编写Mapper接口并标注@Mapper注解
- 简单方法直接注解方式
- 复杂方法编写mapper.xml进行绑定映射
- `@MapperScan("com.hjc.mapper")` 简化，其他的接口就可以不用标注`@Mapper`注解

```java
@Mapper
public interface CityMapper {

    @Select("select * from city where id=#{id}")
    public City getById(Long id);

    public void insert(City city);

}
```

```java
@MapperScan("com.hjc.mapper") //mapper接口扫描配置
@SpringBootApplication
public class MainApplication {
	public static void main(String[] args) {
		SpringApplication.run(MainApplication.class,args);
    }
}
```

## 声明式事务整合配置

SpringBoot中的事务管理仍然使用的Spring框架中的事务管理机制，在代码实现上更为简单了。不需要手动配置事务管理器，SpringBoot自动配置完成了。只需要使用`@Transactional`注解标注需要控制事务的方法即可。另外事务的特性等仍然延用Spring框架。

注：SpringBoot项目会自动配置一个 DataSourceTransactionManager，所以只需在方法（或者类）加上 `@Transactional` 注解，就自动纳入 Spring 的事务管理了

```java
@Transactional
public void update(){
    User user = new User();
    user.setId(1);
    user.setPassword("test2");
    user.setAccount("test2");
    userMapper.update(user);
}
```
