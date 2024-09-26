# RocketMQ 重复消费问题

RocketMQ 确保所有消息至少传递一次。 在大多数情况下，消息不会重复。

但是RocketMQ无法避免消息重复 (`Exactly-Once`)，所以如果业务对消费重复非常敏感，务必要在业务层面进行去重处理。

- 广播(`BROADCASTING`)模式下，所有注册的消费者都会消费，而这些消费者通常是集群部署的一个个微服务，这样就会多台机器重复消费，当然这个是根据需要来选择。

- 负载均衡(`CLUSTERING`)模式下，如果一个topic被多个consumerGroup消费，也会重复消费。

即使是在CLUSTERING模式下，同一个consumerGroup下，一个队列只会分配给一个消费者，看起来好像是不会重复消费。但是，有个特殊情况：一个消费者新上线后，同组的所有消费者要重新负载均衡，反之一个消费者掉线后也一样。一个队列所对应的新的消费者要获取之前消费的offset (偏移量，也就是消息消费的点位)，此时之前的消费者可能已经消费了一条消息，但是并没有把offset提交给broker，那么新的消费者可能会重新消费一次。虽然orderly模式是前一个消费者先解锁，后一个消费者加锁再消费的模式，比起concurrently要严格了，但是加锁的线程和提交offset的线程不是同一个，所以还是会出现极端情况下的重复消费。

在发送批量消息的时候，会被当做一条消息进行处理，那么如果批量消息中有一条业务处理成功，其他失败了，还是会被重新消费一次。

如果在负载均衡(`CLUSTERING`)模式下，并且在同一个消费者组中，不希望一条消息被重复消费，可以使用去重操作，找到消息唯一的标识，可以是msgId也可以是你自定义的唯一的key，这样就可以去重了

msgId一定是全局唯一标识符，但是实际使用中，可能会存在相同的消息有两个不同msgId的情况（消费者主动重发、因客户端重投机制导致的重复等），这种情况就需要使业务字段进行重复消费。

**官方文档**：https://rocketmq.apache.org/zh/docs/bestPractice/01bestpractice#%E6%B6%88%E8%B4%B9%E8%BF%87%E7%A8%8B%E5%B9%82%E7%AD%89

## 解决方案

使用去重方案解决，例如将消息的唯一标识存起来，然后每次消费之前先判断是否存在这个唯一标识，如果存在则不消费，如果不存在则消费，并且消费以后将这个标记保存，从而保证消息的幂等性(幂等性：多次操作产生的影响和第一次操作产生的影响相同)。

### 使用布隆过滤器解决问题

消息的体量是非常大的，可能在生产环境中会到达上千万甚至上亿条，可以选择布隆过滤器来保存所有消息的标识，并且又可以快速的判断是否存在

布隆过滤器 (`Bloom Filter`) 是1970年由布隆提出的。它实际上是一个很长的二进制向量和一系列随机映射函数。布隆过滤器可以用于检索一个元素是否在一个集合中。

- **优点**：空间效率和查询时间都比一般的算法要好的多
- **缺点**：有一定的误识别率和删除困难。

#### 使用hutool工具

https://hutool.cn/docs/#/bloomFilter/%E6%A6%82%E8%BF%B0

1. 添加hutool的依赖：

   ```xml
   <dependency>
       <groupId>cn.hutool</groupId>
       <artifactId>hutool-all</artifactId>
       <version>5.7.11</version>
   </dependency>
   ```

2. 编写生产者：

   ```java
   public class Producer {
   
       public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
           // 创建默认的生产者
           DefaultMQProducer producer = new DefaultMQProducer("repeat-hutool-producer-group");
           //设置nameServer地址
           producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
           //启动生产者
           producer.start();
           //生成唯一id
           String key = UUID.randomUUID().toString();
           //创建消息
           //第一个参数：主题的名字
           //第二个参数：消息内容
           //发两个同样的消息模拟重复消费
           Message m1 = new Message("repeatTopic", null, key, "扣减库存-1".getBytes());
           Message m1Repeat = new Message("repeatTopic", null, key, "扣减库存-1".getBytes());
   
           producer.send(m1);
           producer.send(m1Repeat);
           System.out.println("发送消息成功");
           //关闭实例
           producer.shutdown();
       }
   }
   ```

3. 编写消费者：

   ```java
   public class Consumer {
       public static BitMapBloomFilter bloomFilter = new BitMapBloomFilter(100);
   
       public static void main(String[] args) throws MQClientException, IOException {
           // 创建默认消费者组
           DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("repeat-hutool-consumer-group");
           consumer.setMessageModel(MessageModel.BROADCASTING);
           // 设置nameServer地址
           consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
           // 订阅一个主题来消费   表达式，默认是*
           consumer.subscribe("repeatTopic", "*");
           // 注册一个消费监听 MessageListenerConcurrently是并发消费
           // 默认是20个线程一起消费，可以参看 consumer.setConsumeThreadMax()
           consumer.registerMessageListener(new MessageListenerConcurrently() {
               @Override
               public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs,
                                                               ConsumeConcurrentlyContext context) {
                   // 拿到消息的key
                   MessageExt messageExt = msgs.get(0);
                   String keys = messageExt.getKeys();
                   // 判断是否存在布隆过滤器中
                   if (bloomFilter.contains(keys)) {
                       // 直接返回了 不往下处理业务
                       System.out.println("该消息已经来过了");
                       return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
                   }
                   // 这个处理业务，然后放入过滤器中
                   // do sth...
                   System.out.println(new String(messageExt.getBody()));
                   bloomFilter.add(keys);
                   return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
               }
           });
           consumer.start();
           System.in.read();
       }
   }
   ```

4. 查看效果：

   ![image-20240327222409080](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403272224316.png)

#### 使用redis的bitmap类型手写布隆过滤器



### 使用数据库解决问题

可以借助关系数据库进行去重。首先需要确定消息的唯一键，可以是msgId，也可以是消息内容中的唯一标识字段，例如订单Id等。在消费之前判断唯一键是否在关系数据库中存在。如果不存在则插入，并消费，否则跳过。
实际过程要考虑原子性问题，判断是否存在可以尝试插入，如果报主键冲突，则插入失败，直接跳过(普通插入是非幂等性，有唯一索引的新增是幂等的)

- 数据库操作，添加去重表：

  ```sql
  CREATE TABLE `order_oper_log` (
    `id` int NOT NULL AUTO_INCREMENT,
    `type` int DEFAULT NULL,
    `order_sn` varchar(255) DEFAULT NULL,
    `user` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `order_sn_idx` (`order_sn`) USING BTREE
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
  ```

- 导入依赖：

  ```xml
  <dependency>
      <groupId>mysql</groupId>
      <artifactId>mysql-connector-java</artifactId>
  	<version>8.0.33</version>
  </dependency>
  ```

- 生产者：

  ```java
  public class Producer {
  
      public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
          // 创建默认的生产者
          DefaultMQProducer producer = new DefaultMQProducer("repeat-mysql-producer-group");
          //设置nameServer地址
          producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
          //启动生产者
          producer.start();
          //生成唯一id
          String key = UUID.randomUUID().toString();
          //创建消息
          //第一个参数：主题的名字
          //第二个参数：消息内容
          //发两个同样的消息模拟重复消费
          Message m1 = new Message("repeatTopic", null, key, "扣减库存-1".getBytes());
          Message m1Repeat = new Message("repeatTopic", null, key, "扣减库存-1".getBytes());
  
          producer.send(m1);
          producer.send(m1Repeat);
          System.out.println("发送消息成功");
          //关闭实例
          producer.shutdown();
      }
  }
  ```

- 消费者：

  ```java
  public class Consumer {
      public static void main(String[] args) throws MQClientException, IOException {
          //创建默认消费者组
          DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("repeat-mysql-consumer-group");
          //设置nameServer地址
          consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
          //订阅一个主题来消费  *表示没有过滤参数 表示这个主题的任何消息
          consumer.subscribe("repeatTopic", "*");
          consumer.registerMessageListener(new MessageListenerConcurrently() {
              @Override
              public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> list, ConsumeConcurrentlyContext consumeConcurrentlyContext) {
                  //拿到key
                  MessageExt messageExt = list.get(0);
                  String keys = messageExt.getKeys();
                  System.out.println(keys);
                  //新增 成功或报错 修改 成功或失败或报错
                  //插入数据库 因为做了唯一索引
                  //原生操作
                  Connection connection = null;
                  try {
                      connection = DriverManager.getConnection("jdbc:mysql://localhost:3306/rocket?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai&useSSL=false", "root", "123123");
                      PreparedStatement statement = connection.prepareStatement("insert into order_oper_log(`type`,`order_sn`,`user`) values (1,'" + keys + "','123')");
                      int i = statement.executeUpdate();
                  } catch (SQLException e) {
                      if (e instanceof SQLIntegrityConstraintViolationException) {
                          //唯一索引冲突异常 说明消息已经来过了
                          System.out.println("该消息已经来过了");
                          return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
                      }
                      e.printStackTrace();
                  }
  
                  //处理业务逻辑
                  //如果业务逻辑报错需要删除掉去重表记录
                  System.out.println(new String(messageExt.getBody()));
                  return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
              }
          });
          // 这个start一定要写在registerMessageListener下面
          consumer.start();
          // 由于是异步回调方式，挂起当前的jvm
          System.in.read();
      }
  }
  ```
  
- 查看效果：

  ![image-20240323161851436](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403231619004.png)