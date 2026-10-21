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

| # | 章节 | 判据族（已交付才填） | 状态 |
| --- | --- | --- | --- |
| 1 | [需求拆分：五个上下文、十个故事与订单状态机](Requirements/index.md) | `EOH-A` ~ `EOH-H` | ✅ 第 181 天 |
| 2 | [技术选型与版本基线](TechBaseline/index.md) | `ETS-A` ~ `ETS-H` | ✅ 第 182 天 |
| 3 | 架构设计：事件流与一致性边界 | — | ⏳ |
| 4 | 数据库设计：九张表与六条不变量 | — | ⏳ |
| 5 | 环境与工程骨架 | — | ⏳ |
| 6 | 第 1 周验收：设计可照着实现 | — | ⏳ |
| 7 | 下单链路与本地事务表 | — | ⏳ 第 2 周 |
| 8 | 支付回调：验签、幂等与乱序 | — | ⏳ |
| 9 | 库存预占与超时释放 | — | ⏳ |
| 10 | 发货与签收 | — | ⏳ |
| 11 | 补偿与对账 | — | ⏳ |
| 12 | 第 2 周验收 | — | ⏳ |
| 13 | 一致性用例矩阵 | — | ⏳ 第 3 周 |
| 14 | 并发与幂等专项 | — | ⏳ |
| 15 | 压测与容量 | — | ⏳ |
| 16 | 第 3 周验收 | — | ⏳ |
| 17 | 一键部署与配置 | — | ⏳ 第 4 周 |
| 18 | 监控与告警 | — | ⏳ |
| 19 | 上线验收与对账日报 | — | ⏳ |
| 20 | 第 4 周验收与交接 | — | ⏳ |

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

## 七、判据纪律

每章 8 条，编号形如 `EOH-A`，逐章前缀唯一（`EOH` / `ETS` / `EAT` / `EDB` / `EEN` / `EW1` / `EOR` / `EPY` / `EIV` / `ESF` / `ERC` / `EW2` / `ECM` / `ECC` / `ECP` / `EW3` / `EDP` / `EMO` / `ELA` / `EW4`），全库不撞号。判据只有三种形态：**可复跑的读数**、**可勾选的检查项**、**可对照的结构**（表/图/契约）。
