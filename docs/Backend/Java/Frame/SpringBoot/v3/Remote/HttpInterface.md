# HTTP Interface 

Spring 允许通过定义接口的方式，给任意位置发送 http 请求，实现远程调用，可以用来简化 HTTP 远程访问。需要webflux场景才可以

## 导入依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

## 定义接口

```java
public interface BingService {

    @GetExchange(url = "/search")
    String search(@RequestParam("q") String keyword);
}
```

## 创建代理&测试

```java
@SpringBootTest
class Boot05TaskApplicationTests {

    @Test
    void contextLoads() throws InterruptedException {
        //1、创建客户端
        WebClient client = WebClient.builder()
                .baseUrl("https://cn.bing.com")
                .codecs(clientCodecConfigurer -> {
                    clientCodecConfigurer
                            .defaultCodecs()
                            .maxInMemorySize(256*1024*1024);
                            //响应数据量太大有可能会超出BufferSize，所以这里设置的大一点
                })
                .build();
        //2、创建工厂
        HttpServiceProxyFactory factory = HttpServiceProxyFactory
                .builder(WebClientAdapter.forClient(client)).build();
        //3、获取代理对象
        BingService bingService = factory.createClient(BingService.class);


        //4、测试调用
        Mono<String> search = bingService.search("hjc");
        System.out.println("==========");
        search.subscribe(str -> System.out.println(str));

        Thread.sleep(100000);

    }

}
```

