# 容器监控

容器监控解决「容器到底在用什么」的问题：CPU、内存、网络、磁盘、事件、日志。本节从零成本的内置命令讲起，再到 Prometheus + cAdvisor + Grafana 的完整方案，并给出选型建议。

::: info 适用版本
本节基于 Docker Engine 29.x。Docker 29.5 起 `docker ps --format` 支持 `.HealthStatus` 占位符，可直接输出健康状态。
:::

## 先看内置命令

### docker stats：实时资源

```shell
docker stats
```

持续输出所有容器的 CPU、内存、网络、磁盘 IO。脚本或排障时用 `--no-stream` 只取一次，并用 `--format` 定制字段：

```shell
docker stats --no-stream \
  --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"
```

`docker stats` 是即时快照，适合人工排障，不适合做历史趋势和告警。

### docker top：容器内进程

```shell
docker top myapp
```

查看容器内实际运行的进程和资源占用，类似于宿主机的 `ps`。

### docker events：事件流

监听容器生命周期事件：

```shell
docker events --filter type=container --filter event=die --since 1h
docker events --filter container=myapp --filter event=oom
```

可以用来做自动告警或联动清理。

### docker logs：日志

```shell
docker logs --tail 200 myapp
docker logs --since 10m --timestamps myapp
docker logs -f myapp
```

日志只采集容器内进程写到 stdout/stderr 的内容，应用必须把日志输出到标准输出，而不是写文件。

## 开启 Docker Engine 自身指标

Docker Engine 内置 Prometheus 格式指标端点，默认关闭。编辑 `/etc/docker/daemon.json`：

```json [daemon.json]
{
  "metrics-addr": "127.0.0.1:9323"
}
```

```shell
sudo systemctl restart docker
curl http://127.0.0.1:9323/metrics | head -20
```

指标包括容器状态、镜像数量、引擎版本等，适合做引擎级监控。建议只绑定 `127.0.0.1`，由采集器抓取。

## 完整方案：Prometheus + cAdvisor + Grafana

经典组合：

| 组件 | 职责 |
| --- | --- |
| cAdvisor | 采集每个容器的资源指标，暴露 `/metrics` |
| node-exporter | 采集宿主机指标 |
| Prometheus | 抓取、存储、查询指标 |
| Grafana | 可视化与告警 |

示例 `compose.yaml`：

```yaml [compose.yaml]
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    privileged: true
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    network_mode: host
    pid: host
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prom-data:/prometheus
    command:
      - --config.file=/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    restart: unless-stopped

volumes:
  prom-data:
  grafana-data:
```

采集配置 `prometheus.yml`：

```yaml [prometheus.yml]
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "cadvisor"
    static_configs:
      - targets: ["cadvisor:8080"]

  - job_name: "node"
    static_configs:
      - targets: ["node-exporter:9100"]
```

启动后：

```shell
docker compose up -d
docker compose ps
```

访问 http://localhost:3000 ，数据源填 `http://prometheus:9090`，导入现成的 cAdvisor 仪表盘（如 14219）即可看到容器资源趋势。

## 告警

Prometheus 的 Alertmanager 负责把告警发到钉钉、邮件、Webhook：

```yaml [alert.yml]
groups:
  - name: container
    rules:
      - alert: ContainerHighCPU
        expr: rate(container_cpu_usage_seconds_total{name!=""}[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "容器 CPU 持续过高"
```

告警规则与阈值要结合业务压测结果设定，避免告警风暴。

## 选型建议

| 需求 | 推荐方案 |
| --- | --- |
| 临时看一眼 | `docker stats` / `docker top` |
| 单机历史趋势 | cAdvisor + Grafana，或现成的 CIG（cAdvisor + InfluxDB + Grafana） |
| 多机、可扩展 | Prometheus + node-exporter + cAdvisor + Alertmanager |
| 完整可观测性 | 引入 Loki（日志）和 Tempo（链路），或直接上托管监控 |
| 容器平台级监控 | 先看现有平台（Portainer、Rancher、K8s）自带能力 |

已有 CIG 部署的读者可以参考本站 [Docker 监控平台（CIG）](../CIG/index.md) 页面，两者的核心差异只是存储后端（InfluxDB 与 Prometheus）。

## 易错点

::: danger 常见错误
1. 用 `docker stats` 当历史监控，进程一重启数据就没了。
2. cAdvisor 不加 `privileged: true` 和宿主机目录挂载，容器只读到空指标。
3. Prometheus 抓取间隔设得太短（如 1s），小规模集群也会产生大量存储压力。
4. 应用日志写文件而不是 stdout，`docker logs` 永远没有内容。
5. 忘记给 Prometheus 数据卷配定期清理，长时间运行磁盘写满。
6. 指标端口（9323、8080、9090）暴露到公网，没有鉴权。
:::

## 验证方式

1. `docker stats --no-stream` 能看到 CPU 和内存数值。
2. `curl http://127.0.0.1:9323/metrics` 返回 Prometheus 格式指标。
3. 监控栈启动后，`curl http://localhost:9090/api/v1/targets` 里 cAdvisor 与 node-exporter 状态为 UP。
4. Grafana 中能看到容器 CPU 使用率随时间变化的曲线。
5. 人为停止一个容器，`docker events --filter event=die` 能实时收到事件。

## 参考资料

- Docker 运行指标：https://docs.docker.com/engine/daemon/prometheus/
- cAdvisor：https://github.com/google/cadvisor
- Prometheus 官方文档：https://prometheus.io/docs/
- Grafana 官方文档：https://grafana.com/docs/
