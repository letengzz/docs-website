# Java操作RabbitMQ

## 基本Java客户端

使用最基本的Java客户端连接方式。

### 导入依赖

```xml
<dependency>
    <groupId>com.rabbitmq</groupId>
    <artifactId>amqp-client</artifactId>
    <version>5.14.2</version>
</dependency>
```

### 生产者

生产者负责将信息发送到消息队列：

```java
public static void main(String[] args) {
    //使用ConnectionFactory来创建连接
    ConnectionFactory factory = new ConnectionFactory();

    //设定连接信息
    factory.setHost("192.168.56.181");
    factory.setPort(5672);  //注意这里写5672，是amqp协议端口
    factory.setUsername("admin");
    factory.setPassword("admin");
    factory.setVirtualHost("/test");
  
 		//创建连接
    try(Connection connection = factory.newConnection()){
        
    }catch (Exception e){
        e.printStackTrace();
    }
}
```

这里可以直接在程序中定义并创建消息队列（实际上是和在管理页面创建一样的效果）客户端需要通过连接创建一个新的通道（Channel），同一个连接下可以有很多个通道，这样就不用创建很多个连接也能支持分开发送了。

```java
try(Connection connection = factory.newConnection();
    Channel channel = connection.createChannel()){   //通过Connection创建新的Channel
    //声明队列，如果此队列不存在，会自动创建
    channel.queueDeclare("testJava", false, false, false, null);
    //将队列绑定到交换机
    channel.queueBind("testJava", "amq.direct", "my_queue");
    //发布新的消息，注意消息需要转换为byte[]
    channel.basicPublish("amq.direct", "my_queue", null, "Hello World!".getBytes());
}catch (Exception e){
    e.printStackTrace();
}
```

`queueDeclare`方法的参数：

* queue：队列的名称（默认创建后routingKey和队列名称一致）
* durable：是否持久化。
* exclusive：是否排他，如果一个队列被声明为排他队列，该队列仅对首次声明它的连接可见，并在连接断开时自动删除。排他队列是基于Connection可见，同一个Connection的不同Channel是可以同时访问同一个连接创建的排他队列，并且，如果一个Connection已经声明了一个排他队列，其他的Connection是不允许建立同名的排他队列的，即使该队列是持久化的，一旦Connection关闭或者客户端退出，该排他队列都会自动被删除。
* autoDelete：是否自动删除。
* arguments：设置队列的其他一些参数，这里暂时不需要什么其他参数。

`queueBind`方法参数：

* queue：需要绑定的队列名称。
* exchange：需要绑定的交换机名称。
* routingKey

`basicPublish`方法的参数：

* exchange：对应的Exchange名称，我们这里就使用第二个直连交换机。
* routingKey：这里我们填写绑定时指定的routingKey，其实和之前在管理页面操作一样。
* props：其他的配置。
* body：消息本体。

执行完成后，可以在管理页面中看到刚刚创建好的消息队列了：

![image-20240312235711737](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130001157.png)

并且此消息队列已经成功与`amq.direct`交换机进行绑定：

![image-20240312235646035](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130001169.png)

### 消费者

消息队列中已经存在数据了，创建一个消费者将其读取出来：

```java
public static void main(String[] args) throws IOException, TimeoutException {
    ConnectionFactory factory = new ConnectionFactory();
    factory.setHost("10.37.129.4");
    factory.setPort(5672);
    factory.setUsername("admin");
    factory.setPassword("admin");
    factory.setVirtualHost("test");

    //这里不使用try-with-resource，因为消费者是一直等待新的消息到来，然后按照
    //我们设定的逻辑进行处理，所以这里不能在定义完成之后就关闭连接
    Connection connection = factory.newConnection();
    Channel channel = connection.createChannel();

    //创建一个基本的消费者
    channel.basicConsume("testJava", false, (s, delivery) -> {
        System.out.println(new String(delivery.getBody()));
        //basicAck是确认应答，第一个参数是当前的消息标签，后面的参数是
        //是否批量处理消息队列中所有的消息，如果为false表示只处理当前消息
        channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        //basicNack是拒绝应答，最后一个参数表示是否将当前消息放回队列，如果
        //为false，那么消息就会被丢弃
        //channel.basicNack(delivery.getEnvelope().getDeliveryTag(), false, false);
        //跟上面一样，最后一个参数为false，只不过这里省了
        //channel.basicReject(delivery.getEnvelope().getDeliveryTag(), false);
    }, s -> {});
}
```

`basicConsume`方法参数：

* queue  -  消息队列名称，直接指定。
* autoAck - 自动应答，消费者从消息队列取出数据后，需要跟服务器进行确认应答，当服务器收到确认后，会自动将消息删除，如果开启自动应答，那么消息发出后会直接删除。
* deliver  -  消息接收后的函数回调，我们可以在回调中对消息进行处理，处理完成后，需要给服务器确认应答。
* cancel  -  当消费者取消订阅时进行的函数回调，这里暂时用不到。

现在启动一下消费者，可以看到立即读取到刚刚插入到队列中的数据：

![image-20240313000143704](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130001376.png)





