# 常见问题与排错

这一页把分片上线后最常遇到的问题按**现象**归类：查不到数据、性能反而更差、数据对不上。每一条都给出「怎么定位」与「怎么修」，核心工具是**SQL 路由日志**。

::: tip 一句话定位
分片排查有一个别的领域没有的利器：**路由日志**。它直接告诉你「这条 SQL 实际打到了几个分片」。绝大多数问题在打开路由日志的那一刻就能定位。
:::

## 打开路由日志

这是排查任何分片问题的第一步。

```yaml [application.yml（本地/预发）]
spring:
  shardingsphere:
    props:
      sql-show: true       # 打印逻辑 SQL 与每条实际 SQL
```

日志形态：

```text
Logic SQL: SELECT * FROM t_order WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10
Actual SQL: ds1 ::: SELECT * FROM t_order_3 WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10
```

**读日志的三个要点**：

| 看什么 | 含义 |
| --- | --- |
| `Actual SQL` 的**条数** | 1 条 = 单播（最优）；N 条 = 多播；等于分片总数 = 广播（最差） |
| `dsX ::: t_order_Y` | 实际命中的库表，用于验证分片算法 |
| 改写后的 SQL | 分页、表名、聚合都被改写过了，确认改写是否符合预期 |

::: danger 路由日志不能带到生产
`sql-show: true` 会打印**每条** SQL（含参数拼接后的形态），日志量巨大，且可能包含敏感数据。

**正确做法**：
- 本地与预发打开，用于验证；
- 生产关闭，改为记录**聚合指标**：单播/多播/广播的查询次数占比。广播占比超过阈值时告警——这是一个非常有价值的监控指标。
:::

## 一类：查不到数据

### 1. 分片键没传

**现象**：明明写了数据，按某个条件却查不到。

**原因**：查询条件里没有分片键，中间件只能广播到所有分片；如果此时某个分片的数据还没同步到（如双写期间新写失败），就查不到。

**定位**：看路由日志的 `Actual SQL` 条数。如果只有 1 条，说明中间件认为它只该在 1 个分片里找——那就要确认这条数据到底写到了哪个分片。

**修复**：检查写入与查询使用的分片键值是否一致。常见的坑是**写入时用 `user_id`，查询时用的是从别处拿到的另一个 `userId`（如商户 ID）**。

### 2. 分片键值类型不一致

**现象**：`WHERE user_id = '123'`（字符串）能查到，`WHERE user_id = 123`（数字）查不到，或反之。

**原因**：分片算法对字符串 `"123"` 与数字 `123` 计算出的哈希值不同 → 路由到不同分片。

**定位**：在日志里对比两条 SQL 的 `Actual SQL` 的表名。如果不同，就是这个问题。

**修复**：统一分片键的 Java 类型（`Long`），并在接口层做参数校验与转换。**不要让它靠数据库的隐式转换兜底**。

### 3. 取模结果为负

**现象**：某些 `user_id` 的记录查不到。

**原因**：某些语言的 `%` 运算符对负数返回负数（如 Java 的 `-7 % 4 = -3`），导致算出的分片序号为负，路由到一个不存在的表。

**正确定法**：

```java
// 反例：负数取模得到负下标
int shard = userId % 16;

// 正例一：floorMod 保证结果非负
int shard = Math.floorMod(userId, 16);

// 正例二：位运算（仅当分片数是 2 的幂时可用，且要求 hash 非负）
int shard = (int) (userId & 15);   // 等价于 % 16，且对负数也返回非负
```

::: danger `Inline` 表达式里也可能踩到
ShardingSphere 的 `INLINE` 表达式（如 `user_id % 16`）使用的是 Groovy 表达式求值。**在分片键为负数时，需要确认其取模行为**。

**稳妥做法**：分片键在应用层就保证为正（如用户 ID 从 1 开始），或在表达式里显式取绝对值：`Math.abs(user_id) % 16`。上线前用「枚举 1~1000 与 -1~-1000」两组值验证路由结果。
:::

### 4. 广播表没同步

**现象**：JOIN 广播表时返回空结果。

**原因**：广播表只在部分数据源上建了表或写了数据。

**定位**：

```sql
-- 在每个数据源上分别查广播表的行数，应完全一致
SELECT COUNT(*) FROM t_dict_channel;   -- 在 ds0 上执行
SELECT COUNT(*) FROM t_dict_channel;   -- 在 ds1 上执行
```

**修复**：广播表的写入必须由中间件完成（配置成 `broadcast-tables` 后写操作会自动广播），**不要绕过中间件直接连库写入**——绕过之后只有那一个数据源有数据。

## 二类：性能反而更差

### 5. 查询变成了广播

**现象**：分片后某些查询比单库时慢好几倍。

**定位**：看日志里 `Actual SQL` 的条数是不是等于分片总数。

**四个常见原因**：

| 原因 | 例子 | 修复 |
| --- | --- | --- |
| 没带分片键 | `WHERE channel_id = 8` | 补分片键，或改走只读副本 |
| 分片键被函数包裹 | `WHERE DATE(user_id) = ?`、`WHERE user_id + 0 = ?` | 去掉函数，用原始列 |
| 字段名对不上 | `sharding-column: userId`（应为 `user_id`） | 改成数据库列名 |
| `IN` 条件过大 | `WHERE user_id IN (5000 个值)` | 控制批量大小，或接受多播 |

::: danger 把「不带分片键的查询」拦在入口
最有效的做法不是「想办法让它变快」，而是**在接口层禁止**：

```java
// 在 DAO 层加一道守卫：检测到可能广播的查询就拒绝
public class ShardGuardInterceptor implements InnerInterceptor {
    @Override
    public void beforeQuery(Executor executor, MappedStatement ms, Object parameter,
                            RowBounds rowBounds, ResultHandler resultHandler, BoundSql boundSql) {
        String sql = boundSql.getSql().toLowerCase();
        // 只对分片表生效
        if (!sql.contains("from t_order")) return;
        // 没有分片键条件 → 拒绝
        if (!sql.contains("user_id")) {
            throw new IllegalArgumentException(
                "查询 t_order 必须带 user_id 条件；如需全局查询请走只读副本或数仓：" + sql);
        }
    }
}
```

这道守卫的价值在于：**把「性能问题」变成「启动就能发现的错误」**，而不是等到线上出现慢查询才回头改代码。
:::

### 6. 深分页

**现象**：翻到后面几页时，查询时间从几十毫秒涨到几秒。

**定位**：看日志里改写后的 SQL，`LIMIT` 的值远大于实际需要的条数（`LIMIT 100020` 这种）。

**修复**：改用游标分页，见 [跨分片查询与分布式事务](../CrossShard/index.md)。

### 7. 归并排序吃内存

**现象**：查询大量跨分片排序的数据时，应用出现 GC 压力甚至 OOM。

**原因**：中间件把各分片返回的结果都拉到内存里做归并。

**修复**：

1. 让排序字段带分片键前缀（能定位到单片）；
2. 限制返回条数上限（应用层校验 `LIMIT ≤ 500`）；
3. 大结果集查询改走只读副本或数仓。

### 8. 连接池被撑爆

**现象**：`Too many connections`，或应用启动时连接数告警。

**定位**：

```sql
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';
```

**计算**：总连接数 = 数据源数 × 每池最大连接数 × 应用实例数。

```text
16 个分片（2 库） × 每池 20 连接 × 4 个应用实例 = 160 个连接
如果数据库 max_connections = 151（MySQL 默认值），直接爆
```

**修复**：① 减少每池的 `maximum-pool-size`；② 提高 `max_connections`（需同步考虑内存）；③ 分层部署（多个数据库实例，每实例承载部分分片）。

## 三类：数据对不上

### 9. 双写失败导致新表缺数据

**现象**：切读后部分订单查不到。

**定位**：查双写失败记录表。

```sql
-- 统计双写失败记录（迁移期专用表）
SELECT COUNT(*) AS fail_cnt, MIN(created_at), MAX(created_at)
FROM t_dual_write_failure
WHERE status = 0;
```

**修复**：重放失败记录（幂等写入新表），并对这段时间的订单做一次全量补数。**根因要一起解决**：为什么双写会失败（网络抖动、连接池不足、字段不兼容）？

### 10. 分布式事务未补偿

**现象**：订单创建成功，但库存没扣减。

**定位**：

```sql
-- 找出待发送但长期未成功的消息
SELECT * FROM t_local_message
WHERE status IN (0, 1) AND next_retry_at < DATE_SUB(NOW(), INTERVAL 10 MINUTE)
ORDER BY created_at;
```

**修复**：

1. 检查投递任务是否在运行（定时任务挂了是最常见原因）；
2. 检查下游是否幂等（若下游不幂等且已处理过，重投会造成重复扣减）；
3. `retry_count` 超过阈值后应转人工队列并告警。

::: danger 对账不是可选项
```sql
-- 每日对账：订单数与扣减流水数应相等
SELECT
  (SELECT COUNT(*) FROM t_order WHERE DATE(created_at) = CURDATE())               AS order_cnt,
  (SELECT COUNT(*) FROM t_stock_flow WHERE DATE(created_at) = CURDATE())          AS flow_cnt;
-- 差值 != 0 即告警，由人工或补偿任务处理
```

**对账机制的价值不在于「修数据」，而在于「让不一致可被发现」**。没有对账，不一致会一直积累到某天集中爆发；有对账，问题在产生的当天就能被处理。
:::

### 11. 分片键被业务修改

**现象**：某条数据「凭空消失」——查不到，但数据库里确实有。

**原因**：业务修改了分片键的值（如把订单从一个用户转给另一个用户），但数据仍留在原分片。之后按新的 `user_id` 查询，路由到新分片，自然找不到。

**修复**：这类操作必须实现为「**删除 + 重新插入**」（或跨分片搬迁），不能写成 `UPDATE t_order SET user_id = ?`。

::: tip 设计阶段就把这类操作识别出来
分片键必须**不可变**（见 [拆分策略与分片键设计](../Strategy/index.md) 的四条硬要求）。所以在设计阶段要问：

- 「这个字段的业务上会不会被修改？」
- 「如果必须修改，代价是什么？」

如果答案是「会且频繁」，那就不能选它做分片键。
:::

## 三句通用追问

遇到任何分片问题，先问自己这三句：

1. **「这条 SQL 实际打到几个分片？」** —— 打开路由日志，答案立刻可见。
2. **「这条数据按分片键应该落在哪个分片？」** —— 用 [实战页的枚举脚本](../Practice/index.md) 算一遍。
3. **「写入路径与查询路径走的是同一套规则吗？」** —— 应用（JDBC）与代理（Proxy）的规则不一致是最隐蔽的一类问题。

## 快速自查表

| 检查项 | 判定标准 | 怎么查 |
| --- | --- | --- |
| 路由是单播 | `Actual SQL` 只有 1 条 | 打开 `sql-show` |
| 分片键类型一致 | 写入与查询用同一 Java 类型 | 看接口签名 |
| 分片键非负 | 负数取模不会算出负下标 | 枚举 -1000~1000 验证路由 |
| 绑定表已配置 | 同分片键的表 JOIN 不跨片 | 看 `binding-tables` 配置 |
| 广播表数据一致 | 每个数据源的行数相同 | 分别 COUNT |
| 表结构一致 | 去掉表名后缀后 DDL 完全相同 | 批量 `SHOW CREATE TABLE` 比对 |
| 连接数可控 | 总连接 < `max_connections` 的 70% | 计算 + `SHOW STATUS` |
| 消息表在推进 | 无长期停留在「待发送」的记录 | 查 `t_local_message` |
| 对账任务在跑 | 每日有对账结果且差值为 0 | 看对账表或任务日志 |
| 生产已关 `sql-show` | 生产配置里为 `false` | 检查配置文件 |

## 最佳实践清单

::: tip 十条落地建议
1. **先排除 90% 不该拆的场景**（索引、从库、缓存、归档），再谈分片。
2. **分片键选「出现频率最高 + 基数高 + 不可变」的字段**。
3. **分片数取 2 的幂并留 2~4 倍余量**，宁多勿少。
4. **会一起查的表做成绑定表**（同分片键同算法），这是成本最低的优化。
5. **小字典表做成广播表**，避免跨片 JOIN。
6. **主键用雪花或号段**，不要用 UUID 做聚簇主键。
7. **业务单号单独设计**，带随机段防枚举。
8. **在 DAO 层加守卫**，禁止不带分片键的查询。
9. **迁移按六步走**，每步可停可回滚；读的切换排在写的切换之后。
10. **对账是常规机制**，不是出问题后的补救措施。
:::

## 参考资料

- [Apache ShardingSphere 官方文档](https://shardingsphere.apache.org/document/current/cn/overview/)
- [ShardingSphere · SQL 解析与路由](https://shardingsphere.apache.org/document/current/cn/features/sharding/principle/)（理解路由日志的原理）
- [ShardingSphere · DistSQL](https://shardingsphere.apache.org/document/current/cn/user-manual/shardingsphere-proxy/distsql/)（查看与调整分片规则）
- [MySQL 官方文档 · 服务端连接与线程](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_max_connections)（`max_connections` 相关）
- [MySQL 官方文档 · XA 事务](https://dev.mysql.com/doc/refman/8.4/en/xa.html)（`XA RECOVER` 排查未决事务）
- [项目交付 · 常见问题与排错](../../../../Others/ProjectDelivery/FAQ/index.md)（跨领域的问题分类与追问方法）
