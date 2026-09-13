# 实战：商品搜索服务

把前面所学串成一个可落地的工程：以「商品搜索」为例，实现 **MySQL → ES 数据同步 → 搜索接口 → 结果高亮 → 聚合筛选**的完整链路。技术栈为 Spring Boot + Java API Client，数据库同步采用双写之外的稳妥方案——基于 binlog 的 Canal 或直接定时任务，本页给出代码可跑的两条路径。

## 架构

```text
┌────────┐  binlog   ┌────────┐   bulk    ┌──────────────┐
│ MySQL  │ ────────> │ Canal  │ ────────> │ Elasticsearch │
│ 主库   │  或定时任务 │ 同步器  │  _bulk    │ products 索引  │
└────────┘           └────────┘           └──────┬───────┘
                                                 │ search
                                          ┌──────┴───────┐
                                          │  搜索服务 API  │
                                          └──────────────┘
```

:::tip 为什么不双写
业务代码同时写 MySQL 和 ES 会遇到「一边成功一边失败」的一致性黑洞，且耦合严重。**MySQL 是唯一事实源（Single Source of Truth），ES 是可重放的投影**：同步失败可以从 binlog 或全量任务重新灌入。
:::

## 索引设计

```json
PUT products_v1
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "ik_smart_syn": {
          "tokenizer": "ik_smart",
          "filter": ["synonym_filter"]
        }
      },
      "filter": {
        "synonym_filter": {
          "type": "synonym_graph",
          "synonyms": ["手机,移动电话", "电脑,计算机"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title":   { "type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart_syn", "fields": { "keyword": { "type": "keyword" } } },
      "brand":   { "type": "keyword" },
      "price":   { "type": "scaled_float", "scaling_factor": 100 },
      "sales":   { "type": "integer" },
      "status":  { "type": "keyword" },
      "tags":    { "type": "keyword" },
      "updated": { "type": "date" }
    }
  },
  "aliases": { "products": {} }
}
```

设计要点：价格用 `scaled_float` 存分；标题挂同义词搜索分析器；对外服务永远走别名 `products`，重建索引用 `products_v2` 无缝切换。

## Spring Boot 集成

```xml [pom.xml 片段]
<dependency>
    <groupId>co.elastic.clients</groupId>
    <artifactId>elasticsearch-java</artifactId>
    <version>9.5.3</version>
</dependency>
```

```java [SearchService.java]
@Service
public class SearchService {

    private final ElasticsearchClient client;

    public SearchService(ElasticsearchClient client) {
        this.client = client;
    }

    /** 核心搜索：关键词 + 品牌 + 价格区间 + 排序 + 分页 */
    public Map<String, Object> search(String keyword, String brand,
                                      Double minPrice, Double maxPrice,
                                      int page, int size) throws IOException {
        int from = (page - 1) * size;

        SearchResponse<Map> resp = client.search(s -> s
                .index("products")
                .from(from).size(size)
                .query(q -> q.bool(b -> {
                    if (keyword != null && !keyword.isBlank()) {
                        b.must(m -> m.match(mm -> mm.field("title").query(keyword)));
                    }
                    if (brand != null) {
                        b.filter(f -> f.term(t -> t.field("brand").value(brand)));
                    }
                    if (minPrice != null || maxPrice != null) {
                        b.filter(f -> f.range(r -> r.number(n -> {
                            n.field("price");
                            if (minPrice != null) n.gte(minPrice);
                            if (maxPrice != null) n.lte(maxPrice);
                            return n;
                        })));
                    }
                    return b;
                }))
                .aggregation("brands", a -> a.terms(t -> t.field("brand").size(20)))
                .highlight(h -> h.fields("title", f -> f.preTags("<em>").postTags("</em>"))),
                Map.class);

        long total = resp.hits().total() == null ? 0 : resp.hits().total().value();
        List<Map<String, Object>> items = resp.hits().hits().stream()
                .map(h -> {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> src = h.source();
                    if (h.highlight().get("title") != null) {
                        src.put("highlightTitle", String.join("", h.highlight().get("title")));
                    }
                    return src;
                }).toList();
        List<String> brandFacets = resp.aggregations().get("brands").lterms()
                .buckets().array().stream().map(b -> b.key()).toList();

        return Map.of("total", total, "items", items, "brandFacets", brandFacets);
    }
}
```

## 数据同步：定时增量方案

小数据量/分钟级延迟可接受时，最简单的同步器（Canal / Flink CDC 方案见扩展阅读）：

```java [ProductSyncJob.java]
@Scheduled(fixedDelay = 60_000)   // 每分钟增量一次
public void sync() {
    LocalDateTime cursor = lastSyncTime;          // 上次同步水位（存 DB 或 Redis）
    List<Product> changed = productMapper.selectByUpdatedAfter(cursor);
    if (changed.isEmpty()) return;

    BulkRequest.Builder br = new BulkRequest.Builder();
    for (Product p : changed) {
        Map<String, Object> doc = Map.of(
                "title", p.getTitle(), "brand", p.getBrand(),
                "price", p.getPrice(), "sales", p.getSales(),
                "status", p.getStatus(), "updated", p.getUpdated().toString());
        br.operations(op -> op.index(idx -> idx
                .index("products")
                .id(String.valueOf(p.getId()))
                .document(doc)));
    }
    BulkResponse resp = client.bulk(br.build());
    if (resp.errors()) throw new IllegalStateException("bulk 同步存在失败项，需重放");
    lastSyncTime = changed.get(changed.size() - 1).getUpdated();
}
```

:::danger 增量同步的可靠性要点
1. **水位用 `updated` 字段**：商品表必须带 `ON UPDATE CURRENT_TIMESTAMP` 的更新时间列；
2. **同一毫秒多条变更会漏**：水位取「本批最大值减 1 秒」做重叠窗口，靠 `_id` 幂等覆盖；
3. **失败重放**：bulk 返回 errors 时记录失败 id 清单重试——ES 写入是幂等的（同 `_id` 覆盖）。
:::

## 搜索结果页效果

调用 `search("蓝牙耳机", null, 100.0, 500.0, 1, 10)` 的返回：

```json
{
  "total": 128,
  "items": [
    { "title": "无线<em>蓝牙</em><em>耳机</em> Pro", "brand": "X", "price": 299, "highlightTitle": "无线<em>蓝牙</em><em>耳机</em> Pro" }
  ],
  "brandFacets": ["X", "Y", "Z"]
}
```

前端用 `brandFacets` 渲染「品牌筛选面板」，点击后把 `brand` 作为 `filter` 条件回传——这就是电商搜索页的「搜索结果 + 左侧 facet 联动」。

## 上线检查清单

1. **压测**：`wrk`/`JMeter` 打搜索接口，P99 < 200ms（单次 `size ≤ 20`）；
2. **慢查询**：开启慢日志 `index.search.slowlog.threshold.query.warn: 1s` 巡检；
3. **别名切换演练**：`products_v1 → products_v2` 重建一次全流程（映射改动只能走这条路）；
4. **监控**：集群 `yellow/red`、磁盘水位、同步延迟（`updated` 与当前时间差）三项告警。

## 易错点

:::danger 工程落地高频坑
1. **搜索接口把用户输入直接拼 query_string**：注入 `AND`/`*` 等语法——用 `match` 并对输入 trim、限长。
2. **分页直接用 from+size 无上限**：恶意翻页打爆集群——接口层限制 `page × size ≤ 1000`，更深走 `search_after`。
3. **同步全量重灌没关副本**：灌数期间副本重建拖慢 3~5 倍——重灌前 `number_of_replicas: 0`，完成恢复。
4. **索引重建忘了切别名**：`products_v2` 建好但服务还在查 `products_v1`——切换与验证写进同一脚本。
:::

## 验证方式

1. `docker compose` 起 MySQL + ES，执行建索引 SQL 与 PUT mapping；
2. 跑一次全量同步，`GET products/_count` 与 MySQL 商品总数一致；
3. 修改一条商品价格，1 分钟内搜索结果同步变化；
4. 带品牌与价格区间搜索，`brandFacets` 与高亮 `<em>` 正常返回。

## 参考资料

- [elasticsearch-java 客户端](https://www.elastic.co/docs/reference/elasticsearch-clients/java-api-client)
- [Canal（Alibaba）](https://github.com/alibaba/canal)
- [Flink CDC](https://nightlies.apache.org/flink/flink-cdc-docs-stable/)
