# 关于user表相关操作

## 相关SQL操作

### 创建表

```sql
CREATE DATABASE IF NOT EXISTS `mybatis-example`;

USE `mybatis-example`;

CREATE TABLE `user`(
id INT AUTO_INCREMENT,
username VARCHAR(20),
password VARCHAR(20),
age INT,
PRIMARY KEY(id)
);
```

### 添加数据

```sql
insert into user(username,password,age) values ("刘备","456123",23);
insert into user(username,password,age) values ("关羽","123456",20);
insert into user(username,password,age) values ("张飞","124356",19);
insert into user(username,password,age) values ("司马光","494161",23);
insert into user(username,password,age) values ("李白","444444",28);
insert into user(username,password,age) values ("杜甫","124356",70);
```

## 相关MyBatis操作

:::danger 注意

个别操作可能不适合下列内容，仅作通用参考。

:::

### 整体结构

![image-20230131195712260](assets/202303011020660.png)

### 导入依赖

```xml
<!-- 打包方式为jar包-->
<packaging>jar</packaging>

<!--添加依赖-->
<dependencies>
	<!-- Mybatis核心 -->
    <dependency>
		<groupId>org.mybatis</groupId>
        <artifactId>mybatis</artifactId>
        <version>3.5.11</version>
    </dependency>

    <!-- Junit测试 -->
    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.13.2</version>
        <scope>test</scope>
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
```

### POJO类

```java
package com.hjc.demo.pojo;

/**
 * User实体类
 * @author hjc
 */
public class User {
    private Integer id;
    private String username;
    private String password;
    private Integer age;

    //构造方法

    public User() {
    }

    public User(Integer id, String username, String password, Integer age) {
        this.id = id;
        this.username = username;
        this.password = password;
        this.age = age;
    }

    //getter和setter方法

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", username='" + username + '\'' +
                ", password='" + password + '\'' +
                ", age=" + age +
                '}';
    }
}
```

### 全局核心配置文件

```xml [mybatis-config.xml]
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <!-- Mybatis核心配置文件种，标签是存在顺序问题的 -->
    <!-- properties>settings>typeAliases>typeHandlers>objectFactory>objectWrapperFactory>reflectorFactory>plugins>environments>databaseIdProvider>mappers -->

    <!-- 引入properties -->
    <properties resource="jdbc.properties"/>

    <!-- 设置类型别名 -->
    <typeAliases>
        <!-- 在mybatis范围都可以通过别名表示当前的类型，且不区分大小写-->
        <!--<typeAlias type="com.hjc.demo.pojo.User" alias="User"/>-->
        <!-- 如果不设置alias，将拥有默认的别名，别名就是类名且不区分大小写 -->
        <!--<typeAlias type="com.hjc.demo.pojo.User"/>-->
        <!-- 可以使用package包为单位来设置默认的别名-->
        <package name="com.hjc.demo.pojo"/>
    </typeAliases>

    <!-- environments表示配置Mybatis的开发环境，可以配置多个环境，在众多具体环境中，使用default属性指定实际运行时使用的环境。default属性的取值是environment标签的id属性的值。 -->
    <environments default="development">
        <!-- environment表示配置Mybatis的一个具体的环境 -->
        <environment id="development">

            <!-- Mybatis的内置的事务管理器 -->
            <transactionManager type="JDBC"/>

            <!-- 配置数据源 -->
            <dataSource type="POOLED">
                <!-- 建立数据库连接的具体信息 -->

                <!-- 设置连接数据库的驱动 -->
                <property name="driver" value="${jdbc.driver}"/>
                <!-- 设置谅解数据库的连接地址 -->
                <property name="url" value="${jdbc.url}"/>
                <!-- 设置连接数据库的用户名 -->
                <property name="username" value="${jdbc.username}"/>
                <!-- 设置连接数据库的密码 -->
                <property name="password" value="${jdbc.password}"/>
            </dataSource>
        </environment>
        <environment id="test">
            <transactionManager type="JDBC"/>
            <dataSource type="POOLED">
                <property name="driver" value="com.mysql.jdbc.Driver"/>
                <property name="url" value="jdbc:mysql://localhost:3306/mybatis"/>
                <property name="username" value="root"/>
                <property name="password" value="123456"/>
            </dataSource>
        </environment>
    </environments>

    <!-- 引入映射文件 -->
    <mappers>
        <!-- Mapper注册：指定Mybatis映射文件的具体位置 -->
        <!-- mapper标签：配置一个具体的Mapper映射文件 -->
        <!-- resource属性：指定Mapper映射文件的实际存储位置，这里需要使用一个以类路径根目录为基准的相对路径 -->
        <!--    对Maven工程的目录结构来说，resources目录下的内容会直接放入类路径，所以这里我们可以以resources目录为基准 -->

        <!-- <mapper resource="mappers/UserMapper.xml"/>-->

        <!-- 引入映射文件过多，不推荐使用上述方案 -->
        <!-- 以包为单位引入映射文件-->
        <!-- 要求：mapper接口所在的包要和映射文件所在的包一致、mapper接口要和映射文件的名字一致-->
        <package name="com.hjc.demo.mapper"/>
    </mappers>
</configuration>
```

### mapper接口

```java [com.hjc.demo.mapper.UserMapper.java]
/**
 * mapper接口
 * @author hjc
 */
public interface UserMapper {
}
```

### mapper接口映射文件

```xml [UserMapper.xml]
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.hjc.demo.mapper.UserMapper">

</mapper>
```

### 相关配置文件

```properties [jdbc.properties]
jdbc.driver=com.mysql.cj.jdbc.Driver
jdbc.url=jdbc:mysql://localhost:3306/mybatis-example
jdbc.username=root
jdbc.password=123123
```

```xml [log4j.xml]
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE log4j:configuration SYSTEM "log4j.dtd">

<log4j:configuration xmlns:log4j="http://jakarta.apache.org/log4j/">

    <appender name="STDOUT" class="org.apache.log4j.ConsoleAppender">
        <param name="Encoding" value="UTF-8" />
        <layout class="org.apache.log4j.PatternLayout">
            <param name="ConversionPattern" value="%-5p %d{MM-dd HH:mm:ss,SSS} %m  (%F:%L) \n" />
        </layout>
    </appender>
    <logger name="java.sql">
        <level value="debug" />
    </logger>
    <logger name="org.apache.ibatis">
        <level value="info" />
    </logger>
    <root>
        <level value="debug" />
        <appender-ref ref="STDOUT" />
    </root>
</log4j:configuration>
```

### 测试代码

:::warning 说明

使用Junit测试

:::

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

    //...

}
```
