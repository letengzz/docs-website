# 指标采集

Prometheus 自身不产生指标，它靠 **Exporter（导出器）** 把各种系统的指标转成 `/metrics` 文本格式再抓取。本页覆盖主机、容器、数据库、Java 应用等常用采集方式，以及短时任务的 Pushgateway 方案。

## 采集方式总览

| 方式 | 适用 | 代表 |
| --- | --- | --- |
| Exporter（官方/社区） | 系统与中间件 | node_exporter、mysqld_exporter、redis_exporter |
| 客户端库 | 自研应用 | Prometheus Java/Go/Python Client |
| 框架集成 | Web 框架 | Spring Boot Actuator、Prometheus.Net |
| cAdvisor | 容器 | kubelet 内嵌、独立部署 |
| Pushgateway | 短时任务/批处理 | cron 任务、离线作业 |
| 黑盒探测 | 外部可访问性 | blackbox_exporter（HTTP/TCP/ICMP） |

## node_exporter：主机指标

```shell [docker-compose-node.yml]
services:
  node-exporter:
    image: prom/node-exporter:v1.12.1
    container_name: node-exporter
    ports:
      - "9100:9100"
    pid: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - --path.procfs=/host/proc
      - --path.sysfs=/host/sys
      - --path.rootfs=/rootfs
```

访问 http://localhost:9100/metrics 查看指标：

```text
node_cpu_seconds_total{cpu="0",mode="idle"} 12345.6
node_memory_MemTotal_bytes 16777216000
node_filesystem_avail_bytes{mountpoint="/"} 50000000000
node_network_receive_bytes_total{device="eth0"}
```

常用查询：

```promql
# CPU 使用率（排除 idle）
100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100

# 内存使用率
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# 磁盘使用率
(1 - node_filesystem_avail_bytes{mountpoint="/"} /
    node_filesystem_size_bytes{mountpoint="/"}) * 100
```

## cAdvisor：容器指标

```yaml
scrape_configs:
  - job_name: cadvisor
    static_configs:
      - targets: ["cadvisor:8080"]
```

常用指标：

```promql
# 容器 CPU 使用率
rate(container_cpu_usage_seconds_total{container!=""}[5m])

# 容器内存使用
container_memory_usage_bytes{container!=""}
```

::: tip K8s 环境
在 Kubernetes 中，**kubelet 内嵌 cAdvisor**，直接用 `kubernetes_sd_configs` + `/metrics/cadvisor` 采集即可，无需单独部署。
:::

## 中间件 Exporter

| 中间件 | Exporter | 关键指标 |
| --- | --- | --- |
| MySQL | mysqld_exporter | `mysql_global_status_threads_connected`、`mysql_global_status_queries` |
| Redis | redis_exporter | `redis_connected_clients`、`redis_memory_used_bytes` |
| Kafka | kafka_exporter（社区） | `kafka_consumergroup_lag`、`kafka_brokers` |
| RabbitMQ | rabbitmq_exporter | `rabbitmq_queue_messages` |
| Nginx | nginx-prometheus-exporter | `nginx_connections_active` |
| Elasticsearch | elasticsearch_exporter | `es_cluster_health_status` |

```yaml
scrape_configs:
  - job_name: mysql
    static_configs:
      - targets: ["mysqld-exporter:9104"]
  - job_name: redis
    static_configs:
      - targets: ["redis-exporter:9121"]
```

## Java 应用：Prometheus 客户端库

```xml [pom.xml]
<dependency>
    <groupId>io.prometheus</groupId>
    <artifactId>simpleclient_hotspot</artifactId>
    <version>0.16.0</version>
</dependency>
<dependency>
    <groupId>io.prometheus</groupId>
    <artifactId>simpleclient_servlet</artifactId>
    <version>0.16.0</version>
</dependency>
```

```java
DefaultExports.initialize();   // JVM 指标：GC、内存、线程

// 自定义指标
Counter requests = Counter.build()
    .name("http_requests_total")
    .help("Total HTTP requests")
    .labelNames("path")
    .register();
requests.labels("/api/order").inc();
```

暴露 `/metrics` 端点（如用 servlet 或独立 HTTP 服务），Prometheus 即可抓取。

## Spring Boot Actuator

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
```

访问 `http://localhost:8080/actuator/prometheus`，指标包括：

```text
jvm_memory_used_bytes
http_server_requests_seconds_bucket（RED 指标开箱即用）
system_cpu_usage
```

## Pushgateway：短时任务

Prometheus 是 Pull 模型，但 cron 任务跑完就没了，抓不到；让任务把结果**推**给 Pushgateway，Prometheus 再从 Pushgateway 拉取。

```shell
docker run -d -p 9091:9091 prom/pushgateway
```

```shell
# 推送一条指标（job=backup 最后一次成功时间）
echo "backup_last_success_timestamp $(date +%s)" |
  curl --data-binary @- http://localhost:9091/metrics/job/backup
```

::: danger Pushgateway 使用注意
1. **不要**把服务常规指标推给它——推给 Pushgateway 的指标是“最后一次值”，服务挂了还会显示旧值。
2. 只用于批处理、短时任务。
3. 定时清理过期 job 组，避免垃圾指标堆积。
:::

## blackbox_exporter：黑盒探测

从外部探测 HTTP/TCP/ICMP 可达性：

```yaml
scrape_configs:
  - job_name: blackbox
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets: ["https://example.com", "https://api.example.com"]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

```promql
probe_success == 0   # 站点不可达
```

## 易错点与最佳实践

::: danger 常见错误
1. **Exporter 权限过大**：node_exporter 容器用 host pid/rootfs 只读挂载，别给可写权限。
2. **每个实例一个 Exporter 忘了加标签**：不加 `instance`/`job` 标签，聚合查询全乱。
3. **业务指标用 Exporter**：Exporter 只导系统/中间件指标；业务指标用客户端库埋点。
4. **采集频率过高**：1s 抓一次对高基数指标压力很大；默认 15s 足够。
5. **Pushgateway 滥用**：把在线服务指标推给它，服务挂掉监控却“正常”。
6. **忘记安全**：`/metrics` 端口暴露公网会泄露内部信息；用网络策略/认证保护。
:::

::: tip 最佳实践
1. 每类系统一个 job_name，用标签区分环境（`env="prod"`）。
2. 指标命名与单位规范统一，避免混乱。
3. 业务核心指标：QPS、错误率、耗时分布、队列积压、依赖可用性。
4. 对暴露端点的 Exporter 做抓取前验证（`curl /metrics` 确认格式合法）。
5. 新采集项上线后先在测试环境观察 1 周，确认指标稳定再上告警。
:::

## 相关专题

- [SQL 优化](../../../DB/Relational/SQLOptimization/index.md)：mysqld_exporter 慢查询指标的治理入口
- [慢查询定位与分析](../../../DB/Relational/SQLOptimization/SlowQuery/index.md)：慢日志聚合与根因分析

## 验证方式

1. 启动 node_exporter，`curl localhost:9100/metrics` 能看到指标输出。
2. Prometheus 配置 job 后，Targets 页面显示 UP。
3. 用 Pushgateway 推一条测试指标，Prometheus 查询到该指标。
4. 用 blackbox_exporter 探测一个内网地址，`probe_success` 返回 1。

## 参考资料

- Exporter 列表：https://prometheus.io/docs/instrumenting/exporters/
- node_exporter：https://github.com/prometheus/node_exporter
- cAdvisor：https://github.com/google/cadvisor
- blackbox_exporter：https://github.com/prometheus/blackbox_exporter
- Spring Boot Actuator：https://docs.spring.io/spring-boot/reference/actuator/index.html
