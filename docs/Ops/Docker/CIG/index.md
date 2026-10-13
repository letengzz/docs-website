# Docker 监控平台

::: info 版本现状
CIG（cAdvisor + InfluxDB + Grafana）仍是单机容器监控的经典组合；cAdvisor 官方镜像为 `gcr.io/cadvisor/cadvisor`，注意保持更新以修复 CVE。新项目也可选择 Prometheus 体系，参见「容器监控」。
:::

CIG，即 CAdvisor 、 InfluxDB 与 Grafana ，被称为 Docker 监控三剑客。其中 CAdvisor 用于
监控数据的收集， InfluxDB 用于数据存储， Grafana 用于数据展示。

## CAdvisor

cAdvisor是谷歌公司用来分析运行中的 Docker 容器的资源占用以及性能特性的工具
包括对容器的内存、 CPU 、网络、磁盘 IO 等监控，同时提供了 WEB 页面用于展示监控数据。
cAdvisor 使用一个运行中的守护进程 来收集、聚合、处理和导出运行容器相关的信息， 为每
个容器保存 独立的参数、历史资源使用情况和完整的资源使用数据。

默认情况下，CAdvisor 可以针对单个主机存储 2 分钟的监控数据。不过其提供了很多的
数据集成接口用于存储监控数据，支持 InfluxDB Redis Kafka Elasticsearch 等，官方推荐
InfluxDB 。

## InfluxDB

InfluxDB是一个由 InfluxData 用 GO 语言开发的 、 开源 的、高性能的、 时序型数据库，
专注于海量时序数据的高性能读、高性能写、高效存储与实时分析等，无需外部依赖。

## Grafana

Grafana是一款采用 GO 语言编写的、开源的、 数据监控分析可视化平台 ，主要用于大
规模指标数据的可视化展示，是网络架构和应用分析中最流 行的 时序数据展示 工 具，目前已
经支持绝大部分常用的时序数据库。拥有 丰富的插件及模板功能支持图表权限控制和报警。

## 安装

对于CIG 的安装，采用 docker compose 。所以需要先定义 compose.yml 文件，再启动所
有服务容器。

### 创建工作目录

在任意目录下创建任意名称的目录。这里在/root 下创建 cig 目录：

```shell
mkdir cig
```

### 定义componse.yml

在cig 目录中创建 compose.yml ：

```yaml

```

### 启动容器

通过`docker compose up -d` 启动所有容器。

```shell
docker compose up -d
```

## 查看 CIG 各页面

### 查看 cadvisor 页面

由于其完成的是原始数据收集功能，所以该页面在打开时会较慢，有一个收集、展示的
过程。在浏览器输入 docker 宿主机 ip:8080 即可访问。

### 查看 influxdb 页面

在浏览器输入 `http://<Docker 宿主机 IP>:8086` 即可打开 InfluxDB 的 Web 界面（InfluxDB 2.x 的 UI 默认在 8086）。用它确认「cAdvisor 采集到的原始数据到底进没进来」——这一步不能跳过，**后面 Grafana 查不到数据时，先回到这里判断问题在采集端还是在展示端**。

### 查看 grafana 页面

在浏览器输入 `http://<Docker 宿主机 IP>:3000` 打开 Grafana。首次登录账号与密码都是 `admin`，会要求立即修改密码。默认监听 3000 端口。

## 配置 grafana

### 添加数据源

进入 `Connections → Data sources → Add new data source`，选择 **InfluxDB**，然后按容器内可达的地址填写：

| 字段 | 值 | 说明 |
| --- | --- | --- |
| Query Language | InfluxQL / Flux | 与 InfluxDB 版本对应，选错会导致查询语法不匹配 |
| URL | `http://influxdb:8086` | 同编排里用**服务名**，不要写 `localhost` |
| Database | `cadvisor` | 必须与 InfluxDB 里实际写入的库名一致 |
| User / Password | 编排里配置的账号 | 见本页 compose 文件 |

点 `Save & test`，期望出现 `datasource is working` 之类的成功提示。

### 配置 Dashboards

在 `Dashboards → New → Import` 中导入 cAdvisor 的官方看板（社区常用 ID 为 `14282`），导入时选择刚建好的 InfluxDB 数据源即可看到容器维度的 CPU、内存、网络与磁盘曲线。

::: danger 两处最容易卡住的地方
1. **数据源地址写成 `localhost`**。Grafana 自己是容器，`localhost` 指向的是 Grafana 容器，不是 InfluxDB 容器——必须用**服务名**（`influxdb`）或宿主机 IP。
2. **看板导入成功但全是 `No data`**。这时按「InfluxDB 页面 → Grafana 数据源 → 看板变量」的顺序倒查：先确认原始数据在不在，再确认数据源能否连通，最后才怀疑看板本身。
:::

## 相关专题

- [监控告警专题](../../Monitoring/index.md)：Prometheus + Grafana + Alertmanager + Loki 完整监控栈
- [容器监控](../../Docker/Monitor/index.md)：cAdvisor 与 node_exporter 的采集方式
