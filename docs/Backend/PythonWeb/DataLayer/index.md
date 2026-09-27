# 数据层：SQLAlchemy 2.0 与 Alembic

一句话定位：SQLAlchemy 2.0 的价值不是「多了新功能」，而是**把 ORM 与 Core 统一到一套 `select()` 语法**——以前 ORM 有 `session.query()`、Core 有 `select()`，两套写法互不通气；2.0 之后只有一套，而且全部支持类型推断。Alembic 则是把「改表结构」变成可 review、可回滚的代码。

![SQLAlchemy 的会话、事务与连接池三层结构](../assets/sqlalchemy-session.svg)

## 一、2.0 与 1.4 的根本变化

| 场景 | 1.x 写法 | 2.0 写法 |
| --- | --- | --- |
| 查询 | `session.query(User).filter(User.id == 1)` | `session.execute(select(User).where(User.id == 1))` |
| 单条 | `session.query(User).get(1)` | `session.get(User, 1)` |
| 字段列 | `session.query(User.name)` | `select(User.name)` |
| 连接 | `engine.execute(...)` | `with engine.connect() as conn: conn.execute(...)` |
| 模型基类 | `declarative_base()` | `class Base(DeclarativeBase)` |
| 字段声明 | `name = Column(String(32))` | `name: Mapped[str] = mapped_column(String(32))` |
| 异步 | 需第三方 `databases` | **原生 `AsyncSession`** |

::: danger 注意：`engine.execute()` 在 2.0 已被移除
1.4 里它是「废弃但仍可用」，2.0 直接删除。如果升级后报 `AttributeError: 'Engine' object has no attribute 'execute'`，改法是显式建连接：

```python
with engine.begin() as conn:      # begin() 自动开启并提交事务
    conn.execute(text("UPDATE t SET x = 1"))
```
:::

## 二、模型定义：类型注解驱动的写法

```python
from datetime import datetime
from decimal import Decimal
from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "t_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(32), default=None)
    balance_cents: Mapped[int] = mapped_column(BigInteger, default=0, comment="单位：分")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="user", lazy="raise")

class Order(Base):
    __tablename__ = "t_order"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("t_user.id", ondelete="RESTRICT"), index=True)
    amount_cents: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(16), default="created")
    idem_key: Mapped[str | None] = mapped_column(String(64), unique=True, default=None)

    user: Mapped[User] = relationship(back_populates="orders", lazy="raise")

    __table_args__ = (
        Index("idx_user_status_created", "user_id", "status", "id"),
    )
```

::: tip `lazy="raise"` 是异步项目里的必选项
SQLAlchemy 默认 `lazy="select"`——访问 `order.user` 时会**隐式再发一条 SQL**。在异步会话里，这种隐式 IO 会在「不在 `await` 上下文」时触发，直接抛 `MissingGreenlet` 错误；即使侥幸不报错，它也是 **N+1 查询的源头**。

设成 `lazy="raise"` 后，任何未显式加载的关联访问都会报错，**强制你在查询时用 `selectinload()` 明确写出要加载什么**。这是把「性能问题在开发期暴露」的最小代价方案。
:::

## 三、查询：只写一种风格

### 基础与关联加载

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# 单条
stmt = select(User).where(User.id == 1)
user = (await session.execute(stmt)).scalar_one_or_none()

# 列表 + 关联（一次额外查询解决 N+1，而不是 N 次）
stmt = (
    select(Order)
    .options(selectinload(Order.user))
    .where(Order.user_id == 1)
    .order_by(Order.id.desc())
    .limit(20)
)
orders = (await session.execute(stmt)).scalars().all()

# 只取需要的列（避免 SELECT *）
stmt = select(Order.id, Order.amount_cents).where(Order.status == "created")
rows = (await session.execute(stmt)).all()
```

四种加载策略的取舍：

| 策略 | 生成的 SQL | 适用 | 风险 |
| --- | --- | --- | --- |
| `selectinload` | 1 + 1（子查询 IN） | **默认首选**，一对多 | 关联数极大时 IN 列表很长 |
| `joinedload` | 1（LEFT JOIN） | 多对一、一对一 | 一对多会产生笛卡尔积行数放大 |
| `subqueryload` | 1 + 1（子查询） | 复杂过滤场景 | 旧写法，一般用 `selectinload` 替代 |
| `lazy="raise"` | 不生成 | 强制显式声明 | 需要每个查询都写 `options` |

### 分页的正确写法

```python
# 深分页必须用游标（keyset）而不是 OFFSET
stmt = (
    select(Order)
    .where(Order.user_id == user_id)
    .where(Order.id < cursor)              # 上一页最后一条的 id
    .order_by(Order.id.desc())
    .limit(page_size)
)
```

::: danger 注意：`OFFSET 100000` 是性能陷阱
`LIMIT 20 OFFSET 100000` 要求数据库**先扫描并丢弃 10 万行**。数据量上来后，第 1 页 5 ms、第 5000 页 3 s。游标分页（`WHERE id < last_id ORDER BY id DESC LIMIT 20`）在任意页都是索引范围的顺序读，耗时恒定。前提是**排序字段上有索引**，且不能跳页（这是可接受的取舍）。
:::

### 批量操作与 upsert

```python
from sqlalchemy.dialects.mysql import insert as mysql_insert

# 批量插入：一次 SQL 而不是 N 次
await session.execute(
    mysql_insert(Order),
    [{"user_id": u, "amount_cents": a} for u, a in batch],
)

# 幂等写入：唯一键冲突时改为更新（MySQL 方言）
stmt = mysql_insert(Order).values(user_id=1, amount_cents=100)
stmt = stmt.on_duplicate_key_update(amount_cents=stmt.inserted.amount_cents)
await session.execute(stmt)
```

## 四、异步引擎与 Session 生命周期

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    "mysql+asyncmy://user:pass@127.0.0.1:3306/shop?charset=utf8mb4",
    pool_size=20,             # 常驻连接数
    max_overflow=10,          # 峰值可临时超出 10 条（共 30）
    pool_timeout=5,           # 等连接超过 5s 就报错，快速失败
    pool_recycle=1800,        # 30 分钟主动回收（必须小于服务端 wait_timeout）
    pool_pre_ping=True,       # 取连接前 ping 一次，检出坏连接
    echo=False,
)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,   # 关键：见下方说明
    autoflush=False,
)
```

::: danger 注意：`expire_on_commit` 默认是 `True`，异步下必须改
默认行为是「commit 后把所有已加载对象标记为过期」，下次访问属性时会**再发一次查询刷新**。在同步代码里这只是多一次查询；在异步代码里，这个「隐式查询」发生在你没有 `await` 的地方，直接抛：

```text
MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
```

所以在 FastAPI + `AsyncSession` 的组合里，**`expire_on_commit=False` 是必须的**。代价是 commit 后对象里的值可能「不是最新」（被其他事务改过），这属于可接受的权衡——需要强一致就重新查询。
:::

### 会话与事务的边界

```python
# 推荐的会话工厂（供 FastAPI 依赖使用）
async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# 需要显式控制事务边界时（比如一个逻辑里要提交两次）
async def create_with_audit(db: AsyncSession, payload: dict):
    async with db.begin():                  # 独立事务
        order = Order(**payload)
        db.add(order)
    # 出了 with 已提交
    async with db.begin():                  # 第二个独立事务
        db.add(AuditLog(action="create_order"))
```

::: warning 说明：`async with session.begin()` 与 `session.commit()` 不要混用
`session.begin()` 会开启一个事务上下文，退出时自动 commit。如果在里面又手动 `commit()`，SQLAlchemy 2.0 会报 `InvalidRequestError: A transaction is already begun`。**一个会话内只用一种事务控制方式**。
:::

## 五、连接池：参数与「隐形上限」

### 端到端的连接预算

数据库的连接数是**所有实例共享的硬上限**，必须从总量倒推：

```text
DB max_connections = 500
├─ 业务服务 4 个实例 × (pool_size 20 + max_overflow 10) = 120
├─ 定时任务 2 个实例 × (5 + 2) = 14
├─ 运维/迁移工具预留 = 20
└─ 余量（应对突发与人工排查）= 346  ✅
```

如果算下来超出上限，表现是 **`Too many connections`**，而且往往发生在扩容时——新实例一起启动、一起建连，把连接占满。

| 参数 | 建议 | 说明 |
| --- | --- | --- |
| `pool_size` | 按上表倒推，通常 10~20 | 常驻连接，占内存但不占 CPU |
| `max_overflow` | `pool_size` 的 50% | 峰值缓冲；给太大会在突发时打爆 DB |
| `pool_timeout` | 3~5 s | **快速失败**，不要默认的 30 s（会把请求全堆住） |
| `pool_recycle` | 1800 s | 必须小于服务端 `wait_timeout` |
| `pool_pre_ping` | `True` | 每次取连接做一次轻量探活（约 0.1 ms），代价远小于重建 |

::: danger 注意：用了 PgBouncer / ProxySQL 之后 `pool_pre_ping` 可能失效
中间件通常不允许 `SELECT 1` 这类探活语句（或会拦截）。此时可能出现「池里全是坏连接但 pre_ping 检不出」的情况。对策是把 `pool_recycle` 设得更短（如 300 s），让连接在中间件的空闲回收之前就被客户端主动淘汰。
:::

## 六、Alembic：把改表变成可 review 的代码

### 初始化与日常工作流

```shell
# 一次性初始化
alembic init -t async migrations        # -t async 生成异步模板
# 编辑 alembic.ini 的 sqlalchemy.url，或在 env.py 里从应用配置读取

# 日常三步
alembic revision --autogenerate -m "add idem_key to t_order"   # 1. 生成草稿
# 2. 人工 review 生成的脚本（必做，见下方清单）
alembic upgrade head                                            # 3. 应用
```

### `--autogenerate` 检测不到的四类变更（必须手写）

| 变更 | 为什么检不到 | 手写要点 |
| --- | --- | --- |
| **列改名** | 只能看到「删了一列、加了一列」 | 手改成 `alter_column(..., new_column_name=...)`，否则会丢数据 |
| **`server_default` 变化** | 部分方言不支持对比 | 显式写 `server_default` |
| **索引 / 唯一约束的名字变化** | 只按结构对比 | 显式 `op.create_index(..., name=...)` |
| **表注释、列注释、字符集** | 不在对比范围 | 手写 `op.alter_column(..., comment=...)` |

::: danger 注意：`--autogenerate` 的脚本必须人工 review
最常见的生产事故是「autogenerate 生成了一个 `drop_column`」，因为本地模型删了字段但没人意识到**生产数据还在那一列里**。review 清单固定四条：

1. **有没有 `drop_column` / `drop_table`？** 有就必须确认是「确实要删」而不是「模型没同步」。
2. **有没有 `alter_column` 改类型？** MySQL 改类型可能锁表，大表必须用 `ALTER ... ALGORITHM=INPLACE` 或 gh-ost。
3. **加索引是否在高峰期？** 大表加索引要 `ALTER TABLE ... ADD INDEX ..., ALGORITHM=INPLACE, LOCK=NONE`。
4. **`downgrade()` 是否真的可回滚？** 很多自动生成的 `downgrade` 是空的，出事时退不回去。

**删除列的正确流程是三步而不是一步**：① 发布「不再读写该列」的代码 → ② 观察至少一个发布周期 → ③ 再删列。一次删掉会让灰度中的旧版本代码直接报错。
:::

### 迁移的纪律

| 纪律 | 原因 |
| --- | --- |
| **迁移脚本与代码一起提交** | Schema 与代码不同步时，回滚会卡住 |
| **一个迁移只做一件事** | 失败时能精确定位；重跑更容易 |
| **禁止在迁移里写业务数据修复** | 迁移是 DDL 工具，数据修复要有独立脚本与幂等设计 |
| **上线顺序：先迁移后发布** | 新代码可能依赖新列；兼容旧代码的迁移（先加可空列）是无停机升级的标准做法 |
| **保留 `downgrade` 且验证过** | 没验证过的 `downgrade` 等于没有 |

## 七、常见问题与排错

| 现象 | 高概率原因 | 定位手段 |
| --- | --- | --- |
| `MissingGreenlet` | 在异步会话里访问了未预加载的关联，或 `expire_on_commit=True` | 查该对象的关联是否写了 `selectinload`；确认 `expire_on_commit=False` |
| `Too many connections` | 连接池总量 × 实例数 超出 DB 上限 | 按第五节算一遍端到端预算 |
| 每小时一批 `Lost connection` | `pool_recycle` 大于服务端 `wait_timeout` | 把 `pool_recycle` 调到 1800 或更小 |
| `A transaction is already begun` | 同时用了 `session.begin()` 与 `session.commit()` | 每种会话只用一种事务控制方式 |
| 列表接口慢且 SQL 数量 = 记录数 + 1 | N+1 查询 | 打开 `echo=True` 或看慢查询日志统计条数；加 `selectinload` |
| `idle in transaction` 堆积 | 异常路径没 rollback | 查 `pg_stat_activity.state`；确认依赖的 `except` 里有 rollback |

```shell
# 快速确认「一条请求发了几条 SQL」：打开引擎 echo
# create_async_engine(..., echo=True) 后请求一次，数日志里 SELECT 的条数
```

## 八、验证方式

```shell
# 1. 模型与数据库是否一致（迁移没落后）
alembic check
# 期望：No new upgrade operations detected

# 2. 当前版本
alembic current
# 期望：输出 head 的 revision id 与 "(head)"

# 3. 从零重建（验证迁移链完整、可复现）
dropdb shop_dev 2>/dev/null; createdb shop_dev
alembic upgrade head && alembic current
# 期望：无报错，current 为 head

# 4. 验证可回滚（至少退一步再前进）
alembic downgrade -1 && alembic upgrade head
# 期望：两步都无报错

# 5. 连接池健康状况（MySQL）
docker exec -i mysql mysql -uroot -ppass -e \
  "SHOW STATUS LIKE 'Threads_connected'; SHOW VARIABLES LIKE 'max_connections';"
# 期望：Threads_connected 明显小于 max_connections
```

::: tip 第 3、4 步应该是 CI 的固定环节
「从零重建能成功」与「能回滚一步」这两条，是迁移链唯一可靠的健康判据。放进 CI 的成本是几秒钟，收益是避免上线时才发现第 7 个迁移脚本坏了。
:::

## 参考资料

- [SQLAlchemy 2.0 官方：ORM 快速入门](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [SQLAlchemy 2.0 迁移指南（1.4 → 2.0）](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [SQLAlchemy 官方：关系加载技术（selectinload / joinedload）](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)
- [SQLAlchemy 官方：连接池配置](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [Alembic 官方：自动生成迁移的注意事项](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)
- [MySQL：`ALTER TABLE` 的 Online DDL 支持](https://dev.mysql.com/doc/refman/8.4/en/innodb-online-ddl-operations.html)

## 相关页面

- [FastAPI 进阶：类型、异步与依赖注入](../FastAPI/index.md) —— `get_db` 依赖与会话生命周期
- [框架选型：FastAPI / Django / Flask](../Overview/index.md) —— 数据层选型的上下文
- [实战：可部署的 API 服务](../Practice/index.md) —— 迁移在部署流水线里的位置
- [关系型数据库](../../../DB/Relational/index.md) —— 索引与查询优化的底层原理
- [SQL 优化](../../../DB/Relational/SQLOptimization/index.md) —— 深分页与索引失效的完整分析
- [分库分表](../../../DB/Relational/Sharding/index.md) —— 单库装不下之后的下一步
