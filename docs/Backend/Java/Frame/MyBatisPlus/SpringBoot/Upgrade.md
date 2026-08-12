# Mybatis升级成Mybatis-plus

## 引入Maven 依赖

注释掉原来的Mybatis依赖，否则可能会报错。引入 Mybatis-plus 的包：

```xml
 <!-- 注释掉原来的mybatis，否则可能会报错 -->
<!--        <dependency>-->
<!--            <groupId>org.mybatis.spring.boot</groupId>-->
<!--            <artifactId>mybatis-spring-boot-starter</artifactId>-->
<!--        </dependency>-->
<!-- 引入 mybatis-plus 的包 -->
<dependency>
	<groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-extension</artifactId>
    <version>3.4.1</version>
    <scope>compile</scope>
</dependency>
```

## 添加配置类

```java
@Configuration
//扫描的mapper文件夹地址
@MapperScan(basePackages = {"com.hjc.mapper"})
//开启注解事务管理
@EnableTransactionManagement
public class MybatisPlusConfig {
}
```

## 修改nacos或者配置文件中关于mybatis的配置

```yaml
# mybatis配置
# mybatis:  //将原先的mybatis注释掉，调整为 mybatis-plus 即可
mybatis-plus:
  type-aliases-package: com.hjc.pojo
  configuration:
    # 驼峰转换
    map-underscore-to-camel-case: true
    # 延迟加载
    lazy-loading-enabled: true
  mapper-locations: classpath:mapper/*.xml
```

由于Mybatis-plus是在Mybatis的基础上进行的封装，所以对其的兼容性做的很好，之前的代码最好就不要再动了，要对线上保持敬畏。如果后续需要新开发的接口和功能，可以采用Mybatis-plus进行开发了
