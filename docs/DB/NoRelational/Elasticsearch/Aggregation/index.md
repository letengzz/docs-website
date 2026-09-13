# 聚合分析（Aggregations）

聚合（Aggregations）是 ES 的分析能力：对检索结果做分组统计、数值计算与嵌套下钻，类似 SQL 的 `GROUP BY` + `SUM/COUNT/AVG`，但可以层层嵌套形成分析树。本页覆盖三类聚合、与 SQL 的对应关系、桶内再查（top_hits）以及性能要点。

## 聚合的三类

| 类别 | 关键字 | 作用 | SQL 类比 |
| --- | --- | --- | --- |
| 桶聚合（Bucket） | `terms` / `range` / `date_histogram` / `filter` | 按条件分桶 | `GROUP BY` |
| 指标聚合（Metric） | `sum` / `avg` / `max` / `min` / `value_count` / `cardinality` | 桶内统计 | `SUM/AVG/COUNT(DISTINCT)` |
| 管道聚合（Pipeline） | `bucket_sort` / `derivative` / `cumulative_sum` | 对聚合结果再计算 | 窗口/二次计算 |

:::info 前置约定
聚合的桶默认取前 10 个；`size` 参数控制桶数量。聚合字段必须是**可聚合类型**（keyword、数值、date），text 字段默认不可聚合。
:::

## terms 桶 + 指标：分组统计

「各品牌商品的均价与数量」：

```json
POST products/_search
{
  "size": 0,
  "aggs": {
    "by_brand": {
      "terms": { "field": "brand", "size": 20 },
      "aggs": {
        "avg_price": { "avg": { "field": "price" } },
        "total": { "value_count": { "field": "brand" } }
      }
    }
  }
}
```

返回节选：

```json
{
  "aggregations": {
    "by_brand": {
      "buckets": [
        { "key": "X", "doc_count": 2, "avg_price": { "value": 249.0 } },
        { "key": "Y", "doc_count": 1, "avg_price": { "value": 99.0 } }
      ]
    }
  }
}
```

`"size": 0` 表示不返回文档命中（hits），只要聚合结果——纯统计查询的标配。

## date_histogram：时间序列

「每天订单量与销售额」（日志/订单分析最高频用法）：

```json
POST orders/_search
{
  "size": 0,
  "query": { "range": { "created": { "gte": "now-7d/d" } } },
  "aggs": {
    "per_day": {
      "date_histogram": {
        "field": "created",
        "calendar_interval": "day",
        "format": "yyyy-MM-dd",
        "min_doc_count": 0
      },
      "aggs": {
        "revenue": { "sum": { "field": "amount" } }
      }
    }
  }
}
```

| 参数 | 说明 |
| --- | --- |
| `calendar_interval` | 日历间隔：`minute/hour/day/week/month/year`（按日历语义补齐空桶） |
| `fixed_interval` | 固定间隔：如 `30s`、`12h`（旧版 `interval` 已废弃） |
| `min_doc_count: 0` | 空桶也返回，时间轴连续 |
| `format` | 返回桶 key 的日期格式 |

## range / filter 桶

```json
"aggs": {
  "price_bands": {
    "range": {
      "field": "price",
      "ranges": [
        { "to": 100 },
        { "from": 100, "to": 300 },
        { "from": 300 }
      ]
    }
  }
}
```

## 嵌套聚合与 top_hits：每组取 Top N

「每个品牌下最便宜的 3 件商品」——桶聚合嵌 `top_hits`：

```json
POST products/_search
{
  "size": 0,
  "aggs": {
    "by_brand": {
      "terms": { "field": "brand" },
      "aggs": {
        "top3_cheap": {
          "top_hits": {
            "size": 3,
            "sort": [{ "price": "asc" }],
            "_source": ["title", "price"]
          }
        }
      }
    }
  }
}
```

配合管道聚合做「只看均值最高的前 5 个品牌」：

```json
"by_brand": {
  "terms": { "field": "brand", "size": 100 },
  "aggs": {
    "avg_price": { "avg": { "field": "price" } },
    "sort_by_price": {
      "bucket_sort": { "sort": [{ "avg_price": { "order": "desc" } }], "size": 5 }
    }
  }
}
```

## 基数去重与百分位

```json
"aggs": {
  "uv":         { "cardinality": { "field": "user_id" } },
  "latency_pct": { "percentiles": { "field": "cost_ms", "percents": [50, 95, 99] } }
}
```

`cardinality` 基于 HyperLogLog++ 是**近似值**（默认误差 5% 以内，`precision_threshold` 可调），不是精确 `COUNT(DISTINCT)`——报表对账场景需注意。

## 与 SQL 对照速查

| 需求 | SQL | ES |
| --- | --- | --- |
| 分组计数 | `GROUP BY brand` | `terms` |
| 平均值 | `AVG(price)` | `avg` |
| 去重计数 | `COUNT(DISTINCT user_id)` | `cardinality`（近似） |
| 时间序列 | `DATE_FORMAT(...)` + `GROUP BY` | `date_histogram` |
| 分组 Top N | 窗口函数 | `terms` + `top_hits` |
| 分组后取前 N 组 | 子查询 + LIMIT | `bucket_sort` |

## 易错点

:::danger 聚合高频坑
1. **text 字段聚合报错**：默认 `fielddata=false`——用 keyword 子字段（`brand.keyword`）。
2. **terms 默认只取 10 桶**：以为只有 10 个分类——显式 `size`，但注意「桶数 × 分片数」的内存与协调节点压力。
3. **cardinality 当精确值用**：对账差几百条——精确去重要么 `collapse`（仅单字段排序去重），要么外部（数据库/Spark）算。
4. **聚合同时返回全部命中文档**：忘了 `"size": 0`，大结果集白白传输。
5. **date_histogram 忘 `min_doc_count: 0`**：没有数据的日子直接消失，图表断线。
6. **深度嵌套聚合失控**：3 层以上嵌套 + 每层大 size，协调节点内存暴涨——下钻逻辑拆成多次查询。
:::

## 验证方式

1. 对 `products` 执行品牌聚合，结果桶数与 `GET products/_count` 的总数一致；
2. 给 `date_histogram` 配 `min_doc_count: 0`，确认空日期桶出现；
3. 用 Kibana Dev Tools 对同一分析写 SQL（Elasticsearch SQL：`POST _sql`）对照结果一致性。

## 参考资料

- [Aggregations 官方文档](https://www.elastic.co/docs/reference/aggregations)
- [Bucket aggregations](https://www.elastic.co/docs/reference/aggregations/bucket-aggregations)
- [Elasticsearch SQL](https://www.elastic.co/docs/explore-analyze/query-filter/languages/sql)
