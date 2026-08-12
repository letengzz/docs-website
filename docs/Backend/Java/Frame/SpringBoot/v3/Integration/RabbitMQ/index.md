# SpringBoot 整合 RabbitMQ

官方文档：https://docs.spring.io/spring-amqp/docs/current/reference/html/

## 基本使用

### 基本信息配置

导入依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

配置RabbitMQ的地址等信息：

```yaml
spring:
  rabbitmq:
    addresses: 192.168.56.181
    username: admin
    password: admin
    virtual-host: test
```

这样完成了最基本信息配置。

### 生产者

:::danger 注意

每一队列同时只能绑定一个交换机

:::

声明一个消息队列只需要一个配置类：

```java
@Configuration
public class RabbitConfiguration {
    //定义交换机Bean，可以很多个
    //fanout
    public static final String FANOUT_EXCHANGE_NAME = "fanout.exchange";
    public static final String QUEUE_1 = "queue.1";
    public static final String QUEUE_2 = "queue.2";

    //direct
    public static final String DIRECT_EXCHANGE_NAME = "direct.exchange";
    public static final String DIRECT_QUEUE1_ROUTING_KEY = "direct.queue.1.routingkey";
    public static final String DIRECT_QUEUE2_ROUTING_KEY = "direct.queue.2.routingkey";
    //topic
    public static final String TOPIC_EXCHANGE_NAME = "topic.exchange";
    public static final String TOPIC_QUEUE1_ROUTING_KEY = "*.rabbit.*"; //* 代表一个单词
    public static final String TOPIC_QUEUE2_ROUTING_KEY = "#.rabbit"; //# 代表零个或多个单词
    /*
    队列声明
     */
    @Bean
    public Queue queue1(){
        return QueueBuilder.durable(QUEUE_1).build();
    }
    @Bean
    public Queue queue2(){
        return QueueBuilder.durable(QUEUE_2).build();
    }
    /*
    fanout交换机模式的声明
     */
    @Bean
    public FanoutExchange fanoutExchange(){
        return new FanoutExchange(FANOUT_EXCHANGE_NAME);
    }
//    @Bean
//    public Binding queue1BindingFanoutExchange1(@Qualifier("fanoutExchange") FanoutExchange fanoutExchange,
//                                         @Qualifier("queue1") Queue queue){
//        return BindingBuilder.bind(queue).to(fanoutExchange);
//    }
//    @Bean
//    public Binding queue2BindingFanoutExchange(@Qualifier("fanoutExchange") FanoutExchange fanoutExchange,
//                                         @Qualifier("queue2") Queue queue){
//        return BindingBuilder.bind(queue).to(fanoutExchange);
//    }

    /*
    direct交换机模式的声明
     */
    @Bean
    public DirectExchange directExchange(){
        return new DirectExchange(DIRECT_EXCHANGE_NAME);
    }
    @Bean
    public Binding queue1BindingDirectExchange(@Qualifier("directExchange") DirectExchange directExchange,
                                         @Qualifier("queue1") Queue queue1){
        return BindingBuilder.bind(queue1).to(directExchange).with(DIRECT_QUEUE1_ROUTING_KEY);
    }
    @Bean
    public Binding queue2BindingDirectExchange(@Qualifier("directExchange") DirectExchange directExchange,
                                         @Qualifier("queue2") Queue queue2){
        return BindingBuilder.bind(queue2).to(directExchange).with(DIRECT_QUEUE2_ROUTING_KEY);
    }

    /*
    topic交换机模式的声明
     */
//    @Bean
//    public TopicExchange topicExchange(){
//        return new TopicExchange(TOPIC_EXCHANGE_NAME);
//    }
//    @Bean
//    public Binding queue1BindingDirectExchange(@Qualifier("topicExchange") TopicExchange topicExchange,
//                                         @Qualifier("queue1") Queue queue1){
//        return BindingBuilder.bind(queue1).to(topicExchange).with(TOPIC_QUEUE1_ROUTING_KEY);
//    }
//    @Bean
//    public Binding queue2BindingDirectExchange(@Qualifier("topicExchange") TopicExchange topicExchange,
//                                         @Qualifier("queue2") Queue queue2){
//        return BindingBuilder.bind(queue2).to(topicExchange).with(TOPIC_QUEUE2_ROUTING_KEY);
//    }
    @Bean("directExchange")
    public Exchange exchange(){
        return ExchangeBuilder.directExchange("amq.direct").build();
    }

    @Bean("yydsQueue")     //定义消息队列
    public Queue queue(){
        return QueueBuilder
          				.nonDurable("yyds")   //非持久化类型
          				.build();
    }

    @Bean("binding")
    public Binding binding(@Qualifier("directExchange") Exchange exchange,
                           @Qualifier("yydsQueue") Queue queue){
      	//将我们刚刚定义的交换机和队列进行绑定
        return BindingBuilder
                .bind(queue)   //绑定队列
                .to(exchange)  //到交换机
                .with("my-yyds")   //使用自定义的routingKey
                .noargs();
    }
}
```

接着来创建一个生产者，直接编写在测试用例中：

```java
@SpringBootTest
class SpringCloudMqApplicationTests {

  	//RabbitTemplate封装了大量的RabbitMQ操作，已经由Starter提供，因此直接注入使用即可
    @Resource
    RabbitTemplate template;

    @Test
    void publisher() {
      	//使用convertAndSend方法一步到位，参数基本和之前是一样的
      	//最后一个消息本体可以是Object类型，真是大大的方便
        template.convertAndSend("amq.direct", "my-yyds", "Hello World!");
    }

}
```

运行测试用例：

![image-20240313192639871](assets/img202403131926523.png)

可以看到后台自动声明了刚刚定义好的消息队列和交换机以及对应的绑定关系，并且数据也是成功插入到消息队列中：

![image-20240313193106234](assets/img202410170921578.png)

### 消费者

因为消费者实际上就是一直等待消息然后进行处理的角色，只需要创建一个监听器就行了，它会一直等待消息到来然后再进行处理：

```java
@Component  //注册为Bean
public class TestListener {

    @RabbitListener(queues = "yyds")   //定义此方法为队列yyds的监听器，一旦监听到新的消息，就会接受并处理
    public void test(Message message){
        System.out.println(new String(message.getBody()));
    }
}
```

接着启动服务器：

![image-20240313194152324](assets/img202410170920984.png)

可以看到控制台成功输出了之前放入队列的消息，并且管理页面中也显示此消费者已经连接了：

![image-20240313195511351](assets/img202410170921061.png)

接着再通过管理页面添加新的消息看看，也是可以正常进行接受的。

### 响应结果

当然，如果需要确保消息能够被消费者接受并处理，然后得到消费者的反馈，也是可以的：

```java
@Test
void publisher() {
  	//会等待消费者消费然后返回响应结果
    Object res = template.convertSendAndReceive("amq.direct", "my-yyds", "Hello World!");
    System.out.println("收到消费者响应："+res);
}
```

消费者这边只需要返回一个对应的结果即可：

```java
@RabbitListener(queues = "yyds")
public String receiver(String data){
    System.out.println("一号消息队列监听器 "+data);
    return "收到!";
}
```

测试没有问题：

![image-20240314015043916](assets/img202403140150090.png)

### JSON格式

如果需要直接接收一个JSON格式的消息，并且希望直接获取到实体类。

导入依赖：

```xml
<dependency>
	<groupId>com.fasterxml.jackson.core</groupId>
	<artifactId>jackson-databind</artifactId>
</dependency>
```

创建实体类：

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    int id;
    String name;
}
```

```java
@Configuration
public class RabbitConfiguration {
  	...

    @Bean("jacksonConverter")   //直接创建一个用于JSON转换的Bean
    public Jackson2JsonMessageConverter converter(){
        return new Jackson2JsonMessageConverter();
    }
}
```

接着只需要指定转换器就可以了：

```java
@Component
public class TestListener {

  	//指定messageConverter为刚刚创建的Bean名称
    @RabbitListener(queues = "yyds", messageConverter = "jacksonConverter")
    public void receiver(User user){  //直接接收User类型
        System.out.println(user);
    }
}
```

现在直接在管理页面发送：

> {"id":1,"name":"LB"}

![image-20240314020910698](assets/img202410170920721.png)

可以看到成功完成了转换，并输出了用户信息：

![image-20240314021000252](assets/img202410170921804.png)

同样的，也可以直接发送User，因为刚刚已经配置了Jackson2JsonMessageConverter为Bean，所以直接使用就可以了：

```java
@Test
void publisher() {
    template.convertAndSend("amq.direct", "yyds", new User(1,"hjc"));
}
```

可以看到：

![image-20240314021328397](assets/img202410170920253.png)

这样，就通过SpringBoot实现了RabbitMQ的简单使用。

## 工作队列模式

工作队列模式需要创建两个监听器：

```java
@Component
public class TestListener {
    @RabbitListener(queues = "yyds")
    public void receiver(String data){   //这里直接接收String类型的数据
        System.out.println("一号消息队列监听器 "+data);
    }

    @RabbitListener(queues = "yyds")
    public void receiver2(String data){
        System.out.println("二号消息队列监听器 "+data);
    }
}
```

可以看到发送消息时，会自动进行轮询分发：

![image-20240314212349135](assets/img202410170920626.png)

那么如果一开始就在消息队列中放入一部分消息在开启消费者呢？

![image-20240314212636542](assets/img202410170920314.png)

可以看到，如果是一开始就存在消息，会被一个消费者一次性全部消耗，这是因为没有对消费者的Prefetch count（预获取数量，一次性获取消息的最大数量）进行限制，也就是说现在希望的是消费者一次只能拿一个消息，而不是将所有的消息全部都获取。

![img202410170920816](assets/img202410170920816.png)

因此需要对这个数量进行一些配置，需要在配置类中定义一个自定义的ListenerContainerFactory，可以在这里设定消费者Channel的PrefetchCount的大小：

```java
@Resource
private CachingConnectionFactory connectionFactory;

@Bean(name = "listenerContainer")
public SimpleRabbitListenerContainerFactory listenerContainer(){
    SimpleRabbitListenerContainerFactory factory = new SimpleRabbitListenerContainerFactory();
    factory.setConnectionFactory(connectionFactory);
    factory.setPrefetchCount(1);   //将PrefetchCount设定为1表示一次只能取一个
    return factory;
}
```

接着在监听器这边指定即可：

```java
@Component
public class TestListener {
    @RabbitListener(queues = "yyds",  containerFactory = "listenerContainer")
    public void receiver(String data){
        System.out.println("一号消息队列监听器 "+data);
    }

    @RabbitListener(queues = "yyds", containerFactory = "listenerContainer")
    public void receiver2(String data){
        System.out.println("二号消息队列监听器 "+data);
    }
}
```

再次启动服务器，可以看到PrefetchCount被限定为1：

![image-20240314213425740](assets/img202410170920923.png)

再次重复上述的实现，可以看到消息不会被一号消费者给全部抢走了：

![image-20240314213345178](assets/img202410170920759.png)

当然除了去定义两个相同的监听器之外，也可以直接在注解中定义，比如现在需要10个同样的消费者：

```java
@Component
public class TestListener {
    @RabbitListener(queues = "yyds",  containerFactory = "listenerContainer", concurrency = "10")
    public void receiver(String data){
        System.out.println("一号消息队列监听器 "+data);
    }
}
```

可以看到在管理页面中出现了10个消费者：

![image-20240314213546889](assets/img202410170921946.png)

## 发布订阅模式

实现发布订阅模式，不能使用之前的直连交换机，需要用到另一种类型的交换机，叫做`fanout`（扇出）类型，这时一种广播类型，消息会被广播到所有与此交换机绑定的消息队列中。

使用默认的交换机：这个交换机是一个`fanout`类型的交换机

![img202410170921570](assets/img202410170921570.png)

```java
@Configuration
public class RabbitConfiguration {

    @Bean("fanoutExchange")
    public Exchange exchange(){
      	//注意这里是fanoutExchange
        return ExchangeBuilder.fanoutExchange("amq.fanout").build();
    }

    @Bean("yydsQueue1")
    public Queue queue(){
        return QueueBuilder.nonDurable("yyds1").build();
    }

    @Bean("binding")
    public Binding binding(@Qualifier("fanoutExchange") Exchange exchange,
                           @Qualifier("yydsQueue1") Queue queue){
        return BindingBuilder
                .bind(queue)
                .to(exchange)
                .with("yyds1")
                .noargs();
    }

    @Bean("yydsQueue2")
    public Queue queue2(){
        return QueueBuilder.nonDurable("yyds2").build();
    }

    @Bean("binding2")
    public Binding binding2(@Qualifier("fanoutExchange") Exchange exchange,
                           @Qualifier("yydsQueue2") Queue queue){
        return BindingBuilder
                .bind(queue)
                .to(exchange)
                .with("yyds2")
                .noargs();
    }
}
```

将两个队列都绑定到此交换机上，启动：

![image-20220420230954785](assets/img202410170926403.jpg)

绑定没有什么问题，接着搞两个监听器，监听一下这两个队列：

```java
@Component
public class TestListener {
    @RabbitListener(queues = "yyds1")
    public void receiver(String data){
        System.out.println("一号消息队列监听器 "+data);
    }

    @RabbitListener(queues = "yyds2")
    public void receiver2(String data){
        System.out.println("二号消息队列监听器 "+data);
    }
}
```

现在通过交换机发送消息，看看是不是两个监听器都会接收到消息：

![image-20220420231113658](assets/img202410170926566.jpg)

可以看到确实是两个消息队列都能够接受到此消息：

![image-20220420231145578](assets/img202410170923890.jpg)

## 路由模式

路由模式在绑定时指定想要的`routingKey`只有生产者发送时指定了对应的`routingKey`才能到达对应的队列。

除了一次绑定之外，同一个消息队列可以多次绑定到交换机，并且使用不同的`routingKey`，这样只要满足其中一个都可以被发送到此消息队列中：

```java
@Configuration
public class RabbitConfiguration {

    @Bean("directExchange")
    public Exchange exchange(){
        return ExchangeBuilder.directExchange("amq.direct").build();
    }

    @Bean("yydsQueue")
    public Queue queue(){
        return QueueBuilder.nonDurable("yyds").build();
    }

    @Bean("binding")   //使用yyds1绑定
    public Binding binding(@Qualifier("directExchange") Exchange exchange,
                           @Qualifier("yydsQueue") Queue queue){
        return BindingBuilder
                .bind(queue)
                .to(exchange)
                .with("yyds1")
                .noargs();
    }

    @Bean("binding2")   //使用yyds2绑定
    public Binding binding2(@Qualifier("directExchange") Exchange exchange,
                           @Qualifier("yydsQueue") Queue queue){
        return BindingBuilder
                .bind(queue)
                .to(exchange)
                .with("yyds2")
                .noargs();
    }
}
```

启动后可以看到管理面板中出现了两个绑定关系：

![image-20220420233606749](assets/img202410170924656.jpg)

这里可以测试一下，随便使用哪个`routingKey`都可以。

## 主题模式

实际上这种模式就是一种模糊匹配的模式，可以将`routingKey`以模糊匹配的方式去进行转发。

可以使用`*`或`#`来表示：

- \* - 表示任意的一个单词
- \# - 表示0个或多个单词

```java
@Configuration
public class RabbitConfiguration {

    @Bean("topicExchange")  //这里使用预置的Topic类型交换机
    public Exchange exchange(){
        return ExchangeBuilder.topicExchange("amq.topic").build();
    }

    @Bean("yydsQueue")
    public Queue queue(){
        return QueueBuilder.nonDurable("yyds").build();
    }

    @Bean("binding")
    public Binding binding2(@Qualifier("topicExchange") Exchange exchange,
                           @Qualifier("yydsQueue") Queue queue){
        return BindingBuilder
                .bind(queue)
                .to(exchange)
                .with("*.test.*")
                .noargs();
    }
}
```

启动项目，可以看到只要是满足通配符条件的都可以成功转发到对应的消息队列。

接着可以再试试看`#`通配符。

除了使用的默认主题交换机之外，还有一个叫做`amq.rabbitmq.trace`的交换机：

![image-20220421104035463](assets/img202410170924449.jpg)

可以看到它也是`topic`类型的，实际上这是用于帮助我们记录和追踪生产者和消费者使用消息队列的交换机，它是一个内部的交换机，那么如果使用呢？首先创建一个消息队列用于接收记录：

![image-20220421104619325](assets/img202410170924049.jpg)

接着需要在控制台将虚拟主机`/test`的追踪功能开启：

```sh
sudo rabbitmqctl trace_on -p /test
```

开启后，将此队列绑定到上面的交换机上：

![image-20220421104843224](assets/img202410170926931.jpg)

![image-20220421105141144](assets/img202410170926477.jpg)

由于发送到此交换机上的`routingKey`为routing key为 publish.交换机名称 和 deliver.队列名称，分别对应生产者投递到交换机的消息，和消费者从队列上获取的消息，因此这里使用`#`通配符进行绑定。

现在来测试一下，比如还是往yyds队列发送消息：

![image-20220421105242770](assets/img202410170926312.jpg)

可以看到在发送消息，并且消费者已经处理之后，`trace`队列中新增了两条消息，那么来看看都是些什么消息：

![image-20220421105528532](assets/img202410170926445.jpg)

通过追踪，可以很明确地得知消息发送的交换机、routingKey、用户等信息，包括信息本身，同样的，消费者在取出数据时也有记录：

![image-20220421105638715](assets/img202410170926364.jpg)

可以明确消费者的地址、端口、具体操作的队列以及取出的消息信息等。

## 第四种交换机类型

第四种交换机类型`header`，它是根据头部信息来决定的，在发送的消息中是可以携带一些头部信息的（类似于HTTP），可以根据这些头部信息来决定路由到哪一个消息队列中。

```java
@Configuration
public class RabbitConfiguration {

    @Bean("headerExchange")  //注意这里返回的是HeadersExchange
    public HeadersExchange exchange(){
        return ExchangeBuilder
                .headersExchange("amq.headers")  //RabbitMQ为我们预置了两个，这里用第一个就行
                .build();
    }

    @Bean("yydsQueue")
    public Queue queue(){
        return QueueBuilder.nonDurable("yyds").build();
    }

    @Bean("binding")
    public Binding binding2(@Qualifier("headerExchange") HeadersExchange exchange,  //这里和上面一样的类型
                           @Qualifier("yydsQueue") Queue queue){
        return BindingBuilder
                .bind(queue)
                .to(exchange)   //使用HeadersExchange的to方法，可以进行进一步配置
          			//.whereAny("a", "b").exist();   这个是只要存在任意一个指定的头部Key就行
                //.whereAll("a", "b").exist();   这个是必须存在所有指定的的头部Key
                .where("test").matches("hello");   //比如我们现在需要消息的头部信息中包含test，并且值为hello才能转发给我们的消息队列
      					//.whereAny(Collections.singletonMap("test", "hello")).match();  传入Map也行，批量指定键值对
    }
}
```

现在来启动一下试试看：

![img202410170926819](assets/img202410170926819.jpg)

结果发现，消息可以成功发送到消息队列，这就是使用头部信息进行路由。

## 发布确认

配置：

```yml
spring:
  rabbitmq:
	...
    publisher-confirm-type: correlated
    # publisher-confirms: true  # 已经被废弃
```

在配置文件中添加`spring.rabbitmq.publisher-confirm-type=correlated`

- **none**:禁用发布确认模式，是默认值
- **correlated**:发布消息成功到交换器后会触发回调方法
- **simple**:经测试有两种效果，其一效果和 correlated 值一样会触发回调方法， 其二在发布消息成功后使用 rabbitTemplate 调用 waitForConfirms 或 waitForConfirmsOrDie 方法 等待 broker 节点返回发送结果，根据返回结果来判定下一步的逻辑，要注意的点是 waitForConfirmsOrDie 方法如果返回 false 则会关闭 channel，则接下来无法发送消息到 broker

生产者：

```java
  @GetMapping("/sendMsg/confirm")
    public void sendMessage(){
        String message = "hello ";
        //设置id
        CorrelationData correlationData = new CorrelationData("1");
        rabbitTemplate.convertAndSend(RabbitMQConfig.DIRECT_EXCHANGE_NAME,
                                      RabbitMQConfig.DIRECT_QUEUE1_ROUTING_KEY,
                                      message+"key1",correlationData);
        log.info("发送消息内容：{}",message);
    }

    @GetMapping("/sendMsg/confirm2")
    public void sendMessage2(){
        String message = "confirm2 ";
        //设置id
        CorrelationData correlationData2 = new CorrelationData("2");
        rabbitTemplate.convertAndSend(
                RabbitMQConfig.DIRECT_EXCHANGE_NAME,
            	// routingKey is error
                RabbitMQConfig.DIRECT_QUEUE1_ROUTING_KEY + "1",
                message+"key11",
                correlationData2);
        log.info("发送消息内容：{}",message);
    }
```

消费者：

```java
@RabbitListener(queues = RabbitMQConfig.QUEUE_1)
@Component
@Slf4j
public class RabbitMQConsumer {
    @RabbitHandler
    public void received(String msg ){
        log.info("消息: {}", msg);
    }
}
```

配置：

```java
@Component
@Slf4j
public class MyCallBack implements RabbitTemplate.ConfirmCallback,RabbitTemplate.ReturnsCallback {
    @Resource
    private RabbitTemplate rabbitTemplate;

    @PostConstruct
    public void init(){
        rabbitTemplate.setConfirmCallback(this);
        /**
         * true：
         * 交换机无法将消息进行路由时，会将该消息返回给生产者
         * false：
         * 如果发现消息无法进行路由，则直接丢弃
         */
        rabbitTemplate.setMandatory(true);
        rabbitTemplate.setReturnsCallback(this);
    }

    /**
     * ConfirmCallBack接口的实现方法，在发布到交换机后会回调
     * 交换机不管是否收到消息的一个回调方法
     * CorrelationData
     * 消息相关数据
     * ack
     * 交换机是否收到消息
     */
    @Override
    public void confirm(CorrelationData correlationData, boolean ack, String cause) {
        String id = correlationData != null ? correlationData.getId():"";
        if(ack){
            log.info("交换机已经收到 id 为:{}的消息",id);
        }else{
            log.info("交换机还未收到 id 为:{}消息,由于原因:{}",id,cause);
        }
    }

    /**
     * ReturnsCallback接口的回调
     * 无法路由的消息的回调
     * @param returned 无法路由消息的信息
     */
    @Override
    public void returnedMessage(ReturnedMessage returned) {
        log.info("消息:{} 没有被队列接收，退回原因:{}, 交换机是:{}, 路由 key:{}",
                new String(returned.getMessage().getBody()),returned.getReplyText(),
                returned.getExchange(), returned.getRoutingKey());
    }
}
```

## 消息应答

配置：

```yml
spring:
  rabbitmq:
    ...
    listener:
      simple:
        acknowledge-mode: manual
```

消费者：

```java
@Component
@Slf4j
public class RabbitMQConsumer {

    @RabbitListener(queues = RabbitMQConfig.QUEUE_1)
    public void received1(Message message, MQMsg mqMsg, Channel channel) throws IOException {
        log.info("{}是message对象", message);
        log.info("{}是实体类消息", mqMsg);
        // 第一个参数 标识
        // 第二个参数是 是否批量应答
        channel.basicAck(message.getMessageProperties().getDeliveryTag(), false);
    }
}
```

## 死信队列

实际上本质就是一个死信交换机+绑定的死信队列，当正常队列中的消息被判定为死信时，会被发送到对应的死信交换机，然后再通过交换机发送到死信队列中，死信队列也有对应的消费者去处理消息。

直接在配置类中创建一个新的死信交换机和死信队列，并进行绑定：

```java
@Configuration
public class RabbitConfiguration {

    @Bean("directDlExchange")
    public Exchange dlExchange(){
        //创建一个新的死信交换机
        return ExchangeBuilder.directExchange("dlx.direct").build();
    }

    @Bean("yydsDlQueue")   //创建一个新的死信队列
    public Queue dlQueue(){
        return QueueBuilder
                .nonDurable("dl-yyds")
                .build();
    }

    @Bean("dlBinding")   //死信交换机和死信队列进绑定
    public Binding dlBinding(@Qualifier("directDlExchange") Exchange exchange,
                           @Qualifier("yydsDlQueue") Queue queue){
        return BindingBuilder
                .bind(queue)
                .to(exchange)
                .with("dl-yyds")
                .noargs();
    }

        ...

    @Bean("yydsQueue")
    public Queue queue(){
        return QueueBuilder
                .nonDurable("yyds")
                .deadLetterExchange("dlx.direct")   //指定死信交换机
                .deadLetterRoutingKey("dl-yyds")   //指定死信RoutingKey
                .build();
    }

    ...
}
```

接着将监听器修改为死信队列监听：

```java
@Component
public class TestListener {
    @RabbitListener(queues = "dl-yyds", messageConverter = "jacksonConverter")
    public void receiver(User user){
        System.out.println(user);
    }
}
```

配置完成后，启动，注意启动之前记得把之前的队列给删了，这里要重新定义。

![image-20240314152825723](assets/img202403141528860.png)

队列列表中已经出现了刚刚定义好的死信队列，并且yyds队列也支持死信队列发送功能了，现在尝试向此队列发送一个消息，但是将其拒绝：

![image-20220420105359931](assets/img202403141530848.jpg)

![image-20240314153104863](assets/img202410170921492.png)

可以看到拒绝后，如果不让消息重新排队，那么就会变成死信，直接被丢进死信队列中，可以看到在拒绝后：

![image-20240314174518242](assets/img202410170921357.png)

RabbitMQ支持将超过一定时间没被消费的消息自动删除，这需要消息队列设定TTL值，如果消息的存活时间超过了Time To Live值，就会被自动删除，自动删除后的消息如果有死信队列，那么就会进入到死信队列中。

将yyds消息队列设定TTL值（毫秒为单位）：

```java
@Bean("yydsQueue")
public Queue queue(){
    return QueueBuilder
            .nonDurable("yyds")
            .deadLetterExchange("dlx.direct")
            .deadLetterRoutingKey("dl-yyds")
            .ttl(5000)   //如果5秒没处理，就自动删除
            .build();
}
```

现在重启测试一下，注意修改了之后记得删除之前的yyds队列：

![image-20240314191834294](assets/img202410170921793.png)

可以看到现在yyds队列已经具有TTL特性了，现在来插入一个新的消息：

![image-20220420110504022](assets/img202410170927438.jpg)

可以看到消息5秒钟之后就不见了，而是被丢进了死信队列中。

当消息队列长度达到最大的情况，可以将消息队列的长度进行限制：

```java
@Bean("yydsQueue")
public Queue queue(){
    return QueueBuilder
            .nonDurable("yyds")
            .deadLetterExchange("dlx.direct")
            .deadLetterRoutingKey("dl-yyds")
            .maxLength(3L)   //将最大长度设定为3
            .build();
}
```

重启，然后尝试连续插入4个消息：

![image-20240314204047472](assets/img202410170921507.png)

可以看到yyds消息队列新增了Limit特性，也就是限定长度：

```java
@Test
void publisher() {
    for (int i = 0; i < 4; i++)
        template.convertAndSend("amq.direct", "my-yyds", new User());
}
```

![image-20240314204319574](assets/img202403142043192.png)

可以看到因为长度限制为3，所以有一个消息直接被丢进了死信队列中，为了能够更直观地观察消息队列的机制，我们为User类新增一个时间字段：

```java
@Data
public class User {
    int id;
    String name;
    String date = new Date().toString();
}
```

接着每隔一秒钟插入一个：

```java
@Test
void publisher() throws InterruptedException {
    for (int i = 0; i < 4; i++) {
        Thread.sleep(1000);
        template.convertAndSend("amq.direct", "my-yyds", new User());
    }
}
```

再次进行上述实验，可以发现如果到达队列长度限制，那么每次插入都会把位于队首的消息丢进死信队列，来腾出空间给新来的消息。
