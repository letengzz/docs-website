# MyBatis-Flex

MyBatis-Flex 是一个优雅的 MyBatis 增强框架，它非常轻量、同时拥有极高的性能与灵活性。可以轻松的使用 Mybaits-Flex 链接任何数据库，其内置的 QueryWrapper^亮点 帮助我们极大的减少了 SQL 编写的工作的同时，减少出错的可能性。

总而言之，MyBatis-Flex 能够极大地提高开发效率和开发体验，可以有更多的时间专注于自己的事情。

- Gitee地址：https://gitee.com/mybatis-flex/mybatis-flex
- GitHub地址：https://github.com/mybatis-flex/mybatis-flex
- 操作文档：https://mybatis-flex.com/zh/intro/support-database.html

**特征**：

- **轻量**：除了 MyBatis，没有任何第三方依赖轻依赖、没有任何拦截器，其原理是通过 SqlProvider 的方式实现的轻实现。同时，在执行的过程中，没有任何的 Sql 解析（Parse）轻运行。这带来了几个好处：1、极高的性能；2、极易对代码进行跟踪和调试；3、把控性更高。
- **灵活**：支持 Entity 的增删改查、以及分页查询的同时，MyBatis-Flex 提供了 Db + Row^灵活 工具，可以无需实体类对数据库进行增删改查以及分页查询。与此同时，MyBatis-Flex 内置的 QueryWrapper^灵活 可以轻易的帮助我们实现 多表查询、链接查询、子查询 等等常见的 SQL 场景。
- **强大**：支持任意关系型数据库，还可以通过方言持续扩展，同时支持 多（复合）主键、逻辑删除、乐观锁配置、数据脱敏、数据审计、 数据填充 等等功能。

## Maven 依赖

Spring Boot 场景：

```xml [pom.xml]
<dependency>
    <groupId>com.mybatis-flex</groupId>
    <artifactId>mybatis-flex-spring-boot-starter</artifactId>
    <version>1.5.3</version>
</dependency>

<dependency>
    <groupId>com.mybatis-flex</groupId>
    <artifactId>mybatis-flex-processor</artifactId>
    <version>1.5.3</version>
    <scope>provided</scope>
</dependency>
```

## 同类框架功能对比

MyBatis-Flex 主要是和 MyBatis-Plus 与 Fluent-MyBatis 对比，

- MyBatis-Plus：老牌的 MyBatis 增强框架，开源于 2016 年。
- Fluent-MyBatis：阿里云开发的 MyBatis 增强框架（来自于阿里云·云效产品团队）

## 测试列表(List)数据查询

要求返回的数据为 10 条数据。

MyBatis-Flex 的代码如下：

```java
QueryWrapper queryWrapper = new QueryWrapper();
queryWrapper.where(FLEX_ACCOUNT.ID.ge(100).or(FLEX_ACCOUNT.USER_NAME
.eq("admin" + ThreadLocalRandom.current().nextInt(10000))))
.limit(10);
mapper.selectListByQuery(queryWrapper);
```

MyBatis-Plus 的代码如下：

```java
QueryWrapper queryWrapper = new QueryWrapper();
queryWrapper.ge("id", 100);
queryWrapper.or();
queryWrapper.eq("user_name", "admin" + ThreadLocalRandom.current().nextInt(10000));
queryWrapper.last("limit 10");
mapper.selectList(queryWrapper);
```

10 轮的测试结果：

```sh
---------------
>>>>>>>testFlexSelectTop10:90
>>>>>>>testPlusSelectTop10WithLambda:743
>>>>>>>testPlusSelectTop10:678
---------------
>>>>>>>testFlexSelectTop10:85
>>>>>>>testPlusSelectTop10WithLambda:692
>>>>>>>testPlusSelectTop10:684
---------------
>>>>>>>testFlexSelectTop10:84
>>>>>>>testPlusSelectTop10WithLambda:692
>>>>>>>testPlusSelectTop10:670
---------------
>>>>>>>testFlexSelectTop10:85
>>>>>>>testPlusSelectTop10WithLambda:737
>>>>>>>testPlusSelectTop10:667
---------------
>>>>>>>testFlexSelectTop10:85
>>>>>>>testPlusSelectTop10WithLambda:691
>>>>>>>testPlusSelectTop10:684
---------------
>>>>>>>testFlexSelectTop10:97
>>>>>>>testPlusSelectTop10WithLambda:760
>>>>>>>testPlusSelectTop10:666
---------------
>>>>>>>testFlexSelectTop10:80
>>>>>>>testPlusSelectTop10WithLambda:673
>>>>>>>testPlusSelectTop10:637
---------------
>>>>>>>testFlexSelectTop10:81
>>>>>>>testPlusSelectTop10WithLambda:653
>>>>>>>testPlusSelectTop10:639
---------------
>>>>>>>testFlexSelectTop10:82
>>>>>>>testPlusSelectTop10WithLambda:659
>>>>>>>testPlusSelectTop10:636
---------------
>>>>>>>testFlexSelectTop10:81
>>>>>>>testPlusSelectTop10WithLambda:654
>>>>>>>testPlusSelectTop10:656
```

**测试结论**：

MyBatis-Flex 的查询 10 条数据的速度，大概是 MyBatis-Plus 的 5~10 倍左右。

## 支持的数据库类型

MyBatis-Flex 支持的数据库类型，现在市面上的数据库几乎全部支持，我们还可以通过自定义方言的方式，持续添加更多的数据库支持。

## 数据库方言

在某些场景下，比如用户要实现自己的 SQL 生成逻辑时，我们可以通过实现自己的方言达到这个目的，实现方言分为两个步骤：

1、编写自己的方言类，实现 IDialect 接口

2、通过 DialectFactory.registerDialect() 方法注册自己的方言
