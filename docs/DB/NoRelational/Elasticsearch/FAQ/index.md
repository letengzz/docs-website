# 常见问题与最佳实践

汇总 ES 落地过程中最高频的问题（选型、数据同步、性能、报错）与上线前自查清单。前序页面：[概述](../Overview/index.md)、[索引与映射](../IndexMapping/index.md)、[查询 DSL](../QueryDSL/index.md)、[聚合](../Aggregation/index.md)、[中文分词](../ChineseAnalyzer/index.md)、[集群](../Cluster/index.md)、[实战](../Practice/index.md)。

## 选型与数据一致性类

### 什么时候不该用 ES？

数据量小（百万行以下）、只做精确条件查询、要求强事务——MySQL 一把梭即可。ES 引入的是「同步链路 + 集群运维」两份新成本，**先有检索痛点再上 ES**。

### MySQL 与 ES 的数据不一致怎么办？

接受**最终一致**：同步链路（Canal / 定时任务）保证秒~分钟级追平；关键业务（如库存）查询永远走主库，ES 只承载「搜索与列表」。出现不一致的兜底是**全量重灌**：按 id 幂等覆盖，随时可重建。

### ES 能当主数据库用吗？

不能作为唯一存储：无事务、近实时（默认 1 秒延迟）、段 merge 的特性都不适合承载交易类数据。定位是**检索/分析引擎**，数据源永远在关系库。

## 报错排查类

### `Result window is too large`

深分页超限（`from + size ≤ 10000`）：临时解法是改索引设置 `max_result_window`，**正确解法是改用 search_after**（见 [查询 DSL](../QueryDSL/index.md)）。

### `FORBIDDEN/cluster block` 写不进去

磁盘水位超 95%，集群进入只读：清理磁盘 → `PUT 索引/_settings` 移除 `index.blocks.read_only_allow_delete: true`。预防：磁盘告警设在 85%（默认 allocate 水位）之前。

### 写入后搜不到

近实时特性：默认 refresh 间隔 1 秒。测试用 `?refresh=true`；等待超过几秒还搜不到则查同步链路水位（`GET 索引/_doc/{id}?realtime=true` 直接读 Translog 验证文档是否已写入）。

### red / yellow 集群

| 状态 | 含义 | 处理 |
| --- | --- | --- |
| yellow | 副本未分配 | 单节点正常；多节点查磁盘水位与节点数 |
| red | 主分片丢失 | `_cluster/allocation/explain` 定位根因；节点误删可用快照恢复 |

### 中文搜索相关性差

按 [中文分词](../ChineseAnalyzer/index.md) 页顺序排查：IK 是否安装 → 索引分析器是否 `ik_max_word` → 是否重建过索引（改映射只对新数据生效）→ 搜索分析器是否配了同义词。

## 性能优化清单

| 维度 | 优化项 |
| --- | --- |
| 写入 | 批量用 `_bulk`（每批 5~15MB）；灌数期副本设 0、调大 refresh_interval |
| 查询 | 过滤条件进 `filter`；`_source` 裁剪；避免 `size` 过大与深分页 |
| 映射 | 精确值用 keyword、金额用 scaled_float；关闭不需要的字段索引（`index: false`） |
| 分片 | 单分片 10~50GB；分片总数 = 节点数 × 1~3 倍，避免海量小分片 |
| JVM | 堆 ≤ 物理内存 50% 且 ≤ 31GB，其余留给操作系统页缓存（Lucene 依赖） |
| 硬件 | SSD 明显优于 HDD；预留 20% 磁盘水位 |

## 上线前自查清单

:::tip 生产检查清单（Code Review / 发布评审可直接用）
1. 索引通过**别名**对外服务，映射变更有重建索引预案；
2. Mapping 显式定义、`dynamic: strict` 或 `false`，金额/日期类型正确；
3. 数据同步有监控（延迟、失败重试、全量重灌脚本）；
4. 搜索接口对用户输入限长、trim，禁用 query_string 拼接；
5. 分页有上限或走 search_after；
6. 慢查询日志已开启并接入告警；
7. 集群健康 + 磁盘水位 + 同步延迟三项监控告警；
8. 快照策略已配置且指向共享/对象存储；
9. 压测报告：目标 QPS 下 P99 延迟达标、无 GC 抖动。
:::

## 学习路线建议

1. **入门**：概述 + 索引映射 + 查询 DSL，跑通「写入 → 搜索 → 聚合」闭环；
2. **进阶**：分词调优 + 相关性排序（`function_score`）、`_reindex` 与别名管理；
3. **生产**：集群规划、快照恢复演练、慢日志与监控；
4. **深水区**：Lucene 段合并机制、BM25 相关性调参、向量检索（kNN）。

## 参考资料

- [Elasticsearch 官方文档](https://www.elastic.co/docs/solutions/search)
- [Elasticsearch: The Definitive Guide（官方教程）](https://www.elastic.co/guide/index.html)
- [Lucene 词汇表](https://www.elastic.co/docs/reference/glossary)
