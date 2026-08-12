# 发送对象消息

## 实体类

```java
/**
 * 订单对象
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Order {
    /**
     * 订单号
     */
    private String orderId;

    /**
     * 订单名称
     */
    private String orderName;

    /**
     * 订单价格
     */
    private Double price;

    /**
     * 订单号创建时间
     */
    private Date createTime;

    /**
     * 订单描述
     */
    private String desc;

}
```

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
     * 测试发送对象消息
     *
     * @throws Exception
     */
    @Test
    public void testObjectMsg() throws Exception {
        Order order = new Order();
        order.setOrderId(UUID.randomUUID().toString());
        order.setOrderName("我的订单");
        order.setPrice(998D);
        order.setCreateTime(new Date());
        order.setDesc("加急配送");
        // 往ObjectTopicTest主题发送一个订单对象
        rocketMQTemplate.syncSend("ObjectTopicTest", order);
    }
}
```

## 消费者

```java
/**
 * 创建一个对象消息的监听
 * 1.类上添加注解@Component和@RocketMQMessageListener
 * 2.实现RocketMQListener接口，注意泛型的使用
 */
@Component
@RocketMQMessageListener(topic = "ObjectTopicTest",
        consumerGroup = "object-consumer-group")
public class ObjectMsgListener implements RocketMQListener<Order> {
    /**
     * 消费消息的方法
     * 如果泛型指定了固定的类型 那么消息体就是参数
     * MessageExt 类型是消息的所有内容
     * 如果没有报错 就签收了
     * 如果报错了 就是拒收 就会重试
     * @param order
     */
    @Override
    public void onMessage(Order order) {
        System.out.println(order);
    }
}
```

![image-20240329224222408](assets/img202403292242257.png)
