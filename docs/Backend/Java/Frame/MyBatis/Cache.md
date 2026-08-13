# MyBatis 缓存

缓存可以将数据保存在内存中，是互联网系统常常用到的。目前流行的缓存服务器有 MongoDB、Redis、Ehcache 等。**缓存是在计算机内存上保存的数据，读取时无需再从磁盘读入**，因此具备快速读取和使用的特点。

MyBatis 包含一个非常强大的查询缓存特性，它可以非常方便地配置和定制。 MyBatis3 中的缓存实现的很多改进都已经实现了，使得它更加强大而且易于配置。

和大多数持久化框架一样，MyBatis 提供了一级缓存和二级缓存的支持。**默认情况下，MyBatis 只开启一级缓存，二级缓存需手动开启**。

:::warning 说明

对于 MyBatis 缓存仅作了解即可，因为面对一定规模的数据量，内置的 Cache 方式就派不上用场了，并且对查询结果集做缓存并不是 MyBatis 所擅长的，它专心做的应该是 SQL 映射。对于缓存，采用 OSCache、Memcached 等专门的缓存服务器来做更为合理。

:::

## 缓存机制介绍

![./images](assets/202303011624682.png)

## 缓存的基本原理

### Cache接口

`org.apache.ibatis.cache.Cache`接口：所有缓存都必须实现的顶级接口

![./images](assets/202303062111547.png)

**Cache接口中的方法**：

![./images](assets/202303062112621.png)

![](assets/202303011623148.png)

### 缓存的本质

根据Cache接口中方法的声明我们能够看到，缓存的本质是一个**Map**。

### PerpetualCache

![./images](assets/202303011623500.png)

`org.apache.ibatis.cache.impl.PerpetualCache`是Mybatis的默认缓存，也是Cache接口的默认实现。Mybatis一级缓存和自带的二级缓存都是通过PerpetualCache来操作缓存数据的。同样是PerpetualCache这个类，怎么能区分出来两种不同级别的缓存呢？

其实很简单，调用者不同。

- 一级缓存：由BaseExecutor调用PerpetualCache
- 二级缓存：由CachingExecutor调用PerpetualCache，而CachingExecutor可以看做是对BaseExecutor的装饰

### 一级缓存机制

![./images](assets/202303011623932.png)

`org.apache.ibatis.executor.BaseExecutor`类中的关键方法：

- `query()`方法：

  ```java
  public <E> List<E> query(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler, CacheKey key, BoundSql boundSql) throws SQLException {
      ErrorContext.instance().resource(ms.getResource()).activity("executing a query").object(ms.getId());
      if (closed) {
          throw new ExecutorException("Executor was closed.");
      }
      if (queryStack == 0 && ms.isFlushCacheRequired()) {
          clearLocalCache();
      }
      List<E> list;
      try {
          queryStack++;

          // 尝试从本地缓存中获取数据
          list = resultHandler == null ? (List<E>) localCache.getObject(key) : null;

          if (list != null) {
              handleLocallyCachedOutputParameters(ms, key, parameter, boundSql);
          } else {

              // 如果本地缓存中没有查询到数据，则查询数据库
              list = queryFromDatabase(ms, parameter, rowBounds, resultHandler, key, boundSql);
          }
      } finally {
          queryStack--;
      }
      if (queryStack == 0) {
          for (org.apache.ibatis.executor.BaseExecutor.DeferredLoad deferredLoad : deferredLoads) {
              deferredLoad.load();
          }
          // issue #601
          deferredLoads.clear();
          if (configuration.getLocalCacheScope() == LocalCacheScope.STATEMENT) {
              // issue #482
              clearLocalCache();
          }
      }
      return list;
  }
  ```

- `queryFromDatabase()`方法：

  ```java
  private <E> List<E> queryFromDatabase(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler, CacheKey key, BoundSql boundSql) throws SQLException {
      List<E> list;
      localCache.putObject(key, EXECUTION_PLACEHOLDER);
      try {

          // 从数据库中查询数据
          list = doQuery(ms, parameter, rowBounds, resultHandler, boundSql);
      } finally {
          localCache.removeObject(key);
      }

      // 将数据存入本地缓存
      localCache.putObject(key, list);
      if (ms.getStatementType() == StatementType.CALLABLE) {
          localOutputParameterCache.putObject(key, parameter);
      }
      return list;
  }
  ```

### 二级缓存机制

![./images](assets/202303011623486.png)

CachingExecutor类中的`query()`方法在不同情况下使用的具体缓存对象：

- **未开启二级缓存**：

  ![./images](data:image/png;base64,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)

- **使用自带二级缓存**：

  ![image-20230122181331195](assets/202303011624664.png)

- **使用EHCache**：

  ![image-20230122181401933](assets/202303011624229.png)

# 一级缓存和二级缓存

:::tip 提示

下列各项操作均使用[user表](Table/user.md)来操作。

:::

## 使用顺序

首先查询二级缓存，因为二级缓存中可能会有其他程序已经查出来的数据，可以拿来直接使用。如果二级缓存没有命中，再查询一级缓存。如果一级缓存也没有命中，则查询数据库。SqlSession关闭之前，一级缓存中的数据会写入二级缓存。

![./images](assets/202303011624017.png)

## 效用范围

- 一级缓存：SqlSession级别
- 二级缓存：SqlSessionFactory级别

![./images](assets/202303011623488.png)

它们之间范围的大小：

![./images](assets/202303011623291.png)

## 一级缓存

一级缓存是基于 PerpetualCache(MyBatis自带)的 HashMap 本地缓存，**作用范围为 session 域内**。当 session flush(刷新)或者 close(关闭)之后，该 session 中所有的 cache(缓存)就会被清空。

在参数和 SQL 完全一样的情况下，使用同一个 SqlSession 对象调用同一个 mapper 的方法，往往只执行一次 SQL。因为使用 SqlSession 第一次查询后，MyBatis 会将其放在缓存中，再次查询时，如果没有刷新，并且缓存没有超时的情况下，SqlSession 会取出当前缓存的数据，而不会再次发送 SQL 到数据库。

由于 **SqlSession 是相互隔离的**，所以如果你使用不同的 SqlSession 对象，即使调用相同的 Mapper、参数和方法，MyBatis 还是会再次发送 SQL 到数据库执行，返回结果。

**一级缓存失效的情况**：

- 不是同一个SqlSession
- 同一个SqlSession但是查询条件发生了变化
- 同一个SqlSession两次查询期间执行了任何一次增删改操作
- 同一个SqlSession两次查询期间手动清空了缓存
- 同一个SqlSession两次查询期间提交了事务

**例**：

在 WebsiteMapper 类中添加 selectWebsiteById 方法：

```java
User selectUserById(@Param("id") Integer id);
```

WebsiteMapper.xml 中添加相应的映射 SQL 语句：

```xml
<select id="selectUserById" resultType="com.hjc.demo.pojo.User">
    select * from user where  id = #{id}
</select>
```

测试代码：

```java
public class UserMapperTest {
    private static Logger logger = Logger.getLogger(UserMapperTest.class);

    @Test
    public void testFirstCache() throws IOException {
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

        mapper.selectUserById(1);
        logger.debug("使用同一个SqlSession");
        //在同一SqlSession下
        //若在执行两次查询的期间执行了任何一次增删改操作，则一级缓存失效
//        mapper.insertUser(new User(null,"1","2",2));
        //在执行两次查询的期间执行清空缓存，则一级缓存失效
//        sqlSession.clearCache();
        mapper.selectUserById(1);
        System.out.println("--------");

        //使用不同一个SqlSession
        logger.debug("使用不同一个SqlSession");
        SqlSession sqlSession2 = build.openSession(true);
        UserMapper mapper2 = sqlSession2.getMapper(UserMapper.class);
        mapper2.selectUserById(1);
    }
}
```

**运行结果**：

> DEBUG ==> Preparing: select \_ from website where id = ?
>
> DEBUG ==> Parameters: 1(Integer)
>
> DEBUG <== Total: 1
>
> DEBUG 使用同一个SqlSession
>
> DEBUG 使用不同一个SqlSession
>
> DEBUG ==> Preparing: select \_ from website where id = ?
>
> DEBUG ==> Parameters: 1(Integer)
>
> DEBUG <== Total: 1

从运行结果可以看出，第一个 SqlSession 实际只发生过一次查询，而第二次查询就从缓存中取出了，也就是 SqlSession 层面的一级缓存。为了克服这个问题，往往需要配置二级缓存，使得缓存在 SqlSessionFactory 层面上能够提供给各个 SqlSession 对象共享。

## 二级缓存

二级缓存与一级缓存其机制相同，默认也是采用 PerpetualCache，HashMap存储，不同在于其**存储作用域为 Mapper(Namespace)**，并且**可自定义存储源**，如 Ehcache。

二级缓存是全局缓存，作用域超出 session 范围之外，可以被所有 SqlSession 共享(SqlSessionFactory)。

**一级缓存缓存的是 SQL 语句，二级缓存缓存的是结果对象**。

**二级缓存开启的条件**：

- 在核心配置文件中，设置全局配置属性`cacheEnabled="true"`，默认为true，不需要设置。
- 在映射文件中设置标签`<cache />`。
- 二级缓存必须在SqlSession关闭或提交之后有效。
- 查询的数据所转换的实体类类型必须实现序列化的接口。

**二级缓存失效的情况**： 两次查询之间执行了任意的增删改，会使一级和二级缓存同时失效。

### 二级缓存的配置

1. **开启二级缓存功能**：默认不开启。

   :::danger 注意

   只有再次在 namescape 内(com.hjc.demo.mapper.WebsiteMapper)的查询才能共享这个缓存

   :::

   ```xml [WebsiteMapper.xml]
   <mapper namescape="com.hjc.demo.mapper.WebsiteMapper">
       <!-- cache配置 -->
       <cache eviction="FIFO" flushInterval="60000" size="512" readOnly="true" />
       ...
   </mapper>
   ```

   在 mapper 文件配置支持 cache 后，如果需要对个别查询进行调整，可以单独设置 cache，代码如下。

   ```xml
   <select id="getWebsiteList" resultType="net.biancheng.po.Website" usecache="true">    ...</select>
   ```

2. **让实体类支持序列化**：

   ```java
   public class Website implements Serializable {
       ...
   }
   ```

3. MyBatis 的全局缓存配置需要在 mybatis-config.xml 的 settings 元素中设置(默认为true，可忽略设置)：

   ```xml [mybatis-config.xml]
   <settings>
       <setting name="cacheEnabled" value="true" />
   </settings>
   ```

4. 测试代码：

   ```java
   @Test
   public void testTwoCache() throws IOException {
       InputStream is = Resources.getResourceAsStream("mybatis-config.xml");
       SqlSessionFactory build = new SqlSessionFactoryBuilder().build(is);
       SqlSession sqlSession1 = build.openSession(true);
       UserMapper mapper = sqlSession1.getMapper(UserMapper.class);
       mapper.selectUserById(1);
       //SqlSession关闭的时候，一级缓存中的内容会被存入二级缓存
       sqlSession1.close();

       logger.debug("在同一SqlSessionFactory下");
       //在同一SqlSessionFactory下
       SqlSession sqlSession2 = build.openSession(true);
       UserMapper mapper2 = sqlSession2.getMapper(UserMapper.class);
       mapper2.selectUserById(1);
       //SqlSession关闭的时候，一级缓存中的内容会被存入二级缓存
       sqlSession1.close();

       logger.debug("不在同一SqlSessionFactory下");
       //不在同一SqlSessionFactory下
       InputStream iss = Resources.getResourceAsStream("mybatis-config.xml");
       SqlSessionFactory build1 = new SqlSessionFactoryBuilder().build(iss);
       SqlSession sqlSession3 = build1.openSession(true);
       UserMapper mapper3 = sqlSession3.getMapper(UserMapper.class);
       mapper3.selectUserById(1);
       //SqlSession关闭的时候，一级缓存中的内容会被存入二级缓存
       sqlSession1.close();
   }
   ```

   **运行结果**：

   > DEBUG Cache Hit Ratio [com.hjc.demo.mapper.WebsiteMapper]: 0.0
   >
   > DEBUG ==> Preparing: select \_ from website where id = ?
   >
   > DEBUG ==> Parameters: 1(Integer)
   >
   > DEBUG <== Total: 1
   >
   > DEBUG 在同一SqlSessionFactory下
   >
   > DEBUG Cache Hit Ratio [com.hjc.demo.mapper.WebsiteMapper]: 0.5
   >
   > DEBUG 不在同一SqlSessionFactory下
   >
   > DEBUG Cache Hit Ratio [com.hjc.demo.mapper.WebsiteMapper]: 0.0
   >
   > DEBUG ==> Preparing: select \_ from website where id = ?
   >
   > DEBUG ==> Parameters: 1(Integer)
   >
   > DEBUG <== Total: 1

**cache属性说明**：

- eviction：代表的是**缓存回收策略**，目前 MyBatis 提供策略：
  - LRU：使用较少，移除最长时间不用的对象。
  - FIFO：先进先出，按对象进入缓存的顺序来移除它们。
  - SOFT：软引用，移除基于垃圾回收器状态和软引用规则的对象。
  - WEAK：弱引用，更积极地移除基于垃圾收集器状态和弱引用规则的对象。
- flushInterval：**刷新间隔时间**，单位为毫秒，这里配置的是 100 秒刷新，如果省略该配置，那么只有当 SQL 被执行的时候才会刷新缓存。
- size：**引用数目**，正整数，代表缓存最多可以存储多少个对象，不宜设置过大。设置过大会导致内存溢出。这里配置的是 1024 个对象。
- readOnly：**只读**，默认值为 false，意味着缓存数据只能读取而不能修改，这样设置的好处是可以快速读取缓存，缺点是没有办法修改缓存。

**缓存命中率**：

日志中打印的Cache Hit Ratio叫做缓存命中率

计算公式：**缓存命中率=命中缓存的次数/查询的总次数**

```text
Cache Hit Ratio [com.hjc.demo.mapper.CacheMapper]: 0.5
```

## 自定义缓存

除了使用 MyBatis 提供的默认缓存方式，你还可以通过实现你自己的缓存或其他第三方缓存方案创建适配器来完全覆盖缓存行为。

**使用一个自定义的缓存**：

```xml
<cache type="com.hjc.mybatis.cache.demo4.MyCustomCache" />
```

type 属性指定的类必须实现 `org.mybatis.cache.Cache` 接口。这个接口是 MyBatis 框架中很多复杂的接口之一。

**Cache 源码**：

```java [Cache.java]
package org.apache.ibatis.cache;

import java.util.concurrent.locks.ReadWriteLock;

public interface Cache {
    /** 获取缓存ID，如：com.hxstrive.mybatis.cache.demo4.UserMapper */
    String getId();
    /** 获取缓存大小 */
    int getSize();
    /** 将对象放入到缓存 */
    void putObject(Object key, Object value);
    /** 从缓存获取对象 */
    Object getObject(Object key);
    /** 从缓存移除一个对象 */
    Object removeObject(Object key);
    /** 清空缓存 */
    void clear();
    /** 获取一个读写锁对象 */
    ReadWriteLock getReadWriteLock();
}
```

如果要配置你自定义的缓存，可以通过 `<cache>` 标签的子标签 `<property>` 标签指定自定义缓存对象成员变量的值，相当于调用该变量的 setter 方法。比如：下面代码会在你的缓存实现中调用一个称为 "`setCacheFile(String file)`" 的方法，然后将指定的缓存文件位置放到 cacheFile 属性中。

```xml
<cache type="com.domain.something.MyCustomCache">
    <property name="cacheFile" value="D:\tmp\cache\data.tmp"/>
</cache>
```

当然，你可以使用所有 Java 简单类型作为 JavaBeans 的属性， MyBatis 会自动进行转换。

记得缓存配置和缓存实例是绑定在 SQL 映射文件的命名空间是很重要的。因此，所有在相同命名空间的语句（`<select>`、`<insert>`、`<update>` 和 `<delete>`）绑定的缓存是一样的。语句可以修改和缓存交互的方式，或在语句的基础上使用两种简单的属性（flushCache、useCache）来完全排除它们。 默认情况下，语句是这样配置的：

```xml
<!-- select 语句使用缓存 -->
<select ... flushCache="false" useCache="true" />
<insert ... flushCache="true" />
<update ... flushCache="true" />
<delete ... flushCache="true" />
```

如果你想改变默认的行为，只能设置 flushCache 和 useCache 属性。比如，在一些情况下你也许想排除从缓存中查询特定语句结果，或者你也许想要一个 `<select>` 语句来刷新缓存。相似地，你也许有一些 `<update>` 语句执行是不需要刷新缓存。

**例**：

MyBatis 配置文件 mybatis-cfg.xml：

```xml [mybatis-cfg.xml]
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <properties resource="database.properties"/>
    <settings>
        <!-- 全局映射器启用缓存 -->
        <setting name="cacheEnabled" value="true" />
    </settings>
    <environments default="MySqlDatabase" >
        <environment id="MySqlDatabase" >
            <transactionManager type="JDBC" />
            <dataSource type="POOLED">
                <property name="driver" value="${jdbc.driver}"/>
                <property name="url" value="${jdbc.url}"/>
                <property name="username" value="${jdbc.username}"/>
                <property name="password" value="${jdbc.password}"/>
            </dataSource>
        </environment>
    </environments>
    <mappers>
        <mapper resource="com/hjc/mybatis/cache/demo4/UserMapper.xml" />
    </mappers>
</configuration>
```

```java [UserBean.java]
package com.hjc.mybatis.cache.demo4;

import java.io.Serializable;

public class UserBean implements Serializable {
   private Integer userId;
   private String name;
   private String sex;
   private Integer age;
   // 忽略 getter 和 setter 方法
}
```

定义 Mapper 文件：

```java [UserMapper.java]
package com.hjc.mybatis.cache.demo4;

import org.apache.ibatis.annotations.Param;

public interface UserMapper {
   UserBean getUserById(@Param("userId") int userId);
}
```

```xml [UserMapper.xml]
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
   "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.hxstrive.mybatis.cache.demo4.UserMapper">
   <!-- 开启二级缓存，使用自定义缓存 -->
   <cache type="com.hjc.mybatis.cache.demo4.MyCustomCache">
      <property name="cacheFile" value="D:\tmp\cache\data.tmp" />
   </cache>

   <!-- 映射结果 -->
   <resultMap id="RESULT_MAP" type="com.hjc.mybatis.cache.demo4.UserBean">
      <id column="user_id" jdbcType="INTEGER" property="userId" />
      <result column="name" jdbcType="VARCHAR" property="name" />
      <result column="sex" jdbcType="VARCHAR" property="sex" />
      <result column="age" jdbcType="INTEGER" property="age" />
   </resultMap>

   <!-- 查询所有用户信息 -->
   <select id="getUserById" resultMap="RESULT_MAP" useCache="true">
      select `user_id`, `name`, `sex`, `age`
      from `user` where `user_id`=#{userId}
   </select>
</mapper>
```

**自定义缓存**：

```java
package com.hjc.mybatis.cache.demo4;

import com.alibaba.fastjson.JSONObject;
import org.apache.commons.io.FileUtils;
import org.apache.ibatis.cache.Cache;
import java.io.File;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * 自定义 Cache
 */
public class MyCustomCache implements Cache {
    // 缓存ID，如：com.hjc.mybatis.cache.demo4.UserMapper
    private String id;
    // 读写锁
    private ReadWriteLock readWriteLock = new ReentrantReadWriteLock();
    // 缓存对象Map
    private Map<Object,Object> cache = new ConcurrentHashMap<>();
    // 缓存磁盘文件
    private String cacheFile;

    /** 会被 <cache> 的 <property> 调用 */
    public void setCacheFile(String cacheFile) {
        this.cacheFile = cacheFile;
        System.out.println("setCacheFile() cacheFile=" + cacheFile);
        // 每次创建该对象时，从磁盘加载历史缓存
        try {
            String str = FileUtils.readFileToString(new File(cacheFile), "UTF-8");
            Map<Object,Object> tmpMap = JSONObject.parseObject(str, Map.class);
            for(Map.Entry<Object,Object> entry : tmpMap.entrySet()) {
                cache.put(entry.getKey(), entry.getValue());
            }
        } catch (Exception e) {
            System.err.println("加载缓存失败，" + e.getMessage());
            e.printStackTrace();
        }
    }

    public MyCustomCache(String id) {
        this.id = id;
        System.out.println("MyCustomCache id=" + id);
    }

    @Override
    public String getId() {
        System.out.println("getId()");
        return id;
    }

    @Override
    public int getSize() {
        System.out.println("getSize()");
        return cache.size();
    }

    @Override
    public void putObject(Object key, Object value) {
        System.out.println("putObject() key=" + key + ", value=" + value);
        cache.put(key, value);
        // 将数据写入磁盘
        try {
            String cacheStr = JSONObject.toJSONString(cache);
            FileUtils.write(new File(cacheFile), cacheStr, "UTF-8");
        } catch (Exception e) {
            System.err.println("缓存持久化失败，" + e.getMessage());
            e.printStackTrace();
        }
    }

    @Override
    public Object getObject(Object key) {
        System.out.println("getObject() key=" + key);
        return cache.get(key);
    }

    @Override
    public Object removeObject(Object key) {
        Object value = cache.get(key);
        if(null == value) {
            return null;
        } else {
            cache.remove(key);
            return value;
        }
    }

    @Override
    public void clear() {
        cache.clear();
    }

    @Override
    public ReadWriteLock getReadWriteLock() {
        return readWriteLock;
    }
}
```

**客户端代码**：

```java
package com.hjc.mybatis.cache.demo4;

import org.apache.ibatis.io.Resources;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.session.SqlSessionFactoryBuilder;
import java.io.InputStream;

public class CacheDemo {
   public static void main(String[] args) throws Exception {
      String cfgName = "com/hjc/mybatis/cache/demo4/mybatis-cfg.xml";
      InputStream input = Resources.getResourceAsStream(cfgName);
      SqlSessionFactoryBuilder factoryBuilder = new SqlSessionFactoryBuilder();
      SqlSessionFactory sqlFactory = factoryBuilder.build(input);
      getUserById(sqlFactory, 1);
      getUserById(sqlFactory, 2);
      getUserById(sqlFactory, 3);
      getUserById(sqlFactory, 3);
      getUserById(sqlFactory, 2);
      getUserById(sqlFactory, 1);
   }

   private static void getUserById(SqlSessionFactory sqlFactory, int userId) {
      System.out.println("查询用户信息：");
      SqlSession sqlSession = sqlFactory.openSession();
      UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
      UserBean userBean = userMapper.getUserById(userId);
      System.out.println(userBean + " -- " + userBean.getName());
      sqlSession.close();
   }

}
```

## 整合EHCache

### EHCache简介

官网地址：https://www.ehcache.org/

![./images](assets/202303011623056.png)

> Ehcache is an open source, standards-based cache that boosts performance, offloads your database, and simplifies scalability. **It's the most widely-used Java-based cache because it's robust, proven, full-featured, and integrates with other popular libraries and frameworks**. Ehcache scales from in-process caching, all the way to mixed in-process/out-of-process deployments with terabyte-sized caches.

### 整合操作

#### Mybatis环境

在Mybatis环境下整合EHCache，**前提**当然是要先准备好**Mybatis的环境**。

#### 添加依赖

```xml [pom.xml]
<!-- Mybatis EHCache整合包 -->
<dependency>
    <groupId>org.mybatis.caches</groupId>
    <artifactId>mybatis-ehcache</artifactId>
    <version>1.2.1</version>
</dependency>
<!-- slf4j日志门面的一个具体实现 -->
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.2.3</version>
</dependency>
```

**依赖传递情况**：

![./images](data:image/png;base64,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)

**各主要jar包作用**：

| jar包名称       | 作用                            |
| --------------- | ------------------------------- |
| mybatis-ehcache | Mybatis和EHCache的整合包        |
| ehcache         | EHCache核心包                   |
| slf4j-api       | SLF4J日志门面包                 |
| logback-classic | 支持SLF4J门面接口的一个具体实现 |

#### 整合EHCache

1. 创建EHCache配置文件

   ![./images](data:image/png;base64,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)

   ```xml [ehcache.xml]
   <?xml version="1.0" encoding="utf-8" ?>
   <ehcache xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="../config/ehcache.xsd">
       <!-- 磁盘保存路径 -->
       <diskStore path="D:\hjc\ehcache"/>

       <defaultCache
               maxElementsInMemory="1000"
               maxElementsOnDisk="10000000"
               eternal="false"
               overflowToDisk="true"
               timeToIdleSeconds="120"
               timeToLiveSeconds="120"
               diskExpiryThreadIntervalSeconds="120"
               memoryStoreEvictionPolicy="LRU">
       </defaultCache>
   </ehcache>
   ```

2. 添加指定缓存管理器的具体类型：

   ```xml [UserMapper.xml]
   <cache type="org.mybatis.caches.ehcache.EhcacheCache"/>
   ```

3. 加入logback日志：存在SLF4J时，作为简易日志的log4j将失效，此时我们需要借助SLF4J的具体实现logback来打印日志。

   ```xml [logbock.xml]
   <?xml version="1.0" encoding="UTF-8"?>
   <configuration debug="true">
   	<!-- 指定日志输出的位置 -->
   	<appender name="STDOUT"
   		class="ch.qos.logback.core.ConsoleAppender">
   		<encoder>
   			<!-- 日志输出的格式 -->
   			<!-- 按照顺序分别是：时间、日志级别、线程名称、打印日志的类、日志主体内容、换行 -->
   			<pattern>[%d{HH:mm:ss.SSS}] [%-5level] [%thread] [%logger] [%msg]%n</pattern>
   		</encoder>
   	</appender>

   	<!-- 设置全局日志级别。日志级别按顺序分别是：DEBUG、INFO、WARN、ERROR -->
   	<!-- 指定任何一个日志级别都只打印当前级别和后面级别的日志。 -->
   	<root level="DEBUG">
   		<!-- 指定打印日志的appender，这里通过“STDOUT”引用了前面配置的appender -->
   		<appender-ref ref="STDOUT" />
   	</root>

   	<!-- 根据特殊需求指定局部日志级别 -->
   	<logger name="com.hjc.demo.mapper" level="DEBUG"/>

   </configuration>
   ```

4. junit测试：

   正常按照[二级缓存](#二级缓存)的方式测试即可。因为整合EHCache后，其实就是使用EHCache代替了Mybatis自带的二级缓存。

### EHCache配置文件说明

当借助`CacheManager.add("缓存名称")`创建Cache时，EhCache便会采用`<defalutCache/>`指定的的管理策略。

**defaultCache标签各属性说明**：

![图片2](assets/202303011623422.png)
