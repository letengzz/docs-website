# 发送批量消息

Rocketmq可以一次性发送一组消息，那么这一组消息会被当做一个消息消费

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
public class Producer {
    public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
        // 创建默认的生产者
        DefaultMQProducer producer = new DefaultMQProducer("batch-producer-group");
        //设置nameServer地址
        producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //启动生产者
        producer.start();
        //创建消息
        //第一个参数：主题的名字
        //第二个参数：消息内容
        List<Message> msgs = Arrays.asList(
                new Message("BatchTopicTest", "我是一组消息的A消息".getBytes()),
                new Message("BatchTopicTest", "我是一组消息的B消息".getBytes()),
                new Message("BatchTopicTest", "我是一组消息的C消息".getBytes())
        );

        SendResult send = producer.send(msgs);
        System.out.println("send = " + send);
        //关闭实例
        producer.shutdown();
    }
}
```

启动生产者进行测试：

![image-20240319215958367](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403192200604.png)

## 消费者

批量接收消息能提高传递小消息的性能，同时与顺序消息配合的情况下，还能根据业务主键对顺序消息进行去重 (是否可去重，需要业务来决定)，减少消费者对消息的处理。

对于消费者而言Consumer的MessageListenerConcurrently监听接口的`consumeMessage()`方法的第一个参数为消息列表，但默认情况下每次只能消费一条消息，可以通过：Consumer的pullBatchSize属性设置消息拉取数量(默认32)，可以通过设置 consumeMessageBatchMaxSize 属性设置消息一次消费数量(默认1)。

**注意**：pullBatchSize 和 consumeMessageBatchMaxSize并不是设置越大越好，一次拉取数据量太大会导致长时间等待，性能降低。而且消息处理失败同一批消息都会失败，然后进行重试，导致消费时长增加。增加没必要的重试次数

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("batch-consumer-group");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //订阅一个主题来消费  *表示没有过滤参数 表示这个主题的任何消息
        consumer.subscribe("BatchTopicTest","*");
        //注册一个消费监听 MessageListenerConcurrently 是多线程消费，默认20个线程
        // 可以参看consumer.setConsumeThreadMax()
//        consumer.setMessageModel(MessageModel.CLUSTERING);
        consumer.registerMessageListener(new MessageListenerOrderly() {
            @Override
            public ConsumeOrderlyStatus consumeMessage(List<MessageExt> list, ConsumeOrderlyContext consumeOrderlyContext) {
                // 这里执行消费的代码 默认是多线程消费
                System.out.println("线程id:" + Thread.currentThread().getId());
                System.out.println("消息内容:"+new String(list.get(0).getBody()));
                System.out.println("消费上下文:"+consumeOrderlyContext);
                // 返回消费的状态 如果是CONSUME_SUCCESS 则成功，若为RECONSUME_LATER则该条消息会被重回队列，重新被投递
                // 重试的时间为messageDelayLevel = "1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h
                // 也就是第一次1s 第二次5s 第三次10s  ....  如果重试了18次 那么这个消息就会被终止发送给消费者
                // 返回状态：
                // SUCCESS：成功 消息会从mq出队
                // LATER：失败(报错、null) 消息会重新回到队列 过一会重新投递出来 给当前消费者或者其他消费者消费的
                return ConsumeOrderlyStatus.SUCCESS;
                // return ConsumeConcurrentlyStatus.RECONSUME_LATER;
            }
        });
        // 这个start一定要写在registerMessageListener下面
        consumer.start();
        // 由于是异步回调方式，挂起当前的jvm
        System.in.read();

    }
}
```

启动消费者进行测试：

![image-20240326180813377](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403261808257.png)

## 一次消费多条

可以通过设置consumeMessageBatchMaxSize属性设置消息一次消费数量(默认1)

consumeMessageBatchMaxSize：每次消费(即将多条消息合并为List消费)的最大消息数目，默认值为1

每个消费线程消费批次消费的消息数量，consumeMessageBatchMaxSize 也跟pullBatchSize相关，消费线程实际上每次消费的消息数量不会大于 pullBatchSize，具体可以查看`ConsumeMessageConcurrentlyService.submitConsumeRequest()`，消费任务的提交。

因此，实际上 `consumeMessageBatchMaxSize <= pullBatchSize <= maxTransferCountOnMessageInMemory` 。

RocketMQPushConsumerLifecycleListener：当`@RocketMQMessageListener`中的配置不足以满足我们的需求时，可以实现该接口直接更改消费者类DefaultMQPushConsumer的配置

```java
public class Consumer {
    public static void main(String[] args) throws MQClientException, IOException {
        //创建默认消费者组
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("batch-consumer-group");
        //设置nameServer地址
        consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
        //订阅一个主题来消费  *表示没有过滤参数 表示这个主题的任何消息
        consumer.subscribe("BatchTopicTest","*");
        //注册一个消费监听 MessageListenerConcurrently 是多线程消费，默认20个线程
        // 可以参看consumer.setConsumeThreadMax()
//        consumer.setMessageModel(MessageModel.CLUSTERING);

        //设置每次消息拉取的时间间隔 单位 毫秒
        consumer.setPullInterval(1000);
        //最小消费线程池数
        consumer.setConsumeThreadMin(1);
        //最大消费线程池数
        consumer.setConsumeThreadMax(10);
        //设置消费者单次批量消费的消息数目上限    默认1
        consumer.setConsumeMessageBatchMaxSize(10);
        //设置每个队列每次拉取的最大消费数
        consumer.setPullBatchSize(16);
        consumer.registerMessageListener(new MessageListenerOrderly() {
            @Override
            public ConsumeOrderlyStatus consumeMessage(List<MessageExt> list, ConsumeOrderlyContext consumeOrderlyContext) {
                // 这里执行消费的代码 默认是多线程消费
                System.out.println("线程id:" + Thread.currentThread().getId());
                System.out.println("消息内容:"+new String(list.get(0).getBody()));
                System.out.println("消费上下文:"+consumeOrderlyContext);
                // 返回消费的状态 如果是CONSUME_SUCCESS 则成功，若为RECONSUME_LATER则该条消息会被重回队列，重新被投递
                // 重试的时间为messageDelayLevel = "1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h
                // 也就是第一次1s 第二次5s 第三次10s  ....  如果重试了18次 那么这个消息就会被终止发送给消费者
                // 返回状态：
                // SUCCESS：成功 消息会从mq出队
                // LATER：失败(报错、null) 消息会重新回到队列 过一会重新投递出来 给当前消费者或者其他消费者消费的
                return ConsumeOrderlyStatus.SUCCESS;
               
            }
        });
        // 这个start一定要写在registerMessageListener下面
        consumer.start();
        // 由于是异步回调方式，挂起当前的jvm
        System.in.read();

    }
}
```

## 批量消息的限制使用

**操作步骤**：

- 定义消息切割器切割消息
- 发送消息把消息切割之后，进行多次批量发送

- 定义消息切割器：

  > com.hjc.demo.splitter.ListSplitter

  ```java
  package com.hjc.demo.splitter;
  
  import org.apache.rocketmq.common.message.Message;
  
  import java.util.Iterator;
  import java.util.List;
  import java.util.Map;
  
  /**
   * 消息切割器  按照4M大小切割
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
  public class SplitterProducer {
      /**
       * 发送批量消息(大于4MB)
       * 发送批量消息，最主要的区别是在发送消息的send方法入参一个List。
       */
      public static void main(String[] args) throws MQClientException, MQBrokerException, RemotingException, InterruptedException {
          // 创建默认的生产者
          DefaultMQProducer producer = new DefaultMQProducer("batch-producer-group");
          //设置nameServer地址
          producer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
          //启动生产者
          producer.start();
  
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
              SendResult sendResult = producer.send(listItem,6000);
              System.out.println(sendResult);
          }
          //关闭实例
          producer.shutdown();
      }
  }
  ```

- 批量消费监听：

  ```java
  public class SplitterConsumer {
      public static void main(String[] args) throws MQClientException, IOException {
          //创建默认消费者组
          DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("batch-consumer-group");
          //设置nameServer地址
          consumer.setNamesrvAddr(MqConstant.NAME_SRV_ADDR_LINUX);
          //订阅一个主题来消费  *表示没有过滤参数 表示这个主题的任何消息
          consumer.subscribe("BatchTopicTest","*");
          //注册一个消费监听 MessageListenerConcurrently 是多线程消费，默认20个线程
          // 可以参看consumer.setConsumeThreadMax()
  //        consumer.setMessageModel(MessageModel.CLUSTERING);
  
          //设置每次消息拉取的时间间隔 单位 毫秒
          consumer.setPullInterval(1000);
          //最小消费线程池数
          consumer.setConsumeThreadMin(1);
          //最大消费线程池数
          consumer.setConsumeThreadMax(10);
          //设置消费者单次批量消费的消息数目上限    默认1
          consumer.setConsumeMessageBatchMaxSize(10);
          //设置每个队列每次拉取的最大消费数
          consumer.setPullBatchSize(16);
          consumer.registerMessageListener(new MessageListenerOrderly() {
              @Override
              public ConsumeOrderlyStatus consumeMessage(List<MessageExt> list, ConsumeOrderlyContext consumeOrderlyContext) {
                  System.out.println("批量消息，总个数:"+list.size());
                  list.forEach(message->{
                      System.out.println("批量消息 body:"+new String(message.getBody(), CharsetUtil.UTF_8));
                  });
                  // 返回消费的状态 如果是SUCCESS 则成功，若为LATER则该条消息会被重回队列，重新被投递
                  // 重试的时间为messageDelayLevel = "1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h
                  // 也就是第一次1s 第二次5s 第三次10s  ....  如果重试了18次 那么这个消息就会被终止发送给消费者
                  // 返回状态：
                  // SUCCESS：成功 消息会从mq出队
                  // LATER：失败(报错、null) 消息会重新回到队列 过一会重新投递出来 给当前消费者或者其他消费者消费的
                  return ConsumeOrderlyStatus.SUCCESS;
              }
          });
          // 这个start一定要写在registerMessageListener下面
          consumer.start();
          // 由于是异步回调方式，挂起当前的jvm
          System.in.read();
  
      }
  }
  ```
