# 死信消息

当消费重试到达阈值以后，消息不会被投递给消费者了，而是进入了死信队列

当一条消息初次消费失败，RocketMQ会自动进行消息重试，达到最大重试次数后，若消费依然失败，则表明消费者在正常情况下无法正确地消费该消息。此时，该消息不会立刻被丢弃，而是将其发送到该消费者对应的特殊队列中，这类消息称为死信消息(`Dead-Letter Message`)，存储死信消息的特殊队列称为死信队列 (`Dead-Letter Queue`)

死信队列是死信Topic下分区数唯一的单独队列。如果产生了死信消息，那对应的ConsumerGroup的死信Topic名称为`%DLQ%ConsumerGroupName`，死信队列的消息将不会再被消费。可以利用RocketMQ Admin工具或者RocketMQ Dashboard上查询到对应死信消息的信息。也可以去监听死信队列，然后进行自己的业务上的逻辑

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
     * 发送消息
     *
     * @throws Exception
     */
    @Test
    public void testDeadMsg(){
        String key = UUID.randomUUID().toString();
        System.out.println("key = " + key);
        Message<String> message = MessageBuilder.withPayload("死信队列")
                .setHeader(RocketMQHeaders.KEYS, key)
                .build();
        // 往主题里面发送一个简单的字符串消息
        rocketMQTemplate.syncSend("DeadTopicTest:tagA", message);
        System.out.println("发送成功");
    }
}
```

![image-20240327230230761](assets/img202403272302783.png)

## 消费者

```java
@Component
@RocketMQMessageListener(topic = "DeadTopicTest",
        consumerGroup = "dead-consumer-group",
        selectorExpression = "tagA || tagB || tagC")
public class MsgListener implements RocketMQListener<MessageExt>, RocketMQPushConsumerLifecycleListener {
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
        System.out.println(new Date());
        System.out.println(new String(messageExt.getBody()));
        //消息处理次数的处理
        System.out.println("消息处理次数的处理次数:"+messageExt.getReconsumeTimes());
        // 模拟报错
        throw new RuntimeException("消费失败");
    }

    @Override
    public void prepareStart(DefaultMQPushConsumer consumer) {
        // 设定重试次数
        consumer.setMaxReconsumeTimes(2);
    }
}
```

![image-20240327231142064](assets/img202403272311184.png)

## 查看效果

![image-20240323174833749](assets/img202403231748311.png)

## 监听死信消息

直接监听死信主题的消息,记录下拉 通知人工接入处理：

```java
@Component
@RocketMQMessageListener(topic = "%DLQ%dead-consumer-group",
        consumerGroup = "retry-dead-consumer-group")
public class DeadMsgListener implements RocketMQListener<MessageExt> {
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
        System.out.println(new Date());
        System.out.println(new String(messageExt.getBody()));
        System.out.println("记录到特别的位置 文件 mysql 通知人工处理");
        // 业务报错了 返回null 返回 RECONSUME_LATER 都会重试
    }
}
```

![image-20240327231531186](assets/img202403272315032.png)

![image-20240323175156058](assets/img202403231751595.png)
