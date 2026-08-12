# 创建基础项目

使用SpringBoot创建项目。

## 生产者

导入依赖：

```xml
<dependencies>
	<dependency>
    	<groupId>org.apache.rocketmq</groupId>
        <artifactId>rocketmq-spring-boot-starter</artifactId>
        <version>2.3.0</version>
    </dependency>
</dependencies>
```

修改配置文件：

```yaml
spring:
  application:
    name: rocketmq-producer
rocketmq:
  name-server: 127.0.0.1:9876 # rocketMq的nameServer地址
  producer:
    group: producer-group # 生产者组别
    send-message-timeout: 3000 # 消息发送的超时时间 默认3000ms

    max-message-size: 4194304 # 消息的最大长度 默认为128K
    #消息达到4096字节的时候，消息就会被压缩。默认 4096
    compress-message-body-threshold: 4096
    #同步消息发送失败重试次数
    retry-times-when-send-failed: 3
    #在内部发送失败时是否重试其他代理，这个参数在有多个broker时才生效
    retry-next-server: true
    #异步消息发送失败重试的次数
    retry-times-when-send-async-failed: 3
```

往SimpleTopicTest主题里面发送一个简单的字符串消息：

```java
@SpringBootTest
public class Producer {

    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 测试发送简单的消息
     *
     * @throws Exception
     */
    @Test
    public void testSimpleMsg(){
        // 往simpleTopicTest的主题里面发送一个简单的字符串消息
        SendResult sendResult = rocketMQTemplate.syncSend("SimpleTopicTest", "我是一个简单的消息");
        // 拿到消息的发送状态
        System.out.println(sendResult.getSendStatus());
        // 拿到消息的id
        System.out.println(sendResult.getMsgId());
    }
}
```

运行后查看控制台：

![image-20240324142054258](assets/img202403241420952.png)

查看RocketMQ的控制台：

![image-20240324142108346](assets/img202403241421771.png)

查看消息的细节：

![image-20240324142142483](assets/img202403241421010.png)

## 消费者

导入依赖：

```xml
<dependencies>
	<dependency>
    	<groupId>org.apache.rocketmq</groupId>
        <artifactId>rocketmq-spring-boot-starter</artifactId>
        <version>2.3.0</version>
    </dependency>
</dependencies>
```

修改配置文件：

```yaml
spring:
  application:
    name: rocketmq-consumer
rocketmq:
  name-server: 127.0.0.1:9876 # rocketMq的nameServer地址
```

编写监听类：

```java
/**
 * 创建一个简单消息的监听
 * 1. 类上添加注解@Component和@RocketMQMessageListener
 * @RocketMQMessageListener(topic = "SimpleTopicTest", consumerGroup = "simple-consumer-group")
 *      topic指定消费的主题，consumerGroup指定消费组,一个主题可以有多个消费者组,一个消息可以被多个不同的组的消费者都消费
 * 2. 实现RocketMQListener接口，注意泛型的使用，可以为具体的类型，如果想拿到消息的其他参数可以写成MessageExt
 */
@Component
@RocketMQMessageListener(topic = "SimpleTopicTest",
        consumerGroup = "simple-consumer-group")
public class SimpleMsgListener implements RocketMQListener<MessageExt> {
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
        System.out.println(new String(messageExt.getBody()));
    }
}
```

启动 rocketmq-consumer，运行结果：查看控制台，发现已经监听到消息了

![image-20240324143201101](assets/img202403241432931.png)
