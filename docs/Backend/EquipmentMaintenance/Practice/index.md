# 实战：从台账到可复算可用率的闭环

<p style="text-align:center;"><img src="../assets/em-logo.png" alt="设备维护与可靠性工程" style="zoom:75%;" /></p>

前面八页各讲一段。这一页把它们拧成一条能跑通的闭环：**七张表建起来、五条自检全为 0、四条负向用例全被拒、最后算出一个能被别人复算的可用率**。所有输出都是本机实际跑出来的，不是示意。

本页判据族 `EQX-A` ~ `EQX-H`，共 8 条，定义在第六节。

## 一、场景与边界

![七步闭环：从台账到可复算的可用率](../assets/em-practice.svg)

一个 200 台设备的车间，先只做**一条产线 + 两台 A 类设备**的闭环：

| 项 | 设定 |
| --- | --- |
| 范围 | `PLANT1/LINE2` 的 `EQ-001`（注塑机）、`EQ-002`（冷却泵）、`EQ-003`（传送带，挂 `EQ-001` 下） |
| 周期 | 90 天 |
| 数据来源 | 工单 + 停机登记 + 点检 + 备件领用 |
| 本期**不做** | 预测模型、OEE 性能因子、跨厂汇总、移动端 App |

::: tip 为什么先做两台
闭环的价值不在「覆盖多少设备」，而在「**每一个数都能追到源头**」。两台设备足以跑通全部七段，且任何一处口径错都能在十分钟内发现。铺到 200 台再做，错的地方会藏在平均值里。
:::

## 二、七张表

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE eq_asset (
  asset_id     TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  func_loc     TEXT NOT NULL,
  parent_id    TEXT REFERENCES eq_asset(asset_id),
  criticality  TEXT NOT NULL CHECK (criticality IN ('A','B','C')),
  status       TEXT NOT NULL DEFAULT 'RUNNING'
                 CHECK (status IN ('RUNNING','DOWN','MAINT','RETIRED'))
);

CREATE TABLE eq_plan (
  plan_id      TEXT PRIMARY KEY,
  asset_id     TEXT NOT NULL REFERENCES eq_asset(asset_id),
  strategy     TEXT NOT NULL CHECK (strategy IN ('BM','PM','CBM','PdM')),
  interval_h   INTEGER NOT NULL CHECK (interval_h > 0),
  last_done_at TEXT,
  next_due_at  TEXT NOT NULL,
  active       INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1))
);

CREATE TABLE eq_wo (
  wo_id        TEXT PRIMARY KEY,
  asset_id     TEXT NOT NULL REFERENCES eq_asset(asset_id),
  source       TEXT NOT NULL CHECK (source IN ('REPORT','PLAN','INSPECT')),
  wo_type      TEXT NOT NULL CHECK (wo_type IN ('CORRECTIVE','PREVENTIVE','IMPROVE')),
  fault_code   TEXT,
  state        TEXT NOT NULL DEFAULT 'OPEN'
                 CHECK (state IN ('OPEN','ASSIGNED','WORKING','DONE','CLOSED','CANCELLED')),
  started_at   TEXT,
  finished_at  TEXT,
  dedup_key    TEXT UNIQUE,
  CHECK ( (state IN ('DONE','CLOSED') AND finished_at IS NOT NULL)
       OR (state NOT IN ('DONE','CLOSED')) )
);

CREATE TABLE eq_downtime (
  dt_id        INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id     TEXT NOT NULL REFERENCES eq_asset(asset_id),
  wo_id        TEXT REFERENCES eq_wo(wo_id),
  cause        TEXT NOT NULL CHECK (cause IN ('MECH','ELEC','SETUP','WAIT','PLANNED')),
  is_planned   INTEGER NOT NULL DEFAULT 0 CHECK (is_planned IN (0,1)),
  start_at     TEXT NOT NULL,
  end_at       TEXT,
  open_flag    INTEGER GENERATED ALWAYS AS (CASE WHEN end_at IS NULL THEN 1 ELSE NULL END) VIRTUAL,
  CHECK (end_at IS NULL OR end_at > start_at)
);
CREATE UNIQUE INDEX ux_dt_open ON eq_downtime(asset_id, open_flag);

CREATE TABLE eq_part (
  part_id      TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  abc          TEXT NOT NULL CHECK (abc IN ('A','B','C')),
  on_hand      INTEGER NOT NULL DEFAULT 0 CHECK (on_hand >= 0),
  safety_stock INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE eq_wo_part (
  wo_id        TEXT NOT NULL REFERENCES eq_wo(wo_id),
  part_id      TEXT NOT NULL REFERENCES eq_part(part_id),
  qty          INTEGER NOT NULL CHECK (qty > 0),
  PRIMARY KEY (wo_id, part_id)
);

CREATE TABLE eq_inspect (
  insp_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id     TEXT NOT NULL REFERENCES eq_asset(asset_id),
  point        TEXT NOT NULL,
  value        REAL NOT NULL,
  verdict      TEXT NOT NULL CHECK (verdict IN ('OK','WARN','NG')),
  at           TEXT NOT NULL
);
```

七个 `CHECK` / 一个部分唯一索引 / 一个触发器，是全篇判据的落点：

| 约束 | 挡住的缺陷 |
| --- | --- |
| `eq_wo` 的 `CHECK` | 「已完工但不填完工时间」——MTTR 凭空消失 |
| `ux_dt_open` | 「同一设备两条未闭合停机」——并集算错 |
| `eq_part.on_hand >= 0` | 发料冲成负库存 |
| `eq_plan.interval_h > 0` | 间隔填 0 导致每天到期 |
| `eq_downtime.end_at > start_at` | 逆序区间产生负时长 |
| 触发器 `trg_wo_no_reopen` | 关单后回退，历史报表被改写 |

```sql
CREATE TRIGGER trg_wo_no_reopen BEFORE UPDATE ON eq_wo
WHEN OLD.state = 'CLOSED' AND NEW.state != OLD.state
BEGIN SELECT RAISE(ABORT, 'closed work order is immutable'); END;
```

## 三、五条自检：期望全为 0

```sql
-- C1 工单指向不存在的设备
SELECT count(*) FROM eq_wo w LEFT JOIN eq_asset a USING(asset_id) WHERE a.asset_id IS NULL;

-- C2 计划的下次到期早于上次完成
SELECT count(*) FROM eq_plan WHERE last_done_at IS NOT NULL AND next_due_at <= last_done_at;

-- C3 已关闭的纠正工单缺少停机记录
SELECT count(*) FROM eq_wo w
WHERE w.wo_type='CORRECTIVE' AND w.state='CLOSED'
  AND NOT EXISTS(SELECT 1 FROM eq_downtime d WHERE d.wo_id = w.wo_id);

-- C4 同一设备同时存在两条未闭合停机
SELECT count(*) FROM (SELECT asset_id FROM eq_downtime WHERE end_at IS NULL
                      GROUP BY asset_id HAVING count(*) > 1);

-- C5 备件账面为负
SELECT count(*) FROM eq_part WHERE on_hand < 0;
```

五条自检的共同点：**它们不检查「有没有填」，只检查「填的东西之间矛不矛盾」**。这类检查才能在数据量涨上去之后继续有效。

## 四、四条负向用例：期望全部被拒

负向用例比正向更重要。正向只能证明「能存进去」，负向才能证明「挡得住」。

| 编号 | 用例 | 期望被什么挡住 |
| --- | --- | --- |
| N1 | 已关闭工单改回 `WORKING` | 触发器 `closed work order is immutable` |
| N2 | 同一设备开第二条未闭合停机 | 部分唯一索引 `ux_dt_open` |
| N3 | 发料把库存冲成负数 | `CHECK (on_hand >= 0)` |
| N4 | 维护间隔填 0 | `CHECK (interval_h > 0)` |

```shell
# N1
sqlite3 /tmp/mnt.db "UPDATE eq_wo SET state='WORKING' WHERE wo_id='WO-1001';"
# 期望：Runtime error: closed work order is immutable

# N2
sqlite3 /tmp/mnt.db "INSERT INTO eq_downtime(asset_id,cause,start_at) VALUES('EQ-001','ELEC','2026-11-02T12:00');"
# 期望：UNIQUE constraint failed: eq_downtime.asset_id, eq_downtime.open_flag

# N3
sqlite3 /tmp/mnt.db "UPDATE eq_part SET on_hand = on_hand - 99 WHERE part_id='SP-0001';"
# 期望：CHECK constraint failed: on_hand >= 0

# N4
sqlite3 /tmp/mnt.db "INSERT INTO eq_plan VALUES('PM-009','EQ-003','PM',0,NULL,'2026-11-10T08:00',1);"
# 期望：CHECK constraint failed: interval_h > 0
```

## 五、本机实跑输出

```text
== 建库 ==
表 7 张：eq_asset, eq_downtime, eq_inspect, eq_part, eq_plan, eq_wo, eq_wo_part
部分唯一索引：['ux_dt_open']

== C1~C5 自检（期望全 0）==
C1 工单指向不存在的设备: 0
C2 计划的下次到期早于上次完成: 0
C3 已关闭的纠正工单缺少停机记录: 0
C4 同一设备同时存在两条未闭合停机: 0
C5 备件账面为负: 0

== N1~N4 负向用例（期望全部被拒）==
N1 关闭后改回 WORKING: ✓ 被拒 → closed work order is immutable
N2 同一设备开第二条未闭合停机: ✓ 被拒 → UNIQUE constraint failed: eq_downtime.asset_id, eq_downtime.open_flag
N3 发料把库存冲成负数: ✓ 被拒 → CHECK constraint failed: on_hand >= 0
N4 维护间隔为 0: ✓ 被拒 → CHECK constraint failed: interval_h > 0

== 关键读数 ==
已闭合停机 1 条，合计 2.5 h；未闭合 1 条（进行中）
MTTR = 150.0 min
A(负荷) = 99.971%   （单台口径，8760 h 分母）

EXIT = 0
```

两条读数值得停一下：

- **MTTR = 150.0 min**：单条记录算出来的 MTTR 没有任何统计意义。它的价值是**证明链路通了**——时长能从 `start_at` / `end_at` 算出来，而不是从「感觉修了两小时」抄来。
- **A(负荷) = 99.971%**：`(8760 − 2.5) / 8760`。注意这里分母用的是 `8760`（日历），所以它其实是「日历口径」；真正做报表时必须把 `0.82` 的排产率乘进去，否则和小页里 81.75% / 99.70% 的对照关系对不上。

::: danger 输出里有一个名不副实的标签，保留原样
上面这块输出是脚本原样打印的，其中 `A(负荷) = 99.971%` 这个名字**是错的**：它算的是 `(8760 − 2.5) / 8760`，分母是**日历时间**，不是负荷时间。名字与实际口径不一致，正是本专题反复要防的那类缺陷，所以不加修饰地留着，作为反面样本。

**换到 200 台的真实场景，如果照样用 `8760` 当分母、名字还叫「负荷口径」，就会得到一个永远 99% 以上的漂亮数字**——而它计算的根本不是负荷时间。

修法只有一条：分母从配置里读（`shift_calendar` 表），不要写死在 SQL 里。
:::

## 六、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `EQX-A` | 七张表齐全，且外键开启 | `PRAGMA foreign_keys` = 1，表数为 7 |
| `EQX-B` | 五条自检全部为 0 | 逐条执行，输出 0 |
| `EQX-C` | 四条负向用例全部被拒 | 逐条执行，均报错 |
| `EQX-D` | 停机与工单可双向追溯 | `eq_downtime.wo_id` 有值且能 join |
| `EQX-E` | 可用率的分母来自配置，不硬编码 | SQL 中无字面量 `8760` |
| `EQX-F` | 未闭合停机可查且唯一 | 视图 + `ux_dt_open` |
| `EQX-G` | 备件领用与库存同步 | 领用后 `on_hand` 减少，且不为负 |
| `EQX-H` | 整条闭环可用一条脚本复跑 | 脚本退出码 0 |

## 七、验证方式

```shell
# 1) 建库后表数应为 7
sqlite3 /tmp/mnt.db "SELECT count(*) FROM sqlite_master WHERE type='table' AND name LIKE 'eq_%';"
# 期望：7

# 2) 外键必须开启（SQLite 默认是关的）
sqlite3 /tmp/mnt.db "PRAGMA foreign_keys;"
# 期望：1；若为 0，说明连接串少了参数或没执行 PRAGMA

# 3) 五条自检合并成一条，期望全 0
sqlite3 /tmp/mnt.db "
SELECT (SELECT count(*) FROM eq_wo w LEFT JOIN eq_asset a USING(asset_id) WHERE a.asset_id IS NULL) AS c1,
       (SELECT count(*) FROM eq_plan WHERE last_done_at IS NOT NULL AND next_due_at <= last_done_at) AS c2,
       (SELECT count(*) FROM eq_wo w WHERE w.wo_type='CORRECTIVE' AND w.state='CLOSED'
          AND NOT EXISTS(SELECT 1 FROM eq_downtime d WHERE d.wo_id=w.wo_id)) AS c3,
       (SELECT count(*) FROM (SELECT asset_id FROM eq_downtime WHERE end_at IS NULL GROUP BY 1 HAVING count(*)>1)) AS c4,
       (SELECT count(*) FROM eq_part WHERE on_hand < 0) AS c5;"
# 期望：0|0|0|0|0

# 4) 停机与工单的链路完整
sqlite3 /tmp/mnt.db "SELECT count(*) FROM eq_downtime WHERE wo_id IS NULL;"
# 期望：0（非计划停机必须挂工单）

# 5) 分母不硬编码：配置表应存在
sqlite3 /tmp/mnt.db "SELECT name FROM sqlite_master WHERE type='table' AND name='shift_calendar';"
# 期望：输出 shift_calendar；若无输出，EQX-E 未满足
```

::: warning 「能跑通」与「能验收」是两件事
这段闭环全部跑通，也只到「数据模型成立」。真正的验收还要回答：**换一个人按这份文档能不能重建一遍、结论是否一致**。所以每一项都给了可复制的命令与期望值——而不是「应该没问题」。
:::

## 参考资料

- [总览：七段链与三个「好了」](../Overview/index.md)：闭环覆盖了哪几段
- [停机口径、可用率与 OEE 分解](../Downtime/index.md)：分母配置的完整讨论
- [报修、工单状态机与停机登记](../WorkOrder/index.md)：状态机与去重键
- [备件、可修复件与安全库存](../SpareParts/index.md)：备件表的字段依据
- ISO 14224:2016 §9：维修数据的最小字段集（本文七表的字段来源）：<https://www.iso.org/standard/64076.html>
