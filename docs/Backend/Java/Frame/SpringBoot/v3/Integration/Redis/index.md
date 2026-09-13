# SpringBoot 整合 Redis

## 自动配置原理

**自动配置原理**：

1. `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`中导入了RedisAutoConfiguration、RedisReactiveAutoConfiguration和RedisRepositoriesAutoConfiguration。所有属性绑定在RedisProperties中
2. RedisReactiveAutoConfiguration属于响应式编程，不用管。RedisRepositoriesAutoConfiguration属于 JPA 操作，也不用管
3. RedisAutoConfiguration 配置了以下组件：
   1. LettuceConnectionConfiguration： 给容器中注入了连接工厂LettuceConnectionFactory，和操作 redis 的客户端DefaultClientResources。
   2. RedisTemplate<Object, Object>： 可给 redis 中存储任意对象，会使用 jdk 默认序列化方式。
   3. StringRedisTemplate： 给 redis 中存储字符串，如果要存对象，需要开发人员自己进行序列化。key-value都是字符串进行操作

**操作分析**：

- [选场景](https://docs.spring.io/spring-boot/docs/current/reference/html/using.html#using.build-systems.starters)：`spring-boot-starter-data-redis `
  - 场景AutoConfiguration 就是这个场景的自动配置类

- 写配置：
  - 分析到这个场景的自动配置类开启了哪些属性绑定关系
  - `@EnableConfigurationProperties(RedisProperties.class)`
  - 修改redis相关的配置

- 分析组件：
  - 分析到 `RedisAutoConfiguration`  给容器中放了 `StringRedisTemplate`
  - 给业务代码中自动装配 `StringRedisTemplate`

- 定制化：
  - 修改配置文件
  - 自定义组件，自己给容器中放一个 `StringRedisTemplate`

## 场景整合

添加依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

配置Redis：

```properties
spring.data.redis.host=192.168.200.100
spring.data.redis.password=123123
```

测试：

```java
@Autowired
StringRedisTemplate redisTemplate;

@Test
void redisTest(){
    redisTemplate.opsForValue().set("a","1234");
    Assertions.assertEquals("1234",redisTemplate.opsForValue().get("a"));
}
```

## 定制化 

### 序列化机制 

```java
@Configuration
public class AppRedisConfiguration {


    /**
     * 允许Object类型的key-value，都可以被转为json进行存储。
     * @param redisConnectionFactory 自动配置好了连接工厂
     * @return
     */
    @Bean
    public RedisTemplate<Object, Object> redisTemplate(RedisConnectionFactory redisConnectionFactory) {
        RedisTemplate<Object, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory);
        //把对象转为json字符串的序列化工具
        template.setDefaultSerializer(new GenericJackson2JsonRedisSerializer());
        return template;
    }
}
```

### Redis客户端 

RedisTemplate、StringRedisTemplate： 操作redis的工具类

要从redis的连接工厂获取链接才能操作redis

Redis客户端：

- Lettuce(默认) 
- Jedis

**切换为Jedis**：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
    <exclusions>
		<exclusion>
            <groupId>io.lettuce</groupId>
        	<artifactId>lettuce-core</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<!-- 切换 jedis 作为操作redis的底层客户端-->
<dependency>
    <groupId>redis.clients</groupId>
	<artifactId>jedis</artifactId>
</dependency>
```

```properties
spring.data.redis.host=8.130.74.183
spring.data.redis.port=6379
#spring.data.redis.client-type=lettuce

#设置lettuce的底层参数
#spring.data.redis.lettuce.pool.enabled=true
#spring.data.redis.lettuce.pool.max-active=8

spring.data.redis.client-type=jedis
spring.data.redis.jedis.pool.enabled=true
spring.data.redis.jedis.pool.max-active=8
```

## 连接池与超时配置

生产环境必须显式配置连接池与超时，否则 Redis 抖动会直接拖垮应用线程池。

```properties [src/main/resources/application.yml]
spring:
  data:
    redis:
      timeout: 2000ms                 # 命令超时（含网络往返）
      lettuce:
        pool:
          enabled: true
          max-active: 16              # 最大连接数
          max-idle: 8
          min-idle: 2                 # 保持最小空闲，减少冷启动抖动
          max-wait: 2000ms            # 取连接超时，避免无限等待
        shutdown-timeout: 200ms
```

::: danger 注意
1. `timeout` 一定要设置：默认无限等待时，Redis 卡住会让 Tomcat 线程全部耗尽。
2. `max-active` 不要盲目调大。按「单实例 QPS × 单次命令耗时」估算，一般从 8~32 起调；池过大反而增加上下文切换。
3. 池满时的行为要明确：`max-wait` 设有限值，配合业务降级，而不是无限排队。
:::

## 接入哨兵与集群

单机配置在做了高可用后会失效，需要按部署形态调整。

### 哨兵模式

```properties [src/main/resources/application.yml]
spring:
  data:
    redis:
      password: strong-pass
      timeout: 2000ms
      sentinel:
        master: mymaster
        nodes:
          - 10.0.0.1:26379
          - 10.0.0.2:26379
          - 10.0.0.3:26379
      lettuce:
        pool:
          max-active: 16
          max-idle: 8
          min-idle: 2
```

::: warning
使用 Redisson 做分布式锁时，**必须单独把 Redisson 也配上哨兵**（`useSentinelServers()`）。只配 Spring Data Redis 而让 Redisson 连单机地址，切换后会出现「锁写到旧主库」的互斥失效问题。
:::

### 集群模式

```properties [src/main/resources/application.yml]
spring:
  data:
    redis:
      password: strong-pass
      cluster:
        nodes:
          - 10.0.0.1:7001
          - 10.0.0.1:7002
          - 10.0.0.1:7003
        max-redirects: 3
      lettuce:
        cluster:
          refresh:
            adaptive: true           # 自适应拓扑刷新，故障转移后自动更新槽映射
            period: 30s
```

::: danger 注意
1. Cluster 模式下**多 key 命令要求 key 在同一槽**，否则报 `CROSSSLOT`；用 hash tag 解决（如 `user:{1001}:name`）。
2. Cluster 只有 **db 0**，`SELECT` 不可用，不要沿用单机的多库设计。
3. 必须使用支持 Cluster 的客户端（Spring Data Redis 的 Lettuce 默认支持），不要用单机模式客户端连接。
:::

## 序列化与 Key 可读性

| 模板 | 序列化方式 | Key 可读性 | 适用 |
| --- | --- | --- | --- |
| `StringRedisTemplate` | String | 好 | **推荐**：业务代码自行 JSON 序列化 |
| `RedisTemplate<Object, Object>`（默认） | JDK 序列化 | 差（二进制乱码） | 不建议直接用于新项目 |
| 自定义 `RedisTemplate` + `GenericJackson2JsonRedisSerializer` | JSON | 好 | 需要直接存取对象时 |

```java [推荐写法：StringRedisTemplate + JSON]
@Autowired
private StringRedisTemplate redis;

public void saveUser(User user) {
    redis.opsForValue().set("user:" + user.getId(), JSON.toJSONString(user), Duration.ofMinutes(30));
}

public User getUser(long id) {
    String json = redis.opsForValue().get("user:" + id);
    return json == null ? null : JSON.parseObject(json, User.class);
}
```

::: tip
用 JDK 序列化时，Key 会变成带二进制前缀的乱码，`redis-cli` 与 RedisInsight 里几乎没法排查。新项目统一用 `StringRedisTemplate` + JSON（或二进制 Protobuf）最省心。
:::

## 相关专题

- [Redis 进阶导览](../../../../../../DB/NoRelational/Redis/Advanced/index.md)：复制、哨兵、Cluster、缓存设计与性能调优
- [缓存设计](../../../../../../DB/NoRelational/Redis/Advanced/CacheDesign/index.md)：Cache Aside、TTL 抖动、多级缓存
- [缓存防护](../../../../../../DB/NoRelational/Redis/Advanced/CacheProtection/index.md)：穿透/击穿/雪崩与热点 key
- [分布式锁与 Lua](../../../../../../DB/NoRelational/Redis/Advanced/DistributedLock/index.md)：Redisson 可重入锁与看门狗
- [实战：高可用缓存集群](../../../../../../DB/NoRelational/Redis/Advanced/Practice/index.md)：一主二从三哨兵 + Spring Boot 完整落地
- [SpringBoot 整合 Sa-Token](../../../../Sa-token/index.md)：登录态存储常与 Redis 配合使用


