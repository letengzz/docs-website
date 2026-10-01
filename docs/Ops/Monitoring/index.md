# 监控告警

<p style="text-align:center;"><img src="./assets/monitoring-logo.png" alt="监控告警" style="zoom:75%;" /></p>

监控告警是运维与研发的“仪表盘 + 报警器”：通过指标、日志、链路三支柱看清系统状态，在故障发生前或发生时第一时间通知责任人。本专题覆盖 Prometheus 指标体系、Grafana 可视化、Alertmanager 告警、Loki 日志监控速览与生产落地实战。

::: tip 日志要不要单独建平台？
本主题的 [日志监控](LogMonitoring/index.md) 只从监控视角给出速览。日志的采集器选型、ELK/Loki 深入、查询语言、保留与成本控制，已沉淀为独立专题：[日志体系](../LogSystem/index.md)。
:::

- [监控体系与可观测性](Overview/index.md)
- [Prometheus 入门](Prometheus/index.md)
- [指标采集](MetricsCollect/index.md)
- [Grafana 可视化](Grafana/index.md)
- [告警规则与 Alertmanager](Alerting/index.md)
- [日志监控](LogMonitoring/index.md)
- [实战：监控微服务与容器环境](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

::: tip 指标存哪里？
Prometheus 本地存储适合短周期（默认 15 天）。要做**几个月到几年的指标长期存储**、降采样与容量治理，见 [时序数据库](../../DB/TimeSeries/index.md) 专题（InfluxDB / TDengine，含建库、降采样与保留策略）。
:::

## 相关专题与分工

- [云原生 · 成本治理（FinOps）](../CloudNative/FinOps/index.md)：本专题讲**技术指标**的采集、看板与告警——Prometheus 抓什么、Grafana 怎么画、Alertmanager 怎么触达到人；该页讲**账单这类特殊「指标」**怎么采集（云厂商账单 API / 成本导出）、怎么按标签归因到团队与项目、怎么定单位成本（每千次请求成本、每订单成本）。两者共用「采集 → 存储 → 展示 → 告警」同一套方法，区别在口径：本专题管「系统健不健康」，该页管「钱花在哪」。
- [服务网格：可观测性](../ContainerOrchestration/ServiceMesh/Observability/index.md)：本专题讲**应用侧要暴露什么**与**平台怎么搭**（RED 三件套、两类探针、Prometheus/Grafana/Alertmanager 的安装与规则）；网格专题讲**不写代码就拿到服务间指标**——数据面代理按统一口径产出请求量、延迟分布与错误码，并把 trace 上下文在各跳之间透传。分工边界：**新服务要接入网格时，网格的黄金信号先顶上，本专题的 RED 指标用来补业务维度（按租户、按商品池这类标签）；两者标签要对齐到同一套 `service`/`route` 命名，否则同一个故障在两张看板上有两个名字。** 标签基数这条铁律在网格指标上同样成立——代理会为每个 upstream 组合生成时间序列，服务数量上千时务必先做指标裁剪。

## 应用侧接入：RED 指标与两类探针

本专题讲的是监控体系的搭建（采集、存储、可视化、告警）。**应用侧要暴露什么**，可以收敛成很少的几个约定——多了没人看，少了定位不了。

### RED 三件套覆盖 90% 的告警需求

| 指标 | 类型 | 标签（**必须有界**） | 回答什么 |
| --- | --- | --- | --- |
| `*_requests_total` | Counter | `method` / `route` / `code` | **Rate**：流量与错误率 |
| `*_request_duration_seconds` | Histogram | `method` / `route` | **Duration**：p50 / p95 / p99 |
| `*_errors_total` | Counter | `route` / `code` | **Errors**：按错误码归因 |

::: danger 注意：标签基数是指标体系的头号杀手
**绝不能把「无界」的值放进标签**：

| 禁止 | 原因 | 正确做法 |
| --- | --- | --- |
| 原始 URL（`/order/12345`） | 每个订单号一条时间序列 | 用**路由模板**（`/order/{order_id}`） |
| 用户 ID / 租户 ID | 基数等于用户数 | 需要时用「维度分桶」或改用日志 |
| 时间戳 / Trace ID | 基数无上限 | 放进日志，不放指标 |
| 错误原文 | 基数不可控 | 用错误**码** |

标签基数爆炸的后果是 Prometheus 内存暴涨甚至 OOM——**指标系统挂掉比业务挂掉更难恢复**（它挂了你连「哪里挂了」都不知道）。
:::

### 两条告警阈值原则

1. **阈值从压测基线来，不要拍脑袋**：压测拿到 p99 与容量拐点后，告警线设在 `p99 × 1.5`，错误率设在 `0.5%`。
2. **业务失败不计入 SLO 错误率**：`InvalidArgument`、`NotFound` 属于正常业务拒绝。把它们算进错误率，结果就是**用户输错一次手机号就触发告警**。实现上按状态码过滤后再统计。

### 两类探针的语义（K8s）

| 探针 | 端点 | 失败动作 | 所以它能查什么 |
| --- | --- | --- | --- |
| `livenessProbe` | `/health` | **重启容器** | **只能查进程自身**——绝不能查 DB / Redis |
| `readinessProbe` | `/ready` | **摘流量，不重启** | 应查所有关键依赖 |

::: warning 说明：把依赖检查放进 liveness 是最危险的一种「优化」
看起来「更严谨」（依赖挂了就重启），实际后果是：**依赖抖动 → 所有副本一起被重启 → 服务全挂**。小故障被放大成了完全中断。

**验收方式**：把 Redis 停掉，`/health` 必须仍是 200，`/ready` 必须变 503。这条检查成本 10 秒，能挡住的是一次全站不可用。
:::

应用侧的具体实现见 [Go 服务治理](../../Backend/GoMicroservices/Governance/index.md)（熔断只统计技术失败、Trace 与日志的 trace_id 对齐）与 [Python 服务部署](../../Backend/PythonWeb/Practice/index.md)（结构化日志、指标标签、探针实现）。

## 相关专题

- [备份与容灾](../../Ops/BackupDR/index.md)：监控是备份体系的「眼睛」——**没有告警的备份任务，会在最需要它的时候发现自己早就停了**。具体做法是暴露 `backup_*_last_success_timestamp` 并配一条新鲜度告警，见 [实战 · 接监控](../../Ops/BackupDR/Practice/index.md)。
- [日志体系](../LogSystem/index.md)：备份脚本的失败详情应当落日志，便于复盘。
- [定时任务](../Linux/Advanced/CronTasks/index.md)：备份通常由 cron / systemd timer 驱动，静默失败需要监控兜底。

