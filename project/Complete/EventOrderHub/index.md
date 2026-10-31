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
| [第 4 周第 4 步 · 对账日报与交接](ReconciliationHandover/index.md) | `ELA` | 三向差集、六类差异归口、增量+周全量、runbook 与交接验收 | 8 |
| [第 4 周第 5 步 · 上线验收](LaunchAcceptance/index.md) | `EW4` | 三层判定、21 条验收项、六道闸门、红线与黄线、回滚预算占比 | 8 |
| [第 3 周第 5 步 · 发货与签收](ShipmentFulfillment/index.md) | `ESF` | 发货单五态、运单号唯一、回调幂等/乱序/不来、订单完成聚合判定 | 8 |
| [第 4 周补充 · 退款与部分退款](Refund/index.md) | `ERC` | 额度条件更新、幂等键、回执三通道、库存回补、退满判定成本 | 8 |
| [第 2 周第 5 步 · outbox 死信与重投](OutboxDeadLetter/index.md) | `EDL` | 错误分流、退避与判死、洞的显式登记、守卫与幂等、重投窗口 | 8 |
| [第 4 周补充 · 主写路径的受限批量化](BatchWrite/index.md) | `EWB` | 写分三类、失败放大算术、预检隔离与兜底、批大小依据、三档灰度 | 8 |
| [第 2 周第 6 步 · 第 2 周验收](Week2Gate/index.md) | `EW2` | 五步合成六项、跨步三条断言、三道门、保留期成本读数 | 8 |
| [第 4 周补充 · 交易通知的触达闭环](NotifyFulfillment/index.md) | `ENT` | 三表拆分、事件映射、决策五步、两个幂等键、降级不双发、N1~N8 验收 | 8 |
| [第 4 周补充 · 订单完成后的开票闭环](Invoicing/index.md) | `EIN` | 可开票判定、按行拆票与逐行算税、一单一票、退款红冲守恒、三向逐行对账 | 8 |
| [第 4 周补充 · 库存盘点的批量导入与对账导出](BulkHandover/index.md) | `EBD` | 调整流水、预占保护、内容哈希幂等、事务粒度、快照导出、N1~N8 | 8 |
| [第 4 周补充 · 售后工单受理与 SLA 时钟](SupportSLA/index.md) | `ESA` | 售后入口归并、工单挂订单、两个时钟口径、重开窗口、N1~N8 | 8 |
| [第 4 周补充 · 订单检索与导出：游标、索引与快照](OrderQuery/index.md) | `EOQ` | 游标分页、索引列序、总数三模式、快照导出与自校验、N1~N8 | 8 |
| 第 4 周补充 · 退款协议签署与存证举证 ⚠️ **章节页待补** | — | 阈内判定、签署阻塞退款、摘要一致、时间戳与证据包、N1~N8（判据族原定 `ERA`，随章节页一起待补） | 8 |
| 第 4 周补充（同日第二班）· 运营后台的权限与 PII 边界 ⚠️ **章节页待补** | — | 动作×资源×字段三元组、默认拒绝、列级投影、用途限定、导出上限、N1~N8（判据族原定 `EAC`，随章节页一起待补） | 8 |
| [第 4 周补充 · 上线产物的可复现与构建缓存治理](ReproducibleBuild/index.md) | `EBR` | 五个漂移来源、digest 与 tag 分离、缓存键三纪律、产物⇄manifest 两个目标 | 8 |

**29 章已落地页，2 章登记欠账**（章节页缺失、交付记录在本页第 32、33 节），无占位章节。

> **台账⇄实物对账（第 220 天补记，命令可复算）**：
> `ls -d project/Complete/EventOrderHub/*/ | grep -v assets | wc -l` → **29**；本表行数 **31**。
> 差额 **2** 就是上两行：`RefundAgreement/` 与 `OperationAccess/` 两个目录**在全部历史与全部分支中都不存在**（`git log --all -- project/Complete/EventOrderHub/RefundAgreement` 输出为空），但本表与交付记录把它们的读数写得很详细——**台账先于实物生成**，是这个仓库反复出现的一类缺陷（第 202 天 `linkexistcheck` 立的案由与此同源）。
> 处置：**不造页、只登记**。理由是本仓纪律「宁可少一章，不做双份」——这两章的正文若由第二批人凭台账里的读数补写，写出来的是**没跑过那批实验的人复述别人的读数**，比缺页更不可信。缺页登记在这里，等有实物的人补。



> **章节数口径（第 220 天以命令复算，不再凭记忆累加）**：以实数可复算为准——
> `ls -d project/Complete/EventOrderHub/*/ | grep -v assets | wc -l` → **29**；`git ls-tree -d --name-only HEAD project/Complete/EventOrderHub/ | grep -v assets | wc -l` → **27**（上一版提交时的实数），差额 **2** 正是本页已列出、但当次未提交的两章：订单检索、可复现构建。
> **三个已犯过的计数错误，写在这里防第四次**：① 上一版把「新增 2 章」当成「总数 29」——**增量不是总数**；② 更早一版文字写 28、实际目录只有 27——**页面上的数字必须由命令产出**，不能由「上一版 + 1」推出来；③ 第 210 天那版写「30 章全部交付」，而当时实际目录只有 **28** 个（`RefundAgreement` / `OperationAccess` 从未存在）——**「全部交付」这种话必须先跑一遍目录计数再说**。
> **两次同日交付的处理**：两章互不重叠（一章管「钱怎么被证明」，一章管「谁能看这笔钱」），章节号按落地顺序排，不合并、不互相覆盖。

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

## 二十一、第 199 天交付（第 4 周第 4 步 · 对账日报与交接）

- 新建 [第 4 周第 4 步 · 对账日报与交接](ReconciliationHandover/index.md)（判据 `ELA-A` ~ `ELA-H`），配图 `eoh-reconcile.svg`（三向 → 六类 → 增量/全量 → 两次收敛）。
- **本步不改业务代码，只把「系统现在对不对」变成每天早上七点自动生成的一页纸**：三向差集（订单状态 × 支付流水 × 库存预占）、六类归口、每类一个人名。
- **六类差异与判据 SQL 定死**：D1 漏单 / D2 假支付 / D3 金额不符 / D4 预占缺失 / D5 预占悬挂 / D6 数量不符，每条一个 `CTE`，可单独跑。
- **三条「不算差异」的口径写在 `::: danger` 里**：未付订单无流水不是漏单（否则日报第一天 13 万条，第二天就没人看）、取消订单无预占是正常路径、渠道 T+1 迟到要留宽限窗。
- **本机实测（PG 18.6，20 万单 / 66,663 流水 / 199,993 预占，注入 36 条已知差异）**：六类逐条对上注入值（12 / 9 / 5 / 7 / 0 / 3，合计 36），说明判据本身是准的。
- **增量 vs 全量的真实差别不在总耗时而在单行成本**：昨日窗口 **17.0 ms / 6,666 单（2.56 µs/行）**，全量 30 天 **42.5 ms / 200,000 单（0.21 µs/行）**——差 **12 倍**。结论：增量只发现新差异，全量才能抓出陈年悬挂，两者都要跑。
- **日报落库幂等**：`reconcile_diff` 唯一键 `(biz_date, kind, order_no)`，重跑不翻倍；`state` 四态，`IGNORED` 必须填 `detail.reason`，关闭必须带 `evidence`。
- **runbook 写成「症状 → 一条命令 → 判定阈值 → 下一步」**：五条症状各自给阈值（`D1 > 50` 持续 10 分钟、积压 > 1,000 等），不写「如果异常请联系相关同事」。
- **交接验收是「对方做、你看」**：五个动作由接手人独立执行，其中「自己造一条差异让日报抓到」最关键——能造出差异，说明他理解了六类的口径。

**如何验证**（读者可执行）：

```shell
# 1) 三向源表 + 差异表就位
docker exec -i eoh-pg psql -U postgres -d eoh -f sql/050_reconcile_diff.sql
# 期望：CREATE TABLE / CREATE INDEX

# 2) 六类差异逐类对账（注入 36 条，应报出 36 条）
docker exec -i eoh-pg psql -U postgres -d eoh -f sql/reconcile-daily.sql
# 期望：D1=12 D2=9 D3=5 D4=7 D5=0 D6=3

# 3) 增量耗时（单日 6,666 单）
docker exec -i eoh-pg psql -U postgres -d eoh -c \
  "explain (analyze, costs off) select count(*) from orders o
     where o.status in ('PAID','ALLOCATED','SHIPPED','COMPLETED')
       and o.created_at >= now() - interval '1 day'
       and not exists (select 1 from payment x where x.order_no = o.order_no);"
# 期望：Execution Time 约 17 ms

# 4) 重跑幂等（差异表不翻倍）
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
  "select count(*) from reconcile_diff where biz_date = current_date;"
# 期望：36（跑两次仍是 36）
```

**下一步**（第 200 天）：第 4 周第 5 步「四周验收与交接」（`EW4`）——把第 1~4 周的 12 份交付合成一张四周验收表（L1 正确性 / L2 并发性 / L3 承载性 / L4 可运维性），并补齐 `ESF` 发货签收与 `EW2` 第 2 周验收两处缺口。

## 二十二、第 200 天交付（第 4 周第 5 步 · 上线验收）

- 新建 [第 4 周第 5 步 · 上线验收](LaunchAcceptance/index.md)（判据 `EW4-A` ~ `EW4-H`），配图 `eoh-launch.svg`（三层判定 → 六道闸门 → 上线决策 → 两列状态）。
- **本步不写业务代码，只回答一个问题：明天早上能不能开**。答案由 **21 条验收项 + 六道闸门** 组成，闸门是 G1 一致 / G2 容量 / G3 监控 / G4 回滚 / G5 权限 / G6 交接。
- **三层判定不能颠倒**：L1 正确性（G1）→ L2 承载性（G2、G3）→ L3 可运维性（G4、G5、G6）。**L1 不过就不看 L2/L3**——一个会算错的系统，p99 再好也没意义。
- **状态只有三态**：已跑（本机可复现 9 条）/ 未跑（需 `eoh-app`，8 条标 ⏳）/ 人工（4 条）。**期望值不抄进实测列**，这是本项目从第 196 天起就守着的纪律。
- **负向验收比正向更重要**：G1 的第 3、4 条是「重复回调不重复入账」与「已释放后支付不超卖」——它们证明的不是「功能在」，而是「守卫还在」。第 4 周改过下单链路，最容易的回归就是把第 2 周的守卫改掉。
- **两个「假绿」写进 `::: danger`**：① 在空库上跑三向差集（当然是 0），必须在灌过 36 条已知差异并修完之后跑，并留下「36 → 0」的记录；② 只看 `total` 不看分项，D1 与 D2 可能互相抵消，也可能互相掩盖成 0。
- **红黄规则只有三条**：G1/G2 不过 = 红，无人可批；G3~G6 任一不过 = 黄，可有条件上线但必须写「补偿动作 + 7 天到期日」；全绿 = 排窗口。**不允许把红改成黄、把未跑写成已跑、用「上线后马上修」替代验收。**
- **回滚时间要进预算账**：快路径 9 min = 月度错误预算（43.2 min）的 **20.8%**，慢路径 21 min = **48.6%**——一个月最多承受两次慢路径回滚。这个数字必须写进发布单，否则「回滚」会被当成免费操作。
- **验收结论是「有条件上线」**：G1 绿、G2 黄（p99 待实测）、G3 黄（指标未接）、G4~G6 绿，两条黄各带补偿动作与 7 天到期。**一份全绿的验收表，通常是没认真验的表。**
- **项目收口**：周期 7 的 20 章至此构成一条链路（需求 → 选型 → 设计 → 编码 → 测试 → 部署 → 验收）。三项遗留缺口（退款与部分退款、outbox 死信重投、主写路径批量化）已登记在总览「下一步」，谁接手都能直接开始。

**如何验证**（读者可执行，不需要 `eoh-app`）：

```shell
# 1) 一致性快照：五类差异一次算完
docker exec -i eoh-pg psql -U postgres -d eoh -f sql/reconcile-daily.sql
# 期望：D1~D5 全 0，total = 0（造数并修完之后）

# 2) 不可回滚语句清单：本次变更集里应为空
grep -nE "DROP COLUMN|ALTER COLUMN .* TYPE|UPDATE [a-z_]+ SET [^;]*;" sql/*.sql \
  | grep -v "WHERE" || echo "0 条不可回滚语句"
# 期望：0 条不可回滚语句

# 3) 权限矩阵：应用账号跑 DDL 应被拒
docker exec -i eoh-pg psql -U eoh_app -d eoh -c "alter table orders add column x int;"
# 期望：ERROR: must be owner of table orders（或 permission denied）

# 4) 两列状态自查：验收表里「未跑」项必须带原因
grep -c "⏳" project/Complete/EventOrderHub/LaunchAcceptance/index.md
# 期望：≥ 8（每条未跑项都要有原因，不能只标 ⏳）
```

**下一步**（第 201 天）：补 `ESF` 发货与签收（发货单 / 签收 / 异常件）与 `ERC` 补偿动作两处缺口，并把 G2、G3 两条黄线的补偿动作在 7 天内结清；退款与部分退款需新增一条状态迁移，属下一个迭代的第一项。

## 二十三、第 201 天交付（第 3 周第 5 步 · 发货与签收）

- 新建 [第 3 周第 5 步 · 发货与签收](ShipmentFulfillment/index.md)（判据 `ESF-A` ~ `ESF-H`），配图 `eoh-shipment.svg`（五态状态机 + 三类回调异常）。
- **补的是主线的最后一截**：`payment.succeeded` 之后订单并不会自己完成，必须有「发货 → 签收」这一段。这一步之前，`SHIPPED` 与 `COMPLETED` 之间的迁移在文档里是悬空的。
- **两张表、一条拆单规则**：`shipment` 按**仓**拆（不按商品），唯一键 `(order_id, warehouse_id, seq)`；`tracking_no` 用**部分唯一索引**（`WHERE tracking_no IS NOT NULL`），否则「多个 NULL」的语义在库与库之间不一致。
- **回调日志的唯一键是三元组** `(tracking_no, event, occurred_at)`。只用运单号去重会把「先发车、后签收」的第二个事件吃掉——这是本步最容易写错的一行 DDL。
- **`SHIPPED` 只能内部触发**，回调只能推 `SHIPPED → DELIVERED/EXCEPTION`。否则伪造一条「已发货」回调就能跳过出库环节。
- **订单完成的聚合判定用 `EXISTS` + `NOT EXISTS` 两条**：少了前者，零发货单的订单（虚拟商品）会被判成「全部签收」；少了后者，任意一张签收就完成。**不要用「签收计数 = 明细总数」**——那是两个计数器必须严格同步，任何一处漏更新就永久偏。
- **三类回调异常各有写法**：重复（唯一键 + `ON CONFLICT DO NOTHING`，第二次影响 0 行是正常返回）、乱序（先落日志，再补 `SHIPPED`，再迁 `DELIVERED`；丢弃等于永久丢失）、不来（N 天无回调 → `EXCEPTION` + 人工，**绝不自动 `COMPLETED`**，那是资损）。
- **与超时关单互斥**：关单 SQL 补 `NOT EXISTS (shipment)`，防的是人工改单 / 数据修复造出的「未支付但有发货单」脏数据。
- **补偿方式是不改原单**：少件补发新建 `seq+1` 的发货单；原单是历史事实，改它等于篡改签收记录。

**如何验证**（读者可执行）：

```shell
# 1) 支付事件幂等：投两次只生成一张发货单
curl -s -X POST localhost:8080/internal/events/replay -d '{"topic":"payment.succeeded","order_id":3001}'
curl -s -X POST localhost:8080/internal/events/replay -d '{"topic":"payment.succeeded","order_id":3001}'
psql -U postgres -d eoh -Atc "select count(*) from shipment where order_id=3001;"
# 期望：1

# 2) 重复签收回调：发三次，日志只有一行
for i in 1 2 3; do curl -s -X POST localhost:8080/api/callback/carrier \
  -H 'Content-Type: application/json' \
  -d '{"tracking_no":"SF1000003001","event":"DELIVERED","occurred_at":"2026-10-24T10:00:00Z","signed_by":"本人"}' >/dev/null; done
psql -U postgres -d eoh -Atc "select count(*) from shipment_callback_log where tracking_no='SF1000003001';"
# 期望：1

# 3) 三条不变量（I1/I2/I3）一次跑完
psql -U postgres -d eoh -Atc "select count(*) from shipment where status='DELIVERED' and (tracking_no is null or delivered_at is null);"
psql -U postgres -d eoh -Atc "select count(*) from orders o where o.status='COMPLETED' and exists (select 1 from shipment s join shipment_item si on si.shipment_id=s.id where s.order_id=o.id and s.status not in ('CANCELED') and s.status<>'DELIVERED');"
psql -U postgres -d eoh -Atc "select count(*) from (select tracking_no from shipment where tracking_no is not null and status<>'CANCELED' group by 1 having count(*)>1) t;"
# 期望：0 / 0 / 0
```

**下一步**（第 202 天）：补 `ERC` 补偿动作（退款与部分退款、退货入库），并收拢 `EW2` 第 2 周验收；G2、G3 两条黄线的补偿动作仍在 7 天窗口内。

## 二十四、第 202 天交付（第 4 周补充 · 退款与部分退款）

- 新建 [第 4 周补充 · 退款与部分退款](Refund/index.md)（判据 `ERC-A` ~ `ERC-H`），配图 `eoh-refund.svg`（额度 → 幂等键 → 回执三通道 → 三条不变量）。
- **退款不是「把订单改成已退款」**，而是**在已付金额这个额度上做受控扣减**：额度是并发资源，退款单是幂等单元。这一句是本步的全部内容。
- **四张表**：`refund`（业务键 `SO{order}-R{batch}`）、`refund_item`（按明细分）、`refund_callback`（三元组唯一键）、`refund_ledger`（只追加，失败回滚记 `IN` 不删 `OUT`）。
- **七态状态机**，`MANUAL` 是终态；`FAILED` 重试必须换新批次号，`SUCCESS` 之后只能追加流水。
- **不超退靠一条带条件的 UPDATE**：实测无守卫的增量更新两次各退 60% 得到 **120.0%**（paid 188.13 / refunded 225.76）；带 `WHERE paid_amount - refunded_amount >= :amount` 时停在 **60.0%**，第二条 **UPDATE 0**。双会话并发同样只有一个成功（等锁后重判：40% < 60%）。
- **幂等键冲突的代价是「等」**：会话 A 持键 2 s，会话 B 同号插入阻塞 **2341 ms** 后报 `23505 duplicate key`。所以上游重试超时必须大于「对手事务最长持锁时间」——渠道 HTTP 调用绝不能在事务里。
- **回执三通道缺一不可**：同步受理（`PROCESSING`，不是成功）、异步回调（三态，唯一键去重）、30 分钟主动查询（只等回调 = 用户一直看到「退款中」）。
- **部分退款不改订单状态**：只有 I3（`refunded_amount = paid_amount`）成立才置 `REFUNDED`，否则订单保持 `COMPLETED`。否则客服与对账都会看到「退了一件却显示全额退款」。
- **库存回补带条件**：连续四次「回补 30」实测 `UPDATE 1/1/1/0`，`reserved` 从 100 到 10，**没有变负**；缺条件会写成 −20，凭空多出 20 件可售库存。
- **退满判定分冷热路径**（20 万单 / 1 万条成功退款）：聚合子查询缺索引 **144,281 ms** → 建部分索引 **923 ms** → 读维护列 **112 ms**。热路径读维护列，对账用聚合校验维护列，不一致即 D1 类差异。

**如何验证**（读者可执行）：

```shell
# 1) I1 不超退
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
"select count(*) from orders o join (select order_no,sum(amount) s from refund where status in ('SUCCESS','PROCESSING') group by 1) r on r.order_no=o.order_no where r.s > o.paid_amount;"
# 期望：0

# 2) I3 状态与金额一致
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
"select count(*) from orders where (status='REFUNDED') <> (refunded_amount >= paid_amount);"
# 期望：0

# 3) 幂等：同一 refund_no 提交两次，只有一行
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
"select count(*), sum(amount) from refund where refund_no='SO0000123-R2';"
# 期望：1 | 59.90

# 4) 退满判定耗时（应 < 200 ms）
docker exec -i eoh-pg psql -U postgres -d eoh -c "\timing on" -c \
"select count(*) from orders where status='COMPLETED' and refunded_amount >= paid_amount;"
# 期望：Time 约 110 ms
```

**下一步**（第 203 天）：三项遗留缺口还剩两项，下一轮取 **outbox 死信重投**（判据族 `EDL`）——死信产生条件、退避曲线、重投上限与人工接管、以及「重投会不会破坏顺序」；退款侧留一条待办：渠道 T+1 对账单与 `refund` 表的自动核对，等 `EDL` 落地后接进对账日报。

## 二十五、第 203 天交付（第 2 周第 5 步 · outbox 死信与重投）

- 新建 [第 2 周第 5 步 · outbox 死信与重投](OutboxDeadLetter/index.md)（判据 `EDL-A` ~ `EDL-H`），配图 `eoh-dlq.svg`（outbox → 投递器 → 死信/洞 → 三条处置路径）。
- **一句话结论**：死信的本质不是「一条消息没投出去」，而是**一个永远不会被应用的序号**；系统不能表达「这里有个已知的洞」，就会一直等一个不来的号。
- **四类原因、两种性质**：下游不可用 / 本端资源不足属**瞬时**（退避重试），消息非法 / 业务前置不满足属**永久**（第 1 次即判死）。判死靠**异常类型**，不靠「重试了几次」。
- **退避代价有数**：`base 5 s / factor 2`，重试 3/5/8 次分别白等 **35 s / 155 s / 1275 s（21.2 分钟）**。本项目取 **5 次 / 155 s**，并把抖动设为 `±20%` 防重试风暴。
- **三种处置实测（5 条事件、`seq=2` 是毒消息）**：A 死信照旧阻塞 → eA2 在 **635 s** 判死后 eA3/4/5 **永久 pending**（卡死在投递层）；B 死信跳过但守卫要求 `last_seq = seq-1` → eA3 重试 **73 次**仍被拒、到 1000 s 未交付（卡死在应用层）；C 判死同事务写 `applied_hole` 并让守卫认洞 → 635 s 时 eA3/4/5 **全部交付、每条 attempts=1**。
- **重投不重复副作用靠版本守卫**：`applied.last_seq` 已到 5 时重放 `seq=2`，带守卫 `UPDATE 0` 行、不带守卫 `UPDATE 1` 行（本项目 seq=2 是库存预占确认，多执行一次就是 `reserved` 多扣一次）。
- **去重是第二层**：同一 `event_id` 投 3 次 → **接受 / 跳过 / 跳过**（`consume_log` 主键兜底）。守卫管顺序，幂等键管重复。
- **重投窗口三条**：最早判死后 10 分钟、最晚事件产生后 24 小时、单条最多 3 次；超限转 `abandoned` 并留 `operator` 与原因。
- **监控四数**：`dead_letter_open` / `dead_letter_age_max` / `outbox_pending_age_max` / `replay_rejected_total`。方案 A 的死锁在监控上**只表现为 `outbox_pending_age_max` 持续上涨**——只看死信条数看不出来。

**如何验证**（读者可执行）：

```shell
# 1) 永久错误立即判死（attempts=1，不进退避）
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
"select state, dead_reason from outbox where event_id='evt_bad_1';"
# 期望：dead | invalid_payload

# 2) 瞬时错误 5 次后判死（累计约 2 分 35 秒）
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
"select attempts, state, dead_at - created_at from outbox where event_id='evt_flaky_1';"
# 期望：5 | dead | 约 00:02:35

# 3) 洞被登记且后续事件继续（核心）
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
"select (select seq from applied_hole where agg_id='SO0000123'), (select last_seq from applied where agg_id='SO0000123');"
# 期望：2 | 5（不是 2 | 1）

# 4) 重投已应用序号不产生重复副作用
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
"select count(*) from stock_reservation where agg_id='SO0000123' and seq=2;"
# 期望：1

# 5) 积压年龄（方案 A 的死锁只能靠这个数发现）
docker exec -i eoh-pg psql -U postgres -d eoh -Atc \
"select coalesce(max(extract(epoch from now()-created_at))::int,0) from outbox where state='pending';"
# 期望：稳态 < 60
```

**下一步**（第 204 天）：周期 7 只剩 **`EW2` 第 2 周验收**一章——把第 2 周五步（骨架 / 下单 / 支付回调 / 库存释放 / 死信）收成六项验收与三道门；退款侧的渠道 T+1 对账接进 `ELA` 对账日报。

## 二十六、第 204 天交付（第 4 周补充 · 主写路径的受限批量化）

新建[主写路径的受限批量化](BatchWrite/index.md)（判据 `EWB-A` ~ `EWB-H`）。这一步收掉的是第 3 周验收留下的开放项：「批量化有 4.5 倍吞吐，但暂不启用，仅用于 outbox 投递」。

**这一步的性质**：前 19 章回答「系统能不能按设计跑、坏了能不能回滚、账对不对」，这一章回答**「已经验证过的优化，敢不敢放到主写路径上」**——它不是性能工作，是**风险定价**工作。

**三条最该记住的结论**：

1. **批量只用在「插入型写」上**。状态迁移永远逐条（影响行数=0 是正常并发结果，不是错误），条件扣减必须用 `RETURNING` 对差集（「没扣成」是业务结果，不是异常）。
2. **批越大不代表越快**。1% 坏单率下，100 单/批的有效吞吐只剩 **2.28×**，还不如 30 单/批的 **3.59×**——因为整批回滚会把好单一起拖下去。生产取 **30**，饱和点 100 只作为理论上限。
3. **真正的解不是「批得更小」，是「把坏单挡在批外」**：预检一次 `SELECT ... WHERE key = ANY($1)`，命中的走幂等路径，剩下的按 `warehouse_id` 分组批写，残余失败单条重放。有效吞吐回到 **≈4.2×**，且爆炸半径从「整批」缩到「一条」。

**本机读数（纯算术推导，非压测）**：`(1−r)^b` 的整批成功率在 r=1% 时——b=10 为 90.4%、b=30 为 74.0%、b=100 为 36.6%、b=300 为 4.9%。这组数解释了为什么「批量 100 单 4.5×」只在全部成功时成立。

**当日验证（读者可执行，见章节第六节）**：① 造 10 单已存在键再发 30 单 → `inserted=20 deduped=10`；② 把 `sku-007` 的 `available` 置 0 → 本批只回退 1 单、其余 29 单 `reserved` 均增加；③ 三条不变量查询全为 0。**第 ② 条是本章的通过条件**——它证明「坏一条不坏一批」。

**下一步**：① `write_batch` 的四个指标接进[监控与告警](Monitoring/index.md)（批次回滚率作为新告警项）；② G3 稳过 72 小时后，把 outbox 投递的批大小从 100 降到 30，统一两处批次语义；③ 第 2 周验收（`EW2`）于第 205 天交付，见下一节。

## 二十七、第 205 天交付（第 2 周第 6 步 · 第 2 周验收）

新建[第 2 周验收](Week2Gate/index.md)（判据 `EW2-A` ~ `EW2-H`）+ 配图 `eoh-week2-gate.svg`（五步 → 六项 → 三道门）。周期 7 的唯一悬空章节至此补齐，**21 章构成完整链路**。

**这一步的性质**：不写新功能，只回答一个第 2 周一直没人问的问题——**「这五步连起来，第 1 周的守卫还在不在」**。五步各自的验证都只覆盖「我这一步对不对」，三种失效形态只在串起来时才暴露：骨架的依赖方向被绕过（下单直接 `new` 了库存客户端）、下单与回调用了两套幂等键（同一笔支付应用两次）、释放与死信争同一行（重投把已释放的预占又扣一次）。

**六项验收**（W2-1 ~ W2-6）：可起且依赖单向 / 下单五步且 outbox 同事务 / 回调验签幂等乱序 / 释放与支付竞态 / 死信分流与重投 / 幂等键保留期。**前五项通过，第六项「有条件通过」**。

**唯一没给绿的那一项是本轮最有价值的读数**（SQLite 3，100 万个键在 30 天内均匀分布）：

| 保留期 | 需保留行数 | 占比 |
| --- | --- | --- |
| 24 小时 | 33,349 | 3.3% |
| 7 天 | 233,378 | 23.3% |
| 30 天 | 999,999 | 100% |

主键命中查询 **7.1 µs/次**（查询侧完全不是问题），而一次性清理 24 小时之外的 **966,651 行要 782 ms**（清理侧是问题：长事务 + 大量 WAL，与下单高峰相撞会拖慢主键写入）。所以结论是「保留 7 天可以，但清理必须分批（每批 ≤ 5,000 行）并监控积压行数」——**「任务每天成功」不等于「表没在涨」**。

**三道门**：G1 可启动（4/4 healthy，58 s）、G2 可回放（同 `Idempotency-Key` 两次 → 同 `order_id` 同金额）、G3 可对账。**G3 的口径比「两张表行数相等」强一档**：按聚合根对齐每个订单的最后一条事件——行数相等只能证明数量对得上，一个订单两条 `PAID`、另一个零条，行数照样相等。

**三项遗留写进第 3 周**：幂等键清理未分批、回调乱序只覆盖「晚到」未覆盖「早到」、G3 查询未进 CI。

## 二十八、第 206 天交付（第 4 周补充 · 交易通知的触达闭环）

新建[交易通知的触达闭环](NotifyFulfillment/index.md)（判据 `ENT-A` ~ `ENT-H`）+ 配图 `eoh-notify.svg`（一条链 → 三张表 → 八条验收）。周期 7 章节 21 → **22 章**。

**这一步的性质**：不新增业务功能，只补**状态表达**。前三周的验收一直问「事件有没有丢」，这一步第一次问「**用户有没有收到，以及你能不能证明**」。缺口有三处，都不是「功能没做」：`notify_task` 一行同时表达「消息」与「尝试」；退订与静默发生在入队之后；站内信与短信挤在同一行。

**三表拆分**：`notification_outbox`（一条消息一行 + 三元组唯一键）、`notification_delivery`（一次尝试一行 + `state_rank`）、`notification_inbox`（站内信读模型 + `read_at` 时间戳）。历史 `notify_task` **保留不删**，迁移用 `where not exists` 保证可重跑。

**事件映射五条硬规定**：`order.paid` 站内信主通道、`order.shipped` 短信主通道（带可点短链）、`shipment.delivered` 站内信、`order.refunded` 短信、`payment.failed` 短信且**永不压后**。退款与扣款失败豁免静默时段的判据不是「是否打扰」，而是「**不发的代价是否高于打扰的代价**」。

**三条最有用的结论**：

1. **退订是终止，不是降级**。把「用户退了短信」实现成「改发推送」，在监管口径下仍是一次未经同意的发送。本机模拟万级投放：只在入队判定的写法比「发送时刻再判一次」多发出 **6 条**。
2. **同一事件投 5 次，按 `event_id` 去重后只剩 2 条**（60% 是重复）。这是消费组重平衡时的常态，不是极端情况。
3. **事务消息必须走优先队列**。1 worker / 500 条每秒、营销 700 条每秒注入 180 秒：FIFO 下事务 p99 **51.82 s**，双队列优先 **0.00 s**，而营销 p99 只从 51.82 涨到 52.19（+0.7%）。

**当日验证（读者可执行，见章节第七节）**：N1~N8 八条，每条一条 SQL 或一次 curl。**N5（迟到回执不回退）与 N6（同组 `delivered` 唯一）是核心**——它们对应的 bug 只在回执乱序与降级超时时出现，正常路径永远测不到。

**下一步**：① N5/N6 接进第 3 周的一致性用例矩阵；② `notification_inbox` 清理分批（每批 ≤ 5,000 行）；③ 回执到达率进监控，把 `EMT` 的五个指标扩到六个。

## 二十九、第 207 天交付（第 4 周补充 · 订单完成后的开票闭环）

新建[订单完成后的开票闭环](Invoicing/index.md)（判据 `EIN-A` ~ `EIN-H`）+ 配图 `eoh-invoicing.svg`（五个动作 + 三条不变量 + 两个方向的差异）。周期 7 章节 22 → **23 章**。

**这一步的性质**：不新增业务能力，只补**单据与状态的关系**。第 4 周把「钱」退对了（`ERC`），但没有回答「已经开出去的票怎么办」；上线验收（`EW4`）的 21 条里与发票有关的只有「能查到退款单」。缺口三处，都不是「功能没做」：票面没按行拆、没有可开票判定、已开票退款没有红冲路径。

**两条硬规定**：

1. **发票行必须与订单行一一对应**（`invoice_line.order_line_seq`）。少了这个键，「逐行对账」只能按顺序对，而退款拆行会改变顺序——于是对账从「查 SQL」变成「人工比对」。
2. **税额逐行算**，不用「总额 × 税率再摊回」。本机 5,000 单（12,496 行、税率 6%）：两种口径税额不同的有 **1,182 单（23.64%）**，最大差 2 分。2 分不影响收款，但它让财务系统拒收，退回手工开票。

**三条最有用的读数**：

1. **一单一票靠部分唯一索引**：`unique (order_id) where status <> 'void'` + `on conflict do nothing`。同一批 5,000 单连续申请 3 次，最终仍是 **5,000 张**（29.7 ms）；去掉索引则 15,000 张——这就是「财务每月收到三份导出表」的成因。
2. **退款拆行必须用最大余数法**：朴素逐行四舍五入在 5,000 张退款单里有 **926 张（18.52%）**逐行合计 ≠ 退款额（差 1 分），最大余数法为 0。差 1 分导致红冲票面与退款额不等，又回到手工调整。
3. **跨月开票不是异常**：开票月 ≠ 完成月的有 **1,597 单（31.9%）**、金额 **969,327.08 元**。所以「本月开票金额」与「本月收入」必然不等；这一条不写进交接文档，下个月一定被当 bug 排查。

**当日验证（N1~N8，见章节第七节）**：N3 是反向验收——它期望「两种税额口径不同」，用差异本身证明票面真的按行算，而不是走了「总额 × 税率」的捷径。

**下一步**：① 合并开票（多订单一张票）需要 `invoice_order` 关联表，红冲要能定位到票内哪个订单；② 红冲尚未生成冲减分录，接进[对账日报](ReconciliationHandover/index.md)后再补；③ `invoice_request.state='pending'` 超 24 小时要告警——人工流程里的「卡住」最难被发现。

## 三十、第 208 天交付（第 4 周补充 · 库存盘点的批量导入与对账导出）

新建[库存盘点的批量导入与对账导出](BulkHandover/index.md)（判据 `EBD-A` ~ `EBD-H`）+ 配图 `eoh-bulk.svg`（四段流水 + 一条禁令 + 四条读数）。周期 7 章节 23 → **24 章**。

**这一步的性质**：不新增业务能力，只补**运营入口**。前 23 章的写路径全是「事件驱动、单笔、可幂等」，但没有回答「运营每月盘点改 1.2 万个 SKU 的 `on_hand` 怎么改」。若给一个 `update stock set on_hand = ?`，预占就被绕过——`available = on_hand - reserved` 可能变负，而这正是 `EOH` 族 I1/I5 禁止的状态。

**三条硬规定**：

1. **盘点必须落 `stock_adjust_log`（before/after/delta）**，禁止裸 `update`。裸更新没有 before 值，三个月后没人能解释「这个 SKU 的库存为什么从 5,000 变成 100」。
2. **盘点后 `on_hand >= reserved`**，否则该行进回执 `E_BELOW_RESERVED`。一个 SKU 的盘点错误会放大成全站该 SKU 不可下单——订单侧的条件扣减会让所有新订单失败。
3. **导出带 `snapshot_ts` 且按 `sku` keyset 分页**。运营要拿它与实物盘点表逐行对，按 `sku` 排序天然有序；offset 分页在并发预占下漏 0.1%。

**本机读数（Python 3.13.12 + SQLite 3，非生产压测）**：12,000 行盘点遇 1 行坏数据 → 整批事务 **入账 0 行**、批 500 → **11,500 行**、批 100 → **11,900 行**；同一文件导两次，无幂等键 → 流水 **24,000 行**，`batch_no` 主键 → **12,000 行**；导出 20,000 行期间并发预占 → offset 分页 **漏 20 行（0.1%）**；全量载入 **27,556 KB** vs 流式 **62 KB**。

**当日验证（N1~N8，见章节第五节）**：N3（预占保护）与 N4（`delta` 恒等式）是核心——正常盘点永远测不到「绕过预占」，而差额恒等式是「这次盘点到没盘到」的唯一证据。

**下一步**：① 价目批量导入复用同一套批次表（`batch_type = PRICE`），同样要 before/after 流水；② 给 `E_BELOW_RESERVED` 一个「允许并告警」的显式开关，落 `stock.shortfall` 事件交人工处理；③ 库存快照并入[对账日报](ReconciliationHandover/index.md)，避免订单侧与库存侧两套口径。

## 三十一、第 209 天交付（第 4 周补充 · 售后工单受理与 SLA 时钟）

新建[售后工单受理与 SLA 时钟](SupportSLA/index.md)（判据 `ESA-A` ~ `ESA-H`）+ 配图 `eoh-support-sla.svg`（售后工单与订单的双向关联 + 两个时钟口径的读数）。周期 7 章节 26 → **27 章**（实数口径，见第三节下方说明）。

**这一步的性质**：前 26 章的入口全是**系统对系统**（支付回调、库存回调）或**运营对系统**（盘点导入）。真实客户不调 API，他发一条消息说「订单 20261001 一直没发货」。这条消息若只进邮箱，订单中心就永远不知道**这个客户在等**——而「等待」是这一章唯一要解决的问题。

**三处缺口**（都不是「功能没做」，而是**表达不足**）：

| # | 缺口 | 后果 |
| --- | --- | --- |
| ① | 没有「客户请求」这个对象 | 无法统计多少单在等回复，也答不出「这个客户提过几次」 |
| ② | 没有对外的时钟 | 内部有「支付超时 15 分钟」「发货 48 小时」，但没有一个时钟是**对客户承诺**的 |
| ③ | 工单与订单两套时间 | 订单说「已发货」、客服说「客户还在问货在哪」，谁都不知道卡在哪一段 |

**三条硬规定**：

1. **工单必须挂订单**（`order_id not null`）。不是「方便查询」，而是**一致性**：任何售后动作（退款/补发/开票）都要回订单上下文校验（是否已退、是否已发、是否超窗口）。无 `order_id` 的工单只能人工找单，1.2 万单/天必然找错。
2. **SLA 到期时间落库为快照**，且能从「起点 + 日历版本」重算。日历会被改（加节假日、调班次），现算的到期时间会让历史报表**每天都变**——而客户手里的承诺是当时那一刻。
3. **首响只由客户可见的回复回填**，内部备注不算。这一条决定达标率可不可信：备注也算首响，坐席写一句「我看下」就得到 2 分钟的首响。

**本机读数（Python 3.13.12 标准库，6,000 张工单，到达时间均匀分布在一周的自然时间里）**：自然时钟的到期点落在非工作时段 **4,351 / 6,000 = 72.52%**；同一批实际首响按**自然时钟**判超时 **91.97%**、按**工作时钟**判超时 **50.13%**；换尺后达标率 **8.03% → 49.87%**。差的约 42 个百分点不是算法误差，是「**我们下班了**」被算成了「我们违约」。

**当日验证（N1~N8，见章节第六节）**：N4（时钟口径）与 N8（与订单对账）是核心——N4 证明这把尺是「对客户承诺的那把」，N8 证明工单没有变成第二个真相源。N1/N3/N5 是守卫（工单必挂订单、备注不算首响、解决必须有类型），N2/N6/N7 是幂等（首响、重复关闭、重复升级），缺任何一条两周内就会长出「工单说已退、账上没退」。

**下一步**：① 把「待客户回复」纳入时钟，补「下次响应」；② 受理回执与升级提醒走已有 outbox，不新建通道（见[通知触达闭环](NotifyFulfillment/index.md)）；③ 售后原因结构化，退货要细分「质量问题 / 尺码不符 / 不想要」，否则退款率无法归因；④ `ESA-G` 的两条对账 SQL 并入[对账日报](ReconciliationHandover/index.md)，避免两套口径。

## 三十二、第 210 天交付（第 4 周补充 · 退款协议签署与存证举证）

新建「退款协议签署与存证举证」一章（判据 `ERA-A` ~ `ERA-H`）+ 配图 `eoh-refund-agreement.svg`（五步流水 + 取证包四件物料 + 两条读数）。周期 7 章节 27 → **28 章**。

::: warning 这一章目前只有交付记录，没有章节页
`project/Complete/EventOrderHub/RefundAgreement/` **不存在**（`git log --all` 该路径输出为空）。本节记录的读数与判据保留原样不作删改，但读者**点不进章节页**——这是台账先于实物的缺陷，已在第三节「台账⇄实物对账」登记为欠账。补写应由跑过那批实验的人做，不从本节转述生成。
:::

**这一步的性质**：前 28 章回答的是「钱退得对不对」，这一章第一次回答「**凭什么这么退**」。客服聊天记录不是证据——它可以被截断、可以被不同人解释、也可以根本找不到。协议签署把「责任认定、运费承担、赠品处置」三件最容易吵起来的事，落成一份带时间戳的书面依据。

**三处缺口**（都不是「功能没做」，而是**依据缺失**）：

| # | 缺口 | 后果 |
| --- | --- | --- |
| ① | 退款只有原因枚举，没有责任认定 | 争议时说不清「当时双方认可的费用承担方式」 |
| ② | 没有签署回执 | 客户说「我没同意扣运费」，拿不出他同意的那一刻 |
| ③ | 举证要人工找材料 | 一次举证 2~3 人日，且经常缺件 |

**三条硬规定**：

1. **协议必须同时挂 `refund_id` 与 `order_id`**。只挂退款时，一单拆成多笔部分退款后无法反查「这单签过几份协议」。
2. **签署阻塞退款，且落在数据库层**——执行退款的 SQL 带 `(not require_agreement or agreement_signed)`，绕过 API 也退不出去。
3. **客户签署时的内容摘要必须等于渲染摘要**，不等就拒签。客户签的必须是他看到的那一版。

**本机读数（Python 3.13.12 标准库，5,000 笔退款，金额对数正态，固定种子 20261026）**：退款金额中位数 **2,903.99 元**、p90 **9,185.93 元**；触发协议阈值（> 5,000 元）的 **1,383 笔 = 27.7%**，但这部分占**金额的 62.2%**；若按「先退后签」，最终未签 **284 笔（5.7%）**，敞口 **1,391,153.70 元 = 退款总额的 6.36%**。**27.7% 的笔数挡住 62.2% 的钱**——这是把「阻塞式签署」写进发布单的唯一理由。

**当日验证（N1~N8，见章节第五节）**：N4（未签不得退款）与 N7（追加内容必须被覆盖率抓到）是核心守卫；N3（摘要不一致拒签）与 N6（OTP 一次性）是意愿侧守卫；N1/N2/N5 是外键与幂等，N8 证明证据包能离线复核。

**下一步**：① 协议并入[对账日报](ReconciliationHandover/index.md)的 D3 子类；② 模板按责任类型分版（`SELLER` / `SHARED` / `NO_FAULT`），不靠变量拼条款；③ 小额极速退款给「先退后补签」一个显式豁免（落 `waiver_reason` + 审批人）；④ `ERA-C` 的权限收回并入第 4 周验收闸门 G5。

## 三十三、第 210 天交付（同日第二班 · 运营后台的权限与 PII 边界）

新建「运营后台的权限与 PII 边界」一章（判据 `EAC-A` ~ `EAC-H`）+ 配图 `eoh-access.svg`（三层边界 + 36 格矩阵 + 审计闭环）。周期 7 章节 **28 → 29 章**。

::: warning 这一章同样只有交付记录，没有章节页
`project/Complete/EventOrderHub/OperationAccess/` **不存在**（同属第三节登记的欠账）。本节正文与读数原样保留，等有实物的人补页。
:::

**这一步的性质**：前 28 章里出现过七种「人」——客户、仓、运营、财务、税务、通知运营、客服——但**没有一章回答「他们凭什么看得到这条订单的地址」**。系统里只有一种账号，所有后台操作共用一个 `admin`。这一章补的不是功能，是**边界**。

**三处缺口**（都不影响功能，都影响事故的性质）：

| # | 缺口 | 真实后果 |
| --- | --- | --- |
| ① | 没有「谁在操作」这个维度 | 事故复盘答不出「谁把库存改成了 0」——不可归因 |
| ② | PII 明文可读（含导出） | 一次导出就是一份可外流名单——合规事件 |
| ③ | 没有「看过什么」的记录 | 「谁查过这个客户的地址」无从回答——无法证明没发生 |

**三条硬规定**：

1. **权限判在服务端、判在取数之前**。前端隐藏按钮不算权限，`curl` 一下就绕过；判定点放在 Repository 之上、业务逻辑之下。
2. **每次读 PII 都要写 `purpose`**，取值只有 `FULFILLMENT` / `AFTER_SALE` / `AUDIT` / `LEGAL` 四个。没有用途就没有读取——这不是为了合规好看，而是为了事后能区分「为处理工单看过」与「有人批量翻过」。
3. **导出必须有条数上限 + 水印 + 二次确认**。单次 5,000 行封顶，超限走审批；水印写「导出人 + 时间 + 用途」，因为文件一旦离开系统，剩下的只有纸面证据。

**本机读数（矩阵计数，非压测）**：9 个动作 × 4 个角色 = **36 格**，其中允许 **12 格**、拒绝 **24 格**。默认拒绝时越权面 **0 格**；默认允许时越权面 **24 格**，且**新增动作会静默多一个洞**——这是本章最想钉住的一句话：**风险不在写错哪条规则，而在默认值选错了**。另：9 个动作里 **4 个**会触碰 PII（`order.read_pii`、`shipment.label_reprint`、`invoice.issue`、`export.bulk`），只在导出做审计的覆盖率是 **25%**。

**当日验证（N1~N8，见章节第六节）**：N4（无权限角色的响应体里**没有** PII 字段）与 N5（客服看到 `138****0000` 而库里仍是原值）是核心——它们分辨「列级投影」与「应用层过滤」。N1/N3 是越权面，N2 是用途必填，N6/N7 是批量防护，N8 是权限变更的生效延迟。

**下一步**：① 把 `purpose` 接进工单，让「用途」从自由枚举变成可核对的工单号引用；② 客户端（客户查自己的单）走独立判定，不复用角色表；③ `pii_access_log` 保留期 ≥ 承运商账单争议窗口（180 天）；④ 把 24 格拒绝做成 24 条 `403` 断言，进第 3 周一致性用例矩阵。

## 三十四、第 210 天交付（第 4 周补充 · 订单检索与导出）

**这一步补的是读侧**。前 34 章的入口几乎全是写：下单、支付回调、库存扣减、批量导入、开票、退款、售后、签署、权限。而运营与客服每天真正在用的是读——「把这个商家今天的待发货订单列出来」「把上个月所有退款的单子导给财务」。读侧没有事务包裹，出错不报错，只表现为**列表少一行、导出多一行、总数看着不对**。

**三个缺口与读数（Python 3.13.12 + SQLite 3，20 万行，种子 20261026）**：① **深翻页**——`offset=150000` 的单页要跳过 15 万行才取 20 行（扫 150,020 行、10.82 ms），同样距离用游标翻 7,500 页合计 **662 ms**，每页恒定；② **总数**——`status='PAID' and amount>100000` 的 `count(*)` 要 **49.33 ms**，比取 20 行的 0.08 ms 慢六百倍，1% 采样估算误差 −0.8%~−3.9%，且**采样不一定更快**（`id % 100 = 0` 用不上索引，反而是 29.43 ms vs 7.09 ms）；③ **导出漂移**——导出期间 2 轮各 200 条状态变更，offset 分页读到 100,000 行但唯一只有 99,993（**7 行重复**），游标分页 0 重复。

**一个反直觉的结论**：`where status in ('PAID','SHIPPED') order by created_at desc` 这类查询，索引首列放**排序键**（`created_at`）实测 **0.08 ms**，放**过滤列**（`status`）实测 **77.52 ms**——差约 970 倍。原因是前者可以「按序扫、凑够 20 条即停」，后者要在两个状态区间各扫一遍再归并。这条直接推翻了「先给 where 列建索引」的直觉。

**三条硬规定**：① **排序键必须复合且不可变**（`created_at, order_id`），用 `updated_at` 排序必然漂移；② **游标带 HMAC 与签发时间**，校验失败返回 400，过期拒绝——游标里是排序键，可被伪造就等于可被拖库；③ **导出先固化再分片**（`export_rows` 快照表 + 主键区间切分），完成后校验「行数 + 金额合计」，不一致置 `FAILED` 且不下发链接。

**当日验证（N1~N8）**：N1 同秒三单翻页无重复；N2 篡改 cursor 返回 `400 INVALID_CURSOR`；N3 12 小时前的 cursor 返回 `CURSOR_EXPIRED`；N4 游标第 7,500 页与首页同量级；N5 `total_mode=estimate` 字段名带 `est`；N6 导出期间改 200 单，文件行数 = 快照行数；N7 截断分片一行后 job 置 `FAILED`；N8 `explain` 里无 `SORT`。

**下一步**：① 商家后台的「待发货」看板换用 `ix_order_read_merchant`，先 `explain analyze` 对比再删 `status` 单列索引；② 导出支持 Parquet（CSV 超 1,048,576 行会被 Excel 截断）；③ 游标签名密钥进 KMS 并支持轮换；④ `EOQ-G` 的慢查询采样接入 `Monitoring` 的 p99 看板；⑤ 列表默认 `total=estimate`，只有财务与对账页用 `exact`。

## 三十五、第 220 天交付（第 4 周补充 · 上线产物的可复现与构建缓存治理）

**这一步补的是一条没被验收过的前提**。第四周第 4、5 步做完了「一键部署」和「上线验收」，但那些检查都默认了「重跑一次产出的是同一个东西」。而「回滚到上周的镜像」只有在「上周那个镜像 = 上周那个 commit 的确定产物」时才成立——否则回滚回去的是一个**没人验证过的新东西，只是恰好跑起来了**。

**三个缺口**：① **产物不可复现**——打包保留 `mtime`、`uid/gid` 与遍历顺序，换一台构建机就是新摘要；② **镜像用 tag 引用**——`latest` 无法回滚、上游重发 tag 即静默换底座；③ **缓存键不完整**——只按 `github.sha` 则命中率为 0（等于没缓存），只按锁文件则漏 `src/**` → **假命中，把旧代码发布出去**。

**本机读数（Python 3.13.12 `tarfile`/`gzip`，40 个 200~4,000 字节文件，种子 20261031，脚本不入库、可复跑）**：① **同一棵树连打两次**——默认写法 `e8eda40a = e8eda40a`，**它是相同的**；这说明「默认写法一定有差异」是错的，差异只在**条件变化时**出现，于是问题**不在本地复现**，只在换机器的那一次上线时出现；② **`touch` 一个文件**——默认写法 `e8eda40a → f0bfc7a5`，规范化写法恒为 `1093449f`；③ **换一个 `clone` 目录**——默认 `e8eda40a → eb7a972b`，规范化仍 `1093449f`；④ **gzip 头里的 `mtime`**——两次打包 `fef7fdd4 ≠ 41725f7c`，置 0 后 `4812e07d` 恒等；⑤ **成员顺序反排**——体积仍是 **122,880 B**（分毫不差），摘要却是 `6ce6447c`：**「比大小」这种校验手段在这里直接失效**；⑥ **压缩比**——tar 122,880 B → gzip 86,519 B，仅 **1.42×**（小文件多时别指望压缩救场）。

**三条硬规定**：① **`FROM` 用 `@sha256:`，回滚对象也用 digest**——tag 可被重新 push 指向另一个 digest，钉 tag 等于没钉；② **`SOURCE_DATE_EPOCH` + 成员排序 + 属主归零 + `gzip -n` 四件一起上**，少一件就换摘要；③ **缓存键 = 锁文件 + 全部影响产物的路径**（含 `migrations/**`、`tsconfig.json`），且**只有主干可写远程缓存**——一次错误的 PR 就能污染主干缓存造成假命中。

**一个容易混的地方**：**产物 digest 与镜像 manifest digest 是两件事**。后者还含构建时间与 provenance 来源信息，默认开启时两次构建必然不同——所以验收时要么 `--provenance=false --sbom=false`，要么把「产物可复现」和「manifest 可复现」当两个目标分开验。

**当日验证（S1~S8）**：S1 同树连打两次摘要相同；S2 `touch` 后仍相同；S3 换目录后仍相同（去掉 `--sort=name` 必须变）；S4 `gzip -n` 两次相同、去掉 `-n` 必须变；S5 `imagetools inspect` 拿得到 digest 并已写进 `FROM`；S6 两次 `buildx build` 的 image digest 相同；S7 改一个 `migrations/*.sql` 后缓存键必须变；S8 PR 任务尝试写远程缓存被拒（负向用例）。

**下一步**：① `deploy/compose.yml` 的 `image:` 换成 `order-api@sha256:...`，回滚脚本同步改；② 产物清单 `manifest.txt`（`find dist -type f -exec sha256sum {} +`）一并进镜像，线上可逐文件比对；③ 缓存键的负向用例进 CI；④ 六条验收命令接进[上线验收](LaunchAcceptance/index.md)检查表；⑤ 镜像 digest 写进 `service.version` 标签，与[监控章节](Monitoring/index.md)对齐——「哪个产物在报错」从追问 tag 变成标签查询。

**本页判据 `EBR-A ~ EBR-H`**：产物可复现 / 底座钉 digest / 构建期不联网 / 产物不含构建机痕迹 / 缓存键完整 / 只有主干可写缓存 / 回滚对象是 digest / **每条验收命令都有负向用例**。最后一条最容易被跳过：**一条永远为真的验收命令等于没有验收**。

## 三十六、判据纪律

每章 8 条，编号形如 `EOH-A`，逐章前缀唯一（`EOH` / `ETS` / `EOA` / `EDB` / `EEN` / `EW1` / `EOR` / `EPY` / `EIV` / `ESF` / `ERC` / `EDL` / `EWB` / `EW2` / `ECM` / `ECC` / `ECP` / `EW3` / `EDP` / `EMT` / `ERB` / `ELA` / `EW4` / `ENT` / `EIN` / `EBD` / `ESA` / `ERA` / `EAC` / `EBR`），全库不撞号。判据只有三种形态：**可复跑的读数**、**可勾选的检查项**、**可对照的结构**（表/图/契约）。
