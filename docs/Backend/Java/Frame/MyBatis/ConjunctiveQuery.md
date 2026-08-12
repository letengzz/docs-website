# MyBatis 关联查询及延迟加载

:::tip 提示

下列各项操作均使用[t_dept表、t_emp表](Table/dept_emp.md)来操作。

:::

## 关联查询

SQL关联关系主要体现在数据表的对应关系上。Mybatis中一个表对应一个Java实体类，所以表的对应关系对应的就是反应在Java实体类中的关系。

**关联在数量上的关系**：一对一、一对多、多对多。

**关联在关联关系的方向**(主要体现在Java实体类)：单向、双向。

### 一对一关系

在 MyBatis 中，通过 resultMap 元素的子元素 association 处理一对一级联关系。

association 元素常见属性：

- property：指定映射到实体类的对象属性。
- column：指定表中对应的字段（即查询返回的列名）。
- javaType：指定映射到实体对象属性的类型。
- select：指定引入嵌套查询的子 SQL 语句，该属性用于关联映射中的嵌套查询。

**例**：

```xml
<association property="dept" select="com.hjc.demo.mapper.DeptMapper.getEmpAndDeptByStepTwo" column="dept_id" javaType="com.hjc.demo.pojo.Department" fetchType="lazy" />
```

一对一关联查询可采用以下两种方式：

- **单步查询**：通过关联查询实现(级联属性赋值、使用association)
- **分步查询**：通过两次或多次查询，为一对一关系的实体 Bean 赋值

#### 单步查询(级联)

:::danger 注意

级联的优点是获取关联数据十分便捷。但是级联过多会增加系统的复杂度，同时降低系统的性能，此增彼减。所以记录超过 3 层时，就不要考虑使用级联了，因为这样会造成多个对象的关联，导致系统的耦合、负载和难以维护。

:::

```java [EmpMapper.java]
/**
* 获取员工以及所在部门信息
* 两表联查
* @param eid 员工id
* @return 员工信息
*/
Employee getEmpAndDept(@Param("eid") Integer eid);
```

```xml [EmpMapper.xml]
<!-- 处理一对一映射关系：级联属性赋值-->
<resultMap id="empAndDeptResultMapOne" type="Employee">
	<id property="empId" column="emp_id"/>
    <result property="empName" column="emp_name"/>
    <result property="empSalary" column="emp_salary"/>
    <result property="dept.deptId" column="dept_id"/>
    <result property="dept.deptName" column="dept_name"/>
    <result property="dept.deptCity" column="dept_city"/>
</resultMap>
<!-- 使用association：专门处理一对一的关系-->
<resultMap id="empAndDeptResultMapTwo" type="Employee">
    <id property="empId" column="emp_id"/>
    <result property="empName" column="emp_name"/>
    <result property="empSalary" column="emp_salary"/>
    <association property="dept" javaType="Department">
    	<id property="deptId" column="dept_id"/>
        <result property="deptName" column="dept_name"/>
        <result property="deptCity" column="dept_city"/>
	</association>
</resultMap>
<!-- <select id="getEmpAndDept" resultMap="empAndDeptResultMapOne"> -->
<select id="getEmpAndDept" resultMap="empAndDeptResultMapTwo">
	select * from t_emp left join t_dept  on t_dept.dept_id = t_emp.dept_id where t_emp.emp_id = #{eid}
</select>
```

测试：

```java
@Test
public void testGetEmpAndDept() throws IOException {
    //读取MyBatis的核心配置文件
    InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
    //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
    SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
    //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
    //SqlSession sqlSession = sqlSessionFactory.openSession();
    //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
    SqlSession sqlSession = build.openSession(true);
    EmpMapper mapper = sqlSession.getMapper(EmpMapper.class);
    Employee empAndDept = mapper.getEmpAndDept(1);
	System.out.println("员工名字:" + empAndDept.getEmpName()+",员工工资:"+empAndDept.getEmpSalary()+",员工所在部门:"+empAndDept.getDept().getDeptName()+",部门地点:"+empAndDept.getDept().getDeptCity());
}
```

运行结果：

> DEBUG ==> Preparing: select \* from t_emp left join t_dept on t_dept.dept_id = t_emp.dept_id where t_emp.emp_id = ?
>
> DEBUG ==> Parameters: 1(Integer)
>
> DEBUG <== Total: 1
>
> 员工名字:SMITH,员工工资:100.1,员工所在部门:ACCOUNTING,部门地点:NEW YORK

#### 分步查询

```java [EmpMapper.java]
/**
* 通过分步查询查询员工以及员工所对应的部门信息
* 分布查询第一步：查询员工信息
* @param eid 员工id
* @return 员工信息
*/
Employee getEmpAndDeptByStepOne(@Param("eid") Integer eid);
```

```xml [EmpMapper.xml]
<resultMap id="empAndDeptByStepResultMap" type="Employee">
	<id property="empId" column="emp_id"/>
    <result property="empName" column="emp_name"/>
    <result property="empSalary" column="emp_salary"/>
    <association property="dept" select="com.hjc.demo.mapper.DeptMapper.getEmpAndDeptByStepTwo" column="dept_id">
	</association>
</resultMap>
<select id="getEmpAndDeptByStepOne" resultMap="empAndDeptByStepResultMap">
	select * from t_emp where emp_id = #{eid}
</select>
```

```java [DeptMapper.java]
/**
* 通过分步查询查询员工以及员工所对应的部门信息
* 分布查询第二步:通过did查询员工所对应的部门
* @param did 部门id
* @return 部门信息
*/
Department getEmpAndDeptByStepTwo(@Param("did") Integer did);
```

```xml [DeptMapper.xml]
<select id="getEmpAndDeptByStepTwo" resultType="com.hjc.demo.pojo.Department">
    select dept_id,dept_name deptName,dept_city deptCity from t_dept where dept_id = #{did}
</select>
```

测试：

```java
@Test
public void testGetEmpAndDeptByStep() throws IOException {
	//读取MyBatis的核心配置文件
    InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
    //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
    SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
    //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
    //SqlSession sqlSession = sqlSessionFactory.openSession();
    //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
    SqlSession sqlSession = build.openSession(true);
    EmpMapper mapper = sqlSession.getMapper(EmpMapper.class);
    Employee empAndDeptByStepOne = mapper.getEmpAndDeptByStepOne(1);
    System.out.println("员工名字:" + empAndDeptByStepOne.getEmpName()+",员工工资:"+empAndDeptByStepOne.getEmpSalary()+",员工所在部门:"+empAndDeptByStepOne.getDept().getDeptName()+",部门地点:"+empAndDeptByStepOne.getDept().getDeptCity());
}
```

运行结果如下：

> DEBUG ==> Preparing: select \* from t_emp where emp_id = ?
>
> DEBUG ==> Parameters: 1(Integer)
>
> DEBUG <== Total: 1
>
> DEBUG ==> Preparing: select dept_id,dept_name deptName,dept_city deptCity from t_dept where dept_id = ?
>
> DEBUG ==> Parameters: 1(Integer)
>
> DEBUG <== Total: 1
>
> 员工名字:SMITH,员工工资:100.1,员工所在部门:ACCOUNTING,部门地点:NEW YORK

### 一对多关系

在 MyBatis 中，通过 resultMap 元素的子元素 collection 处理一对多级联关系，collection 可以将关联查询的多条记录映射到一个 list 集合属性中。

在 collection 元素常见属性：

- property：指定映射到实体类的对象属性。
- column：指定表中对应的字段（即查询返回的列名）。
- javaType：指定映射到实体对象属性的类型。
- select：指定引入嵌套查询的子 SQL 语句，该属性用于关联映射中的嵌套查询。

**例**：

```xml
<collection property="orderList"        ofType="com.hjc.demo.po.Order" column="id"        select="com.hjc.demo.mapper.OrderMapper.selectOrderById" />
```

一对多关联查询可采用以下两种方式：

- **分步查询**：通过两次或多次查询，为一对多关系的实体 Bean 赋值
- **单步查询**：通过关联查询实现

#### 单步查询(级联)

:::danger 注意

级联的优点是获取关联数据十分便捷。但是级联过多会增加系统的复杂度，同时降低系统的性能，此增彼减。所以记录超过 3 层时，就不要考虑使用级联了，因为这样会造成多个对象的关联，导致系统的耦合、负载和难以维护。

:::

```java [DeptMapper.java]
/**
* 获取部门以及部门中所有的员工信息
* 两表联查
* @param did 部门id
* @return 部门信息
*/
Department getDeptAndEmp(@Param("did") Integer did);
```

```xml [DeptMapper.xml]
<resultMap id="deptAndEmpResultMap" type="Department">
	<id property="deptId" column="dept_id"/>
    <result property="deptName" column="dept_name"/>
    <result property="deptCity" column="dept_city"/>
    <collection property="employees" ofType="Employee">
		<id property="empId" column="emp_id"/>
        <result property="empName" column="emp_name"/>
        <result property="empSalary" column="emp_salary"/>
    </collection>
</resultMap>
<select id="getDeptAndEmp" resultMap="deptAndEmpResultMap">
    select * from t_dept left join t_emp  on t_dept.dept_id = t_emp.dept_id where t_dept.dept_id = #{did}
</select>
```

测试：

```java
@Test
public void testGetDeptAndEmp() throws IOException {
	//读取MyBatis的核心配置文件
    InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
    //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
    SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
    //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
    //SqlSession sqlSession = sqlSessionFactory.openSession();
    //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
    SqlSession sqlSession = build.openSession(true);
    DeptMapper mapper = sqlSession.getMapper(DeptMapper.class);
    //通过两表联查(collection)
    Department deptAndEmp = mapper.getDeptAndEmp(1);
    System.out.println("部门名:" + deptAndEmp.getDeptName() + ",部门城市:" + deptAndEmp.getDeptCity());
    System.out.println("员工信息:");
    deptAndEmp.getEmployees().forEach((employee) -> {
    	System.out.println("员工名:"+employee.getEmpName()+",员工工资:"+employee.getEmpSalary());
    });
}
```

运行结果：

> DEBUG ==> Preparing: select \* from t_dept left join t_emp on t_dept.dept_id = t_emp.dept_id where t_dept.dept_id = ?
>
> DEBUG ==> Parameters: 1(Integer)
>
> DEBUG <== Total: 2
>
> 部门名:ACCOUNTING,部门城市:NEW YORK
> 员工信息:
> 员工名:SMITH,员工工资:100.1
> 员工名:WARD,员工工资:200.1

#### 分步查询

```java [DeptMapper.java]
/**
* 通过分步查询查询部门以及部门中所有的员工信息
* 分布查询第一步：查询部门信息
* @param did 部门id
* @return 部门信息
*/
Department getDeptAndEmpByStepOne(@Param("did") Integer did);
```

```xml [DeptMapper.xml]
<resultMap id="deptAndEmpByStepResultMap" type="Department">
	<id property="deptId" column="dept_id"/>
    <result property="deptName" column="dept_name"/>
    <collection property="employees" select="com.hjc.demo.mapper.EmpMapper.getDeptAndEmpByStepTwo" column="dept_id" />
</resultMap>
<select id="getDeptAndEmpByStepOne" resultMap="deptAndEmpByStepResultMap">
    select * from t_dept where dept_id = #{did}
</select>
```

```java [EmpMapper.java]
/**
* 通过分布查询查询部门以及部门中所有的员工信息
* 分步查询第二步:根据did查询员工信息
* @param did 员工id
* @return 员工信息
*/
List<Employee> getDeptAndEmpByStepTwo(@Param("did") Integer did);
```

```xml [EmpMapper.xml]
<select id="getDeptAndEmpByStepTwo" resultType="com.hjc.demo.pojo.Employee">
	select * from t_emp where dept_id = #{did}
</select>
```

测试：

```java
@Test
public void testGetDeptAndEmpByStep() throws IOException {
    //读取MyBatis的核心配置文件
    InputStream resource = Resources.getResourceAsStream("mybatis-config.xml");
    //通过核心配置文件所对应的字节输入流创建工厂类SqlSessionFactory，生产SqlSession对象
    SqlSessionFactory build = new SqlSessionFactoryBuilder().build(resource);
    //创建SqlSession对象，此时通过SqlSession对象所操作的sql都必须手动提交或回滚事务
    //SqlSession sqlSession = sqlSessionFactory.openSession();
    //创建SqlSession对象，此时通过SqlSession对象所操作的sql都会自动提交
    SqlSession sqlSession = build.openSession(true);
    DeptMapper mapper = sqlSession.getMapper(DeptMapper.class);
    //分步查询
    Department deptAndEmpByStepOne = mapper.getDeptAndEmpByStepOne(1);
	System.out.println("部门名:" + deptAndEmp.getDeptName() + ",部门城市:" + deptAndEmp.getDeptCity());
    System.out.println("员工信息:");
    deptAndEmp.getEmployees().forEach((employee) -> {
    	System.out.println("员工名:"+employee.getEmpName()+",员工工资:"+employee.getEmpSalary());
    });
}
```

运行结果：

> DEBUG ==> Preparing: select \* from t_dept where dept_id = ?
>
> DEBUG ==> Parameters: 1(Integer)
>
> DEBUG ====> Preparing: select \* from t_emp where dept_id = ?
>
> DEBUG ====> Parameters: 1(Integer)
>
> DEBUG <==== Total: 2
>
> DEBUG <== Total: 1
>
> 部门名:ACCOUNTING,部门城市:NEW YORK
> 员工信息:
> 员工名:SMITH,员工工资:100.1
> 员工名:WARD,员工工资:200.1

### 多对多关系

实际应用中，由于多对多的关系比较复杂，会增加理解和关联的复杂度，所以应用较少。MyBatis 没有实现多对多级联，推荐通过两个一对多级联替换多对多级联，以降低关系的复杂度，简化程序。

## 延迟加载

分步查询可以实现**延迟加载**，但是必须在核心配置文件中设置[全局配置信息](CoreMapping.md#配置settings标签)：

- azyLoadingEnabled：延迟加载的全局开关。当开启时，所有关联对象都会延迟加载。

- aggressiveLazyLoading：当开启时，任何方法的调用都会加载该对象的所有属性。 否则，每个 属性会按需加载此时就可以实现按需加载，获取的数据是什么，就只会执行相应的sql。此时可通过association和 collection中的fetchType属性设置当前的分步查询是否使用延迟加载，`fetchType="lazy(延迟加载)|eager(立即加载)"`
