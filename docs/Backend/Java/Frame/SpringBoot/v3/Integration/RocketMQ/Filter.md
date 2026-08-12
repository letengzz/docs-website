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

从源码注释得知，tag带在主题后面用`:`来携带：

![image-20240324221150661](assets/img202403242211518.png)

```java
@SpringBootTest
class Producer {


    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 发送带标签(Tag)的消息
     */
    @Test
    public void testTagMsg(){
        // 发送一个tag为tagA的数据
        SendResult sendResult = rocketMQTemplate.syncSend("TagTopicTest:tagA", "我是一个带标记的消息A");
        System.out.println(sendResult.getSendStatus());
    }
}
```

运行结果：

![image-20240324225409185](assets/img202403242254169.png)

### 消费者

```java
/**
 * 创建一个简单的标签消息的监听
 * 1.类上添加注解@Component和@RocketMQMessageListener
 *      selectorType = SelectorType.TAG,  指定使用tag过滤。(也可以使用sql92 需要在配置文件broker.conf中开启enbalePropertyFilter=true)
 *      selectorExpression = "tagA"     表达式，默认是*,支持"tag1 || tag2 || tag3"
 * 2.实现RocketMQListener接口，注意泛型的使用
 */
@Component
@RocketMQMessageListener(topic = "TagTopicTest",
        consumerGroup = "tag-consumer-group",
        selectorType = SelectorType.TAG,
        selectorExpression = "tagA"
)
public class TagMsgListener implements RocketMQListener<String> {

    /**
     * 消费消息的方法
     *
     * @param message
     */
    @Override
    public void onMessage(String message) {
        System.out.println(message);
    }
}
```

运行结果：

![image-20240324231944541](assets/img202403242319161.png)

## 发送带key的消息

在RocketMQ中的消息，默认会有一个messageId当做消息的唯一标识，可以给消息携带一个key，用作唯一标识或者业务标识，包括在控制面板查询的时候也可以使用messageId或者key来进行查询

![](assets/img202403200004263.png)

### 生产者

在 `org.apache.rocketmq.spring.support.RocketMQUtil` 的`getAndWrapMessage()`方法里面看到了具体细节，keys在消息头里面携带：

![image-20240324221537525](assets/img202403242215189.png)

```java
@SpringBootTest
class Producer {

    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 发送一个带key的消息,我们使用事务消息 打断点查看消息头
     *
     * @throws Exception
     */
    @Test
    public void testKeyMsg() throws Exception {
        // 发送一个带有key的消息
        //key 要确保唯一 为了查阅和去重
        String uuid = UUID.randomUUID().toString();
        System.out.println("uuid = " + uuid);
        Message<String> message = MessageBuilder.withPayload("我是一个带key的消息")
                .setHeader(RocketMQHeaders.KEYS, uuid)
                .build();
        SendResult sendResult = rocketMQTemplate.syncSend("KeyTopicTest", message);
        System.out.println("sendResult = " + sendResult);
    }
}
```

运行结果：

![image-20240324233232060](assets/img202403242332111.png)

### 消费者

```java
/**
 * 创建一个简单消息的监听
 * 1. 类上添加注解@Component和@RocketMQMessageListener
 * RocketMQMessageListener(topic = "SimpleTopicTest", consumerGroup = "simple-consumer-group")
 *      topic指定消费的主题，consumerGroup指定消费组,一个主题可以有多个消费者组,一个消息可以被多个不同的组的消费者都消费
 * 2. 实现RocketMQListener接口，注意泛型的使用，可以为具体的类型，如果想拿到消息的其他参数可以写成MessageExt
 */
@Component
@RocketMQMessageListener(topic = "KeyTopicTest",consumerGroup = "key-consumer-group")
public class KeyMsgListener implements RocketMQListener<MessageExt> {
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
        System.out.println(new String(messageExt.getKeys()));
        System.out.println(new String(messageExt.getBody()));
    }
}
```

运行结果：

![image-20240324233333928](assets/img202403242333678.png)

### 查看效果

![image-20240324233451076](assets/img202403242334090.png)
