# Flink CDC

Flink CDC 把 CDC 从「搬运」推进到「数据集成」：以 Apache Flink 为运行时，用一段 YAML 描述「从哪个库同步哪些表到哪个目标」，就能完成整库同步、schema 演进、转换与路由。本页讲它的三代演进、增量快照算法、YAML Pipeline 写法与版本矩阵。

![快照四阶段](../assets/cdc-snapshot.svg)

## 一、三代演进：从 SQL 连接器到 Pipeline

| 阶段 | 版本 | 形态 | 关键能力 |
| --- | --- | --- | --- |
| 1.x | 2020 前后 | Flink SQL 的 CDC 连接器 | 单表订阅，依赖锁做快照，停不下来是常态 |
| 2.x | 2021~ | 增量快照 Source | **无锁快照、可并行、可断点续跑**，单表体验质变 |
| 3.x | 2023~ | **YAML Pipeline** | 整库同步一段配置；schema 演进、Transform、Route、UDF |

版本事实（2026-10 口径，按 Apache 官方公告核对）：**Flink CDC 3.6.0（2026-03-30）** 支持运行在 **Flink 1.20.x 与 2.2.x** 上，最低 **JDK 11**；新增 Oracle Pipeline Source 与 Apache Hudi Sink，PostgreSQL 支持表结构演进，Transform 支持 VARIANT 类型与 JSON 解析。Pipeline Source 目前为 **MySQL / PostgreSQL / Oracle** 三种。Flink 侧：2.3.0（2026-06-23）为主线，**1.20 为 LTS**，2.0 与 1.19 已于 2026 年年中 EOL——**Flink CDC 版本要和 Flink 版本按官方矩阵配对**，不要自行混搭。

## 二、增量快照算法：为什么 2.x 之后不再锁表

1.x 时代做初始快照要么全局锁、要么停写，本质问题是「快照读到的数据」与「binlog 起点」对不齐。增量快照算法用**高水位 + 低水位**解决：

1. **记录高水位**：开始读 Chunk 前记下当前 binlog 位点（高水位）。
2. **快照读**：不加锁，直接 `SELECT` 该主键区间的行（快照读）。
3. **回填**：把「高水位之后、该区间」的 binlog 变更取出来，**覆盖**快照结果——保证「同一行以最新变更为准」。
4. **越过低水位**：增量流追上 Chunk 的起点位点后，该 Chunk 完结。

四个阶段环环相扣，任何一步的顺序错误都会导致「旧数据覆盖新数据」——这也是排障时要最先怀疑的点。

## 三、YAML Pipeline：整库同步一段配置

```yaml
source:
  type: mysql
  hostname: mysql
  port: 3306
  username: cdc_user
  password: ${DB_PASSWORD:change-me}
  tables: blog.\.*            # 整库：正则匹配所有表
  server-id: 5400-5404

sink:
  type: elasticsearch         # 或 kafka / doris / starrocks / paimon / iceberg ...
  name: es-sink

route:
  - source-table: blog\._.*
    sink-table: search\.<table-name>

pipeline:
  name: blog-to-es
  parallelism: 2
```

```shell
bash bin/flink-cdc.sh mysql-to-es.yaml
# 期望：作业提交成功，Flink Web UI 中看到 source / sink 两个算子且数据量在涨
```

三个高频配置语义：

- **`tables` 用正则**：`blog.\.*` 表示整库；要排除内部表就写清楚白名单，**不要靠后续过滤**。
- **`route` 做表名映射**：多库汇聚或分库合并到同一张表时用它，注意路由规则按顺序匹配。
- **`pipeline.parallelism`**：快照阶段可并行，增量阶段单并行度足够（binlog 是单流）。

## 四、schema 演进与 Exactly-Once

1. **schema 演进**：源库加列时，Pipeline Sink 可按配置同步建列（各 Sink 支持程度不同，以官方连接器文档为准）。**改类型、缩窄类型仍要走变更评审**，不是所有 DDL 都能自动跟。
2. **Exactly-Once 的边界要讲清楚**：Flink CDC 的 exactly-once 语义由 **Flink checkpoint + Sink 的两阶段提交/幂等写**共同保证，且**只覆盖「从源库读 → 写 Sink」这一段**。源库 binlog 被清理导致位点失效时，照样只能全量重灌——一致性语义救不了运维事故。
3. **checkpoint 间隔**是延迟与恢复成本的权衡：间隔太长，故障恢复要回放更多；太短，checkpoint 开销占比升高。常规起点 1~5 分钟。

## 五、与 Debezium 的关系

Flink CDC 的 MySQL / PostgreSQL 连接器**内部复用了 Debezium 的连接器引擎**——所以 [Debezium](../Debezium/index.md) 页讲的快照模式、事件信封、schema history 在 Flink CDC 里同样成立，只是暴露配置的路径不同。两者分工：**Debezium 是「把变更变成事件流」的组件；Flink CDC 是「把变更集成到目标存储」的作业框架**。需要流计算转换时用 Flink CDC，只需要事件流时用 Debezium 更轻。

## 六、验证方式

```shell
# ① 提交作业并确认运行
bash bin/flink-cdc.sh mysql-to-es.yaml
# 期望：Flink Web UI 显示作业 RUNNING，无 restart 异常

# ② 源库造变更，核对目标库
mysql -uroot -p blog -e "UPDATE posts SET title='flink-cdc-probe' WHERE id=1;"
# 期望：目标端（ES / Kafka / Doris）中该行在秒级更新

# ③ 源库加列，核对 schema 演进
mysql -uroot -p blog -e "ALTER TABLE posts ADD COLUMN read_count INT NOT NULL DEFAULT 0;"
# 期望：目标端表结构出现新列（以所选 Sink 的支持矩阵为准）

# ④ 杀掉 TaskManager 再重启，核对无重复、无丢失
# 期望：恢复后同一行数据以最新值为准，行数与源库一致
```

## 参考资料

- Flink CDC 官方文档：https://nightlies.apache.org/flink/flink-cdc-docs-stable/
- Flink CDC 3.6.0 发布公告：https://flink.apache.org/news/2026/03/30/release-cdc-3.6.0.html
- Apache Flink 下载页（版本矩阵）：https://flink.apache.org/downloads/
- Flink CDC 仓库：https://github.com/apache/flink-cdc
- 下一页：[一致性保障](../Consistency/index.md)
