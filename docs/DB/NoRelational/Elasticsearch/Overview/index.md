# ES 概述与安装

Elasticsearch 是**分布式的搜索与分析引擎**：把数据以 JSON 文档形式存进「索引」，通过倒排索引实现毫秒级全文检索，通过分布式分片实现水平扩展。本页讲清它解决什么问题、与 MySQL/MongoDB 的边界，以及如何在 Windows/Linux/Docker 上完成安装与首次验证。

## 定位：什么场景用 ES

| 场景 | 典型用法 | 为什么不用 MySQL |
| --- | --- | --- |
| 全文搜索 | 商品搜索、站内搜索、内容检索 | `LIKE '%关键词%'` 无法走索引且不支持相关性排序 |
| 日志与可观测性 | ELK / EFK 日志分析、APM | 日志量大、写入吞吐要求高，需要聚合分析 |
| 数据分析 | 订单多维聚合、用户行为分析 | 复杂聚合在 OLTP 库上代价高 |
| 向量检索 | RAG 知识库、语义搜索（kNN） | 关系库无原生向量索引 |

::: tip 一句话理解
MySQL 擅长「按条件精确取数 + 事务」，MongoDB 擅长「灵活文档建模」，**ES 擅长「按相关性搜 + 海量聚合分析」**。ES 不是主数据库：它不支持事务、写入是近实时的，通常作为主库之外的「搜索/分析副本」存在。
:::

## 核心概念速览

| ES 概念 | 类比 MySQL | 说明 |
| --- | --- | --- |
| Index（索引） | Database 中的 Table | 文档的容器，逻辑上的「表」 |
| Document（文档） | Row | JSON 对象，`_id` 唯一标识 |
| Field（字段） | Column | 有类型（keyword/text/number…） |
| Mapping（映射） | Schema | 字段类型与分析器定义 |
| Shard（分片） | 分区 | Lucene 实例，数据水平切分单位 |
| Replica（副本） | 从库 | 主分片的拷贝，容灾 + 分担读压力 |

![ES 集群架构](../assets/es-architecture.svg)

## 安装

### 方式一：Docker（推荐）

```shell
# 单节点开发环境，关闭安全认证简化学习
docker run -d --name es9 \
  -p 9200:9200 \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:9.5.3

# Kibana 可视化（可选，配套 9.5.3）
docker run -d --name kibana9 \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://es9:9200 \
  --link es9 \
  docker.elastic.co/kibana/kibana:9.5.3
```

:::info 内存要求
ES 默认堆内存较大，容器环境建议用 `ES_JAVA_OPTS` 限制在机器内存一半以内（生产上通过 `jvm.options` 配置）。
:::

### 方式二：Linux 压缩包

```shell
cd /opt
curl -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-9.5.3-linux-x86_64.tar.gz
tar -xzf elasticsearch-9.5.3-linux-x86_64.tar.gz
cd elasticsearch-9.5.3

# 单节点配置
echo -e "discovery.type: single-node\nxpack.security.enabled: false" >> config/elasticsearch.yml

# ES 不允许 root 启动，创建专用用户
useradd es
chown -R es:es /opt/elasticsearch-9.5.3
su es -c "./bin/elasticsearch -d"   # -d 后台运行
```

:::danger Linux 常见启动失败
1. **vm.max_map_count 太小**：执行 `sysctl -w vm.max_map_count=262144` 并写入 `/etc/sysctl.conf`；
2. **文件句柄不足**：`/etc/security/limits.conf` 中为 es 用户设置 `nofile 65536`；
3. **内存不足**：`-Xms`/`-Xmx` 各设为可用内存一半，两者必须相等。
:::

## 首次验证

```shell
curl http://localhost:9200
```

预期输出（节选）：

```json
{
  "name" : "es9-node",
  "cluster_name" : "docker-cluster",
  "version" : {
    "number" : "9.5.3",
    "lucene_version" : "10.x"
  },
  "tagline" : "You Know, for Search"
}
```

再做一个完整的「建索引 → 写文档 → 搜」冒烟测试：

```shell
# 1. 创建索引
curl -X PUT http://localhost:9200/products -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "price": { "type": "double" }
    }
  }
}'

# 2. 写入文档
curl -X POST http://localhost:9200/products/_doc -H 'Content-Type: application/json' -d '{
  "title": "无线蓝牙耳机",
  "price": 299.0
}'

# 3. 全文搜索（refresh= true 仅测试用，让文档立即可见）
curl "http://localhost:9200/products/_search?q=耳机&refresh=true"
```

第三步返回的 `hits.total.value` 应为 1，说明链路通了。Kibana 用户访问 http://localhost:5601，在 Dev Tools 中可用同样的请求体交互调试。

## 易错点

:::danger 概念与安装的坑
1. **把 ES 当主库**：ES 无事务、主键冲突靠 `_id` 版本控制兜底——数据源保持在 MySQL 等主库，ES 存「可重放」的副本。
2. **索引名大写**：索引名只能小写（`products`），大写或含空格直接报 `invalid_index_name_exception`。
3. **Windows 下装了带空格的路径**：JVM 启动脚本解析失败——安装路径避免空格与中文。
4. **忘了 `_refresh` 等不到数据**：写入后默认 1 秒才可搜（近实时），测试时可加 `?refresh=true`，生产不要每次请求都刷。
5. **9.x 与 8.x 客户端混用**：8.x 起官方 Java 客户端为 `elasticsearch-java`（ElasticsearchClient），旧的 `RestHighLevelClient` 已在 8.0 移除——新项目直接用新客户端。
:::

## 参考资料

- [Elasticsearch 官方安装文档](https://www.elastic.co/docs/deploy-manage/deploy/self-managed)
- [Elasticsearch 9.x Release Notes](https://www.elastic.co/docs/release-notes/elasticsearch)
- [Docker 镜像页](https://www.docker.elastic.co/)
