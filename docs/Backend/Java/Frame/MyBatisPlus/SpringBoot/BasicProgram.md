# MyBatis-Plus构建入门程序

## 1.创建数据

**创建表**：

:::danger 注意

因为mybatis-plus进行数据插入的时候，默认会使用**雪花算法**来生成id 所以长度比较长，使用bigint

:::

```sql
CREATE DATABASE `mybatis_plus` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
use `mybatis_plus`;
CREATE TABLE `user` (
`id` bigint(20) NOT NULL COMMENT '主键ID',
`name` varchar(30) DEFAULT NULL COMMENT '姓名',
`age` int(11) DEFAULT NULL COMMENT '年龄',
`email` varchar(50) DEFAULT NULL COMMENT '邮箱',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

**添加数据**：

```SQL
INSERT INTO user (id, name, age, email) VALUES
(1, 'Jone', 18, 'test1@baomidou.com'),
(2, 'Jack', 20, 'test2@baomidou.com'),
(3, 'Tom', 28, 'test3@baomidou.com'),
(4, 'Sandy', 21, 'test4@baomidou.com'),
(5, 'Billie', 24, 'test5@baomidou.com');
```

## 2.搭建框架开发环境

### 初始化工程

使用 Spring Initializr 快速初始化一个 Spring Boot 工程，并选择好工具：

![image-20240116213239014](assets/img202401162132105.png)

![image-20240116213712576](assets/img202401162137802.png)

### 引入依赖

```xml [pom.xml]
<!-- mybatis-plus整合springboot -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.5</version>
</dependency>
<dependency>
    <groupId>org.mybatis</groupId>
    <artifactId>mybatis-spring</artifactId>
    <version>3.0.3</version>
</dependency>
<!-- druid-->
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid-spring-boot-3-starter</artifactId>
    <version>1.2.20</version>
</dependency>
<!-- mysql驱动-->
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
</dependency>
```

### 配置application.yaml

:::danger 注意

- 驱动类driver-class-name：

  spring boot 2.0（内置jdbc5驱动），驱动类使用：driver-class-name: `com.mysql.jdbc.Driver`

  spring boot 2.1及以上（内置jdbc8驱动），驱动类使用： driver-class-name: `com.mysql.cj.jdbc.Driver`

  否则运行测试用例的时候会有 WARN 信息。

- 连接地址url MySQL5.7版本的url： `jdbc:mysql://localhost:3306/mybatis_plus?characterEncoding=utf-8&useSSL=false`

- MySQL8.0版本的url： `jdbc:mysql://localhost:3306/mybatis_plus? serverTimezone=GMT%2B8&characterEncoding=utf-8&useSSL=false`

  否则运行测试用例报告如下错误： `java.sql.SQLException: The server time zone value 'ÖÐ¹ú±ê×¼Ê±¼ä' is unrecognized or represents more`

:::

```yaml [application.yaml]
spring:
  # 配置数据源信息
  datasource:
    # 配置数据源类型
    type: com.alibaba.druid.pool.DruidDataSource
    druid:
      # 配置连接数据库信息
      url: jdbc:mysql://localhost:3306/mybatis_plus?serverTimezone=GMT%2B8&characterEncoding=utf-8&useSSL=false
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: root
      password: 123123
# 配置MyBatis-plus
mybatis-plus:
  type-aliases-package: com.hjc.demo.pojo
```

### 启动类

在Spring Boot启动类中添加`@MapperScan`注解，扫描mapper包。

```java [BasicOperationApplication.java]
@SpringBootApplication
@MapperScan("com.hjc.demo.mapper")
public class BasicOperationApplication {

    public static void main(String[] args) {
        SpringApplication.run(BasicOperationApplication.class, args);
    }
}
```

#### 实体类

```java [com.hjc.demo.pojo.User.java]
@Data //lombok注解
@AllArgsConstructor
@NoArgsConstructor
public class User {
	private Long id;
	private String name;
	private Integer age;
	private String email;
}
```

User类编译之后的结果：

![image-20230916223032175](assets/202309162230919.png)

#### 添加mapper

通用 CRUD 封装BaseMapper接口， `Mybatis-Plus` 启动时自动解析实体表关系映射转换为 `Mybatis` 内部对象注入容器，内部包含常见的单表操作。其中包含了基本的CRUD方法，泛型为操作的实体类型。

**注意**：IDEA在 userMapper 处报错，因为找不到注入的对象，因为类是动态创建的，但是程序可以正确的执行。 为了避免报错，可以在mapper接口上添加 `@Repository` 注解

```java [UserMapper.java]
@Repository
public interface UserMapper extends BaseMapper<User> {
}
```

## 4.测试代码

```java [UserMapperTest.java]
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testSelectList() {
        //selectList()根据MP内置的条件构造器查询一个list集合，null表示没有条件，即查询所有
        userMapper.selectList(null).forEach(System.out::println);
    }
}
```

**结果**：

![image-20230916223512798](assets/202309162235792.png)

## 5.添加日志

在application.yml中配置日志输出：

```yaml
# 配置MyBatis-plus日志
mybatis-plus:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

![image-20230916223605704](assets/202309162252862.png)

## 6.原理

mybatis-plus先去扫描实体类，然后通过反射把实体类的属性抽取出来，再去分析操作的表是谁，操作的实体类的属性是谁，也就是表中的字段是谁，最终将生成相应的sql语句，然后注入Mybatis的容器中。

:::warning 说明

mybatis-plus所操作的表以及当前表中的字段由实体类以及实体类中的属性决定。

:::
