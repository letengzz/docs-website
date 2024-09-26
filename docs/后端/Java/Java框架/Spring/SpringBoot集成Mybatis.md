### SpringBoot2.x整合Mybatis
**依赖**：
```xml
<!-- MyBatis -->
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>2.3.0</version>
</dependency>
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <scope>runtime</scope>
</dependency>
```
**配置**：

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://127.0.0.1:3306/test?useUnicode=true&characterEncoding=UTF-8&useSSL=false&useTimezone=true&serverTimezone=Asia/Shanghai&allowMultiQueries=true&autoReconnect=true&allowPublicKeyRetrieval=true
    username: root
    password: abc123

mybatis:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: top.wulan.file.entity
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
    map-underscore-to-camel-case: true
```
**注意**：
> 如果没有使用@MapperScan的话需要在每个Mapper接口上添加@Mapper注解，让其注入容器

### SpringBoot2.x整合Mybatis-Plus

> 官网文档：[简介 | MyBatis-Plus (baomidou.com)](https://baomidou.com/introduce/)

**依赖**：

```xml
<!--mybatis Plus-->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.3.2</version>
</dependency>
```
**配置**：
```yaml
mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml # 默认值
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl # 查看日志
    map-underscore-to-camel-case: true # 默认值
  global-config:
    db-config:
      logic-delete-value: 1
      logic-not-delete-value: 0
      
      
@Configuration
@EnableTransactionManagement
@MapperScan(basePackages = {
        "com.example.edutrain.mapper"
})
public class MybatisConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        PaginationInnerInterceptor paginationInnerInterceptor = new PaginationInnerInterceptor(DbType.MYSQL);
        paginationInnerInterceptor.setOverflow(true); //当前页溢出 处理
        //添加分页插件
        interceptor.addInnerInterceptor(paginationInnerInterceptor);
        return interceptor;
    }
}
```
**注意**：
> 如果没有使用@MapperScan的话需要在每个Mapper接口上添加@Mapper注解，让其注入容器

**实例**:
```java
// UserMapper
public interface UserMapper extends BaseMapper<User> {}

// UserService
public interface UserService extends IService<User> {}

// UserServiceImpl
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {}

@Data
@TableName("tb_user")
public class User implements Serializable{
	private static final long serialVersionUID = 1L;
	@TableId(value = "id", type = IdType.AUTO)
    private Integer id;
    //...
}
```
### Spring Boot 3.2+整合Mybatis-plus
```java
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.5</version>
</dependency>
```
其他配置基本不变
