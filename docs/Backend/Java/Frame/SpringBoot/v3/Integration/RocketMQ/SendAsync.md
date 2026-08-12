# 发送异步消息

异步消息通常用在对响应时间敏感的业务场景，即发送端不能容忍长时间地等待Broker的响应。发送完以后会有一个异步消息通知

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
     * 发送异步消息
     * @throws IOException
     */
    @Test
    public void testAsyncSend() throws IOException {
        // 发送异步消息，发送完以后会有一个异步通知
        rocketMQTemplate.asyncSend("AsyncTopicTest", "发送一个异步消息", new SendCallback() {
            /**
             * 成功的回调
             * @param sendResult
             */
            @Override
            public void onSuccess(SendResult sendResult) {
                System.out.println("发送成功");
            }

            /**
             * 失败的回调
             * @param throwable
             */
            @Override
            public void onException(Throwable throwable) {
                System.out.println("发送失败");
            }
        });
        // 测试一下异步的效果
        System.out.println("谁先执行");
        // 挂起jvm 不让方法结束
        System.in.read();
    }
}
```

运行后查看控制台：

![image-20240324162609683](assets/img202403241626660.png)

查看RocketMQ的控制台：

![image-20240324163206911](assets/img202403241632299.png)

查看消息的细节：

![image-20240324163237090](assets/img202403241632628.png)

## 消费者

```java
/**
 * 创建一个简单消息的监听
 * 1. 类上添加注解@Component和@RocketMQMessageListener
 * RocketMQMessageListener(topic = "SimpleTopicTest", consumerGroup = "simple-consumer-group")
 *      topic指定消费的主题，consumerGroup指定消费组,一个主题可以有多个消费者组,一个消息可以被多个不同的组的消费者都消费
 * 2. 实现RocketMQListener接口，注意泛型的使用，可以为具体的类型，如果想拿到消息的其他参数可以写成MessageExt
 * @author hjc
 */
@Component
@RocketMQMessageListener(topic = "AsyncTopicTest",consumerGroup = "async-consumer-group")
public class AsyncMsgListener implements RocketMQListener<MessageExt> {
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

![image-20240324163922478](assets/img202403241639434.png)
