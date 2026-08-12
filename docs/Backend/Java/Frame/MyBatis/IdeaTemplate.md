# IDEA配置模板

IDEA添加模板：settings --> Editor --> File and Code Templates

![image-20230202101540277](assets/202303011700490.png)

## 配置核心配置文件模板

```xml
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

![image-20230202101734608](assets/202303011700809.png)

## 配置映射文件模板

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
"http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="">

</mapper>
```

![image-20230202101631814](assets/202303011700956.png)
