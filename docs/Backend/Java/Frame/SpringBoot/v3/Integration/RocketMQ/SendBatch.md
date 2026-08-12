# 发送批量消息

Rocketmq可以一次性发送一组消息，那么这一组消息会被当做一个消息消费。

## 使用场景

如果消息过多，每次发送消息都和MQ建立连接，无疑是一种性能开销，批量消息可以把消息打包批量发送，批量发送消息能显著提高传递小消息的性能。

## 批量消息限制

批量发送消息能显著提高传递消息的性能。**限制是这些批量消息应该有相同的Topic，而且不能是延时消息**。此外，这一批消息的**总大小不应超过4MB**

**如果超过可以有2种处理方案**：

1. 将消息进行切割成多个小于4M的内容进行发送
2. 修改4M的限制改成更大：可以设置Producer的maxMessageSize属性；修改配置文件中的maxMessageSize属性

## 生产者

批量发送消息能显著提高传递小消息的性能。限制是这些批量消息应该有相同的 Topic，相同的 waitStoreMsgOK，而且不能是延时消息。此外，这一批消息的总大小不应超过 4MB。

如果批量消息大于1MB就不要用一个批次发送，而要拆分成多个批次消息发送。也就是说，一个批次消息的大小不要超过1MB，实际使用时，这个1MB的限制可以稍微扩大点，实际最大的限制是4194304字节，大概4MB。

```java
@SpringBootTest
class Producer {


    /**
     * 注入rocketMQTemplate，使用它来操作mq
     */
    @Resource
    private RocketMQTemplate rocketMQTemplate;

    /**
     * 发送批量消息
     */
    @Test
    public void testBatchSend(){
        //创建消息
        List<Message> msgs = new ArrayList<>();
        for(int i=0;i<10;i++){
            msgs.add(MessageBuilder.withPayload("批量消息"+(i+1)).build());
        }
        // 发送批量消息
        SendResult sendResult = rocketMQTemplate.syncSend("BatchTopicTest", msgs);
        System.out.println("sendResult = " + sendResult);
    }
}
```

启动生产者进行测试：

![image-20240326172055824](assets/img202403261721889.png)

## 消费者

批量接收消息能提高传递小消息的性能，同时与顺序消息配合的情况下，还能根据业务主键对顺序消息进行去重 (是否可去重，需要业务来决定)，减少消费者对消息的处理。

对于消费者而言Consumer的MessageListenerConcurrently监听接口的`consumeMessage()`方法的第一个参数为消息列表，但默认情况下每次只能消费一条消息，可以通过：Consumer的pullBatchSize属性设置消息拉取数量(默认32)，可以通过设置 consumeMessageBatchMaxSize 属性设置消息一次消费数量(默认1)。

:::danger 注意

pullBatchSize 和 consumeMessageBatchMaxSize并不是设置越大越好，一次拉取数据量太大会导致长时间等待，性能降低。而且消息处理失败同一批消息都会失败，然后进行重试，导致消费时长增加。增加没必要的重试次数

:::

```java
@Component
@RocketMQMessageListener(topic = "BatchTopicTest",consumerGroup = "batch-consumer-group",consumeMode = ConsumeMode.ORDERLY)
public class BatchMsgListener implements RocketMQListener<MessageExt>,RocketMQPushConsumerLifecycleListener {
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

    /**
     * 对消费者客户端的一些配置
     * 重写prepareStart方法
     * @param defaultMQPushConsumer
     */
    @Override
    public void prepareStart(DefaultMQPushConsumer defaultMQPushConsumer) {
        //设置每次消息拉取的时间间隔 单位 毫秒
        defaultMQPushConsumer.setPullInterval(1000);
        //最小消费线程池数
        defaultMQPushConsumer.setConsumeThreadMin(1);
        //最大消费线程池数
        defaultMQPushConsumer.setConsumeThreadMax(10);
        //设置消费者单次批量消费的消息数目上限    默认1
        defaultMQPushConsumer.setConsumeMessageBatchMaxSize(10);
        //设置每个队列每次拉取的最大消费数
        defaultMQPushConsumer.setPullBatchSize(16);
    }
}
```

启动消费者进行测试：

![image-20240326172535513](assets/img202403261725650.png)

## 一次消费多条

可以通过设置consumeMessageBatchMaxSize属性设置消息一次消费数量(默认1)

consumeMessageBatchMaxSize：每次消费(即将多条消息合并为List消费)的最大消息数目，默认值为1

每个消费线程消费批次消费的消息数量，consumeMessageBatchMaxSize 也跟pullBatchSize相关，消费线程实际上每次消费的消息数量不会大于 pullBatchSize，具体可以查看`ConsumeMessageConcurrentlyService.submitConsumeRequest()`，消费任务的提交。

因此，实际上 `consumeMessageBatchMaxSize <= pullBatchSize <= maxTransferCountOnMessageInMemory` 。

RocketMQPushConsumerLifecycleListener：当`@RocketMQMessageListener`中的配置不足以满足我们的需求时，可以实现该接口直接更改消费者类DefaultMQPushConsumer的配置

```java
@Component
@RocketMQMessageListener(topic = "BatchTopicTest",consumerGroup = "batch-consumer-group",consumeMode = ConsumeMode.ORDERLY)
public class BatchMsgListener implements RocketMQListener<MessageExt>,RocketMQPushConsumerLifecycleListener {
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

    /**
     * 对消费者客户端的一些配置
     * 重写prepareStart方法
     * @param defaultMQPushConsumer
     */
    @Override
    public void prepareStart(DefaultMQPushConsumer defaultMQPushConsumer) {
        //设置每次消息拉取的时间间隔 单位 毫秒
        defaultMQPushConsumer.setPullInterval(1000);
        //最小消费线程池数
        defaultMQPushConsumer.setConsumeThreadMin(1);
        //最大消费线程池数
        defaultMQPushConsumer.setConsumeThreadMax(10);
        //设置消费者单次批量消费的消息数目上限    默认1
        defaultMQPushConsumer.setConsumeMessageBatchMaxSize(3);
        //设置每个队列每次拉取的最大消费数
        defaultMQPushConsumer.setPullBatchSize(16);
    }
}
```

## 批量消息的限制使用

**操作步骤**：

- 定义消息切割器切割消息

- 发送消息把消息切割之后，进行多次批量发送

- 定义消息切割器：

  ```java [com.hjc.demo.splitter.ListSplitter]
  package com.hjc.demo.splitter;

  import org.apache.rocketmq.common.message.Message;

  import java.util.Iterator;
  import java.util.List;
  import java.util.Map;

  /**
   * 消息切割器  按照4M大小切割
   * @author qzz
   */
  public class ListSplitter implements Iterator<List<Message>> {

      private final int SIZE_LIMIT = 1024 * 1024 * 4;

      private final List<Message> messages;

      private int currIndex;

      public ListSplitter(List<Message> messages) {
          this.messages = messages;
      }

      @Override
      public boolean hasNext() {
          return currIndex < messages.size();
      }

      @Override
      public List<Message> next() {
          int startIndex = getStartIndex();
          int nextIndex = startIndex;
          int totalSize = 0;
          for (; nextIndex < messages.size(); nextIndex++) {
              Message message = messages.get(nextIndex);
              int tmpSize = calcMessageSize(message);
              if (tmpSize + totalSize > SIZE_LIMIT) {
                  break;
              } else {
                  totalSize += tmpSize;
              }
          }
          List<Message> subList = messages.subList(startIndex, nextIndex);
          currIndex = nextIndex;
          return subList;
      }
      private int getStartIndex() {
          Message currMessage = messages.get(currIndex);
          int tmpSize = calcMessageSize(currMessage);
          while(tmpSize > SIZE_LIMIT) {
              currIndex += 1;
              Message message = messages.get(currIndex);
              tmpSize = calcMessageSize(message);
          }
          return currIndex;
      }
      private int calcMessageSize(Message message) {
          int tmpSize = message.getTopic().length() + message.getBody().length;
          Map<String, String> properties = message.getProperties();
          for (Map.Entry<String, String> entry : properties.entrySet()) {
              tmpSize += entry.getKey().length() + entry.getValue().length();
          }
          // 增加⽇日志的开销20字节
          tmpSize = tmpSize + 20;
          return tmpSize;
      }
  }
  ```

- 批量发送方法：

  ```java
  @SpringBootTest
    class Producer {


        /**
         * 注入rocketMQTemplate，使用它来操作mq
         */
        @Resource
        private RocketMQTemplate rocketMQTemplate;

        /**
         * 发送批量消息(大于4MB)
         * 发送批量消息，最主要的区别是在发送消息的send方法入参一个List。
         */
        @Test
        public void testBatchSendSplitter(){
            List<Message> messageList = new ArrayList<>();
            for(int i=0;i<1000;i++){
                //添加内容
                byte[] bytes = (("批量消息"+i).getBytes(CharsetUtil.UTF_8));
                messageList.add(new Message("BatchTopicTest","message-tag-batch",bytes));
            }

            //切割消息
            //把大的消息分裂传给你若干个小的消息
            ListSplitter splitter = new ListSplitter(messageList);
            while(splitter.hasNext()){
                List<Message> listItem = splitter.next();
                //发送消息
                //参数一：topic   如果想添加tag,可以使用"topic:tag"的写法
                //参数二：消息内容
                SendResult sendResult = rocketMQTemplate.syncSend("BatchTopicTest",listItem,6000);
                System.out.println(sendResult);
            }
        }
    }
  ```

- 批量消费监听：

  ```java
  @Component
  @RocketMQMessageListener(topic = "BatchSplitterTopicTest",consumerGroup = "batch-consumer-group",consumeMode = ConsumeMode.ORDERLY)
  public class ListSplitterListener implements RocketMQListener<List<MessageExt>>,RocketMQPushConsumerLifecycleListener {
      /**
       * 消费消息的方法
       * 如果泛型指定了固定的类型 那么消息体就是参数
       * MessageExt 类型是消息的所有内容
       * 如果没有报错 就签收了
       * 如果报错了 就是拒收 就会重试
       * @param messages
       */
      @Override
      public void onMessage(List<MessageExt> messages) {
          System.out.println("批量消息，总个数:"+messages.size());
          messages.forEach(message->{
              System.out.println("批量消息 body:"+new String(message.getBody(), CharsetUtil.UTF_8));
          });
      }

      /**
       * 对消费者客户端的一些配置
       * 重写prepareStart方法
       * @param defaultMQPushConsumer
       */
      @Override
      public void prepareStart(DefaultMQPushConsumer defaultMQPushConsumer) {
          //设置每次消息拉取的时间间隔 单位 毫秒
          defaultMQPushConsumer.setPullInterval(1000);
          //最小消费线程池数
          defaultMQPushConsumer.setConsumeThreadMin(1);
          //最大消费线程池数
          defaultMQPushConsumer.setConsumeThreadMax(10);
          //设置消费者单次批量消费的消息数目上限    默认1
          defaultMQPushConsumer.setConsumeMessageBatchMaxSize(10);
          //设置每个队列每次拉取的最大消费数
          defaultMQPushConsumer.setPullBatchSize(16);
      }
  }
  ```

- 查看效果：

  ![image-20240326175426389](assets/img202403261754597.png)
