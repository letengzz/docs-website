# MyBatis 基本操作

:::tip 提示

下列各项操作均使用[user表](Table/user.md)来操作。

:::

## 执行SQL的两种方式

MyBatis 有两种执行 SQL 语句的方式：

1. 通过 SqlSession 发送 SQL
2. 通过 SqlSession 获取 Mapper 接口，通过 Mapper 接口发送 SQL

:::warning 说明

建议使用Mapper接口发送SQL语句的方式：

- 使用 Mapper 接口编程可以消除 SqlSession 带来的功能性代码，提高可读性，而 SqlSession 发送 SQL，需要一个 SQL id 去匹配 SQL，比较晦涩难懂。
- 使用 Mapper 接口，类似 `websiteMapper.getWebsite(1)` 则是完全面向对象的语言，更能体现业务的逻辑。
- 使用 `websiteMapper.getWebsite(1)` 方式，IDE 会提示错误和校验，而使用 `sqlSession.selectOne("getWebsite",1L)` 语法，只有在运行中才能知道是否会产生错误。

:::

### SqlSession发送SQL

SqlSession发送SQL这是 MyBatis 前身 iBatis 所留下的方式(不推荐)。

通过SqlSession发送SQL语句不需要定义mapper(dao)接口，可以直接**通过 "命名空间 + id" 的方式发送SQL语句**

### Mapper接口发送 SQL

可以通过SqlSession获取Mapper接口，再通过Mapper接口发送SQL语句。

**需要定义mapper接口**，并在接口中**定义抽象方法**，通过**获取mapper接口对象，再调用方法的形式发送SQL语句**

因为 XML 文件或者接口注解定义的 SQL 都可以通过"**类的全限定名+方法名**"查找，所以 MyBatis 会启用对应的 SQL 运行，并返回结果。

**例**：

```java
 //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
SqlSessionFactory sqlSessionFactory = sqlSessionFactoryBuilder.build(is);

//创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
//SqlSession sqlSession = sqlSessionFactory.openSession();
//创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
SqlSession sqlSession = sqlSessionFactory.openSession(true);

//通过代理模式创建UserMapper接口的代理实现类对象
UserMapper userMapper = sqlSession.getMapper(UserMapper.class);

//调用UserMapper接口中的方法，就可以根据UserMapper的全类名匹配元素文件，通过调用的方法名匹配
//映射文件中的SQL标签，并执行标签中的SQL语句

//执行添加操作：
userMapper.insertUser();
```

## 获取参数的两种方式

MyBatis获取参数值的两种方式：`${}`和`#{}`

- `${}`的本质就是**字符串拼接**，${}使用字符串拼接的方式拼接sql，若为字符串类型或日期类型的字段进行赋值时，需要手动加单引号。
- `#{}`的本质就是**占位符赋值**，#{}使用占位符赋值的方式拼接sql，此时为字符串类型或日期类型的字段进行赋值时，可以自动添加单引号。

### 单个字面量类型的参数

若mapper接口中的方法参数为单个的字面量类型，此时可以使用`${}`和`#{}`以任意的名称获取参数的值

:::danger 注意

`${}`需要手动加单引号。

:::

```xml
<insert id="insertUserForName" parameterType="String">
	<!-- insert into user(username) values (#{username}) -->
    insert into user(username) values ('${username}')
</insert>
```

### 多个字面量的参数

若mapper接口中的方法参数为多个时，此时MyBatis会自动将这些参数放在一个map集合中，以arg0,arg1...为键，以参数为值；以 param1,param2...为键，以参数为值；因此只需要通过`${}`和`#{}`访问map集合的键就可以获取相对应的值

:::danger 注意

`${}`需要手动加单引号。

:::

```xml
<insert id="insertUser">
	<!-- insert into user(username, password, age)values (#{arg0}, #{arg1}, #{arg2}) -->
    insert into user(username, password, age)values (#{param1}, #{param2}, #{param3})
</insert>
```

### map集合类型的参数

若mapper接口中的方法需要的参数为多个时，此时可以手动创建map集合，将这些数据放在map中 只需要通过`${}`和`#{}`访问map集合的键就可以获取相对应的值。

:::danger 注意

`${}`需要手动加单引号。

:::

```xml
<insert id="insertUserByMap" parameterType="map">
	insert into user(username, password, age) values (#{username}, #{password}, #{age})
</insert>
```

### 实体类类型的参数

若mapper接口中的方法参数为实体类对象时 此时可以使用`${}`和`#{}`，通过访问实体类对象中的属性名获取属性值

:::danger 注意

`${}`需要手动加单引号。

:::

```xml
<insert id="insertUserByBean" parameterType="com.hjc.demo.pojo.User">
	insert into user(username,password,age) values (#{username},#{password},#{age})
</insert>
```

### 使用注解标识参数

可以通过[`@Param`注解](Annotation.md#@Param:映射多个参数)标识mapper接口中的方法参数 此时，会将这些参数放在map集合中，以@Param注解的value属性值为键，以参数为值；以 param1,param2...为键，以参数为值；只需要通过`${}`和`#{}`访问map集合的键就可以获取相对应的值

:::danger 注意

`${}`需要手动加单引号。

:::

```xml
<insert id="insertUserByParam">
	insert into user(username,password,age) values (#{username},#{password},#{age})
</insert>
```

## 插入标签

MyBatis通过 insert 标签用来定义插入语句，执行插入操作。

:::warning 说明

当返回值设置为int返回其影响数据库的行数，设置为void，则不获取受影响数据库的行数。

:::

**insert 标签常用属性**：

![图片1](assets/202303011038287.png)

:::danger 注意

insert 标签中没有 resultType 属性，只有查询操作才需要对返回结果类型进行相应的指定。

:::

### 传递单个参数

1. mapper接口中定义一个`insertUserForName()`方法：

   ```java [UserMapper.java]
   /**
   * 添加用户(只添加用户名)
   * @param username 用户名
   * @return SQL受影响行数
   */
   int insertUserForName(String username);
   ```

2. mapper映射文件中增加插入语句：

   ```xml [UserMapper.xml]
   <!-- 只添加用户名-->
   <insert id="insertUserForName" parameterType="String">
   	insert into user(username) values (#{username})
   </insert>
   ```

3. 测试代码：

   ```java
   @Test
   public void testInsert() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行插入操作
       int result = mapper.insertUserForName("张三");
   	System.out.println("共插入" + result + "条数据");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: insert into user(username) values (?)
   >
   > DEBUG ==> Parameters: 张三(String)
   >
   > DEBUG <== Updates: 1
   >
   > 共插入1条数据

### 传递多个参数

Mybatis 实现给映射器传递多个参数：

- 使用 Map 传递参数
- 使用注解传递参数
- 使用 JavaBean 传递参数

3 种方式的区别：

- 使用 Map 传递参数会导致业务可读性的丧失，继而导致后续扩展和维护的困难，所以在实际应用中我们应该果断废弃该方式。
- 使用 @Param 注解传递参数会受到参数个数的影响。当 n≤5 时，它是最佳的传参方式，因为它更加直观；当 n>5 时，多个参数将给调用带来困难。
- 当参数个数大于 5 个时，建议使用 JavaBean 方式。

#### 使用 Map 传递参数

可以将参数封装到一个 Map 对象中，然后传递给 MyBatis 的映射器：

1. mapper接口中定义一个`insertUserByMap()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用Map传递参数
   * @param params 存放数据的map集合
   * @return SQL受影响行数
   */
   int insertUserByMap(Map<String, Object> params);
   ```

2. mapper映射文件中增加插入语句：

   ```xml [UserMapper.xml]
   <!--接收 Map 参数-->
   <insert id="insertUserByMap" parameterType="map">
   	insert into user(username,password,age) values (#{username},#{password},#{age})
   </insert>
   ```

3. 测试代码：

   ```java
   @Test
   public void testInsertByMap() throws IOException {
   	//读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);

       //定义map集合 key必须与xml中的#{}一致
       Map<String,Object> map = new HashMap<>();
       map.put("username","Boss");
       map.put("password","456456");
       map.put("age",44);
       //执行插入操作
       int result = mapper.insertUserByMap(map);
       System.out.println("通过 Map 成功向数据库中添加了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: insert into user(username,password,age) values (?,?,?)
   >
   > DEBUG ==> Parameters: Boss(String), 456456(String), 44(Integer)
   >
   > DEBUG <== Updates: 1
   >
   > 通过 Map 成功向数据库中添加了 1 条记录

#### 使用注解传递参数

可以使用 MyBatis 提供的[`@Param`注解](Annotation.md#@Param:映射多个参数)给注解器传递参数。

1. mapper接口中定义一个`insertUserByParam()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用注解传递参数
   * @param username 账号
   * @param password 密码
   * @param age 年龄
   * @return SQL受影响行数
   */
   int insertUserByParam(@Param("username") String username,@Param("password") String password,@Param("age") Integer age);
   ```

2. mapper映射文件中增加插入语句：

   ```xml [UserMapper.xml]
   <insert id="insertUserByParam">
   	insert into user(username,password,age) values (#{username},#{password},#{age})
   </insert>
   ```

3. 测试代码：

   ```java
   @Test
   public void testInsertByParam() throws IOException {
   	//读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);

       int result = mapper.insertUserByParam("Admin", "121212", 78);
       System.out.println("通过注解成功向数据库中添加了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: insert into user(username,password,age) values (?,?,?)
   >
   > DEBUG ==> Parameters: Admin(String), 121212(String), 78(Integer)
   >
   > DEBUG <== Updates: 1
   >
   > 通过注解成功向数据库中添加了 1 条记录

#### 使用 JavaBean 传递参数

在参数过多的情况下，我们可以将参数通过 setter 方法封装到 JavaBean(实体类)对象中 ，传递给映射器：

1. mapper接口中定义一个`insertUserByBean()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用Bean传递参数
   * @param user Bean对象
   * @return SQL受影响行数
   */
   int insertUserByBean(User user);
   ```

2. mapper映射文件中增加插入语句：

   ```xml [UserMapper.xml]
   <insert id="insertUserByBean" parameterType="com.hjc.demo.pojo.User">
   	insert into user(username,password,age) values (#{username},#{password},#{age})
   </insert>
   ```

3. 测试代码：

   ```java
   @Test
   public void testInsertByBean() throws IOException {
   	//读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行插入操作
   	int result = mapper.insertUserByBean(new User(null,"user","password",19));
       System.out.println("通过JavaBean成功向数据库中添加了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: insert into user(username,password,age) values (?,?,?)
   >
   > DEBUG ==> Parameters: user(String), password(String), 19(Integer)
   >
   > DEBUG <== Updates: 1
   >
   > 通过JavaBean成功向数据库中添加了 1 条记录

### 主键(自动递增)回填

MySQL、SQL Server 等数据库表可以采用自动递增的字段作为其主键，当向这样的数据库表插入数据时，即使不指定自增主键的值，数据库也会根据自增规则自动生成主键并插入到表中。

一些特殊情况下，可能需要将这个刚刚生成的主键回填到请求对象（原本不包含主键信息的请求对象）中，供其他业务使用。此时，可以通过在 insert 标签中添加 keyProperty 和 useGeneratedKeys 属性，来实现该功能。

- useGeneratedKeys：设置当前标签中的sql使用了自增的主键
- keyProperty：将自增的主键的值赋值给传输到映射文件中参数的某个属性

**例**：

1. mapper接口中定义一个`insertUserForId()`方法：

   ```java [UserMapper.java]
   /**
   * 主键(自动递增)回填
   * @param user Bean对象
   * @return SQL受影响行数
   */
   int insertUserForId(User user);
   ```

2. mapper映射文件中增加插入语句：

   ```xml [UserMapper.xml]
   <insert id="insertUserForId" parameterType="com.hjc.demo.pojo.User" keyProperty="id" useGeneratedKeys="true">
   	insert into user(username,password,age) values (#{username},#{password},#{age})
   </insert>
   ```

3. 测试代码：

   ```java
   @Test
   public void testInsertForId() throws IOException {
   	//读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);

       //添加用户信息(除id)
       User user = new User();
       user.setUsername("哈利波特");
       user.setPassword("456566");
       user.setAge(19);
       //执行插入
       int result = mapper.insertUserForId(user);
       System.out.println("添加了 " + result + " 条记录");
       //获取回填的主键
       System.out.println("添加记录的主键是:" + user.getId());

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: insert into user(username,password,age) values (?,?,?)
   >
   > DEBUG ==> Parameters: 哈利波特(String), 456566(String), 19(Integer)
   >
   > DEBUG <== Updates: 1
   >
   > 添加了 1 条记录
   >
   > 添加记录的主键是:11

### 自定义主键

如果在实际项目中，若数据库不支持主键自动递增（例如 Oracle），或者取消了主键自动递增的规则，我们可以使用 MyBatis 的 selectKey 标签自定义生成主键。

**selectKey 标签中属性说明**：

- keyProperty：用于指定主键值对应的 POJO 类的属性。
- order：该属性取值可以为 BEFORE 或 AFTER。
  - BEFORE 表示先执行 selectKey 标签内的语句，再执行插入语句
  - AFTER 表示先执行插入语句再执行 selectKey 标签内的语句

**例**：

1. mapper接口中定义一个`insertUserByCustom()`方法：

   ```java [UserMapper.java]
   /**
   * 自定义主键
   * @param user Bean对象
   * @return SQL受影响行数
   */
   int insertUserByCustom(User user);
   ```

2. mapper映射文件中增加插入语句：

   ```xml [UserMapper.xml]
   <insert id="insertUserByCustom" parameterType="com.hjc.demo.pojo.User">
   	<!-- 先使用selectKey标签定义主键，然后再定义SQL语句 -->
       <selectKey keyProperty="id"  resultType="Integer" order="AFTER">
       	select if(max(id) is null,1,max(id)+1) as newId from user
       </selectKey>
           insert into user(id,username,password,age) values (#{id},#{username},#{password},#{age})
   </insert>
   ```

3. 测试代码：

   ```java
   @Test
   public void testInsertByCustom() throws IOException {
   	//读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);

       //添加用户信息(除id)
       User user = new User();
       user.setUsername("陈申");
       user.setPassword("4561566");
       user.setAge(21);
       //执行插入
       int result = mapper.insertUserByCustom(user);
       System.out.println("添加了 " + result + " 条记录");
       //获取回填的主键
       System.out.println("添加记录的主键是:" + user.getId());

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: insert into user(id,username,password,age) values (?,?,?,?)
   >
   > DEBUG ==> Parameters: null, 陈申(String), 4561566(String), 21(Integer)
   >
   > DEBUG <== Updates: 1
   >
   > DEBUG ==> Preparing: select if(max(id) is null,1,max(id)+1) as newId from user
   >
   > DEBUG ==> Parameters:
   >
   > DEBUG <== Total: 1
   >
   > 添加了 1 条记录
   >
   > 添加记录的主键是:15

## 更新标签

MyBatis update 标签用于定义更新语句，执行更新操作。

:::warning 说明

当返回值设置为int返回其影响数据库的行数，设置为void，则不获取受影响数据库的行数。

:::

**update 标签常用属性**：

![图片1](assets/202303011058380.png)

:::danger 注意

update 标签中没有 resultType 属性，只有查询操作才需要对返回结果类型进行相应的指定。

:::

### 传递单个参数

1. mapper接口中定义一个`updateUserForName()`方法：

   ```java [UserMapper.java]
   /**
   * 通过名字更改密码为123123
   * @param username 用户名
   * @return SQL受影响行数
   */
   int updateUserForName(String username);
   ```

2. mapper映射文件中增加更新语句：

   ```xml [UserMapper.xml]
   <update id="updateUserForName" parameterType="string">
   	update user set password = '123123' where username = #{username}
   </update>
   ```

3. 测试代码：

   ```java
   @Test
   public void testUpdate() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行更新
       int result = mapper.updateUserForName("刘备");
       System.out.println("更新了 " + result + " 条记录");
       // 关闭SqlSession
       sqlSession.close();
   }

   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: update user set password = '123123' where username = ?
   >
   > DEBUG ==> Parameters: 刘备(String)
   >
   > DEBUG <== Updates: 1
   >
   > 更新了 1 条记录

### 传递多个参数

Mybatis 实现给映射器传递多个参数：

- 使用 Map 传递参数
- 使用注解传递参数
- 使用 JavaBean 传递参数

3 种方式的区别：

- 使用 Map 传递参数会导致业务可读性的丧失，继而导致后续扩展和维护的困难，所以在实际应用中我们应该果断废弃该方式。
- 使用 @Param 注解传递参数会受到参数个数的影响。当 n≤5 时，它是最佳的传参方式，因为它更加直观；当 n>5 时，多个参数将给调用带来困难。
- 当参数个数大于 5 个时，建议使用 JavaBean 方式。

#### 使用 Map 传递参数

我们可以将参数封装到一个 Map 对象中，然后传递给 MyBatis 的映射器，示例如下。

1. mapper接口中定义一个`updateUserByMap()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用Map传递参数
   * @param params 存放数据的map集合
   * @return SQL受影响行数
   */
   int updateUserByMap(Map<String, Object> params);

   ```

2. mapper映射文件中增加更新语句：

   ```xml [UserMapper.xml]
   <update id="updateUserByMap" parameterType="map">
   	update user set username = #{username},password = #{password},age = #{age} where id = #{id}
   </update>
   ```

3. 测试代码：

   ```java
   @Test
   public void testUpdateByMap() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       Map<String,Object> map = new HashMap<>();
       map.put("id",1);
       map.put("username","刘邦");
       map.put("password","49111");
       map.put("age",30);
       //执行更新
       int result = mapper.updateUserByMap(map);
       System.out.println("通过 Map 成功向数据库中更新了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close()
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: update user set username = ?,password = ?,age = ? where id = ?
   >
   > DEBUG ==> Parameters: 刘邦(String), 49111(String), 30(Integer), 1(Integer)
   >
   > DEBUG <== Updates: 1
   >
   > 通过 Map 成功向数据库中更新了 1 条记录

#### 使用注解传递参数

我们还可以使用 MyBatis 提供的[`@Param`注解](Annotation.md#@Param:映射多个参数)注解给注解器传递参数。

1. mapper接口中定义一个`updateUserByParam()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用注解传递参数
   * @param username 账号
   * @param password 密码
   * @param age 年龄
   * @param id id
   * @return SQL受影响行数
   */
   int updateUserByParam(@Param("username") String username,@Param("password") String password,@Param("age") Integer age,@Param("id") Integer id);
   ```

2. mapper映射文件中增加更新语句：

   ```xml [UserMapper.xml]
   <update id="updateUserByParam">
   	update user set username = #{username},password = #{password},age = #{age} where id = #{id}
   </update>
   ```

3. 测试代码：

   ```java
   @Test
   public void testUpdateByParam() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行更新
       int result = mapper.updateUserByParam("孔刘","787878",20,1);
       System.out.println("通过注解成功向数据库中更新了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: update user set username = ?,password = ?,age = ? where id = ?
   >
   > DEBUG ==> Parameters: 孔刘(String), 787878(String), 20(Integer), 1(Integer)
   >
   > DEBUG <== Updates: 1
   >
   > 通过注解成功向数据库中更新了 1 条记录

#### 使用 JavaBean 传递参数

在参数过多的情况下，我们还可以将参数通过 setter 方法封装到 JavaBean（实体类）对象中传递给映射器。

1. mapper接口中定义一个`updateUserByBean()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用Bean传递参数
   * @param user Bean对象
   * @return SQL受影响行数
   */
   int updateUserByBean(User user);
   ```

2. mapper映射文件中增加更新语句：

   ```xml [UserMapper.xml]
   <update id="updateUserByBean" parameterType="com.hjc.demo.pojo.User">
   	update user set username = #{username},password = #{password},age = #{age} where id = #{id}
   </update>
   ```

3. 测试代码：

   ```java
   @Test
   public void testUpdateByBean() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行更新
   	int result = mapper.updateUserByBean(new User(2,"user","password",19));
   	System.out.println("通过JavaBean成功向数据库中更新了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: update user set username = ?,password = ?,age = ? where id = ?
   >
   > DEBUG ==> Parameters: user(String), password(String), 19(Integer), 2(Integer)
   >
   > DEBUG <== Updates: 1
   >
   > 通过JavaBean成功向数据库中更新了 1 条记录

## 删除标签

MyBatis delete 标签用于定义 delete 语句，执行删除操作。

:::warning 说明

当返回值设置为int返回其影响数据库的行数，设置为void，则不获取受影响数据库的行数。

:::

**delete 标签常用属性**：

![图片2](assets/202303011102074.png)

:::danger 注意

delete 标签中没有 resultType 属性，只有查询操作才需要对返回结果类型进行相应的指定。

:::

### 传递单个参数

1. mapper接口中定义一个`deleteUserForName()`方法：

   ```java [UserMapper.java]
   /**
   * 删除用户(通过用户名删除)
   * @param username 用户名
   * @return SQL受影响行数
   */
   int deleteUserForName(String username);
   ```

2. mapper映射文件中增加删除语句：

   ```xml [UserMapper.xml]
   <delete id="deleteUserForName" parameterType="string">
   	delete  from user where username = #{username}
   </delete>
   ```

3. 测试代码：

   ```java
   @Test
   public void testDelete() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行删除
       int result = mapper.deleteUserForName("关羽");
       System.out.println("共删除" + result + "条数据");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: delete from user where username = ?
   >
   > DEBUG ==> Parameters: 关羽(String)
   >
   > DEBUG <== Updates: 1
   >
   > 共删除了 1 条记录

### 传递多个参数

Mybatis 实现给映射器传递多个参数：

- 使用 Map 传递参数
- 使用注解传递参数
- 使用 JavaBean 传递参数

3 种方式的区别：

- 使用 Map 传递参数会导致业务可读性的丧失，继而导致后续扩展和维护的困难，所以在实际应用中我们应该果断废弃该方式。
- 使用 @Param 注解传递参数会受到参数个数的影响。当 n≤5 时，它是最佳的传参方式，因为它更加直观；当 n>5 时，多个参数将给调用带来困难。
- 当参数个数大于 5 个时，建议使用 JavaBean 方式。

#### 使用 Map 传递参数

我们可以将参数封装到一个 Map 对象中，然后传递给 MyBatis 的映射器。

1. mapper接口中定义一个`deleteUserByMap()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用Map传递参数
   * @param params 存放数据的map集合
   * @return SQL受影响行数
   */
   int deleteUserByMap(Map<String, Object> params);
   ```

2. mapper映射文件中增加删除语句：

   ```xml [UserMapper.xml]
   <delete id="deleteUserByMap">
   	delete  from user where username = #{username} and password = #{password}
   </delete>
   ```

3. 测试代码：

   ```java
   @Test
   public void testDeleteByMap() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       Map<String,Object> map = new HashMap<>();
       map.put("username","张飞");
       map.put("password","124356");
       //执行删除
       int result = mapper.deleteUserByMap(map);
       System.out.println("通过 Map 成功向数据库中删除了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: delete from user where username = ? and password = ?
   >
   > DEBUG ==> Parameters: 张飞(String), 124356(String)
   >
   > DEBUG <== Updates: 1
   >
   > 通过 Map 成功向数据库中删除了 1 条记录

#### 使用注解传递参数

可以使用 MyBatis 提供的[`@Param`注解](Annotation.md#@Param:映射多个参数)注解给注解器传递参数。

1. mapper接口中定义一个`deleteUserByParam()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用注解传递参数
   * @param username 账号
   * @param password 密码
   * @return SQL受影响行数
   */
   int deleteUserByParam(@Param("username") String username,@Param("password") String password);
   ```

2. mapper映射文件中增加删除语句：

   ```xml [UserMapper.xml]
   <delete id="deleteUserByParam">
   	delete  from user where username = #{username} and password = #{password}
   </delete>
   ```

3. 测试代码：

   ```java
   @Test
   public void testDeleteByParam() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行删除
       int result = mapper.deleteUserByParam("张飞","124356");
       System.out.println("通过注解成功向数据库中删除了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: delete from user where username = ? and password = ?
   >
   > DEBUG ==> Parameters: 张飞(String), 124356(String)
   >
   > DEBUG <== Updates: 1
   >
   > 通过注解成功向数据库中删除了 1 条记录

#### 使用 JavaBean 传递参数

在参数过多的情况下，我们还可以将参数通过 setter 方法封装到 JavaBean（实体类）对象中传递给映射器。

1. mapper接口中定义一个`deleteUserByBean()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用Bean传递参数
   * @param user Bean对象
   * @return SQL受影响行数
   */
   int deleteUserByBean(User user);
   ```

2. mapper映射文件中增加删除语句：

   ```xml [UserMapper.xml]
   <delete id="deleteUserByBean">
   	delete  from user where username = #{username} and password = #{password}
   </delete>
   ```

3. 测试代码：

   ```java
   @Test
   public void testDeleteByBean() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行删除
       int result = mapper.deleteUserByBean(new User(null,"张飞","124356",21));
       System.out.println("通过JavaBean成功向数据库中删除了 " + result + " 条记录");

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: delete from user where username = ? and password = ?
   >
   > DEBUG ==> Parameters: 张飞(String), 124356(String)
   >
   > DEBUG <== Updates: 1
   >
   > 通过JavaBean成功向数据库中删除了 1 条记录

## 查询标签

在 MyBatis 中，select 标签是最常用也是功能最强大的 SQL 语言，用于执行查询操作。

**select 标签常用属性**：

![图片3](assets/202303011105702.png)

:::danger 注意

查询功能必须设置resultType(结果类型)或resultMap(结果映射)

:::

### 传递单个参数

1. mapper接口中定义一个`selectUserForName()`方法：

   ```java [UserMapper.java]
   /**
   * 通过用户名查询
   * @param username 用户名
   * @return User 返回数据
   */
   User selectUserForName(@Param("username")String username);
   ```

2. mapper映射文件中增加查询语句：

   ```xml [UserMapper.xml]
   <select id="selectUserForName" resultType="com.hjc.demo.pojo.User">
   	select id,username,password,age from user where username like concat('%',#{username},'%');
   </select>
   ```

3. 测试代码：

   ```java
   @Test
   public void testSelect() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行查询操作
       User user = mapper.selectUserForName("关");
       if (user != null) {
               System.out.println("id:" + user.getId() + ",用户名:" + user.getUsername() + ",密码:" + user.getPassword() + ",年龄:" + user.getAge());
           }

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG 02-01 15:46:42,003 ==> Preparing: select id,username,password,age from user where username like concat('%',?,'%');
   >
   > DEBUG 02-01 15:46:42,033 ==> Parameters: 关(String)
   >
   > DEBUG 02-01 15:46:42,074 <== Total: 1
   >
   > id:18,用户名:关羽,密码:123456,年龄:20

### 传递多个参数

Mybatis 实现给映射器传递多个参数：

- 使用 Map 传递参数
- 使用注解传递参数
- 使用 JavaBean 传递参数

3 种方式的区别：

- 使用 Map 传递参数会导致业务可读性的丧失，继而导致后续扩展和维护的困难，所以在实际应用中我们应该果断废弃该方式。
- 使用 @Param 注解传递参数会受到参数个数的影响。当 n≤5 时，它是最佳的传参方式，因为它更加直观；当 n>5 时，多个参数将给调用带来困难。
- 当参数个数大于 5 个时，建议使用 JavaBean 方式。

#### 使用Map传递参数

使用 MyBatis 提供的 Map 接口作为参数实现。

:::tip 提示

使用 Map 传递参数虽然简单易用，但是由于这样设置参数需要键值对应，业务关联性不强，开发人员需要深入到程序中看代码，造成可读性下降。

:::

1. mapper接口中定义一个`selectUserByMap()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用Map传递参数
   * @param params 存放数据的map集合
   * @return SQL受影响行数
   */
   List<User> selectUserByMap(Map<String, Object> params);
   ```

2. mapper映射文件中增加查询语句：

   ```xml [UserMapper.xml]
   <select id="selectUserByMap" resultType="com.hjc.demo.pojo.User">
   	select id,username,password,age from user where username like concat('%',#{username},'%') and password like concat('%',#{password},'%')
   </select>
   ```

3. 测试代码：

   ```java
   @Test
   public void testSelectByMap() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       Map<String,Object> map = new HashMap<>();
       map.put("username","飞");
       map.put("password","124");
       //执行查询操作
       List<User> users = mapper.selectUserByMap(map);
       users.forEach(System.out::println);

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: select id,username,password,age from user where username like concat('%',?,'%') and password like concat('%',?,'%')
   >
   > DEBUG ==> Parameters: 飞(String), 124(String)
   >
   > DEBUG <== Total: 1
   >
   > `User{id=19, username='张飞', password='124356', age=19}`

#### 使用注解传递参数

使用 MyBatis 的注解[`@Param`注解](Annotation.md#@Param:映射多个参数)传递参数。

:::warning 说明

把参数传递给后台时，MyBatis 通过 `@Param` 提供的名称就会知道 `#{name}` 代表 name 参数，提高了参数可读性。但是如果这条 SQL 拥有 10 个参数的查询，就会造成可读性下降，增强了代码复杂性。

:::

1. mapper接口中定义一个`selectUserByParam()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用注解传递参数
   * @param username 账号
   * @param password 密码
   * @return SQL受影响行数
   */
   List<User> selectUserByParam(@Param("username") String username,@Param("password") String password);
   ```

2. mapper映射文件中增加查询语句：

   ```xml [UserMapper.xml]
   <select id="selectUserByParam" resultType="com.hjc.demo.pojo.User">
   	select id,username,password,age from user where username like concat('%',#{username},'%') and password like concat('%',#{password},'%')
   </select>
   ```

3. 测试代码：

   ```java
   @Test
   public void testSelectByParam() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行查询操作
       List<User> list = mapper.selectUserByParam("刘", "123");
       list.forEach(System.out::println);

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: select id,username,password,age from user where username like concat('%',?,'%') and password like concat('%',?,'%')
   >
   > DEBUG ==> Parameters: 刘(String), 123(String)
   >
   > DEBUG <== Total: 1
   >
   > `User{id=17, username='刘备', password='456123', age=23}`

#### 使用JavaBean传递参数

在参数过多的情况下，MyBatis 允许组织一个 JavaBean，通过简单的 setter 和 getter 方法设置参数，提高可读性。

**例**：

1. mapper接口中定义一个`deleteUserByMap()`方法：

   ```java [UserMapper.java]
   /**
   * 多个参数时使用Bean传递参数
   * @param user Bean对象
   * @return SQL受影响行数
   */
   List<User> selectUserByBean(User user);
   ```

2. mapper映射文件中增加查询语句：

   ```xml [UserMapper.xml]
   <select id="selectUserByBean" resultType="com.hjc.demo.pojo.User">
   	 select id,username,password,age from user where username like concat('%',#{username},'%') and password like concat('%',#{password},'%')
   </select>
   ```

3. 测试代码：

   ```java
   @Test
   public void testInsert() throws IOException {
       //读取MyBatis的核心配置文件
       InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = build.openSession(true);
       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper mapper = sqlSession.getMapper(UserMapper.class);
       //执行查询操作
       List<User> list = mapper.selectUserByBean(new User(null,"刘","123",null));
       list.forEach(System.out::println);

       // 关闭SqlSession
       sqlSession.close();
   }
   ```

4. 执行测试代码，控制台输出：

   > DEBUG ==> Preparing: select id,username,password,age from user where username like concat('%',?,'%') and password like concat('%',?,'%')
   >
   > DEBUG ==> Parameters: 刘(String), 123(String)
   >
   > DEBUG <== Total: 1
   >
   > `User{id=17, username='刘备', password='456123', age=23}`

## resultType和resultMap

#### resultType

使用resultType进行输出映射，只有查询出来的列名和pojo中的属性名一致，该列才可以映射成功。

如果查询出来的列名和pojo中的属性名全部不一致，没有创建pojo对象。

只要查询出来的列名和pojo中的属性有一个一致，就会创建pojo对象。

#### resultMap

resultMap 是 MyBatis 中最复杂的元素，主要用于解决实体类属性名与数据库表中字段名不一致的情况，可以将查询结果映射成实体对象。

如果字段名和属性名不一致的情况下才需要用到resultMap 一对多和多对一的关系也需要用到resultmap

> 现有的 MyBatis 版本只支持 resultMap 查询，不支持更新或者保存，更不必说级联的更新、删除和修改。

resultMap 元素还可以包含以下子元素：

```xml
<resultMap id="" type="">
    <constructor><!-- 类在实例化时用来注入结果到构造方法 -->
        <idArg/><!-- ID参数，结果为ID -->
        <arg/><!-- 注入到构造方法的一个普通结果 -->
    </constructor>
    <id/><!-- 用于表示哪个列是主键 -->
    <result/><!-- 注入到字段或JavaBean属性的普通结果 -->
    <association property=""/><!-- 用于一对一关联 -->
    <collection property=""/><!-- 用于一对多、多对多关联 -->
    <discriminator javaType=""><!-- 使用结果值来决定使用哪个结果映射 -->
        <case value=""/><!-- 基于某些值的结果映射 -->
    </discriminator>
</resultMap>
```

其中：

- resultMap 元素的 type 属性表示需要的 POJO，id 属性是 resultMap 的唯一标识。
- 子元素 constructor 用于配置构造方法。当一个 POJO 没有无参数构造方法时使用。
- 子元素 id 用于表示哪个列是主键。允许多个主键，多个主键称为联合主键。
- 子元素 result 用于表示 POJO 和 SQL 列名的映射关系。
- 子元素 association、collection 和 discriminator 用在级联的情况下。

id 和 result 元素属性：

| 元素        | 说明                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| property    | 映射到列结果的字段或属性。如果 POJO 的属性和 SQL 列名（column元素）是相同的，那么 MyBatis 就会映射到 POJO 上 |
| column      | 对应 SQL 列                                                                                                  |
| javaType    | 配置 Java 类型。可以是特定的类完全限定名或 MyBatis 上下文的别名                                              |
| jdbcType    | 配置数据库类型。这是 JDBC 类型，MyBatis 已经为我们做了限定，基本支持所有常用数据库类型                       |
| typeHandler | 类型处理器。允许你用特定的处理器来覆盖 MyBatis 默认的处理器。需要指定 jdbcType 和 javaType 相互转化的规则    |

一条 SQL 查询语句执行后会返回结果集，结果集有两种存储方式，即使用 Map 存储和使用 POJO 存储。

#### 区别

MyBatis 的每一个查询映射的返回类型都是 resultMap，只是当我们提供的返回类型是 resultType 时，MyBatis 会自动把对应的值赋给 resultType 所指定对象的属性，而当我们提供的返回类型是 resultMap 时，MyBatis 会将数据库中的列数据复制到对象的相应属性上，可用于复制查询。

:::danger 注意

resultMap 和 resultType 不能同时使用。

:::
