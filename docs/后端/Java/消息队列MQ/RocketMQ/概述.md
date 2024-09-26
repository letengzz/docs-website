# RocketMQ 概述

RocketMQ是阿里巴巴2016年MQ中间件，使用Java语言开发，RocketMQ 是一款开源的分布式消息系统，基于高可用分布式集群技术，提供低延时的、高可靠、可伸缩的消息发布与订阅服务。是实现业务削峰，分布式事务的优秀框架。RocketMQ支持集群模式、消费者负载均衡、水平扩展和广播模式。采用零拷贝原理，顺序写盘、支持亿级消息堆积能力。同时提供了丰富的消息机制，比如顺序消息、事务消息等。同时，广泛应用于多个领域，包括异步通信解耦、企业解决方案、金融支付、电信、电子商务、快递物流、广告营销、社交、即时通信、移动应用、手游、视频、物联网、车联网等。

**官方网站**：http://rocketmq.apache.org/

## RocketMQ 特点

1. 能够保证严格的消息顺序

2. 提供丰富的消息拉取模式

3. 高效的订阅者水平扩展能力

4. 实时的消息订阅机制

5. 亿级消息堆积能力

## RocketMQ 角色

- **Producer**：消息的发送者，生产者，负责将消息发送到Broker (举例：发件人)
- **Consumer**：消息接收者，消费者，负责从Broker订阅Topic并消费消息 (举例：收件人)
- **Broker**：RocketMQ核心组件，用于暂存和传输消息的通道 (举例：快递)
- **NameServer**：命名服务，用于管理Broker的地址信息 (举例：各个快递公司的管理机构 相当于broker的注册中心，保留了broker的信息)
- **Queue**：队列，消息存放的位置，一个Broker中可以有多个队列
- **Topic**：主题，消息的分类
- **ProducerGroup**：生产者组 
- **ConsumerGroup**：消费者组，多个消费者组可以同时消费一个主题的消息

## 消息发送的流程

Producer询问NameServer，NameServer分配一个broker 然后Consumer也要询问NameServer，得到一个具体的broker，然后消费消息

![image-20231219201339268](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202312192013335.png)

