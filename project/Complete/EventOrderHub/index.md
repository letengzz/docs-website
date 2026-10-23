# 事件驱动订单与履约中心

**一句话定位**：做一个「下单 → 支付 → 库存预占 → 发货 → 完成 / 退款」的订单中心，把跨服务的一致性用**事件 + 本地事务表**做出来，并保证每一步都能在本地复现、能对账、能补偿。

周期 7（第 181–210 天）从 0 到 1 交付。与周期 6 的 TeamBoard 不同，这个项目的难点不在「多人实时」，而在**「一笔订单跨四个上下文之后，怎么证明它没丢、没重、没停留在中间态」**。

::: tip 本项目的三个「不做」
1. **不接真实支付通道**：支付只做到「渠道回调的验签、幂等、对账」这一层，不申请任何商户号。
2. **不做物流轨迹**：履约只到「发货单 + 运单号 + 签收状态回传」，不接快递公司 API。
3. **不做商品中心**：商品与价格由外部给定（本项目内用一张 `product_snapshot` 表模拟），避免把范围撑成电商全站。
:::

## 一、四周里程碑

| 周 | 天数 | 里程碑 | 验收（可执行） |
| --- | --- | --- | --- |
| 第 1 周 | 181–187 | 需求设计 | 需求拆分、技术选型、架构图、ER 图、完整 DDL、接口契约齐全 |
| 第 2 周 | 188–194 | 核心编码 | 服务能启动、下单/支付/发货接口可调用、事件能投递 |
| 第 3 周 | 195–201 | 联调测试 | 四类一致性用例全绿、幂等与补偿验证、压测达标 |
| 第 4 周 | 202–210 | 部署验收 | 一键部署、监控接入、上线验收清单全通过、对账日报可跑 |

## 二、上下文边界

![订单中心上下文地图](./assets/eoh-context-map.svg)

| 上下文 | 拥有什么数据 | 明确不拥有 | 对外只暴露 |
| --- | --- | --- | --- |
| 订单（Order） | `orders`、`order_items`、`order_events`、`outbox` | 库存数量、支付流水 | 下单、取消、查询、状态事件 |
| 库存（Inventory） | `stock`、`stock_reservation` | 订单金额、买家信息 | 预占、释放、确认扣减 |
| 支付（Payment） | `payment`、`payment_callback_log` | 订单状态（只发事件） | 发起支付、回调处理、退款 |
| 履约（Fulfillment） | `shipment`、`shipment_item` | 支付金额 | 创建发货单、签收回传 |
| 通知（Notify） | `notify_task` | 任何业务状态 | 消费事件、发消息 |

**关键决定**：订单是**唯一有权改订单状态**的上下文。库存、支付、履约只发事件（`stock.reserved`、`payment.succeeded`、`shipment.delivered`），由订单侧消费后推进状态机。这样「订单状态」只有一个写者，避免了四个服务同时改一个字段的经典泥潭。

## 三、章节清单

| 章节 | 判据族 | 这一族管什么 | 条数 |
| --- | --- | --- | --- |
| [需求拆分：五个上下文与订单状态机](Requirements/index.md) | `EOH` | 上下文边界、十状态十六迁移、六条不变量 | 8 |
| [技术选型与版本基线](TechBaseline/index.md) | `ETS` | 版本选择理由、三条能力边界、本地最小可跑集 | 8 |
| [架构设计：事件流与一致性边界](Architecture/index.md) | `EOA` | 同步/异步定性、事件信封、topic 分区、三处事务 | 8 |
| [数据库设计：九张表与六条不变量](DatabaseDesign/index.md) | `EDB` | DDL 约束、部分索引、不变量 SQL、并发实测 | 8 |
| [第 1 周收口 · 接口契约与第 1 周验收](Week1Gate/index.md) | `EW1` | 9 端点幂等与迁移覆盖、错误码表、契约⇄DDL 对齐、七道门 | 8 |
| [第 2 周第 1 步 · 环境与工程骨架](Bootstrap/index.md) | `EEN` | 四层依赖方向、三套 profile、启动六步、池预算、五条验收 | 8 |
| [第 2 周第 2 步 · 下单链路与 outbox 首次写入](OrderFlow/index.md) | `EOR` | 五步顺序与回滚点、条件扣减、outbox 同事务、SKIP LOCKED 投递 | 8 |
| [第 2 周第 3 步 · 支付回调：验签、幂等与对账](PaymentCallback/index.md) | `EPY` | 五步顺序、回调唯一键、CAS 守卫、双向对账、乱序应用 | 8 |
| [第 2 周第 4 步 · 库存预占的释放与超时回滚](StockRelease/index.md) | `EIV` | 三态迁移、宽限期扫描、双向 CAS、回补同事务 | 8 |
| [第 3 周第 1 步 · 一致性用例矩阵](ConsistencyMatrix/index.md) | `ECM` | 四类场景、18 条用例、迁移覆盖率、并发对照 | 8 |
| [第 3 周第 2 步 · 并发与幂等专项](ConcurrencyIdempotency/index.md) | `ECC` | 三组竞态实测、CAS 与唯一键两层守卫、退款第二次回补 | 8 |
| [第 3 周第 3 步 · 压测与容量](CapacityTest/index.md) | `ECP` | 四档并发读数、尾延迟、outbox 排空、容量算式 | 8 |
| [第 3 周第 4 步 · 第 3 周验收](Week3Gate/index.md) | `EW3` | 29 条结论合成、七道门、批量化四档读数与误伤、四条负向复验 | 8 |
| [第 4 周第 1 步 · 一键部署与配置](DeployCompose/index.md) | `EDP` | 三处 dev/deploy 差异、健康驱动顺序、探针分层、密钥注入、九条验收 | 8 |
| [第 4 周第 2 步 · 监控与告警](Monitoring/index.md) | `EMT` | 五个指标、p99 口径、双序列阈值校准、燃烧率双档、积压差分 | 8 |
| [第 4 周第 3 步 · 发布与回滚](ReleaseRollback/index.md) | `ERB` | 五阶段状态机、可回滚边界、相对基线判据、回滚验证 | 8 |

后续 5 章（判据族已预留，交付时补条数）：

- 发货与签收（判据族 `ESF`：发货单、签收、异常件）
- 补偿与对账（判据族 `ERC`：补偿动作、对账日报）
- 第 2 周验收（判据族 `EW2`：第 2 周六项验收）
- 上线验收与对账日报（判据族 `ELA`：上线清单与日报）
- 第 4 周验收与交接（判据族 `EW4`：四周收口与交接）

> 章节按天推进，**每章都自带「如何验证」**：读者按页面里的命令跑一遍，应得到页面写明的读数。项目目录只放 Markdown 与配图，不放任何工程文件。

## 四、技术基线（第 182 天定稿）

| 层 | 定稿版本 | 理由（一句话） |
| --- | --- | --- |
| 语言/运行时 | **Java 25（LTS）** | 与周期 6 保持同一基线，虚拟线程适合大量短事务 |
| 框架 | **Spring Boot 4.1.1**（Spring Framework 7.0.9） | 4.1.x 在 OSS 支持窗口内（至 2027-07），事务、调度、可观测开箱即用 |
| 数据库 | **PostgreSQL 18.6** | 需要 `FOR UPDATE SKIP LOCKED`（扫描 outbox）与 `jsonb`（事件载荷） |
| 消息 | **Kafka 4.2.1（KRaft，单节点）** | 4.x 起 ZooKeeper 已移除；本地单节点只验语义，不追集群 |
| 缓存 | **Redis 8.2** | 幂等键与热点商品快照，按「可丢」设计 |
| 迁移 | **Flyway 11.x** | 迁移以手写 SQL 为主，`afterMigrate` 回调挂清单校验 |
| 可观测 | **OpenTelemetry 1.62 + Prometheus** | 事件延迟与积压必须能看见 |

三条能力边界（详见 [技术选型与版本基线](TechBaseline/index.md)）：**事务内一致性归 PostgreSQL**（订单 + 订单项 + outbox 同事务）、**跨上下文一致性归 outbox + Kafka**（至少一次 + 消费端幂等）、**缓存只做加速不做判定**。

## 五、第 181 天交付

- 新建 [需求拆分：五个上下文、十个故事与订单状态机](Requirements/index.md)（判据 `EOH-A` ~ `EOH-H`）。
- 两张自绘示意图：`eoh-context-map.svg`（上下文与事件方向）、`eoh-order-state.svg`（十状态十六迁移）。
- 本机实测两份读数，写进章节：① 状态机可达性（10 状态 / 16 迁移 / 全部可达 / `CANCELLED → SHIPPED` 无路径）；② `check-then-act` 与 `compare-and-set` 的对比（**双成功 1000/1000 对 0/1000**）。

**如何验证**（读者可执行）：

```shell
# 1) 状态机可达性：把章节里的状态与迁移抄成两个列表，跑一遍 BFS
python3 - <<'PY'
states = ["CREATED","AWAITING_PAYMENT","PAID","ALLOCATED","SHIPPED","COMPLETED","CANCELLED","REFUNDING","REFUNDED","CLOSED"]
trans = [("CREATED","AWAITING_PAYMENT"),("CREATED","CANCELLED"),("AWAITING_PAYMENT","PAID"),
         ("AWAITING_PAYMENT","CANCELLED"),("AWAITING_PAYMENT","CLOSED"),("PAID","ALLOCATED"),
         ("PAID","REFUNDING"),("PAID","CANCELLED"),("ALLOCATED","SHIPPED"),("ALLOCATED","REFUNDING"),
         ("SHIPPED","COMPLETED"),("SHIPPED","REFUNDING"),("COMPLETED","REFUNDING"),
         ("REFUNDING","REFUNDED"),("CANCELLED","CLOSED"),("REFUNDED","CLOSED")]
adj = {s: [] for s in states}
for a, b in trans: adj[a].append(b)
seen, stack = {"CREATED"}, ["CREATED"]
while stack:
    s = stack.pop()
    for n in adj[s]:
        if n not in seen: seen.add(n); stack.append(n)
print("states=%d trans=%d reachable=%d" % (len(states), len(trans), len(seen)))
PY
# 期望输出：states=10 trans=16 reachable=10
```

**下一步**（第 183 天）：架构设计：事件流与一致性边界——五条事件的完整流向、outbox 投递器三个参数、消费端幂等键与去重窗口、三类故障的检测手段。

## 六、第 182 天交付

- 新建 [技术选型与版本基线](TechBaseline/index.md)（判据 `ETS-A` ~ `ETS-H`）。
- 一张自绘示意图：`eoh-tech-baseline.svg`（三条能力边界与本地最小可跑集）。
- 七条组件的版本表，每条都带「为什么不是相邻版本」与「已知坑」；三条能力边界写成可检查的判据。
- 本地最小可跑集：3 个容器（PG 18.6 / Kafka 4.2.1 / Redis 8.2）+ `deploy/compose.yaml` 骨架 + 四段验收命令。

**如何验证**（读者可执行，四步全过才算基线可跑）：

```shell
# 1) 编排文件语法
docker compose -f deploy/compose.yaml config >/dev/null && echo COMPOSE_OK

# 2) 三个容器健康
docker compose -f deploy/compose.yaml up -d
docker compose -f deploy/compose.yaml ps --format 'table {{.Name}}\t{{.Status}}'
# 期望：三行均为 (healthy)

# 3) 关键版本与参数
docker exec eoh-pg psql -U eoh -d eoh -Atc "select version();"
docker exec eoh-pg psql -U eoh -d eoh -Atc "show lock_timeout; show statement_timeout;"
docker exec eoh-redis redis-cli INFO server | grep redis_version
# 期望：PostgreSQL 18.6 / 3s / 30s / redis_version:8.2.x
```

## 七、第 183 天交付

- 新建 [架构设计：事件流与一致性边界](Architecture/index.md)（判据 `EOA-A` ~ `EOA-H`）。
- 一张自绘示意图：`eoh-architecture.svg`（一个写者、两条通道、三处事务，含下游事件回流）。
- 今天把前两天的结论**落成结构**：18 个跨上下文调用逐个定性同步/异步、事件信封六个必填字段、四个 topic 的分区键与保留期、三处事务的可执行 SQL、七种失败的归属矩阵。
- 一条本机实测读数（2000 条未发布、limit 500、两路并发）：`FOR UPDATE SKIP LOCKED` 两路各拿 500、**重复 0**；去掉它，两路都抓到同一批 500 条、**重复 500**。

**如何验证**（读者可执行，六步全过才算架构落地）：

```shell
# 1) 起骨架（PG 18.6 / Kafka 4.2.1 / Redis 8.2）
docker compose -f deploy/compose.yaml up -d && docker compose -f deploy/compose.yaml ps

# 2) 建 topic（关闭自动创建，避免 topic 拼错却"能用"）
docker exec -it eoh-kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 --create \
  --topic order.events --partitions 3 --replication-factor 1
docker exec -it eoh-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
# 期望：只有你手动建的 topic

# 3) outbox 表与部分索引
docker exec eoh-pg psql -U eoh -d eoh -c "\d outbox"
# 期望：出现 idx_outbox_unpublished ... WHERE (NOT published)

# 4) relay 并发零重复：两个终端同时执行章节里的 CTE + UPDATE
# 期望：各返回 500 行，两个结果集交集为空

# 5) 幂等表去重：同一 event_id 插两次
# 期望：第二次 ERROR 23505，业务表状态不变

# 6) 参数兜底
docker exec eoh-pg psql -U eoh -d eoh -Atc "show lock_timeout;"
# 期望：3s（迁移与 DDL 不会挂住队列）
```

**下一步**（第 184 天）：数据库设计——九张表的完整 DDL + 六条不变量的可执行 SQL，把今天的 outbox 扩成完整表族。

## 八、第 184 天交付

- 新建 [数据库设计：九张表与六条不变量](DatabaseDesign/index.md)（判据 `EDB-A` ~ `EDB-H`）。
- 一张自绘示意图：`eoh-db-design.svg`（五个上下文、十张表、六条不变量）。
- **九张业务表 + outbox 的完整 DDL**（含生成列、部分唯一索引、成对 CHECK），并回答了第 183 天留下的一个缺口：`order_events` 不单独建表，事件已在 `outbox` 里。
- **六条不变量各配一条可执行 SQL**，在 10 万单 / 30 万明细上实测：I1 199 ms、I2 95 ms、I3 21 ms、I4 22 ms、I5 21 ms、I6 52 ms，基线全部为 0；逐条埋违反后全部抓得到。
- 三组必须两个会话才能测出来的行为：① 幂等键冲突**阻塞 2.30 s 后**才报 23505（不是立刻失败）；② 条件 UPDATE 后到者**阻塞 1.41 s 后 `UPDATE 0`**，最终 `reserved=1/1` 零超卖；③ 在数量型库存上误用 `EXCLUDE` 约束 → `23P01`，第二笔订单下不进去。
- 两条反例读数：`uuidv7()` 主键索引 **6,184 KB vs 8,752 KB（−29.3%）**、按 id 取 1 万行 **64 页 vs 1,274 页**；`stored` 生成列让 10 万行插入 **288.6 ms → 522.6 ms（+81%）**。
- 造数翻车记录：脚本给两个租户建了预留却只给一个租户建库存行 → I3 一次报 **2,994 条**违反；修一行 SQL 后归零。

**如何验证**（读者可执行，六步全过才算设计落地）：

```shell
# 1) 建库 + 十张表（期望：约 1 秒，无报错）
docker run -d --name eoh-pg -e POSTGRES_PASSWORD=eoh -p 55432:5432 postgres:18
docker exec -i eoh-pg psql -U postgres -c "create database eoh"
docker exec -i eoh-pg psql -U postgres -d eoh -f 001_schema.sql

# 2) 表数（期望：10）
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
  "select count(*) from pg_class where relkind='r' and relnamespace='public'::regnamespace;"

# 3) 六条不变量（期望：全部 0）
docker exec -i eoh-pg psql -U postgres -d eoh -f 900_invariants.sql

# 4) 幂等插入：两个会话同键（期望：后到者约 2s 后 23505；改 on conflict 则 0 行不报错）

# 5) 防超卖：两个会话条件 UPDATE（期望：UPDATE 1 / UPDATE 0，最终 reserved=total）

# 6) 排他约束误用演示（期望：ERROR 23P01）
docker exec -i eoh-pg psql -U postgres -d eoh -f 910_slot_hold_demo.sql
```

**下一步**（第 186 天）：第 2 周第 1 步「环境与工程骨架」已交付（见下节）；接着做第 2 周第 2 步——下单链路与 outbox 的第一次真实写入（`POST /api/orders` 的幂等键校验 → 状态机守卫 → 订单/明细/outbox 三表同事务，判据族建议 `EOC`）。

## 九、第 185 天交付

- 新建 [第 1 周收口 · 接口契约与第 1 周验收](Week1Gate/index.md)（判据 `EW1-A` ~ `EW1-H`）。
- 一张自绘示意图：`eoh-week1-gate.svg`（七道门 + 契约面三类断言）。
- **9 个端点的契约总表**：每个写接口都标出幂等键来源、能触发的状态迁移、声明的错误码；`GET` 接口明确不参与状态机。
- **8 个错误码**的口径表，其中 `DUPLICATE_CALLBACK` 用 **200 + code**（渠道把非 2xx 当失败会持续重推 24 小时）。
- **契约字段 ⇄ DDL 列**的对照表 + 三条硬约定（金额只用 `numeric` 列、时间只用 `timestamptz`、契约不发明列）。
- **收口当天真的抓到了 5 条 FAIL**：需求页里的 5 条迁移没有任何接口能触发（退款路径完全缺失）→ 补 `cancel_order` 的三条迁移 + 新增 `POST /api/orders/{id}/refunds`，端点 8 → 9，重跑 `fails=0`。

**如何验证**（读者可执行，四步全过才算第 1 周收口）：

```shell
# 1) 契约自检（G5/G6/G7）
python3 week1_gate.py
# 期望：states=10 transitions=16 endpoints=9 errors=8 fields=24 / G5=PASS G6=PASS G7=PASS fails=0

# 2) DDL 与六条不变量回归
docker exec -i eoh-pg psql -U postgres -d eoh -f 900_invariants.sql
# 期望：六条不变量各返回 0；表数 10

# 3) 状态机：十状态全可达、唯一终态 CLOSED
python3 - <<'PY'
states = ["CREATED","AWAITING_PAYMENT","PAID","ALLOCATED","SHIPPED","COMPLETED",
          "CANCELLED","REFUNDING","REFUNDED","CLOSED"]
trans = [("CREATED","AWAITING_PAYMENT"),("CREATED","CANCELLED"),("AWAITING_PAYMENT","PAID"),
         ("AWAITING_PAYMENT","CANCELLED"),("AWAITING_PAYMENT","CLOSED"),("PAID","ALLOCATED"),
         ("PAID","REFUNDING"),("PAID","CANCELLED"),("ALLOCATED","SHIPPED"),("ALLOCATED","REFUNDING"),
         ("SHIPPED","COMPLETED"),("SHIPPED","REFUNDING"),("COMPLETED","REFUNDING"),
         ("REFUNDING","REFUNDED"),("CANCELLED","CLOSED"),("REFUNDED","CLOSED")]
adj = {s: [] for s in states}
for a, b in trans: adj[a].append(b)
seen, stack = {"CREATED"}, ["CREATED"]
while stack:
    for n in adj[stack.pop()]:
        if n not in seen: seen.add(n); stack.append(n)
print("reachable=%d terminal=%s" % (len(seen), sorted(s for s in states if not adj[s])))
PY
# 期望：reachable=10 terminal=['CLOSED']

# 4) 三容器 + 四个 topic
docker compose -f deploy/compose.yaml ps
docker exec -it eoh-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
# 期望：三行 healthy；topic 恰好 4 个
```

**下一步**（第 187 天）：第 2 周第 2 步 · 下单链路与 outbox 的第一次真实写入（`EOC`）——幂等键校验、状态机守卫、订单/明细/outbox 三表同事务、投递器用 `FOR UPDATE SKIP LOCKED`。

## 十、第 186 天交付（第 2 周第 1 步 · 环境与工程骨架）

- 新建 [环境与工程骨架](Bootstrap/index.md)（判据 `EEN-A` ~ `EEN-H`），配图 `eoh-bootstrap.svg`（四层依赖 + 六步就绪）。
- **四层目录与依赖方向落成 3 条 ArchUnit 断言**：`domain` 不依赖 `org.springframework`/`jakarta.persistence`/`java.sql`；`api` 不碰 `infra`；`infra.persistence` 与 `infra.messaging` 互不依赖。写不进 CI 的架构规则等于没有。
- **启动六步定序**：TCP 可查询 → Flyway → 连接池 → 缓存/消息 → 消费组分区分配 → 就绪探针。每一步都写了「提前了会怎样」，其中 `5 → 6` 的提前是**假就绪**：订阅没完成就 UP，灰度期看起来正常但不消费。
- **实测把 `healthcheck` 的写法钉死**：PostgreSQL 18 容器从 `docker run` 到 **TCP 可查询 1.57~2.01 s**，期间连接是 `Connection refused`；`pg_isready` 返回 0 比 TCP 可查询**早约 312 ms**（1,697 ms 对 2,009 ms）——所以健康检查必须是「真的查一次」，不能用端口存活或 `pg_isready`。
- **池预算落进配置并故意留了一处错**：`maximumPoolSize=20`、2 实例 → 40 ≤ 80 ✅；但示例里 `leak-detection-threshold: 10000` 大于 `connection-timeout: 3000`，池会先抛「借不到」，泄漏检测永远抓不到（本周专题判据 `CPK-B`）。页内明确写出「这段是故意的，别照抄」，并给了两种正确组合。
- **五条验收断言**：四服务 `healthy`、`/actuator/health` 组件齐全、Flyway 最新一条 `success=t`、库侧连接数 20±2、下单后 outbox 有 1 行且 order/stock 都已写。

**如何验证**（读者可执行）：

```shell
# 1) 一条命令起全栈，退出码即「是否真的就绪」
docker compose -f deploy/compose.yaml up -d --build --wait
docker compose -f deploy/compose.yaml ps --format '{{.Name}} {{.Health}}'
# 期望：四个服务全部 healthy

# 2) 健康聚合与池
curl -s localhost:8080/actuator/health | jq '.status, (.components|keys)'
docker exec eoh-postgres psql -U postgres -d eoh -tAc \
  "select count(*) from pg_stat_activity where application_name='eoh-app';"
# 期望：UP / ["db","kafka","redis"]；连接数 20 ± 2

# 3) 下单写出 outbox
curl -s -X POST localhost:8080/api/v1/orders -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: boot-0001' \
  -d '{"customerId":"c-1","items":[{"skuId":"sku-1","qty":2,"unitPrice":"19.90"}]}' | jq '.status'
docker exec eoh-postgres psql -U postgres -d eoh -tAc \
  "select event_type,status from outbox order by id desc limit 1;"
# 期望：CREATED / OrderCreated|PENDING
```

## 十一、第 187 天交付（第 2 周第 2 步 · 下单链路与 outbox 首次写入）

- 新建 [下单链路与 outbox 首次写入](OrderFlow/index.md)（判据 `EOR-A` ~ `EOR-H`），配图 `eoh-orderflow.svg`（事务边界 + 投递器 + 两条红线）。
- **五步顺序与回滚点定死**：幂等键 → 商品快照 → 订单头/行 → 库存条件扣减 → outbox；幂等键必须最前（否则重复请求会先占库存），outbox 必须同事务最后（否则「订单成功事件丢了」）。
- **库存预占写成条件 `UPDATE` + `RETURNING`**：`WHERE available - reserved >= :qty`，影响 0 行即库存不足。写 `available >= :qty` 会漏掉已预占量，只在并发预占时暴露——这类 bug 测试环境几乎复现不出来。
- **outbox 表结构定稿**：`event_id` 唯一、`aggregate_id` 作 Kafka 分区键、`published_at IS NULL` 部分索引。投递器取件用 `FOR UPDATE SKIP LOCKED`，沿用第 183 天的实测结论（去掉后两路各 500 条、重复 500 条）。
- **六条验收断言**：四处计数同增、库存不足四处全零、幂等重投不增、**停掉 Kafka 下单仍成功**、恢复后 30 秒内 `published_at` 全部非空、同事件投两次读模型只 +1。

**如何验证**（读者可执行）：

```shell
# 1) Kafka 停掉，下单仍应成功（业务不被中间件绑架）
docker compose -f deploy/compose.yaml stop kafka
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8080/api/v1/orders \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: eor-0001' \
  -d '{"customerId":"c-1","items":[{"skuId":"sku-1","qty":2,"unitPrice":"19.90"}]}'
# 期望：201

# 2) 四处计数：正常下单应为 1 / n / 1 / 1
docker exec eoh-postgres psql -U postgres -d eoh -U postgres -c \
  "select (select count(*) from orders where order_no='$NO') o,
          (select count(*) from order_items where order_no='$NO') i,
          (select count(*) from stock_reservation where order_no='$NO') r,
          (select count(*) from outbox where aggregate_id=(select id from orders where order_no='$NO')) ob;"

# 3) 恢复 Kafka 与投递器，30 秒内 outbox 应清空
docker compose -f deploy/compose.yaml start kafka && docker compose -f deploy/compose.yaml up -d worker
sleep 10
docker exec eoh-postgres psql -U postgres -d eoh -tAc \
  "select count(*) from outbox where published_at is null;"
# 期望：0
```

## 十二、第 188 天交付（第 2 周第 3 步 · 支付回调）

- 新建 [支付回调：验签、幂等与对账](PaymentCallback/index.md)（判据 `EPY-A` ~ `EPY-H`），配图 `eoh-payment.svg`（五步链路 + 三条不变量 + 三个必失点）。
- **五步顺序定死**：收单落 `raw_body` → 验签 → 幂等 → CAS 守卫 → 同事务落 `outbox`。两个「不能换」：落 raw 必须在验签之前（否则伪造攻击无从分析），CAS 必须在 outbox 之前（否则事件会先于订单状态可见）。
- **唯一键是 `(channel, channel_txn_no, callback_type)`**：用订单号做幂等键会把「同一单第二次支付」当重复吞掉；不含 `callback_type` 会把退款回调当重复。
- **对账分两个方向**：渠道有我方无（漏单，最高优先级）与 我方有渠道无（假支付，禁止自动回退）。漏单查询留 2 分钟窗口，判据是「假阳性为 0」。
- **五条验收**：伪造签名、重复回调 ×5、乱序（`refund` 早于 `pay`）、金额不符、人为制造漏单。其中签名相关的两条需要 mock 渠道私钥，页面明确标注「前置条件未满足，未跑」。
- **下一步**：第 2 周第 4 步「库存预占的释放与超时回滚」（判据族 `EPR`）——超时释放与支付回调会同时推进同一张单，竞态仍是 CAS，但要处理「跨上下文双向竞争」；容量面要验证 1 万笔同时释放时的行锁等待，按 `id` 排序可显著降死锁率。

## 十三、第 189 天交付（第 2 周第 4 步 · 库存预占的释放与超时回滚）

- 新建 [库存预占的释放与超时回滚](StockRelease/index.md)（判据 `EIV-A` ~ `EIV-H`），配图 `eoh-stock-release.svg`（三态迁移 + 双向竞态 + 扫描纪律）。
- **前缀按总览收口**：第 188 天「下一步」写的 `EPR` 是临时名，总览第 1 周预留的是 `EIV`，本页统一为 `EIV`，全库不撞号。
- **三态且终态不可逆**：`HELD → CONSUMED`（支付成功）与 `HELD → RELEASED`（超时）都是 CAS；`CHECK` 约束写在库层，不靠应用层「约定」。
- **扫描三要素**：`(status, expires_at, id)` 部分索引只覆盖 `HELD`、`ORDER BY id` 统一加锁顺序、`FOR UPDATE SKIP LOCKED` 让多实例互不阻塞；**宽限期 30 秒**给在途回调留窗。
- **两支竞态不对称**：释放输了可以静默（它不该赢），支付输了**不能静默**（钱已收、库存已放），必须进退款/补货队列——这是本步最容易写错的一处。
- **回补同事务**：改状态与 `available + qty` 放在同一条 CTE 里；先回补后改状态会让「已支付却被释放」的单把同一份货卖两次。
- **容量不写未跑的读数**：1 万笔同时释放的压测留到第 3 周（`ECP`），本页只给三个读数口径（锁等待会话数、`deadlocks` 增量、剩余 `HELD`）与期望值。
- **下一步**：第 3 周进入「联调与一致性用例矩阵」（判据族 `ECM`）；已登记三个缺口——退款（`CONSUMED → REFUNDED` 与第二次回补）、积压自愈（I2 只报不修）、跨上下文乱序（已释放却收到支付成功）。

## 十四、第 190 天交付（第 3 周第 1 步 · 一致性用例矩阵）

- 新建 [一致性用例矩阵](ConsistencyMatrix/index.md)（判据 `ECM-A` ~ `ECM-H`），配图 `eoh-consistency-matrix.svg`（四维组织 + 覆盖率 + 并发对照）。
- **18 条用例、18/18 PASS，迁移覆盖 11/16 = 68.8%**：覆盖率的算法是「16 条状态迁移左连接 covered 表」，不是人工数——这样新增迁移时缺口会自动浮现。
- **矩阵的四维是「场景 × 动作 × 断言 × 观测点」**：只断言「接口返回 200」等于没断言，因为 200 的语义可能是幂等命中，也可能是重复插入被忽略。每条用例的 `expect` 必须是 `n=1`、`0 行`、`payment=1` 这类可判定值。
- **并发两条对照（本机实测）**：CAS 版本后到者等锁 **1,210 ms** 后 `UPDATE 0`；无守卫版本等锁 **1,188 ms** 后 `UPDATE 1`，终态被后来的取消覆盖，**两边都不报错**。
- **未覆盖的 5 条边全是售后**（退款链路缺失），矩阵里显式标注「原因 + 归属步骤」，不用 `skip` 藏——写一条必然失败的用例只会让矩阵红灯常亮，然后被所有人忽略。

**如何验证**（读者可执行）：

```shell
# 1) 18 条用例逐条跑（每条一个事务，末尾 truncate）
docker exec -i eoh-pg psql -U postgres -d eoh -f 930_matrix.sql
# 期望：18 行，result 全 PASS

# 2) 覆盖率
docker exec -i eoh-pg psql -U postgres -d eoh -c \
  "select count(*) filter (where covered) as covered, count(*) as total from covered;"
# 期望：covered=11 total=16

# 3) 并发对照（两个终端）
#    A: begin; update o set status='PAID' where id=10 and status='AWAITING_PAYMENT'; select pg_sleep(2); commit;
#    B: 0.5 秒后执行同一句
#    期望：B 等锁约 1.2 秒，UPDATE 0
```

**下一步**（第 191 天）：第 3 周第 2 步「并发与幂等专项」（`ECC`）——补退款链路（矩阵 5 条未覆盖边的前置），并把「支付 vs 释放」「4 消费者 outbox」「重复退款」三组竞态跑出读数。

## 十五、第 191 天交付（第 3 周第 2 步 · 并发与幂等专项）

- 新建 [并发与幂等专项](ConcurrencyIdempotency/index.md)（判据 `ECC-A` ~ `ECC-H`），配图 `eoh-concurrency.svg`（三组竞态 + 两道守卫）。
- **补上退款链路**：`CONSUMED → REFUNDED`（迁移 16 → 17）与第二次库存回补；幂等键落在库层 `refund(order_no unique)`，不靠应用约定。
- **三组竞态实测**（PostgreSQL 18 容器、真实多会话）：
  - ① 支付 vs 超时释放：S1 `UPDATE 1` 持锁 2 s，S2 **阻塞 1.85 s** 后 `UPDATE 0`；终态 `CONSUMED`、`reserved=10`、`available=90`。若释放分支不看影响行数，`available` 会变成 **92**——超卖 2。
  - ② outbox 四消费者：`SKIP LOCKED` 下 500×4 = **2,000 条、重复 0、0.20 s**；去掉 skip 用固定区间，同样 2,000 条但 distinct 只有 **500，重复 1,500（75%）**。
  - ③ 重复退款：唯一键 + CAS 下后者等 **0.12 s** 后 `UPDATE 0`，`reserved` 10 → **8**（只回补一次），`refund` 仅 1 行；拆掉守卫的读后写反例里 `reserved` 变成 **6**——同一份货补了两次。
- **孤儿支付必须入队**：已 `RELEASED` 再收到支付成功时 CAS 必然 `UPDATE 0`，此时只 `log.warn` 就返回 200 会导致「钱收了、货没发、监控无感」，必须写 `orphan_payment`。
- **幂等三层模型**：请求层（`Idempotency-Key`）、事件层（`event_id` 唯一）、状态层（CAS）。第三层只保证「只有一个赢家」，**不保证赢的那个是对的**——「谁该赢」是业务规则（支付优先于超时释放）。

**如何验证**（读者可执行）：

```shell
# 1) 三张表 + 退款表
docker exec -i eoh-pg psql -U postgres -d eoh -f 020_reservation_refund.sql

# 2) 支付 vs 释放：两个会话按第二节时序执行
docker exec -i eoh-pg psql -U postgres -d eoh -c \
  "select status from stock_reservation where order_no='o-1';"
# 期望：CONSUMED；且 stock.reserved 未变

# 3) 四路 SKIP LOCKED：4 个终端同时执行 sql/claim-batch.sql
docker exec -i eoh-pg psql -U postgres -d eoh -c \
  "select count(*) filter (where published_at is not null) pub, count(*) total from outbox;"
# 期望：2000 / 2000，且四个终端的 id 集合两两无交集

# 4) 重复退款：两个终端同时执行同一退款 CTE
docker exec -i eoh-pg psql -U postgres -d eoh -c \
  "select reserved from stock where sku='sku-1'; select count(*) from refund;"
# 期望：reserved 只减一次；refund=1

# 5) 不变量 A1~A10
docker exec -i eoh-pg psql -U postgres -d eoh -f 900_invariants.sql
# 期望：全部 0 行
```

**下一步**（第 192 天）：第 3 周第 3 步「压测与容量」（`ECP`）——本节量到的「释放扫描 1.85 s 锁等待」「4 路取件 0.20 s」正好是压测模型的输入；要给出 1 万笔同时释放的 `pg_locks` 等待会话数、`deadlocks` 增量与 outbox 积压拐点。

## 十六、第 192 天交付（第 3 周第 3 步 · 压测与容量）

- 新建 [压测与容量](CapacityTest/index.md)（判据 `ECP-A` ~ `ECP-H`），配图 `eoh-capacity.svg`（吞吐随并发下降 + 尾延迟 + outbox 排空三块）。
- **三个数取代一个 TPS**：吞吐 / 尾延迟 / 积压排空。四档并发（4/8/16/32）读数 `7,734 → 7,123 → 6,550 → 5,921`，并发翻 8 倍吞吐 **-23.4%**。
- **p99 骗人**：p50 = 0.10 ms、p99 = 0.38 ms 全程不动，但 max 到 **5,097 ms**——p99 统计的是没排队的那些请求（p99 与 max 相差 13,000 倍）。
- **零错误是配置假象**：`timeout=10s` 大于 5 秒压测窗口，所以永远等不到 `database is locked`；把超时调到 0.5 s 才是过载的真实形态（`ECP-E`）。
- **outbox 加消费者不变快**：1 个 24.0 ms / 2 个 27.0 ms（-12.5%），原因是单写者抢同一把锁；解法是按 id 取模分片而不是加消费者。
- **不许半成功**：压测后 `orders = 136,639`、`outbox = 136,639`、`order_items = 273,278`（正好 2 倍），三个数自洽（`ECP-F`）。
- **容量算式带安全系数**：5,921 × 0.3 ≈ 1,776 TPS/实例，50 TPS 目标只需 1 个实例；三处「以为的瓶颈」与算式结论不一致，下一步应查尾延迟而不是加资源（`ECP-G`）。
- **口径边界写在页首**：压测台跑在 SQLite 单写者上（读者零依赖可复跑），**形态可迁移、绝对值不可迁移**，7,734 TPS 不能当生产容量。

**下一步**（第 195 天）：第 3 周第 4 步「第 3 周验收」（`EW3`）——把一致性矩阵 18 条、并发专项 3 组、压测 8 条合成一张验收表，并补「批量化实验」（1 事务 10 单）作为 `ECP-H` 第 4 步的读数。

## 十七、第 195 天交付（第 3 周第 4 步 · 第 3 周验收）

- 新建 [第 3 周验收](Week3Gate/index.md)（判据 `EW3-A` ~ `EW3-H`），配图 `eoh-week3-gate.svg`（三份证据 → 合成表 → 七道门）。
- **29 条结论按层级排，不按来源排**：L1 正确性（矩阵 18 条）→ L2 并发性（3 组竞态）→ L3 承载性（压测 8 条）。L1 不通过就不看 L2、L3——验收要能**在最早的地方停下**。
- **批量化读数（补 `ECP-H` 第 4 步）**：2,000 单四档，1 / 10 / 100 / 500 单每事务 → **11,291 / 51,163 / 101,567 / 101,024 单每秒**。10 单/事务就是 **4.5 倍**，100 单到 **9 倍**后饱和；均摊 0.089 → 0.010 ms/单。
- **但批量化误伤放大 50 倍**：1,000 单里只有 10 个坏单（1% 重复键），批量 100 下 **5 个批次全回滚，丢掉 500 个好单**。结论：收益成立，但**只用于 outbox 投递这类重复无害的路径**，主写路径必须先把坏单挑出去、失败二分重试。
- **「零错误」被证明是配置假象**：`timeout=10s` 大于 5 秒压测窗口，所以永远等不到 `database is locked`；调到 0.5 s 后错误立刻出现（`EW3-E`）。判据：**零错误必须先证明错误通道是通的**。
- **四条负向复验全部仍然失败**：重复支付回调、已释放后支付成功、重复退款、超卖写入。这条比正向用例更重要——它验证的是「本周改动没有把上周的守卫改回去」。
- **结论分「通过」与「有条件通过」**：承载性写的是「1,776 TPS（含 0.3 安全系数）够 50 TPS 目标」，目标一变就要重算；覆盖度写「16 条迁移覆盖 11 条」，退款分支留给第 4 周。
- **三条遗留缺口都写成「下一步的第一步」**：退款与部分退款、outbox 死信重投、主写路径批量化评估。

**下一步**（第 194 天）：第 4 周第 1 步「一键部署与配置」（`EDP`）——先用 `docker compose` 起三容器（PG 18 / Kafka 4.2 / Redis 8），把第 2 周 `Bootstrap` 定的四个服务串起来；验收是四个服务 `healthy` + `/actuator/health` UP + 一条下单能写出 outbox。同时把本节登记的三条缺口写进第 4 周施工顺序。

## 十八、第 196 天交付（第 4 周第 1 步 · 一键部署与配置）

- 新建 [第 4 周第 1 步 · 一键部署与配置](DeployCompose/index.md)（判据 `EDP-A` ~ `EDP-H`），配图 `eoh-deploy-compose.svg`（三容器 → `--wait` → 四服务 → 一条下单 → 三条负向）。
- **本步不改业务代码，只把「怎么跑起来」从开发态推到可交付态**：dev 与 deploy 只差三处（profile / 卷 / 密钥来源），其余一行不动——差异越小，越不容易「本地好、线上不行」。
- **三个刻意的部署选择**：`ADVERTISED_LISTENERS` 用容器名（写 `localhost` 会「连上了但拉不到分区」）；`AUTO_CREATE_TOPICS_ENABLE=false`（开着会把 topic 拼错变成「静默空 topic」，而 `health` 还是 UP）；`POSTGRES_PASSWORD_FILE` + `secrets`（环境变量会出现在 `docker inspect` 与 `/proc/<pid>/environ`）。
- **探针分三层**：`liveness` 只看进程、`readiness` 含 `db,kafka,redis,flyway`、`startup` 给首次启动宽限。`--wait` 只等容器健康，**不等应用 readiness**，所以部署脚本第 4 步必须自己 `curl` 轮询。
- **最值钱的一条负向验收**：停掉 Kafka 再下单**仍然 201**，`outbox` 留 1 行 `PENDING`，恢复后 30 s 内清空——一次同时证明「业务不被中间件绑架」与「outbox 真的在同一个事务里」。
- **`deploy.resources` 在非 Swarm 下会被静默忽略**：本项目改为在 README 写内存预算表（PG 512 MB + Kafka 1 GB + Redis 128 MB + 4×JVM 512 MB ≈ 3.7 GB），预算表比一个不起作用的 `limits` 有用。
- **备份必须演练**：`pg_dump -Fc` 成功不等于能 `pg_restore`；恢复目标固定为临时库 `eoh_restore`，不动生产库。
- 九项自检收敛成 `doctor.sh`（`compose config` / 三容器健康 / 版本一致 / liveness / readiness / env 无口令 / outbox 可读 / 具名卷存在 / **内存上限已落地**），任何一行 FAIL 都指向「失败模式速查」表的一行；最后一项查的是「写的东西算不算数」，前八项只查「服务在不在」。

**下一步**（第 197 天）：第 4 周第 2 步「监控与告警」（`EMO`）——把九项自检变成持续采集的指标（容器健康、readiness 翻转次数、outbox 积压深度、下单 p99、清空耗时），各配阈值；三条遗留缺口按「能被监控证明」的顺序排。

## 十九、第 197 天交付（第 4 周第 2 步 · 监控与告警）

- 新建 [第 4 周第 2 步 · 监控与告警](Monitoring/index.md)（判据 `EMT-A` ~ `EMT-H`），配图 `eoh-monitoring.svg`（九项自检 → 五个指标 → 三条告警）。
- **本步不改代码，只把「一次性自检」改造成「持续信号」**：自检回答「现在对不对」，指标回答「什么时候开始不对、不对了多久、是不是刚变严重」。前者只在有人跑的时候存在，后者才叫监控。
- **五个指标各有分母**：容器健康、readiness 翻转次数、outbox 积压行数、下单 p99、outbox 清空耗时。积压**用行数不用延迟**——投递延迟的中位数永远很小，只有行数能反映「进得比出得快」。
- **p99 与均值差 2.9 倍**（合成序列 86.4 万单，固定种子 20261023）：均值 45.0 ms、p50 42.1、p95 60.3、p99 128.9、p99.9 443.9。用均值做告警，只有事故大到能拉动均值时才响。
- **阈值靠双序列校准，不靠拍**：400 ms + 连续 1 min → 7 天误报 **23** 次；400 ms + 5 min → 0 次；劣化 1.6 倍时 **500 ms + 5 min 报 3 次**、600 ms 报 **0 次**（漏报）。结论：阈值必须与「持续时间」一起定，且要拿劣化序列跑一遍。
- **积压差额 5/s，延迟看不出来**：生产 100/s、消费 95/s，60 分钟积压 **18,000** 行，同期单条 p99 几乎不变（约 128 ms）；停产后清空需 **189.5 s**——这个数决定「重启投递器」是否可接受。
- **燃烧率双档**：SLO 99.9% → 每月预算 **43.2 min**，1 小时窗口燃烧率 14.4 = 2 天烧完，配 6（1 周）与 1（刚好用完）两档；只配快烧会让慢烧把预算悄悄烧完。
- **验证边界按纪律标死**：本仓无 Java 工程代码，凡需 `eoh-app` 在跑的验收（①~④）全标 **⏳ 未跑**并注明原因；阈值校准、积压算式、燃烧率换算、分位数复现四条（⑤~⑧）为本机已跑读数。**能验证的写实测，不能验证的写期望值，两列不混。**

**下一步**（第 198 天）：第 4 周第 3 步「发布与回滚」（`ERB`）——先把本章三条告警接到发布脚本的自动中止条件（p99 超阈 5 分钟即回滚），再补金丝雀与回滚判据；三条遗留缺口按「能被监控证明」排序，死信重投优先（它的证据正是「积压只增不减」）。

## 二十、第 198 天交付（第 4 周第 3 步 · 发布与回滚）

- 新建 [第 4 周第 3 步 · 发布与回滚](ReleaseRollback/index.md)（判据 `ERB-A` ~ `ERB-H`），配图 `eoh-release-rollback.svg`（五阶段 → 四条出口 → 中止 → 回滚四步）。
- **本步不改业务代码，只把「发一次版」从人工操作改成状态机**：P0 preflight → P1 金丝雀（不接流）→ P2 5% → P3 50%/100% → P4 收尾，每档都有出口条件与超时；「中止」与「回滚」拆成两个动作（P0/P1 只需不继续，P2 之后才真回滚）。
- **先定「什么不能回」再谈回滚**：六类变更里有两类不可回滚——减法迁移（`DROP COLUMN` / 改类型）与外部副作用（已发通知、已扣库存）。判据是机械的：迁移里扫到这几类语句就在 P0 阻断，强制走两阶段（本版只 expand）。
- **最值钱的实测：绝对阈值抓不到劣化**。用第 197 天同一套口径（种子 20261023，p99 128.9 ms）注入 1.6 倍劣化（→206.2 ms）：500 ms 绝对阈值在 5 min 窗口 **检出 0/200**，相对判据（基线 × 1.3）**159/200**。所以金丝雀判据必须与自己的基线比。
- **但相对判据有代价：小样本上 p99 极不稳定**。同一份正常数据的 p99 估计 90% 区间：1 min（300 样本）宽 147.5%、5 min（1,500 样本）宽 65.8%、10 min 宽 42.4%。+30% 门限在 5 min 窗口的假阳性 **16.5%**，收到 +50% 后降到 **6.5%**——本项目采用 ×1.5，并加「连续两档都超才中止」。
- **金丝雀比例与样本量是同一件事**：100 rps 下 1% 比例要 **25 min** 才攒到 1,500 样本（观察窗比回滚预算还长），5% 只要 **5 min**。这就是很多团队「金丝雀开了但从不报警」的真实原因。
- **回滚的时间账**：快路径（告警直接中止）5 + 1 + 2 + 1 = **9 min**，烧掉月度预算（43.2 min）的 **20.8%**；慢路径（人工确认）21 min，烧掉 **48.6%**——一次人工回滚几乎吃掉半个月预算，所以发布期自动中止不是炫技。
- **回滚要有验证而不是「以为」**：切权重回 0 之后，唯一可靠的证据是 **outbox 积压回落**（300 s 内降到起始值 10%）；契约类变更的回滚顺序是**先回消费侧**，与升级顺序相反。

**下一步**（第 199 天）：第 4 周第 4 步「对账日报与交接」（`ELA`）——把发布记录升级成对账日报的数据源（订单状态 / 支付流水 / 库存预占三向差集）；三条遗留缺口按「能被监控证明」排序，死信重投优先；runbook 要能让凌晨三点被叫起来的人照着做完。

## 二十一、判据纪律

每章 8 条，编号形如 `EOH-A`，逐章前缀唯一（`EOH` / `ETS` / `EOA` / `EDB` / `EEN` / `EW1` / `EOR` / `EPY` / `EIV` / `ESF` / `ERC` / `EW2` / `ECM` / `ECC` / `ECP` / `EW3` / `EDP` / `EMT` / `ERB` / `ELA` / `EW4`），全库不撞号。判据只有三种形态：**可复跑的读数**、**可勾选的检查项**、**可对照的结构**（表/图/契约）。
