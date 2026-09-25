# 日志监控

指标告诉你“系统坏了”，日志告诉你“**为什么**坏了”。日志监控 = 统一采集 + 集中存储 + 快速检索 + 异常告警。本页从监控体系视角给出日志监控的定位与速览配置；日志平台的完整建设（选型、采集器、ELK/Loki、查询、保留与成本）见专题 [日志体系](../../LogSystem/index.md)。

![日志流水线（Loki 方案）](../assets/log-pipeline.svg)

## 日志在可观测性中的位置

| 信号 | 回答的问题 | 在监控体系中的角色 |
| --- | --- | --- |
| 指标 Metrics | 现在健康吗 | 第一层告警（阈值、趋势） |
| **日志 Logs** | 具体错在哪 | 第二层定位（异常类型、堆栈、业务上下文） |
| 链路 Traces | 慢在哪个环节 | 第三层追因（跨服务调用关系） |

配合顺序：**指标告警 → 日志定位 → 链路追因**。三个信号由同一个 `traceId` 串起来时，排障效率最高。

## 为什么需要统一日志平台

微服务时代日志散落在几十台机器：

1. 出问题要一台台 SSH 上去 `grep`，效率极低。
2. 同一请求的日志分布在多个服务，难以串联（需 traceId）。
3. 容器删除后日志随之消失，故障现场丢失。
4. 磁盘被日志写满，应用崩溃。
5. 没有保留策略，日志无限增长，成本失控。

统一日志平台一次性解决：采集、存储、检索、告警、关联。

## Loki vs ELK（速览）

| 维度 | Loki | ELK（Elasticsearch） |
| --- | --- | --- |
| 索引方式 | 只索引标签，不建全文索引 | 全文倒排索引 |
| 存储成本 | 低（压缩 + 对象存储） | 高（索引 + 副本） |
| 查询语言 | LogQL | KQL / Lucene / ES\|QL |
| 集成 | 与 Grafana 原生一体 | Kibana |
| 适用 | 日志量大、预算有限、Grafana 用户 | 复杂全文检索、安全分析 |
| 版本（2026-09 核对） | 3.7.7 | Elastic Stack 9.5.3 |

::: tip 选型一句话
团队已用 Grafana → 选 **Loki**；需要复杂全文检索 / 安全分析 / 合规 → 选 **ELK**。详细对比见 [日志体系 · 技术选型](../../LogSystem/Overview/index.md#技术选型)。
:::

::: danger 版本提醒（2026-09 核对）
1. **Promtail 已于 2026-03-02 EOL**，并自 Loki **3.7.3** 起被移除，采集请改用 **Grafana Alloy**。
2. Loki 的 `boltdb-shipper` 索引已弃用，默认使用 **TSDB（schema v13）**。
3. Elasticsearch **7.x 已于 2026-01-15 停止维护**，请升级到 8.19.x 或 9.x。
:::

## 日志规范（采集前先立规矩）

### 结构化日志

```json
{"time":"2026-09-13T10:00:00+08:00","level":"ERROR","service":"order-service","traceId":"abc123","message":"库存不足","orderNo":"1001"}
```

### 标签设计

标签用于索引，**基数要低**：

```text
✓ 好标签：job、level、service、pod、container、env
✗ 坏标签：traceId、orderNo、user_id（高基数，应放结构化元数据或日志正文）
```

## 速览：部署 Loki + Alloy + Grafana

```yaml [docker-compose.yml]
services:
  loki:
    image: grafana/loki:3.7.7
    container_name: loki
    ports: ["3100:3100"]
    volumes: [loki-data:/loki]
    command: -config.file=/etc/loki/local-config.yaml

  alloy:
    image: grafana/alloy:latest
    container_name: alloy
    command: ["run", "/etc/alloy/config.alloy", "--server.http.listen-addr=0.0.0.0:12345"]
    volumes:
      - ./config.alloy:/etc/alloy/config.alloy:ro
      - ./logs:/var/log/app:ro
    depends_on: [loki]

volumes:
  loki-data: {}
```

```hcl [config.alloy]
local.file_match "app" {
  path_targets = [{ __path__ = "/var/log/app/*.log", job = "order-service" }]
}

loki.source.file "app" {
  targets    = local.file_match.app.targets
  forward_to = [loki.process.parse.receiver]
}

loki.process "parse" {
  forward_to = [loki.write.default.receiver]

  stage.json {
    expressions = { level = "level", service = "service", trace_id = "traceId" }
  }
  stage.labels {
    values = { level = "", service = "" }
  }
  stage.structured_metadata {
    values = { trace_id = "" }        # traceId 不做标签，避免流数量爆炸
  }
}

loki.write "default" {
  endpoint { url = "http://loki:3100/loki/api/v1/push" }
}
```

验证：`curl http://localhost:3100/ready` 返回 `ready`，且往日志目录写入一条日志后能在 Grafana Explore 中查到。

## LogQL 速览

``` text
# 按标签过滤 + 关键字
{job="order-service"} |= "ERROR"

# 解析 JSON 后按字段过滤
{job="order-service"} | json | level="ERROR"

# 统计错误数量（把日志变成指标，可直接用于告警）
sum(count_over_time({job="order-service"} | json | level="ERROR" [5m])) > 50
```

## 日志告警速览

Grafana 告警支持 Loki 数据源：

```text
Alert rule 查询：sum(count_over_time({job="order-service"} |= "ERROR" [5m])) > 50
评估：每 1m，for 5m（防抖动）
路由：severity=P1 → 值班 IM 群
```

日志告警的完整设计（三种模式、降噪、分级路由）见 [日志告警与联动](../../LogSystem/Alerting/index.md)。

## 日志与链路关联

1. 应用日志统一输出 `traceId`。
2. Grafana 的 Loki 数据源配置派生字段后，点击日志行中的 traceId 可直接跳到链路视图。
3. 反之，链路视图的 Span 也可以关联回日志。

```yaml
# Grafana 数据源 Loki 配置片段
jsonData:
  derivedFields:
    - name: traceId
      matcherRegex: '"traceId":"(\\w+)"'
      url: "http://skywalking-ui:8080/trace?traceId=${__value.raw}"
```

## 易错点与最佳实践

::: danger 常见错误
1. **标签高基数**：把 traceId/订单号当标签，Loki 索引与流数量爆炸。
2. **日志不打 traceId**：跨服务无法串联，排障回到“石器时代”。
3. **容器日志不采集**：容器一删日志就没，故障现场丢失。
4. **采集端单点**：采集器挂了日志断流；应配置多副本/自愈。
5. **明文敏感信息入日志**：密码、Token 打进日志，安全审计不通过。
6. **还在用 Promtail**：已 EOL，需迁移到 Grafana Alloy。
:::

::: tip 最佳实践
1. 统一日志格式：JSON + level + service + traceId。
2. 日志级别规范：INFO 记业务、WARN 记异常、ERROR 记故障；禁止 DEBUG 上生产。
3. ERROR 日志必须可操作：带上业务主键、堆栈、上下文。
4. 敏感信息脱敏后再落盘。
5. 保留策略分级，成本与排查能力平衡。
6. 日志告警与指标告警配合：指标先报，日志定位。
:::

## 验证方式

1. 启动 Loki + Alloy，往日志目录写一条测试日志，Grafana 日志面板能检索到。
2. 用 LogQL 过滤 `ERROR`，确认只返回错误日志。
3. 配置日志数量告警，批量制造错误日志，确认告警触发。
4. 点击日志中的 traceId，验证跳转到链路追踪视图。

## 深入阅读

| 想了解 | 去哪里 |
| --- | --- |
| 技术选型与整体框架 | [日志体系概述](../../LogSystem/Overview/index.md) |
| 采集器（Alloy / Fluent Bit / Vector）与 K8s 采集 | [日志采集与传输](../../LogSystem/Collection/index.md) |
| ELK 的索引、ILM 与写入优化 | [Elastic Stack（ELK）](../../LogSystem/ElasticStack/index.md) |
| Loki 架构、标签设计与生产部署 | [Grafana Loki](../../LogSystem/Loki/index.md) |
| KQL / ES\|QL / LogQL 与分析六步法 | [日志查询与分析](../../LogSystem/QueryAnalysis/index.md) |
| 日志告警模式与降噪 | [日志告警与联动](../../LogSystem/Alerting/index.md) |
| 保留策略与成本优化 | [存储、保留与成本优化](../../LogSystem/Retention/index.md) |
| 端到端落地 | [实战：搭建集中式日志平台](../../LogSystem/Practice/index.md) |
| 排障速查 | [日志体系常见问题](../../LogSystem/FAQ/index.md) |

## 参考资料

- Grafana Loki 文档：https://grafana.com/docs/loki/latest/
- LogQL 参考：https://grafana.com/docs/loki/latest/query/
- Grafana Alloy 文档：https://grafana.com/docs/alloy/latest/
- Promtail 迁移到 Alloy：https://grafana.com/docs/alloy/latest/set-up/migrate/from-promtail/
- ELK（Elastic Stack）：https://www.elastic.co/guide/
