# 响应式数据访问

响应式链路的成败，八成取决于数据访问层：**JDBC 是阻塞的**，只要它出现在非阻塞链路里，前面所有的努力都会被抵消。这一页讲 R2DBC 的正确用法、事务边界、连接池这个新瓶颈，以及五个最容易藏阻塞的位置。

## 一句话定位

R2DBC（Reactive Relational Database Connectivity）是「关系型数据库的非阻塞驱动规范」。它不是一个 ORM——它给出的是**基于 Reactive Streams 的数据库连接与结果流**，上层由 Spring Data R2DBC 包成 Repository 形态。

::: warning 本节的前提
**JDBC 与 JPA 无法变成非阻塞。** 这不是配置问题，而是协议与驱动模型的问题：JDBC 的 `ResultSet` 是「一次读一行、读完才返回」的阻塞接口，任何「异步包装」都只是在外面套了一层线程（`Mono.fromCallable(() -> jdbc.query(...)).subscribeOn(boundedElastic())`）——那是虚拟线程路线的做法，不是响应式。
:::

## 一、JDBC 与 R2DBC 的模型差异

| 维度 | JDBC / JPA | R2DBC |
| --- | --- | --- |
| 调用模型 | 阻塞，调用线程等到结果 | 非阻塞，结果通过 `Publisher` 推送 |
| 结果读取 | `ResultSet` 游标逐行读 | `Flux<Row>` 流，可背压 |
| 线程占用 | 等待期间占住线程 | 只占一个连接，不占线程 |
| 事务 | `ThreadLocal` 绑定（`@Transactional`） | `ReactiveTransactionManager`，事务上下文随订阅传播 |
| 生态成熟度 | 极高（ORM、分页插件、审计、动态 SQL） | 中等：动态 SQL、复杂映射、分页需要自己补 |
| 适用 | 绝大多数 CRUD 业务 | 高并发非阻塞链路 |

::: tip 一句话判据
链路里出现 `java.sql.*` 或 `javax.sql.DataSource` 的调用栈，就说明这段是阻塞的。**要么换成 R2DBC，要么把这段隔离到 `boundedElastic` 线程池，并承认它是链路的容量瓶颈。**
:::

## 二、R2DBC 起步

### 2.1 依赖

```groovy [build.gradle]
dependencies {
    // Boot 4.1 统一管理版本：starter 不要手写版本号
    implementation 'org.springframework.boot:spring-boot-starter-data-r2dbc'
    runtimeOnly 'io.asyncer:r2dbc-mysql'        // MySQL 驱动（1.4.x）
    // 或 runtimeOnly 'org.postgresql:r2dbc-postgresql'
    testImplementation 'io.projectreactor:reactor-test'
}
```

```yaml [application.yml]
spring:
  r2dbc:
    url: r2dbc:mysql://127.0.0.1:3306/blog?serverZoneId=Asia%2FShanghai
    username: app
    password: ${DB_PASSWORD}
    pool:
      initial-size: 4
      max-size: 16            # 与数据库 max_connections 一起算，不是越大越好
      max-idle-time: 30m
      max-acquire-time: 3s    # 拿不到连接时的等待上限，必须有
```

::: danger 三个配置陷阱
1. **`url` 必须是 `r2dbc:` 前缀**：写成 `jdbc:mysql://` 会在启动时报驱动找不到，或者更糟——在运行时以奇怪的错误失败。
2. **`max-acquire-time` 不配**：拿不到连接时会**无限等待**，表现为请求悬挂、最终被网关超时切断，而日志里没有任何错误。
3. **`max-size` 与数据库 `max_connections` 不匹配**：多个实例 × 每实例 pool size 很容易超过数据库上限，结果是「连接被拒绝」的间歇性故障。
:::

### 2.2 两种使用方式

```java [DatabaseClientDemo.java]
// 方式一：DatabaseClient（细粒度控制，适合复杂查询）
@Component
public class ArticleQuery {

    private final DatabaseClient client;

    public Flux<ArticleRow> topByViews(int limit, long offset) {
        return client.sql("""
                SELECT id, title, view_count FROM article
                WHERE status = 'PUBLISHED'
                ORDER BY view_count DESC LIMIT :limit OFFSET :offset
                """)
            .bind("limit", limit)
            .bind("offset", offset)
            .map((row, meta) -> new ArticleRow(
                row.get("id", Long.class),
                row.get("title", String.class),
                row.get("view_count", Long.class)))
            .all();
    }
}
```

```java [ArticleRepository.java]
// 方式二：Repository（CRUD 与简单派生查询，最省事）
public interface ArticleRepository extends ReactiveCrudRepository<Article, Long> {

    Flux<Article> findByStatusOrderByViewCountDesc(String status, Pageable pageable);

    // 返回值也可以是 Mono<Long>，但不要写成 long（那会迫使实现去 block）
    Mono<Long> countByStatus(String status);

    @Query("SELECT * FROM article WHERE team_id = :teamId AND status = 'PUBLISHED'")
    Flux<Article> listPublished(long teamId);
}
```

::: warning 方法返回值不要用「非响应式类型」
Spring Data R2DBC 支持在 Repository 方法上返回 `Flux` / `Mono`（推荐）；一旦签名写成 `List<Article>` 或 `long`，框架只能在内部把流收集起来再返回，**这会把非阻塞结果转成同步等待**，在某些版本上直接抛 `BlockingOperationError`。判据：**Repository 的返回值里不应该出现非响应式类型**。
:::

## 三、事务边界

响应式事务的核心难点：**事务上下文不再靠 `ThreadLocal` 绑定，而是随着订阅链传播**。

```java [OrderService.java]
@Service
public class OrderService {

    // ① 声明式：方法必须返回 Mono/Flux，且链路上不能出现 block()
    @Transactional
    public Mono<Void> placeOrder(Order order) {
        return orderRepository.save(order)
            .then(stockRepository.decrease(order.itemId(), order.qty()))
            .then(eventPublisher.publish(new OrderPlaced(order.id())));
    }

    // ② 编程式：需要根据条件动态决定事务边界时使用
    private final TransactionalOperator operator;

    public Mono<Long> upsertWithRetry(Order order) {
        return operator.transactional(
            orderRepository.save(order).map(Order::id)
                .delayUntil(id -> stockRepository.decrease(order.itemId(), order.qty()))
        );
    }
}
```

| 手段 | 生效条件 | 注意 |
| --- | --- | --- |
| `@Transactional` | 方法返回 `Mono` / `Flux`；事务管理器是 **`ReactiveTransactionManager`**；链路上没有 `block()` | 在同一个类内部自调用不生效（AOP 代理限制，与 MVC 相同） |
| `TransactionalOperator` | 需要动态边界、需要显式组合 | 事务范围就是括号里那条管道 |
| `R2dbcTransactionManager` | Boot 自动装配（有 R2DBC 时） | 与 JDBC 的 `DataSourceTransactionManager` **不能混用** |

::: danger 三条「事务静默失效」
1. **链路上出现 `block()`**：一旦阻塞，事务上下文所在的订阅链被切断，后续操作**不在同一事务里**——而代码看起来完全正常。
2. **`flatMap` 里另起订阅**：在 `flatMap` 内部对另一个 `Mono` 调用 `.subscribe()`，那是一个**独立订阅**，不受外层事务管辖。
3. **两种数据访问混用**：同一个方法里既用 R2DBC 又用 JDBC，事务各管一半，回滚时只回滚了一半——这类问题通常在对账时才发现。
:::

## 四、五个最容易阻塞的位置

![响应式链路里五个最容易阻塞的位置](../assets/rp-blocking-sites.svg)

| # | 位置 | 症状 | 判据 | 替代 |
| --- | --- | --- | --- | --- |
| 1 | JDBC / JPA 调用 | 并发上不去、CPU 低、线程都在 `socketRead` | `jstack` 里出现 `HikariPool-*` 或 `pooled-*` 在 socket 读 | 换 R2DBC，或隔离到 `boundedElastic` |
| 2 | `RestTemplate` / 阻塞 HTTP 客户端 | event loop 线程出现 `synRead` 等待 | BlockHound 直接报错并给栈 | `WebClient` / 响应式 HTTP Interface |
| 3 | `synchronized` 段里有 IO 或重计算 | 偶发尖刺，与 QPS 不相关 | 看锁竞争与持有时长 | 改 `ReentrantLock` + 缩小临界区；热点数据移出 |
| 4 | 文件、命令、同步日志 | P99 与磁盘相关 | 链路上出现 `FileInputStream` / `ProcessBuilder` | 异步日志、独立有界线程池 |
| 5 | 自己写的阻塞 | 压测正常、生产偶发大面积超时 | BlockHound 在 CI 里常开 | `publishOn(boundedElastic)`，或改为异步组合 |

```java [BlockingIsolation.java]
// 确认无法避免的阻塞调用：显式隔离，并给它一个有界线程池
private final Scheduler blockingScheduler =
        Schedulers.newBoundedElastic(8, 100_000, "legacy-io", 60, true);

public Mono<Report> build(long id) {
    return Mono.fromCallable(() -> legacyReportService.build(id))   // 阻塞方法
        .subscribeOn(blockingScheduler)                             // 明确放在弹性线程上
        .timeout(Duration.ofSeconds(3));
}
```

::: tip 隔离是权宜之计，不是终点
隔离解决的是「不要拖累其他请求」，不解决「这段的吞吐上限」。线程池大小就是这段的并发上限——**必须把它当作容量约束写进压测报告**，并给它单独的指标（排队时长、拒绝数）。
:::

## 五、连接池：新的瓶颈

响应式的一大反直觉之处：**并发度不再由线程数限制，于是瓶颈立刻转移到连接池**。

| 参数 | 作用 | 经验取值 | 不配的后果 |
| --- | --- | --- | --- |
| `initial-size` | 启动时建几条连接 | 与最小并发匹配（如 4） | 首个请求要等建连 |
| `max-size` | 每实例最大连接数 | 与慢查询并发匹配（8~24 常见） | 过小则排队，过大则压垮数据库 |
| `max-acquire-time` | 拿连接的等待上限 | 200ms~3s（小于接口 SLA） | 无限等待 → 请求悬挂 |
| `max-idle-time` | 空闲连接回收 | 30m | 连接被数据库侧先断开（`wait_timeout`）导致偶发失效 |
| `validation-query` / `validation-depth` | 借出前校验 | 视驱动默认 | 拿到死连接，第一个请求必失败 |

::: danger 连接池相关的三个典型故障
1. **池满 + 无限等待**：表现为「接口从某一刻起全部超时」，`jstack` 里大量线程在拿连接。必须配 `max-acquire-time`，并让超时抛出**可识别**的异常（`PoolAcquireTimeoutException`）而不是笼统的 500。
2. **数据库侧先断开**：MySQL 默认 `wait_timeout` 8 小时，JVM 侧连接池还留着，于是「隔夜第一个请求失败」——`max-idle-time` 要小于数据库侧超时。
3. **压测时把库打垮**：`max-size` 设成 200 看起来能扛，但数据库 `max_connections` 只有 500，多实例部署时直接连不上。
:::

## 六、其他数据源的响应式选择

| 组件 | 响应式客户端 | 阻塞替代（不要用在响应式链路） |
| --- | --- | --- |
| MySQL / PostgreSQL / MariaDB / SQL Server | R2DBC 驱动 | JDBC、JPA、MyBatis |
| Redis | **Lettuce**（Spring Data Redis Reactive 默认）/ Redisson | Jedis |
| MongoDB | 官方响应式驱动（`spring-boot-starter-data-mongodb-reactive`） | 同步 MongoTemplate |
| Elasticsearch | 官方 `ElasticsearchClient` 的响应式 API | 旧版 `RestHighLevelClient` |
| Kafka | `reactor-kafka` | 原生 `KafkaConsumer` 拉取循环 |
| 文件 / 本地命令 | **无** | 只能隔离到 `boundedElastic` 或独立线程池 |

```java [RedisReactive.java]
// 响应式缓存读写：链路上依然是管道，不产生阻塞等待
public Mono<Article> get(long id) {
    return redis.opsForValue().get("article:" + id)
        .map(json -> jsonMapper.read(json, Article.class))
        .switchIfEmpty(repository.findById(id)
            .flatMap(a -> redis.opsForValue()
                .set("article:" + id, jsonMapper.write(a), Duration.ofMinutes(10))
                .thenReturn(a)));
}
```

## 验证方式

响应式数据访问的正确性靠两类验证：**功能断言 + 阻塞门禁**。

```java [ReactiveDataAccessTest.java]
@SpringBootTest
class ReactiveDataAccessTest {

    // ① 功能与时序：写入后立刻能查到（事务边界是否正确）
    @Test
    void 事务内写入对后续读取可见() {
        StepVerifier.create(service.placeOrder(new Order(1L, 2)))
            .verifyComplete();
        StepVerifier.create(repository.findById(1L))
            .expectNextMatches(o -> o.qty() == 2)
            .verifyComplete();
    }

    // ② 事务回滚：第二步失败时第一步必须回滚
    @Test
    void 第二步失败时第一步回滚() {
        StepVerifier.create(service.placeOrderWithFailure(new Order(2L, 999)))
            .expectError(IllegalStateException.class)
            .verify();
        StepVerifier.create(repository.findById(2L)).verifyComplete();   // 不应存在
    }
}
```

```shell
# ③ 阻塞门禁（最关键的一步）：把 BlockHound 装进集成测试
#    加依赖：testImplementation 'io.projectreactor.tools:blockhound'
#    在测试基类里安装并放宽允许的 API（见调试与排障页），
#    这样「有人在响应式链路上写了阻塞调用」会让集成测试直接失败。
./gradlew test --tests '*ReactiveDataAccessTest'
# 预期：全部通过；出现 BlockingOperationError 必须当成缺陷修，不要放宽放行清单。

# ④ 连接池与慢查询的现场判据
jcmd <pid> Thread.print | grep -c "r2dbc"          # 预期：远小于并发数（连接不绑线程）
curl -s http://127.0.0.1:8080/actuator/metrics/r2dbc.pool.acquired
```

::: warning 判据不是实测记录
上面三段是判据：`BlockHound` 的放行清单要按自己项目实际用到的 API 收敛，不要照抄。本机没有可运行工程时如实标注「未跑 + 原因」。
:::

## 参考资料

- R2DBC 官方网站（驱动与规范）：https://r2dbc.io/
- Spring Data R2DBC 官方文档：https://docs.spring.io/spring-data/relational/reference/r2dbc.html
- Spring Framework 官方文档 · 响应式事务：https://docs.spring.io/spring-framework/reference/data-access/transaction/reactive.html
- `r2dbc-mysql` 项目主页（版本事实来源）：https://github.com/asyncer-io/r2dbc-mysql
- BlockHound 项目主页（阻塞检测）：https://github.com/reactor/BlockHound
