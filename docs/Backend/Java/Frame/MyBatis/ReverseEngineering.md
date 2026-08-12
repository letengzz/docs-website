# MyBatis 逆向工程

Mybatis 提供了一个逆向工程工具，该工具可以**根据数据表自动生成针对单表的 po 类、mapper 映射文件和 mapper 接口**。大大缩减了开发时间，可以让开发人员将更多的精力放在繁杂的业务逻辑上。

之所以强调单表两个字，是因为 MyBatis 逆向工程生成的 Mapper 中的操作都是针对单表的。在大型项目中，很少有复杂的多表关联查询，所以该工具作用还是很大的。

- [MyBatis逆向工程使用手册](http://mybatis.org/generator/index.html)

## 相关概念

- **正向工程**：先创建Java实体类，由框架负责根据实体类生成数据库表。Hibernate是支持正向工程的。
- **逆向工程**：先创建数据库表，由框架负责根据数据库表，反向生成Java实体类、Mapper接口、Mapper映射文件。

**基本原理**：

![image-20230206093533532](assets/202303011331434.png)

## 操作步骤(例)

:::tip 提示

下列各项操作均使用[user表](Table/user.md)来操作(不做相关MyBatis操作)。

:::

### 1. 下载jar包/配置POM

- 通过[jar包下载](https://github.com/mybatis/generator/releases) (不推荐)

- 通过构建Maven项目添加相关依赖：

  ```xml [pom.xml]
    <!-- 依赖信息 -->
    <dependencies>
  	<!-- junit测试 -->
      <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.13.2</version>
        <scope>test</scope>
      </dependency>

      <!-- Mybatis核心 -->
      <dependency>
        <groupId>org.mybatis</groupId>
        <artifactId>mybatis</artifactId>
        <version>3.5.11</version>
      </dependency>

      <!-- 数据库连接池 -->
      <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>druid</artifactId>
        <version>1.2.15</version>
      </dependency>

      <!-- MySQL驱动 -->
      <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>8.0.31</version>
      </dependency>
      <!-- 逆向工程插件-->
      <dependency>
        <groupId>org.mybatis.generator</groupId>
        <artifactId>mybatis-generator-core</artifactId>
        <version>1.4.1</version>
       </dependency>
    </dependencies>

    <!-- 控制Maven在构建过程中相关配置 -->
    <build>
      <!-- 构建过程中用到的插件 -->
      <plugins>
        <!-- 具体插件，逆向工程的操作是以构建过程中插件形式出现的 -->
        <plugin>
          <groupId>org.mybatis.generator</groupId>
          <artifactId>mybatis-generator-maven-plugin</artifactId>
          <version>1.4.1</version>
          <!-- 插件的依赖 -->
          <dependencies>
            <!-- 逆向工程的核心依赖 -->
            <dependency>
              <groupId>org.mybatis.generator</groupId>
              <artifactId>mybatis-generator-core</artifactId>
              <version>1.4.1</version>
            </dependency>
            <!-- 数据库连接池 -->
            <dependency>
              <groupId>com.alibaba</groupId>
              <artifactId>druid</artifactId>
              <version>1.2.15</version>
            </dependency>
            <!-- MySQL驱动 -->
            <dependency>
              <groupId>mysql</groupId>
              <artifactId>mysql-connector-java</artifactId>
              <version>8.0.31</version>
            </dependency>
            <!-- log4j日志 -->
  		  <dependency>
              <groupId>log4j</groupId>
              <artifactId>log4j</artifactId>
        		<version>1.2.17</version>
            </dependency>
          </dependencies>
        </plugin>
      </plugins>
    </build>
  ```

### 2. 创建数据表

- 参考[user表](Table/user.md)

### 3. 创建项目

创建普通项目时，导入所需jar包，并将Mybatis 全局核心配置文件、日志文件、数据库配置文件引入。新建资源文件夹 config，在 config 文件夹下创建 generatorConfig.xml 文件，用于配置及指定数据库及表等。

创建Maven项目时，导入依赖，并将Mybatis 全局核心配置文件、日志文件、数据库配置文件引入。在resource下创建 generatorConfig.xml 文件，用于配置及指定数据库及表等。

:::danger 注意

generatorConfig.xml不能随意起名。

:::

```xml [generatorConfig.xml]
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE generatorConfiguration PUBLIC "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"
        "http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd">

<generatorConfiguration>
    <!--
        targetRuntime: 执行生成的逆向工程的版本
            MyBatis3Simple: 生成基本的CRUD
            MyBatis3: 生成带条件的CRUD
     -->
    <context id="DB2Tables" targetRuntime="MyBatis3">
        <!-- 生成的Java文件的编码 -->
        <property name="javaFileEncoding" value="UTF-8" />
        <!-- 格式化java代码 -->
        <property name="javaFormatter" value="org.mybatis.generator.api.dom.DefaultJavaFormatter" />
        <!-- 防止生成重复代码 -->
        <plugin type="org.mybatis.generator.plugins.UnmergeableXmlMappersPlugin"/>
        <!-- JavaBean 实现 序列化 接口 -->
        <plugin type="org.mybatis.generator.plugins.SerializablePlugin" />
        <!--  pojo中生成toString -->
        <plugin type="org.mybatis.generator.plugins.ToStringPlugin" />
        <!-- 开启支持内存分页   可生成 支持内存分布的方法及参数 -->
        <!--<plugin type="org.mybatis.generator.plugins.RowBoundsPlugin" /> -->
        <!-- generate entity时，生成hashcode和equals方法 -->
        <!--<plugin type="org.mybatis.generator.plugins.EqualsHashCodePlugin" /> -->
        <!-- 此处是将Example改名为Criteria 当然 想改成什么都行~    -->
        <!--<plugin type="org.mybatis.generator.plugins.RenameExampleClassPlugin">
        <property name="searchString" value="Example$" />
        &lt;!&ndash;替换后&ndash;&gt;
        <property name="replaceString" value="Criteria" />
        <property name="replaceString" value="Query" />
        </plugin>-->
        <!-- 是否去除自动生成的注释 true：是 ： false:否 -->
        <commentGenerator>
            <!-- 是否去除生成日期-->
            <property name="suppressDate" value="true"/>
            <!-- 是否去除自动生成的注释 -->
            <property name="suppressAllComments" value="true" />
        </commentGenerator>
        <!-- Mysql数据库连接的信息：驱动类、连接地址、用户名、密码 -->
        <jdbcConnection driverClass="com.mysql.cj.jdbc.Driver"
                        connectionURL="jdbc:mysql://localhost:3306/mybatis-example"
                        userId="root"
                        password="123123" >
            <!-- 修复逆向生成实体类字段不全的问题-->
            <property name="nullCatalogMeansCurrent" value="true"/>
        </jdbcConnection>


        <!-- 默认为false，把JDBC DECIMAL 和NUMERIC类型解析为Integer，为true时 把JDBC DECIMAL 和NUMERIC类型解析为java.math.BigDecimal -->
        <javaTypeResolver>
            <property name="forceBigDecimals" value="false" />
        </javaTypeResolver>

        <!-- javaBean的生成策略-->
        <javaModelGenerator
                targetPackage="com.hjc.demo.pojo" targetProject=".\src\main\java">
            <!-- 从数据库返回的值被清理前后的空格(去掉字符串的空格) -->
            <property name="trimStrings" value="true" />
            <!-- 是否开启子包，即targetPackage.schemaName.tableName -->
            <property name="enableSubPackages" value="false" />
            <!-- 是否对model添加 构造函数 -->
            <property name="constructorBased" value="true"/>
            <!-- 是否对类CHAR类型的列的数据进行trim操作 -->
            <property name="trimStrings" value="true"/>
            <!-- 建立的Model对象是否 不可改变  即生成的Model对象不会有 setter方法，只有构造方法 -->
            <property name="immutable" value="false"/>
        </javaModelGenerator>

        <!-- SQL映射文件的生成策略 -->
        <sqlMapGenerator targetPackage="com.hjc.demo.mapper"
                         targetProject=".\src\main\resources">
            <!-- 是否开启子包 -->
            <property name="enableSubPackages" value="true" />
        </sqlMapGenerator>

        <!-- Mapper接口的生成策略 -->
        <!--ANNOTATEDMAPPER: 生成java类文件,基于注解的Mapper接口，不会有对应的XML映射文件
            MIXEDMAPPER:XML和注解的混合形式
            XMLMAPPER:所有的方法都在XML中，接口调用依赖XML文件 -->
        <javaClientGenerator type="XMLMAPPER"
                             targetPackage="com.hjc.demo.mapper" targetProject=".\src\main\java">
            <!-- 是否开启子包 -->
            <property name="enableSubPackages" value="true" />
        </javaClientGenerator>

        <!-- 逆向分析的表 -->
        <!-- tableName设置为*号，可以对应所有表，此时不写domainObjectName -->
        <!-- domainObjectName属性指定生成出来的实体类的类名 -->
        <!-- 添加enableSelectByExample可去除按条件删除，增删改同理-->
        <table tableName="user" domainObjectName="User" enableSelectByExample="true"/>
    </context>

</generatorConfiguration>
```

普通项目需要创建 GeneratorSqlmap 类执行生成代码：

```java
package com.hjc.demo;
import java.io.File;
import java.util.*;
import org.mybatis.generator.api.MyBatisGenerator;
import org.mybatis.generator.config.Configuration;
import org.mybatis.generator.config.xml.ConfigurationParser;
import org.mybatis.generator.internal.DefaultShellCallback;
public class GeneratorSqlmap {
    public void generator() throws Exception {
        List<String> warnings = new ArrayList<String>();
        boolean overwrite = true;
        // 指定配置文件
        File configFile = new File("./config/generatorConfig.xml");
        ConfigurationParser cp = new ConfigurationParser(warnings);
        Configuration config = cp.parseConfiguration(configFile);
        DefaultShellCallback callback = new DefaultShellCallback(overwrite);
        MyBatisGenerator myBatisGenerator = new MyBatisGenerator(config, callback, warnings);
        myBatisGenerator.generate(null);
    }
    // 执行main方法以生成代码
    public static void main(String[] args) {
        try {
            GeneratorSqlmap generatorSqlmap = new GeneratorSqlmap();
            generatorSqlmap.generator();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

使用Maven创建的项目，只需将插件双击运行即可构建项目。

![1](assets/202303011331426.gif)

### 4. 测试代码

#### 测试MyBatis3Simple

当执行生成的逆向工程的版本是MyBatis3Simple:时，生成基本的CRUD。

**生成的mapper接口中，包含**：

![image-20230206105840419](assets/202303011331233.png)

```java
@Test
public void testMyBatis3Simple() throws IOException {
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

    //添加功能
    int result = mapper.insert(new User(null, "李白", "123456", 19));
    System.out.println("result = " + result);

    //根据主键删除
    mapper.deleteByPrimaryKey(2);

    //查询所有
    List<User> users = mapper.selectAll();
    users.forEach(System.out::println);

    //根据主键查询
    User user = mapper.selectByPrimaryKey(1);
    System.out.println("user = " + user);

    //根据主键更改
    int result2 = mapper.updateByPrimaryKey(new User(1, "李白", "123456", 19));
    System.out.println("result2 = " + result2);

    sqlSession.close();
}
```

#### 测试MyBatis3

执行生成的逆向工程的版本是MyBatis3时，生成带条件的CRUD。

**生成的mapper接口中，包含**：

![image-20230206105144591](assets/202303011331082.png)

在 pojo 包中，有一个名字为 XxxExample 的类，里面定义了一系列方法用来做条件，比如：排序、去重、大于、小于、等于、模糊查询、数据在某某之间等等。

类中包含以下 3 个成员变量：

```java
protected String orderByClause;
protected boolean distinct;
protected List<Criteria> oredCriteria;
```

:::warning 说明

- distinct 字段用于指定 DISTINCT 查询。
- orderByClause 字段用于指定 ORDER BY 条件，这个条件没有构造方法，直接通过传递字符串值指定。
- oredCriteria 字段用于自定义查询条件。

:::

在TEmpExample类中定义了一个内部类GeneratedCriteria，这个内部类就定义了一系列条件的方法，这些条件最后都会拼接在SQL中(使用QBC查询)，但是我们一般不用它，都用它的子类Criteria来进行操作，Criteria继承了内部类GeneratedCriteria。

**拓展**：QBC(`Query By Criteria`)查询最大的特点就是将SQL语句中的WHERE子句进行了组件化的封装，让我们可以通过调用Criteria对象的方法自由的拼装查询条件。

![202301211516207](assets/202303011331141.png)

```java
@Test
public void testMyBatis3() throws IOException {
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

    // 1.创建EmployeeExample对象
    UserExample example = new UserExample();

    // 2.通过example对象创建Criteria对象
    UserExample.Criteria criteria01 = example.createCriteria();
    UserExample.Criteria criteria02 = example.or();

    // 3.在Criteria对象中封装查询条件
    criteria01
              .andAgeBetween(15,99)
              .andUsernameLike("%李%")
              .andPasswordEqualTo("123456");
    criteria02
              .andAgeBetween(0,20)
              .andUsernameLike("%刘%")
              .andPasswordEqualTo("123123");


    // 4.基于Criteria对象进行查询
    List<User> tempList = mapper.selectByExample(example);

    for (User user : tempList) {
        System.out.println("user = " + user);
    }

    sqlSession.close();

    // 最终SQL的效果：
    // WHERE ( age between ? and ? and username like ? and password = ? ) or( age between ? and ? and username like ? and password = ? )

    User user = new User(null,"李白",null,10);
    //添加:属性是null 执行直接赋值为null
    int insert = mapper.insert(user);
    System.out.println("insert = " + insert);
    //添加:不会将null赋值添加到字段的 只会将不为空赋值
    int selective = mapper.insertSelective(user);
    System.out.println("selective = " + selective);

    //根据主键删除
    int deleteByPrimaryKey = mapper.deleteByPrimaryKey(5);
    System.out.println("deleteByPrimaryKey = " + deleteByPrimaryKey);
    //根据条件删除:年龄等于十岁的或id大于30的
    //两个sql语句通过or来连接
    UserExample userExample = new UserExample();
    userExample.createCriteria().andAgeEqualTo(10);
    userExample.or().andIdGreaterThan(30);
    mapper.deleteByExample(userExample);


    User user1 = new User(2,"嬴政",null,null);
    //根据主键更改:属性是null 执行直接赋值为null
    mapper.updateByPrimaryKey(user1);
    //根据主键更改:不会将null赋值添加到字段的 只会将不为空赋值
    mapper.updateByPrimaryKeySelective(user1);

    User user2 = new User(1,"冯巩",null,null);
    UserExample userExample1 = new UserExample();
    userExample1.createCriteria().andPasswordIsNotNull().andIdIn(Arrays.asList(21,22,23));

    //根据条件更改:属性是null 执行直接赋值为null
    mapper.updateByExample(user2,userExample1);

    //根据条件更改:不会将null赋值添加到字段的 只会将不为空赋值
    mapper.updateByExampleSelective(user2,userExample1);

    //根据主键查询
    User eig1 = mapper.selectByPrimaryKey(1);
    System.out.println("eig1 = " + eig1);

    //根据条件查询
    UserExample userExample2 = new UserExample();
    userExample2.createCriteria().andIdLessThan(50);
    List<User> users = mapper.selectByExample(userExample2);
    users.forEach(System.out::println);

    //根据条件查询总数:名字带有李且年龄是0-60的总人数
    UserExample userExample3 = new UserExample();
    userExample3.createCriteria().andUsernameLike("%李%").andAgeBetween(0,60);
    int result = (int) mapper.countByExample(userExample3);
    System.out.println("result = " + result);

    sqlSession.close();
}
```
