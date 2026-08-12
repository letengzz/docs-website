# MyBatis-Plus多数据源

适用于多种场景：纯粹多库、 读写分离、 一主多从、 混合模式等。

场景说明： 创建两个库，分别为：mybatis_plus（以前的库不动）与mybatis_plus_1（新建），将 mybatis_plus库的product表移动到mybatis_plus_1库，这样每个库一张表，通过一个测试用例 分别获取用户数据与商品数据，如果获取到说明多库模拟成功。

**创建数据库及表**：

```sql
CREATE DATABASE `mybatis_plus_1` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
use `mybatis_plus_1`;
CREATE TABLE product
(
	id BIGINT(20) NOT NULL COMMENT '主键ID',
	name VARCHAR(30) NULL DEFAULT NULL COMMENT '商品名称',
	price INT(11) DEFAULT 0 COMMENT '价格',
	version INT(11) DEFAULT 0 COMMENT '乐观锁版本号',
	PRIMARY KEY (id)
);
```

**添加数据**：

```sql
INSERT INTO product (id, NAME, price) VALUES (1, '外星人笔记本', 100);
```

**删除mybatis_plus库product表**：

```sql
use mybatis_plus;
DROP TABLE IF EXISTS product;
```

## 引入依赖

```xml
<dependency>
	<groupId>com.baomidou</groupId>
	<artifactId>dynamic-datasource-spring-boot-starter</artifactId>
	<version>4.3.0</version>
</dependency>
```

## 配置多数据源

```yaml
spring:
  # 配置数据源信息
  datasource:
    dynamic:
      # 设置默认的数据源或者数据源组,默认值即为master
      primary: master
      # 严格匹配数据源,默认false.true未匹配到指定数据源时抛异常,false使用默认数据源
      strict: false
      datasource:
        master:
          url: jdbc:mysql://localhost:3306/mybatis_plus?characterEncoding=utf8&useSSL=false
          driver-class-name: com.mysql.cj.jdbc.Driver
          username: root
          password: 123123
        slave_1:
          url: jdbc:mysql://localhost:3306/mybatis_plus_1?characterEncoding=utf8&useSSL=false
          driver-class-name: com.mysql.cj.jdbc.Driver
          username: root
          password: 123123
# 配置MyBatis日志
mybatis-plus:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  # 配置类型别名所对应的包
  type-aliases-package: com.hjc.demo.pojo
```

## 创建Service

```java [ProductServiceImpl.java]
@DS("slave_1")
@Service
public class ProductServiceImpl extends ServiceImpl<ProductMapper,Product> implements ProductService {
}
```

```java [UserServiceImpl.java]
@DS("master")
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
}
```

## 测试

```java
@SpringBootTest
class ServiceImplTest {
    @Autowired
    private UserService userService;
    @Autowired
    private ProductService productService;

    @Test
    public void testDynamicDataSource(){
        System.out.println(userService.getById(1L));
        System.out.println(productService.getById(1L));
    }
}
```
