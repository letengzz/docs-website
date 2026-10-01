# 日志体系

<p style="text-align:center;"><img src="./assets/logsystem-logo.png" alt="日志体系" style="zoom:75%;" /></p>

日志体系把散落在成千上万台机器上的日志，变成**可采集、可存储、可检索、可告警、可关联**的统一资产。它是指标与链路之外的可观测性第三支柱，也是排障时唯一能回答“**到底错在哪一行**”的数据来源。

本专题覆盖：选型决策、采集与传输、Elastic Stack（ELK）、Grafana Loki、查询与分析、告警联动、保留与成本控制，以及一套可照着跑通的集中式日志平台实战。

- [日志体系概述](Overview/index.md)
- [日志采集与传输](Collection/index.md)
- [Elastic Stack（ELK）](ElasticStack/index.md)
- [Grafana Loki](Loki/index.md)
- [日志查询与分析](QueryAnalysis/index.md)
- [日志告警与联动](Alerting/index.md)
- [存储、保留与成本优化](Retention/index.md)
- [实战：搭建集中式日志平台](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

::: tip 三条最容易过期的结论（2026-09 核对）
1. **Promtail 已于 2026-03-02 EOL**，并从 Loki 3.7.3 起移除，新项目请直接使用 **Grafana Alloy**。
2. **Loki 的 `boltdb-shipper` 索引已弃用**，默认是 TSDB（schema v13），计划在 Loki 4.0 移除。
3. **Elasticsearch 7.x 已于 2026-01-15 停止维护**，新部署请用 9.5.x（当前 9.5.3），存量集群升级走 8.19.x 跳板。
:::

## 相关专题与分工

可观测性三支柱里，本专题只负责**日志**这一根，另外两根各有归属：

- [监控告警](../Monitoring/index.md)：负责**指标**——Prometheus 抓什么、Grafana 怎么画、Alertmanager 怎么触达人，以及 RED 指标与探针那套约定。日志回答「**错在哪一行**」，指标回答「**现在健不健康**」；告警大多从指标触发，定位几乎都要落到日志，所以两边的标签（`service`、`pod`、`route`）必须能对齐。
- [服务网格：可观测性](../ContainerOrchestration/ServiceMesh/Observability/index.md)：网格的数据面代理会**无侵入**地产生访问日志、`istio_requests_total` 这类指标与分布式追踪 span——不改一行业务代码就能拿到服务间的黄金信号（延迟、流量、错误、饱和度）。分工是：**网格负责服务间调用的三段式数据与跨服务 trace 上下文传播**，本专题负责**应用自己打出来的结构化日志**怎么采、存多久、怎么查、怎么告警。两者最终在 Kibana / Loki 里汇合，用 `trace_id` 把「网格看到的耗时」与「应用打出的那一行异常」串起来——这也是排一个跨服务超时问题的标准动作。
- [时序数据库](../../DB/TimeSeries/index.md)：本专题讲日志的保留与成本控制，长期指标存储与降采样在那一边。
