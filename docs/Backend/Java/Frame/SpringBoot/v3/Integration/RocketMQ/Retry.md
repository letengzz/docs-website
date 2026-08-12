# 重试机制

## 生产者重试

失败的情况重发3次：

```yaml [application.yaml]
rocketmq:
  producer:
    #同步消息发送失败重试次数
    retry-times-when-send-failed: 3
    #异步消息发送失败重试的次数
    retry-times-when-send-async-failed: 3
```

消息在1S内没有发送成功，就会重试：

```java
rocketMQTemplate.syncSend("RetryTopicTest", "我是一个简单的消息",1000);
```

## 消费者重试

在业务报错 返回null也会执行重试。

**重试时间**：

> 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h

第一次10s .... 如果重试了16次(**默认重试16次**)，那么这个消息就会被终止发送给消费者，传递到死信队列。

**例**：

```java
@Component
@RocketMQMessageListener(topic = "DeadTopicTest",
        consumerGroup = "dead-consumer-group",
        selectorExpression = "tagA || tagB || tagC"
)
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
        // 获取重试的次数 失败一次消息中的失败次数会累加一次
        System.out.println("消息处理次数的处理次数:"+messageExt.getReconsumeTimes());
        // 模拟报错
        throw new RuntimeException("消费失败");
    }
    /**
     * 对消费者客户端的一些配置
     * 重写prepareStart方法
     * @param defaultMQPushConsumer
     */
    @Override
    public void prepareStart(DefaultMQPushConsumer defaultMQPushConsumer) {
        // 设定重试次数 重试的次数一般 5次
        defaultMQPushConsumer.setMaxReconsumeTimes(5);
    }
}
```
