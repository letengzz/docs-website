# Kafka 概述

<p style="text-align:center;"><img src="./assets/kafka-logo.png" alt="Apache Kafka" style="zoom:75%;" /></p>

Apache Kafka 是一个**分布式事件流平台**：它把消息以「日志」形式追加到分区中，消费者通过 offset 自行控制读取位置，因此既支持高吞吐消息传递，也支持历史数据回溯。日志采集、事件驱动、CDC 同步、大数据管道、流式计算都能用它承载。

本页是「Kafka 深入」小节的入口，讲清**定位、版本现状、核心概念和 10 分钟快速上手**；生产者、消费者、副本、可靠性、集群与实战等细节在下方子页展开，示例统一基于当前稳定版 **Apache Kafka 4.3.1（2026-06-25 发布，仅支持 KRaft 模式）**。

## 专题导航

### 入门

- [版本演进与迁移（ZooKeeper → KRaft）](Version/index.md)

### 原理

- [架构与存储原理](Architecture/index.md)
- [分区与副本机制](PartitionReplica/index.md)

### 开发

- [生产者深入](Producer/index.md)
- [消费者与消费组深入](Consumer/index.md)
- [可靠性与 Exactly-Once](Reliability/index.md)

### 生产实践

- [集群部署、运维与监控](Cluster/index.md)
- [实战：订单事件管道](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

::: tip 一句话理解
Kafka 的核心是「**一个可以反复读的分布式提交日志**」：写入只能追加，读取靠消费者自己维护的 offset。理解这一点，就能理解它为什么既能当消息队列，又能当流存储。
:::

## 版本速览

| 版本 | 状态（2026-09 核对） | 元数据模式 | 说明 |
| --- | --- | --- | --- |
| 4.3.1 | 当前支持版本，**推荐使用** | 仅 KRaft | 2026-06-25 发布，Docker 镜像 `apache/kafka:4.3.1` |
| 4.2.1 | 支持中 | 仅 KRaft | 4.2 起 Share Groups（KIP-932）生产可用 |
| 4.1.2 | 支持中 | 仅 KRaft | 4.0 之后的稳定性修复版本线 |
| 4.0.x | 已归档 | 仅 KRaft | 移除 ZooKeeper；新版消费组协议（KIP-848）GA |
| 3.9.x | 已归档，**仅存量集群使用** | 支持 KRaft 与 ZooKeeper | ZooKeeper 模式最后一代，迁移前的中转版本 |

::: info 环境前提
Broker、Connect、命令行工具需要 **Java 17+**；Java 客户端与 Kafka Streams 最低 **Java 11**（官方 KIP-750）。本库对 3.x（ZooKeeper）时代的配置说明**不删除**，在 [版本演进与迁移](Version/index.md) 中标注为「仅存量集群使用」。
:::

## 核心概念

### Topic、Partition 与 Offset

- **Topic（主题）**：消息的逻辑分类，如 `orders`、`user-events`。
- **Partition（分区）**：一个 Topic 被拆成多个分区，每个分区是一个**有序追加的日志文件**；分区是 Kafka 并行与水平扩展的基本单位。
- **Offset（偏移量）**：消息在分区内的单调递增序号，消费者通过它记录「读到哪里」。

### Broker、副本与 ISR

| 概念 | 说明 |
| --- | --- |
| Broker | 一台 Kafka 服务器，集群由多个 Broker 组成，负责存储与读写分区 |
| 副本（Replica） | 每个分区有多个副本，Leader 负责读写，Follower 主动拉取同步 |
| ISR | In-Sync Replica，与 Leader 保持同步的副本集合；`acks=all` 时写入需按 `min.insync.replicas` 在 ISR 中确认 |
| Controller | KRaft 模式下由 Controller Quorum 负责选主、分区分配与元数据管理 |

### Producer、Consumer 与消费组

- **Producer（生产者）**：把消息写入指定 Topic 的分区；相同 key 进入同一分区，从而保证同一 key 的消息有序。
- **Consumer（消费者）**：从分区拉取消息；多个消费者组成 **Consumer Group（消费组）**，组内按分区分配分摊消费，组间互相独立（广播）。

::: warning 分区内有序、跨分区无序
Kafka 只保证**同一个分区内**的消息顺序。需要全局有序时，把 Topic 设为单分区（牺牲吞吐），或按业务 key 分区把需要有序的消息收敛到同一分区。
:::

### 重平衡与 Share Groups

消费组成员数量变化（新增、宕机、主动退出）会触发 **Rebalance（重平衡）**，重新分配分区；重平衡期间消费可能短暂停顿并重复消费，因此消费端需要幂等。4.2 起 **Share Groups（共享消费组，KIP-932）** 生产可用，提供「点对点队列」语义：组内成员弹性伸缩、逐条确认，弥补传统消费组按分区分配的不足。

## 安装与快速启动

### 方式一：单机 Docker（演示环境）

```yaml [docker-compose.yml]
services:
  kafka:
    image: apache/kafka:4.3.1
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: "broker,controller"
      KAFKA_LISTENERS: "PLAINTEXT://:9092,CONTROLLER://:9093"
      KAFKA_ADVERTISED_LISTENERS: "PLAINTEXT://localhost:9092"
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT"
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093"
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
```

```shell
docker compose up -d
```

### 方式二：官方二进制包（本地开发）

```shell
# 1. 确认 Java 版本（Broker 与工具需要 17+）
java -version

# 2. 解压官方包（本文以 4.3.1 为例）
tar -xzf kafka_2.13-4.3.1.tgz
cd kafka_2.13-4.3.1

# 3. 生成集群 ID 并格式化 KRaft 日志目录（单节点 = broker + controller）
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties

# 4. 启动
bin/kafka-server-start.sh config/server.properties
```

::: danger 易错点
1. 4.x 已没有 ZooKeeper：不要再去启动 `zookeeper-server-start.sh`，也不要使用带 `--zookeeper` 参数的老命令。
2. 忘记 `kafka-storage.sh format` 直接启动：Broker 会因为日志目录未格式化而启动失败。
3. 生产环境必须拆分角色并至少 3 个节点，单节点合并部署（`--standalone`）只用于本地体验，见 [集群部署、运维与监控](Cluster/index.md)。
:::

## 基础命令行操作

```shell
# 进入容器（使用官方镜像时工具位于 /opt/kafka/bin）
docker exec -it kafka bash

# 创建 Topic（6 分区、3 副本）
/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
  --topic orders --partitions 6 --replication-factor 3 \
  --config min.insync.replicas=2

# 查看 Topic 列表与详情
/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic orders

# 控制台生产者
/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic orders

# 控制台消费者（从最早开始，指定消费组）
/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders --group console-demo --from-beginning \
  --property print.key=true --property print.partition=true

# 查看消费组积压（LAG 是关键指标）
/opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group console-demo
```

预期输出：生产者窗口输入内容后，消费者窗口立即打印；`--describe` 输出中 `LAG` 会随消费推进回落为 `0`。

## Java 客户端示例

引入依赖：

```xml [pom.xml]
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>4.3.1</version>
</dependency>
```

### 生产者（幂等 + 按 key 分区）

```java [KafkaProducerDemo.java]
import org.apache.kafka.clients.producer.*;
import java.util.Properties;

public class KafkaProducerDemo {
    public static void main(String[] args) throws Exception {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
                "org.apache.kafka.common.serialization.StringSerializer");
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
                "org.apache.kafka.common.serialization.StringSerializer");
        // 4.x 默认即为 all + true，这里显式写出便于理解
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");

        try (KafkaProducer<String, String> producer = new KafkaProducer<>(props)) {
            for (int i = 0; i < 10; i++) {
                // 相同 key 进入同一分区，保证同一订单的事件有序
                ProducerRecord<String, String> record =
                        new ProducerRecord<>("orders", "order-1001", "paid-" + i);
                producer.send(record, (metadata, ex) -> {
                    if (ex != null) {
                        System.err.println("发送失败：" + ex.getMessage());
                    } else {
                        System.out.printf("已写入 partition=%d offset=%d%n",
                                metadata.partition(), metadata.offset());
                    }
                });
            }
            producer.flush();
        }
    }
}
```

### 消费者（手动提交位移）

```java [KafkaConsumerDemo.java]
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.StringDeserializer;
import java.time.Duration;
import java.util.List;
import java.util.Properties;

public class KafkaConsumerDemo {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        // 手动提交：先处理业务，成功后再提交，保证至少一次
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");

        try (KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props)) {
            consumer.subscribe(List.of("orders"));
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("key=%s value=%s partition=%d offset=%d%n",
                            record.key(), record.value(),
                            record.partition(), record.offset());
                    // 业务处理（生产环境要配合幂等去重）
                }
                if (!records.isEmpty()) {
                    consumer.commitSync();
                }
            }
        }
    }
}
```

::: danger 易错点
1. `enable.auto.commit=true` 且在业务处理前自动提交：进程崩溃会丢消息，生产建议手动提交。
2. 单条消息处理超过 `max.poll.interval.ms`（默认 5 分钟）：消费者被判定死亡触发重平衡，产生重复消费，应改为异步处理 + 限流或调大该值。
3. 循环内逐条 `commitSync()`：提交请求过多会拖垮吞吐，应按批提交。
4. `auto.offset.reset=latest`（默认）配合新消费组：表现为「消息凭空消失」，需要历史数据时显式设置为 `earliest`。
5. 依赖跨分区全局有序：Kafka 只保证分区内有序，应按业务 key 分区。
6. 消费者数量大于分区数：多出的消费者空闲，不提升消费速度。
:::

## 常用配置速查

详细原理与调优见 [生产者深入](Producer/index.md) 与 [消费者与消费组深入](Consumer/index.md)，这里只列最常用的几项（默认值以 4.3 官方文档为准）。

| 端 | 参数 | 默认值 | 说明 |
| --- | --- | --- | --- |
| 生产者 | `acks` | `all` | 写入确认策略，`0` 最快但可能丢 |
| 生产者 | `enable.idempotence` | `true` | 幂等生产者，避免重试产生重复 |
| 生产者 | `batch.size` | `16384` | 单分区批次上限（字节） |
| 生产者 | `linger.ms` | `5` | 批量等待时间，**4.0 起由 0 改为 5** |
| 生产者 | `delivery.timeout.ms` | `120000` | 发送总超时，覆盖重试 |
| 消费者 | `enable.auto.commit` | `true` | 生产建议改为 `false` 手动提交 |
| 消费者 | `auto.offset.reset` | `latest` | 无位移时的起始位置 |
| 消费者 | `max.poll.records` | `500` | 单次 poll 最大条数 |
| 消费者 | `max.poll.interval.ms` | `300000` | 两次 poll 最大间隔，超时触发重平衡 |
| Broker | `min.insync.replicas` | `1` | 生产建议 ≥ 2，配合 `acks=all` |
| Broker | `unclean.leader.election.enable` | `false` | 禁止非同步副本当选，避免丢数据 |

## 验证方式

1. `docker compose up -d` 后执行 `docker exec -it kafka bash`，用控制台生产者发送、消费者接收，确认消息实时打印。
2. 运行上面的 Java Producer/Consumer Demo，观察输出中的 `partition`、`offset`，确认相同 key 落在同一分区。
3. 停掉消费者，生产多条消息后重启消费者，用 `--from-beginning` 验证消息持久化未丢。
4. 执行 `kafka-consumer-groups.sh --describe --group order-group`，确认 `LAG` 在消费完成后回到 `0`。

## 相关专题

- 消息队列概念、选型与跨产品对比：[消息队列概念与选型](../Overview/index.md)、[消息队列对比总结](../Comparison/index.md)
- 可靠投递与消费幂等的通用方法论：[可靠投递](../Reliability/index.md)、[消费幂等](../Idempotency/index.md)
- 用 Spring Cloud Stream 以编程模型收发 Kafka：[消息驱动：Spring Cloud Stream](../../SpringCloud/Stream/index.md)
- 微服务中的事件驱动与最终一致性：[微服务概述与服务拆分](../../Microservices/Overview/index.md)、[分布式事务](../../Microservices/DistributedTransaction/index.md)

## 参考资料

- Apache Kafka 官方文档：https://kafka.apache.org/documentation/
- Kafka 4.3 快速开始：https://kafka.apache.org/43/getting-started/quickstart/
- Kafka 4.3 升级说明：https://kafka.apache.org/43/getting-started/upgrade/
- Kafka 4.3 生产者配置：https://kafka.apache.org/43/generated/producer_config.html
- Kafka 4.3 消费者配置：https://kafka.apache.org/43/generated/consumer_config.html
- Kafka 版本下载与支持状态：https://kafka.apache.org/community/downloads/
