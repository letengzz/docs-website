# RocketMQ 消息不丢失

**方式一**：

1. 生产者使用同步发送模式 ，收到mq的返回确认以后  顺便往自己的数据库里面写入 `msgId`、`status`(0)、`time`

2. 消费者消费以后，修改数据这条消息的状态 = 1

3. 写一个定时任务，间隔两天去查询数据  如果有`status = 0 and time < day-2`数据进行补发，结合幂等性操作控制重复问题

**方式二**：

1. 将mq的刷盘机制设置为同步刷盘 (由于消息放到broker，broker放入到磁盘后，返回给生产者确认信息，但是性能不高，每次都进行磁盘IO操作)
2. 使用集群模式 ，搞主备模式，将消息持久化在不同的硬件上

**方式三**：

1. 可以开启MQ的trace机制，消息跟踪机制

   - 在broker.conf中开启消息追踪 `traceTopicEnable=true`，重启broker即可

     ```sh
     traceTopicEnable=true
     ```

   - 生产者配置文件开启消息轨迹 `enable-msg-trace: true`

     > SpringBoot

     ```yaml
     enable-msg-trace: true
     ```

     > Java

     ```java
     DefaultMQProducer producer = new DefaultMQProducer("test-producer-group",true);
     ```

   - 消费者开启消息轨迹功能，可以给单独的某一个消费者开启`enableMsgTrace = true`

     > SpringBoot

     ```sh
     enableMsgTrace = true
     ```

     > Java

     ```java
     DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("consumer_group",true);
     ```

在RocketMQ的面板中可以查看消息轨迹：默认会将消息轨迹的数据存在 `RMQ_SYS_TRACE_TOPIC` 主题里面

![image-20240326235012794](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403262350925.png)
