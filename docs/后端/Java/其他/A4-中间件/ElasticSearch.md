## 7.8.0
版本：7.8.0
### 基础知识


### 操作
#### JavaAPI-POM
```xml
<dependency>
    <groupId>org.elasticsearch</groupId>
    <artifactId>elasticsearch</artifactId>
    <version>7.8.0</version>
</dependency>
<!-- elasticsearch 的客户端 -->
<dependency>
    <groupId>org.elasticsearch.client</groupId>
    <artifactId>elasticsearch-rest-high-level-client</artifactId>
    <version>7.8.0</version>
</dependency>
<!-- elasticsearch 依赖 2.x 的 log4j -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.8.2</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.8.2</version>
</dependency>
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.9.9</version>
</dependency>
```
#### JavaAPI-获取客户端
```java
public class EsUtils {

    public static RestHighLevelClient getClient(){
        return new RestHighLevelClient(RestClient.builder(new HttpHost("localhost", 9200, "http")));
    }

    public static void closeClient(RestHighLevelClient client){
        try{
            client.close();
        }catch (Exception ex){
            System.out.println(ex.getMessage());
        }
    }
}

```
#### 索引
##### RESTAPI
```xml
添加索引
PUT http://localhost:9200/student

查看所有索引
GET http://localhost:9200/_cat/indices

查看单个索引
GET http://localhost:9200/student

删除索引
DELETE http://localhost:9200/student
```
##### JavaAPI
```java
//添加索引
CreateIndexRequest req = new CreateIndexRequest(index);
CreateIndexResponse res = client.indices().create(req, RequestOptions.DEFAULT);
//查看索引
GetIndexRequest req = new GetIndexRequest(index);
GetIndexResponse res = client.indices().get(req, RequestOptions.DEFAULT);
//删除索引
DeleteIndexRequest req = new DeleteIndexRequest(index);
AcknowledgedResponse res = client.indices().delete(req, RequestOptions.DEFAULT);
```
#### 文档
##### RESTAPI
```http
# 创建文档
POST http://localhost:9200/shopping/_doc
{
    "title": "小米手机",
    "category": "小米",
    "images": "http://www.gulixueyuan.com/xm.jpg",
    "price": 3999.00
}

# 创建或整体修改（指定_id）
POST http://localhost:9200/shopping/_doc/1001
{
    "title": "小米手机",
    "category": "小米",
    "images": "http://www.gulixueyuan.com/xm.jpg",
    "price": 3999.00
}

# 查看文档
GET http://localhost:9200/shopping/_doc/1001

# 修改字段
POST http://localhost:9200/shopping/_update/1001
{
  "doc":{
    "price":2000
  }
}

# 删除文档
DELETE http://localhost:9200/shopping/_doc/1001

# 删除多条文档
POST http://localhost:9200/shopping/_delete_by_query
{
  "query": {
    "match": {
        "price": 4000.00
    }
  }
}

# 创建映射
PUT http://localhost:9200/student/_mapping
{
    "properties": {
        "name": {
            "type": "text",
            "index": true
        },
        "gender": {
            "type": "keyword",
            "index": true
        },
        "age": {
            "type": "long",
            "index": false
        }
    }
}

# 查看映射
GET http://localhost:9200/student/_mapping

# 索引关联映射
PUT http://localhost:9200/student1
# 会创建索引
{
  "settings": {},
  "mappings": {
  "properties": {
      "name": {
          "type": "text",
          "index": true
      },
      "sex": {
          "type": "keyword",
          "index": true
      },
      "age": {
          "type": "long",
          "index": false
      }
    }
  }
}

```
##### JavaAPI
```java
//添加
IndexRequest req = new IndexRequest();
req.index(index).id("1003");
User user = new User("zhangsan","男",40);
String userJson = new ObjectMapper().writeValueAsString(user);
req.source(userJson,XContentType.JSON);
IndexResponse res = client.index(req, RequestOptions.DEFAULT);
System.out.println("id ==》 " + res.getId());
System.out.println("result ==》 " + res.getResult());

//删除
DeleteRequest req = new DeleteRequest();
req.index(index).id("1001");
DeleteResponse res = client.delete(req, RequestOptions.DEFAULT);
System.out.println(res.status());

//更新
UpdateRequest update = new UpdateRequest();
update.index(index).id("1002");
HashMap<String, Object> map = new HashMap<>();
map.put("name", "zhangsan");
update.doc(new ObjectMapper().writeValueAsString(map), XContentType.JSON);
UpdateResponse updateRes = client.update(update, RequestOptions.DEFAULT);
System.out.println(updateRes.status());

//批量操作  增删改
BulkRequest req = new BulkRequest();
ObjectMapper objectMapper = new ObjectMapper();
req.add(new IndexRequest().index(index).source(objectMapper.writeValueAsString(new User("zhangsan","女",20)), XContentType.JSON));
req.add(new IndexRequest().index(index).source(objectMapper.writeValueAsString(new User("zhangsan2","男",30)), XContentType.JSON));
req.add(new IndexRequest().index(index).source(objectMapper.writeValueAsString(new User("zhangsan3","女",40)), XContentType.JSON));
BulkResponse res = client.bulk(req, RequestOptions.DEFAULT);
System.out.println(res.status());

//查询
GetRequest req = new GetRequest();
req.index(index).id("1001");
GetResponse res = client.get(req, RequestOptions.DEFAULT);
System.out.println(res.getSourceAsString());
```
#### 高级查询
##### RESTAPI
```java
# 所有高级查询的请求接口都一样
GET http://localhost:9200/student/_search
# 查询匹配
{
    "query": {
        "match": {
            "name": "张"
        }
    }
}

# 查看所有文档
{
    "query": {
        "match_all": {}
    }
}
//# "query"：这里的 query 代表一个查询对象，里面可以有不同的查询属性
//# "match_all"：查询类型，例如：match_all(代表查询所有)， match，term ， range 等等
//# {查询条件}：查询条件会根据类型的不同，写法也有差异

# 字段匹配查询
{
    "query": {
        "multi_match": {
            "query": "lisi",
            "fields": [
                "nickname"
            ]
        }
    }
}

# 关键字精确查询
{
    "query": {
        "term": {
            "name": {
                "value": "zhangsan"
            }
        }
    }
}

# 多关键字查询
{
    "query": {
        "terms": {
            "name": [
                "zhangsan",
                "lisi"
            ]
        }
    }
}


# 指定查询字段
{
    "_source": [
        "name",
        "nickname"
    ],
    "query": {
        "match_all": {}
    }
}


# 过滤查询字段
{
    //includes：来指定想要显示的字段
    //excludes：来指定不想要显示的字段
    "_source": {
        "includes": [
            "name",
            "nickname"
        ]
    },
    "query": {
        "match_all": {}
    }
}

# 组合查询
//`bool`把各种其它查询通过`must`（必须 ）、`must_not`（必须不）、`should`（应该）的方式进行组合
//与must等同级还有filter过滤作为条件
{
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "name": "lisi"
                    }
                }
            ],
            "must_not": [
                {
                    "match": {
                        "nickname": "zhangsan"
                    }
                }
            ],
            "should": [
                {
                    "match": {
                        "gender": "男"
                    }
                }
            ]
        }
    }
}

# 范围查询
{
    "query": {
        "range": {
            "age": {
                "gte": 20,
                "lte": 99
            }
        }
    }
}
//gt大于 gte大于等于  lt小于 lte小于等于

# 模糊查询
{
    "query": {
        "fuzzy": {
            "name": {
                "value": "zhangsan",
                "fuzziness":2
            }
        }
    }
}

# 单字段排序
{
    "query": {
        "match_all":{}
    },
    "sort": [
        {
            "age": {
                "order": "desc"
                //asc desc
            }
        }
    ]
}

# 多字段排序
{
    "query": {
        "match_all":{}
    },
    "sort": [
        {
            "age": {
                "order": "desc"
                //asc desc
            }
        },
        {
            "_score": {
                "order": "desc"
            }
        }
    ]
}

# 高亮查询  
// 想要显示高亮，查询条件里面需要有高亮显示的字段
{
    "query": {
        "match": {
            "name": "zhangsan"
        }
    },
    "highlight": {
        "pre_tags": "<font color='red'>",
        "post_tags": "</font>",
        "fields": {
            "name": {}
        }
    }
}

# 分页查询
{
    "query": {
        "match_all": {}
    },
    "sort": [
        {
            "age": {
                "order": "desc"
            }
        }
    ],
    "from": 0,  //from= （pageNum - 1）* size
    "size": 2
}

# 聚合查询
{
    "aggs": {
        "max_age": { //自定义名称   
            "stats": {  //最大max | 最小min | 总和sum | 平均值avg  
                // 对某个字段的值进行去重之后再取总数cardinality | stats 聚合，对某个字段一次性返回 count，max，min，avg 和 sum 五个指标
                "field": "age"
            }
        }
    },
    "size": 0
}
//聚合允许使用者对 es 文档进行统计分析，类似与关系型数据库中的 group by，当然还有很多其他的聚合，例如取最大值、平均值等等。

# 桶聚合查询
{
    "aggs": {
        "age_groupby": { //自定义名称
            "terms": {  //分组
                "field": "age"  //分组字段
            },
            "aggs": {  //子聚合
                "sum_age": { //子聚合名称
                    "sum": {
                        "field": "age"
                    }
                }
            }
        }
    },
    "size": 0 //不需要原始数据
}
// 桶聚和相当于 sql 中的 group by 语句
// terms 聚合，分组统计
// 在terms分组下可以继续进行聚合
```
##### JavaAPI
```java
SearchRequest req = new SearchRequest();
req.indices("user");  //指定索引
SearchSourceBuilder builder = new SearchSourceBuilder();
//查询全部
builder.query(QueryBuilders.matchAllQuery());

//匹配查询
builder.query(QueryBuilders.matchQuery("name","zhangsan"));

//字段匹配查询
builder.query(QueryBuilders.multiMatchQuery("zhangsan","name","gender"));

//关键字精确查询
//多关键字精确查询
builder.query(QueryBuilders.termsQuery("name","zhangsan","zhangsan2"));

//指定查询字段
//过滤字段
builder.fetchSource(new String[]{"name","gender"},null);
builder.query(QueryBuilders.matchAllQuery());

//组合查询
BoolQueryBuilder boolQuery = QueryBuilders.boolQuery();
boolQuery.must(QueryBuilders.matchQuery("name","zhangsan"));
boolQuery.should(QueryBuilders.matchQuery("gender","男"));
builder.query(boolQuery);

//范围查询
builder.query(QueryBuilders.rangeQuery("age").gte(30).lte(90));

//模糊查询
builder.query(QueryBuilders.fuzzyQuery("name","zhangsan").fuzziness(Fuzziness.ONE));

//单字段排序
builder.query(QueryBuilders.matchAllQuery());
builder.sort("age",SortOrder.DESC);
// or
builder.sort(SortBuilders.fieldSort("age").order(SortOrder.ASC));

//多字段排序
builder.query(QueryBuilders.matchAllQuery());
builder.sort("age",SortOrder.ASC).sort("_score",SortOrder.ASC);
builder.sort("age",SortOrder.DESC);
builder.sorts().add(SortBuilders.fieldSort("age").order(SortOrder.ASC));
builder.sorts().add(SortBuilders.fieldSort("_score").order(SortOrder.ASC));

//高亮查询
builder.query(QueryBuilders.fuzzyQuery("name","zhangsan").fuzziness(Fuzziness.TWO));
HighlightBuilder highlightBuilder = new HighlightBuilder();
highlightBuilder.preTags("<font color='red'>");
highlightBuilder.postTags("</font>");
highlightBuilder.field("name");
builder.highlighter(highlightBuilder);

//分页查询
builder.query(QueryBuilders.matchAllQuery());
builder.from(0);
builder.size(3);

//聚合查询
builder.aggregation(AggregationBuilders.stats("age_stats").field("age"));

//桶聚合查询
builder.aggregation(AggregationBuilders.terms("age_groupby").field("age")
        .subAggregation(AggregationBuilders.sum("age_sum_group").field("age")));

req.source(builder);
SearchResponse res = client.search(req, RequestOptions.DEFAULT);
SearchHits hits = res.getHits();
Iterator<SearchHit> iterator = hits.iterator();
while(iterator.hasNext()){
    SearchHit next = iterator.next();
    System.out.println(next.getIndex());
    System.out.println(next.getId());
    System.out.println(next.getSourceAsString());
    System.out.println(next.getScore());
    System.out.println("===================");

    // 高亮输出
System.out.println(next.getHighlightFields().get("name"));
System.out.println("===================");
}
System.out.println("==========聚合输出==============");
System.out.println(res);
System.out.println("===================");
```
## 8.10.2
版本：8.10.2
### 基础知识

### 操作
#### JavaAPI-POM
```xml
<dependencies>
    <dependency>
        <groupId>co.elastic.clients</groupId>
        <artifactId>elasticsearch-java</artifactId>
        <version>8.10.2</version>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.12.3</version>
    </dependency>
    <dependency>
        <groupId>jakarta.json</groupId>
        <artifactId>jakarta.json-api</artifactId>
        <version>2.0.1</version>
    </dependency>
</dependencies>
```

#### JavaAPI-获取客户端
```java
public static ElasticsearchClient client = null;
public static ElasticsearchAsyncClient asyncClient = null;
public static ElasticsearchTransport transport = null;

RestClientBuilder builder = RestClient.builder(new HttpHost("localhost", 9200, "http"));
RestClient restClient = builder.build();
transport = new RestClientTransport(restClient, new JacksonJsonpMapper());
client = new ElasticsearchClient(transport);
asyncClient = new ElasticsearchAsyncClient(transport);

//关闭
transport.close();
```

## SpringData-Elasticsearch
POM
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-elasticsearch</artifactId>
</dependency>
```
配置文件
```yaml
spring:
  elasticsearch:
    rest:
      # repository
      uris: http://localhost:9200

  data:
    # elasticsearch template
    elasticsearch:
      repositories:
        enabled: true
      client:
        reactive:
          endpoints: localhost:9200
```
实体类
```java
@Data
@Builder
@Document(indexName = "spring-data-es")
public class Person {
    @Id
    private String id;
    private String name;
    private String gender;
    private Integer age;
    private Integer height;

//    @Field(type = FieldType.Nested, includeInParent = true)
    @Field(type = FieldType.Nested)
    private List<Student> students;
}
```
repository
```java
public interface PersonRepository extends ElasticsearchRepository<Person, String> {
    Page<Person> findByName(String name, Pageable pageable);
    List<Person> findByName(String name);
}
```
使用
```java
@SpringBootTest(classes = EsApplication.class)
@ExtendWith(SpringExtension.class)
class PersonRepositoryTest {

    @Autowired
    private PersonRepository personRepository;

    @Test
    void savePerson(){
        //保存
        Person one = Person.builder().id("1001").name("zhangsan").age(20).height(170).gender("male")
                .students(Arrays.asList(Student.builder().score(90).build())).build();
        personRepository.save(one);
    }

    @Test
    void findByName() {
        // 验证查询列表
        List<Person> list = personRepository.findByName("zhangsan");
        list.forEach(System.out::println);

    }

    @Test
    void testFindByName() {
        //验证分页方法
        Page<Person> page = personRepository.findByName("zhangsan", PageRequest.of(0, 1));
        System.out.println(page.getTotalPages());
        System.out.println(page.getNumber());
        page.getContent().forEach(System.out::println);
    }

    @Test
    void testUpdate(){
        //通过repository更新  没有部分更新，只有通过save方法整体更新
        Person person = Person.builder().id("1001").gender("lisi").build();
        personRepository.save(person); //整体更新了
    }

    @Test
    void testDelete(){
        //删除
        personRepository.deleteById("1001");
    }

    @Autowired
    private ElasticsearchRestTemplate restTemplate;

    @Test
    void testTemplate() throws JsonProcessingException {
       //保存 或者说 整体更新
//        Person one = Person.builder().name("zhangsan").id("1001").age(20).height(170).gender("female")
//                .students(Arrays.asList(Student.builder().score(90).build())).build();
//        restTemplate.save(one);
         
        // 通过template更新
//        HashMap<String, Object> map = new HashMap<>();
//        map.put("name","lisi");
//        String json = new ObjectMapper().writeValueAsString(one);
//        UpdateQuery query = UpdateQuery.builder("1001").withDocument(Document.parse(json)).build();
//        UpdateResponse res = restTemplate.update(query, IndexCoordinates.of("spring-data-es"));
//        System.out.println(res.getResult());

        // 通过template根据id查询
//        Person person = restTemplate.get("1001", Person.class);
//        System.out.println(person);
        
//        FuzzyQueryBuilder queryBuilder = QueryBuilders.fuzzyQuery("name", "zhangsan").fuzziness(Fuzziness.TWO);
        MatchAllQueryBuilder queryBuilder = QueryBuilders.matchAllQuery();
        NativeSearchQuery query = new NativeSearchQuery(queryBuilder);
        SearchHits<Person> hits = restTemplate.search(query, Person.class);
        hits.forEach(System.out::println);
    }

}
```
