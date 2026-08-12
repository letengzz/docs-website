# MyBatis 构建入门程序

:::tip 环境要求

- JDK：Java8
- Maven：3.6.5

:::

## 1.创建数据

**创建表**：

```sql
CREATE DATABASE `mybatis-example`;

USE `mybatis-example`;

CREATE TABLE `company`(
id INT AUTO_INCREMENT,
c_name VARCHAR(100),
email VARCHAR(100),
PRIMARY KEY(id)
);
```

**添加数据**：

```SQL
INSERT INTO `company`(c_name,email) VALUES("阿李","1@ali.com");
INSERT INTO `company`(c_name,email) VALUES("疼讯","2@teng.com");
INSERT INTO `company`(c_name,email) VALUES("白度","3@bai.com");
```

## 2.创建项目

1. 创建一个maven项目(打包方式为jar即可)：

   ![image-20221222185104943](assets/202303010949956.png)

2. 创建一个**Java实体类**：实体类是和现实世界中某一个具体或抽象的概念对应，是软件开发过程中，为了管理现实世界中的数据而设计的模型。

   **实体类的多个不同的叫法**：

   - **领域模型**：`domain`

   - **实体**：`entity`

   - **Plain Old Java Object**：`POJO`

   - **一个Java类**：`Java bean`

   :::danger 注意

   Java 的实体类中，属性的类型不要使用基本数据类型，要使用包装类型。因为包装类型可以赋值为null，表示空，而基本数据类型不可以。

   :::

   ```java [com.hjc.demo.pojo/Company.java]
   package com.hjc.demo.pojo;

   /**
    * 数据库表 company 对应的实体类
    * @author hjc
    */
   public class Company {
       private Integer id;
       private String cName;
       private String email;

       public Company() {
       }

       public Company(Integer id, String cName, String email) {
           this.id = id;
           this.cName = cName;
           this.email = email;
       }

       public Integer getId() {
           return id;
       }

       public void setId(Integer id) {
           this.id = id;
       }

       public String getcName() {
           return cName;
       }

       public void setcName(String cName) {
           this.cName = cName;
       }

       public String getEmail() {
           return email;
       }

       public void setEmail(String email) {
           this.email = email;
       }

       @Override
       public String toString() {
           return "Company{" +
                   "id=" + id +
                   ", cName='" + cName + '\'' +
                   ", email='" + email + '\'' +
                   '}';
       }
   }
   ```

## 3.搭建框架开发环境

1. **导入依赖**：

   ```xml [pom.xml]
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
   </dependencies>
   ```

2. **Mybatis 全局核心配置文件**：

   习惯上命名为 `mybatis-config.xml`，这个文件名仅仅只是建议，并非强制要求。将来整合 Spring 之后，这个配置文件可以省略，操作时可以直接复制、粘贴。

   :::danger 注意

   配置文件存放的位置是src/main/resources目录下。

   :::

   ```xml [mybatis-config.xml]
   <?xml version="1.0" encoding="UTF-8" ?>
   <!DOCTYPE configuration
           PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
           "http://mybatis.org/dtd/mybatis-3-config.dtd">
   <configuration>

       <!-- environments表示配置Mybatis的开发环境，可以配置多个环境，在众多具体环境中，使用default属性指定实际运行时使用的环境。default属性的取值是environment标签的id属性的值。 -->
       <environments default="development">
           <!-- environment表示配置Mybatis的一个具体的环境 -->
           <environment id="development">

               <!-- Mybatis的内置的事务管理器 -->
               <transactionManager type="JDBC"/>

               <!-- 配置数据源 -->
               <dataSource type="POOLED">

                   <!-- 建立数据库连接的具体信息 -->
                   <property name="driver" value="com.mysql.cj.jdbc.Driver"/>
                   <property name="url" value="jdbc:mysql://localhost:3306/mybatis-example"/>
                   <property name="username" value="root"/>
                   <property name="password" value="123123"/>
               </dataSource>
           </environment>
       </environments>

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

3. **mapper接口**：

   MyBatis中的mapper接口相当于dao。但是区别在于，mapper仅仅是接口，不提供实现类。

   ```java [com.hjc.demo.mapper.CompanyMapper.java]
   /**
    * Mapper映射
    * @author hjc
    */
   public interface CompanyMapper {
       /**
        * 查询信息
        * @param id id
        * @return 所需要的信息
        */
       Company selectCompany(Integer id);
   }
   ```

4. **Mybatis 映射文件**：

   - [ORM对象关系映射](../../Others/ORM/index.md)

   **映射文件的命名规则**：表所对应的实体类的类名+Mapper.xml

   例：表t_user，映射的实体类为User，所对应的映射文件为UserMapper.xml 因此一个映射文件对应一个实体类，对应一张表的操作 MyBatis映射文件用于编写SQL，访问以及操作表中的数据 MyBatis映射文件存放的位置是src/main/resources/mappers目录下。

   **MyBatis中可以面向接口操作数据，要保证两个一致**：

   - mapper接口的全类名和映射文件的命名空间(namespace)保持一致
   - mapper接口中方法的方法名和映射文件中编写SQL的标签的id属性保持一致

   **目录结构**：

   <img src="./assets/202308281739576.png" alt="image-20230203204143207" style="zoom:50%;" />

   :::danger 注意

   CompanyMapper.xml所在的目录要和mybatis-config.xml中使用mapper标签配置的一致。

   :::

   ```xml [mapper/CompanyMapper.xml]
   <?xml version="1.0" encoding="UTF-8" ?>
   <!DOCTYPE mapper
           PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
           "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

   <!-- mapper是根标签，namespace属性：在Mybatis全局范围内找到一个具体的Mapper配置 -->
   <!-- 引入接口后，为了方便通过接口全类名来找到Mapper配置文件，所以通常将namespace属性设置为接口全类名 -->
   <mapper namespace="com.hjc.demo.mapper.CompanyMapper">

       <!-- 编写具体的SQL语句，使用id属性唯一的标记一条SQL语句 -->
       <!-- resultType属性：指定封装查询结果的Java实体类的全类名 -->
       <select id="selectCompany" resultType="com.hjc.demo.pojo.Company">
           <!-- Mybatis负责把SQL语句中的#{}部分替换成“?”占位符，在#{}内部还是要声明一个见名知意的名称 -->
           select id,c_name cName,email from company where id= #{id}
       </select>
   </mapper>
   ```

## 4.测试代码

:::warning 说明

- SqlSession：代表Java程序和**数据库**之间的**会话**。(HttpSession是Java程序和浏览器之间的会话)
- SqlSessionFactory：是"生产"SqlSession的"工厂"，使用的是工厂模式。

:::

```java [MyBatisTest.java]
public class MyBatisTest {
    @Test
    public void testSelectCompany() throws IOException {

        // 1.创建SqlSessionFactory对象
        // ①声明Mybatis全局配置文件的路径
        String mybatisConfigFilePath = "mybatis-config.xml";

        // ②以输入流的形式加载Mybatis配置文件
        InputStream inputStream = Resources.getResourceAsStream(mybatisConfigFilePath);

        // ③基于读取Mybatis配置文件的输入流创建SqlSessionFactory对象
        SqlSessionFactory sessionFactory = new SqlSessionFactoryBuilder().build(inputStream);

        // 2.使用SqlSessionFactory对象开启一个会话
        SqlSession session = sessionFactory.openSession();

        // 3.根据Mapper配置文件的名称空间+SQL语句的id找到具体的SQL语句
        // 格式是：名称空间.SQL语句的id
        String statement = "com.hjc.demo.mapper.CompanyMapper.selectCompany";

        // 要传入SQL语句的参数
        Integer id = 1;

        // 执行SQL语句
        Object result = session.selectOne(statement, id);

        System.out.println("查询结果:" + result);

        // 4.关闭SqlSession
        session.close();
    }
}
```

## 5.添加日志

**通过使用log4j添加日志**：

1. 添加依赖：

   ```xml
   <!-- log4j日志 -->
   <dependency>
   	<groupId>log4j</groupId>
   	<artifactId>log4j</artifactId>
   	<version>1.2.17</version>
   </dependency>
   ```

2. 加入log4j配置文件：

   ```xml [src/main/resources/log4j.xml]
   <?xml version="1.0" encoding="UTF-8" ?>
   <!DOCTYPE log4j:configuration SYSTEM "log4j.dtd">
   <log4j:configuration xmlns:log4j="http://jakarta.apache.org/log4j/">
   	<appender name="STDOUT" class="org.apache.log4j.ConsoleAppender">
   		<param name="Encoding" value="UTF-8" />
   		<layout class="org.apache.log4j.PatternLayout">
   			<param name="ConversionPattern" value="%-5p %d{MM-dd HH:mm:ss,SSS} %m (%F:%L) \n" />
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

3. 日志级别：FATAL(致命)>ERROR(错误)>WARN(警告)>INFO(信息)>DEBUG(调试) **从左到右打印的内容越来越详细**

4. MyBatis添加日志后执行语句：

   ![image-20230203204439018](assets/202303011008283.png)
