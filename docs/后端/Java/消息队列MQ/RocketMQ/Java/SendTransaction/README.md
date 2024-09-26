# 发送事务消息

## 事务消息的发送流程

事务消息可以被认为是一个两阶段的提交消息实现，以确保分布式系统的最终一致性。事务性消息确保本地事务的执行和消息的发送可以原子地执行。

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403192216672.png)

事务消息的大致分为两个流程：正常事务消息的发送及提交、事务消息的补偿流程：

- 事务消息发送及提交：
  1. 发送消息（half消息）
  2. 服务端响应消息写入结果
  3. 根据发送结果执行本地事务（如果写入失败，此时half消息对业务不可见，本地逻辑不执行）
  4. 根据本地事务状态执行Commit或Rollback（Commit操作生成消息索引，消息对消费者可见）

- 事务补偿：
  1. 对没有Commit/Rollback的事务消息 (pending状态的消息)，从服务端发起一次“回查”
  2. Producer收到回查消息，检查回查消息对应的本地事务的状态
  3. 根据本地事务状态，重新Commit或者Rollback
  4. 其中，补偿阶段用于解决消息UNKNOW或者Rollback发生超时或者失败的情况。


![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403192217004.png)

**事务消息共有三种状态**：提交状态、回滚状态、中间状态

- **提交事务** (`TransactionStatus.CommitTransaction`)：它允许消费者消费此消息。
- **回滚事务** (`TransactionStatus.RollbackTransaction`)：它代表该消息将被删除，不允许被消费。
- **中间状态** (`TransactionStatus.Unknown`)：它代表需要检查消息队列来确定状态。

## 生产者

```java
public class Producer {
    /**
     * TransactionalMessageCheckService的检测频率默认1分钟，可通过在broker.conf文件中设置transactionCheckInterval的值来改变默认值，单位为毫秒。
     * 从broker配置文件中获取transactionTimeOut参数值。
     * 从broker配置文件中获取transactionCheckMax参数值，表示事务的最大检测次数，如果超过检测次数，消息会默认为丢弃，即回滚消息。
     *
     */
    public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException, IOException {
        //创建一个事务消息生产者
        TransactionMQProducer producer = new TransactionMQProducer("transaction-producer-group");
        producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //设置事务消息监听器
        producer.setTransactionListener(new TransactionListener() {
            //执行本地业务方法
            @Override
            public LocalTransactionState executeLocalTransaction(Message message, Object o) {
                // 这个可以使用try catch对业务代码进行性包裹
                // COMMIT_MESSAGE 表示允许消费者消费该消息
                // ROLLBACK_MESSAGE 表示该消息将被删除，不允许消费
                // UNKNOW表示需要MQ回查才能确定状态 那么过一会 代码会走下面的checkLocalTransaction(msg)方法

                // TODO 执行业务代码（插入订单数据库表）
                // int i = orderDatabaseService.insert(....)
                // TODO 提交或回滚本地事务(如果用spring事务注解，这些都不需要手工去操作)

                // 模拟一个处理结果
//                int index = 5;
                //模拟返回事务状态
                switch ((int)o) {
                    case 3:
                        System.out.printf("本地事务回滚，回滚消息，id:%s%n", message.getKeys());
                        return LocalTransactionState.ROLLBACK_MESSAGE;
                    case 5:
                    case 8:
                        return LocalTransactionState.UNKNOW;
                    default:
                        System.out.println("事务提交，消息正常处理");
                        return LocalTransactionState.COMMIT_MESSAGE;
                }
            }

            // 这里是回查方法 回查不是再次执行业务操作，而是确认上面的操作是否有结果
            // 默认是1min回查 默认回查15次 超过次数则丢弃打印日志 可以通过参数设置
            // transactionTimeOut 超时时间
            // transactionCheckMax 最大回查次数
            // transactionCheckInterval 回查间隔时间单位毫秒
            // 触发条件:
            //   1.当上面执行本地事务返回结果UNKNOW时,或者下面的回查方法也返回UNKNOW时 会触发回查
            //   2.当上面操作超过20s没有做出一个结果，也就是超时或者卡住了，也会进行回查
            @Override
            public LocalTransactionState checkLocalTransaction(MessageExt messageExt) {
                // 根据业务，正确处理： 订单场景，只要数据库有了这条记录，消息应该被commit
                String transactionId = messageExt.getTransactionId();
                String key = messageExt.getKeys();
                System.out.printf("回查事务状态 key:%-5s msgId:%-10s transactionId:%-10s %n", key, messageExt.getMsgId(), transactionId);

                if ("id_5".equals(key)) { // 刚刚测试的10条消息， 把id_5这条消息提交，其他的全部回滚。
                    System.out.printf("回查到本地事务已提交，提交消息，id:%s%n", messageExt.getKeys());
                    return LocalTransactionState.COMMIT_MESSAGE;
                } else {
                    System.out.printf("未查到本地事务状态，回滚消息，id:%s%n", messageExt.getKeys());
                    return LocalTransactionState.ROLLBACK_MESSAGE;
                }
            }
        });
        producer.start();
        for (int i = 0; i < 10; i++) {
            String content = "Hello transaction message " + i;
            Message message = new Message("TransactionTopicTest", "TagA", "id_" + i, content.getBytes(RemotingHelper.DEFAULT_CHARSET));

            // 发送消息(发送一条新订单生成的通知)
            SendResult result = producer.sendMessageInTransaction(message, i);

            System.out.printf("发送结果：%s%n", result);
        }
        System.out.println(new Date());
        System.in.read();
    }
}
```

启动生产者进行测试：

![image-20240327164402122](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403271644786.png)

## 消费者

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        // 创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("transaction-consumer-group");
        // 设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        // 订阅一个主题来消费   *表示没有过滤参数 表示这个主题的任何消息
        consumer.subscribe("TransactionTopicTest", "*");
        // 注册一个消费监听 MessageListenerConcurrently是并发消费
        // 默认是20个线程一起消费，可以参看 consumer.setConsumeThreadMax()
        consumer.registerMessageListener(new MessageListenerConcurrently() {
            @Override
            public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs,
                                                            ConsumeConcurrentlyContext context) {
                // 这里执行消费的代码 默认是多线程消费
                System.out.println(Thread.currentThread().getName() + "----" + new String(msgs.get(0).getBody()));
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
            }
        });
        consumer.start();
        System.in.read();
    }
}
```

启动消费者进行测试：

![image-20240327164427352](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403271644339.png)
