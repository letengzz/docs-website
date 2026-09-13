# 存储、保留与成本优化

日志是**只增不减**的数据：只要系统在跑，日志就在产生。日志平台的账单里，**存储与索引通常占 60%~80%**，而绝大多数被存下来的日志**永远不会被查询**。因此“日志体系”的工程能力，很大程度体现在**保留策略与成本控制**上。

本页讲清成本构成、分层存储、数据缩减手段、容量估算方法，并给出一套可直接套用的分级保留方案。

![日志分层存储与生命周期](../assets/log-lifecycle.svg)

## 成本从哪里来

| 成本项 | 占比（经验值） | 说明 |
| --- | --- | --- |
| 存储（对象存储 / 块存储） | 40%~60% | 日志原始体积 × 压缩比 × 保留天数 |
| 索引与元数据 | 10%~25% | ES 的倒排索引、Loki 的 TSDB 索引 |
| 副本冗余 | 0%~200% | ES 副本数直接翻倍成本；Loki 靠对象存储自身冗余 |
| 计算（采集/解析/查询） | 10%~25% | 采集器 CPU、解析器、查询节点 |
| 网络出口 | 5%~15% | 跨可用区/跨云传输 |
| 人力运维 | 难以量化 | 集群调优、故障处理 |

::: tip 结论先行
**降本的第一优先级不是换存储，而是“少存、早删、分级”。** 把 DEBUG 日志在生产关掉、把健康检查日志丢弃、把 ERROR 保留 30 天而不是 365 天，收益远大于任何压缩算法调优。
:::

## 分层存储

### Elasticsearch 的 ILM 分层

| 层 | 硬件 | 数据状态 | 查询能力 | 相对成本 |
| --- | --- | --- | --- | --- |
| **hot** | SSD，高配 | 正在写入 | 全能力 | 高 |
| **warm** | SSD/HDD，中配 | 只读、已 forcemerge | 全能力 | 中 |
| **cold** | HDD，低配 | 只读、副本可降为 0 | 可查，稍慢 | 低 |
| **frozen** | 对象存储 + 可搜索快照 | 按需加载 | 查询明显变慢 | 极低 |
| **delete** | —— | 删除 | —— | 0 |

```json
{
  "policy": {
    "phases": {
      "hot":    { "actions": { "rollover": { "max_primary_shard_size": "40gb", "max_age": "1d" } } },
      "warm":   { "min_age": "3d",  "actions": { "shrink": { "number_of_shards": 1 }, "forcemerge": { "max_num_segments": 1 }, "set_priority": { "priority": 50 } } },
      "cold":   { "min_age": "15d", "actions": { "set_priority": { "priority": 0 }, "readonly": {} } },
      "frozen": { "min_age": "45d", "actions": { "searchable_snapshot": { "snapshot_repository": "found-snapshots" } } },
      "delete": { "min_age": "90d", "actions": { "delete": {} } }
    }
  }
}
```

::: warning frozen 层的前提
`searchable_snapshot` 需要先注册**快照仓库**；部分可搜索快照能力与订阅层级相关，落地前请对照官方订阅页确认。小规模集群通常不需要 frozen 层，cold 层 + 更短的保留期更划算。
:::

### Loki 的分层

| 层 | 存储位置 | 保留 | 说明 |
| --- | --- | --- | --- |
| 内存/本地 | ingester 内存 + WAL | 近 1~2 小时 | 查询最近数据最快 |
| 热 | 对象存储 | 7~15 天 | chunk 按块读取 |
| 冷 | 对象存储（不同 bucket / 更廉价存储类） | 30~180 天 | 用 `retention_stream` 指定不同存储桶 |
| 删除 | —— | —— | compactor 执行 |

```yaml [Loki 分级保留 + 独立冷存储桶]
limits_config:
  retention_period: 360h                     # 默认 15 天
  retention_stream:
    - selector: '{level="ERROR"}'
      priority: 10
      period: 2160h                          # 90 天
    - selector: '{job="nginx-access"}'
      priority: 5
      period: 168h                           # 7 天
    - selector: '{job="audit"}'
      priority: 20
      period: 4320h                          # 180 天
      # 可指定独立的存储桶（需在 common.storage 中定义）
      # location: s3://audit-archive

compactor:
  retention_enabled: true
  retention_delete_delay: 2h
  delete_request_store: s3
```

## 数据缩减：五个层次的减法

从“最省事”到“最彻底”排序：

| 层次 | 手段 | 典型收益 | 风险 |
| --- | --- | --- | --- |
| ① 源头不产生 | 生产关闭 DEBUG、去掉健康检查/心跳日志 | 30%~70% | 排查时信息变少 |
| ② 采集端丢弃 | Vector `filter` / Alloy `stage.drop` 按条件丢 | 20%~50% | 规则过宽会丢关键信息 |
| ③ 采集端压缩/采样 | 访问日志按比例采样、gzip/zstd 压缩 | 50%~90%（体积） | 采样后无法精确计数 |
| ④ 存储端压缩 | chunk 压缩、列式压缩、forcemerge | 60%~90% | 查询时需解压，CPU 上升 |
| ⑤ 保留期缩短 | 按级别分级保留 | 与天数线性相关 | 合规要求需先确认 |

::: danger 采样会破坏“可计数”能力
按 1/100 采样后，`count_over_time` 得到的是**采样数而不是真实数**。如果需要用日志做错误率统计或告警，就**不要对这类日志采样**——采样只适用于“仅用于排障”的高流量访问日志。
:::

## 容量估算

### 公式

```text
日增量（存储） = 原始日志体积/天 × 索引膨胀系数 ÷ 压缩比 × (1 + 副本数)

总容量 = 日增量 × 保留天数 × (1 + 安全余量 30%)
```

经验参数：

| 参数 | Elasticsearch | Loki |
| --- | --- | --- |
| 索引膨胀系数 | 1.1 ~ 1.5（取决于字段数与 mapping） | 1.01 ~ 1.03（只有 TSDB 索引） |
| 压缩比 | 与源数据相关；结构化 JSON 通常 3:1 ~ 6:1 | 通常 5:1 ~ 10:1（zstd/gzip 后按块存） |
| 副本数 | 通常 1（总占用 ×2） | 依靠对象存储冗余，通常不再乘副本 |

### 示例：100GB/天 的系统

| 项目 | ELK 方案 | Loki 方案 |
| --- | --- | --- |
| 原始日志 | 100GB/天 | 100GB/天 |
| 索引膨胀系数 | ×1.3 | ×1.02 |
| 压缩比 | ÷4 | ÷8 |
| 副本 | ×2（1 副本） | —— |
| **日增量** | 100 × 1.3 ÷ 4 × 2 ≈ **65GB/天** | 100 × 1.02 ÷ 8 ≈ **12.75GB/天** |
| 保留 30 天 | ≈ 1.95TB | ≈ 383GB |
| 保留 90 天 | ≈ 5.85TB | ≈ 1.15TB |

::: tip 这个数量级差异从哪来
- **Loki 不建全文索引**，省掉索引膨胀与副本冗余；
- **Loki 的压缩在块级别做**，比逐文档压缩更充分；
- **Loki 不需要副本**（对象存储自带多副本）。

代价是 Loki 的全文检索能力弱于 ES。**“用更贵的存储换更强的检索”是否值得，取决于你的查询模式。**
:::

## 分级保留策略模板

可直接抄用的分级表：

| 日志类型 | 热保留 | 温/冷保留 | 归档 | 依据 |
| --- | --- | --- | --- | --- |
| DEBUG / TRACE | **不采集**（生产默认关闭） | —— | —— | 无长期价值 |
| 健康检查 / 心跳 / 探针 | 不采集（或只统计条数） | —— | —— | 高噪声、零信息量 |
| INFO 业务日志 | 7 天 | 15 天 | —— | 排障为主 |
| WARN | 15 天 | 30 天 | —— | 需观察趋势 |
| ERROR / 异常堆栈 | 30 天 | 90 天 | 180 天（对象存储） | 故障复盘、质量分析 |
| 访问日志（Nginx/网关） | 7 天（可采样） | 30 天（可聚合） | —— | 流量分析 |
| 数据库慢查询 | 15 天 | 90 天 | —— | 性能优化依据 |
| 审计日志（登录、权限变更、数据导出） | 90 天 | 180 天 | **按合规要求长期留存** | 合规、追溯 |
| 容器/K8s 事件 | 7 天 | —— | —— | 生命周期短 |
| 云平台审计 | 按云厂商默认 | —— | 转储对象存储 | 云厂商保留策略 |

::: info 关于合规留存
行业（金融、医疗、电信等）与等级保护对日志留存期限有具体要求，且可能因地区与业务类型而异。**本文给出的天数仅是工程实践建议，落地前必须以所属行业的现行规范与法务意见为准。**
:::

## 实战：为 100GB/天 系统设计保留方案

**需求**：20 个微服务、50 个 Pod、日志量约 100GB/天、有 5 人研发团队、故障平均每周 2 次、需要支持 90 天内的历史日志回溯。

**方案**（Loki + 对象存储）：

```yaml [loki-config.yaml 关键片段]
limits_config:
  retention_period: 168h                     # 默认 7 天（INFO 类）
  retention_stream:
    - selector: '{level="ERROR"}'
      priority: 10
      period: 2160h                          # 90 天
    - selector: '{level="WARN"}'
      priority: 5
      period: 720h                           # 30 天
    - selector: '{job="audit"}'
      priority: 20
      period: 4320h                          # 180 天
  # 限制写入速率，防止单租户把集群打满
  ingestion_rate_mb: 32
  ingestion_burst_size_mb: 64
  per_stream_rate_limit: 8MB
  per_stream_rate_limit_burst: 16MB

compactor:
  retention_enabled: true
  retention_delete_delay: 2h
  delete_request_store: s3
```

**采集端先做减法**：

```hcl [Alloy：丢弃噪声日志]
loki.process "filter_noise" {
  forward_to = [loki.write.default.receiver]

  stage.drop {
    expression  = "(?i)(healthcheck|/actuator/health|readiness|liveness)"
    drop_counter_reason = "health_check"
  }
  stage.drop {
    expression  = "level=DEBUG"
    drop_counter_reason = "debug_level"
  }
}
```

**成本估算（相对值，以实际云账单为准）**：

| 项目 | 数值 |
| --- | --- |
| 原始日志 | 100GB/天 |
| 采集端丢弃后 | ≈ 60GB/天（丢掉健康检查与 DEBUG） |
| 存储日增量（Loki 估算） | ≈ 6GB/天 |
| 热层保留 7 天 | ≈ 42GB |
| ERROR 保留 90 天（约占总量的 5%） | 60×0.05×1.02÷8×90 ≈ 34GB |
| WARN 保留 30 天（约 10%） | ≈ 23GB |
| 审计 180 天（约 2%） | ≈ 28GB |
| **合计对象存储** | **≈ 130GB 量级** |

对比“不做任何裁剪、全部保留 90 天”的粗放方案（≈ 690GB），**降幅接近 80%**，而排障能力几乎不受影响。

**验证降本是否生效**：

```logql
# 1. 各服务日志字节速率（找出「话最多」的服务）
sum by (service) (bytes_rate({env="prod"}[1h]))

# 2. 噪声日志是否已被丢弃（应返回空）
{env="prod"} |~ "(?i)healthcheck|/actuator/health"

# 3. 保留策略是否生效：查询超过保留期的数据应返回空
{level="DEBUG"}    # 期望无结果
```

## 易错点与最佳实践

::: danger 常见错误
1. **默认永久保留**：`retention_period` 不配或没开 compactor，数据只增不减，最终磁盘 100% 打满。
2. **只配保留期不开 compactor**：Loki 的 `retention_period` **必须**配合 `compactor.retention_enabled: true` 才真正删除数据。
3. **保留期长于合规要求**：多存的都是纯成本；合规要求 6 个月的日志留 3 年没有任何收益。
4. **副本数“为了安全”设 3**：日志不是交易数据，热层 1 副本 + 对象存储冗余足够。
5. **生产开 DEBUG**：日志量放大 10 倍，成本与噪声同步放大。
6. **采样后又用日志做精确统计**：数字对不上，还找不到原因。
7. **不做容量规划**：上线 3 个月后磁盘告警，被迫紧急删数据。
8. **把审计日志和业务日志放同一保留策略**：要么合规不达标，要么业务日志被迫超期保存。
:::

::: tip 最佳实践
1. **按“查询价值”而不是“日志类型”设计保留**：会被查的留久，不会查的早删。
2. **审计日志单独一条流**：独立标签、独立保留、独立权限（只读、不可删）。
3. **给存储设硬上限**：Loki 的 `storage.total_limit_size`、ES 的磁盘水位线，防止写爆磁盘。
4. **每月复盘一次用量**：`bytes_rate` 按服务排名，找出日志量 Top 3 的服务去优化。
5. **成本纳入监控**：把对象存储用量、ES 磁盘使用率做成看板上墙。
6. **变更保留期先确认合规**：缩短保留期可能违反合规要求，必须走审批。
:::

## 验证方式

1. **保留期生效**：配置 `retention_period: 168h` 后，尝试查询 8 天前的日志，确认返回为空（`logcli` 或 API）。
2. **compactor 在跑**：`curl -s http://localhost:3100/metrics | grep loki_compactor_runs_started_total` 有非零计数。
3. **丢弃规则生效**：`{env="prod"} |= "healthcheck"` 返回空，说明采集端过滤已生效。
4. **容量趋势**：观察对象存储桶的日增量与估算值是否吻合（偏差 > 50% 说明压缩比或估算参数需要修正）。
5. **水位线告警**：确认 ES 磁盘水位线 / 对象存储配额告警已配置并在正常状态。

## 相关专题

- [日志体系概述](../Overview/index.md)：日志生命周期与成本分布
- [Grafana Loki](../Loki/index.md)：`retention_stream` 与 compactor 配置
- [Elastic Stack（ELK）](../ElasticStack/index.md)：ILM 与 Data Stream
- [日志采集与传输](../Collection/index.md)：采集端过滤与丢弃
- [监控体系与可观测性](../../Monitoring/Overview/index.md)：容量规划与监控指标
- [Redis 进阶 · 缓存设计](../../../DB/NoRelational/Redis/Advanced/CacheDesign/index.md)：缓存分层思路的同类实践

## 参考资料

- Elastic ILM 与数据层：https://www.elastic.co/guide/en/elasticsearch/reference/current/data-tiers.html
- Elasticsearch 可搜索快照：https://www.elastic.co/guide/en/elasticsearch/reference/current/searchable-snapshots.html
- Loki 保留策略：https://grafana.com/docs/loki/latest/operations/retention/
- Loki 限制配置：https://grafana.com/docs/loki/latest/configure/#limits_config
- Loki Compactor：https://grafana.com/docs/loki/latest/configure/#compactor
- Vector 过滤与采样：https://vector.dev/docs/reference/configuration/transforms/filter/
