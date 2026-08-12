# SqlSession

SqlSession是Mybatis最重要的构建之一，可以简单的任务Mybatis一系列的配置目的是生成类似JDBC生成的Connection对象的SqlSession，这样才能和数据库开启“沟通的桥梁”，通过SqlSession可以实现增删改查（当然现在更加推荐是使用Mapper接口的形式），那么它是如何执行实现的呢？

因为Mybatis的插件会在SqlSession运行过程中“插入”运行，如果没有很好理解的话，Mybatis插件可能会覆盖相应的源码造成严重的问题。

## sqlsession原理

sqlSession提供select、insert、update、delete方法，在旧版本中使用sqlsession接口的这些方法，但是在新版本中Mybatis就会建议直接使用mapper接口的方法。

映射器其实就是一个动态代理对象，进入到MapperMethod的execute方法就能简单找打sqlsession的删除，更新、查询、选择方法，从底层实现来说：通过动态代理技术，让接口跑起来，之后采用命令模式，最后还是采用了sqlsession的接口方法（getMapper()方法等到Mapper）执行sql查询（也就是说Mapper接口方法的底层实现还是采用了Sqlsession的接口方法实现的）。

## selsession的四个重要对象

- Execute：调度执行StatementHandler、ParmmeterHandler、ResultHandler执行相应的SQL语句；

- StatementHandler：使用数据库中的Statement（PrepareStatement）执行操作，即底层是封装好的PrepareStatement；

- ParammeterHandler：处理SQL参数；

- ResultHandler：结果集ResultSet封装处理放回。

![image-20230131185358336](assets/202303011659535.png)

![image-20230131185427570](assets/202303011659549.png)

## selectOne

selectOne 方法表示使用查询并且只返回一个对象，必须指定查询条件。只能查询 0 或 1 条记录，大于 1 条记录则运行错误。

**语法格式**：（也有其它重载方法，根据需要选择）。

```java
sqlSession.selectOne(String arg0, Object arg1)
```

## selectList

selectList 方法表示使用查询并且返回一个列表。可以查询 0 或 N 条记录。常用格式如下。

```java
sqlSession.selectOne(String arg0)
```

也可指定参数：

```java
sqlSession.selectList(String arg0, Object arg1)
```

以上语法格式中，String 对象由一个命名空间加 SQL id 组合而成，它完全定位了一条 SQL，这样 MyBatis 就会找到对应的 SQL。Object 对象为需要传递的参数，也就是查询条件。

> selectOne 实现的 selectList 都可以实现，即 list 中只有一个对象。但 selectList 能实现的，selectOne 不一定能实现。

如果 MyBatis 中只有一个 id 为 getWbsite 的 SQL，那么也可以简写为：

```java
Website website = (Website )sqlSession.selectOne("getWbsite",1);
```
