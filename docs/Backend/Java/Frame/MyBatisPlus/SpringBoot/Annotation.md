# Mybatis-Plus注解

## @TableName

在使用MyBatis-Plus实现基本的CRUD时，并没有指定要操作的表，只是在 Mapper接口继承BaseMapper时，设置了泛型User，而操作的表为user表。

MyBatis-Plus在确定操作的表时，由BaseMapper的泛型决定，即实体类型决定，且默认操作的表名和实体类型的类名一致。

将表user更名为t_user，测试查询功能程序抛出异常，`Table 'mybatis_plus.user' doesn't exist`，因为现在的表名为t_user，而默认操作的表名和实体类型的类名一致，即user表。

![image-20230225212655158](assets/202302261313778.png)

在实体类类型上添加`@TableName("t_user")`，标识实体类对应的表，即可成功执行SQL语句。

```java
@Data //lombok注解
@TableName("t_user") //标识实体类对应的表
public class User {
    private Long id;
    private String name;
    private Integer age;
    private String email;
}
```

## @TableId

MyBatis-Plus在实现CRUD时，会默认将id作为主键列，并在插入数据时，默认基于**雪花算法**的策略生成id。

雪花算法生成的数字，需要使用Long 或者 String类型主键。

若实体类和表中表示主键的不是id，而是其他字段，例如uid，MyBatis-Plus不会自动识别uid为主键列。

在实体类中uid属性上通过`@TableId`将其标识为主键，即可成功执行SQL语句。

在以下场景下，添加`@TableId`注解是必要的：

1.  实体类的字段与数据库表的主键字段不同名：如果实体类中的字段与数据库表的主键字段不一致，需要使用`@TableId`注解来指定实体类中表示主键的字段。
2.  主键生成策略不是默认策略：如果需要使用除了默认主键生成策略以外的策略，也需要添加`@TableId`注解，并通过`value`属性指定生成策略。

### value属性

若实体类中主键对应的属性为id，而表中表示主键的字段为uid，此时若只在属性id上添加注解 `@TableId`，则抛出异常`Unknown column 'id' in 'field list'`，即MyBatis-Plus仍然会将id作为表的主键操作，而表中表示主键的是字段uid 此时需要通过`@TableId`注解的value属性，指定表中的主键字段，`@TableId("uid")`或 `@TableId(value="uid")`

![image-20230225213830005](assets/202302261314212.png)

```java
@Data //lombok注解
public class User {
    //将属性所对应的字段指定为主键
    //@TableId注解的value属性用于指定主键的字段
    @TableId("id")
    private Long uid;
    private String name;
    private Integer age;
    private String email;
}
```

### type属性

type属性用来定义主键策略。

**常用的主键策略**：

![图片1](assets/202302261314819.png)

```java
@Data //lombok注解
public class User {
    //将属性所对应的字段指定为主键
    //@TableId注解的value属性用于指定主键的字段
    //@TableId注解的type属性用于指定主键的主键策略
    @TableId(value = "id",type = IdType.AUTO)
    private Long uid;
    private String name;
    private Integer age;
    private String email;
}
```

## @TableField

MyBatis-Plus在执行SQL语句时，要保证实体类中的属性名和表中的字段名一致。

若实体类中的属性使用的是驼峰命名风格，而表中的字段使用的是下划线命名风格，例如实体类属性userName，表中字段user_name 此时MyBatis-Plus会自动将下划线命名风格转化为驼峰命名风格，相当于在MyBatis中配置。

若实体类中的属性和表中的字段不满足驼峰命名， 例如实体类属性name，表中字段username，此时需要在实体类属性上使用`@TableField("username")`设置属性所对应的字段名。

**属性**：

- value：数据库字段名
- exist：是否为数据库表字段

```java
@Data //lombok注解
public class User {
    private Long id;
    @TableField("name")
    private String username;
    private Integer age;
    private String email;
}
```

可以排除实体类中非表字段：

```java
@TableField(exist = false)
private String queryName;
```

## @TableLogic

- **物理删除**：真实删除，将对应数据从数据库中删除，之后查询不到此条被删除的数据
- **逻辑删除**：假删除，将对应数据中代表是否被删除字段的状态修改为“被删除状态”，之后在数据库中仍旧能看到此条数据记录

逻辑删除，可以方便地实现对数据库记录的逻辑删除而不是物理删除。逻辑删除是指通过更改记录的状态或添加标记字段来模拟删除操作，从而保留了删除前的数据，便于后续的数据分析和恢复。

**使用场景**：可以进行数据恢复

1. 数据库中创建逻辑删除状态列，设置默认值为0

   ```sql
   alter table user add is_deleted int DEFAULT 0 COMMENT '逻辑删除';
   ```

2. 实体类中添加逻辑删除属性：

   ```java
   @Data //lombok注解
   public class User {
       private Long id;
       private String name;
       private Integer age;
       private String email;

       //添加逻辑删除属性 value默认逻辑未删除值 delval默认逻辑删除值
       @TableLogic(value = "0",delval = "1")
       private Integer isDeleted;
   }
   ```

   全局指定：

   ```yaml
   mybatis-plus:
     global-config:
       db-config:
         logic-delete-field: deleted # 全局逻辑删除的实体字段名(since 3.3.0,配置后可以忽略不配置步骤2)
         logic-delete-value: 1 # 逻辑已删除值(默认为 1)
         logic-not-delete-value: 0 # 逻辑未删除值(默认为 0)
   ```

3. 测试：

   ```java
   @SpringBootTest
   class UserMapperTest {
       @Autowired
       private UserMapper userMapper;

       @Test
       void testDelete() {
           //测试删除
           int delete = userMapper.deleteById(2L);
           System.out.println("delete = " + delete);
       }

       @Test
       void testSelect() {
           //测试查询
           userMapper.selectList(null).forEach(System.out::println);
       }
   }
   ```
