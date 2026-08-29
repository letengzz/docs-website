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
Loki（:3100） ← Promtail 采集容器日志
```

## 环境要求

::: info 当前使用的版本
- Prometheus 3.14.0、Grafana 13.x、Alertmanager 0.33.1、Loki 3.7.6、node_exporter 1.12.1
- Docker + Docker Compose
- 一个可访问 `/actuator/prometheus` 的 Spring Boot 应用（可选）
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
    image: grafana/grafana:13.0.0
    ports: ["3000:3000"]
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin123
    volumes:
      - grafana-data:/var/lib/grafana

  loki:
    image: grafana/loki:3.7.6
    ports: ["3100:3100"]
    command: -config.file=/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail:3.7.6
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

volumes:
  prom-data:
  grafana-data:
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

## 第五步：Promtail 日志采集

```yaml [promtail-config.yml]
server:
  http_listen_port: 9080
clients:
  - url: http://loki:3100/loki/api/v1/push
scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: ["__meta_docker_container_name"]
        target_label: "container"
```

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
2. 接入 [Kubernetes 监控](../../../Ops/Kubernetes/Monitoring/index.md)：用 kube-prometheus-stack 监控集群。
3. 与 [链路追踪](../../../Backend/Microservices/Tracing/index.md) 打通：日志带 traceId 一键跳转。
4. 与 [CI/CD 部署回滚](../../../Tools/CICD/DeployRollback/index.md) 联动：部署后自动健康检查，指标异常自动回滚。

## 参考资料

- Prometheus 下载：https://prometheus.io/download/
- Grafana 仪表盘市场：https://grafana.com/grafana/dashboards/
- kube-prometheus-stack：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack
- 本专题其余章节：回到 [监控告警目录](../index.md)
