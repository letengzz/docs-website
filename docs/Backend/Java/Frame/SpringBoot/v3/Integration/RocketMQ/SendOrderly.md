# 发送顺序消息

消息有序指的是可以按照消息的发送顺序来消费(FIFO)。RocketMQ可以严格的保证消息有序，可以分为：分区有序或者全局有序。

RocketMQ的broker的机制，导致了RocketMQ会有这个问题 因为一个broker中对应了四个queue

![img](assets/img202403172013509.png)

**顺序消费的原理**：在默认的情况下消息发送会采取Round Robin轮询方式把消息发送到不同的queue(分区队列)；而消费消息的时候从多个queue上拉取消息，这种情况发送和消费是不能保证顺序。但是如果控制发送的顺序消息只依次发送到同一个queue中，消费的时候只从这个queue上依次拉取，则就保证了顺序。当发送和消费参与的queue只有一个，则是全局有序；如果多个queue参与，则为分区有序，即相对每个queue，消息都是有序的。

用订单进行分区有序的示例：

- 一个订单的顺序流程是：下订单、发短信通知、物流、签收。订单顺序号相同的消息会被先后发送到同一个队列中，消费时，同一个顺序获取到的肯定是同一个队列。

- 模拟一个订单的发送流程，创建两个订单，发送的消息分别是

  - 订单号111 消息流程 下订单->物流->签收
  - 订单号112 消息流程 下订单->物流->拒收

- 步骤：

  1. 创建订单对象：

     ```java [com.hjc.demo.domain.Order]
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

         /**
          * 订单的流程顺序
          */
         private Integer seq;

     }
     ```

  2. 顺序消息生产者：

     ```java
     @SpringBootTest
     class Producer {


         /**
          * 注入rocketMQTemplate，使用它来操作mq
          */
         @Resource
         private RocketMQTemplate rocketMQTemplate;

         /**
          * 发送顺序消息
          */
         @Test
         public void testOrderlySend(){
             List<Order> orders = Arrays.asList(
                     new Order(UUID.randomUUID().toString().substring(0, 5), "张三的下订单", null, null, null, 1),
                     new Order(UUID.randomUUID().toString().substring(0, 5), "张三的发短信", null, null, null, 1),
                     new Order(UUID.randomUUID().toString().substring(0, 5), "张三的物流", null, null, null, 1),
                     new Order(UUID.randomUUID().toString().substring(0, 5), "张三的签收", null, null, null, 1),
                     new Order(UUID.randomUUID().toString().substring(0, 5), "李四的下订单", null, null, null, 2),
                     new Order(UUID.randomUUID().toString().substring(0, 5), "李四的发短信", null, null, null, 2),
                     new Order(UUID.randomUUID().toString().substring(0, 5), "李四的物流", null, null, null, 2),
                     new Order(UUID.randomUUID().toString().substring(0, 5), "李四的签收", null, null, null, 2)
             );
             orders.forEach(order -> {
                 SendResult sendResult = rocketMQTemplate.syncSendOrderly("OrderlyTopicTest", JSON.toJSONString(order), String.valueOf(order.getSeq()));
                 System.out.println(sendResult);
             });
         }
     }
     ```

     ![image-20240324190038528](assets/img202403241900142.png)

     运行后查看控制台：

     ![image-20240324191536654](assets/img202403241915888.png)

  3. 顺序消息消费者：测试时等一会即可有延迟

     ```java
     import com.hjc.demo.domain.Order;
     /**
      * 创建一个对象消息的监听
      * 1.类上添加注解@Component和@RocketMQMessageListener
      * 2.实现RocketMQListener接口，注意泛型的使用
      * consumeMode 指定消费类型
      * CONCURRENTLY 并发消费
      * ORDERLY 顺序消费 messages orderly. one queue, one thread
      */
     @Component
     @RocketMQMessageListener(topic = "OrderlyTopicTest",
             consumerGroup = "orderly-consumer-group",
             consumeMode = ConsumeMode.ORDERLY)
     public class OrderlyMsgListener implements RocketMQListener<Order> {

         /**
          * 消费消息的方法
          *
          * @param order
          */
         @Override
         public void onMessage(Order order) {
             System.out.println(order);
         }
     }
     ```

     启动 rocketmq-consumer，运行结果：查看控制台，发现已经监听到消息了

     ![image-20240324191645218](assets/img202403241916906.png)
