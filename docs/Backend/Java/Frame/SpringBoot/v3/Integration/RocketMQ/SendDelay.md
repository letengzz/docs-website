# 发送延迟消息

消息放入mq后，过一段时间，才会被监听到，然后消费

比如下订单业务，提交了一个订单就可以发送一个延时消息，30min后去检查这个订单的状态，如果还是未付款就取消订单释放库存。

注意：RocketMQ不支持任意时间的延时 只支持几个固定的延时等级，等级1就对应1s，以此类推，最高支持2h延迟

```java
private String messageDelayLevel = "1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h";
```

## 生产者

```java
@SpringBootTest
class Producer {
    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 发送延迟消息
     */
    @Test
    public void testDelaySend(){
        // 构建消息对象
        Message<String> message = MessageBuilder.withPayload("延迟消息").build();
        // 发送一个延时消息，延迟等级为4级，也就是30s后被监听消费
        SendResult sendResult = rocketMQTemplate.syncSend("DelayTopicTest", message, 2000, 4);
        //打印时间
        System.out.println("发送时间："+new Date());
        System.out.println(sendResult.getSendStatus());
    }
}
```

运行后查看控制台：

![image-20240324173610681](assets/img202403241736152.png)

查看RocketMQ的控制台：

![image-20240324173919342](assets/img202403241739777.png)

查看消息的细节：

![image-20240324173955807](assets/img202403241739845.png)

## 消费者

```java
/**
 * 创建一个简单消息的监听
 * 1. 类上添加注解@Component和@RocketMQMessageListener
 *  RocketMQMessageListener(topic = "SimpleTopicTest", consumerGroup = "simple-consumer-group")
 *      topic指定消费的主题，consumerGroup指定消费组,一个主题可以有多个消费者组,一个消息可以被多个不同的组的消费者都消费
 * 2. 实现RocketMQListener接口，注意泛型的使用，可以为具体的类型，如果想拿到消息的其他参数可以写成MessageExt
 */
@Component
@RocketMQMessageListener(topic = "DelayTopicTest", consumerGroup = "delay-consumer-group")
public class DelayMsgListener implements RocketMQListener<MessageExt> {
    /**
     * 消费消息的方法
     * 如果泛型指定了固定的类型 那么消息体就是参数
     * MessageExt 类型是消息的所有内容
     * 如果没有报错 就签收了
     * 如果报错了 就是拒收 就会重试
     * @param messageExt
     */
    @Override
    public void onMessage(MessageExt messageExt) {
        System.out.println(new String(messageExt.getBody()));
        //打印时间
        System.out.println("发送时间："+new Date());
    }
}
```

启动 rocketmq-consumer，运行结果：查看控制台，发现已经监听到消息了

![image-20240324174203617](assets/img202403241742416.png)
