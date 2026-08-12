# MyBatis-Plus条件构造器

## wapper

通过观察BaseMapper中的方法，大多方法中都有Wrapper类型的形参，此为条件构造器，可针对于SQL语句设置不同的条件，若没有条件，则可以为该形参赋值null，即查询（删除/修改）所有数据。

使用MyBatis-Plus的条件构造器，可以构建灵活、高效的查询条件，而不需要手动编写复杂的 SQL 语句。它提供了许多方法来支持各种条件操作符，并且可以通过链式调用来组合多个条件。这样可以简化查询的编写过程，并提高开发效率。

条件构造器类结构：

![image-20230225222850348](assets/202302261313615.png)

- Wrapper ： 条件构造抽象类，最顶端父类
  - AbstractWrapper ： 用于查询条件封装，生成 sql 的 where 条件
    - QueryWrapper ： 查询条件封装
    - UpdateWrapper ： Update 条件封装
    - AbstractLambdaWrapper ： 使用Lambda 语法
      - LambdaQueryWrapper ：用于Lambda语法使用的查询Wrapper
      - LambdaUpdateWrapper ： Lambda 更新封装Wrapper

## QueryWrapper

QueryWrapper主要用于查询和删除功能也可以用修改功

**组装条件**：

![image_k_cPdiIiy4](assets/img202412031137869.png)

### 组装查询条件

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    //组装查询条件
    @Test
    void testSelect() {
        // 查询用户名包含a 年龄在20到30之间 邮箱信息不为null的信息
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.like("name", "a")
                .between("age", 20, 30)
                .isNotNull("email");
        userMapper.selectList(wrapper).forEach(System.out::println);
    }
}
```

```java
QueryWrapper<User> queryWrapper = new QueryWrapper<>();
queryWrapper.eq("name", "John"); // 添加等于条件
queryWrapper.ne("age", 30); // 添加不等于条件
queryWrapper.like("email", "@gmail.com"); // 添加模糊匹配条件
```

### 组装排序条件

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testSort() {
        //查询用户信息，按照年龄的降序排序，若年龄相同，则按照id升序排序
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.orderByDesc("age")
                .orderByAsc("id");
        userMapper.selectList(wrapper).forEach(System.out::println);
    }
}
```

### 组装删除条件

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testDelete() {
        //删除邮箱地址为null的用户信息
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.isNull("email");
        int delete = userMapper.delete(wrapper);
        System.out.println("delete = " + delete);
    }
}
```

### 组装修改条件

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testUpdate() {
        //将年龄大于20并且用户名中包含有a 或 邮箱为null的用户信息修改
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.gt("age", 20)
                .like("name", "a")
                .or()
                .isNull("email");
        User user = new User();
        user.setUsername("小白");
        user.setEmail("232332");
        int result = userMapper.update(user, wrapper);
        System.out.println("result = " + result);
    }
}
```

### 指定列映射查询

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

   @Test
   public void test05() {
        //查询用户信息的username和age字段
        //SELECT name,age FROM t_user
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.select("name", "age");
        //selectMaps()返回Map集合列表，通常配合select()使用，避免User对象中没有被查询到的列值为null
        List<Map<String, Object>> maps = userMapper.selectMaps(queryWrapper);
        maps.forEach(System.out::println);
    }
}
```

### 条件的优先级

优先执行的可以使用`and()`/`or()`方法(sql中添加小括号)：

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void test() {
        //将年龄大于20并且用户名中包含有a 或 邮箱为null的用户信息修改
        //lambda中的条件优先执行
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.like("name", "a")
                .and(i->i.gt("age",20).or().isNull("email"));
        User user = new User();
        user.setUsername("小白");
        user.setEmail("232332");
        int result = userMapper.update(user, wrapper);
        System.out.println("result = " + result);
    }
}
```

### 组装select子句

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    //组装select子句
    @Test
    void testSelect1() {
        //查询用户的用户名、年龄、邮箱信息
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.select("name","age","email");
        userMapper.selectMaps(wrapper).forEach(System.out::println);
    }
}
```

### 组装子查询

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testSubQuery() {
        //查询id小于等于100的用户信息
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.inSql("id","select id from t_user where id <= 100");
        userMapper.selectList(wrapper).forEach(System.out::println);

    }
}
```

### condition 组装条件

在真正开发的过程中，组装条件是常见的功能，而这些条件数据来源于用户输入，是可选的，因此在组装这些条件时，必须先判断用户是否选择了这些条件，若选择则需要组装该条件，若 没有选择则一定不能组装，以免影响SQL执行的结果

```java
@SpringBootTest
class QueryWrapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testCondition() {
        String username = "";
        Integer ageBegin = 20;
        Integer ageEnd = 30;

        //不使用condition组装条件
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        if (StringUtils.isNotBlank(username)){
            //isNotBlank判断某个字符串是否不为空字符串，不为null，不为空白符
            wrapper.like("name",username);
        }
        if (ageBegin != null){
            wrapper.ge("age",ageBegin);
        }
        if (ageEnd != null){
            wrapper.le("age",ageEnd);
        }
        userMapper.selectList(wrapper).forEach(System.out::println);

        //使用condition组装条件
        QueryWrapper<User> wrapper1 = new QueryWrapper<>();
        wrapper1.like(StringUtils.isNotBlank(username),"name",username)
                .ge(ageBegin != null,"age",ageBegin)
                .le(ageEnd != null,"age",ageEnd);
        userMapper.selectList(wrapper).forEach(System.out::println);
    }
}
```

## UpdateWrapper

UpdateWrapper设置修改的条件、设置要修改的字段。

:::warning 说明

建议使用UpdateWrapper就可以不使用实体类了。

:::

```java
@SpringBootTest
public class UpdateWrapperTest {
    @Autowired
    private UserMapper userMapper;
    @Test
    void testUpdateWrapper() {
        //将用户名中包含有a并且 年龄大于20或邮箱为null的用户信息修改
        UpdateWrapper<User> wrapper = new UpdateWrapper<>();
        wrapper.like("name","a")
                .and(i ->i.ge("age",20).or().isNull("email"));
        wrapper.set("name","小王").set("email","4566");
        int update = userMapper.update(null, wrapper);
        System.out.println("update = " + update);
    }
}
```

## LambdaQueryWrapper

```java
@SpringBootTest
class LambdaQueryWrapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testInsert() {
    }

    @Test
    void testDelete() {
        //删除邮箱地址为null的用户信息
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.isNull(User::getEmail);
        int delete = userMapper.delete(wrapper);
        System.out.println("delete = " + delete);
    }

    @Test
    void testUpdate() {
        //将年龄大于20并且用户名中包含有a 或 邮箱为null的用户信息修改
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.gt(User::getAge, 20)
                .like(User::getUsername, "a")
                .or()
                .isNull(User::getEmail);
        User user = new User();
        user.setUsername("小白");
        user.setEmail("232332");
        int result = userMapper.update(user, wrapper);
        System.out.println("result = " + result);
    }

    @Test
    void test() {
        //将年龄大于20并且用户名中包含有a 或 邮箱为null的用户信息修改
        //lambda中的条件优先执行
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(User::getUsername, "a")
                .and(i->i.gt(User::getAge,20).or().isNull(User::getEmail));
        User user = new User();
        user.setUsername("小白");
        user.setEmail("232332");
        int result = userMapper.update(user, wrapper);
        System.out.println("result = " + result);
    }

    @Test
    void testSort() {
        //查询用户信息，按照年龄的降序排序，若年龄相同，则按照id升序排序
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByDesc(User::getAge)
                .orderByAsc(User::getUid);
        userMapper.selectList(wrapper).forEach(System.out::println);
    }

    //组装查询条件
    @Test
    void testSelect() {
        // 查询用户名包含a 年龄在20到30之间 邮箱信息不为null的信息
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(User::getUsername, "a")
                .between(User::getAge, 20, 30)
                .isNotNull(User::getEmail);
        userMapper.selectList(wrapper).forEach(System.out::println);
    }

    //组装select子句

    @Test
    void testSelect1() {
        //查询用户的用户名、年龄、邮箱信息
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.select(User::getUsername,User::getAge,User::getEmail);
        userMapper.selectMaps(wrapper).forEach(System.out::println);
    }

    @Test
    void testSubQuery() {
        //查询id小于等于100的用户信息
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.inSql(User::getUid,"select id from t_user where id <= 100");
        userMapper.selectList(wrapper).forEach(System.out::println);

    }

    @Test
    void testCondition() {
        String username = "";
        Integer ageBegin = 20;
        Integer ageEnd = 30;

        //不使用condition组装条件
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        if (StringUtils.isNotBlank(username)){
            //isNotBlank判断某个字符串是否不为空字符串，不为null，不为空白符
            wrapper.like(User::getUsername,username);
        }
        if (ageBegin != null){
            wrapper.ge(User::getAge,ageBegin);
        }
        if (ageEnd != null){
            wrapper.le(User::getAge,ageEnd);
        }
        userMapper.selectList(wrapper).forEach(System.out::println);
        //使用condition组装条件
        LambdaQueryWrapper<User> wrapper1 = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.isNotBlank(username),User::getUsername,username)
                .ge(ageBegin != null,User::getAge,ageBegin)
                .le(ageEnd != null,User::getAge,ageEnd);
    }
}
```

## LambdaUpdateWrapper

```java
@SpringBootTest
public class LambdaUpdateWrapperTest {
    @Autowired
    private UserMapper userMapper;
    @Test
    void testUpdateWrapper() {
        //将用户名中包含有a并且 年龄大于20或邮箱为null的用户信息修改
        LambdaUpdateWrapper<User> wrapper = new LambdaUpdateWrapper<>();
        wrapper.like(User::getUsername,"a")
                .and(i ->i.ge(User::getAge,20).or().isNull(User::getEmail));
        wrapper.set(User::getUsername,"小王").set(User::getEmail,"4566");
        int update = userMapper.update(null, wrapper);
        System.out.println("update = " + update);
    }
}
```
