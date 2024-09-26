# 发送顺序消息

消息有序指的是可以按照消息的发送顺序来消费(FIFO)。RocketMQ可以严格的保证消息有序，可以分为：分区有序或者全局有序。

RocketMQ的broker的机制，导致了RocketMQ会有这个问题 因为一个broker中对应了四个queue

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403172013509.png)

**顺序消费的原理**：在默认的情况下消息发送会采取Round Robin轮询方式把消息发送到不同的queue(分区队列)；而消费消息的时候从多个queue上拉取消息，这种情况发送和消费是不能保证顺序。但是如果控制发送的顺序消息只依次发送到同一个queue中，消费的时候只从这个queue上依次拉取，则就保证了顺序。当发送和消费参与的queue只有一个，则是全局有序；如果多个queue参与，则为分区有序，即相对每个queue，消息都是有序的。

用订单进行分区有序的示例：

- 一个订单的顺序流程是：下订单、发短信通知、物流、签收。订单顺序号相同的消息会被先后发送到同一个队列中，消费时，同一个顺序获取到的肯定是同一个队列。

- 模拟一个订单的发送流程，创建两个订单，发送的消息分别是

  - 订单号111 消息流程 下订单->物流->签收
  - 订单号112 消息流程 下订单->物流->拒收

- 步骤：

  1. 创建订单对象

     > com.hjc.demo.domain.Order

     ```java
     @NoArgsConstructor
     @AllArgsConstructor
     @Data
     public class Order {
         /**
          * 订单id
          */
         private Integer orderId;
     
         /**
          * 订单编号
          */
         private Integer orderNumber;
     
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

  2. 顺序消息生产者

     ```java
     public class Producer {
         public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
             // 创建默认的生产者
             DefaultMQProducer producer = new DefaultMQProducer("orderly-send-producer");
             //设置nameServer地址
             producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
             //启动生产者
             producer.start();
     
             List<Order> orderList = Arrays.asList(
                     new Order(1, 111, 59D, new Date(), "下订单"),
                     new Order(2, 111, 59D, new Date(), "物流"),
                     new Order(3, 111, 59D, new Date(), "签收"),
                     new Order(4, 112, 89D, new Date(), "下订单"),
                     new Order(5, 112, 89D, new Date(), "物流"),
                     new Order(6, 112, 89D, new Date(), "拒收")
     
             );
             //循环集合开始发送
             //发送顺序消息  发送时要确保有序 并且要发到同一个队列下面去
             orderList.forEach(order -> {
                 Message message = new Message("OrderTopicTest", order.toString().getBytes());
                 try {
                     // 送的时候 相同的订单号选择同一个队列
                     producer.send(message, new MessageQueueSelector() { //队列选择器
                         @Override
                         public MessageQueue select(List<MessageQueue> list, Message message, Object o) {
                             // 当前主题有多少个队列
                             int queueNumber = list.size();
                             // 这个arg就是后面传入的 order.getOrderNumber()
                             Integer i = (Integer) o;
                             // 用这个值去%队列的个数得到一个队列
                             // 2 % 4 =2
                             // 3 % 4 =3
                             // 4 % 4 =0
                             // 5 % 4 =1
                             // 6 % 4 =2  周期性函数
                             int index = i % queueNumber;
                             // 返回选择的这个队列即可 ，那么相同的订单号 就会被放在相同的队列里 实现FIFO了
                             return list.get(index);
                         }
                     },order.getOrderNumber() /*参数*/);
                 }catch (Exception e){
                     System.out.println("发送异常");
                 }
             });
     
             //关闭实例
             producer.shutdown();
             System.out.println("发送完成");
         }
     }
     ```

     ![image-20240319134014174](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403191340476.png)

  3. 顺序消息消费者：测试时等一会即可有延迟

     ```java
     public class Consumer {
         public static void main(String[] args) throws MQClientException, IOException {
             //创建默认消费者组
             DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("orderly-consumer-group");
             //设置nameServer地址
             consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
             //订阅一个主题来消费  *表示没有过滤参数 表示这个主题的任何消息
             consumer.subscribe("OrderTopicTest","*");
             // MessageListenerConcurrently 并发模式 多线程的  重试16次
             // MessageListenerOrderly 顺序模式 单线程的   无限重试Integer.Max_Value
             // 注册一个消费监听 MessageListenerOrderly 是顺序消费 单线程消费
             consumer.registerMessageListener(new MessageListenerOrderly() {
                 @Override
                 public ConsumeOrderlyStatus consumeMessage(List<MessageExt> list, ConsumeOrderlyContext consumeOrderlyContext) {
                     System.out.println("线程id:" + Thread.currentThread().getId());
                     System.out.println(new String(list.get(0).getBody()));
                     return ConsumeOrderlyStatus.SUCCESS;
                 }
             });
             // 这个start一定要写在registerMessageListener下面
             consumer.start();
             // 挂起当前的jvm
             System.in.read();
         }
     }
     ```

     ![image-20240319135217765](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403191352348.png)
