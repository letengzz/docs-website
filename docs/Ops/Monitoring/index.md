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
