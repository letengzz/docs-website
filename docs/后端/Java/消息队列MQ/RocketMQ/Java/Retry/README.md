# 重试机制

## 生产者重试

失败的情况重发3次：

```java
producer.setRetryTimesWhenSendFailed(3);
producer.setRetryTimesWhenSendAsyncFailed(3);
```

消息在1S内没有发送成功，就会重试：

```java
producer.send(msg, 1000);
```

**例**：

```java
public class Producer {
    public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException, IOException {
        DefaultMQProducer producer = new DefaultMQProducer("retry-producer-group");
        producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        producer.start();
        // 生产者发送消息 重试次数
        producer.setRetryTimesWhenSendFailed(2);
        producer.setRetryTimesWhenSendAsyncFailed(2);
        String key = UUID.randomUUID().toString();
        System.out.println("key = " + key);
        Message message = new Message("RetryTopicTest", "tagA", key, "重试".getBytes());
        producer.send(message,1000);
        System.out.println("发送成功");
        // 关闭实例
        producer.shutdown();
    }
}
```

## 消费者重试

在消费者返回`RECONSUME_LATER`后就会执行重试，在业务报错 返回null也会执行重试。

**重试时间**：

> 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h

 第一次10s  ....  如果重试了16次(**默认重试16次**)，那么这个消息就会被终止发送给消费者，传递到死信队列。

**例**：

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("retry-consumer-group");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        // 订阅一个主题来消费   表达式，默认是*,支持"tagA || tagB || tagC" 这样或者的写法 只要是符合任何一个标签都可以消费
        consumer.subscribe("RetryTopicTest","tagA || tagB || tagC");
        // 设定重试次数 重试的次数一般 5次
        consumer.setMaxReconsumeTimes(5);
        consumer.registerMessageListener(new MessageListenerConcurrently() {
            @Override
            public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> list, ConsumeConcurrentlyContext consumeConcurrentlyContext) {
                try {
                    // 这里执行消费的代码
                    System.out.println(Thread.currentThread().getName() + "----" + list);
                    // 这里制造一个错误
                    int i = 10 / 0;
                } catch (Exception e) {
                    // 出现问题 判断重试的次数
                    MessageExt messageExt = list.get(0);
                    // 获取重试的次数 失败一次消息中的失败次数会累加一次
                    int reconsumeTimes = messageExt.getReconsumeTimes();
                    // 第四次会把消息确认
                    if (reconsumeTimes >= 3) {
                        // 则把消息确认了，可以将这条消息记录到日志或者数据库 通知人工处理
                        return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
                    } else {
                        return ConsumeConcurrentlyStatus.RECONSUME_LATER;
                    }
                }
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
            }
        });
        consumer.start();
        System.in.read();
    }
}
```

![image-20240323165902896](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403231659991.png)

