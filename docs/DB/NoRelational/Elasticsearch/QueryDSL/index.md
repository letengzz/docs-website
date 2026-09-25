# 查询 DSL（Query DSL）

Query DSL 是 ES 的 JSON 查询语言，分两大体系：**全文查询**（会打分，按相关性排序）与**词项查询**（不打分，精确过滤）。本页覆盖 DSL 结构、match/term 的本质区别、布尔组合、高亮、排序分页与深分页方案。

## DSL 基本结构

```shell
curl -X POST http://localhost:9200/products/_search -H 'Content-Type: application/json' -d '{
  "query": { ... },
  "from": 0, "size": 10,
  "sort": [ ... ],
  "_source": ["title", "price"],
  "highlight": { ... }
}'
```

一次搜索请求的两个阶段（Query Then Fetch）：

![搜索两阶段](../assets/es-search-flow.svg)

## match vs term：最核心的区别

| | `match` | `term` |
| --- | --- | --- |
| 是否分析输入 | 会用字段分析器切词 | 原样作为词条 |
| 适用字段 | `text` | `keyword` / 数值 / 日期 |
| 是否打分 | 是（BM25） | filter 上下文不打分 |
| 典型场景 | 「蓝牙耳机」搜商品名 | `status: "PAID"` 精确过滤 |

```json
// match：输入先分词，各词 OR 匹配，按相关性排序
{ "query": { "match": { "title": "蓝牙耳机" } } }

// match 的 AND 语义（所有词都命中）
{ "query": { "match": { "title": { "query": "蓝牙耳机", "operator": "and" } } } }

// term：keyword 字段精确匹配（不分词）
{ "query": { "term": { "brand": "X" } } }

// terms：命中任一值即可（等价 SQL 的 IN）
{ "query": { "terms": { "brand": ["X", "Y"] } } }

// range：范围过滤（等价 SQL 的 BETWEEN / 比较）
{ "query": { "range": { "price": { "gte": 100, "lt": 300 } } } }
```

:::danger text 字段用 term 查不到数据
`term` 查询不分析输入，而 `text` 字段存储的是**切词后的小写词条**。`{"term": {"title": "蓝牙耳机"}}` 几乎必然匹配不到整串（title 被切成多个单字/词）。text 字段全文搜用 `match`；精确匹配需求请查它的 `title.keyword` 子字段。
:::

## bool：组合查询

```json
{
  "query": {
    "bool": {
      "must":     [ { "match": { "title": "耳机" } } ],          // AND，参与打分
      "filter":   [ { "term": { "brand": "X" } },
                    { "range": { "price": { "lte": 500 } } } ],   // AND，不打分、可缓存
      "should":   [ { "term": { "tags": "wireless" } } ],         // OR，提升相关性分
      "must_not": [ { "term": { "tags": "refurbished" } } ]       // NOT
    }
  }
}
```

:::tip filter 优先
只做「过滤」不关心排序贡献的条件放进 `filter`：跳过打分计算，且结果可被查询缓存复用，性能显著优于 `must`。搜索类查询的惯用结构是「`must` 放全文关键词 + `filter` 放状态/分类/价格」。
:::

## 全文查询进阶

```json
// match_phrase：短语匹配，保证词序相邻
{ "query": { "match_phrase": { "title": "无线蓝牙" } } }

// multi_match：多字段搜索，title 权重 ×3
{
  "query": {
    "multi_match": {
      "query": "蓝牙耳机",
      "fields": ["title^3", "description", "brand"]
    }
  }
}

// query_string：简单语法组合（输入可信时使用）
{ "query": { "query_string": { "default_field": "title", "query": "蓝牙 AND 耳机" } } }
```

## 分页与深分页

| 方式 | 语法 | 适用 |
| --- | --- | --- |
| from + size | `"from": 100, "size": 10` | 常规分页，`from + size ≤ 10000`（默认上限） |
| search_after | 排序值游标 `"search_after": [171234, "id"]` | 深分页 / 无限滚动（推荐） |
| scroll | `?scroll=1m` + `_scroll_id` | 全量导出（新代码推荐用 `search_after` + PIT） |

深分页的本质代价：每个分片都要返回 `from + size` 条候选，协调节点汇总 `(from + size) × 分片数` 条再截取。`search_after` 用上一页末尾的排序值作游标，各分片只取 size 条，代价恒定：

```json
{
  "size": 10,
  "sort": [{ "price": "asc" }, { "_id": "asc" }],
  "search_after": [199, "3"]
}
```

排序值必须全局唯一可比较——最后追加 `_id` 作为 tiebreaker，避免同价商品翻页丢失。

## 高亮与结果控制

```json
{
  "query": { "match": { "title": "耳机" } },
  "_source": ["title", "price"],                       // 只返回需要的字段
  "highlight": {
    "fields": { "title": {} },
    "pre_tags": ["<em>"], "post_tags": ["</em>"]
  },
  "track_total_hits": true                              // 精确统计总数（默认 10000 内）
}
```

## 向量检索与 ES 的衔接

前面所有查询都建立在同一个前提上：**查询词必须和文档里的词对得上**。BM25 再好也解决不了「查询『跨库一致性』却检索不到写『分布式事务』的文档」——因为两者没有共同词项。语义检索靠的是**向量近邻**：把文本编码成一个高维向量，语义相近的文本在向量空间里距离更近。

ES 从 7.x 起内置 `dense_vector` 类型，8.x 起提供原生 `knn` 查询，8.8+ 支持 RRF 混合检索；到 9.x 这套能力已经可以直接用于生产。**它最大的价值不是「替代专用向量库」，而是「让关键词检索与语义检索在同一个引擎、同一份数据上完成」**。

### 第一步：声明向量字段

```json
PUT docs-vec
{
  "mappings": {
    "properties": {
      "title":     { "type": "text" },
      "title_vec": {
        "type": "dense_vector",
        "dims": 1024,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}
```

四个参数各自的含义与易错点：

| 参数 | 说明 |
| --- | --- |
| `dims` | 必须与嵌入模型输出维度**完全一致**，写错直接报错；换模型就要重建索引 |
| `similarity` | `cosine` 最常用（文本向量通常已归一化）；已归一化的向量用 `dot_product` 更快 |
| `index` | 为 `true` 才会建立近似近邻索引（HNSW），否则只能做精确但很慢的暴力检索 |
| `element_type` | 默认 `float`；`byte` / `bit` 可大幅省内存，但需模型侧配合量化 |

### 第二步：kNN 查询

```json
POST docs-vec/_search
{
  "knn": {
    "field": "title_vec",
    "query_vector": [0.0123, -0.0456, 0.0789],
    "k": 10,
    "num_candidates": 100
  },
  "_source": ["title"]
}
```

::: warning `num_candidates` 是最该调的参数
kNN 是**近似**检索：ES 先对每个分片随机取 `num_candidates` 个候选，再在其中挑真正的 top-k。所以 `num_candidates` 越小越快、召回越低。起步经验是 **`num_candidates ≈ 10 × k`**，之后用一组带标准答案的查询做召回率评测再调——只看「查询变快了」而没有召回数据，等于在用准确率换速度。
:::

kNN 还可以和过滤条件组合，此时**过滤先执行、只在命中的文档里做向量检索**（`filter` 与 `knn` 同级）：

```json
POST docs-vec/_search
{
  "knn": {
    "field": "title_vec",
    "query_vector": [0.0123, -0.0456, 0.0789],
    "k": 10,
    "num_candidates": 100,
    "filter": { "term": { "status": "published" } }
  }
}
```

### 第三步：混合检索（RRF 融合）

只靠向量会丢掉**精确词匹配**的能力（比如型号 `AX-2000` 这种向量模型没见过几次的 token），只靠 BM25 又缺语义泛化。ES 8.8+ 提供了 **RRF（Reciprocal Rank Fusion，倒数排名融合）**：不做分数归一化，只看两路结果里的**排名**，因此不需要为「BM25 分数与余弦相似度量纲不同」调权重。

```json
POST docs-vec/_search
{
  "retriever": {
    "rrf": {
      "retrievers": [
        { "standard": { "query": { "match": { "title": "分布式事务" } } } },
        { "knn": {
            "field": "title_vec",
            "query_vector": [0.0123, -0.0456, 0.0789],
            "k": 50, "num_candidates": 200
        } }
      ],
      "rank_window_size": 50,
      "rank_constant": 60
    }
  }
}
```

`rank_constant` 越大，排名靠后的文档被「拉平」得越明显（默认 60 是论文推荐值）；`rank_window_size` 决定每路取多少条参与融合。**RRF 的另一个好处是免调参**——上线时不必先跑一轮离线评测确定两路权重，先用等权融合上线，再按评测结果决定要不要换成加权方案。

### ES 做向量库，什么时候合适

| 判断维度 | 适合用 ES | 更适合专用向量库（Milvus / Qdrant 等） |
| --- | --- | --- |
| 检索形态 | 关键词 + 语义**混合**，需要过滤、聚合、高亮 | 纯语义检索，不需要聚合与排序字段 |
| 已有资产 | 业务数据本来就在 ES 里，不必同步一份到新系统 | 只做向量，没有其他检索需求 |
| 数据规模 | 千万级向量以内，维度 ≤ 1024 | 上亿向量、超大规模或超高低维张力场景 |
| 更新频率 | 增量写入为主 | 需要频繁全量重建、多路向量索引实验 |
| 运维成本 | 复用现有 ES 集群与监控 | 接受引入并维护一个新组件 |

**一句话判据**：如果「语义检索」只是你现有搜索能力的一个补充维度，用 ES 最省事；如果向量检索是产品的全部（比如以图搜图、推荐召回），再考虑专用向量库。选型的完整对比见 [AI · RAG · 向量库与索引](../../../../AI/RAG/VectorStore/index.md)。

## 易错点

:::danger 查询 DSL 高频坑
1. **text 用 term 查**：见上文，全文搜用 match，精确搜用 keyword 子字段。
2. **from + size 翻到几千页**：报 `Result window is too large` 或性能崩塌——改 `search_after`。
3. **`must` 里塞大量过滤条件**：白白做 BM25 打分——过滤条件进 `filter`。
4. **排序时字段是 text**：text 不能排序/聚合（除非 fielddata）——用 keyword 子字段。
5. **should 不生效**：bool 中存在 `must`/`filter` 时，`should` 默认只是「加分项」；需要「至少满足 N 个」时设 `"minimum_should_match": 1`。
6. **忘记 `_source` 过滤**：大文档全字段返回，带宽浪费——返回列裁剪。
:::

## 验证方式

1. 分别执行 `match` 与 `term` 查询同一中文关键词，观察返回差异，验证分词行为；
2. 把 `from` 设为 10000 制造深分页报错，再改用 `search_after` 复现同样的「第 10001 条」；
3. 用 `profile: true` 查看查询在各分片上的执行细节。

## 参考资料

- [Query DSL 官方文档](https://www.elastic.co/docs/reference/query-languages/query-dsl)
- [search_after / PIT](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/paginate-search-results)
- [相关性打分（BM25）](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/sort-search-results)
