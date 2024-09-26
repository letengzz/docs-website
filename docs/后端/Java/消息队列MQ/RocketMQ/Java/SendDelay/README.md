# 发送延迟消息

消息放入mq后，过一段时间，才会被监听到，然后消费

比如下订单业务，提交了一个订单就可以发送一个延时消息，30min后去检查这个订单的状态，如果还是未付款就取消订单释放库存。

注意：RocketMQ不支持任意时间的延时 只支持几个固定的延时等级，等级1就对应1s，以此类推，最高支持2h延迟

```java
private String messageDelayLevel = "1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h";
```

## 生产者

```java
public class Producer {
    public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
        //创建默认的生产者
        DefaultMQProducer producer = new DefaultMQProducer("delay-send-producer");
        //设置nameServer地址
        producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //启动实例
        producer.start();

        Message message = new Message("DelayTopicTest","延迟消息".getBytes());
        //给这个消息设定一个延迟等级
        // messageDelayLevel = "1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h
        message.setDelayTimeLevel(3);
        //发送单向消息
        producer.send(message);
        //打印时间
        System.out.println("发送时间："+new Date());
        //关闭实例
        producer.shutdown();
    }
}
```

启动生产者进行测试：

![image-20240318233848443](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403182338539.png)

## 消费者

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("delay-consumer-test");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //订阅一个主题来消费  *表示没有过滤参数 表示这个主题的任何消息
        consumer.subscribe("DelayTopicTest","*");
        consumer.registerMessageListener(new MessageListenerConcurrently() {
            @Override
            public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> list, ConsumeConcurrentlyContext consumeConcurrentlyContext) {
                System.out.println("收到消息:"+new Date());
                System.out.println(new String(list.get(0).getBody()));
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

![image-20240318234115561](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403182341175.png)