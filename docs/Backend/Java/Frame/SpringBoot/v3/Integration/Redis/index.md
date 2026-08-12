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

