# Grafana 可视化

Grafana 是开源的可观测性可视化平台：连接 Prometheus、Loki、MySQL 等数据源，用面板（Panel）和仪表盘（Dashboard）把指标变成可读的图表，并支持数据源告警。截至 2026 年 8 月，最新版本为 **Grafana 13.x**。

## 核心概念

| 概念 | 说明 |
| --- | --- |
| Data Source | 数据源，如 Prometheus、Loki、MySQL |
| Dashboard | 仪表盘，一个页面的面板集合 |
| Panel | 面板，一个可视化单元（时序图、表格、Stat） |
| Row | 仪表盘内的分组行 |
| Variable | 模板变量，如按环境/实例切换 |
| Alert | 基于查询的告警规则 |
| Provisioning | 用配置文件声明式管理数据源与仪表盘 |

## 安装与启动

```shell [docker-compose.yml]
services:
  grafana:
    image: grafana/grafana:13.0.0
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin123
    volumes:
      - grafana-data:/var/lib/grafana
volumes:
  grafana-data:
```

```shell
docker compose up -d
```

访问 http://localhost:3000，用 `admin / admin123` 登录（首次会要求改密码）。

## 添加 Prometheus 数据源

1. **Connections → Data sources → Add data source**。
2. 选择 **Prometheus**。
3. URL 填 `http://prometheus:9090`（容器网络）或 `http://localhost:9090`（本机）。
4. 点击 **Save & test**，出现绿色 “Successfully queried” 即连接成功。

## 创建第一个面板

1. **Dashboards → New dashboard → Add visualization**。
2. 选择 Prometheus 数据源。
3. 查询框输入：

```promql
100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100
```

4. 面板类型选择 **Time series**，标题改为“CPU 使用率”。
5. 保存仪表盘。

## 常用面板类型

| 面板 | 用途 | 适合数据 |
| --- | --- | --- |
| Time series | 时间序列折线/面积图 | CPU、QPS、延迟趋势 |
| Stat | 单个数值 + 状态色 | 当前 CPU、错误数 |
| Gauge | 仪表盘形态 | 磁盘使用率、水位 |
| Bar chart | 柱状图 | 分时段对比 |
| Table | 表格 | 实例列表、Top N |
| Logs | 日志面板 | Loki 日志流 |
| State timeline | 状态时间线 | 服务可用性 |

## 模板变量

变量让一个仪表盘可切换环境/实例：

```text
新建变量 job_name：
类型：Query
查询：label_values(node_cpu_seconds_total, job)
```

面板查询中使用变量：

```promql
100 - avg(rate(node_cpu_seconds_total{job="$job_name", mode="idle"}[5m])) * 100
```

顶部下拉框即可切换 `job`，一个仪表盘覆盖所有服务。

## 仪表盘导入

从 [grafana.com/dashboards](https://grafana.com/grafana/dashboards/) 导入社区仪表盘：

```text
Dashboards → Import → 输入 ID（如 Node Exporter Full：1860）
→ 选择 Prometheus 数据源 → Import
```

::: tip 常用仪表盘 ID
- Node Exporter Full：**1860**
- Spring Boot Statistics：**19004**
- Docker Monitoring：**10619**
- MySQL Overview：**7362**
- Kubernetes：**15757**（kube-prometheus-stack 自带）
:::

## Provisioning：配置即代码

把数据源和仪表盘用文件声明，随仓库管理：

```yaml [provisioning/datasources/prometheus.yml]
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

```yaml [provisioning/dashboards/dashboards.yml]
apiVersion: 1
providers:
  - name: default
    orgId: 1
    folder: "通用"
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

仪表盘 JSON 文件放进挂载目录即可自动加载。

## 数据源告警（Grafana Alerting）

```text
Alerting → Alert rules → New alert rule
查询：A：max(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) /
          node_memory_MemTotal_bytes > 0.9
评估：每 1m，for 5m
通知：联系钉钉/企微/邮件
```

Grafana 告警可直接通知，也可对接 Alertmanager（见 [告警规则与 Alertmanager](../Alerting/index.md)）。

## 权限与多租户

| 能力 | 说明 |
| --- | --- |
| Organization | 组织隔离，每个组织独立数据源与仪表盘 |
| Folder | 文件夹组织仪表盘 |
| Role | Viewer / Editor / Admin 三级权限 |
| Service Account | 服务账号 + Token 供 API/CI 使用 |
| Teams | 团队级权限分配 |

## 易错点与最佳实践

::: danger 常见错误
1. **时间范围不一致**：查询用 `[5m]` 但面板时间范围 1 小时，曲线锯齿严重；保持 `rate` 窗口 ≤ 面板步长。
2. **数据源地址写错**：容器里用 `localhost` 访问不到 Prometheus，要用服务名或宿主机 IP。
3. **面板过载**：一个仪表盘几百个面板，加载缓慢；拆分子仪表盘或按需加载。
4. **默认密码不换**：`admin/admin` 上线不换，被爆破。
5. **所有人都是 Admin**：审计与安全失控；按角色分配权限。
6. **仪表盘没备份**：手工配置丢失无法恢复；用 Provisioning 管起来。
:::

::: tip 最佳实践
1. 仪表盘模板化：变量 + 图例规范，一套模板套所有服务。
2. 颜色/单位规范：CPU/内存用百分比，延迟用毫秒，明确标注单位。
3. 关键面板加阈值线（如磁盘 80% 黄、90% 红）。
4. 用 Provisioning 管理生产数据源与仪表盘，配置进 Git。
5. 定期检查无用的仪表盘与查询，控制资源消耗。
:::

## 验证方式

1. 添加 Prometheus 数据源并 Save & test 成功。
2. 创建 CPU 面板，能看到随时间变化的曲线。
3. 导入 Node Exporter Full 仪表盘，确认图表有数据。
4. 配置一个变量切换 job，切换后图表随之变化。

## 参考资料

- Grafana 文档：https://grafana.com/docs/
- Grafana 仪表盘市场：https://grafana.com/grafana/dashboards/
- Grafana Provisioning：https://grafana.com/docs/grafana/latest/administration/provisioning/
- Grafana Alerting：https://grafana.com/docs/grafana/latest/alerting/
