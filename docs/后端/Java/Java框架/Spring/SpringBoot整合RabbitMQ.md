### 依赖
```java
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <!-- 无需在parent的配置文件中添加 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-amqp</artifactId>
    </dependency>

</dependencies>
```
### 配置文件

```yml
spring:
  rabbitmq:
    host: 192.168.10.100
    username: pnz
    password: abc123
```

### 配置交换机&队列

**注意：**每一队列同时只能绑定一个交换机

```java
@Configuration
public class RabbitMQConfig {
    //声明交换机
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
    
    /**
    * 将消息转换器设置为Json消息转化器
    */
    @Bean
    public MessageConverter messageConverter(){
        return new Jackson2JsonMessageConverter();
    }
}
```
### 自动确认&自动应答

#### 生产者

```java
@NoArgsConstructor
@Data  //MQMsg2
public class MQMsg implements Serializable {
    private static final long serialVersionUID = 11L;
    private Integer id;
    private String content;

    public MQMsg(Integer id, String content) {
        this.id = id;
        this.content = content;
    }

}
```

> 注意：
>
> 发送的消息如果是对象，那么该对象需要实现Serializable
>
> 并且要有无参构造函数（java在反序列化是需要无参构造）

```java
@RestController
@Slf4j
public class ProducerController {
    @Resource
    private RabbitTemplate rabbitTemplate;
    
    @GetMapping("/sendMsg")
    public String sendMsg(@RequestParam(name = "msg", defaultValue = "10", required = false) Integer num) {
        for (int i = 0; i < num; i++) {
            if(i % 2 == 0) {
                MQMsg msg = new MQMsg(i, RabbitMQConfig.DIRECT_QUEUE1_ROUTING_KEY + " content: " + i);
                System.out.println("send msg: " + msg);
                rabbitTemplate.convertAndSend(RabbitMQConfig.DIRECT_EXCHANGE_NAME, 
                                              RabbitMQConfig.DIRECT_QUEUE1_ROUTING_KEY, 
                                              msg);
            }else{
                MQMsg2 msg = new MQMsg2(i, RabbitMQConfig.DIRECT_QUEUE2_ROUTING_KEY + " content: " + i);
                System.out.println("send msg: " + msg);
                rabbitTemplate.convertAndSend(RabbitMQConfig.DIRECT_EXCHANGE_NAME, 
                                              RabbitMQConfig.DIRECT_QUEUE2_ROUTING_KEY, 
                                              msg);
            }
        }
        return "sendMsg success";
    }
}
```
#### 消费者

> 消息只会被一个消费者消费，不会重复消费
>
> 消费者接收一个消息后，会在处理完这个消息后再次接收消息
>
> 被@RabbitListener标识的方法，可以将第二个参数的类型声明为消息对象的类型，此参数会直接获取消息的body

```java
@Component
@Slf4j
public class RabbitMQConsumer {

    @RabbitListener(queues = RabbitMQConfig.QUEUE_1)
    public void received1(Message message, MQMsg mqMsg, Channel channel){
        log.info("{}是message对象", message);
        log.info("{}是实体类消息", mqMsg);
//        log.info("{}是channel", channel);
    }

    @RabbitListener(queues = RabbitMQConfig.QUEUE_2)
//    public void received2(Message message, Channel channel){
    public void received2(Message message, MQMsg2 mqMsg, Channel channel){
        log.info("message对象: {}", message);
        log.info("实体类消息: {}", mqMsg);
//        log.info("{}是channel", channel);
    }
}
```

```java
// 通过@RabbitHandler  消费数据
// 通过@RabbitListener确定监听的队列
// 通过@RabbitHandler 确定消费消息的类型
// 方法中参数的位置随意，程序根据类型注入参数

@RabbitListener(queues = RabbitMQConfig.QUEUE_1)
@Component
@Slf4j
public class RabbitMQConsumer2 {

    @RabbitHandler
    public void received1(Message message, MQMsg mqMsg, Channel channel){
        log.info("{}是message对象", message);
        log.info("{}是实体类消息", mqMsg);
    }

    @RabbitHandler
    public void received2(MQMsg2 mqMsg){
        log.info("实体类消息: {}", mqMsg);
    }
}
```



### 发布确认

#### 配置

```yml
spring:
  rabbitmq:
	...
    publisher-confirm-type: correlated
    # publisher-confirms: true  # 已经被废弃  
```

在配置文件中添加`spring.rabbitmq.publisher-confirm-type=correlated`

**none**:禁用发布确认模式，是默认值 

**correlated**:发布消息成功到交换器后会触发回调方法 

**simple**:经测试有两种效果，其一效果和 correlated 值一样会触发回调方法， 其二在发布消息成功后使用 rabbitTemplate 调用 waitForConfirms 或 waitForConfirmsOrDie 方法 等待 broker 节点返回发送结果，根据返回结果来判定下一步的逻辑，要注意的点是 waitForConfirmsOrDie 方法如果返回 false 则会关闭 channel，则接下来无法发送消息到 broker

#### 生产者

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

#### 消费者

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

#### 配置

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

### 消息应答

#### 配置

```yml
spring:
  rabbitmq:
    ...
    listener:
      simple:
        acknowledge-mode: manual
```

#### 消费者

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

