### 使用Jedis
导入maven依赖
```
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>4.3.1</version>
</dependency>
```
使用
```java
Jedis jedis = new Jedis("192.168.10.201", 6301);
jedis.auth("abc123");

log.info("redis conn status:{}","连接成功");
log.info("redis ping retvalue:{}",jedis.ping());

jedis.set("k1","jedis");
log.info("k1 value:{}",jedis.get("k1"));
/**
 * 12:56:01.236 [main] INFO top.wlpnz.redis.jedis.JedisDemo - redis conn status:连接成功
 * 12:56:01.239 [main] INFO top.wlpnz.redis.jedis.JedisDemo - redis ping retvalue:PONG
 * 12:56:01.252 [main] INFO top.wlpnz.redis.jedis.JedisDemo - k1 value:jedis
 */
```
### 使用lettuce
导入pom依赖
```java
<!--lettuce-->
<dependency>
    <groupId>io.lettuce</groupId>
    <artifactId>lettuce-core</artifactId>
    <version>6.2.1.RELEASE</version>
</dependency>
```
使用
```java
//使用构建器 RedisURI.builder
RedisURI uri = RedisURI.builder()
        .redis("192.168.10.201")
        .withPort(6301)
        .withAuthentication("default","abc123")
        .build();
//创建连接客户端
RedisClient client = RedisClient.create(uri);
StatefulRedisConnection conn = client.connect();
//操作命令api
RedisCommands<String,String> commands = conn.sync();

//keys
List<String> list = commands.keys("*");
for(String s : list) {
    log.info("key:{}",s);
}
//String
commands.set("k1","1111");
String s1 = commands.get("k1");
System.out.println("String s ==="+s1);

//list
commands.lpush("myList2", "v1","v2","v3");
List<String> list2 = commands.lrange("myList2", 0, -1);
for(String s : list2) {
    System.out.println("list ssss==="+s);
}
//set
commands.sadd("mySet2", "v1","v2","v3");
Set<String> set = commands.smembers("mySet2");
for(String s : set) {
    System.out.println("set ssss==="+s);
}
//hash
Map<String,String> map = new HashMap<>();
map.put("k1","138xxxxxxxx");
map.put("k2","atguigu");
map.put("k3","zzyybs@126.com");//课后有问题请给我发邮件

commands.hmset("myHash2", map);
Map<String,String> retMap = commands.hgetall("myHash2");
for(String k : retMap.keySet()) {
    System.out.println("hash  k="+k+" , v=="+retMap.get(k));
}

//zset
commands.zadd("myZset2", 100.0,"s1",110.0,"s2",90.0,"s3");
List<String> list3 = commands.zrange("myZset2",0,10);
for(String s : list3) {
    System.out.println("zset ssss==="+s);
}

//sort
SortArgs sortArgs = new SortArgs();
sortArgs.alpha();
sortArgs.desc();

List<String> list4 = commands.sort("myList2",sortArgs);
for(String s : list4) {
    System.out.println("sort ssss==="+s);
}

//关闭
conn.close();
client.shutdown();
```
### 使用RedisTemplate
#### Redis单机
导入Mave依赖
```java
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-pool2</artifactId>
</dependency>
```
配置yml
```java
spring:
  redis:
    database: 0
    host: 192.168.10.201
    port: 6301
    password: abc123
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        max-wait: -1ms
        min-idle: 0
```
配置序列化
```java
@Bean
@SuppressWarnings("all")
public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory redisConnectionFactory)
{
    RedisTemplate<String,Object> redisTemplate = new RedisTemplate<>();
    redisTemplate.setConnectionFactory(redisConnectionFactory);
    //设置key序列化方式string
    redisTemplate.setKeySerializer(new StringRedisSerializer());
    //设置value的序列化方式json，使用GenericJackson2JsonRedisSerializer替换默认序列化
    redisTemplate.setValueSerializer(new GenericJackson2JsonRedisSerializer());
    redisTemplate.setHashKeySerializer(new StringRedisSerializer());
    redisTemplate.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
    redisTemplate.afterPropertiesSet();
    return redisTemplate;
}
```
使用
```java
public class OrderService
{
    public static final String ORDER_KEY = "order:";

    @Resource
    private RedisTemplate redisTemplate;

    public void addOrder()
    {
        int keyId = ThreadLocalRandom.current().nextInt(1000)+1;
        String orderNo = UUID.randomUUID().toString();
        redisTemplate.opsForValue().set(ORDER_KEY+keyId,"京东订单"+ orderNo);
        log.info("=====>编号"+keyId+"的订单流水生成:{}",orderNo);
    }

    public String getOrderById(Integer id)
    {
        return (String)redisTemplate.opsForValue().get(ORDER_KEY + id);
    }
}
```
#### Redis集群
修改yml配置
```java
  redis:
    cluster:
      max-redirects: 3
      nodes:
        - 192.168.10.201:6381
        - 192.168.10.201:6382
        - 192.168.10.202:6383
        - 192.168.10.202:6384
        - 192.168.10.203:6385
        - 192.168.10.203:6386
    password: 111111
    lettuce:
      cluster:
        refresh:
          adaptive: true
          period: 2000
      pool:
        max-active: 8
        max-idle: 8
        max-wait: -1ms
        min-idle: 0
```
