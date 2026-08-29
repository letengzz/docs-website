# 监控告警常见问题与最佳实践

本页汇总监控体系落地中最常遇到的问题：数据采集中断、指标不显示、告警误报/漏报、存储膨胀、监控自身高可用，以及生产环境的最佳实践清单。

## Targets 显示 DOWN，怎么排查

```text
Prometheus Targets → DOWN
```

按顺序检查：

1. **服务是否启动**：`docker ps` / `systemctl status` 确认目标进程活着。
2. **端口是否监听**：在目标机器 `ss -lntp | grep 9100`。
3. **防火墙/网络策略**：Prometheus 到目标的端口是否放行。
4. **`/metrics` 是否可访问**：`curl http://目标:端口/metrics` 看返回。
5. **地址是否写对**：容器间用服务名，本机用 `localhost`，别写反。
6. **抓取超时**：目标响应慢，`scrape_timeout`（默认 10s）不够。

## 面板没有数据

1. 先用 Prometheus Graph 直接跑查询，确认数据源有数据。
2. 检查指标名是否拼错（`node_cpu_seconds_total` vs `node_cpu`）。
3. 检查标签：面板查询用了 `{instance="..."}`，但实际标签名不同。
4. 时间范围：面板时间范围太短/太长，`rate` 窗口与面板步长不匹配。
5. Grafana 数据源 URL 是否正确（容器内用服务名）。

## 告警误报（噪音）怎么治

| 原因 | 对策 |
| --- | --- |
| 瞬时抖动 | 加 `for`（持续 N 分钟才触发） |
| 阈值太敏感 | 基于压测/历史数据重设阈值 |
| 短时任务 Pushgateway 残留 | 任务结束清理指标 |
| 发布/维护期间 | 用静默或维护窗口标签 |
| 监控目标被摘除 | 明确预期的“下线”流程，临时静默 |

## 告警漏报怎么办

1. **规则是否加载**：`promtool check rules` 校验 + `curl /api/v1/rules` 查看规则状态。
2. **`for` 与评估间隔**：`for` 比评估间隔大太多，延迟触发。
3. **阈值方向**：`>` 还是 `<` 写反。
4. **数据本身缺失**：目标 DOWN 时查询无数据，用 `up == 0` 单独告警。
5. **Alertmanager 路由**：告警发了但路由到没人看的 receiver。

## 存储膨胀，怎么控成本

| 手段 | 说明 |
| --- | --- |
| 缩短保留期 | `retention.time` / `retention.size` 按需设置 |
| 降采样聚合 | 历史数据用 recording rule 聚合后丢弃原始数据 |
| 减少标签基数 | 去掉高基数标签，控制序列数量 |
| 分级存储 | 热数据 Prometheus，冷数据 Thanos/对象存储 |
| 日志分级保留 | Loki 按环境/级别差异化保留 |
| 定期清理 | 删除废弃的 job 与指标（谨慎，先验证） |

## 监控自身挂了怎么办

监控系统本身也要被监控：

1. **高可用**：Prometheus 双实例或 Thanos，Alertmanager 集群部署。
2. **数据持久化**：TSDB 挂卷 + 定期备份。
3. **自监控**：监控 Prometheus 自身（`up{job="prometheus"}`）、磁盘、Grafana 可用性。
4. **外部探测**：用黑盒探测监控入口页（blackbox_exporter）。
5. **异地通知兜底**：核心告警走两个以上渠道（如 IM + 电话）。

## 指标高基数（Cardinality）问题

```text
症状：Prometheus 内存暴涨、查询变慢、TSDB 写入变慢
```

常见元凶：

- 标签带用户 ID、订单号、请求参数。
- 为每个动态对象建一个指标名（如 `job_<name>_count`）。
- 高基数 Counter 忘记用 `rate` 聚合。

对策：

1. 标签只放**低基数**维度（环境、服务、方法）。
2. 高基数数据用日志/追踪承载。
3. 用 `promtool` / `tsdb analyze` 分析高基数序列。
4. 写入路径加基数限制（3.x 支持 `native_histograms` 与基数保护）。

## 生产监控最佳实践清单

::: tip 监控十诫
1. 监控三层都要有：基础设施、中间件、应用/业务。
2. 接口用 RED（速率/错误/耗时），资源用 USE。
3. 核心指标先压测定基线，再设告警阈值。
4. 告警带 `for`、说明、runbook 链接与责任人。
5. 告警分组 + 抑制，一个根因只发一条。
6. 发布/维护自动静默，防止告警风暴。
7. 日志统一 JSON + traceId，Loki/ELK 集中检索。
8. 监控数据分级保留，冷数据进对象存储。
9. 监控自身高可用、可备份、可自愈。
10. 每周复盘告警噪音，持续收敛到“少而准”。
:::

## 验证方式

1. 用 `promtool check rules` 校验全部告警规则语法。
2. 做一次告警演练：触发、通知、静默、恢复全流程。
3. 检查 TSDB 磁盘增长速率，评估保留期与成本。
4. 用 `tsdb analyze` 找出 Top 高基数指标并整改。

## 参考资料

- Prometheus 排障：https://prometheus.io/docs/prometheus/latest/troubleshooting/
- 告警最佳实践：https://prometheus.io/docs/practices/alerting/
- Prometheus 存储：https://prometheus.io/docs/prometheus/latest/storage/
- Grafana 故障排查：https://grafana.com/docs/grafana/latest/troubleshooting/
- 本专题章节入口：[监控告警目录](../index.md)
