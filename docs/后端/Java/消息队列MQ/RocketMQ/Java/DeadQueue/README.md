# RocketMQ 死信消息

当消费重试到达阈值以后，消息不会被投递给消费者了，而是进入了死信队列

当一条消息初次消费失败，RocketMQ会自动进行消息重试，达到最大重试次数后，若消费依然失败，则表明消费者在正常情况下无法正确地消费该消息。此时，该消息不会立刻被丢弃，而是将其发送到该消费者对应的特殊队列中，这类消息称为死信消息(`Dead-Letter Message`)，存储死信消息的特殊队列称为死信队列 (`Dead-Letter Queue`)

死信队列是死信Topic下分区数唯一的单独队列。如果产生了死信消息，那对应的ConsumerGroup的死信Topic名称为`%DLQ%ConsumerGroupName`，死信队列的消息将不会再被消费。可以利用RocketMQ Admin工具或者RocketMQ Dashboard上查询到对应死信消息的信息。也可以去监听死信队列，然后进行自己的业务上的逻辑

## 生产者

```java
public class Producer {
    public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException, IOException {
        DefaultMQProducer producer = new DefaultMQProducer("dead-producer-group");
        producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        producer.start();
        // 生产者发送消息 重试次数
        producer.setRetryTimesWhenSendFailed(2);
        producer.setRetryTimesWhenSendAsyncFailed(2);
        String key = UUID.randomUUID().toString();
        System.out.println("key = " + key);
        Message message = new Message("DeadTopicTest", "tagA", key, "死信队列".getBytes());
        producer.send(message,1000);
        System.out.println("发送成功");
        // 关闭实例
        producer.shutdown();
    }
}
```

![image-20240323173028210](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403231730669.png)

## 消费者

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("dead-consumer-group");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        // 订阅一个主题来消费   表达式，默认是*,支持"tagA || tagB || tagC" 这样或者的写法 只要是符合任何一个标签都可以消费
        consumer.subscribe("DeadTopicTest","tagA || tagB || tagC");
        // 设定重试次数
        consumer.setMaxReconsumeTimes(2);
        consumer.registerMessageListener(new MessageListenerConcurrently() {
            @Override
            public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> list, ConsumeConcurrentlyContext consumeConcurrentlyContext) {
                MessageExt messageExt = list.get(0);
                System.out.println(new Date());
                System.out.println(new String(messageExt.getBody()));
                //消息处理次数的处理
                System.out.println("消息处理次数的处理次数:"+messageExt.getReconsumeTimes());
                // 业务报错了 返回null 返回 RECONSUME_LATER 都会重试
                return ConsumeConcurrentlyStatus.RECONSUME_LATER;
            }
        });
        consumer.start();
        System.in.read();
    }
}
```

![image-20240323174729729](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403231747802.png)

## 查看效果

![image-20240323174833749](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403231748311.png)

## 监听死信消息

直接监听死信主题的消息,记录下拉 通知人工接入处理：

```java
public class DeadConsumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("retry-dead-consumer-group");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        // 订阅一个主题来消费   表达式，默认是*,支持"tagA || tagB || tagC" 这样或者的写法 只要是符合任何一个标签都可以消费
        consumer.subscribe("%DLQ%dead-consumer-group","*");
        consumer.registerMessageListener(new MessageListenerConcurrently() {
            @Override
            public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs, ConsumeConcurrentlyContext context) {
                MessageExt messageExt = msgs.get(0);
                System.out.println(new Date());
                System.out.println(new String(messageExt.getBody()));
                System.out.println("记录到特别的位置 文件 mysql 通知人工处理");
                // 业务报错了 返回null 返回 RECONSUME_LATER 都会重试
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
            }
        });
        consumer.start();
        System.in.read();
    }
}
```

![image-20240323175116412](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403231751840.png)

![image-20240323175156058](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403231751595.png)