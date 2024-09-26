# RocketMQ 保证消息有序

RocketMQ 保证消息的有序性分为了两种：

- **全局有序：** 适用于并发度不大，并且对消息要求严格一致性的场景下通过创建一个 topic，并且该 topic 下只有一个队列，那么生产者向着一个队列中发消息，消费者也在这一个队列中消费消息，来保证消息的有序性
- **局部有序：** 适用于对性能要求比较高的场景，在设计层面将需要保证有序的消息放在 Topic 下的同一个队列即可保证有序

那么一般情况下，只需要保证局部有序即可，那么为了保证局部有序，可以在发送消息时，指定一个 MessageSelector 对象，来指定消息发送到哪一个 Message Queue 中去，将需要保证有序的消息发送到同一个 Message Queue 来保证消息的局部有序性

## 保证消息的局部有序

将需要保证有序的消息放在 Topic 下的同一个 Message Queue 即可：

![image-20240329175038307](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403291750009.png)

代码如下，在发送消息的时候，指定 MessageSelector 对象 来将需要保证有序的消息发送到同一个队列中去即可：

```java
/**
 * 这里发送消息的时候，根据 orderId 来选择对应发送的队列
 */
producer.send(msg, new MessageQueueSelector() {
    @Override
    public MessageQueue select(List<MessageQueue> mqs, Message msg, Object arg) {
        int orderId = (int)arg;
        int idx = orderId % mqs.size();
        return mqs.get(idx);
    }
}, order.orderId);
```

上边在 **发送消息时保证了消息的有序性** ，那么在 **消费消息** 时也需要保证消息的有序消费，RocketMQ 的 MessageListener 回调函数提供了两种消费模式：

- **有序消费**：MessageListenerOrderly
- **并发消费**：MessageListenerConcurrently

为了保证有序消费，需要保证消费者注册 MessageListenerOrderly 的回调函数，来实现 **顺序消费**

上边两种消费方式都是使用线程池去消费消息，只不过在 MessageListenerOrderly 通过分布式锁和本地锁来保证同时只有一条线程去队列中消费数据，以此来保证顺序消费

但是使用了 MessageListenerOrderly 顺序消费会导致 两个**问题**：

- 使用了锁，导致吞吐量下降
- 前一个消息阻塞时，会导致后边消息都被阻塞。因此如果消息消费失败，要设置好最大重试