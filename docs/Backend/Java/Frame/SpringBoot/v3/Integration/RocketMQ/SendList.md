# 发送集合消息

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
     * 测试发送数组消息
     *
     * @throws Exception
     */
    @Test
    public void testListMsg() throws Exception {
        List<String> list = Arrays.asList("A", "B", "C");
        // 往ListTopicTest主题发送一个订单对象
        rocketMQTemplate.syncSend("ListTopicTest", list);
    }
}
```

## 消费者

:::danger 注意

修改泛型中的类型为Object即可

:::

```java
@Component
@RocketMQMessageListener(topic = "ListTopicTest",
        consumerGroup = "list-consumer-group")
public class ListMsgListener implements RocketMQListener<Object> {
    /**
     * 消费消息的方法
     * 如果泛型指定了固定的类型 那么消息体就是参数
     * MessageExt 类型是消息的所有内容
     * 如果没有报错 就签收了
     * 如果报错了 就是拒收 就会重试
     * @param object
     */
    @Override
    public void onMessage(Object object) {
        List<String> list = (List<String>) object;
        System.out.println(list);
    }
}
```

![image-20240329225529668](assets/img202411182232209.png)
