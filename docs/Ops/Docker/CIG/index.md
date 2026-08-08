# Docker 监控平台

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

### 查看 grafana 页面

## 配置 grafana

### 添加数据源

### 配置 Dashboards