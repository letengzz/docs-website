# MyBatis 注解

因为最初设计时，MyBatis 是一个 XML 驱动的框架。配置信息是基于 XML 的，而且映射语句也是定义在 XML 中的。而到了 MyBatis 3，有新的可用的选择了。MyBatis3 构建在基于全面而且强大的 Java 配置 API 之上。这个配置 API 是基于 XML 的 MyBatis 配置的基础，也是新的基于注解配置的基础。注解提供了一种简单的方式来实现简单映射语句，而不会引入大量的开销。

注解主要分为三大类，即 [SQL 语句映射](#1)、[结果集映射](#2)和[关系映射](#3)。

![图片2](assets/202303011122854.png)

为了简化 XML 的配置，MyBatis 提供了注解。可以通过 MyBatis 的 jar 包查看注解：

![img](assets/202303011122371.gif)

## SQL 语句映射 {#1}

### @Insert:实现新增功能

使用 `@Insert` 注解实现 insert 语句，插入数据。

- 通过传递普通参数插入数据：

  ```java
  @Insert("insert into t_emp(emp_name, emp_salary) values (#{empName},#{empSalary})")
  int insertEmpToParam(@Param("empName") String empName,@Param("empSalary")Double empSalary);
  ```

- 通过传递 JavaBean 插入数据：

  ```java
  @Insert("insert into t_emp(emp_name, emp_salary) values (#{empName},#{empSalary})")
  int insertEmpToBean(Employee emp);
  ```

- 通过 [`@SelectKey` 注解](#@SelectKey:插入后,获取id的值)获取刚刚插入数据的 ID：

  ```java
  @Insert("insert into t_emp(emp_name, emp_salary) values (#{emp.empName},#{emp.empSalary})")
  @SelectKey(statement = "SELECT last_insert_id()", keyProperty = "emp.empId",keyColumn = "emp_id",before = false, resultType = Integer.class)
  void insertEmpToKey(@Param("emp") Employee emp);
  ```

### @Update:实现更新功能

使用 `@Update` 注解实现 update 语句，修改数据：

```java
@Update("update t_emp set emp_name=#{empName},emp_salary=#{empSalary} where emp_id = #{empId}")
void updateEmp(@Param("empName") String empName,@Param("empSalary")Double empSalary,@Param("empId")Integer empId);
```

### @Delete:实现删除功能

使用 `@Delete` 注解实现 delete 语句，删除数据：

```java
@Delete("delete from t_emp where emp_id=#{empId}")
int deleteEmp(Integer empId);
```

### @Select:实现查询功能

```java
@Select("select * from t_emp")
@Results({
	@Result(id = true,column = "emp_id",property = "empId"),
    @Result(column = "emp_Name",property = "empName"),
    @Result(column = "emp_salary",property = "empSalary")
})
List<Employee> selectAllEmp();
```

### @Param:映射多个参数

`@Param` 用于在 Mapper 接口中映射多个参数。

:::warning 说明

`@Param` 中的 value 属性可省略，用于指定参数的别名。

:::

```java
int insertEmpToParam(@Param("empName") String empName,@Param("empSalary")Double empSalary);
```

### @SelectKey:插入后,获取id的值

MySQL 在插入一条数据后，使用 `select last_insert_id()` 可以获取到自增 id 的值。

```java
@Insert("insert into t_emp(emp_name, emp_salary) values (#{emp.empName},#{emp.empSalary})")
@SelectKey(statement = "SELECT last_insert_id()", keyProperty = "emp.empId",keyColumn = "emp_id",before = false, resultType = Integer.class)
int insertEmpToKey(@Param("emp") Employee emp);
```

`@SelectKey` 各个属性：

- statement：表示要运行的 SQL 语句；
- keyProperty：可选项，表示将查询结果赋值给代码中的哪个对象；
- keyColumn：可选项，表示将查询结果赋值给数据表中的哪一列；
- resultType：指定 SQL 语句的返回值；
- before：默认值为 true，在执行插入语句之前，执行 `select last_insert_id()`。值为 false，则在执行插入语句之后，执行 `select last_insert_id()`。

### @MapKey:设置当前map的键

`@MapKey`设置当前map集合的键，会把当前我们查询出来的数据的某一个字段来作为键，把转换成的map集合作为值。

:::danger 注意

如果键重复就会把值覆盖掉，所以要找一个唯一的字段来作为键。

```java
@MapKey("id")
Map<Integer,Object> getStuAllToMap();
```

:::

## 结果集映射 {#2}

`@Result`、`@Results`、`@ResultMap` 是结果集映射的三大注解。

### Results

声明结果集映射关系。

`@Results` 属性：

- id：表示当前结果集声明的唯一标识；
- value：表示结果集映射关系；
- `@Result`：代表一个字段的映射关系。

#### Result

- column：指定数据库字段的名称
- property：指定实体类属性的名称
- jdbcType：数据库字段类型
- id：为 true 表示主键，默认 false。

```java
@Select("select * from t_emp")
@Results({
	@Result(id = true,column = "emp_id",property = "empId"),
    @Result(column = "emp_name",property = "empName"),
    @Result(column = "emp_salary",property = "empSalary")
})
List<Employee> selectAllByResults();
```

### ResultMap

可使用 @ResultMap 来引用映射结果集，其中 value 可省略。

```java
@Select("select * from t_emp where id = #{id}")
@ResultMap(value="empMap")
Employee selectById(Integer id);
```

这样不需要每次声明结果集映射时都复制冗余代码，简化开发，提高了代码的复用性。

1. 使用 `@ResultMap` 注解引用 Mapper XML 文件中 resultMap 定义的映射：

   ```java
   @Select("select * from t_emp")
   @ResultMap("empMap")
   List<Employee> getAllEmp();
   ```

2. mapper映射文件中增加resultMap语句：

   ```xml
   <!-- 结果映射，和其他方法共用 -->
   <resultMap id="empMap" type="com.hjc.demo.pojo.Employee">
   	<id column="emp_id" property="empId"/>
       <result column="emp_name" property="empName"/>
       <result column="emp_salary" property="empSalary"/>
   </resultMap>
   ```

## 关系映射 {#3}

:::tip 提示

下列各项操作均使用[t_dept表、t_emp表](Table/dept_emp.md)来操作。

:::

### @one:用于一对一关系映射

使用 `@One` 注解实现一对一关联映射。使用 `@Result` 注解的 one 属性配合 `@One` 注解实现关联映射。`@One` 注解通过 select 属性指定了 getDeptEmpTwo 方法，当每条数据映射时，将会调用 getDeptEmpTwo 方法。：

```java
@Select("SELECT * FROM t_emp")
@Results({
	@Result(id = true,column = "emp_id",property = "empId"),
    @Result(column = "emp_name",property = "empName"),
    @Result(column = "emp_salary",property = "empSalary"),
    @Result(column = "dept_id",property = "dept",one = @One(select = "getDeptEmpTwo"))
})
List<Employee> getEmpDeptOne();

@Select("select * from t_dept where dept_id=#{id}")
@Results({
	@Result(id=true, column="dept_id", property="deptId"),
    @Result(column="dept_name", property="deptName"),
    @Result(column="dept_city", property="deptCity")
})
Department getDeptEmpTwo(Integer id);
```

### @many:用于一对多关系映射

使用 `@Many` 注解实现一对多关联关系映射，通过 `@Result` 注解的 many 属性配合 `@Many` 注解实现一对多映射。其中，`@Many` 注解通过 select 属性指定映射方法 getDeptEmpTwo。

:::danger 注意

getDeptEmpTwo 映射方法在同一 Mapper 中进行了定义：

```java
@Select("select * from t_dept")
@Results({
	@Result(id=true, column="dept_id", property="deptId"),
    @Result(column="dept_name", property="deptName"),
    @Result(column="dept_city", property="deptCity"),
    @Result(column = "dept_id",property = "employees",many = @Many(select = "getDeptEmpTwo"))
})
List<Department> getDeptEmpOne();

@Select("SELECT * FROM t_emp where dept_id = #{id}")
@Results({
    @Result(id = true,column = "emp_id",property = "empId"),
    @Result(column = "emp_name",property = "empName"),
    @Result(column = "emp_salary",property = "empSalary"),
})
List<Employee> getDeptEmpTwo(Integer id);
```

:::
