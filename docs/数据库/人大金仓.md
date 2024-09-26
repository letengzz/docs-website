## MySQL迁移至KingBase

[人大金仓文档](https://help.kingbase.com.cn/v8/index.html)

数据迁移工具：KDTS

数据库客户端：KStudio For KES

### 迁移工具KDTS启动

[文档](https://help.kingbase.com.cn/v8/development/develop-transfer/kdts-plus/index.html)

### KDTS使用

[4. BS 版使用说明 — KingbaseES产品手册](https://help.kingbase.com.cn/v8/development/develop-transfer/kdts-plus/kdts-plus-3.html)

### 常见兼容问题

> [常见问题手册](https://help.kingbase.com.cn/v8/faq/faq-new/index.html)

> 严格的group by语法

解决方法：设置sql-mode,让其不包含ONLY_FULL_GROUP_BY

```sql
show sql_mode
alter system set sql_mode=ANSI_QUOTES
select sys_reload_conf()
```







### SpringBoot+MyBatis+KingBase

> 官网文档：[KingbaseES客户端编程开发框架-MyBatis — KingbaseES产品手册](https://help.kingbase.com.cn/v8/development/client-interfaces-frame/mybatis/index.html)

> POM

```xml
<!-- 数据库相关 -->
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>1.3.2</version>
</dependency>
<dependency>
    <groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper-spring-boot-starter</artifactId>
    <version>1.2.4</version>
</dependency>

<!--人大金仓 驱动 -->
<dependency>
    <groupId>cn.com.kingbase</groupId>
    <artifactId>kingbase8</artifactId>
    <version>8.6.0</version>
    <scope>system</scope>
    <systemPath>${project.basedir}/lib/kingbase8-8.6.0.jar</systemPath>
</dependency>


打包插件：
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <includeSystemScope>true</includeSystemScope>
    </configuration>
</plugin>
```

> yml
>
> 注意事项：
>
> 正常访问表需要使用 schema.table
>
> 想要只通过表明访问需要 使用与模式同名用户，且模式拥有者为同名用户
>
> 创建用户dsjoa：`create user dsjoa with SUPERUSER CREATEDB CREATEROLE LOGIN REPLICATION ENCRYPTED PASSWORD 'abcd1234';`
>
> 创建模式dsjoa，拥有者为dsjoa：`CREATE SCHEMA dsjoa AUTHORIZATION dsjoa;`

```yaml
spring:
  datasource:
    driver-class-name: com.kingbase8.Driver
    url: jdbc:kingbase8://127.0.0.1:54321/test
    username: dsjoa
    password: abcd1234
```

```yaml
# 使用自定义dialect   因为KingBase选择mysql模式，也可以将kingbase替换为mysql
pagehelper:
  helper-dialect: kingbase
```

> 自定义Dialect

```java
@Component
public class KingBaseDialect extends AbstractHelperDialect {

    static {
        PageAutoDialect.registerDialectAlias("kingbase", KingBaseDialect.class);
    }

    @Override
    public Object processPageParameter(MappedStatement ms, Map<String, Object> paramMap, Page page, BoundSql boundSql,
                                       CacheKey pageKey) {
        //第一个值 是偏移量
        paramMap.put(PAGEPARAMETER_FIRST, page.getStartRow());
        // 第二个值 是返回的最大行数
        paramMap.put(PAGEPARAMETER_SECOND, page.getPageSize());
        //处理pageKey
        pageKey.update(page.getStartRow());
        pageKey.update(page.getPageSize());
        //处理参数配置
        if (boundSql.getParameterMappings() != null) {
            List<ParameterMapping> newParameterMappings = new ArrayList<ParameterMapping>();
            if (boundSql != null && boundSql.getParameterMappings() != null) {
                newParameterMappings.addAll(boundSql.getParameterMappings());
            }
            if (page.getStartRow() == 0) {
                newParameterMappings.add(new ParameterMapping.Builder(ms.getConfiguration(), PAGEPARAMETER_SECOND, Integer.class).build());
            } else {
                newParameterMappings.add(new ParameterMapping.Builder(ms.getConfiguration(), PAGEPARAMETER_SECOND, Integer.class).build());
                newParameterMappings.add(new ParameterMapping.Builder(ms.getConfiguration(), PAGEPARAMETER_FIRST, Integer.class).build());
            }
            MetaObject metaObject = MetaObjectUtil.forObject(boundSql);
            metaObject.setValue("parameterMappings", newParameterMappings);
        }
        return paramMap;
    }

    @Override
    public String getPageSql(String sql, Page page, CacheKey pageKey) {
        StringBuilder sqlBuilder = new StringBuilder(sql.length() + 20);
        sqlBuilder.append(sql);
        if (page.getStartRow() == 0) {
            sqlBuilder.append(" LIMIT ? ");
        } else {
            sqlBuilder.append(" LIMIT ? OFFSET ? ");
        }
        pageKey.update(page.getPageSize());
        return sqlBuilder.toString();
    }
}
```

### SpringBoot+MyBatisPlus+KingBase

> 官网文档：[KingbaseES客户端编程开发框架-MyBatis-Plus — KingbaseES产品手册](https://help.kingbase.com.cn/v8/development/client-interfaces-frame/mybatis-plus/index.html)

> POM

```xml
<!--人大金仓 驱动 -->
<dependency>
    <groupId>cn.com.kingbase</groupId>
    <artifactId>kingbase8</artifactId>
    <version>8.6.0</version>
    <scope>system</scope>
    <systemPath>${project.basedir}/lib/kingbase8-8.6.0.jar</systemPath>
</dependency>
<!--SpringBoot3使用 -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.7</version>
</dependency>
```

> 配置

```yml
spring:
  datasource:
    driver-class-name: com.kingbase8.Driver
    url: jdbc:kingbase8://localhost:54321/test
    username: wlpnz
    password: wlpnz

mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml # 默认值
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl # 查看日志
    map-underscore-to-camel-case: true # 默认值
```

> 分页插件配置

```java
/**
* 添加分页插件
*/
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
     // 如果配置多个插件, 切记分页最后添加
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.KINGBASE_ES));
    return interceptor;
}
```

