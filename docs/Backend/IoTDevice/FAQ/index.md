# 常见问题与分诊

设备类故障的特点是**现场没人能描述清楚**：客服说「设备离线了」，运维说「平台显示在线」，设备厂商说「我这边日志正常」。本页给一张分诊表，把一句模糊的话变成一条可执行的命令。

::: tip 一句话定位
分诊的第一问永远是：**这条连接现在还在不在**。在，问题在设备或业务；不在，问题在网络或凭证。这一问能把排查范围砍掉一半。
:::

## 一、十行分诊表

| 现象 | 先看什么 | 命令 | 常见结论 |
| --- | --- | --- | --- |
| 平台显示在线，但没数据 | `received_at` 最新时间 | `sqlite3 iot.db "SELECT max(received_at) FROM telemetry_raw WHERE device_id=?"` | 设备在线但采集/上报停了 |
| 平台显示离线，设备灯正常 | Broker 会话 | `mosquitto_sub -h h -t '$SYS/broker/clients/connected' -C 1` | 连接被踢（重复 client_id）或 KeepAlive 超时 |
| 指令发了没反应 | 指令状态 + 是否有 ACK 主题 | `SELECT state, attempts FROM command WHERE command_id=?` | 停在 `SENT` → 设备没回执；停在 `QUEUED` → 设备离线 |
| 指令执行了两次 | 设备去重窗与 `command_id` | 设备日志搜 `cmd=` | 重试换了 `command_id`，或去重窗太小 |
| 曲线出现规律缺口 | 接入层限频 | `SELECT count(*) FROM auth_fail WHERE reason='rate'` | 被限流丢掉（应改合并） |
| 曲线往回折 | `event_time` 与 `received_at` 差值 | `SELECT max(julianday(received_at)-julianday(event_time))*86400 FROM telemetry_raw` | 设备时钟漂移 / 补传 |
| 升级率卡在 30% | `upgrade_task.state` 分布 | `SELECT state, count(*) FROM upgrade_task GROUP BY 1` | 停在 `DOWNLOADING` → 网络/带宽；`FAILED` → 兼容矩阵 |
| 设备全部连不上（批量） | Broker 进程与证书有效期 | `mosquitto_sub -h h -t 'x' -C 1 -W 3` | Broker 挂了 / 证书过期 / 密码文件未 reload |
| 同一设备频繁上下线 | 抢占日志 | `grep 'Session taken over' broker.log \| tail` | 两台设备同 `client_id`（克隆） |
| 设置的值自己变回去了 | 影子 `version` 与写入方 | `SELECT version, desired, desired_at FROM shadow WHERE device_id=?` | 整档覆盖丢更新（缺 CAS） |

## 二、止血五步（按顺序，不要跳）

1. **确认范围**：一台 / 一批 / 全部。一批以上先看 Broker 与证书，不要从设备查起。
2. **确认凭证**：`mosquitto_pub` 用同凭证手工连一次。连不上 = 凭证问题，与业务无关。
3. **确认会话**：手工连上后看是否立刻被踢（`Session taken over`）。被踢 = 克隆或设备重连风暴。
4. **确认数据**：能连上但没数据时，抓一条原始报文（`mosquitto_sub -v -t 'up/#'`），看是设备没发还是解析失败。
5. **再动生产**：以上四步都做完再改配置。**在没确认范围前重启 Broker，会把一次局部故障放大成全局故障**（所有设备同时重连）。

## 三、十二问

| 问题 | 答案 |
| --- | --- |
| 1. 「在线」到底指哪个口径？ | 连接在线 / 心跳在线 / 数据新鲜，三者不同（见[总览](../Overview/index.md)） |
| 2. KeepAlive 设多少？ | 30~300 s，按业务能忍的掉线检测延迟反推；固件按 0.8× 发送 |
| 3. 需要 TLS 吗？ | 公网必须；内网也建议，因为凭证要在链路上传 |
| 4. 一机一密还是一机一证？ | 消费级一机一密足够；工业/支付用 mTLS |
| 5. 设备离线多久的消息要保留？ | 按离线分布 P99 定，通常 24 h；再长要评估内存 |
| 6. 为什么不直接用 Kafka？ | 设备侧连不了 Kafka；MQTT 是为弱网与低功耗设计的 |
| 7. 影子与指令的区别？ | 影子只要最终态，指令要每一次（见[设备影子](../DeviceShadow/index.md)） |
| 8. 固件一定要 A/B 吗？ | 有变砖风险就必须；单分区只能靠「刷写过程绝不掉电」的运气 |
| 9. 设备时钟不准怎么办？ | 排序用平台时间，展示用设备时间并标注（见[遥测接入](../TelemetryIngest/index.md)） |
| 10. 10 万连接要多少内存？ | 约 4 GB 起步（40 KB/连接），未计排队消息 |
| 11. 怎么防克隆？ | 一机一密 + `secret_fp` 唯一 + 抢占告警；无法根除，只能提高成本与暴露率 |
| 12. 退役设备怎么处理？ | 状态置 `RETIRED` + 吊销凭证 + 断开连接，三件事都要做 |

## 四、术语表

| 术语 | 含义 |
| --- | --- |
| **三元组** | `product_key` / `device_name` / `device_secret`，一机一密的凭证组合 |
| **影子（shadow）** | 设备的期望态与报告态账本，含 `version` |
| **delta** | `desired` 与 `reported` 的差，派生值不落库 |
| **遗嘱（Will）** | 连接异常断开时由 Broker 代发的消息 |
| **`Session Expiry`** | MQTT 5 的会话保留时长，0 = 断开即丢 |
| **抢占（takeover）** | 同 `client_id` 新连接把旧连接踢掉 |
| **in-flight** | 已发出但未收到确认的指令，同一设备通常限 1 条 |
| **A/B 分区** | 双固件槽，新固件写入非运行槽，失败自动回滚 |
| **水位（watermark）** | 流处理里「认为某时间点之前的数到齐了」的界线 |

## 五、本专题明确不做的事

| 不做 | 理由 | 该去哪 |
| --- | --- | --- |
| Broker 集群搭建与调优 | 属产品运维，不是接入设计 | [消息队列](../../MessageQueue/Overview/index.md) |
| 时序库选型与压缩算法 | 属数据库专题 | [时序数据](../../../DB/TimeSeries/index.md) |
| 设备固件的 C 代码实现 | 本专题只给契约与判据 | 设备厂商文档 |
| 端侧模型推理 | 属 AI 专题 | [端侧推理](../../../AI/EdgeInference/index.md) |
| 物联网安全合规（等保、数据出境） | 属合规专题 | [AI 安全与合规](../../../AI/AISecurityCompliance/index.md) |

## 六、判据

| 判据 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `IOQ-A` | 分诊表是否覆盖「在线无数据」「离线灯正常」两类高频现象 | 未覆盖即不合格 | 按本页第一节补齐 |
| `IOQ-B` | 每条分诊是否给出可执行命令而非「检查配置」 | 无命令即不合格 | 补命令与预期输出 |
| `IOQ-C` | 止血五步是否明确「先确认范围再动生产」 | 未写明即不合格 | 在第 5 步加粗该纪律 |
| `IOQ-D` | 是否有「重启 Broker 会放大故障」的警示 | 无即不合格 | 补警示与替代做法（分批重启 + 客户端抖动） |
| `IOQ-E` | 十二问是否每问都有确定答案而非「视情况」 | 有「视情况」即不合格 | 给出默认值与反推方法 |
| `IOQ-F` | 术语表是否覆盖本专题全部专有名词 | 缺项即不合格 | 补术语 |
| `IOQ-G` | 「不做的事」是否写明该去哪 | 未指路即不合格 | 补链接 |
| `IOQ-H` | 本页所有命令是否能在 Practice 页的环境里直接跑 | 有依赖缺失即不合格 | 统一环境与库路径 |

## 参考资料

- [实战：本机跑通一条闭环](../Practice/index.md)——本页命令的运行环境
- [总览：七段链与三个「在线」](../Overview/index.md)——分诊表第一问的理论依据
- [连接与会话](../ConnectionSession/index.md)——`Session taken over` 与 KeepAlive
- MQTT 5.0 §3.1.2.11——`Session Expiry Interval` 的语义
