# 发送同步消息

发送同步消息，发送过后会有一个返回值，也就是mq服务器接收到消息后返回的一个确认，这种方式非常安全，但是性能上并没有这么高，而且在mq集群中，也是要等到所有的从机都复制了消息以后才会返回，所以针对重要的消息可以选择这种方式

消息由消费者发送到broker后，会得到一个确认，是具有可靠性的。这种可靠性同步地发送方式使用的比较广泛，比如：重要的消息通知，短信通知等。

![](assets/img202403172015667.jpg)

## 生产者

三种方式发送同步消息：这三种发送消息的方法，底层都是调用syncSend，发送的是同步消息

- `rocketMQTemplate.syncSend()`
- `rocketMQTemplate.send()`
- `rocketMQTemplate.convertAndSend()`

```java
@SpringBootTest
class Producer {
    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 发送同步消息
     *
     * @throws Exception
     */
    @Test
    public void testSyncSend(){
        // 往simpleTopicTest的主题里面发送一个简单的字符串消息
        SendResult sendResult = rocketMQTemplate.syncSend("SyncTopicTest", "发送一个同步消息");
        // 拿到消息的发送状态
        System.out.println(sendResult.getSendStatus());
        // 拿到消息的id
        System.out.println(sendResult.getMsgId());
    }
}
```

运行后查看控制台：

![image-20240324160317526](assets/img202403241603211.png)

查看RocketMQ的控制台：

![image-20240324160436245](assets/img202403241604647.png)

查看消息的细节：

![image-20240324160509280](assets/img202403241605700.png)

## 消费者

```java
/**
 * 创建一个同步消息的监听
 * 1. 类上添加注解@Component和@RocketMQMessageListener
 * RocketMQMessageListener(topic = "SyncTopicTest", consumerGroup = "sync-consumer-group")
 *      topic指定消费的主题，consumerGroup指定消费组,一个主题可以有多个消费者组,一个消息可以被多个不同的组的消费者都消费
 * 2. 实现RocketMQListener接口，注意泛型的使用，可以为具体的类型，如果想拿到消息的其他参数可以写成MessageExt
 */
@Component
@RocketMQMessageListener(topic = "SyncTopicTest",
        consumerGroup = "sync-consumer-group")
public class SyncMsgListener implements RocketMQListener<MessageExt> {
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
    }
}
```

启动 rocketmq-consumer，运行结果：查看控制台，发现已经监听到消息了

![image-20240324160839789](assets/img202403241608816.png)
