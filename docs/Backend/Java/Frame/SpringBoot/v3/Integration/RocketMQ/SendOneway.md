# 发送单向消息

发送单向消息主要用在不关心发送结果的场景，这种方式吞吐量很大，但是存在消息丢失的风险，例如日志信息的发送

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
     * 发送单向消息
     */
    @Test
    public void testOnewaySend(){
        // 发送单向消息，没有返回值和结果
        rocketMQTemplate.sendOneWay("OnewayTopicTest","我是一个单向消息");
        System.out.println("执行完毕");
    }
}
```

运行后查看控制台：

![image-20240324170746555](assets/img202403241707010.png)

查看RocketMQ的控制台：

![image-20240324171017135](assets/img202403241710522.png)

查看消息的细节：

![image-20240324171044934](assets/img202403241710861.png)

## 消费者

```java
/**
 * 创建一个简单消息的监听
 * 1. 类上添加注解@Component和@RocketMQMessageListener
 * RocketMQMessageListener(topic = "SimpleTopicTest", consumerGroup = "simple-consumer-group")
 *      topic指定消费的主题，consumerGroup指定消费组,一个主题可以有多个消费者组,一个消息可以被多个不同的组的消费者都消费
 * 2. 实现RocketMQListener接口，注意泛型的使用，可以为具体的类型，如果想拿到消息的其他参数可以写成MessageExt
 */
@Component
@RocketMQMessageListener(topic = "OnewayTopicTest",consumerGroup = "oneway-consumer-group")
public class OnewayMsgListener implements RocketMQListener<MessageExt> {
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

![image-20240324171235756](assets/img202403241717717.png)
