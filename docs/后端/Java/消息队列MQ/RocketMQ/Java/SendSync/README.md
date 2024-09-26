# 发送同步消息

发送同步消息，发送过后会有一个返回值，也就是mq服务器接收到消息后返回的一个确认，这种方式非常安全，但是性能上并没有这么高，而且在mq集群中，也是要等到所有的从机都复制了消息以后才会返回，所以针对重要的消息可以选择这种方式

消息由消费者发送到broker后，会得到一个确认，是具有可靠性的。这种可靠性同步地发送方式使用的比较广泛，比如：重要的消息通知，短信通知等。

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403172015667.jpg)

## 生产者

```java
public class Producer {
    public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
        // 创建默认的生产者
        DefaultMQProducer producer = new DefaultMQProducer("sync-send-producer");
        //设置nameServer地址
        producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //启动生产者
        producer.start();

        for (int i = 0; i < 10; i++) {
            //创建消息
            //第一个参数：主题的名字
            //第二个参数：消息内容
            Message msg = new Message("SyncTopicTest", ("同步消息-" + i).getBytes());
            SendResult send = producer.send(msg);
            System.out.println("send = " + send);
        }
        //关闭实例
        producer.shutdown();
    }
}
```

启动生产者进行测试：

![image-20240318230028805](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403182300863.png)

## 消费者

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("sync-consumer-test");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //订阅一个主题来消费  *表示没有过滤参数 表示这个主题的任何消息
        consumer.subscribe("SyncTopicTest","*");
        //注册一个消费监听 MessageListenerConcurrently 是多线程消费，默认20个线程
        // 可以参看consumer.setConsumeThreadMax()
        consumer.registerMessageListener(new MessageListenerConcurrently() {
            @Override
            public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> list, ConsumeConcurrentlyContext consumeConcurrentlyContext) {
                System.out.println(Thread.currentThread().getName() + "----" + list);
                System.out.println("消息内容:"+new String(list.get(0).getBody()));
                System.out.println("消费上下文:"+consumeConcurrentlyContext);
                // 返回消费的状态 如果是CONSUME_SUCCESS 则成功，若为RECONSUME_LATER则该条消息会被重回队列，重新被投递
                // 重试的时间为messageDelayLevel = "1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h
                // 也就是第一次1s 第二次5s 第三次10s  ....  如果重试了16次 那么这个消息就会被终止发送给消费者
                // 返回状态：
                // CONSUME_SUCCESS：成功 消息会从mq出队
                // RECONSUME_LATER：失败(报错、null) 消息会重新回到队列 过一会重新投递出来 给当前消费者或者其他消费者消费的
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
                // return ConsumeConcurrentlyStatus.RECONSUME_LATER;
            }
        });
        // 这个start一定要写在registerMessageListener下面
        consumer.start();
        // 由于是异步回调方式，挂起当前的jvm
        System.in.read();

    }
}
```

启动消费者进行测试：

![image-20240318230127620](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403182301790.png)
