# Mybatis 分页操作

:::tip 提示

下列各项操作均使用[user表](Table/user.md)来操作(不做相关MyBatis操作)。

:::

## 手动实现分页操作

MyBatis 的分页功能是基于内存的分页，即先查询出所有记录，再按起始位置和页面容量取出结果。

**例**：

```java [UserMapper.java]
 List<User> selectAllUserLimit(@Param("from") Integer currentPageNo,@Param("pageSize") Integer pageSize);
```

起始位置（from）和页面容量（pageSize），用于实现分页查询。

修改 UserMapper.xml 的查询语句，增加 limit 关键字：

```xml [UserMapper.xml]
<select id="selectAllUserLimit" resultType="com.hjc.demo.pojo.User">
	select * from user limit #{from},#{pageSize}
</select>
```

**测试类代码**：

```java
@Test
public void testPagingLimit() throws IOException {
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

    List<User> users = mapper.selectAllUserLimit(1, 3);
    users.forEach(System.out::println);

    // 关闭SqlSession
    sqlSession.close();
}
```

运行结果：

> DEBUG ==> Preparing: select \* from user limit ?,?
>
> DEBUG ==> Parameters: 1(Integer), 3(Integer)
>
> DEBUG ,354 <== Total: 3
>
> `User{id=2, username='关羽', password='123456', age=20}`
>
> `User{id=3, username='张飞', password='124356', age=19}`
>
> `User{id=4, username='司马光', password='494161', age=23}`

根据传入的起始位置(currentPageNo=0)和页面容量(pageSize=3)进行相应分页，查看第一页的数据列表，运行测试方法，输出正确的分页列表。

:::danger 注意

MyBatis 实现分页查询属于 DAO 层操作，由于 DAO 层不牵涉任何业务实现，所以实现分页的方法中第一个参数为 limit 的起始位置(下标从 0 开始)，而不是用户输入的真正页码(页码从1开始)。页码如何转换为 limit 的起始位置下标，即：起始位置下标=（页码-1）\*页面容量，那么这个转换操作必然不能在 DAO 层实现，需要在业务层实现。所以我们在测试类中传入的参数为下标，而不是页码。

:::

## 使用第三方实现分页操作

### 1.下载jar包/配置POM

- 通过[jar包下载](https://github.com/pagehelper/Mybatis-PageHelper/releases/tag/v5.3.2) (不推荐)

- 通过构建Maven项目添加相关依赖：

  ```xml [pom.xml]
  <dependency>
  	<groupId>com.github.pagehelper</groupId>
  	<artifactId>pagehelper</artifactId>
  	<version>5.2.0</version>
  </dependency>
  ```

### 2.配置分页插件

在MyBatis的核心配置文件中配置插件：

```xml [mybatis-config.xml]
<plugins>
	<!--设置分页插件-->
    <plugin interceptor="com.github.pagehelper.PageInterceptor"/>
</plugins>
```

### 分页插件的使用

1. 在查询功能之前使用`PageHelper.startPage(int pageNum, int pageSize)`开启分页功能

   - pageNum：当前页的页码
   - pageSize：每页显示的条数

2. 在查询获取list集合之后，使用`PageInfo pageInfo = new PageInfo<>(List list, int navigatePages)`获取分页相关数据

   - list：分页之后的数据
   - navigatePages：导航分页的页码数(一般为奇数)

3. 分页相关数据

   1. > PageInfo{ pageNum=8, pageSize=4, size=2, startRow=29, endRow=30, total=30, pages=8, list=Page{count=true, pageNum=8, pageSize=4, startRow=28, endRow=32, total=30, pages=8, reasonable=false, pageSizeZero=false}, prePage=7, nextPage=0, isFirstPage=false, isLastPage=true, hasPreviousPage=true, hasNextPage=false, navigatePages=5, navigateFirstPage4, navigateLastPage8, navigatepageNums=[4, 5, 6, 7, 8] }

   2. 常用数据：

      1. pageNum：当前页的页码
      2. pageSize：每页显示的条数
      3. size：当前页显示的真实条数
      4. total：总记录数
      5. pages：总页数
      6. prePage：上一页的页码
      7. nextPage：下一页的页码
      8. isFirstPage/isLastPage：是否为第一页/最后一页
      9. hasPreviousPage/hasNextPage：是否存在上一页/下一页
      10. navigatePages：导航分页的页码数(一般为奇数)
      11. navigatepageNums：导航分页的页码，[1,2,3,4,5]

```java
@Test
public void testPaging() throws IOException {
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

    PageHelper.startPage(1,3);
    List<User> users = mapper.selectAllUser();
    //查询之后 获取分页的所有数据
    PageInfo<User> page = new PageInfo<>(users,5);
    System.out.println("page = " + page);
    users.forEach(System.out::println);

    // 关闭SqlSession
    sqlSession.close();
}
```
