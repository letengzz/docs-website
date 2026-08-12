# MyBatis 核心配置和映射器

## 核心配置

MyBatis 的 XML 核心配置文件主要用于配置连接数据库的环境以及MyBatis的全局配置信息。

:::danger 注意

核心配置文件中的标签**必须按照固定的顺序**： ①properties、②settings、③typeAliases、④typeHandlers、⑤objectFactory、⑥objectWrapperFactory、⑦reflectorFactory、⑧plugins、⑨environments、⑩databaseIdProvider、⑪mappers

:::

**核心配置文件结构**：

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
"http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration><!-- 配置 -->
    <properties /><!-- 属性 -->
    <settings /><!-- 设置 -->
    <typeAliases /><!-- 类型命名 -->
    <typeHandlers /><!-- 类型处理器 -->
    <objectFactory /><!-- 对象工厂 -->
    <objectWrapperFactory /><!-- 对象加工工厂 -->
    <reflectorFactory /><!-- 缓存 Reflector -->
    <plugins /><!-- 插件 -->
    <environments><!-- 配置环境 -->
        <environment><!-- 环境变量 -->
            <transactionManager /><!-- 事务管理器 -->
            <dataSource /><!-- 数据源 -->
        </environment>
    </environments>
    <databaseIdProvider /><!-- 数据库厂商标识 -->
    <mappers /><!-- 映射器 -->
</configuration>
```

### configuration标签

configuration标签是 MyBatis 配置文件的根元素。配置各类信息需放入在configuration标签中。

#### 配置properties标签

MyBatis 配置中，properties 标签用来引入一个属性文件或者定义多个属性，然后在配置文件中使用 `${}` 方式进行引用。

**properties 标签 DTD 定义**：

```
<!ELEMENT properties (property*)>
<!ATTLIST properties
resource CDATA #IMPLIED
url CDATA #IMPLIED
>
```

properties 拥有两个**属性**：

- resource：从本地文件系统载入属性文件：`resource="database.properties"`，将从项目 classpath 路径下面加载 database.properties 属性文件。

- url：可以从互联网加载属性文件：

  `url="http://www.baidu.com/data/database.properties"` 将从网络位置下载属性文件。

properties 标签是外部化的，可替代的属性，这些属性也可以配置在典型的 Java 属性配置文件中，或者通过 properties 元素的子元素来传递。

```xml
<properties resource="org/mybatis/example/config.properties">
    <property name="username" value="root"/>
    <property name="password" value="123456"/>
</properties>
```

属性就可以在整个配置文件中使用，使用可替换的属性来实现动态配置(通过`${}` 方式进行引用)：

```xml
<properties resource="jdbc.properties" />
<dataSource type="POOLED">
    <property name="driver" value="${jdbc.driver}"/>
    <property name="url" value="${jdbc.url}"/>
    <property name="username" value="${jdbc.username}"/>
    <property name="password" value="${jdbc.password}"/>
</dataSource>
```

属性也可以被传递到 `SqlSessionBuilder.build()` 方法中：

```java
SqlSessionFactory factory = sqlSessionFactoryBuilder.build(reader, props);
//SqlSessionFactory factory = sqlSessionFactoryBuilder.build(reader, environment, props);
```

MyBatis 属性按照顺序加载：

- 在 properties 元素体内指定的属性首先被读取。
- 从类路径下资源或 properties 元素的 url 属性中加载的属性第二被读取，它会覆盖已经存在的完全一样的属性。
- 作为方法参数传递的属性最后被读取，它也会覆盖任一已经存在的完全一样的属性，这些属性可能是从 properties 元素体内和资源/url 属性中加载的。

因此，**最高优先级的属性是那些作为方法参数的，然后是资源/url 属性，最后是 properties 元素中指定的属性。**

##### property

properties的子标签。用来定义单个属性。

**property 标签 DTD 定义**：

```
<!ELEMENT property EMPTY>
<!ATTLIST property
name CDATA #REQUIRED
value CDATA #REQUIRED
>
```

property 拥有两个**属性**：

- name：属性名
- value：属性值

#### 配置settings标签

settings标签用于配置 MyBatis 的运行时行为，能深刻的影响 MyBatis 的底层运行，一般不需要大量配置，大部分情况下使用其默认值即可。

**settings 标签 DTD 定义**：

```
<!ELEMENT settings (setting+)>
```

::: danger 注意

settings至少需要一个以上的 setting标签

:::

##### setting

setting 标签用来设置一个 key-value，其中内容为空，只有两个属性：

- name：指定设置项的名称。
- value：指定设置项的值。

**设置的信息**：

![图片2](assets/202303011009954.png)

**例**：

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <!-- 配置MyBatis在运行时的行为方式。如：启用缓存等 -->
    <settings>
        <!-- 配置使全局的映射器启用或禁用缓存，true-启用；false-禁用；默认：true -->
        <setting name="cacheEnabled" value="true" />
        <!-- 全局启用或禁用延迟加载。当禁用时,所有关联对象都会即时加载。（true|false） 默认：true -->
        <setting name="lazyLoadingEnabled" value="true" />
        <!-- 当启用时,有延迟加载属性的对象在被调用时将会完全加载任意属性。否则,每种属性将会按需要加载。（true|false） 默认：true -->
        <setting name="aggressiveLazyLoading" value="true"/>
        <!-- 允许或不允许多种结果集从一个单独 的语句中返回(需要适合的驱动)（true|false）默认：true -->
        <setting name="multipleResultSetsEnabled" value="true"/>
        <!-- 使用列标签代替列名。不同的驱动在这方面表现不同。 参考驱动文档或充分测试两种方法来决定所使用的驱动。true|false 默认：true -->
        <setting name="useColumnLabel" value="true"/>
        <!-- 允许 JDBC支持生成的键。 需要适合的驱动。 如果设置为true则这个设置强制 生成的键被使用
            ,-尽管一些驱动拒绝兼容但仍然有效(比如Derby)true|false 默认：False -->
        <setting name="useGeneratedKeys" value="false" />
        <!-- 指定 MyBatis如何自动映射列到字段/属性。PARTIAL只NONE,PARTIAL,FULL会自动映射简单
            ,没有嵌套的结果。FULL会自动映射任意复杂的结果(嵌套的或其他情况)。默认：PARTIAL -->
        <setting name="autoMappingBehavior" value="PARTIAL"/>
        <!-- 配置默认的执行器。SIMPLE执行器没有什么特别之处。REUSE执行器重用预处理语句。
            BATCH执行器重用语句和批量更新。默认：SIMPLE -->
        <setting name="defaultExecutorType" value="SIMPLE"/>
        <!-- 设置超时时间, 它决定驱动等待一个数据库响应的时间。
            Any positive integer Not Set (null) -->
        <setting name="defaultStatementTimeout" value="1000"/>
        <!-- 允许在嵌套语句上使用RowBounds。true|false 默认：False -->
        <setting name="safeRowBoundsEnabled" value="false"/>
        <!-- 启用可以自动从数据库中根据列名生成驼峰式的变量名。
            -如：A_COLUMN -> aColumn。true|false 默认：False -->
        <setting name="mapUnderscoreToCamelCase" value="false"/>
        <!-- MyBatis使用本地缓存以防止循环引用和加快重复嵌套查询。
            -默认（SESSION）在会话中执行的所有查询缓存。SESSION|STATEMENT -->
        <setting name="localCacheScope" value="SESSION"/>
        <!-- 设置mapUnderscoreToCamelCase为true,可以实现将数据表中的下划线映射成驼峰来为实体类赋值 -->
        <setting name="mapUnderscoreToCamelCase" value="true"/>
    </settings>
    <!-- 忽略其他配置 -->
</configuration>
```

#### 配置typeAliases标签

该标签用来设置指定类的别名，可以简化在 Mapper 中使用类的全限定名。

关系映射需要指定了 JavaBean 完全限定名，每次都要完整的输入。因此就出现了 typeAliases 标签，该标签用来将给定的实体定义别名，如：将 com.hjc.demo.User 别名定义为定义为 User。那么映射时就可以使用别名了。

```xml
<!-- 映射结果 -->
<resultMap id="RESULT_MAP" type="User">
	<id column="id" jdbcType="INTEGER" property="id" />
    <result column="username" jdbcType="VARCHAR" property="username" />
    <result column="sex" jdbcType="VARCHAR" property="sex" />
    <result column="age" jdbcType="INTEGER" property="age" />
</resultMap>
```

**typeAliases标签 DTD 定义**：

```
<!ELEMENT typeAliases (typeAlias*,package*)>
```

**typeAliases> 标签允许有一个或多个 typeAlias 或 package 标签**。

::: danger 注意

- 设置的别名不区分大小写。
- 类型别名是为 Java 类型命名一个短的名字。它只和 XML 配置有关，只用来减少类完全限定名的多余部分。

:::

##### typeAlias

typeAlias 标签用来为一个 JavaBean 指定别名，type 属性指定 JavaBean 类型，alias 属性指定别名名称。

::: danger 注意

如果不设置alias 将拥有默认的别名，别名就是类名且不区分大小写，所以alias是可写可不写的。

:::

```xml
<typeAliases>
    <typeAlias alias="User" type="com.hjc.demo.pojo.User" />
</typeAliases>
```

##### package

使用 package 标签可以将指定一个包名称，然后 MyBatis 自动将该包下面的所有 JavaBean 进行别名声明，其中别名为类名。

```xml
<typeAliases>
	<package name="com.hjc.demo.pojo" />
</typeAliases>
```

#### 配置typeHandlers标签

typeHandlers标签用来定义类型处理器。无论是 MyBatis 在预处理语句中设置一个参数，还是从结果集中取出一个值时，类型处理器被用来将获取的值以合适的方式转换成 Java 类型。

::: danger 注意

使用这样的类型处理器将会覆盖已经存在的处理 Java 的 String 类型属性和 VARCHAR 参数及结果的类型处理器。要注意 MyBatis 不会审视数据库元信息来决定使用哪种类型，所以你必须在参数和结果映射中指定那是 VARCHAR 类型的字段，来绑定到正确的类型处理器上。这是因为 MyBatis 直到语句被执行都不知道数据类型的这个现实导致的。

:::

**默认的类型处理器**：

![图片4](assets/202303011010106.png)

可以重写类型处理器或创建你自己的类型处理器来处理不支持的或非标准的类型。要这样做的话，简单实现 TypeHandler 接口(org.mybatis.type)，然后映射新的类型处理器类到 Java 类型，还有可选的一个 JDBC 类型。

**例**：

```java [ExampleTypeHandler.java]
public class ExampleTypeHandler implements TypeHandler {

    public void setParameter(PreparedStatement ps, int i, Object parameter,JdbcType jdbcType) throws SQLException {
        ps.setString(i, (String) parameter);
    }

    public Object getResult(ResultSet rs, String columnName) throws SQLException {
        return rs.getString(columnName);
    }

    public Object getResult(CallableStatement cs, int columnIndex) throws SQLException {
        return cs.getString(columnIndex);
    }
}
```

```xml [MapperConfig.xml]
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <properties resource="database.properties"/>

    <!-- 定义自己的类型处理器 -->
    <typeHandlers>
        <typeHandler javaType="String" jdbcType="VARCHAR" handler="org.mybatis.example.ExampleTypeHandler"/>
    </typeHandlers>

    <!-- 忽略其他配置 -->
</configuration>
```

#### 配置objectFactory标签

objectFactory标签用来指定对象工厂。

MyBatis 每次创建结果对象新的实例时，它使用一个 ObjectFactory 实例来完成。如果存在构造参数映射：

```xml
<resultMap id="RESULT_MAP" type="com.hjc.demo.pojo.User">
    <constructor>
        <idArg column="id" javaType="int" />
        <arg column="username" javaType="String" />
    </constructor>
</resultMap>
```

MyBatis 默认的 ObjectFactory 对象，将不使用默认构造方法，而是使用带有参数（int、String类型）的构造方法去创建对象。

如果你想重写默认的 ObjectFactory，你可以创建你自己的 ObjectFactory（继承 DefaultObjectFactory 类）：

```java
public class MyObjectFactory extends DefaultObjectFactory {

    /** 处理默认构造方法 */
    public Object create(Class type) {
        return super.create(type);
    }

    /** 处理带参数构造方法 */
    public Object create(Class type,List<Class> constructorArgTypes, List<Object> constructorArgs) {
        return super.create(type, constructorArgTypes, constructorArgs);
    }

    /**
     * 在初始化你的 ObjectFactory 实例后，<objectFactory> 标签中定义的属性会被传递给 setProperties 方法
     * 该方法可以被用来配置 ObjectFactory 对象
     */
    public void setProperties(Properties properties) {
        super.setProperties(properties);
    }

}
```

然后在 mybatis-config.xml 文件中配置自定义对象工厂：

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <properties resource="database.properties"/>

    <!-- 定义自己的对象工厂 -->
    <objectFactory type="com.hjc.demo.factory.MyObjectFactory ">
        <property name="someProperty" value="100"/>
    </objectFactory>

    <!-- 忽略其他配置 -->
</configuration>
```

#### 配置plugins标签

plugins标签用来我们自定义的插件。

**plugins标签 DTD 定义**：

```
<!ELEMENT plugins (plugin+)>
<!ELEMENT plugin (property*)>
<!ATTLIST plugin
interceptor CDATA #REQUIRED
>
```

一个 plugins 标签内部至少拥有一个 plugin 标签，且 plugin 标签中允许使用多个 property 定义属性。

MyBatis 中允许你在某一点拦截已映射语句执行的调用（称为“拦截器”）。默认情况下，MyBatis 允许使用插件来拦截以下方法调用：

- **Executor** (update, query, flushStatements, commit, rollback, getTransaction, close, isClosed)
- **ParameterHandler** (getParameterObject, setParameters)
- **ResultSetHandler** (handleResultSets, handleOutputParameters)
- **StatementHandler** (prepare, parameterize, batch, update, query)

**使用 plugins 标签配置自定义插件/拦截器**：

**例**：

使用 property定义了一个 someProperty 属性值，可以在拦截器内部的 `setProperties()` 方法中获取到。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <properties resource="database.properties"/>

    <!-- 定义自定义插件和拦截器 -->
    <plugins>
        <plugin interceptor="com.hjc.demo.interceptor.MyInterceptor">
            <property name="someProperty" value="100"/>
        </plugin>
    </plugins>

    <!-- 忽略其他配置 -->
</configuration>
```

#### 配置environments标签

environments标签用于配置多种环境，用于支持不同的数据库，例如：同时支持 Oracle 和 MySQL 数据库。也有可能是为了分别定义开发环境、测试环境和生产环境。

::: danger 注意

可以配置多种环境(environment)，但是每个 SqlSessionFactory 实例只能选择一个环境。所以，如果你想连接两个数据库，你需要创建两个 SqlSessionFactory 实例，每个数据库对应一个数据库。如果你有三个数据库，你就需要创建三个 SqlSessionFactory 实例，以此类推。

:::

- **每个数据库对应一个 SqlSessionFactory**

为了明确创建哪种环境的 SqlSessionFactory，你可以将环境（environment）作为可选的参数传递给 SqlSessionFactoryBuilder。

SqlSessionFactoryBuilder 的 `build()` 方法可接受环境配置的两个方法签名：

```java
// 接受环境
SqlSessionFactory factory = sqlSessionFactoryBuilder.build(reader, environment);
// 接受环境和属性
SqlSessionFactory factory = sqlSessionFactoryBuilder.build(reader, environment, properties);
```

如果环境被忽略，那么默认环境将会被加载：

```java
SqlSessionFactory factory = sqlSessionFactoryBuilder.build(reader);
SqlSessionFactory factory = sqlSessionFactoryBuilder.build(reader, properties);
```

**environments 标签 DTD 定义**：

```
<!ELEMENT environments (environment+)>
<!ATTLIST environments
default CDATA #REQUIRED
>

<!ELEMENT environment (transactionManager,dataSource)>
<!ATTLIST environment
id CDATA #REQUIRED
>
```

上面的 DTD 定义中，允许 environments 标签下面添加一到多个 environment，而每一个 environment 表示一个环境，并且可以通过 default 属性定义默认的环境。其中：

- transactionManager：用来定义事务管理器
- dataSource：用来定义数据源

**例**：同时配置两个环境（开发环境-development，正式环境-prod），且将开发环境设置为默认环境。配置如下：

```xml
<?xml version="1.0" encoding="UTF-8" ?>
        <!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
                "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <properties resource="database.properties"/>
    <environments default="development">
        <!-- 测试环境 -->
        <environment id="development">
            <!-- 事务管理器配置 -->
            <transactionManager type="JDBC">
                <property name="..." value="..."/>
            </transactionManager>
            <!-- 数据源配置 -->
            <dataSource type="POOLED">
                <property name="driver" value="${driver}"/>
                <property name="url" value="${url}"/>
                <property name="username" value="${username}"/>
                <property name="password" value="${password}"/>
            </dataSource>
        </environment>
        <!-- 正式环境 -->
        <environment id="prod">
            <!-- 事务管理器配置 -->
            <transactionManager type="JDBC">
                <property name="..." value="..."/>
            </transactionManager>
            <!-- 数据源配置 -->
            <dataSource type="POOLED">
                <property name="driver" value="${driver}"/>
                <property name="url" value="${url}"/>
                <property name="username" value="${username}"/>
                <property name="password" value="${password}"/>
            </dataSource>
        </environment>
    </environments>

    <mappers>
        <mapper resource="com/hjc/demo/mapper/UserMapper.xml" />
    </mappers>
</configuration>
```

上面配置的关键点：

- 使用 environments 标签的 default 属性指定默认的环境 ID，比如：指定默认为环境为开发环境，`default="development"`
- 每个 environment 标签通过 ID 属性定义环境唯一 ID，如：`id="development"`
- 事务管理器的配置，如：`type="JDBC"`
- 数据源的配置，如：`type="POOLED"`

默认的环境和环境 ID 是自我解释的。你可以使用你喜欢的名称来命名，只要确定默认的要匹配其中之一。

##### environment

定义一个环境

**transactionManager**

定义一个事务管理器

在 MyBatis 中有两种事务管理器类型，也就是 `type="[JDBC|MANAGED]"`，两种事务管理器都不需要任何属性：

- **JDBC**：这个配置直接简单使用了 JDBC 的提交和回滚设置。它依赖于从数据源得到的连接来管理事务范围。

  JDBC 类型对应 JdbcTransactionFactory、JdbcTransaction。

- **MANAGED**：这个配置几乎没做什么。它从来不提交或回滚一个连接。而它会让容器来管理事务的整个生命周期（比如 Spring 或 JEE 应用服务器的上下文）。默认情况下它会关闭连接。然而一些容器并不希望这样，因此如果你需要从连接中停止它，将 closeConnection 属性设置为 false。

  MANAGED 类型对应 ManagedTransactionFactory、ManagedTransaction。

```xml
<transactionManager type="MANAGED">
    <property name="closeConnection" value="false"/>
</transactionManager>
```

JdbcTransactionFactory、JdbcTransaction、ManagedTransactionFactory、ManagedTransaction分别实现了 TransactionFactory 和 Transaction 接口：

![img](assets/202303011010547.png)

![img](assets/202303011010265.png)

**自定义事务管理器**：

自定义事务管理器需要实现 TransactionFactory 和 Transaction 接口。

1. TransactionFactory 接口源码：该接口定义了三个方法，一个用来设置属性，另外两个用来创建事务对象。

   ```java
   public interface TransactionFactory {

     /**
      * Sets transaction factory custom properties.
      * @param props
      */
     void setProperties(Properties props);

     /**
      * Creates a {@link Transaction} out of an existing connection.
      * @param conn Existing database connection
      * @return Transaction
      * @since 3.1.0
      */
     Transaction newTransaction(Connection conn);

     /**
      * Creates a {@link Transaction} out of a datasource.
      * @param dataSource DataSource to take the connection from
      * @param level Desired isolation level
      * @param autoCommit Desired autocommit
      * @return Transaction
      * @since 3.1.0
      */
     Transaction newTransaction(DataSource dataSource, TransactionIsolationLevel level, boolean autoCommit);

   }
   ```

2. Transaction 接口源码：该接口定义了四个方法，分别用于获取数据库连接、提交事务、回滚事务、关闭数据库连接。

   ```java
   public interface Transaction {

     /**
      * Retrieve inner database connection
      * @return DataBase connection
      * @throws SQLException
      */
     Connection getConnection() throws SQLException;

     /**
      * Commit inner database connection.
      * @throws SQLException
      */
     void commit() throws SQLException;

     /**
      * Rollback inner database connection.
      * @throws SQLException
      */
     void rollback() throws SQLException;

     /**
      * Close inner database connection.
      * @throws SQLException
      */
     void close() throws SQLException;

   }
   ```

3. 实现了上面两个接口，需要在别名中进行声明：

   ```xml
   <typeAliases>
       <!-- 声明自定义的事务管理器 -->
       <typeAlias alias="my_transaction" type="com.hjc.mybatis.transaction.demo1.MyTransactionFactory" />
   </typeAliases>
   ```

4. 在 transactionManager 标签的 type 属性中指定定义事务管理器别名，如：my_transaction

   ```xml
   <transactionManager type="my_transaction" />
   ```

源码：

![img](assets/202303011011274.png)

进入 resolveClass 方法，该方法将调用 resolveAlias 方法去解析别名（这里别名为 my_transaction）：

![img](assets/202303011011299.png)

resolveAlias 方法中将从 TYPE_ALIASES Map中根据 key 获取别名对应的类全限定名称：

![img](assets/202303011011341.png)

**例**：

1. MyBatis 配置文件 mybatis-cfg.xml 内容：

   ```xml
   <?xml version="1.0" encoding="UTF-8" ?>
   <!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
     "http://mybatis.org/dtd/mybatis-3-config.dtd">
   <configuration>
       <properties resource="database.properties"/>
       <typeAliases>
           <!-- 声明自定义的事务管理器 -->
           <typeAlias alias="my_transaction" type="com.hjc.mybatis.transaction.demo1.MyTransactionFactory" />
       </typeAliases>
       <environments default="MySqlDatabase" >
           <environment id="MySqlDatabase" >
               <!-- 使用自定义事务管理器 -->
               <transactionManager type="my_transaction" />
               <dataSource type="POOLED">
                   <property name="driver" value="${jdbc.driver}"/>
                   <property name="url" value="${jdbc.url}"/>
                   <property name="username" value="${jdbc.username}"/>
                   <property name="password" value="${jdbc.password}"/>
               </dataSource>
           </environment>
       </environments>
       <mappers>
           <mapper resource="com/hjc/demo/mapper/UserMapper.xml" />
       </mappers>
   </configuration>
   ```

2. 自定义事务工厂类：

   ```java
   public class MyTransactionFactory implements TransactionFactory {
       private static final String NAME = MyTransactionFactory.class.getSimpleName();

       @Override
       public void setProperties(Properties props) {
           System.out.println(NAME + " setProperties()");
       }

       @Override
       public Transaction newTransaction(Connection conn) {
           System.out.println(NAME + " newTransaction()");
           return new MyTransaction(conn);
       }

       @Override
       public Transaction newTransaction(DataSource dataSource, TransactionIsolationLevel level, boolean autoCommit) {
           System.out.println(NAME + " newTransaction()");
           try {
               return new MyTransaction(dataSource.getConnection());
           } catch (SQLException e) {
               e.printStackTrace();
           }
           return null;
       }
   }
   ```

3. 自定义事务类：

   ```java
   public class MyTransaction implements Transaction {
       private static final String NAME = MyTransaction.class.getSimpleName();
       private Connection connection;

       public MyTransaction(Connection connection) {
           this.connection = connection;
       }

       @Override
       public Connection getConnection() throws SQLException {
           System.out.println(NAME + " getConnection()");
           return this.connection;
       }

       @Override
       public void commit() throws SQLException {
           System.out.println(NAME + " commit()");
           if(null != this.connection && !this.connection.getAutoCommit()) {
               this.connection.commit();
           }
       }

       @Override
       public void rollback() throws SQLException {
           System.out.println(NAME + " rollback()");
           if(null != this.connection && !this.connection.getAutoCommit()) {
               this.connection.rollback();
           }
       }

       @Override
       public void close() throws SQLException {
           System.out.println(NAME + " close()");
           if(null != this.connection) {
               this.connection.close();
           }
       }

   }
   ```

4. 定义 Mapper 接口和配置文件

   ```java [UserMapper.java]
   public interface UserMapper {
       /** 查询用户数 */
       int getUserCount();
   }
   ```

   ```xml [UserMapper.xml]
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
      "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
   <mapper namespace="com.hjc.mybatis.transaction.demo1.UserMapper">
       <!-- 查询用户数 -->
       <select id="getUserCount" resultType="integer">
           select count(*) from `user`
       </select>
   </mapper>
   ```

5. 客户端代码：

   ```java
   public class TransactionDemo {

       public static void main(String[] args) throws Exception {
           String cfgName = "com/hjc/mybatis/transaction/demo1/mybatis-cfg.xml";
           InputStream input = Resources.getResourceAsStream(cfgName);
           SqlSessionFactoryBuilder factoryBuilder = new SqlSessionFactoryBuilder();
           SqlSessionFactory sqlFactory = factoryBuilder.build(input);
           SqlSession sqlSession = sqlFactory.openSession(true);
           UserMapper userMapper = sqlSession.getMapper(UserMapper.class);

           int userCount = userMapper.getUserCount();
           System.out.println("用户总数=" + userCount);

           sqlSession.close();
       }

   }
   ```

运行客户端代码，输出结果：

> MyTransactionFactory setProperties()
> 2020-09-13 15:59:08,269 DEBUG [org.apache.ibatis.logging.LogFactory] - Logging initialized using 'class org.apache.ibatis.logging.slf4j.Slf4jImpl' adapter.
> 2020-09-13 15:59:08,316 DEBUG [org.apache.ibatis.datasource.pooled.PooledDataSource] - PooledDataSource forcefully closed/removed all connections.
> 2020-09-13 15:59:08,317 DEBUG [org.apache.ibatis.datasource.pooled.PooledDataSource] - PooledDataSource forcefully closed/removed all connections.
> 2020-09-13 15:59:08,317 DEBUG [org.apache.ibatis.datasource.pooled.PooledDataSource] - PooledDataSource forcefully closed/removed all connections.
> 2020-09-13 15:59:08,317 DEBUG [org.apache.ibatis.datasource.pooled.PooledDataSource] - PooledDataSource forcefully closed/removed all connections.
> MyTransactionFactory newTransaction()
> 2020-09-13 15:59:08,934 DEBUG [org.apache.ibatis.datasource.pooled.PooledDataSource] - Created connection 1555690610.
> MyTransaction getConnection()
> 2020-09-13 15:59:08,971 DEBUG [com.hxstrive.mybatis.transaction.demo1.UserMapper.getUserCount] - ooo Using Connection [com.mysql.jdbc.JDBC4Connection@5cb9f472]
> 2020-09-13 15:59:08,972 DEBUG [com.hxstrive.mybatis.transaction.demo1.UserMapper.getUserCount] - ==> Preparing: select count(\*) from `user`
> 2020-09-13 15:59:09,080 DEBUG [com.hxstrive.mybatis.transaction.demo1.UserMapper.getUserCount] - ==> Parameters:
> 2020-09-13 15:59:09,138 DEBUG [com.hxstrive.mybatis.transaction.demo1.UserMapper.getUserCount] - <== Total: 1
> 用户总数=3
> MyTransaction close()
> 2020-09-13 15:59:09,139 DEBUG [org.apache.ibatis.datasource.pooled.PooledDataSource] - Returned connection 1555690610 to pool.

**dataSource**

dataSource 标签使用基本的 JDBC 数据源接口来配置 JDBC 连接对象的资源。

::: danger 注意

配置数据源并不是必须的。为了方便使用延迟加载，数据源才是必须的。

:::

有三种内建的数据源类型(`type="UNPOOLED | POOLED | JNDI"`)：

- **UNPOOLED**：

  这个数据源的实现是每次被请求时简单打开和关闭连接。它有一点慢，这是对简单应用程序的一个很好的选择，因为它不需要及时的可用连接。不同的数据库对这个的表现也是不一样的，所以对某些数据库来说配置数据源并不重要，这个配置也是闲置的。

  UNPOOLED 类型的数据源仅仅用来配置以下 4 种属性：

  - **driver** – 这是 JDBC 驱动的 Java 类的完全限定名（如果你的驱动包含，它也不是数据源类）。
  - **url** – 这是数据库的 JDBC URL 地址。
  - **username** – 登录数据库的用户名。
  - **password** – 登录数据库的密码。
  - **defaultTransactionIsolationLevel** – 默认的连接事务隔离级别。

  作为可选项，你可以传递数据库驱动的属性。要这样做，属性的前缀是以"driver."开头的：

  - **driver.encoding=UTF8**

  这样就会传递以值 "UTF8" 来传递属性 "encoding"， 它是通过 `DriverManager.getConnection(url,driverProperties)` 方法传递给数据库驱动。

- **POOLED**：

  这是 JDBC 连接对象的数据源连接池的实现，用来避免创建新的连接实例时必要的初始连接和认证时间。这是一种当前 Web 应用程序用来快速响应请求很流行的方法。

  除了UNPOOLED的属性之外，还有很多属性可以用来配置 POOLED 数据源：

  - **poolMaximumActiveConnections** – 在任意时间存在的活动（也就是正在使用）连接的数量。默认值：10
  - **poolMaximumIdleConnections** – 任意时间存在的空闲连接数。
  - **poolMaximumCheckoutTime** – 在被强制返回之前，池中连接被检查的时间。默认值：20000 毫秒（也就是 20 秒）
  - **poolTimeToWait** – 这是给连接池一个打印日志状态机会的低层次设置，还有重新尝试获得连接，这些情况下往往需要很长时间（为了避免连接池没有配置时静默失败）。默认值：20000 毫秒（也就是 20 秒）
  - **poolPingQuery** – 发送到数据的侦测查询，用来验证连接是否正常工作，并且准备接受请求。默认是“NO PING QUERY SET”，这会引起许多数据库驱动连接由一个错误信息而导致失败。
  - **poolPingEnabled** – 这是开启或禁用侦测查询。如果开启，你必须用一个合法的SQL 语句（最好是很快速的）设置 poolPingQuery 属性。默认值：false。
  - **poolPingConnectionsNotUsedFor** – 这是用来配置 poolPingQuery 多次时间被用一次。这可以被设置匹配标准的数据库连接超时时间，来避免不必要的侦测。默认值：0（也就是所有连接每一时刻都被侦测-但仅仅当 poolPingEnabled 为 true 时适用）。

- **JNDI**：

  这个数据源的实现是为了使用如 Spring 或应用服务器这类的容器，容器可以集中或在外部配置数据源，然后放置一个 JNDI 上下文的引用。这个数据源配置只需要两个属性：

  - **initial_context** – 这 个 属 性 用 来 从 初 始 上 下 文 中 寻 找 环 境 （ 也 就 是initialContext.lookup（initial——context））。这是个可选属性，如果被忽略，那么 data_source 属性将会直接以 initialContext 为背景再次寻找。
  - **data_source** – 这是引用数据源实例位置的上下文的路径。它会以由 initial_context 查询返回的环境为背景来查找，如果 initial_context 没有返回结果时，直接以初始上下文为环境来查找。和其他数据源配置相似，它也可以通过名为“env.”的前缀直接向初始上下文发送属性。比如：
  - **env.encoding=UTF8**

  在初始化之后，这就会以值“UTF8”向初始上下文的构造方法传递名为“encoding”的属性。

#### 配置mappers标签

定义多个 Mapper 映射。

##### mapper标签

mapper标签配置一个具体的Mapper映射文件。

MyBatis 支持将 SQL 映射语句写入到 XML 文件(称为 Mapper 文件)或者通过注解直接指定。

```java
@Select("SELECT book_id, book_name, price, content FROM book")
@Results({
   @Result(id=true, column="book_id", property="bookId"),
   @Result(column="book_name", property="bookName"),
   @Result(column="price", property="price"),
   @Result(column="content", property="content")
})
List<BookBean> getBookList();
```

如果我们使用 XML 文件映射 SQL 语句，首先需要告诉 MyBatis 到哪里去找到这些语句。Java 在这方面没有提供一个很好的方法，所以最佳的方式是告诉 MyBatis 到哪里去找映射文件。你可以使用相对于类路径的资源引用，或者字符表示，或 url 引用的完全限定名(包括 file:///URLs)：

1. 使用 classpath 下的相对资源：

   ```xml
   <mappers>
       <mapper resource="org/mybatis/builder/AuthorMapper.xml"/>
       <mapper resource="org/mybatis/builder/BlogMapper.xml"/>
       <mapper resource="org/mybatis/builder/PostMapper.xml"/>
   </mappers>
   ```

2. 使用 url 完全限定名路径：

   ```xml
   <mappers>
       <mapper url="file:///var/sqlmaps/AuthorMapper.xml"/>
       <mapper url="file:///var/sqlmaps/BlogMapper.xml"/>
       <mapper url="file:///var/sqlmaps/PostMapper.xml"/>
   </mappers>
   ```

当引入映射文件过多，不推荐使用上述方案，可以使用package以包为单位引入映射文件。

**要求**：mapper接口所在的包要和映射文件所在的包一致、mapper接口要和映射文件的名字一致。

::: danger 注意

配置文件中创建包使用/分割来创建包。

:::

```xml
<mappers>
	<package name="com.hjc.demo.mapper"/>
</mappers>
```

## 映射器

映射器是MyBatis中最为重要的文件，文件中包含一组 SQL 语句（例如查询、添加、删除、修改），这些语句称为**映射语句**或**映射 SQL 语句**。

**映射器由 Java 接口和 XML 文件(或注解)共同组成。**

**映射器作用**：

- 定义参数类型
- 配置缓存
- 提供 SQL 语句和动态 SQL
- 定义查询结果和 POJO 的映射关系

**映射器两种实现方式**：

- 通过 XML 文件方式实现，比如在 mybatis-config.xml 文件中描述的 XML 文件，用来生成 mapper。
- 通过注解的方式实现，使用 Configuration 对象注册 Mapper 接口。

::: danger 注意

如果 SQL 语句存在动态 SQL 或者比较复杂，使用注解写在 Java 文件里可读性差，且增加了维护的成本。所以一般建议使用 XML 文件配置的方式，避免重复编写 SQL 语句。

:::

### XML实现映射器

XML 定义映射器分为两个部分：mapper接口和XML映射文件。

**XML映射文件的主要元素**：

![图片1](assets/202303011016414.png)

关于 MyBatis 的 SQL 映射文件中的 mapper 元素的 namescape 属性要求：

- namescape 的命名必须跟某个 DAO 接口同名，同属于 DAO 层，因此代码结构上，映射文件与该接口应放置在同一 package 下（如 com.hjc.demo.mapper），并且习惯上是以 Mapper 结尾（如 UserMapper.java、UserMapper.xml）。
- 不同的 mapper 文件中子元素的 id 可以相同，MyBatis 通过 namescape 和子元素的 id 联合区分。接口中的方法与映射文件中的 SQL 语句 id 应一 一对应。

**例**：操作使用[user表](Table/user.md)来操作。

1. 定义接口：

   ```java [main:com.hjc.demo.mapper.UserMapper.java]
   /**
    * Mapper接口映射
    * @author hjc
    */
   public interface UserMapper {
       List<User> selectAll();
   }
   ```

2. 定义映射文件：

   ```xml [resources:com.hjc.demo.mapper.UserMapper.xml]
   <?xml version="1.0" encoding="UTF-8"?><!DOCTYPE mapperPUBLIC "-//mybatis.org//DTD Mapper 3.0//EN""http://mybatis.org/dtd/mybatis-3-mapper.dtd">
   <mapper namespace="com.hjc.demo.mapper.UserMapper">
       <!-- 查询所有用户信息 -->
       <select id="selectAll" resultType="com.hjc.demo.pojo.User">
           select * from user
       </select>
   </mapper>
   ```

   - namespace 用来定义命名空间，该命名空间和定义接口的全限定名一致。
   - select 元素表明这是一条查询语句，属性 id 用来标识这条 SQL。resultType 表示返回的是一个 User 类型的值。

3. 在 MyBatis 配置文件中添加(引入 XML 文件，MyBatis 会读取 UserMapper.xml 文件，生成映射器)：

   ```xml
   <!-- 引入映射文件 -->
   <mappers>
   	<!-- Mapper注册：指定Mybatis映射文件的具体位置 -->
       <!-- mapper标签：配置一个具体的Mapper映射文件 -->
       <!-- resource属性：指定Mapper映射文件的实际存储位置，这里需要使用一个以类路径根目录为基准的相对路径 -->
       <!--    对Maven工程的目录结构来说，resources目录下的内容会直接放入类路径，所以这里我们可以以resources目录为基准 -->

   <!--        <mapper resource="mappers/UserMapper.xml"/>-->

       <!-- 引入映射文件过多，不推荐使用上述方案 -->
       <!-- 以包为单位引入映射文件-->
       <!-- 要求：mapper接口所在的包要和映射文件所在的包一致、mapper接口要和映射文件的名字一致-->
       <!-- 配置文件中创建包使用/分割来创建包-->
       <package name="com.hjc.demo.mapper"/>
   </mappers>
   ```

4. 测试：

   ```java
   @Test
   public void testMybatis() throws IOException {
   	//读取MyBatis的核心配置文件
       InputStream is = Resources.getResourceAsStream("mybatis-config.xml");
   	//创建SqlSessionFactoryBuilder对象
       SqlSessionFactoryBuilder sqlSessionFactoryBuilder = new SqlSessionFactoryBuilder();

       //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
       SqlSessionFactory sqlSessionFactory = sqlSessionFactoryBuilder.build(is);

       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
       //SqlSession sqlSession = sqlSessionFactory.openSession();
       //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
       SqlSession sqlSession = sqlSessionFactory.openSession(true);

       //通过代理模式创建UserMapper接口的代理实现类对象
       UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
   	//执行查询操作：
   	List<User> allUser = userMapper.selectAll();
   	allUser.forEach(System.out::println);

       sqlSession.close();
   }
   ```

5. 运行结果：

   > DEBUG ==> Preparing: select \* from user;
   >
   > DEBUG ==> Parameters:
   >
   > DEBUG <== Total: 3
   >
   > `User{id=1, username='刘备', password='456123', age=23}` > `User{id=2, username='关羽', password='123456', age=20}` > `User{id=3, username='张飞', password='124356', age=19}`

### 注解实现映射器

使用注解的方式实现映射器，只需要在接口中使用 Java 注解，注入 SQL 即可：

```java
public interface UserMapper {
    @Select(value = "select * from user")
    public List<Website> selectAllWebsite();
}
```

使用了 [`@Select` 注解](Annotation.md#@Select:实现查询功能)，并且注入了和 XML 中相同的 select 语句。

- [SQL语句映射注解](Annotation.md#SQL 语句映射)

::: danger 注意

如果使用注解和 XML 文件两种方式同时定义，那么 XML 方式将覆盖掉注解方式。

:::

虽然这里注解的方式看起来比 XML 简单，但是现实中遇到的 SQL 会比该例子复杂得多。如果 SQL 语句中有多个表的关联、多个查询条件、级联、条件分支等，显然这条 SQL 就会复杂的多，所以并不建议使用这种方式：

```sql
select * from t_user u
left join t_user_role ur on u.id = ur.user_id
left join t_role r on ur.role_id = r.id
left join t_user_info ui on u.id = ui.user_id
left join t_female_health fh on u.id = fh.user_id
left join t_male_health mh on u.id = mh.user_id
where u.user_name like concat('%', ${userName},'%')
and r.role_name like concat('%', ${roleName},'%')
and u.sex = 1
and ui.head_image is not null;
```

如果把以上 SQL 放到 @Select 注解中，无疑会大大降低代码的可读性。如果同时还要考虑使用动态 SQL 或需要加入其他的逻辑，这样就使得这个注解更加复杂了，不利于日后的维护和修改。

此外，XML 可以相互引入，而注解是不可以的，所以在一些比较复杂的场景下，使用 XML 方式会更加灵活和方便。因此大部分的企业都以 XML 为主。当然在一些简单的表和应用中使用注解方式也会比较简单。

这个接口可以在 XML 中定义，将在 mybatis-config.xml 中配置 XML 的语句修改为以下语句即可：

```xml
<mapper resource="com/hjc/demo/mapper/UserMapper" />
```

也可以使用 configuration 对象注册这个接口：

```java
configuration.addMapper(UserMapper.class);
```

### 映射文件的命名规则

**映射文件的命名规则**：

- 表所对应的实体类的类名+Mapper.xml

  例如：表t_user，映射的实体类为User，所对应的映射文件为UserMapper.xml 因此一个映射文件对应一个实体类，对应一张表的操作

- MyBatis映射文件用于编写SQL，访问以及操作表中的数据 MyBatis映射文件存放的位置是src/main/resources/mappers目录下

- MyBatis中可以面向接口操作数据，要保证两个一致：

  - mapper接口的全类名和映射文件的命名空间(namespace)保持一致
  - mapper接口中方法的方法名和映射文件中编写SQL的标签的id属性保持一致
