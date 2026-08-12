# 消息消费两种模式

Rocketmq消息消费的模式分为两种：**负载均衡模式**和**广播模式**

消息会被投递(或者消费者主动拉取)给每一个组，在每一个组内是进行负载均衡还是广播模式，是看这个消费者组的配置

- **负载均衡模式**`MessageModel.CLUSTERING`：负载均衡模式表示多个消费者交替消费同一个主题里面的消息
- **广播模式**`MessageModel.BROADCASTING`：广播模式表示每个每个消费者都消费一遍订阅的主题的消息

![image-20231219205310716](assets/img202312192053776.png)

:::danger 注意

- 负载均衡模式下，队列会被消费者分摊，队列数量≥消费者数量。消息的消费位点，MQ服务器会记录处理
- 广播模式下，消息会被每一个消费者都处理一次，MQ服务器不会记录消费点位，也不会重试

:::

## 负载均衡模式

生产者：

```java
@SpringBootTest
class Producer {

    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 测试发送消息
     *
     * @throws Exception
     */
    @Test
    public void testClusterMsg(){
        // 往主题里面发送一个简单的字符串消息
        for (int i = 0; i < 10; i++) {
            rocketMQTemplate.syncSend("ModeClusterTopicTest", "我是消息" + i);
        }
    }
}
```

消费者1：

```java
@Component
@RocketMQMessageListener(topic = "ModeClusterTopicTest",
        consumerGroup = "cluster-consumer-group",
        messageModel = MessageModel.CLUSTERING
        /* messageModel  指定消息消费的模式
         *   CLUSTERING 为负载均衡模式
         *   BROADCASTING 为广播模式 */
)
public class MsgCluster1Listener implements RocketMQListener<MessageExt> {
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
        System.out.println("Msg1---" +new String(messageExt.getBody()));
    }
}
```

消费者2：

```java
@Component
@RocketMQMessageListener(topic = "ModeClusterTopicTest",
        consumerGroup = "cluster-consumer-group",
        messageModel = MessageModel.CLUSTERING
        /* messageModel  指定消息消费的模式
         *   CLUSTERING 为负载均衡模式
         *   BROADCASTING 为广播模式 */
)
public class MsgCluster2Listener implements RocketMQListener<MessageExt> {
    /**
     * 消费消息的方法
     * 如果泛型指定了固定的类型 那么消息体就是参数
     * MessageExt 类型是消息的所有内容
     * 如果没有报错 就签收了
     * 如果报错了 就是拒收 就会重试
     *
     * @param messageExt
     */
    @Override
    public void onMessage(MessageExt messageExt) {
        System.out.println("Msg2---" + new String(messageExt.getBody()));
    }
}
```

查看效果：

![image-20240328233805626](assets/img202403282338339.png)

## 广播模式

项目中 一般部署多态机器 消费者 2 - 3 根据业务可以选择具体的模式来配置

重置消费点位, 将一个组的消费节点 设置在之前的某一个时间点上去 从这个时间点开始往后消费

跳过堆积 选择一个组 跳过堆积以后 这个组里面的的所有都不会被消费了

---

生产者：

```java
@SpringBootTest
class Producer {

    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 测试发送消息
     *
     * @throws Exception
     */
    @Test
    public void testBroadMsg(){
        // 往主题里面发送一个简单的字符串消息
        for (int i = 0; i < 10; i++) {
            rocketMQTemplate.syncSend("ModeBroadTopicTest", "我是消息" + i);
        }
    }
}
```

消费者1：

```java
@Component
@RocketMQMessageListener(topic = "ModeBroadTopicTest",
        consumerGroup = "broad-consumer-group",
        messageModel = MessageModel.BROADCASTING
        /* messageModel  指定消息消费的模式
         *   CLUSTERING 为负载均衡模式
         *   BROADCASTING 为广播模式 */
)
public class MsgBroad1Listener implements RocketMQListener<MessageExt>, RocketMQPushConsumerLifecycleListener {
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
        System.out.println("Msg1---" +new String(messageExt.getBody()));
    }

    @Override
    public void prepareStart(DefaultMQPushConsumer consumer) {
        //设置当前实例的名称
        consumer.setInstanceName("MsgBroad1Listener");
    }
}
```

消费者2：

```java
@Component
@RocketMQMessageListener(topic = "ModeBroadTopicTest",
        consumerGroup = "broad-consumer-group",
        messageModel = MessageModel.BROADCASTING
        /* messageModel  指定消息消费的模式
         *   CLUSTERING 为负载均衡模式
         *   BROADCASTING 为广播模式 */
)
public class MsgBroad2Listener implements RocketMQListener<MessageExt>, RocketMQPushConsumerLifecycleListener {
    /**
     * 消费消息的方法
     * 如果泛型指定了固定的类型 那么消息体就是参数
     * MessageExt 类型是消息的所有内容
     * 如果没有报错 就签收了
     * 如果报错了 就是拒收 就会重试
     *
     * @param messageExt
     */
    @Override
    public void onMessage(MessageExt messageExt) {
        System.out.println("Msg2---" + new String(messageExt.getBody()));
    }

    @Override
    public void prepareStart(DefaultMQPushConsumer consumer) {
        //设置当前实例的名称
        consumer.setInstanceName("MsgBroad2Listener");
    }
}
```

查看效果：

![image-20240328233730554](assets/img202403282337444.png)
