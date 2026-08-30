# 常见问题与最佳实践

汇总 PostgreSQL 使用中最高频的问题：选型、迁移、膨胀、连接、JSON、备份与升级，方便快速查阅。

## 选型与迁移

### PostgreSQL 和 MySQL 怎么选？

| 你的情况 | 推荐 |
| --- | --- |
| 复杂查询、报表、窗口函数 | PostgreSQL |
| JSON 半结构化 + 关系数据 | PostgreSQL（JSONB） |
| GIS / 向量检索（AI） | PostgreSQL（PostGIS/pgvector） |
| 团队全栈熟悉 MySQL、生态依赖 | MySQL |
| 云厂商托管服务选择 | 按团队与场景评估 |

### 从 MySQL 迁移要注意什么？

1. **自增**：`AUTO_INCREMENT` → `GENERATED ALWAYS AS IDENTITY`；
2. **字符串拼接**：`CONCAT()`/`+` → `||`；
3. **布尔**：`0/1` → `TRUE/FALSE`；
4. **反引号**：→ 双引号（或不用）；
5. **`LIMIT`** 语法基本一致，但 `ON DUPLICATE KEY UPDATE` → `ON CONFLICT ... DO UPDATE`；
6. 类型与函数逐表核对，用迁移工具（pgloader）可提速但必须验证。

## 存储与类型

### 自增主键用 SERIAL 还是 IDENTITY？

推荐 `GENERATED ALWAYS AS IDENTITY`：

```sql
CREATE TABLE t (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
);
```

`SERIAL` 是历史写法（隐式序列），新代码用标准 IDENTITY。

### JSON 用 json 还是 jsonb？

**用 jsonb**：

- 二进制存储、支持索引（GIN）、自动去重；
- 查询运算符（`@>`、`->>`）更丰富；
- 输入校验严格，写入略慢可接受。

### 金额用什么类型？

`NUMERIC(p,s)`，不用 `FLOAT/DOUBLE`（精度丢失）。

## 性能与维护

### 表越来越大、查询越来越慢？

排查顺序：

1. 是否缺少索引（EXPLAIN 看 Seq Scan）；
2. 是否统计信息过期（ANALYZE）；
3. 是否死元组堆积（`n_dead_tup` 高 → VACUUM）；
4. 是否缓存命中率低（`shared_buffers` 不足）；
5. 是否连接/锁等待（`pg_stat_activity`）。

### 连接数打满怎么办？

1. 应用接入连接池（PgBouncer）复用连接；
2. 调小应用池与 `max_connections` 匹配；
3. 排查泄漏连接（未关闭的连接）；
4. 避免每请求新建连接。

### 需要手动跑 VACUUM 吗？

默认 autovacuum 会处理；手动场景：

- 大批量更新/删除后立即 VACUUM ANALYZE；
- `VACUUM FULL` 压缩膨胀（低峰期、pg_repack 更稳）；
- 大表调小 autovacuum 触发阈值。

## JSONB 与全文

### JSONB 字段要索引吗？

高频查询条件（`@>`、`->>`）必须建 GIN 索引：

```sql
CREATE INDEX ON products USING GIN (attrs);
```

### 中文全文检索怎么实现？

PG 内置分词器对中文支持有限，方案：

1. 扩展：zhparser / pg_jieba；
2. 应用层分词后存 tsvector；
3. 规模大用 Elasticsearch。

## 备份与升级

### 只备份数据文件行不行？

**不行**。直接拷贝数据目录不是一致备份（写并发），必须用：

- `pg_dump`（逻辑备份）；
- `pg_basebackup`（物理备份）；
- pgBackRest/Barman（生产级全量 + WAL）。

### 大版本升级怎么做？

```shell
# 1. 完整备份
pg_dumpall -U postgres -f /backup/pre-upgrade.sql
# 或 pg_basebackup

# 2. 用 pg_upgrade（推荐：快、可回退）
pg_upgrade --old-datadir=... --new-datadir=... --old-bindir=... --new-bindir=...

# 3. 升级后运行 ANALYZE + 回归测试
```

升级前必须演练；PostgreSQL 18 起统计信息可随 pg_upgrade 保留。

## 安全类

### 远程访问怎么配才安全？

1. `pg_hba.conf` 限定来源 IP + `scram-sha-256`；
2. 禁止 `trust` 认证；
3. 应用用专用低权限账号；
4. 生产走内网/VPN，不直接暴露 5432；
5. 开启 SSL（`ssl = on`）。

### 用户权限如何最小化？

```sql
-- 只读账号
CREATE ROLE readonly LOGIN PASSWORD 'xxx';
GRANT CONNECT ON DATABASE appdb TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

## 最佳实践清单

::: tip PostgreSQL 检查清单
1. 主键用 IDENTITY，金额用 NUMERIC；
2. 时间统一 TIMESTAMPTZ；
3. JSONB 配 GIN 索引；
4. 高频查询验证 EXPLAIN ANALYZE；
5. autovacuum 开启并监控死元组；
6. 连接走 PgBouncer，max_connections 合理；
7. 备份 = 全量 + WAL 归档 + 定期恢复演练；
8. 大版本升级前完整备份 + pg_upgrade；
9. 远程访问限定 IP + scram + SSL；
10. 复杂查询用窗口函数/CTE 保持可读。
:::

## 参考资料

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [PostgreSQL 中文社区](http://www.postgres.cn/)
- [PostgreSQL wiki（FAQ）](https://wiki.postgresql.org/wiki/FAQ)
