# 发送事务消息

## 事务消息的发送流程

事务消息可以被认为是一个两阶段的提交消息实现，以确保分布式系统的最终一致性。事务性消息确保本地事务的执行和消息的发送可以原子地执行。

![](assets/img202403192216672.png)

事务消息的大致分为两个流程：正常事务消息的发送及提交、事务消息的补偿流程：

- 事务消息发送及提交：

  1. 发送消息（half消息）
  2. 服务端响应消息写入结果
  3. 根据发送结果执行本地事务（如果写入失败，此时half消息对业务不可见，本地逻辑不执行）
  4. 根据本地事务状态执行Commit或Rollback（Commit操作生成消息索引，消息对消费者可见）

- 事务补偿：
  1. 对没有Commit/Rollback的事务消息（pending状态的消息），从服务端发起一次“回查”
  2. Producer收到回查消息，检查回查消息对应的本地事务的状态
  3. 根据本地事务状态，重新Commit或者Rollback
  4. 其中，补偿阶段用于解决消息UNKNOW或者Rollback发生超时或者失败的情况。

![](assets/img202403192217004.png)

**事务消息共有三种状态**：提交状态、回滚状态、中间状态

- **提交事务** (`TransactionStatus.CommitTransaction`)：它允许消费者消费此消息。
- **回滚事务** (`TransactionStatus.RollbackTransaction`)：它代表该消息将被删除，不允许被消费。
- **中间状态** (`TransactionStatus.Unknown`)：它代表需要检查消息队列来确定状态。

## 消息发送

添加单元测试：

```java
@SpringBootTest
class Producer {

    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 测试事务消息
     * 默认是sync（同步的）
     * 事务消息会有确认和回查机制
     * 事务消息都会走到同一个监听回调里面，所以需要使用tag或者key来区分过滤
     *
     * @throws Exception
     */
    @Test
    public void testTransactionMsg() throws IOException {
        // 构建消息体
        Message<String> message = MessageBuilder.withPayload("这是一个事务消息").build();
        // 发送事务消息（同步的） 最后一个参数才是消息主题
        TransactionSendResult transaction = rocketMQTemplate.sendMessageInTransaction("TransactionTopicTest", message, "消息的参数");
        // 拿到本地事务状态
        System.out.println(transaction.getLocalTransactionState());
        // 挂起jvm，因为事务的回查需要一些时间
        System.in.read();
    }
}
```

消息会先到事务监听类的执行方法：

2. 如果返回状态为COMMIT，则消费者可以直接监听到

3. 如果返回状态为ROLLBACK，则消息发送失败，直接回滚

4. 如果返回状态为UNKNOW，则过一会会走回查方法

5. 如果回查方法返回状态为UNKNOW或者ROLLBACK，则消息发送失败，直接回滚
6. 如果回查方法返回状态为COMMIT，则消费者可以直接监听到

添加一个本地事务消息的监听 (半消息)：

```java
/**
 * 事务消息的监听与回查
 * 类上添加注解@RocketMQTransactionListener 表示这个类是本地事务消息的监听类
 * 实现RocketMQLocalTransactionListener接口
 * 两个方法为执行本地事务，与回查本地事务
 */
@Component
@RocketMQTransactionListener(corePoolSize = 4,maximumPoolSize = 8)
public class TransactionMsgListener implements RocketMQLocalTransactionListener {
    /**
     * 执行本地事务，这里可以执行一些业务
     * 比如操作数据库，操作成功就return RocketMQLocalTransactionState.COMMIT;
     * 可以使用try catch来控制成功或者失败;
     * @param msg
     * @param arg
     * @return
     */
    @Override
    public RocketMQLocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        // 拿到消息参数
        System.out.println(arg);
        // 拿到消息头
        System.out.println(msg.getHeaders());
        // 返回状态COMMIT,UNKNOWN
        return RocketMQLocalTransactionState.UNKNOWN;
    }
    /**
     * 回查本地事务，只有上面的执行方法返回UNKNOWN时，才执行下面的方法 默认是1min回查
     * 此方法为回查方法，执行需要等待一会
     * xxx.isSuccess()  这里可以执行一些检查的方法
     * 如果返回COMMIT，那么本地事务就算是提交成功了，消息就会被消费者看到
     *
     * @param msg
     * @return
     */
    @Override
    public RocketMQLocalTransactionState checkLocalTransaction(Message msg) {
        System.out.println(msg);
        return RocketMQLocalTransactionState.COMMIT;
    }
}
```
