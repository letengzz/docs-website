# 实战：监控微服务与容器环境

本实战用 Docker Compose 搭一套完整的监控栈，监控一个 Spring Boot 微服务 + 主机 + 容器：**node_exporter + cAdvisor + Prometheus + Grafana + Alertmanager + Loki**，并打通“指标异常 → 告警通知”的完整闭环。按步骤做完，就得到一套可复用的监控模板。

![Prometheus 架构](../assets/prometheus-arch.svg)

## 架构总览

```text
业务容器（Spring Boot，/actuator/prometheus）
node_exporter（主机指标 :9100）
cAdvisor（容器指标 :8080）
        ↓ Prometheus 抓取（:9090）
Grafana（:3000） ← 查询
Alertmanager（:9093） → 告警通知
Loki（:3100） ← Grafana Alloy 采集容器日志
```

## 环境要求

::: info 当前使用的版本
- Prometheus 3.14.0、Grafana 13.2.1、Alertmanager 0.33.1、Loki 3.7.7、Grafana Alloy 1.19.x、node_exporter 1.12.1
- Docker + Docker Compose
- 一个可访问 `/actuator/prometheus` 的 Spring Boot 应用（可选）
:::

::: warning 采集器已换代
Promtail 已于 2026-03-02 EOL，并自 Loki 3.7.3 起被移除。本实战的日志采集使用官方推荐的 **Grafana Alloy**；存量 Promtail 配置可用 `alloy convert --source-format=promtail` 迁移，详见 [日志体系 · 日志采集与传输](../../LogSystem/Collection/index.md)。
:::

## 第一步：完整 Compose 编排

```yaml [docker-compose.yml]
services:
  node-exporter:
    image: prom/node-exporter:v1.12.1
    pid: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - --path.procfs=/host/proc
      - --path.sysfs=/host/sys
      - --path.rootfs=/rootfs

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro

  prometheus:
    image: prom/prometheus:v3.14.0
    ports: ["9090:9090"]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert-rules.yml:/etc/prometheus/alert-rules.yml
      - prom-data:/prometheus

  alertmanager:
    image: prom/alertmanager:v0.33.1
    ports: ["9093:9093"]
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

  grafana:
    image: grafana/grafana:13.2.1
    ports: ["3000:3000"]
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin123
    volumes:
      - grafana-data:/var/lib/grafana

  loki:
    image: grafana/loki:3.7.7
    ports: ["3100:3100"]
    command: -config.file=/etc/loki/local-config.yaml

  alloy:
    image: grafana/alloy:latest
    command:
      - run
      - /etc/alloy/config.alloy
      - --server.http.listen-addr=0.0.0.0:12345
      - --storage.path=/var/lib/alloy/data
    ports: ["12345:12345"]
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./config.alloy:/etc/alloy/config.alloy:ro
      - alloy-data:/var/lib/alloy/data
    depends_on: [loki]

volumes:
  prom-data:
  grafana-data:
  alloy-data:
```

## 第二步：Prometheus 配置

```yaml [prometheus.yml]
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert-rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: node
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: cadvisor
    static_configs:
      - targets: ["cadvisor:8080"]

  - job_name: order-service
    metrics_path: /actuator/prometheus
    static_configs:
      - targets: ["order-service:8080"]
```

## 第三步：告警规则

```yaml [alert-rules.yml]
groups:
  - name: host-alerts
    rules:
      - alert: HostHighCpu
        expr: 100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100 > 85
        for: 5m
        labels: {severity: warning}
        annotations:
          summary: "主机 CPU 过高"
          description: "{{ $labels.instance }} CPU > 85%"

      - alert: InstanceDown
        expr: up == 0
        for: 2m
        labels: {severity: critical}
        annotations:
          summary: "采集目标离线"
          description: "{{ $labels.job }} / {{ $labels.instance }} 已离线"

      - alert: HighErrorRate
        expr: |
          sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m])) by (job) /
          sum(rate(http_server_requests_seconds_count[5m])) by (job) > 0.05
        for: 5m
        labels: {severity: critical}
```

## 第四步：Alertmanager 通知

```yaml [alertmanager.yml]
route:
  group_by: ["alertname", "instance"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: default
  routes:
    - matchers:
        - severity="critical"
      receiver: critical-webhook

receivers:
  - name: default
    webhook_configs:
      - url: http://host.docker.internal:8088/alert   # 本地 webhook 演示
  - name: critical-webhook
    webhook_configs:
      - url: http://host.docker.internal:8088/alert
```

## 第五步：Grafana Alloy 日志采集

```hcl [config.alloy]
// 发现本节点所有容器（替代已 EOL 的 Promtail）
discovery.docker "containers" {
  host = "unix:///var/run/docker.sock"
}

loki.source.docker "containers" {
  host       = "unix:///var/run/docker.sock"
  targets    = discovery.docker.containers.targets
  forward_to = [loki.process.parse.receiver]
  labels     = { job = "docker" }
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
    values = { trace_id = "" }
  }
}

loki.write "default" {
  endpoint { url = "http://loki:3100/loki/api/v1/push" }
}
```

验证：访问 Alloy 的调试界面 http://localhost:12345，确认 `loki.source.docker.containers` 组件健康、`loki.write.default` 无报错。

## 第六步：启动与验证

```shell
docker compose up -d
docker compose ps    # 全部 Running
```

### 逐项验证

| 检查项 | 地址/命令 | 预期 |
| --- | --- | --- |
| Prometheus | http://localhost:9090/targets | 所有 job 状态 UP |
| PromQL | `up` 查询 | 全部返回 1 |
| Grafana | http://localhost:3000（admin/admin123） | 登录成功 |
| 数据源 | Grafana 添加 Prometheus（`http://prometheus:9090`） | Save & test 成功 |
| 仪表盘 | 导入 1860（Node Exporter Full） | CPU/内存图表有数据 |
| Alertmanager | http://localhost:9093 | UI 可访问 |
| Loki | `curl localhost:3100/ready` | 返回 ready |
| 日志 | Grafana 添加 Loki 数据源，`{container="order-service"}` | 能检索到日志 |

### 告警闭环演练

1. 临时把 CPU 告警阈值改成 1（或停掉一个 Exporter），等待 `for` 时间。
2. 观察 Alertmanager UI 出现告警。
3. 确认 webhook/邮件收到通知。
4. 恢复目标，确认告警恢复并收到恢复通知。

## 进阶收尾

1. 把 Grafana 数据源与仪表盘改成 Provisioning 管理，配置进 Git。
2. 接入 [Kubernetes 监控](../../Kubernetes/Monitoring/index.md)：用 kube-prometheus-stack 监控集群，日志采集用 Alloy 的 DaemonSet 模式。
3. 与 [链路追踪](../../../Backend/Microservices/Tracing/index.md) 打通：日志带 traceId 一键跳转。
4. 与 [CI/CD 部署回滚](../../../Tools/CICD/DeployRollback/index.md) 联动：部署后自动健康检查，指标异常自动回滚。
5. 日志平台本身的生产化（对象存储、Simple Scalable 模式、保留策略、成本优化）见 [日志体系](../../LogSystem/index.md) 专题。

## 参考资料

- Prometheus 下载：https://prometheus.io/download/
- Grafana 仪表盘市场：https://grafana.com/grafana/dashboards/
- kube-prometheus-stack：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack
- Grafana Alloy 文档：https://grafana.com/docs/alloy/latest/
- 指标长期存储落地（建库、降采样、告警链路）：[时序数据库 · 实战](../../../DB/TimeSeries/Practice/index.md)
- 本专题其余章节：回到 [监控告警目录](../index.md)
