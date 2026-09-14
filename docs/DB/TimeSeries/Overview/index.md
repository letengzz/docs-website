# 时序数据库概述与选型

时序数据库（Time-Series Database，TSDB）针对"**按时间连续产生的测量值**"这一种数据形态做极致优化。本文讲清三件事：它和关系型数据库的本质差异、什么场景必须用它、以及怎么在 InfluxDB / TDengine / Prometheus 之间选。

![时序数据 vs 关系型数据](../assets/tsdb-vs-rdb.svg)

## 什么是时序数据

时序数据的四个特征：

1. **每条记录都带时间戳**，且时间戳基本单调递增（来自设备、服务的"现在"）。
2. **只追加、不更新**：历史测量值不会变（错了就补一条修正记录，而不是 UPDATE）。
3. **按时间范围查询**：用得最多的是"最近 1 小时"、"昨天到今天"、"同比上周"。
4. **写入量远大于读取量**：常见比例 100:1 以上。

典型数据：服务器 CPU/内存/磁盘、应用 QPS 与耗时、传感器温度与电流、车辆坐标、股价 Tick、日志事件计数。

## 与关系型数据库的本质差异

| 维度 | 关系型（MySQL/PG） | 时序型（InfluxDB/TDengine） |
| --- | --- | --- |
| 写入模式 | 随机位置 INSERT/UPDATE，B+ 树维护 | 追加写，顺序落盘 |
| 索引 | 二级索引、支持复杂条件 | 时间主索引 + 标签索引（刻意简化） |
| 更新/删除 | 一等公民（UPDATE/DELETE） | 极少更新；删除靠整块过期（或行级删除，代价高） |
| 压缩 | 一般（行存） | 高压缩（列存 + 差分编码，5:1~20:1） |
| 聚合 | 通用但慢 | 时间窗口聚合是内置能力 |
| 事务 | ACID | 一般不追求跨行事务，换取吞吐 |
| 过期清理 | DELETE 逐行、代价高 | 保留策略整块丢弃，秒级完成 |

::: warning 不是"关系型调优一下就能扛"
一台设备每秒 1 个指标 × 10 万测点 = 10 万行/秒 = 86 亿行/天。关系型库在这种量级下会遇到三重瓶颈：B+ 树随机插入导致页分裂、二级索引写放大、`DELETE` 历史数据时锁与 binlog 压力。**这是存储引擎层面的差异，不是加索引能解决的。**
:::

## 什么时候该上时序数据库

满足以下任意两条，就该认真评估：

- 每秒写入点数（points/s）持续超过 1 万；
- 单表/单集合预期超过 1 亿行，且按月增长；
- 查询以"时间范围 + 标签过滤 + 聚合"为主；
- 数据有明显的"冷热分层"需求（近 7 天要快、更早的只需偶尔查）；
- 需要按时间自动过期，而不是靠人工清理脚本。

反过来说，如果数据量小（每天几百万点以内）、或者需要频繁更新与复杂事务，**用 MySQL/PostgreSQL 加分区表就够了**，引入时序库反而增加运维成本。

## 技术栈全景

| 层次 | 常用组件 | 说明 |
| --- | --- | --- |
| 采集 | Telegraf、Prometheus Exporters、自研 SDK、MQTT Broker | 采集端要支持批量与重试 |
| 传输/缓冲 | Kafka、MQTT、HTTP 批量接口 | 削峰与解耦，防止库被打挂 |
| 存储 | InfluxDB、TDengine、Prometheus TSDB、TimescaleDB、ClickHouse | 本专题重点 |
| 降采样 | 连续查询 / 物化视图 / 流计算（Flink） | 把秒级数据聚合成分钟/小时 |
| 展示 | Grafana、自研看板 | Grafana 是事实标准 |
| 告警 | Grafana Alerting、Alertmanager、TDengine 事件流 | 注意抖动抑制 |
| 长期归档 | 对象存储（S3/OSS）+ Parquet | 成本最低 |

## 主流产品对比

| 产品 | 数据模型 | 查询语言 | 部署形态 | 强项 | 弱项 |
| --- | --- | --- | --- | --- | --- |
| **InfluxDB 3** | 表（time/tag/field） | SQL（+ InfluxQL 兼容） | Core 单机 / Enterprise 集群 / Cloud | Parquet 列存、对象存储友好、SQL 生态 | Core 无集群；从 1.x/2.x 迁移需改造 Flux 任务 |
| **InfluxDB 2.x** | bucket + measurement | Flux / InfluxQL | 单机 / Cloud | 采集-任务-告警一体化，存量生态大 | Flux 学习成本高，与 SQL 生态割裂 |
| **TDengine 3.x** | 超级表 + 子表 | 类 SQL（含窗口、流计算） | 单机 / 集群（开源版含集群） | 物联网场景吞吐强、国产化支持、单机就能扛很高写入 | 生态相对小，跨场景通用性弱于 PG 系 |
| **Prometheus** | metric + label | PromQL | 单机为主（+ 远程存储） | 云原生监控事实标准，K8s 自动发现 | 默认本地存储不适合长期海量存储 |
| **TimescaleDB** | PostgreSQL 超表 | 完整 SQL | 扩展在 PG 上 | 复用 PG 生态与 SQL 能力 | 海量写入下要精细调优 |
| **ClickHouse** | 宽表 + MergeTree | SQL | 集群 | 分析能力极强、压缩好 | 不是专门的时序库，需自行设计标签与 TTL |

## 选型决策树

![时序库选型决策树](../assets/tsdb-selection.svg)

三步收敛：

1. **按场景定候选**：指标监控 → Prometheus（+ 远程存储）；IoT/工业设备 → TDengine；大规模分析与云原生 → InfluxDB 3 或 ClickHouse。
2. **按约束收敛**：是否有国产化/信创要求？是否必须开源可自托管？团队是否熟悉 SQL 与 Grafana？
3. **用真实数据压测**：按目标写入速率灌 10 分钟以上，同时跑看板查询，看 P95 延迟、CPU、磁盘增量是否符合预算。

::: danger 选型的三个常见误区
1. **只看写入性能不看查询模式**：写入快但看板查询慢，最终还是被业务投诉。压测必须"写入 + 查询"并发跑。
2. **用标签存高基数字段**：把 `user_id`、`order_id` 当标签，索引直接爆炸（详见[数据模型](../DataModel/index.md)）。
3. **忽略保留策略**：不设 TTL 就上线，磁盘几天写满，最后被迫紧急删数据（往往还删错）。
:::

## 验证方式

选型结论要用数字验证，不能只靠感觉。最小验证脚本（以 InfluxDB 3 为例，先起容器）：

```shell
# 1. 启动 InfluxDB 3 Core（本地验证用）
docker run --rm -d --name influxdb3 \
  -p 8181:8181 \
  -e INFLUXDB3_AUTH_TOKEN=apiv3-local-dev-token \
  influxdb:3-core
# 预期：容器启动，8181 端口可访问

# 2. 探活
curl -s http://localhost:8181/health
# 预期：包含 "ok" 或 status 正常

# 3. 写入一批数据（改用自动化压测更准确，这里只验证链路）
curl -s -X POST "http://localhost:8181/api/v3/write_lp?db=tsdb_demo&precision=second" \
  -H "Authorization: Bearer apiv3-local-dev-token" \
  --data-binary 'cpu,host=srv-01,region=cn-east usage=42.5 1790000000'
```

```sql
-- 4. 查询验证：按时间窗口聚合
SELECT date_bin(INTERVAL '1 minute', time) AS ts, host, AVG(usage) AS avg_usage
FROM cpu
WHERE time >= now() - INTERVAL '1 hour'
GROUP BY ts, host
ORDER BY ts DESC;
```

收尾确认：写入返回 2xx、查询能按窗口聚合出结果、单条写入链路通畅。**正式压测请用 `taosBenchmark`（TDengine）或 `influxdb3` 写入压测工具**，按目标速率跑 10 分钟以上再对比选型。

## 参考资料

- InfluxDB 官方文档：[docs.influxdata.com](https://docs.influxdata.com/)
- TDengine 官方文档：[docs.tdengine.com](https://docs.tdengine.com/)
- Prometheus 官方文档：[prometheus.io/docs](https://prometheus.io/docs/)
- 延伸阅读：[数据模型](../DataModel/index.md) / [查询与降采样](../Query/index.md) / [实战案例](../Practice/index.md)
