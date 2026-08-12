# MyBatis-Plus特殊操作

## 配置表的默认前缀

### 通过注解解决

可以通过在[实体类类型上添加`@TableName("表名")`](Annotation.md)，标识实体类对应的表，即可成功执行SQL语句。

```java
@Data //lombok注解
@TableName("t_user")
public class User {
    private Long id;
    private String name;
    private Integer age;
    private String email;
}
```

### 通过全局配置解决

当实体类所对应的表都有固定的前缀，例如`t_`或`tbl_` 此时，可以使用MyBatis-Plus提供的全局配置，为实体类所对应的表名设置默认的前缀，那么就不需要在每个实体类上通过@TableName标识实体类对应的表。

```yaml [application.yml]
spring:
  # 配置数据源信息
  datasource:
    # 配置连接数据库信息
    url: jdbc:mysql://localhost:3306/mybatis_plus? serverTimezone=GMT%2B8&characterEncoding=utf-8&useSSL=false
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: 123123
    # 配置数据源类型
    type: com.alibaba.druid.pool.DruidDataSource
mybatis-plus:
  configuration:
  	# 配置MyBatis日志
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    db-config:
      # 配置MyBatis-Plus操作表的默认前缀
      table-prefix: t_
```

## 配置主键生成策略

### 通过注解解决

可以在实体类中uid属性上通过[`@TableId`](Annotation.md)将其标识为主键，即可成功执行SQL语句。

### 通过全局配置解决

```yaml [application.yml]
spring:
  # 配置数据源信息
  datasource:
    # 配置连接数据库信息
    url: jdbc:mysql://localhost:3306/mybatis_plus? serverTimezone=GMT%2B8&characterEncoding=utf-8&useSSL=false
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: 123123
    # 配置数据源类型
    type: com.alibaba.druid.pool.DruidDataSource
# 配置MyBatis日志
mybatis-plus:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    db-config:
      # 配置MyBatis-Plus操作表的默认前缀
      table-prefix: t_
      # 配置MyBatis-Plus的主键策略
      id-type: auto
```

## 通用枚举

表中的有些字段值是固定的，例如性别（男或女），此时我们可以使用MyBatis-Plus的通用枚举来实现。

### 声明通用枚举属性

**新建数据库表**：

```sql
use `mybatis_plus`;
CREATE TABLE `t_stu` (
	`id` bigint(20) NOT NULL COMMENT '主键ID',
	`name` varchar(30) DEFAULT NULL COMMENT '姓名',
	`age` int(11) DEFAULT NULL COMMENT '年龄',
	`email` varchar(50) DEFAULT NULL COMMENT '邮箱',
	`sex` int COMMENT '性别',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

```java [StudentMapper.java]
@Repository
public interface StudentMapper extends BaseMapper<Student> {
}
```

### 使用 `@EnumValue` 注解

**创建枚举类型**：

```java
@Getter
public enum SexEnum {
    MALE(1,"男"),
    FEMALE(2,"女");

    @EnumValue
    private final Integer sex;
    private final String sexName;

    SexEnum(Integer sex, String sexName) {
        this.sex = sex;
        this.sexName = sexName;
    }
}
```

```java [Student.java]
@AllArgsConstructor
@NoArgsConstructor
@Data //lombok注解
@TableName("t_stu")
public class Student {
    private Long id;
    private String name;
    private AgeEnum age;
    private String email;
    //将注解所标识的属性的值存储到数据库中
    //3.5.2版本之后 声明通用枚举属性 即可使用可不添加注解
    @EnumValue
    private SexEnum sex;
}
```

### 枚举属性，实现 IEnum 接口

**创建枚举类型**：

```java
@Getter
public enum AgeEnum implements IEnum<Integer> {
    /**
     * 注意需要实现 IEnums 也需要扫描枚举包
     */
    ONE(1, "一岁"),
    TWO(2, "二岁"),
    THREE(3, "三岁");

    AgeEnum(int value, String desc) {
        this.value = value;
        this.desc = desc;
    }

    private final int value;
    private final String desc;
    /**
     * 枚举数据库存储值
     */
    @Override
    public Integer getValue() {
        return value;
    }
}
```

```java [Student.java]
@AllArgsConstructor
@NoArgsConstructor
@Data //lombok注解
@TableName("t_stu")
public class Student {
    private Long id;
    private String name;
    private AgeEnum age;
    private String email;
    //将注解所标识的属性的值存储到数据库中
    //3.5.2版本之后 声明通用枚举属性 即可使用可不添加注解
    @EnumValue
    private SexEnum sex;
}
```

### 测试

```java
@SpringBootTest
public class EnumsTest {

    @Autowired
    private StudentMapper studentMapper;
    @Test
    void testEnums() {
        Student student = new Student();
        student.setName("刘备");
        student.setEmail("222");
        student.setAge(AgeEnum.ONE);
        //设置性别信息为枚举项，会将@EnumValue注解所标识的属性值存储到数据库
        student.setSex(SexEnum.MALE);

        int insert = studentMapper.insert(student);
        System.out.println("insert = " + insert);
    }
}
```

## 代码生成器

**引入依赖**：

```xml
<dependency>
	<groupId>com.baomidou</groupId>
	<artifactId>mybatis-plus-generator</artifactId>
	<version>3.5.5</version>
</dependency>
<dependency>
	<groupId>org.freemarker</groupId>
	<artifactId>freemarker</artifactId>
	<version>2.3.32</version>
</dependency>
```

**快速生成**：

```java
public class FastAutoGeneratorTest {
    public static void main(String[] args) {
        FastAutoGenerator.create("jdbc:mysql://127.0.0.1:3306/mybatis_plus?characterEncoding=utf-8&userSSL=false", "root", "123123")
                .globalConfig(builder -> {
                    builder.author("hjc") // 设置作者
                            //.enableSwagger() // 开启 swagger 模式
                            .fileOverride() // 覆盖已生成文件
                            .outputDir("D://mybatis_plus"); // 指定输出目录
                })
                .packageConfig(builder -> {
                    builder.parent("com.hjc.demo") // 设置父包名
                            .moduleName("mybatisplus") // 设置父包模块名
                            .pathInfo(Collections.singletonMap(OutputFile.mapperXml, "D://mybatis_plus"));
                            // 设置mapperXml生成路径
                })
                .strategyConfig(builder -> {
                    builder.addInclude("t_user") // 设置需要生成的表名
                            .addTablePrefix("t_", "c_"); // 设置过滤表前缀
                })
                .templateEngine(new FreemarkerTemplateEngine()) // 使用Freemarker引擎模板，默认的是Velocity引擎模板
                .execute();
    }
}
```
