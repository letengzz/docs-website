# PostgreSQL

<p style="text-align:center;"><img src="./assets/postgresql-logo.png" style="zoom:75%;" /></p>

PostgreSQL（常称 PG）是功能最强大的开源关系型数据库之一：完整 ACID、丰富类型（JSONB/数组/地理）、全文检索、分区表与强大扩展生态。本专题覆盖概述、安装、SQL 基础、高级特性、索引、备份恢复、性能调优与实战。

本专题默认基于 **PostgreSQL 18**（2025 年 9 月发布，当前稳定版 18.6），涉及版本差异时在文中标注。

- [PostgreSQL 概述](Overview/index.md)
- [安装与配置](Install/index.md)
- [SQL 基础](SqlBasic/index.md)
- [高级特性](Advanced/index.md)
- [索引详解](Index/index.md)
- [备份与恢复](BackupRestore/index.md)
- [性能调优](Performance/index.md)
- [实战：博客系统数据库](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 与在线协作任务看板的分工

本页是 PostgreSQL 的**通用用法**：安装、SQL 基础、索引、备份恢复。它不讲「一张会被多个人同时改的表该怎么设计」。

[在线协作任务看板 · 卡片拖动](../../../../project/Complete/TeamBoard/CardMove/index.md) 把两件 Postgres 能力用在同一个写操作上，是两条容易被忽视的事实来源：

| 能力 | 本页讲什么 | 任务看板用它解决什么 |
| --- | --- | --- |
| 乐观并发 | 事务与隔离级别的通用语义 | `version` 列 + `update ... where id = ? and version = ?`，受影响行数为 0 时返回 **409**（不是 200 也不是 500） |
| 字符串比较 | `COLLATE` 与排序规则的一般用法 | 顺序字段是**可比较字符串**而不是整数：整数 `position` 会让一次拖动写成整列更新；字符串排序要落在确定的 `COLLATE` 上，否则中文与大小写会让顺序在不同环境里不一致 |

::: danger 顺序字段用整数是这类系统最典型的设计事故
一次拖动只应该更新**一行**。用整数 `position`（1,2,3…）时，把第 5 张卡插到第 1 位需要把它前面四张各自 `+1`——于是「一次拖动」变成「一次批量更新」，并发下必然互相覆盖，而且**功能测试完全测不出来**（单用户操作看起来一切正常）。
:::

## 与「租户边界」章节集的分工（第 155 天补充）

| 维度 | 本页 | 「租户边界」章节集（第 155 天） |
| --- | --- | --- |
| 回答的问题 | 行级安全策略怎么写、`USING` 与 `WITH CHECK` 各管什么 | 在这套系统上，谁来用、用什么角色、越过边界时留什么痕 |
| 角色 | 不涉及（只假设有 `app_user`） | 四类角色：`app_owner` / `app_user` / `ops_readonly` / `platform_ops`，把「绕过 RLS」与「能写」拆成两个属性 |
| 备份与恢复 | 不涉及 | `pg_dump` 默认把 `row_security` 设为 `off`，因此备份账号必然是「能绕过 RLS」的账号；恢复后必须验一次跨租户查询 |
| 粒度 | 单条策略 | 策略 + 应用层上下文 + 缓存 key + 对象 key 前缀，四条链路一起看 |

一句话结论：**本页讲「策略能写成什么样」，章节集讲「这套策略在真实系统里被谁绕开、怎么发现」**。

::: danger 这一页特有的坑
本页的 RLS 示例只写了 `ENABLE ROW LEVEL SECURITY`。表 owner 默认**不受**策略约束，所以只写这一句时，用 owner 连接跑出来的结果永远是全量——必须同时写 `FORCE ROW LEVEL SECURITY`，并用非 owner 角色验证。
:::

## 相关专题

::: tip 与「向量数据库深入」专题的分工（第 135 天补充）
PG 通过 `pgvector` 扩展提供向量类型与近邻检索（HNSW / IVFFlat 两种索引），因此「用不用 PG 存向量」
是选型阶段的常见问题。分工是：**本专题讲 PG 自身**（SQL、高级特性、索引详解、备份恢复、性能调优，
以及 pgvector 的安装与建索引写法），[向量数据库深入](../../VectorDatabase/index.md) 讲**向量检索的引擎侧机制**——
HNSW 的三参数各自换到什么、量化能省多少内存、带过滤条件的检索为什么会让召回崩（选择性悬崖）、
pgvector 的迭代扫描怎么开、内存与容量怎么按三段做预算。

判据一句话：**「数据已经在 PG 里、能不能不引新组件」看本专题；「引了之后参数怎么定、容量怎么算」看那边。**
把选型问题当机制问题处理（或反过来）是本库最常见的一次误判——选型错了要换组件，调参错了只需改配置，
两者的成本差一个数量级。
:::

::: tip 与「分布式锁与选主」专题的分工（第 159 天补充）
PG 自带两种「锁服务」能力：行锁（`SELECT ... FOR UPDATE`）与会话级 / 事务级咨询锁（`pg_try_advisory_lock` / `pg_try_advisory_xact_lock`）。新增的 [三种实现](/docs/Backend/DistributedLock/Implementations/index.md) 把它们与 Redis、etcd 放在一起比较「正确性托付给谁」，本页只讲语法与事务语义。

第 159 天在本机 PG 18.6 上实测的三条读数，可直接当排障依据：

| 动作 | 读数 | 含义 |
| --- | --- | --- |
| 同一会话连续三次 `pg_try_advisory_lock(42)` | `t \| t \| t` | 会话级咨询锁**可重入**，内部计数 +1 |
| 连接断开后新会话再加同一把 | `t` | 会话结束自动释放，不会泄漏 |
| 另一事务持锁时 `SELECT ... FOR UPDATE` | 阻塞 **1.34 s** | 行锁是**真阻塞**，必须配 `lock_timeout` 或 `NOWAIT` |

最容易踩的是第一行：连接池复用连接时，上一次的咨询锁还挂着，下一个请求会「莫名抢不到」。修法是成对解锁，或改用 `pg_try_advisory_xact_lock` 让 `COMMIT` 自动释放。
:::
