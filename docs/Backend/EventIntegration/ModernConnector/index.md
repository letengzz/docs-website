# 当前主线采集栈

这一页只回答一件事：**新项目按哪套配置契约搭采集栈**。它不重复讲工具怎么安装、也不讲 binlog 原理（那在[数据同步与 CDC](../../../DB/CDC/index.md)），只把「会导致事件契约不成立」的配置项写清楚，并给出可核对的上线清单。旧线上配置请看[旧版采集栈（仅存量项目使用）](../LegacyConnector/index.md)。

本页判据族 `EMC-A` ~ `EMC-H`，共 8 条。

## 一、版本基线

版本事实联网核对（2026-11-11 检索，以官方页面为准）：

| 组件 | 当前版本 | 发布日 | 来源 |
| --- | --- | --- | --- |
| Debezium（稳定） | **3.7.1.Final** | 2026-11-06 | [Debezium Releases](https://debezium.io/releases/) |
| Debezium（开发中） | 3.8.0.Alpha1 | 2026-11-02 | 同上，不用于生产 |
| Debezium（旧稳定线） | 2.7.4.Final | 2024-12-11 | 同上，见[旧版目录](../LegacyConnector/index.md) |
| Apache Kafka | **4.4.0** | 2026-10-22 | [Kafka Downloads](https://kafka.apache.org/downloads) |

::: info 版本口径
本册的判据（事务边界、契约、顺序、接缝、对账）不随产品版本变化，所以正文按「问题」分章；这里只固定**配置契约**的版本。小版本补丁不需要单独建目录，用本页表格说明即可（对应 `AGENTS.md` 第 3 节第 3 条）。涉及 Java / Kafka Connect 的运行时版本要求，请以官方安装与部署文档为准，本页不写死未核对的版本号。
:::

## 二、当前配置契约（完整示例）

```properties [connector-current.properties]
name=order-connector
connector.class=io.debezium.connector.mysql.MySqlConnector
tasks.max=1

database.hostname=mysql-primary
database.port=3306
database.user=debezium
database.password=${env:DEBEZIUM_PASSWORD}
database.server.id=154011
topic.prefix=orderdb
table.include.list=orderdb.orders,orderdb.order_items,orderdb.debezium_signals

# 快照：当前有效取值，不用弃用的 schema_only
snapshot.mode=initial

# 内部 schema history：官方明确要求单分区
schema.history.internal.kafka.topic=internal.orderdb.history
schema.history.internal.kafka.bootstrap.servers=kafka:9092

# 增量快照：信号表必须在 include.list 里，且连接器账号有写权限
signal.data.collection=orderdb.debezium_signals
signal.enabled.channels=source

# 事件形状：保留完整前镜像所需的数据库侧配置见第 2 章
decimal.handling.mode=string
```

官方 [MySQL Connector 配置文档](https://debezium.io/documentation/reference/stable/connectors/mysql.html) 中 `snapshot.mode` 的当前取值为：

| 取值 | 含义 |
| --- | --- |
| `always` | 每次启动都做快照，然后继续流式 |
| `initial` | 默认值，首次快照后继续流式 |
| `initial_only` | 只快照，完成后停止 |
| `no_data` | 只捕获结构，不生成表示现存数据的 READ 事件 |
| `recovery` | 从源表重建损坏/丢失的 schema history topic |
| `when_needed` | 无位点或位点已不可用时才快照 |
| `configuration_based` | 由一组 `snapshot.mode.configuration.based.*` 属性控制 |
| `custom` | 注入自定义 `Snapshotter` 实现 |

`schema_only` / `schema_only_recovery` 标 **Deprecated**（分别指向 `no_data` / `recovery`），`never` 不在取值表。这张表是[旧版迁移映射](../LegacyConnector/index.md)的依据。

::: warning `recovery` 不能随便用
官方明确警告：若连接器上次关闭之后源库又提交过 schema 变更，不要用 `recovery` 模式重建 history topic。它适用于「history 丢了但结构没变」的窄场景；其余情况应保留原 topic 或从备份恢复。
:::

## 三、信号表与增量快照

新表加进 `table.include.list` **不会自动回填历史数据**，需要发一个 `execute-snapshot` 信号触发增量快照。官方列出的前提：信号机制已启用、源库存在信号数据集合、由 `signal.data.collection` 指定、连接器账号有写权限（只读增量快照例外）。

```sql [V5__signal_table.sql]
CREATE TABLE IF NOT EXISTS orderdb.debezium_signals (
  id     VARCHAR(255) PRIMARY KEY,
  type   VARCHAR(255) NOT NULL,
  data   VARCHAR(2048)
);
GRANT SELECT, INSERT, UPDATE, DELETE ON orderdb.debezium_signals TO 'debezium'@'%';
```

```sql [trigger-ad-hoc-snapshot.sql]
INSERT INTO orderdb.debezium_signals(id, type, data)
VALUES ('snap-2026-11-11-01', 'execute-snapshot',
        '{"data-collections":["orderdb.order_items"],"type":"INCREMENTAL"}');
```

三条纪律：

1. **信号表要进 `table.include.list`**，否则连接器读不到信号；官方文档说明 MySQL 表名格式为 `database.table` 且大小写敏感。
2. **水位写进信号表**：open/close 水位夹住 chunk 扫描窗口，这正是[快照与增量接缝](../SnapshotHandoff/index.md)里 `T0/T1` 的块级版本。
3. **只读增量快照有额外前提**：MySQL 需开启 GTID；从多线程副本读取且 `replica_parallel_workers > 0` 时，还需 `replica_preserve_commit_order=ON`（或旧名 `slave_preserve_commit_order=ON`）。

## 四、schema history 与位点

| 对象 | 约束 | 违反后果 |
| --- | --- | --- |
| `schema.history.internal.kafka.topic` | **partition count = 1**（官方明确要求）、无限期保留 | 重启后无法按位点重建表结构 |
| 连接器位点 | 持久化在 broker 的 offsets topic，按连接器名隔离 | 位点丢失 → 不知从哪条日志继续 |
| 源库日志保留 | 覆盖最长停机窗口 | 日志被清理 → 位点失效，只能重快照 |

::: danger 三个上线前最容易漏的配置
1. **history topic 被 broker 自动创建成多分区**：官方要求手动创建时分区数为 1，或把 broker 的 `num.partitions` 设为 1。这个错误在首次启动时不报错，只在某次重启时暴露。
2. **把信号表漏在 `table.include.list` 之外**：平时没有问题，第一次想回填新表时才发现 `execute-snapshot` 发不出去。
3. **只配 `snapshot.mode=initial` 就宣布「新表也有历史」**：`initial` 只在连接器首次启动时执行；后来加进来的表需要显式触发增量快照。
:::

## 五、上线前核查表

| 项 | 检查方式 | 预期 |
| --- | --- | --- |
| 配置里无弃用值 | 检索 `schema_only` / `never` | 0 命中 |
| history topic 分区数 | topic describe | 1 |
| 信号表在 include list | 配置与 DDL 对照 | 存在且有写权限 |
| 事件带解释版本 | 抽样一条事件 JSON | `schema_version` 非空 |
| 位点来源 | 抽样一条事件 JSON | `source` 里有位点字段 |
| 接缝演练 | 按[快照接缝](../SnapshotHandoff/index.md)七项清单跑一遍 | 全通过 |
| 下游门禁 | [实战](../Practice/index.md)十条断言 | 10/10 PASS |

## 本页判据

| 判据 | 约定 | 定错了会怎样 | 怎么验证 |
| --- | --- | --- | --- |
| `EMC-A` | 新项目只用当前稳定版，Alpha 不进生产 | 生产跑开发中版本 | 部署清单版本号为 3.7.1.Final |
| `EMC-B` | 配置无 `schema_only` / `never` 等弃用值 | 校验失败或快照行为不符 | 检索 0 命中 |
| `EMC-C` | `snapshot.mode` 从当前八项取值中选并写明理由 | 默认值被当成决策 | 配置注释有选型理由 |
| `EMC-D` | history topic 单分区且无限保留 | 重启后无法重建结构 | 分区数 = 1、retention = -1 |
| `EMC-E` | `signal.data.collection` 已配且信号表可写 | 无法触发增量快照 | 发一次信号收到 chunk 事件 |
| `EMC-F` | 新表历史数据靠显式信号回填 | 下游缺历史行 | 回填后分块校验和一致 |
| `EMC-G` | 只读增量快照先核 GTID 与提交顺序前提 | 水位不可靠、窗口错乱 | 前提清单逐项打勾 |
| `EMC-H` | 旧版映射只在[旧页](../LegacyConnector/index.md)维护 | 两代写法混成一份通用配置 | 本页不含旧写法样例 |

## 验证方式

在自己的 Kafka / 数据库环境里按顺序执行（命令给出形式，具体地址按实际环境替换）：

```shell
# 1) 确认配置里没有弃用值
grep -nE 'schema_only|snapshot.mode=never' connector-current.properties
# 预期：无输出（0 命中）

# 2) 确认 history topic 分区数（官方要求 1）
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic internal.orderdb.history
# 预期：PartitionCount: 1

# 3) 触发一次增量快照信号后，观察 topic 是否出现 READ 事件
# 预期：chunk 事件可识别，且带 open/close 水位

# 4) 抽样一条事件，确认信封字段齐全
# 预期：event_id / op / schema_version / source.lsn / source.snapshot 均非空
```

收尾判据：按[实战页](../Practice/index.md)跑一次端到端断言，输出 `10/10 PASS / EXIT=0`；再按[快照接缝](../SnapshotHandoff/index.md)第七节清单确认 0 行回退。两项都绿，才说明采集栈不只是「起来了」，而是「事件契约成立」。

## 参考资料

- [Debezium Releases（版本与发布日期）](https://debezium.io/releases/)
- [Debezium MySQL Connector 配置文档](https://debezium.io/documentation/reference/stable/connectors/mysql.html)
- [Debezium：Incremental Snapshot 与 Signaling](https://debezium.io/documentation/reference/stable/connectors/mysql.html#mysql-incremental-snapshots)
- [Debezium：Signaling 机制](https://debezium.io/documentation/reference/stable/signalling.html)
- [Apache Kafka Downloads](https://kafka.apache.org/downloads)
