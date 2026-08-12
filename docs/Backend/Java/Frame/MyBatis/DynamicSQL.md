# MyBatis 动态SQL

动态 SQL 是 MyBatis 的强大特性之一。在 JDBC 或其它类似的框架中，开发人员通常需要手动拼接 SQL 语句。根据不同的条件拼接 SQL 语句是一件极其痛苦的工作。例如，拼接时要确保添加了必要的空格，还要注意去掉列表最后一个列名的逗号。而动态 SQL 恰好解决了这一问题，可以根据场景动态的构建查询。

动态 SQL 大大减少了编写代码的工作量，更体现了 MyBatis 的灵活性、高度可配置性和可维护性。

> MyBatis 也可以在注解中配置 SQL，但是由于注解功能受限，且对于复杂的 SQL 语句来说可读性差，所以使用较少。

MyBatis 采用功能强大的基于 OGNL(`Object Graph Navigation Language`，对象导航语言)的表达式来消除其他元素。

MyBatis 的动态 SQL 包括以下几种元素：

![](assets/202303011628126.png)

:::tip 提示

下列各项操作均使用[user表](Table/user.md)来操作。

:::

## if标签

MyBatis if 类似于 Java 中的 if 语句，是 MyBatis 中最常用的**判断语句**。使用 if 标签可以节省许多拼接 SQL 的工作，把精力集中在 XML 的维护上。

if 语句使用方法简单，**必须存在test属性**(判断条件)。

:::warning 说明

当判断条件为 true 时，才会执行所包含的 SQL 语句。

:::

:::danger 注意

使用if标签时，需要注意WHERE语句放置位置，当if标签为一个时，WHERE语句需放入在if标签内，避免当条件不满足时，WHERE语句多余，出现 SQL 语法异常。当if标签为多个时，可将WHERE放在if标签外并在后追加一个恒成立语句，配合if标签内的SQL语句前加`AND`进行拼接。

:::

**语法格式**：

```xml
<if test="判断条件">
	SQL语句
</if>
```

**例**：

在 if 语句中包含 where 子句：

```xml
<select id="selectUserByLike" resultType="com.hjc.demo.pojo.User">
    SELECT * FROM user
    <if test="username != null and username != ''">
        WHERE username LIKE #{username}
    </if>
</select>
```

当username不为null或空字符串时，执行if标签中的SQL语句，即 `SELECT * FROM user WHERE username LIKE #{username}      `，当username为null或空字符串时，不执行if标签中的SQL语句，即 `SELECT * FROM user     `

---

可多个 if 语句同时使用，使用`AND`连接。多个条件进行模糊查询。如果条件都不满足，则返回所有的记录。但是，如果你传递了任意一个参数，它就会返回与给定参数相匹配的记录：

```xml
<select id="selectUserByLike" resultType="com.hjc.demo.pojo.User">
     SELECT * FROM user WHERE 1=1
    <if test="username != null and username != ''">
        AND username LIKE #{username}
    </if>
    <if test="password != null and password != ''">
        AND password LIKE #{password}
    </if>
</select>
```

## where标签

当单独使用if标签时，会需要**额外注意where语句的拼接及使用**，稍有不慎就会出现SQL语句拼接异常，为解决条件判断时可能出现的问题，Mybatis提供了where标签来解决此类问题。

where 标签主要用来**简化 SQL 语句中的条件判断**，除能在条件判断前加WHERE，还可以自动处理条件。

if 语句中判断条件为 true 时，where 关键字才会加入到组装的 SQL 里面，否则就不加入。where 会检索语句，它会将 where 后的第一个 SQL 条件语句的 AND 或者 OR 关键词去掉。

**语法格式**：

```xml
<where>
    <if test="判断条件">
        AND/OR ...
    </if>
</where>
```

**例**：

```xml [UserMapper.xml]
<select id="selectUserByLike" resultType="com.hjc.demo.pojo.User">
     SELECT * FROM user
    <where>
    	<if test="username != null and username != ''">
        	AND username LIKE #{username}
    	</if>
    	<if test="password != null and password != ''">
        	AND password LIKE #{password}
    	</if>
    </where>
</select>
```

## set标签

在 MyBatis 中，update 语句可以使用 set 标签动态更新列。set 标签可以**为 SQL 语句动态的添加 SET 关键字，并且动态剔除两端多余的逗号**。

**语法格式**：

```xml
<set>
	<if test="判断条件">
       ... ,
    </if>
</set>
```

**例**：

所有条件都满足 `SET username=?, password=?` ，部分条件满足 `SET username=?`，所有条件都不满足 `update t_emp where emp_id=?` (没有set子句的update语句会导致SQL语法错误)

```xml [UserMapper.xml]
<!--使用set元素动态修改记录 -->
<update id="updateUser" parameterType="com.hjc.demo.pojo.User">
	UPDATE user
	<set>
		<if test="username!=null">
			username=#{username},
        </if>
        <if test="password!=null">
            password=#{password},
        </if>
	</set>
	WHERE id=#{id}
</update>
```

## trim标签

在 MyBatis 中除了使用 if+where 实现多条件查询，还有一个更为灵活的元素 trim 能够替代之前的做法。

trim **一般用于去除 SQL 语句中多余的 AND 关键字、逗号`,`或者给 SQL 语句前拼接 where、set 等后缀**，可用于选择性插入、更新、删除或者条件查询等操作。

若标签中没有内容时，trim标签没有任何效果。

:::danger 注意

prefixOverrides/suffixOverrides可以使用"|"分隔有可能的多个值。

:::

**语法格式**：

```xml
<trim prefix="前缀" suffix="后缀" prefixOverrides="忽略前缀字符" suffixOverrides="忽略后缀字符">
    SQL语句
</trim>
```

**trim 中属性说明**：

![图片1](assets/202303011628406.png)

**例**：

```xml [UserMapper.xml]
<select id="selectUser" resultType="com.hjc.demo.pojo.User">
    SELECT * FROM user
    <trim prefix="where" prefixOverrides="and|or">
        <if test="username != null and username !=''">
            AND username = #{username}
        </if>
        <if test="password!= null and username !='' ">
            AND password = #{password}
        </if>
    </trim>
</select>
```

```java [WebsiteMapper.java]
public List<User> selectUser(User user);
```

## choose、when和otherwise标签

MyBatis 中动态语句 choose-when-otherwise 类似于 Java 中的 switch-case-default 语句。由于 MyBatis 并没有为 if 提供对应的 else 标签，如果想要达到`<if>...<else>...</else> </if>` 的效果，可以借助 choose、when、otherwise 来实现。

:::danger 注意

when至少有一个，otherwise最多只能有一个。

:::

**语法格式**：

```xml
<choose>
    <when test="判断条件1">
        SQL语句1
    </when >
    <when test="判断条件2">
        SQL语句2
    </when >
    <when test="判断条件3">
        SQL语句3
    </when >
    <otherwise>
        SQL语句4
    </otherwise>
</choose>
```

choose 标签按顺序判断其内部 when 标签中的判断条件是否成立，如果有一个成立，则执行相应的 SQL 语句，choose 执行结束；如果都不成立，则执行 otherwise 中的 SQL 语句。这类似于 Java 的 switch 语句，choose 为 switch，when 为 case，otherwise 则为 default。

**例**：

```xml [UserMapper.xml]
<select id="getUserByConditionCWO" resultType="com.hjc.demo.pojo.User">
        select * from user
        <where>
            <choose>
                <when test="username != null and username != ''">
                    username = #{username}
                </when>
                <when test="password != null and password != ''">
                    password = #{password}
                </when>
                <when test="age != null and age != ''">
                    age = #{age}
                </when>
                <when test="sex != null and sex != ''">
                    sex = #{sex}
                </when>
                <otherwise>
                    id = 1
                </otherwise>
            </choose>
        </where>
</select>
```

## foreach标签

对于一些 SQL 语句中含有 IN 条件，需要迭代条件集合来生成的情况，可以使用 foreach 来实现 SQL 条件的迭代。

Mybatis foreach 标签用于循环语句，它很好的支持了数据和 List、set 接口的集合，并对此**提供遍历的功能**。

**语法格式**：

```xml
<foreach item="item" index="index" collection="list|array|map key" open="(" separator="," close=")">
    参数值
</foreach>
```

**foreach 标签说明**：

- item：表示集合中每一个元素进行迭代时的别名。
- index：指定一个名字，表示在迭代过程中每次迭代到的位置。
- open：表示该语句以什么开始(既然是 in 条件语句，所以必然以`(`开始)。
- separator：表示在每次进行迭代之间以什么符号作为分隔符(既然是 in 条件语句，所以必然以`,`作为分隔符)。
- close：表示该语句以什么结束(既然是 in 条件语句，所以必然以`)`开始)。

**collection 属性是必选的**，但在不同情况下该属性的值是不一样的。

主要情况：

- 如果传入的是单参数且参数类型是一个 List，collection 属性值为 list。
- 如果传入的是单参数且参数类型是一个 array 数组，collection 的属性值为 array。
- 如果传入的参数是多个，需要把它们封装成一个 Map，当然单参数也可以封装成 Map。Map 的 key 是参数名，collection 属性值是传入的 List 或 array 对象在自己封装的 Map 中的 key。

**拓展**：在使用 foreach 标签时，应提前预估一下 collection 对象的长度。因为大量数据的 IN 语句会影响性能，且还有一些数据库会限制执行的 SQL 语句长度。

:::danger 注意

- 在实际开发中，为了避免隐晦的表达造成一定的误会，建议使用[`@Param`注解](Annotation.md)明确声明变量的名称，然后在foreach标签的collection属性中按照`@Param`注解指定的名称来引用传入的参数。

- 实现批量更新则需要多条SQL语句拼起来，用分号分开。也就是一次性发送多条SQL语句让数据库执行。此时需要在**数据库连接信息的URL地址**中设置：

  ```properties
  jdbc.url=jdbc:mysql://localhost:3306/mybatis-example?allowMultiQueries=true
  ```

  ```xml [UserMapper.xml]
  <update id="updateUser">
      <foreach collection="userList" item="user" separator=";">
          update user set username=#{user.username} where id=#{user.id}
      </foreach>
  </update>
  ```

  ```java [UserMapper.java]
  public List<User> updateUser(@Param("userList") List<User> userList);
  ```

:::

**例**：

- **批量查询**：

  ```xml [UserMapper.xml]
  <select id="selectUser" parameterType="com.hjc.demo.pojo.User" resultType="com.hjc.demo.pojo.User">
        SELECT * FROM user WHERE age in
        <foreach item="age" index="index" collection="lists" open="(" separator="," close=")">
            #{age}
        </foreach>
  </select>
  ```

  ```java [UserMapper.java]
  public List<User> selectUser(@Param("lists") List<Integer> ageList);
  ```

- **批量添加**：

  ```xml [UserMapper.xml]
  <select id="insertUser" parameterType="com.hjc.demo.pojo.User" resultType="com.hjc.demo.pojo.User">
        INSERT INTO user VALUES
        <foreach index="user" collection="users" separator=",">
            (null,#{user.username},#{user.password},#{user.age})
        </foreach>
  </select>
  ```

  ```java [UserMapper.java]
  public List<User> insertUser(@Param("users") List<User> users);
  ```

- **批量删除**：

  ```xml [UserMapper.xml]
  <select id="deleteUser" parameterType="com.hjc.demo.pojo.User" resultType="com.hjc.demo.pojo.User">
      <!-- DELETE FROM user WHERE age IN
      <foreach index="age" collection="ageList" open="(" separator="," close=")">
          #{age}
      </foreach> -->
      DELETE FROM user WHERE
      <foreach index="age" collection="ageList" separator="or">
          age = #{age}
      </foreach>
  </select>
  ```

  ```java [UserMapper.java]
  public List<User> deleteUser(@Param("ageList") List<User> ageLists);
  ```

## bind标签

每个数据库的拼接函数或连接符号都不同，例如 MySQL 的 concat 函数、Oracle 的连接符号"||"等。这样 SQL 映射文件就需要根据不同的数据库提供不同的实现，显然比较麻烦，且不利于代码的移植。MyBatis 提供了 bind 标签来解决这一问题。

bind 标签可以通过 OGNL 表达式自定义一个上下文变量。

bind 元素属性：

- value：对应传入实体类的某个字段，可以进行字符串拼接等特殊处理。
- name：给对应参数取的别名。

**例**：按照网站名称进行模糊查询，SQL 映射文件如下。

```xml
<select id="selectUser" resultType="com.hjc.demo.pojo.User">
    <bind name="pattern" value="'%'+username+'%'" />
    SELECT * FROM user    WHERE username like #{pattern}
</select>
```

以上代码中的"username"代表传递进来的参数，它和通配符连接后，赋给了 pattern，然后就可以在 select 语句中使用这个变量进行模糊查询，不管是 MySQL 数据库还是 Oracle 数据库都可以使用这样的语句，提高了可移植性。

**传递多个参数时 bind**：

```java [UserMapper.java]
public List<User> selectWebsite(User user);
```

```xml [UserMapper.xml]
<select id="selectUser" resultType="com.hjc.demo.pojo.User">
    <bind name="pattern_name" value="'%'+username+'%'" />
    <bind name="pattern_pwd" value="'%'+password+'%'" />
    SELECT * FROM user WHERE
    	username like #{pattern_name}
    	AND password like #{pattern_pwd}
</select>
```

## sql标签

sql标签可以将常用的片段进行记录，在需要用的时候就可以直接引用。

:::tip 提示

在查询功能的时候，尽量不要写"`*`"，要把查询的字段手动写上。

:::

抽取重复的SQL片段：

```xml
<!-- 使用sql标签抽取重复出现的SQL片段 -->
<sql id="userColumns">
    id,username,password,age
</sql>
```

引用已抽取的SQL片段：

```xml
<!-- 使用include标签引用声明的SQL片段 -->
<select id="getStuByConditionSql" resultType="User">
	SELECT <include refid="userColumns"/> FROM user
</select>

```

## script标签

要在带注解的映射器接口类中使用动态 SQL，可以使用 `script `元素：

```java
@Update({"<script>",
      "update user",
      "  <set>",
      "    <if test='username != null'>username=#{username},</if>",
      "    <if test='password != null'>password=#{password},</if>",
      "  </set>",
      "where id=#{id}",
      "</script>"})
void updateAuthorValues(Author author);
```

## 多数据库支持

如果配置了 `databaseIdProvider`，你就可以在动态代码中使用名为 “`_databaseId`” 的变量来为不同的数据库构建特定的语句：

```xml
<insert id="insert">
  <selectKey keyProperty="id" resultType="int" order="BEFORE">
    <if test="_databaseId == 'oracle'">
      select seq_users.nextval from dual
    </if>
    <if test="_databaseId == 'db2'">
      select nextval for seq_users from sysibm.sysdummy1"
    </if>
  </selectKey>
  insert into user values (#{id}, #{name})
</insert>
```

## 动态 SQL 中的插入脚本语言

MyBatis 从 3.2 版本开始支持插入脚本语言，这允许你插入一种语言驱动，并基于这种语言来编写动态 SQL 查询语句。

可以通过实现以下接口来插入一种语言：

```java
public interface LanguageDriver {
  ParameterHandler createParameterHandler(MappedStatement mappedStatement, Object parameterObject, BoundSql boundSql);
  SqlSource createSqlSource(Configuration configuration, XNode script, Class<?> parameterType);
  SqlSource createSqlSource(Configuration configuration, String script, Class<?> parameterType);
}
```

实现自定义语言驱动后，你就可以在 `mybatis-config.xml` 文件中将它设置为默认语言：

```xml
<typeAliases>
  <typeAlias type="org.sample.MyLanguageDriver" alias="myLanguage"/>
</typeAliases>
<settings>
  <setting name="defaultScriptingLanguage" value="myLanguage"/>
</settings>
```

或者，你也可以使用 `lang `属性为特定的语句指定语言：

```xml
<select id="selectBlog" lang="myLanguage">
  SELECT * FROM BLOG
</select>
```

或者，在你的 `mapper `接口上添加 `@Lang` 注解：

```java
public interface Mapper {
  @Lang(MyLanguageDriver.class)
  @Select("SELECT * FROM BLOG")
  List<Blog> selectBlog();
}
```

可以使用 `Apache Velocity` 作为动态语言，更多细节请参考 `MyBatis-Velocity` 项目。

所有 xml 标签都由默认 MyBatis 语言提供，而它由语言驱动`org.apache.ibatis.scripting.xmltags.XmlLanguageDriver`（别名为 xml）所提供。
