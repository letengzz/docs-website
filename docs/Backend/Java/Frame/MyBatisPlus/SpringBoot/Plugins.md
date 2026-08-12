# Mybatis-Plus插件

## 分页

### 自带分页插件

MyBatis Plus只要简单的配置即可实现分页功能。进行分页查询时，若查询语句中包含一对多的查询，只能使用**[嵌套查询 (Nested Select for Collection)](https://mybatis.org/mybatis-3/sqlmap-xml.html#nested-select-for-collection)**，而不能使用**[嵌套结果映射 (Nested Results for Collection)](https://mybatis.org/mybatis-3/sqlmap-xml.html#nested-results-for-collection)**。

嵌套结果用多表连查，一对多关系会导致主数据重复出现（比如 1 道题对应 3 个选项，连查后会生成 3 条包含这道题的记录）。而分页插件是按 “记录条数” 分页的，它会把这些重复记录当成不同的主数据，导致分页结果和实际需要的主数据数量对不上。

**举例说明**：假设要查 “第 1 页，每页 10 道题”，且每道题平均有 3 个选项。

**用嵌套结果映射 (多表连查)**：

1. 连查后，10 道题会变成 30 条记录 (每道题重复 3 次，对应 3 个选项)。
2. 分页插件按 “30 条记录” 分页，取前 10 条 → 这 10 条记录实际只对应 3-4 道题 (每道题占 3 条记录)。
3. 结果：本想查 10 道题，实际只返回了 3-4 道，分页完全错误。

**用嵌套查询 (分步查)**：

1. 先查题目表，分页插件直接取前 10 道题 (无重复，准确)。
2. 再用这 10 道题的 ID 查对应的选项，组装后返回 → 正好 10 道题，每道题带 3 个选项。
3. 结果：符合预期，分页正确。

:::danger

版本 3.5.9+ 插件部分开始修改为可选依赖，具体查看下文 maven bom 部分，根据自行项目选取对应插件支持模块。 引入哪个模块才有分页插件：

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-extension</artifactId>
    <version>你的版本号（如 3.5.9 或更高）</version>
</dependency
```

也可以单独引入 `mybatis-plus-jsqlparser` 依赖：

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-jsqlparser</artifactId>
    <version>你的版本号（如 3.5.9 或更高）</version>
</dependency>
```

:::

**分页插件的原理**：

首先分页参数放到ThreadLocal中，拦截执行的sql，根据数据库类型添加对应的分页语句重写sql，例如：(`select * from table where a`) 转换为 (`select count(*) from table where a`)和(`select * from table where a limit ,`)

计算出了total总条数、pageNum当前第几页、pageSize每页大小和当前页的数据，是否为首页，是否为尾页，总页数等。

**配置插件功能**：

```java [config/PluginConfig.java]
@Configuration
//扫描mapper接口所在的包
@MapperScan("com.hjc.demo.mapper")
public class PluginConfig {
    //配置mybatisplus的插件 需要在插件中添加一个内部插件(分页插件叫做paginationInnerceptor)
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor(){
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}
```

**测试**：

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testSelectList() {
        //设置分页参数
        Page<User> page = new Page<>(1,3);
        //selectList()根据MP内置的条件构造器查询一个list集合，null表示没有条件，即查询所有
        userMapper.selectPage(page, null);
        //当前页的数据
        page.getRecords().forEach(user ->System.out.println("当前页的数据: "+user));
        //获取当前页的页码
        System.out.println("获取当前页的页码: "+page.getCurrent());
        //获取每页的条数
        System.out.println("获取每页的条数: "+page.getSize());
        //获取总页数
        System.out.println("获取总页数: "+page.getTotal());
        //是否存在上一页
        System.out.println("是否存在上一页: "+page.hasPrevious());
        //是否存在下一页
        System.out.println("是否存在下一页: "+page.hasNext());
        //当前分页总页数
        System.out.println("当前分页总页数: "+page.getPages());
    }
}
```

**xml自定义分页**：

UserMapper中定义接口方法：

```java
@Repository
public interface UserMapper extends BaseMapper<User> {
    /**
     * 根据年龄查询用户列表，分页显示
     * @param page 分页对象,xml中可以从里面进行取值,传递参数 Page 即自动分页,必须放在第一位
     * @param age 年龄
     * @return
     */
    IPage<User> selectPageVo(@Param("page") Page<User> page, @Param("age") Integer age);

}

```

UserMapper.xml中编写SQL：

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.hjc.demo.mapper.UserMapper">
    <!--SQL片段，记录基础字段-->
    <sql id="BaseColumns">id,name,age,email</sql>
    <select id="selectPageVo" resultType="com.hjc.demo.pojo.User">
        SELECT <include refid="BaseColumns"/> FROM t_user WHERE age > #{age}
    </select>
</mapper>
```

测试：

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testSelectList2() {
        Page<User> page = new Page<>(1,3);
        //selectList()根据MP内置的条件构造器查询一个list集合，null表示没有条件，即查询所有
        userMapper.selectPageVo(page,10);
        //当前页的数据
        page.getRecords().forEach(user ->System.out.println("当前页的数据: "+user));
        //获取当前页的页码
        System.out.println("获取当前页的页码: "+page.getCurrent());
        //获取每页的条数
        System.out.println("获取每页的条数: "+page.getSize());
        //获取总页数
        System.out.println("获取总页数: "+page.getTotal());
        //是否存在上一页
        System.out.println("是否存在上一页: "+page.hasPrevious());
        //是否存在下一页
        System.out.println("是否存在下一页: "+page.hasNext());
        //当前分页总页数
        System.out.println("当前分页总页数: "+page.getPages());
    }
}
```

### PageHelper插件

使⽤PageHelper的分⻚拦截器与自带的分页插件，⼆者冲突，推荐后者PageHelper进行分页

**导入依赖**：

```xml [pom.xml]
<dependency>
	<groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper</artifactId>
    <version>6.1.0</version>
</dependency>
```

**配置插件功能**：

```java
@Configuration
//扫描mapper接口所在的包
@MapperScan("com.hjc.demo.mapper")
public class PluginConfig {

    //配置pageHelper
    @Bean
    public PageInterceptor pageInterceptor(){
        return new PageInterceptor();
    }
}
```

**测试**：

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testPageHelper() {
        PageInfo<User> page = PageHelper.startPage(1,2).doSelectPageInfo(()->{
            userMapper.selectList(null);
        });
        page.getList().forEach(System.out :: println);
        System.out.println("总行数=" + page.getTotal());
        System.out.println("当前页=" + page.getPageNum());
        System.out.println("每页行数=" + page.getPageSize());
        System.out.println("总页数=" + page.getPages());
        System.out.println("起始行数=" + page.getStartRow());
        System.out.println("是第一页=" + page.isIsFirstPage());
        System.out.println("是最后页=" + page.isIsLastPage());
        System.out.println("还有下一页=" + page.isHasNextPage());
        System.out.println("还有上一页=" + page.isHasPreviousPage());
        System.out.println("页码列表=" + Arrays.toString(page.getNavigatepageNums()));
    }
}
```

## 乐观锁

**场景**：

一件商品，成本价是80元，售价是100元。老板先是通知小李，说你去把商品价格增加50元。小 李正在玩游戏，耽搁了一个小时。正好一个小时后，老板觉得商品价格增加到150元，价格太 高，可能会影响销量。又通知小王，你把商品价格降低30元。 此时，小李和小王同时操作商品后台系统。小李操作的时候，系统先取出商品价格100元；小王 也在操作，取出的商品价格也是100元。小李将价格加了50元，并将100+50=150元存入了数据 库；小王将商品减了30元，并将100-30=70元存入了数据库。是的，如果没有锁，小李的操作就 完全被小王的覆盖了。 现在商品价格是70元，比成本价低10元。几分钟后，这个商品很快出售了1千多件商品，老板亏1 万多。

**乐观锁与悲观锁**：

如果是乐观锁，小王保存价格前，会检查下价格是否被人修改过了。如果被修改过 了，则重新取出的被修改后的价格，150元，这样他会将120元存入数据库。

如果是悲观锁，小李取出数据后，小王只能等小李操作完之后，才能对价格进行操作，也会保证最终的价格是120元。

乐观锁和悲观锁是在并发编程中用于处理并发访问和资源竞争的两种不同的锁机制!!

**悲观锁**：

- 悲观锁的基本思想是：在整个数据访问过程中，将共享资源锁定，以确保其他线程或进程不能同时访问和修改该资源。悲观锁的核心思想是"先保护，再修改"。在悲观锁的应用中，线程在访问共享资源之前会获取到锁，并在整个操作过程中保持锁的状态，阻塞其他线程的访问。只有当前线程完成操作后，才会释放锁，让其他线程继续操作资源。这种锁机制可以确保资源独占性和数据的一致性，但是在高并发环境下，悲观锁的效率相对较低。

**乐观锁**：

- 乐观锁的基本思想是：认为并发冲突的概率较低，因此不需要提前加锁，而是在数据更新阶段进行冲突检测和处理。乐观锁的核心思想是"先修改，后校验"。在乐观锁的应用中，线程在读取共享资源时不会加锁，而是记录特定的版本信息。当线程准备更新资源时，会先检查该资源的版本信息是否与之前读取的版本信息一致，如果一致则执行更新操作，否则说明有其他线程修改了该资源，需要进行相应的冲突处理。乐观锁通过避免加锁操作，提高了系统的并发性能和吞吐量，但是在并发冲突较为频繁的情况下，乐观锁会导致较多的冲突处理和重试操作。

**具体技术和方案:**

1.  乐观锁实现方案和技术：
    - 版本号/时间戳：为数据添加一个版本号或时间戳字段，每次更新数据时，比较当前版本号或时间戳与期望值是否一致，若一致则更新成功，否则表示数据已被修改，需要进行冲突处理。
    - CAS（Compare-and-Swap）：使用原子操作比较当前值与旧值是否一致，若一致则进行更新操作，否则重新尝试。
    - 无锁数据结构：采用无锁数据结构，如无锁队列、无锁哈希表等，通过使用原子操作实现并发安全。
2.  悲观锁实现方案和技术：
    - 锁机制：使用传统的锁机制，如互斥锁（Mutex Lock）或读写锁（Read-Write Lock）来保证对共享资源的独占访问。
    - 数据库锁：在数据库层面使用行级锁或表级锁来控制并发访问。
    - 信号量（Semaphore）：使用信号量来限制对资源的并发访问。

**乐观锁实现流程**：

数据库中添加version字段：

- 取出记录时，获取当前version：

  ```sql
  SELECT id,`name`,price,`version` FROM product WHERE id=1
  ```

- 更新时，version+1，如果where语句中的version版本不对，则更新失败

  ```sql
  UPDATE product SET price=price+50, `version`=`version` + 1 WHERE id=1 AND
  `version`=1
  ```

### 修改冲突

**数据库中添加商品表**：

```sql
CREATE TABLE t_product
(
	id BIGINT(20) NOT NULL COMMENT '主键ID',
	NAME VARCHAR(30) NULL DEFAULT NULL COMMENT '商品名称',
	price INT(11) DEFAULT 0 COMMENT '价格',
	version INT(11) DEFAULT 0 COMMENT '乐观锁版本号',
	PRIMARY KEY (id)
);
```

**添加数据**：

```sql
INSERT INTO t_product (id, NAME, price) VALUES (1, '外星人笔记本', 100);
```

**添加实体类**：

```java [Product.java]
@Data
public class Product {
    private Long id;
    private String name;
    private Integer price;
    private Integer version;
}
```

**添加mapper**：

```java
public interface ProductMapper extends BaseMapper<Product> {
}
```

**测试**：

```java
@SpringBootTest
class ProductMapperTest {
    @Autowired
    private ProductMapper productMapper;

    @Test
    void test1() {
        //1、小李
        Product p1 = productMapper.selectById(1L);
        System.out.println("小李取出的价格：" + p1.getPrice());
        //2、小王
        Product p2 = productMapper.selectById(1L);
        System.out.println("小王取出的价格：" + p2.getPrice());
        //3、小李将价格加了50元，存入了数据库
        p1.setPrice(p1.getPrice() + 50);
        int result1 = productMapper.updateById(p1);
        System.out.println("小李修改结果：" + result1);
        //4、小王将商品减了30元，存入了数据库
        p2.setPrice(p2.getPrice() - 30);
        int result2 = productMapper.updateById(p2);
        System.out.println("小王修改结果：" + result2);
        //最后的结果
        Product p3 = productMapper.selectById(1L);
        //价格覆盖，最后的结果：70
        System.out.println("最后的结果：" + p3.getPrice());
    }
}
```

### 使用乐观锁

![image-20230226104932989](assets/202302261314410.png)

**修改实体类**：

```java
@Data
public class Product {
    private Long id;
    private String name;
    private Integer price;
    @Version
    private Integer version;
}
```

- 支持的数据类型只有：int，Integer，long，Long，Date，Timestamp，LocalDateTime
- 仅支持 `updateById(id)` 与 `update(entity, wrapper)` 方法

**添加乐观锁插件**：

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor(){
	MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
	//添加分页插件
	interceptor.addInnerInterceptor(new
	PaginationInnerInterceptor(DbType.MYSQL));
	//添加乐观锁插件
	interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
	return interceptor;
}
```

**测试**：

```java
@SpringBootTest
class ProductMapperTest {
    @Autowired
    private ProductMapper productMapper;

    @Test
    void test2() {
        //小李取数据
        Product p1 = productMapper.selectById(1L);
        //小王取数据
        Product p2 = productMapper.selectById(1L);
        //小李修改 + 50
        p1.setPrice(p1.getPrice() + 50);
        int result1 = productMapper.updateById(p1);
        System.out.println("小李修改的结果：" + result1);
        //小王修改 - 30
        p2.setPrice(p2.getPrice() - 30);
        int result2 = productMapper.updateById(p2);
        System.out.println("小王修改的结果：" + result2);

        if (result2 == 0) {
            //失败重试，重新获取version并更新
            p2 = productMapper.selectById(1L);
            p2.setPrice(p2.getPrice() - 30);
            result2 = productMapper.updateById(p2);
        }
        System.out.println("小王修改重试的结果：" + result2);
        //老板看价格
        Product p3 = productMapper.selectById(1L);
        System.out.println("老板看价格：" + p3.getPrice());
    }
}
```

## 防全表更新和删除实现

针对 update 和 delete 语句

作用：阻止恶意的全表更新删除

添加防止全表更新和删除拦截器

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
  MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
  interceptor.addInnerInterceptor(new BlockAttackInnerInterceptor());
  return interceptor;
}
```

测试全部更新或者删除

```java
@Test
public void testQuick8(){
    User user = new User();
    user.setName("custom_name");
    user.setEmail("xxx@mail.com");
    //Caused by: com.baomidou.mybatisplus.core.exceptions.MybatisPlusException: Prohibition of table update operation
    //全局更新,报错
    userService.saveOrUpdate(user,null);
}
```

![image-20240116234102697](assets/img202401162341354.png)
