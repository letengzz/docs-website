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
