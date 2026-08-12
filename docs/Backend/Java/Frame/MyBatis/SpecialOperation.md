# MyBatis 处理特殊操作

:::tip 提示

下列各项操作均使用[student表](Table/student.md)来操作。

:::

## 处理字段和属性的映射关系

数据表中字段通常使用**下划线命名法**，而Java命名变量使用**驼峰命名法**，两者命名不同，MyBatis自动映射关联不到，字段将无法赋值到实体类中。

处理字段和属性的映射关系三种方式：

- [通过设置字段别名处理映射关系](#通过设置字段别名处理映射关系)
- [通过resultMap处理映射关系](#通过resultMap处理映射关系)
- [通过配置文件处理映射关系](#通过配置文件处理映射关系)

### 通过设置字段别名处理映射关系

只需要在SQL语句中设置同属性名相同的别名即可解决：

- mapper接口中定义一个`selectAllByAlias()`方法：

  ```java [StudentMapper.java]
  /**
  * 通过Sql起别名来解决映射问题
  * @return 所有数据
  */
  List<Student> selectAllByAlias();
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="selectAllByAlias" resultType="com.hjc.demo.pojo.Student">
  	select id,s_name sName,age,sex from student;
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testSelectByAlias() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //执行查询
      List<Student> students = mapper.selectAllByAlias();
      students.forEach(System.out::println);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select id,s_name sName,age,sex from student;
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Total: 3
  >
  > `Student{id=1, sName='小明', age=15, sex='男'}` > `Student{id=2, sName='小红', age=19, sex='女'}` > `Student{id=3, sName='小寸', age=25, sex='男'}`

### 通过resultMap处理映射关系

resultMap 是 MyBatis 中最复杂的元素，主要用于解决实体类属性名与数据库表中字段名不一致的情况，可以将查询结果映射成实体对象。

通过sql语句查询出来的数据就会通过resultMap设置的自定义映射的关系进行映射

**拓展**：[resultMap用法](Annotation.md#ResultMap)

- mapper接口中定义一个`selectAllByResultMap()`方法：

  ```java [StudentMapper.java]
  /**
  * 通过resultMap来解决映射问题
  * @return 所有数据
  */
  List<Student> selectAllByResultMap();
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <!-- 设置自定义映射关系：id：唯一标识，不能重复、type：设置映射关系中的实体类类型-->
  <resultMap id="stuResultMap" type="com.hjc.demo.pojo.Student">
  	<!-- 设置主键字段:property属性名 column表中字段名 -->
      <id property="id" column="id"/>
      <!-- 设置普通字段:property属性名 column表中字段名-->
      <result property="sName" column="s_name"/>
      <!-- 设置普通字段:property属性名 column表中字段名-->
      <result property="age" column="age"/>
      <!-- 设置普通字段:property属性名 column表中字段名-->
      <result property="sex" column="sex"/>
  </resultMap>
  <select id="selectAllByResultMap" resultMap="stuResultMap">
  	select id,s_name,age,sex from student;
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testSelectByResultMap() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //执行查询
      List<Student> students = mapper.selectAllByResultMap();
      students.forEach(System.out::println);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select id,s_name,age,sex from student;
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Total: 3
  >
  > `Student{id=1, sName='小明', age=15, sex='男'}` > `Student{id=2, sName='小红', age=19, sex='女'}` > `Student{id=3, sName='小寸', age=25, sex='男'}`

### 通过配置文件处理映射关系

MyBatis为解决此类问题，内置了将字段名中的下划线转换为Java的驼峰命名。

**拓展**：[settings用法](CoreMapping.md#配置settings标签)

- MyBatis核心配置文件：

  ```xml
  <?xml version="1.0" encoding="UTF-8" ?>
  <!DOCTYPE configuration
  PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-config.dtd">
  <configuration>
       <!-- ...-->
       <settings>
           <setting name="mapUnderscoreToCamelCase" value="true" />
       </settings>
       <!-- ...-->
  </configuration>
  ```

- mapper接口中定义一个`selectAllBySettings()`方法：

  ```java [StudentMapper.java]
  /**
  * 通过设置mapUnderscoreToCamelCase来解决映射问题
  * @return 所有数据
  */
  List<Student> selectAllBySettings();
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="selectAllBySettings" resultType="com.hjc.demo.pojo.Student">
  	select id,s_name,age,sex from student;
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testSelectBySettings() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //执行查询
      List<Student> students = mapper.selectAllBySettings();
      students.forEach(System.out::println);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select id,s_name,age,sex from student;
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Total: 3
  >
  > `Student{id=1, sName='小明', age=15, sex='男'}` > `Student{id=2, sName='小红', age=19, sex='女'}` > `Student{id=3, sName='小寸', age=25, sex='男'}`

## 批量插入大量数据

Mybatis批量插入的方式有三种

1. 普通插入
2. foreach 优化插入
3. `ExecutorType.BATCH`插入

在插入大数据量时优先选择第三种方式，`ExecutorType.BATCH`插入。

### 普通插入

默认的插入方式是遍历insert语句，单条执行，效率肯定低下，如果成堆插入，更是性能有问题。

- mapper接口中定义一个`insertOnBatch1()`方法：

  ```java [StudentMapper.java]
  /**
  * 普通插入
  * @param student
  * @return
  */
  Integer insertOnBatch1(Student student);
  ```

- mapper映射文件中增加删除语句：

  ```xml [StudentMapper.xml]
  <!-- 普通插入 -->
  <insert id="insertOnBatch1">
  	insert into student values (null,#{sName},#{age},#{sex})
  </insert>
  ```

- 测试代码：

  ```java
  @Test
  public void testDeleteMore1() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //执行批量添加
      for (int i = 0; i < 100; i++) {
          Student student = new Student();
          student.setsName("stu"+i);
          student.setAge(i);
          student.setSex("男");
      	mapper.insertOnBatch1(student);
      }

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: insert into student values (null,?,?,?)
  >
  > DEBUG ==> Parameters: stu0(String), 0(Integer), 男(String)
  >
  > DEBUG <== Updates: 1
  >
  > ......
  >
  > DEBUG ==> Preparing: insert into student values (null,?,?,?)
  >
  > DEBUG ==> Parameters: stu99(String), 99(Integer), 男(String)
  >
  > DEBUG <== Updates: 1

可以看到每个语句的执行创建一个新的预处理语句，单条提交sql，性能低下。

### foreach 优化插入

如果要优化插入速度时，可以将许多小型操作组合到一个大型操作中。理想情况下，这样可以在单个连接中一次性发送许多新行的数据，并将所有索引更新和一致性检查延迟到最后才进行。

- mapper接口中定义一个`insertOnBatch2()`方法：

  ```java [StudentMapper.java]
  /**
  * foreach插入
  * @param stus
  * @return
  */
  Integer insertOnBatch2(@Param("stus") List<Student> stus);
  ```

- mapper映射文件中增加删除语句：

  ```xml [StudentMapper.xml]
  <insert id="insertOnBatch2">
  	insert into student values
      <foreach collection="stus" item="stu" index="index" separator=",">
      	(null,#{stu.sName},#{stu.age},#{stu.sex})
  	</foreach>
  </insert>
  ```

- 测试代码：

  ```java
  @Test
  public void testDeleteMore2() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //执行批量添加
      List<Student> list = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
  		Student student = new Student();
          student.setsName("stu"+i);
          student.setAge(i);
          student.setSex("男");
      	list.add(student);
  	}
      mapper.insertOnBatch2(list);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: insert into student values (null,?,?,?) , (null,?,?,?) , (null,?,?,?) ....(null,?,?,?)
  >
  > DEBUG ==> Parameters: stu0(String), 0(Integer), 男(String),..., stu99(String), 99(Integer), 男(String)
  >
  > DEBUG <== Updates: 100

乍看上去这个foreach没有问题，但是经过项目实践发现，当表的列数较多（20+），以及一次性插入的行数较多（5000+）时，整个插入的耗时十分漫长，达到了14分钟，这是不能忍的。在资料中也提到了一句话：

> Of course don’t combine ALL of them, if the amount is HUGE. Say you have 1000 rows you need to insert, then don’t do it one at a time. You shouldn’t equally try to have all 1000 rows in a single query. Instead break it into smaller sizes.

它强调，当插入数量很多时，不能一次性全放在一条语句里。可是为什么不能放在同一条语句里呢？这条语句为什么会耗时这么久呢？查阅了资料发现：

> > Insert inside Mybatis foreach is not batch, this is a single (could become giant) SQL statement and that brings drawbacks:
>
> some database such as Oracle here does not support.
>
> in relevant cases: there will be a large number of records to insert and the database configured limit (by default around 2000 parameters per statement) will be hit, and eventually possibly DB stack error if the statement itself become too large.
>
> Iteration over the collection must not be done in the mybatis XML. Just execute a simple Insertstatement in a Java Foreach loop. The most important thing is the session Executor type.
>
> Unlike default ExecutorType.SIMPLE, the statement will be prepared once and executed for each record to insert.

从资料中可知，默认执行器类型为Simple，会为每个语句创建一个新的预处理语句，也就是创建一个`PreparedStatement`对象。在项目中，会不停地使用批量插入这个方法，而因为MyBatis对于含有的语句，无法采用缓存，那么在每次调用方法时，都会重新解析sql语句。

> Internally, it still generates the same single insert statement with many placeholders as the JDBC code above. MyBatis has an ability to cache PreparedStatement, but this statement cannot be cached because it contains element and the statement varies depending on the parameters. As a result, MyBatis has to 1) evaluate the foreach part and 2) parse the statement string to build parameter mapping [1] on every execution of this statement.
>
> And these steps are relatively costly process when the statement string is big and contains many placeholders.
>
> [1] simply put, it is a mapping between placeholders and the parameters.

从上述资料可知，耗时就耗在，由于foreach后有5000+个values，所以这个`PreparedStatement`特别长，包含了很多占位符，对于占位符和参数的映射尤其耗时。并且，查阅相关资料可知，values的增长与所需的解析时间，是呈指数型增长的。

**foreach 遇到数量大，性能瓶颈**

项目实践发现，当表的列数较多（超过20），以及一次性插入的行数较多（上万条）时，插入性能非常差，通常需要20分钟以上

![image-20230425133328250](assets/202304251345264.png)

所以，如果非要使用 foreach 的方式来进行批量插入的话，可以考虑减少一条 insert 语句中 values 的个数，最好能达到上面曲线的最底部的值，使速度最快。一般按经验来说，一次性插20~50行数量是比较合适的，时间消耗也能接受。

此外Mysql 对执行的SQL语句大小进行限制，相当于对字符串进行限制。默认允许最大SQL是 4M 。

超过限制就会抛错:

> com.mysql.jdbc.PacketTooBigException: Packet for query is too large (8346602 > 4194304). You can change this value on the server by setting the max_allowed_packet’ variable.

这个错误是 Mysql 的JDBC包抛出的,跟Mybatis框架无关，Mybatis 解析动态SQL的源码：

```java
// 开始解析
public void parse() {
    if (!configuration.isResourceLoaded(resource)) {
        configurationElement(parser.evalNode("/mapper"));
        configuration.addLoadedResource(resource);
        bindMapperForNamespace();
    }

    parsePendingResultMaps();
    parsePendingChacheRefs();
    parsePendingStatements();
}
// 解析mapper
private void configurationElement(XNode context) {
    try {
        String namespace = context.getStringAttribute("namespace");
        if (namespace.equals("")) {
            throw new BuilderException("Mapper's namespace cannot be empty");
        }
        builderAssistant.setCurrentNamespace(namespace);
        cacheRefElement(context.evalNode("cache-ref"));
        cacheElement(context.evalNode("cache"));
        parameterMapElement(context.evalNodes("/mapper/parameterMap"));
        resultMapElements(context.evalNodes("/mapper/resultMap"));
        sqlElement(context.evalNodes("/mapper/sql"));
        buildStatementFromContext(context.evalNodes("select|insert|update|delete"));
    } catch (Exception e) {
        throw new BuilderException("Error parsing Mapper XML. Cause: " + e, e);
    }
}

// 创建 select|insert|update|delete 语句
private void buildStatementFromContext(List<XNode> list, String requiredDatabaseId) {
    for (XNode context : list) {
        final XMLStatementBuilder statementParser = new XMLStatementBuilder(configuration, builderAssistant, context, requiredDatabaseId);
        try {
            statementParser.parseStatementNode();
        } catch (IncompleteElementException e) {
            configuration.addIncompleteStatement(statementParser);
        }
    }
}

// 填充参数，创建语句
public BoundSql getBoundSql(Object parameterObject) {
    DynamicContext context = new DynamicContext(configuration, parameterObject);
    rootSqlNode.apply(context);
    SqlSourceBuilder sqlSourceParser = new SqlSourceBuilder(configuration);
    Class<?> parameterType = parameterObject == null ? Object.class : parameterObject.getClass();
    SqlSource sqlSource = sqlSourceParser.parse(context.getSql(), parameterType, context.getBindings());
    BoundSql boundSql = sqlSource.getBoundSql(parameterObject);
    for (Map.Entry<String, Object> entry : context.getBindings().entrySet()) {
        boundSql.setAdditionalParameter(entry.getKey(), entry.getValue());
    }
    return boundSql;
}
```

从开始到结束， Mybatis 都没有对填充的条数和参数的数量做限制，是MySQL 对语句的长度有限制，默认是 4M。

### ExecutorType.BATCH插入

Mybatis内置的ExecutorType有3种，`SIMPLE`、`REUSE`、`BATCH`; **默认的是simple**，该模式下它为每个语句的执行创建一个新的预处理语句，单条提交sql；而batch模式重复使用已经预处理的语句，并且批量执行所有更新语句，显然batch性能将更优；但batch模式也有自己的问题，比如在Insert操作时，在事务没有提交之前，是没有办法获取到自增的id，这在某型情形下是不符合业务要求的。

JDBC 在执行 SQL 语句时，会将 SQL 语句以及实参通过网络请求的方式发送到数据库，一次执行一条 SQL 语句，一方面会减小请求包的有效负载，另一个方面会增加耗费在网络通信上的时间。

通过批处理的方式，就可以在 JDBC 客户端缓存多条 SQL 语句，然后在 flush 或缓存满的时候，将多条 SQL 语句打包发送到数据库执行，这样就可以有效地降低上述两方面的损耗，从而提高系统性能。进行jdbc批处理时需在JDBC的url中加入`rewriteBatchedStatements=true`

:::danger 注意

每次向数据库发送的 SQL 语句的条数是有上限的，如果批量执行的时候超过这个上限值，数据库就会抛出异常，拒绝执行这一批 SQL 语句，所以我们需要控制批量发送 SQL 语句的条数和频率。

:::

使用Batch批量处理数据库，当需要向数据库发送一批SQL语句执行时，应避免向数据库一条条的发送执行，而应采用JDBC的批处理机制，以提升执行效率。

`ExecutorType.BATCH`原理：把SQL语句发个数据库，数据库预编译好，数据库等待需要运行的参数，接收到参数后一次运行，`ExecutorType.BATCH`只打印一次SQL语句，预编译一次sql，多次设置参数步骤。

```java
@Test
public void testInsert3() throws IOException {
	//读取MyBatis的核心配置文件
    InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
    //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
    SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
    //如果自动提交设置为true,将无法控制提交的条数，改为最后统一提交
    SqlSession sqlSession = build.openSession(ExecutorType.BATCH,false);
    //通过代理模式创建StudentMapper接口的代理实现类对象
    StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
    int BATCH = 1000;
    for (int i = 0; i < BATCH; i++) {
        Student student = new Student();
        student.setsName("stu"+i);
        student.setAge(i);
        student.setSex("男");
        mapper.insertOnBatch1(student);
        if (i != 0 && i % 100 == 0) {
            sqlSession.commit();
        }
    }
    sqlSession.commit();

    // 关闭SqlSession
    sqlSession.close();
}
```

执行测试代码，控制台输出：

> DEBUG ==> Preparing: insert into student values (null,?,?,?)
>
> DEBUG ==> Parameters: stu0(String), 0(Integer), 男(String)
>
> DEBUG ==> Parameters: stu1(String), 1(Integer), 男(String)
> ....

:::warning 说明

在commit后不需要调用`sqlSession.clearCache()`和`sqlSession.flushStatements();`，用以刷新缓存和提交到数据库，源码解析如下:

```java
public void commit(boolean required) throws SQLException {
    if (this.closed) {
        throw new ExecutorException("Cannot commit, transaction is already closed");
    } else {
        this.clearLocalCache();
        this.flushStatements();
        if (required) {
            this.transaction.commit();
        }

    }
}
 public void clearCache() {
    this.executor.clearLocalCache();
}
```

源码`commit()`方法已经调用了`clearLocalCache()`和`flushStatements()`，而`clearCache()`方法也是调用了`clearLocalCache()`，所以只需写`commit()`即可。

:::

## 模糊查询

当使用模糊查询时，由于`#{}`底层为占位符，获取参数值并且执行过程中用`?`代替`#{}` 不会解析成占位符，会被认为是字符串。

![image-20230202193346092](assets/202308281741126.png)

解决办法：

1. 使用`${}`解决问题(不推荐，会存在注入问题)：

   ```xml
   <select id="selectStuByLike" resultType="com.hjc.demo.pojo.Student">
   	select id,s_name,age,sex from student where s_name like '%${name}%';
   </select>
   ```

2. 通过concat解决问题：

   ```xml
   <select id="selectStuByLike" resultType="com.hjc.demo.pojo.Student">
   	select id,s_name,age,sex from student where s_name like concat('%',#{name},'%');
   </select>
   ```

3. 通过拼接方式解决问题：

   ```xml
   <select id="selectStuByLike" resultType="com.hjc.demo.pojo.Student">
   	select id,s_name,age,sex from student where s_name like "%"#{name}"%";
   </select>
   ```

## 批量删除

由于`#{}`本身解析之后就会带一个`'` `'`，导致结果出现问题，所以只能使用`${}`。

- mapper接口中定义一个`deleteMore()`方法：

  ```java [StudentMapper.java]
  /**
  * 批量删除
  * @param ids 需要删除的id
  * @return 删除的条数
  */
  int deleteMore(@Param("ids") String ids);
  ```

- mapper映射文件中增加删除语句：

  ```xml [StudentMapper.xml]
  <delete id="deleteMore">
  	delete from student where id in (${ids})
  </delete>
  ```

- 测试代码：

  ```java
  @Test
  public void testDeleteMore() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //执行批量删除
      int result = mapper.deleteMore("1,2,3");
      System.out.println("result = " + result);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: delete from student where id in (1,2,3)
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Updates: 3
  >
  > result = 3

## 动态设置表名

由于`#{}`本身解析之后就会带一个`'` `'`，导致结果出现问题，所以只能使用`${}`。

- mapper接口中定义一个`getAllStu()`方法：

  ```java [StudentMapper.java]
  /**
  * 动态设置表名，查询所有的用户信息
  * @param tableName 需要查询的表
  * @return 表中的所有数据
  */
  List<Student> getAllStu(@Param("tableName") String tableName);
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="getAllStu" resultType="com.hjc.demo.pojo.Student">
  	select * from ${tableName}
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testSelectByTable() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //查询指定表中的数据
      List<Student> students = mapper.getAllStu("student");
      students.forEach(System.out::println);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select \* from student
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Total: 3
  >
  > `Student{id=4, sName='小明', age=15, sex='男'}` > `Student{id=5, sName='小红', age=19, sex='女'}` > `Student{id=6, sName='小寸', age=25, sex='男'}`

## 获取自增的主键

- [主键（自动递增）回填](<BasicOperation.md#主键(自动递增)回填>)

## 各类查询功能

:::danger 注意

查询功能必须设置resultType(结果类型)或resultMap(结果映射)

:::

- 若查询出的数据只有一条：

  1. 可以通过实体类对象接收
  2. 可以通过list集合接收

- 若查询出的数据有多条：
  1. 可以通过list集合接收。一定不能通过实体类对象接收，此时会抛异常TooManyResultsException
  2. 可以通过map类型的list集合接收
  3. 可以在mapper接口的方法上添加[`@MapKey`注解](Annotation.md#@MapKey:设置当前map的键)，此时可以将每条数据转换的map集合作为值，以某个字段的值作为键，放在同一个map集合中

### 查询单个数据

#### 使用实体类

- mapper接口中定义一个`selectById()`方法：

  ```java [StudentMapper.java]
  /**
  * 根据id查询用户信息(查询出的数据只有一条)
  * @param id 根据id查询
  * @return 返回一个表中信息
  */
  Student selectById(@Param("id") Integer id);
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="selectById" resultType="com.hjc.demo.pojo.Student">
      select * from student where id = #{id}
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testOneQueryToBean() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //查询数据
      Student student = mapper.selectById(1);
      System.out.println("student = " + student);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select \* from student where id = ?
  >
  > DEBUG ==> Parameters: 1(Integer)
  >
  > DEBUG <== Total: 1
  >
  > `student = Student{id=1, sName='小明', age=15, sex='男'}`

#### 使用List集合

- mapper接口中定义一个`selectByIdToList()`方法：

  ```java [StudentMapper.java]
  /**
  * 根据id查询用户信息(查询出的数据只有一条，通过list接收)
  * @param id 根据id查询
  * @return 返回一个表中信息
  */
  List<Student> selectByIdToList(@Param("id") Integer id);
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="selectByIdToList" resultType="com.hjc.demo.pojo.Student">
      select * from student where id = #{id}
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testOneQueryToList() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //查询数据
      List<Student> students = mapper.selectByIdToList(1);
      students.forEach(System.out::println);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select \* from student where id = ?
  >
  > DEBUG ==> Parameters: 1(Integer)
  >
  > DEBUG <== Total: 1
  >
  > `Student{id=1, sName='小明', age=15, sex='男'}`

#### 使用Map集合

- mapper接口中定义一个`getStuByIdToMap()`方法：

  ```java [StudentMapper.java]
  /**
  * 根据id查询用户信息为一个map集合
  * @param id 需要查询数据的id
  * @return 所匹配的数据
  */
  @MapKey("id")
  Map<String,Object> getStuByIdToMap(@Param("id") Integer id);
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="getStuByIdToMap" resultType="java.util.Map">
          select * from student where id = #{id}
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testOneQueryToMap() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //查询数据
      Map<String, Object> map = mapper.getStuByIdToMap(1);
      System.out.println("map = " + map);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select \* from student where id = ?
  >
  > DEBUG ==> Parameters: 1(Integer)
  >
  > DEBUG <== Total: 1
  >
  > map = {1={sex=男, id=1, s_name=小明, age=15}}

#### 查询总记录数

查询总记录数：

```sql
 select count(*) from 表名
```

:::warning 说明

设置为count(1)、count(\*)、count(字段)都可以。

:::

从查询结果来说：count(1)、 count(\*)、 count(字段) 不一样的，count字段如果某一字段的值为null，这条记录是不会被放到总记录数中的。

COUNT(column_name) 函数返回指定列的值的数目(NULL 不计入)。

- mapper接口中定义一个`getCount()`方法：

  ```java [StudentMapper.java]
  /**
  * 查询总记录数
  * @return 总记录条数
  */
  Integer getCount();
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="getCount" resultType="java.lang.Integer">
          select count(*) from student
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testCount() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //查询总记录数
      Integer count = mapper.getCount();
      System.out.println("count = " + count);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select count(\*) from student
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Total: 1
  >
  > count = 3

### 查询多个数据

#### 使用List集合

- mapper接口中定义一个`selectAllToList()`方法：

  ```java [StudentMapper.java]
  /**
  * 通过list接收所有表中信息
  * @return 返回所有表中信息
  */
  List<Student> selectAllToList();
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="selectAllToList" resultType="com.hjc.demo.pojo.Student">
  	select * from student
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testAllQueryToList() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //查询数据
      List<Student> students = mapper.selectAllToList();
      students.forEach(System.out::println);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select \* from student
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Total: 3
  >
  > `Student{id=1, sName='小明', age=15, sex='男'}` > `Student{id=2, sName='小红', age=19, sex='女'}` > `Student{id=3, sName='小寸', age=25, sex='男'}`

#### 使用Map集合

- mapper接口中定义一个`getStuAllToMap()`方法：

  ```java [StudentMapper.java]
  /**
  * 查询用户信息为一个map集合
  * @return 所匹配的数据
  */
  @MapKey("id")
  Map<Integer,Object> getStuAllToMap();
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="getStuAllToMap" resultType="java.util.Map">
          select * from student
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testAllQueryToMap() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //查询数据
      Map<Integer, Object> map = mapper.getStuAllToMap();
      System.out.println("map = " + map);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select \* from student
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Total: 3
  >
  > map = {1={sex=男, id=1, s_name=小明, age=15}, 2={sex=女, id=2, s_name=小红, age=19}, 3={sex=男, id=3, s_name=小寸, age=25}}

#### 使用List+Map结合

- mapper接口中定义一个`getAllStuToMap()`方法：

  ```java [StudentMapper.java]
  /**
  * 将表中所有的数据以map的方式存入到list集合中
  * @return 返回以id为key 把转换成的map集合作为值
  */
  @MapKey("id")
  List<Map<String,Object>> getAllStuToMap();
  ```

- mapper映射文件中增加查询语句：

  ```xml [StudentMapper.xml]
  <select id="getAllStuToMap" resultType="java.util.Map">
  	select * from student
  </select>
  ```

- 测试代码：

  ```java
  @Test
  public void testAllQueryToListMap() throws IOException {
      //读取MyBatis的核心配置文件
      InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
      //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
      SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
      //SqlSession sqlSession = sqlSessionFactory.openSession();
      //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
      SqlSession sqlSession = build.openSession(true);
      //通过代理模式创建StudentMapper接口的代理实现类对象
      StudentMapper mapper = sqlSession.getMapper(StudentMapper.class);
      //查询数据
      List<Map<String, Object>> stu = mapper.getAllStuToMap();
      stu.forEach(System.out::println);

      // 关闭SqlSession
      sqlSession.close();
  }
  ```

- 执行测试代码，控制台输出：

  > DEBUG ==> Preparing: select \* from student
  >
  > DEBUG ==> Parameters:
  >
  > DEBUG <== Total: 3
  >
  > `{sex=男, id=1, s_name=小明, age=15}` > `{sex=女, id=2, s_name=小红, age=19}` > `{sex=男, id=3, s_name=小寸, age=25}`
