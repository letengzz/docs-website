# 消息过滤

RocketMQ提供消息过滤功能，通过tag或者key进行区分

往一个主题里面发送消息的时候，根据业务逻辑，可能需要区分，比如带有tagA标签的被A消费，带有tagB标签的被B消费，还有在事务监听的类里面，只要是事务消息都要走同一个监听，也需要通过过滤来区别对待

## 发送带标签(Tag)的消息

不同的业务应该使用不同的Topic如果是相同的业务里面有不同表的表现形式，那么要使用tag进行区分：

1. **消息类型是否一致**：如普通消息、事务消息、定时（延时）消息、顺序消息，不同的消息类型使用不同的 Topic，无法通过 Tag 进行区分。
2. **业务是否相关联**：没有直接关联的消息，如淘宝交易消息，京东物流消息使用不同的 Topic 进行区分；而同样是天猫交易消息，电器类订单、女装类订单、化妆品类订单的消息可以用 Tag 进行区分。
3. **消息优先级是否一致**：如同样是物流消息，盒马必须小时内送达，天猫超市 24 小时内送达，淘宝物流则相对会慢一些，不同优先级的消息用不同的 Topic 进行区分。
4. **消息量级是否相当**：有些业务消息虽然量小但是实时性要求高，如果跟某些万亿量级的消息使用同一个 Topic，则有可能会因为过长的等待时间而"饿死"，此时需要将不同量级的消息进行拆分，使用不同的 Topic。

总的来说，针对消息分类，您可以选择创建多个 Topic，或者在同一个 Topic 下创建多个 Tag。但通常情况下，不同的 Topic 之间的消息没有必然的联系，而 Tag 则用来区分同一个 Topic 下相互关联的消息，例如全集和子集的关系、流程先后的关系。

### 生产者

```java
public class Producer {
    public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
        // 创建默认的生产者
        DefaultMQProducer producer = new DefaultMQProducer("tag-producer-group");
        //设置nameServer地址
        producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //启动实例
        producer.start();

        Message message1 = new Message("TagTopicTest", "tagA", "我是一个带标记的消息A".getBytes());
        Message message2 = new Message("TagTopicTest", "tagB", "我是一个带标记的消息B".getBytes());
        SendResult send1 = producer.send(message1);
        SendResult send2 = producer.send(message2);
        System.out.println("send1 = " + send1);
        System.out.println("send2 = " + send2);
        // 关闭实例
        producer.shutdown();
    }
}
```

启动生产者进行测试：

![image-20240320000152692](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403200002595.png)

### 消费者

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("tag-consumer-group-b");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        // 订阅一个主题来消费   表达式，默认是*,支持"tagA || tagB || tagC" 这样或者的写法 只要是符合任何一个标签都可以消费
        consumer.subscribe("TagTopicTest", "tagA");
        // 注册一个消费监听 MessageListenerConcurrently是并发消费
        // 默认是20个线程一起消费，可以参看 consumer.setConsumeThreadMax()
        consumer.registerMessageListener(new MessageListenerConcurrently() {
            @Override
            public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> list, ConsumeConcurrentlyContext consumeConcurrentlyContext) {
                // 这里执行消费的代码 默认是多线程消费
                System.out.println(Thread.currentThread().getName() + "----" + new String(list.get(0).getBody()));
                System.out.println(list.get(0).getTags());
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
            }
        });
        // 这个start一定要写在registerMessageListener下面
        consumer.start();
        // 挂起当前的jvm
        System.in.read();
    }
}
```

启动消费者进行测试：

![image-20240320000313973](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403200003819.png)

## 发送带key的消息

在RocketMQ中的消息，默认会有一个messageId当做消息的唯一标识，可以给消息携带一个key，用作唯一标识或者业务标识，包括在控制面板查询的时候也可以使用messageId或者key来进行查询

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403200004263.png)

### 生产者

```java
public class Producer {
    public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
        // 创建默认的生产者
        DefaultMQProducer producer = new DefaultMQProducer("key-producer-group");
        //设置nameServer地址
        producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //启动生产者
        producer.start();

        //key 要确保唯一 为了查阅和去重
        String uuid = UUID.randomUUID().toString();
        System.out.println("uuid = " + uuid);
        Message message = new Message("KeyTopicTest", "tagA", uuid, "我是一个带标记和key的消息A".getBytes());
        // 发送两个消息
        SendResult send1 = producer.send(message);
        System.out.println("send1 = " + send1);
        // 关闭实例
        producer.shutdown();
    }
}
```

启动生产者进行测试：

![image-20240320000935348](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403200009472.png)

### 消费者

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("consumer_group");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        // 订阅一个主题来消费   表达式，默认是*,支持"tagA || tagB || tagC" 这样或者的写法 只要是符合任何一个标签都可以消费
        consumer.subscribe("KeyTopicTest", "tagA || tagB || tagC");
        // 注册一个消费监听 MessageListenerConcurrently是并发消费
        // 默认是20个线程一起消费，可以参看 consumer.setConsumeThreadMax()
        consumer.registerMessageListener(new MessageListenerConcurrently() {
            @Override
            public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> list, ConsumeConcurrentlyContext consumeConcurrentlyContext) {
                System.out.println(Thread.currentThread().getName() + "----" + new String(list.get(0).getBody()));
                System.out.println(list.get(0).getTags());
                System.out.println(list.get(0).getKeys());
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
            }
        });
        // 这个start一定要写在registerMessageListener下面
        consumer.start();
        // 挂起当前的jvm
        System.in.read();
    }
}
```

启动消费者进行测试：

![image-20240320001048212](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403200011707.png)

### 查看效果

![image-20240320001512907](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403200015549.png)
