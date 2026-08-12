# MyBatis-Plus基本操作

## 基本功能

MyBatis-Plus中的基本CRUD在内置的BaseMapper中都已得到了实现：

```java
/**
 * Mapper 继承该接口后，无需编写 mapper.xml 文件，即可获得CRUD功能
 * <p>这个 Mapper 支持 id 泛型</p>
 */
public interface BaseMapper<T> extends Mapper<T> {

    /**
     * 插入一条记录
     *
     * @param entity 实体对象
     */
    int insert(T entity);

    /**
     * 根据 ID 删除
     *
     * @param id 主键ID
     */
    int deleteById(Serializable id);

    /**
     * 根据实体(ID)删除
     *
     * @param entity 实体对象
     * @since 3.4.4
     */
    int deleteById(T entity);

    /**
     * 根据 columnMap 条件，删除记录
     *
     * @param columnMap 表字段 map 对象
     */
    int deleteByMap(@Param(Constants.COLUMN_MAP) Map<String, Object> columnMap);

    /**
     * 根据 entity 条件，删除记录
     *
     * @param queryWrapper 实体对象封装操作类（可以为 null,里面的 entity 用于生成 where 语句）
     */
    int delete(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

    /**
     * 删除（根据ID或实体 批量删除）
     *
     * @param idList 主键ID列表或实体列表(不能为 null 以及 empty)
     */
    int deleteBatchIds(@Param(Constants.COLL) Collection<?> idList);

    /**
     * 根据 ID 修改
     *
     * @param entity 实体对象
     */
    int updateById(@Param(Constants.ENTITY) T entity);

    /**
     * 根据 whereEntity 条件，更新记录
     *
     * @param entity        实体对象 (set 条件值,可以为 null)
     * @param updateWrapper 实体对象封装操作类（可以为 null,里面的 entity 用于生成 where 语句）
     */
    int update(@Param(Constants.ENTITY) T entity, @Param(Constants.WRAPPER) Wrapper<T> updateWrapper);

    /**
     * 根据 ID 查询
     *
     * @param id 主键ID
     */
    T selectById(Serializable id);

    /**
     * 查询（根据ID 批量查询）
     *
     * @param idList 主键ID列表(不能为 null 以及 empty)
     */
    List<T> selectBatchIds(@Param(Constants.COLL) Collection<? extends Serializable> idList);

    /**
     * 查询（根据 columnMap 条件）
     *
     * @param columnMap 表字段 map 对象
     */
    List<T> selectByMap(@Param(Constants.COLUMN_MAP) Map<String, Object> columnMap);

    /**
     * 根据 entity 条件，查询一条记录
     * <p>查询一条记录，例如 qw.last("limit 1") 限制取一条记录, 注意：多条数据会报异常</p>
     *
     * @param queryWrapper 实体对象封装操作类（可以为 null）
     */
    default T selectOne(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper) {
        List<T> ts = this.selectList(queryWrapper);
        if (CollectionUtils.isNotEmpty(ts)) {
            if (ts.size() != 1) {
                throw ExceptionUtils.mpe("One record is expected, but the query result is multiple records");
            }
            return ts.get(0);
        }
        return null;
    }

    /**
     * 根据 Wrapper 条件，判断是否存在记录
     *
     * @param queryWrapper 实体对象封装操作类
     * @return 是否存在记录
     */
    default boolean exists(Wrapper<T> queryWrapper) {
        Long count = this.selectCount(queryWrapper);
        return null != count && count > 0;
    }

    /**
     * 根据 Wrapper 条件，查询总记录数
     *
     * @param queryWrapper 实体对象封装操作类（可以为 null）
     */
    Long selectCount(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

    /**
     * 根据 entity 条件，查询全部记录
     *
     * @param queryWrapper 实体对象封装操作类（可以为 null）
     */
    List<T> selectList(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

    /**
     * 根据 Wrapper 条件，查询全部记录
     *
     * @param queryWrapper 实体对象封装操作类（可以为 null）
     */
    List<Map<String, Object>> selectMaps(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

    /**
     * 根据 Wrapper 条件，查询全部记录
     * <p>注意： 只返回第一个字段的值</p>
     *
     * @param queryWrapper 实体对象封装操作类（可以为 null）
     */
    List<Object> selectObjs(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

    /**
     * 根据 entity 条件，查询全部记录（并翻页）
     *
     * @param page         分页查询条件（可以为 RowBounds.DEFAULT）
     * @param queryWrapper 实体对象封装操作类（可以为 null）
     */
    <P extends IPage<T>> P selectPage(P page, @Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

    /**
     * 根据 Wrapper 条件，查询全部记录（并翻页）
     *
     * @param page         分页查询条件
     * @param queryWrapper 实体对象封装操作类
     */
    <P extends IPage<Map<String, Object>>> P selectMapsPage(P page, @Param(Constants.WRAPPER) Wrapper<T> queryWrapper);
}
```

### 新增功能

MyBatis-Plus在实现插入数据时，会默认基于雪花算法的策略生成id：

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testInsert() {
        User user = new User();
        user.setName("张三");
        user.setAge(23);
        user.setEmail( "zhangsan@qq.com");
        //INSERT INTO user ( id, name, age, email ) VALUES ( ?, ?, ?, ? )
        int result = userMapper.insert(user);
        System.out.println("受影响行数："+result);
        //id自动获取：1629070359040888833
        System.out.println("id自动获取："+user.getId());
    }
}
```

### 删除功能

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testDelete() {
        //通过id删除用户信息
        int result = userMapper.deleteById(1L);
        System.out.println("删除id为1的用户: " + result);

        //根据map集合中所设置的条件删除用户信息
        HashMap<String, Object> map = new HashMap<>();
        map.put("name","张三");
        map.put("age",23);
        int result2 = userMapper.deleteByMap(map);
        System.out.println("删除名字为张三,age为23岁的用户: " + result2);
    }
}
```

### 修改功能

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testUpdate() {
       User user = userMapper.selectById(2L);
       user.setAge(45);
       //根据id修改信息
       int result = userMapper.updateById(user);
       System.out.println("根据id修改信息: " + result);
    }
}
```

### 查询功能

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testSelect() {
        //根据id查询用户
        User user = userMapper.selectById(5L);
        System.out.println("根据id查询用户: " + user);

        //根据map集合中的条件查询用户信息
        HashMap<String, Object> map = new HashMap<>();
        map.put("name","张三");
        map.put("age",23);
        userMapper.selectByMap(map).forEach(u -> System.out.println("根据map集合中的条件查询用户信息: " + u));
    }
}
```

### 自定义功能

mybatis-plus的默认mapperxml位置：

```yaml [application.yaml]
mybatis-plus: # mybatis-plus的配置
  # 默认位置 private String[] mapperLocations = new String[]{"classpath*:/mapper/**/*.xml"};
  mapper-locations: classpath:/mapper/*.xml
```

```java [UserMapper.java]
/**
 * mapper接口继承BaseMapper 包含了基本的CRUD操作
 * IDEA在 userMapper 处报错，因为找不到注入的对象，因为类是动态创建的，但是程序可以正确的执行。
 * 为了避免报错，可以在mapper接口上添加 @Repository 注解
 * @author hjc
 */
@Repository
public interface UserMapper extends BaseMapper<User> {
    /**
     * 根据id查询用户信息为map集合
     * @param id l
     * @return l
     */
    @MapKey("id")
    Map<String,Object> selectMapById(Long id);
}
```

```xml [resources/mapper/UserMapper.xml]
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.hjc.demo.mapper.UserMapper">

    <select id="selectMapById" resultType="java.util.Map">
        select * from user where  id =#{id}
    </select>
</mapper>
```

```java [UserMapperTest.java]
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testCustomer() {
        //测试自定义
        Map<String, Object> map = userMapper.selectMapById(2L);
        System.out.println("map = " + map);
    }
}
```

## 批量操作

### 批量删除

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testBatchDelete() {
        //通过多个id实现批量删除
        List<Long> list = Arrays.asList(2L, 3L);
        int result = userMapper.deleteBatchIds(list);
        System.out.println("删除id为2,3的用户: " + result);
    }
}
```

### 批量查询

```java
@SpringBootTest
class UserMapperTest {
    @Autowired
    private UserMapper userMapper;

    @Test
    void testBatchSelect() {
        //根据多个id查询多个用户信息
        List<Long> list = Arrays.asList(1L, 2L, 3L);
        userMapper.selectBatchIds(list).forEach(System.out::println);

        //通过条件构造器查询一个list集合，若没有条件，则可以设置null为参数
        //查询所有数据
        userMapper.selectList(null).forEach(System.out::println);
    }
}
```

## 通用Service

通用 Service CRUD 封装IService接口，进一步封装 CRUD。

采用：get 查询单行、remove 删除、list 查询集合、page 分页。前缀命名方式区分 Mapper 层避免混淆， 泛型 T 为任意实体对象。建议如果存在自定义通用 Service 方法的可能，请创建自己的 IBaseService 继承 Mybatis-Plus 提供的基类。

**对比Mapper接口CRUD区别**：

- service添加了批量方法
- service层的方法自动添加事务

官网地址：https://baomidou.com/pages/49cc81/#service-crud-%E6%8E%A5%E5%8F%A3

### IService

MyBatis-Plus中有一个接口 IService和其实现类 ServiceImpl，封装了常见的业务层逻辑。

![image-20230225150753143](assets/202302261313729.png)

![image-20230225150819726](assets/202302261313888.png)

### 创建Service接口和实现类

```java [service/UserService.java]
/**
 * UserService继承IService模板提供的基础功能
 * @author hjc
 */
public interface UserService extends IService<User> {
}
```

```java [service/Imp/UserServiceImpl]
/**
 * ServiceImpl实现了IService，提供了IService中基础功能的实现
 * 若ServiceImpl无法满足业务需求，则可以使用自定的UserService定义方法，并在实现类中实现
 * @author hjc
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
}
```

### 测试插入

```java
@SpringBootTest
class UserServiceTest {
    @Autowired
    private UserService userService;
    @Test
    void testSave() {
        //插入一条数据
        User user = new User();
        user.setName("李贝");
        user.setEmail("2331@qq.com");
        user.setAge(15);
        boolean result = userService.save(user);
        System.out.println("插入一条信息: " + result);

        //批量插入数据
        ArrayList<User> users = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            User user1 = new User();
            user1.setName("测试" + i);
            user1.setAge(10 + i);
            user1.setEmail("test" + i + "@163.com");
            users.add(user1);
        }
        boolean saveBatch = userService.saveBatch(users);
        System.out.println("批量插入数据: " + saveBatch);

        //批量插入数据(按照插入批次数量)
        ArrayList<User> users1 = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            User user1 = new User();
            user1.setName("测试" + i);
            user1.setAge(10 + i);
            user1.setEmail("test" + i + "@163.com");
            users1.add(user1);
        }
        boolean saveBatch1 = userService.saveBatch(users1, 2);
        System.out.println("批量插入数据(按照插入批次数量): " + saveBatch1);

        //saveOrUpdateBatch既有修改功能又有修改功能
        //区分：看实体类有没有id 有id是修改 没有id是添加
        User user1 = new User();
        user1.setName("李贝");
        user1.setEmail("2331@qq.com");
        user1.setAge(15);
        boolean saveOrUpdate = userService.saveOrUpdate(user1);
        System.out.println(saveOrUpdate);

        //规则同上 执行批量添加或更改
        ArrayList<User> users2 = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            User user2 = new User();
            user2.setId(Long.getLong(UUID.randomUUID().toString()));
            user2.setName("测试" + i);
            user2.setAge(10 + i);
            user2.setEmail("test" + i + "@163.com");
            users2.add(user1);
        }
        boolean saveOrUpdateBatch = userService.saveOrUpdateBatch(users2);
        System.out.println(saveOrUpdateBatch);

        // 批量修改插入
        boolean saveOrUpdateBatch2 = userService.saveOrUpdateBatch(users2,2);
        System.out.println(saveOrUpdateBatch);
    }
}
```

### 测试删除

```java
@SpringBootTest
class UserServiceTest {
    @Autowired
    private UserService userService;

    @Test
    void testRemove() {
        //根据id删除
        User user = userService.getById(1L);
        userService.removeById(user);
        userService.removeById(2L);
        //是否启用填充(为true的情况,会将入参转换实体进行delete删除)
        userService.removeById(3L,true);

        //根据多个id删除
        userService.removeByIds(Arrays.asList(1L,2L));
        //是否填充(为true的情况,会将入参转换实体进行delete删除)
        userService.removeByIds(Arrays.asList(3L,4L),true);

        //批量删除
        userService.removeBatchByIds(Arrays.asList(3L,4L));
        //是否填充(为true的情况,会将入参转换实体进行delete删除)
        userService.removeBatchByIds(Arrays.asList(3L,4L),true);
        //批量删除(按照插入批次数量)
        userService.removeBatchByIds(Arrays.asList(3L,4L),1);
        //是否填充(为true的情况,会将入参转换实体进行delete删除)(按照插入批次数量)
        userService.removeBatchByIds(Arrays.asList(3L,4L),1,true);

        //使用map进行删除
        HashMap<String, Object> map = new HashMap<>();
        map.put("id",1);
        userService.removeByMap(map);
    }
}
```

### 测试修改

```java
@SpringBootTest
class UserServiceTest {
    @Autowired
    private UserService userService;

    @Test
    void testUpdate() {
        //根据id修改
        userService.updateById(new User(1L,"孙策",10,"222"));
        //批量修改
        ArrayList<User> list = new ArrayList<>();
        list.add(new User(2L,"孙策",12,"123"));
        list.add(new User(3L,"孙权",44,"456"));
        userService.updateBatchById(list);
        //批量插入数据(按照插入批次数量)
        userService.updateBatchById(list,2);
    }
}
```

### 测试查询

```java
@SpringBootTest
class UserServiceTest {
    @Autowired
    private UserService userService;

    @Test
    void testSelect() {
        //查询总记录数
        long count = userService.count();
        System.out.println("count = " + count);

        //查询所有数据
        userService.list().forEach(System.out::println);


        //查询所有数据 格式：List<Map<String, Object>>
        List<Map<String, Object>> maps = userService.listMaps();
        System.out.println(maps);

        //根据id批量查询
        userService.listByIds(Arrays.asList(2L,3L)).forEach(System.out::println);

        //查询所有主键id
        //说明：取出的数据并不包括对象所有的字段，最多只能返回一个字段
        userService.listObjs().forEach(System.out::println);

        //使用map查询数据
        HashMap<String, Object> map = new HashMap<>();
        map.put("name","李贝");
        userService.listByMap(map).forEach(System.out::println);

        //根据id查询数据
        User user = userService.getById(1L);
        System.out.println("user = " + user);

        //使用mapper 查询所有数据
        BaseMapper<User> baseMapper = userService.getBaseMapper();
        baseMapper.selectList(null).forEach(System.out::println);
    }
}
```
