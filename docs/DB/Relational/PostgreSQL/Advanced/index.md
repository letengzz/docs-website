# 高级特性

PostgreSQL 的高级特性让它超越「传统关系型」：JSONB 文档能力、全文检索、分区表、物化视图与丰富扩展（PostGIS、pgvector）。本页逐个实战讲解。

## 特性地图

![高级特性](./../assets/pg-advanced.svg)

## JSONB：文档能力

```sql
-- Advanced/01-jsonb.sql
CREATE TABLE products (
    id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    attrs   JSONB NOT NULL DEFAULT '{}'
);

INSERT INTO products (name, attrs) VALUES
    ('手机', '{"brand": "X", "ram": 8, "colors": ["黑", "白"]}'),
    ('笔记本', '{"brand": "Y", "ram": 16, "colors": ["灰"]}');

-- 路径查询
SELECT name, attrs->>'brand' AS brand, attrs->'ram' AS ram
FROM products
WHERE attrs @> '{"ram": 16}';

-- 更新 JSON 字段
UPDATE products
SET attrs = jsonb_set(attrs, '{ram}', '12')
WHERE name = '手机';
```

::: tip JSONB 要点
- `jsonb`（二进制、可索引、去重）优于 `json`（原样文本）；
- `@>`（包含）、`->`/`->>`（取值）与 GIN 索引配合；
- 适合「结构会变的半结构化字段」，固定字段仍用列。
:::

## 全文检索

```sql
-- Advanced/02-fulltext.sql
CREATE TABLE articles (
    id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title   TEXT NOT NULL,
    body    TEXT NOT NULL
);

-- 建立 tsvector 生成列 + GIN 索引
ALTER TABLE articles
ADD COLUMN search_vec tsvector
GENERATED ALWAYS AS (to_tsvector('simple', title || ' ' || body)) STORED;

CREATE INDEX articles_search_idx ON articles USING GIN (search_vec);

-- 查询
SELECT title
FROM articles
WHERE search_vec @@ to_tsquery('simple', '数据库 & 优化');
```

::: warning 中文分词
内置分词器对中文支持有限；生产中文搜索需扩展（如 zhparser、pg_jieba）或接 Elasticsearch。
:::

### 权重与排序：`{D, C, B, A}` 的顺序坑（第 167 天补充）

上面那条生成列把 `title` 与 `body` 拼成了一串，**两者同权重**。要区分，得用 `setweight` 分开写：

```sql
ALTER TABLE articles ADD COLUMN search_vec_w tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(body, '')),  'D')
) STORED;
```

排序时 `ts_rank` / `ts_rank_cd` 的**权重数组顺序固定为 `{D, C, B, A}`**：

```sql
-- 标题最重：A 在最后一位，取 1.0
SELECT ts_rank_cd('{0.1, 0.2, 0.4, 1.0}', search_vec_w, q) FROM articles, websearch_to_tsquery('simple','索引') q;
-- 写成 {1.0, 0.4, 0.2, 0.1} 就变成「正文最重」，且不会报任何错
```

另外两点：`ts_rank` **不是 BM25**（没有词频饱和与长度归一），得分只能在**同一查询内**比较；`websearch_to_tsquery` 比手拼 `to_tsquery` 安全得多，用户输入 `&`、`|` 时不会抛语法错。

工程层（选型、评估、重建、容量）见 [全文检索与搜索工程](/docs/DB/FullTextSearch/index.md)；本节只保留语法与两个高频坑。

## 分区表

```sql
-- Advanced/03-partition.sql
CREATE TABLE orders (
    id          BIGINT GENERATED ALWAYS AS IDENTITY,
    user_id     BIGINT NOT NULL,
    amount      NUMERIC(10,2) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

-- 按月建分区
CREATE TABLE orders_2026_07 PARTITION OF orders
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE orders_2026_08 PARTITION OF orders
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

-- 分区裁剪：只扫相关分区
EXPLAIN SELECT * FROM orders WHERE created_at >= '2026-08-01' AND created_at < '2026-09-01';
```

分区类型：`RANGE`（范围）、`LIST`（列表）、`HASH`（哈希）。

## 物化视图

```sql
-- Advanced/04-materialized.sql
-- 复杂报表预计算
CREATE MATERIALIZED VIEW monthly_stats AS
SELECT
    date_trunc('month', created_at) AS month,
    COUNT(*) AS orders,
    SUM(amount) AS total
FROM orders
GROUP BY 1;

-- 刷新（可加 CONCURRENTLY 避免阻塞查询，需唯一索引）
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_stats;

-- 查询
SELECT * FROM monthly_stats ORDER BY month DESC;
```

## 视图 / 存储过程 / 触发器

```sql
-- Advanced/05-procedure.sql
-- 视图
CREATE VIEW active_users AS
SELECT id, username, created_at FROM users WHERE status = 'active';

-- 存储过程（PL/pgSQL）
CREATE OR REPLACE FUNCTION create_user(p_username TEXT, p_email TEXT)
RETURNS BIGINT AS $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO users (username, email) VALUES (p_username, p_email)
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

SELECT create_user('carol', 'carol@example.com');

-- 触发器：更新 updated_at
CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_touch BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
```

## 扩展生态

```sql
-- Advanced/06-extensions.sql
-- 统计插件（调优必备）
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 地理空间
CREATE EXTENSION IF NOT EXISTS postgis;

-- AI 向量检索（RAG）
CREATE EXTENSION IF NOT EXISTS vector;

-- 模糊匹配
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### pgvector 示例

```sql
-- Advanced/07-pgvector.sql
CREATE TABLE embeddings (
    id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    content  TEXT,
    embedding vector(1536)
);

CREATE INDEX embeddings_idx ON embeddings
USING hnsw (embedding vector_cosine_ops);

-- 相似度检索
SELECT content, 1 - (embedding <=> $1::vector) AS similarity
FROM embeddings
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

## 易错点与最佳实践

::: danger 常见坑
1. **JSONB 字段全表扫描**：查询 JSON 条件必须建 GIN 索引。
2. **分区表不建索引**：分区索引要建在每个分区（或通过父表 `CREATE INDEX ON ONLY` 管理）。
3. **物化视图不刷新**：数据过期，需定期 `REFRESH`（cron / pg_cron）。
4. **触发器滥用**：隐藏逻辑难排查，优先应用层事务。
5. **扩展版本与 PG 不匹配**：装扩展前核对兼容性。
:::

::: tip 最佳实践
- JSONB 用于「属性可变」的字段，核心业务字段坚持强类型列；
- 大表（千万级+）用分区 + 定期归档；
- pgvector 适合中小规模向量检索，超大规模（千万+）考虑专用向量库。
:::

## 验证方式

```sql
-- 逐节执行后验证
SELECT attrs->>'brand' FROM products WHERE attrs @> '{"ram": 16}';
EXPLAIN SELECT * FROM orders WHERE created_at >= '2026-08-01';
SELECT * FROM monthly_stats ORDER BY month DESC LIMIT 5;
```

预期：JSONB 查询返回品牌、分区查询走 `Seq Scan on orders_2026_08`（分区裁剪）、物化视图返回统计行。

## 与分区分表与冷热分离专题的分工

本页「分区表」一节只回答**语法怎么写**（`PARTITION BY RANGE`、建分区、`EXPLAIN` 里看到裁剪）。下面四件事归专题页：

- 分区键怎么选、粒度与分区数上界（含每分区约 6 µs 规划开销的实测）：[分区策略](/docs/DB/PartitionArchival/PartitionStrategy/index.md)
- `ATTACH` / `DETACH`、默认分区的三重代价、PG 18 的 `VACUUM` 继承行为：[分区维护](/docs/DB/PartitionArchival/PartitionOps/index.md)
- 为什么 `date_trunc('month', ts) = ?` 会扫全部分区：[跨分区查询](/docs/DB/PartitionArchival/CrossPartition/index.md)
- 到期分区怎么摘、怎么搬、怎么校验：[在线归档](/docs/DB/PartitionArchival/OnlineArchive/index.md)

本页特有的一个坑：示例里 `orders` 带 `GENERATED ALWAYS AS IDENTITY`，日后若用 `CREATE TABLE new_part (LIKE orders INCLUDING ALL)` 建表再 `ATTACH`，会直接报 `table ... being attached contains an identity column`——`INCLUDING ALL` 把 identity 一起复制了过去。回挂用的分区表要用 `LIKE orders`（默认不含 identity）。

## 与「通知中心读接口」的分工

本页讲 PostgreSQL 的**语法与能力**（部分索引、`INCLUDE`、行值比较、`EXPLAIN` 读法）。**「什么时候该建两条索引」这个判断属于应用侧**，见[在线协作任务看板 · 通知中心读接口](/project/Complete/TeamBoard/NotificationCenter/index.md)。

那页给出的实测值得在这里补一句，因为它是本页「部分索引」一节最容易被忽略的边界：

| 写法 | 未读计数 | 「全部通知」列表 |
| --- | --- | --- |
| 只有 `(recipient_id, created_at) WHERE read_at IS NULL` | **0.660 ms**（走部分索引） | **10.143 ms**（`Parallel Seq Scan`，3,538 buffers） |
| 再补 `(recipient_id, created_at DESC, id DESC)` | 0.660 ms | **0.093 ms**（`Index Scan`，23 buffers） |

::: danger 部分索引只能服务「部分」
`WHERE read_at IS NULL` 的索引**不包含已读行**，所以任何「不带 `read_at` 条件」的查询都用不上它——优化器会安静地退化成全表扫描，`EXPLAIN` 里只留下一行 `Rows Removed by Filter: 66633`。
判断方法：`EXPLAIN (ANALYZE, BUFFERS)` 里如果没有出现你预期的索引名，先看**该索引的谓词是否覆盖了这次查询的行集**，而不是先怀疑统计信息。
:::

## 与「部署前置」章节集的分工（第 169 天补充）

本页讲 PostgreSQL 的**事务、锁模式与并发控制机制**；[迁移前置闸门](/project/Complete/TeamBoard/MigrationPreflight/index.md) 讲的是「把这些机制用在上线那一刻」的工程闸门。分工：

| 问题 | 归本页 | 归「部署前置」章节集 |
| --- | --- | --- |
| 八种表锁的冲突矩阵、MVCC 与隔离级别 | ✅ 机制 | —— |
| 迁移该设多大的 `lock_timeout`、超时后怎么办 | —— | ✅ `MGP-A` |
| `ACCESS EXCLUSIVE` 为什么阻塞一切 | ✅ | —— |
| 排队中的 DDL 为什么会把只读查询一起堵住（实测 1.19 s） | —— | ✅ `MGP-B` |

::: danger 本页特有的一条坑：锁队列是「后来者堵后来者」
`ACCESS EXCLUSIVE` 在队列里排队时，**后续到达的普通 `SELECT` 不能越过它去和持锁者共享锁**（否则排队的 DDL 会被饿死）。所以一条只读查询会被一条尚未执行的 `ALTER` 堵住——本机实测：会话 A 持锁 2 s、会话 B 的 `ALTER` 排队、会话 C 的 `select count(*)` 等了 **1.19 s** 才返回。这就是「迁移引发全站超时」的真实机制：不是 DDL 慢，是它在队列里当了一堵墙。结论：迁移必须设 `lock_timeout`（200~500 ms），失败后**不许自动重试**。
:::

## 参考资料

- [PostgreSQL JSON 类型](https://www.postgresql.org/docs/current/datatype-json.html)
- [PostgreSQL 全文检索](https://www.postgresql.org/docs/current/textsearch.html)
- [PostgreSQL 分区](https://www.postgresql.org/docs/current/ddl-partitioning.html)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
