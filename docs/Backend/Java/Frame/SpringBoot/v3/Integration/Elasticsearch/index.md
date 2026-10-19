# SpringBoot 整合 Elasticsearch

Spring Boot 通过 `spring-boot-starter-data-elasticsearch` 提供 Spring Data Elasticsearch：实体注解映射 + Repository 接口 + ElasticsearchOperations 模板三种用法。本页讲在 Spring Boot 3.x 中接入 ES 的完整步骤；ES 本身的概念（映射、DSL、分词、集群）见 [Elasticsearch 专题](../../../../../../../DB/NoRelational/Elasticsearch/index.md)，本页不重复。

:::info 客户端演进
- Spring Boot 3.x + Spring Data Elasticsearch 5.x 使用新的 **Java API Client**（`co.elastic.clients:elasticsearch-java`）；
- 旧的 `RestHighLevelClient` 已在 ES 8.0 移除，旧版 Spring Boot 2.x 的示例代码不能直接照搬；
- 版本兼容矩阵以 [Spring Data Elasticsearch 官方页面](https://docs.spring.io/spring-data/elasticsearch/reference/) 为准。
:::

## 依赖与配置

```xml [pom.xml 片段]
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-elasticsearch</artifactId>
</dependency>
```

```yaml [application.yml]
spring:
  elasticsearch:
    uris: http://localhost:9200
    connection-timeout: 5s
    socket-timeout: 30s
```

Spring Boot 自动装配 `ElasticsearchOperations`（模板）与 Reactive 变体；如需完整控制客户端：

```java [ElasticsearchConfig.java]
@Configuration
public class ElasticsearchConfig extends ElasticsearchConfiguration {

    @Override
    public ClientConfiguration clientConfiguration() {
        return ClientConfiguration.builder()
                .connectedTo("localhost:9200")
                .withConnectTimeout(Duration.ofSeconds(5))
                .withSocketTimeout(Duration.ofSeconds(30))
                .build();
    }
}
```

## 实体映射

```java [ProductDoc.java]
@Document(indexName = "products", createIndex = false)  // 索引与映射由 DBA/脚本管理
public class ProductDoc {

    @Id
    private String id;

    @Field(type = FieldType.Text, analyzer = "ik_max_word", searchAnalyzer = "ik_smart")
    private String title;

    @Field(type = FieldType.Keyword)
    private String brand;

    @Field(type = FieldType.Double)
    private Double price;

    // getter / setter 省略
}
```

:::tip createIndex = false
实体注解只描述映射的「读侧」。生产索引的 analyzer、分片数等 setting 无法全靠注解表达——统一用脚本建索引（见 [索引与映射](../../../../../../../DB/NoRelational/Elasticsearch/IndexMapping/index.md)），实体 `createIndex = false` 避免启动时自动建出缺配置的索引。
:::

## Repository 方式

```java [ProductRepository.java]
public interface ProductRepository extends ElasticsearchRepository<ProductDoc, String> {

    List<ProductDoc> findByBrandAndPriceLessThanEqual(String brand, Double price);
}
```

方法名即查询（`findBy...` 生成 bool 查询），适合简单场景；复杂查询用模板方式。

## 模板方式（复杂查询）

```java [ProductSearchService.java]
@Service
public class ProductSearchService {

    private final ElasticsearchOperations operations;

    public ProductSearchService(ElasticsearchOperations operations) {
        this.operations = operations;
    }

    public SearchHits<ProductDoc> search(String keyword, String brand, Double maxPrice) {
        Criteria criteria = new Criteria("title").matches(keyword)
                .and("brand").is(brand)
                .and("price").lessThanEqual(maxPrice);

        Query query = new CriteriaQuery(criteria)
                .setPageable(PageRequest.of(0, 10));
        return operations.search(query, ProductDoc.class);
    }
}
```

需要原生 DSL 精细控制（高亮、聚合、function_score）时，直接注入 `ElasticsearchClient`：

```java [用法片段]
public SearchResponse<Map> nativeSearch(String keyword) throws IOException {
    return client.search(s -> s.index("products")
                    .query(q -> q.match(m -> m.field("title").query(keyword)))
                    .highlight(h -> h.fields("title", f -> f.preTags("<em>").postTags("</em>"))),
            Map.class);
}
```

## 易错点

:::danger Spring 整合高频坑
1. **自动建索引缺分析器**：未装 IK 插件时 `analyzer = "ik_max_word"` 会让启动建索引直接失败——先装插件或 `createIndex = false`。
2. **版本不匹配**：Spring Boot 3.1.x 对应 Spring Data ES 5.1.x，跨大版本混用会有序列化兼容问题——按官方矩阵对齐。
3. **Repository 方法生成不了查询**：`findBy` 命名解析失败在启动期报错——字段名与实体保持一致，复杂条件换 Criteria/原生 DSL。
4. **分页属性未透传**：`PageRequest.of(page, size)` 的页码从 0 开始，别按页面习惯从 1 传。
5. **把 Repository 当 ORM 用**：ES 不是主库，只做检索投影——写入仍走 MySQL，通过同步链路进 ES（见 [实战：商品搜索服务](../../../../../../../DB/NoRelational/Elasticsearch/Practice/index.md)）。
:::

## 验证方式

1. 启动应用无报错，`actuator/health` 中 elasticsearch 组件为 UP；
2. 用脚本建好 `products` 索引并同步一条数据，调用 Repository 的 `findByBrand...` 返回结果；
3. 原生 DSL 搜索返回带 `<em>` 高亮片段。

## 与「全文检索与搜索工程」专题的分工（第 167 天补充）

本页讲 **Spring Boot 侧怎么接 ES**：依赖选型、`ElasticsearchClient` 的注入、`RestClient` 与 `spring-data-elasticsearch` 的取舍、`@Document` 映射。搜索本身的工程问题（分析链契约、相关性、索引重建、召回评估）归 [全文检索与搜索工程](/docs/DB/FullTextSearch/index.md)。

接入层最容易背锅的两件事，其实都不在本页：

| 现象 | 真实原因 | 去哪看 |
| --- | --- | --- |
| 「保存成功但立刻搜不到」 | ES 默认 1 秒 refresh，不是写失败 | [索引更新](/docs/DB/FullTextSearch/IndexUpdate/index.md) |
| 「搜出来的顺序很奇怪」 | 字段未设 boost / analyzer 不一致 | [相关性排序](/docs/DB/FullTextSearch/Relevance/index.md) |

::: danger 客户端版本与集群版本不匹配
ES 9 起基于 Lucene 10，**8.x 的客户端不保证与 9.x 集群兼容**（反之亦然）。`spring-data-elasticsearch` 的大版本跟随 Spring Boot 与 ES 客户端的对应关系，升级时三者的版本矩阵要一起查，不能只升一个。

典型症状是「启动正常、简单查询正常，某些 API 返回 400 或字段反序列化失败」——这类问题在集成测试里最容易漏，因为它依赖的是集群真实版本，而不是编译期依赖。
:::

## 参考资料

- [Spring Data Elasticsearch 官方文档](https://docs.spring.io/spring-data/elasticsearch/reference/)
- [Elasticsearch Java API Client](https://www.elastic.co/docs/reference/elasticsearch-clients/java-api-client)
- [Elasticsearch 专题（本站）](../../../../../../../DB/NoRelational/Elasticsearch/index.md)
