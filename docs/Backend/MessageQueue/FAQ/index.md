# 消息队列常见问题与最佳实践

本页汇总消息队列在生产中最常踩的坑与对应解法：丢消息、重复消费、乱序、积压、延迟、脑裂等，并给出可直接照抄的排查步骤和最佳实践清单。

## 消息丢失了，怎么排查

按链路逐环检查：

```text
生产端确认 → Broker 持久化 → 消费端 ACK
```

1. **生产端**：Kafka 看 `acks` 是否为 `all`、`enable.idempotence` 是否开启；RabbitMQ 看是否启用 Publisher Confirms。查看生产日志有没有发送异常被吞掉。
2. **Broker**：Kafka 看 `replication.factor` 与 `min.insync.replicas`；RabbitMQ 看队列是否 `durable`、消息是否 `delivery_mode=2`。检查磁盘是否写满、日志是否有刷盘报错。
3. **消费端**：是否开启自动确认/自动提交？是否“先确认后处理”？失败消息是否被无限 requeue 或直接丢弃？

::: danger 排查禁忌
1. 只查一个环节：丢消息通常是“生产没确认 + 消费先 ACK”叠加造成的。
2. 凭印象判断：用监控指标说话（生产失败率、unacked 数、消费组 lag）。
3. 直接改配置不压测：改 `acks` 或副本数会影响吞吐，改完必须验证。
:::

## 消息重复了，怎么处理

重复消费无法靠 MQ 完全杜绝（至少一次语义），正确姿势是**消费幂等**：

- 消息必须携带全局唯一业务 ID。
- 用去重表/唯一索引/状态机/乐观锁兜底。
- 详见 [消费幂等](../Idempotency/index.md)。

## 消息乱序了，怎么保证顺序

| 诉求 | 做法 |
| --- | --- |
| 同一订单的事件有序 | Kafka：同 key 进同分区；RabbitMQ：发到同一队列，单消费者串行消费 |
| 全局有序 | Kafka：单分区 Topic；RabbitMQ：单队列 + 单消费者（牺牲吞吐） |
| 多消费者并行且有序 | 按业务 key 分片路由，每个 key 内部串行 |

::: warning 顺序与吞吐的取舍
顺序性本质上要求“同一组数据只能被一条链路串行处理”，并行度越高越难保证顺序。先想清楚是“必须全链路有序”还是“单业务对象有序”。
:::

## 消息积压了，怎么快速处理

### 定位

- Kafka：`kafka-consumer-groups.sh --describe --group xxx`，看 `LAG`。
- RabbitMQ：管理界面 Queues 页面看 `messages ready`。

### 处理

1. **临时扩容消费者**：Kafka 消费组内消费者数不能超过分区数，要同时增加分区；RabbitMQ 增加同一队列的消费者即可。
2. **先保证不丢**：积压期间消费者处理慢，先把告警阈值调低、保护数据库。
3. **清理无效消息**：已过期的业务（如已取消订单的通知）可以直接丢弃，但必须有明确的业务判定。
4. **临时降级**：极端情况下停掉非核心消费者，优先处理核心队列。
5. **事后优化**：处理慢的原因通常是业务逻辑重（DB 慢、第三方调用慢），而不是 MQ 本身。

::: danger 积压处理的坑
1. 只加消费者不加分区：Kafka 新增消费者空闲，积压不变。
2. 消费者处理逻辑里做重 IO：应先把消息批量取出落库，再异步处理。
3. 积压时把消息全部 requeue：会放大风暴，应先暂停投递再处理。
:::

## 消息延迟高，怎么优化

| 瓶颈 | 优化 |
| --- | --- |
| 批量发送等待 | Kafka 调小 `linger.ms`，牺牲一点吞吐换低延迟 |
| 消费者轮询间隔 | 调小 `poll` 间隔、提高 `max.poll.records` 处理效率 |
| 预取过多 | RabbitMQ 调小 `prefetch_count`，避免单消费者本地积压 |
| 磁盘 IO 慢 | 使用 SSD、独立数据盘，Kafka 顺序写对磁盘很敏感 |
| 跨机房网络 | 就近部署消费者，或使用云厂商专线 |

## 消费者挂掉后，消息会怎样

- **Kafka**：该消费者负责的分区触发重平衡，分配给组内其他消费者；未提交 offset 的消息会被重新消费（重复）。
- **RabbitMQ**：未 ACK 的消息回到队列，重新投递给其他消费者。
- 因此：**消费者的幂等是标配**，不是可选项。

## 如何监控消息队列

| 指标 | Kafka | RabbitMQ |
| --- | --- | --- |
| 积压量 | 消费组 LAG | 队列 ready 数 |
| 吞吐 | 生产/消费速率 | 消息速率 |
| 健康度 | 控制器状态、ISR 数量 | 节点内存、连接数、Channel 数 |
| 失败量 | 发送错误、重试次数 | unacked、nack 次数 |

建议接入 Prometheus + Grafana 或云监控，并设置告警：

- LAG 超过阈值（如 1 万）持续 5 分钟。
- 生产失败率 > 0。
- 节点磁盘使用率 > 80%。
- RabbitMQ 内存超过高水位。

## 最佳实践清单

::: tip 生产级 MQ 八条军规
1. 生产端：`acks=all`（Kafka）或 Publisher Confirms（RabbitMQ），开启幂等/全局消息 ID。
2. Broker：副本数 ≥ 3、`min.insync.replicas=2`、消息与队列持久化。
3. 消费端：手动 ACK / 手动提交 offset，处理成功后才确认。
4. 幂等：每条消息带唯一业务 ID，落库去重与业务同事务。
5. 失败兜底：限次重试 → 死信队列 → 告警人工介入。
6. 监控：LAG、失败率、磁盘、内存全部接入告警。
7. 容量：按峰值流量预留 2~3 倍分区/节点余量。
8. 演练：定期做故障演练（停节点、停消费者、灌压测流量）。
:::

## 常用排查命令速查

```shell
# Kafka：查看消费组与积压
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group order-group

# Kafka：查看 Topic 分区与副本
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic orders

# RabbitMQ：查看集群状态
rabbitmqctl cluster_status

# RabbitMQ：查看队列积压
rabbitmqadmin list queues name messages ready unacknowledged consumers

# RabbitMQ：查看连接与 Channel
rabbitmqadmin list connections name state
```

## 验证方式

1. 人为制造一次消费者崩溃，确认消息不丢、可能重复，且重启后自动恢复。
2. 制造一次 Broker 宕机，确认集群自动选主、客户端自动重连。
3. 灌入压测流量，确认监控指标正常、LAG 能回落、无消息丢失。
4. 按 [Kafka 常见问题与最佳实践](../Kafka/FAQ/index.md) 的排查地图逐项核对 Kafka 侧的 Lag、ISR、Controller 指标。

## 参考资料

- Kafka 运维与监控：https://kafka.apache.org/documentation/#monitoring
- Kafka 消费组管理：https://kafka.apache.org/documentation/#basic_ops_consumer_group
- Kafka 深入专题（本库）：[Kafka 常见问题与最佳实践](../Kafka/FAQ/index.md)
- RabbitMQ 监控与指标：https://www.rabbitmq.com/monitoring.html
- RabbitMQ 故障排查：https://www.rabbitmq.com/troubleshooting.html
