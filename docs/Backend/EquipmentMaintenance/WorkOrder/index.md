# 报修、工单状态机与停机登记

<p style="text-align:center;"><img src="../assets/em-logo.png" alt="设备维护与可靠性工程" style="zoom:75%;" /></p>

工单系统里最贵的一张表不是工单表，是**停机表**。因为工单只证明「有人修过」，停机表才决定「可用率是多少、损失是多少、下次该改什么」。而多数系统把两者合成一张表，用一个 `status` 同时表达「修到哪一步」和「停了多久」——这两个问题的时间尺度完全不同。

本页判据族 `EQW-A` ~ `EQW-H`，共 8 条，定义在第七节。

## 一、六态状态机与两条不能走的路

![工单六态与两条不能走的路](../assets/em-wo.svg)

| 状态 | 含义 | 进入条件 | 允许去向 |
| --- | --- | --- | --- |
| `OPEN` | 已受理，未派工 | 报修或计划触发 | `ASSIGNED` / `CANCELLED` |
| `ASSIGNED` | 已派人 | 有 `assignee` | `WORKING` / `OPEN` / `CANCELLED` |
| `WORKING` | 已开工 | 有 `started_at` | `DONE` / `ASSIGNED` |
| `DONE` | 已完工 | 有 `finished_at` + 原因码 | `CLOSED` / `WORKING`（返工） |
| `CLOSED` | 已关单 | 成本归集完成 | **不可回退** |
| `CANCELLED` | 作废 | 误报 / 重复 | 不可回退 |

两条必须挡住的路：

1. **`CLOSED` → 任何状态**：关单意味着成本已经归集、时长已经入账。允许回退，历史报表就会在无人察觉的情况下变化。
2. **`DONE` → `OPEN`**：真要重开，必须新建工单并关联原单（`reopen_of`），而不是把旧单退回去——否则同一张单会出现两段 `started_at`，时长算不清。

```sql
CREATE TRIGGER trg_wo_no_reopen BEFORE UPDATE ON eq_wo
WHEN OLD.state = 'CLOSED' AND NEW.state != OLD.state
BEGIN SELECT RAISE(ABORT, 'closed work order is immutable'); END;
```

## 二、去重键：一个字段省掉 26% 的假工时

现场同一个故障会被上报多次：操作工报一次、班组长转发一次、维修在群里说一声又被录一次。本机模拟 1,200 次「真实故障」，加上 35% 的重复上报：

| 口径 | 工单数 | 说明 |
| --- | --- | --- |
| 不去重 | 1,623 | 每条上报一张单 |
| `(设备, 故障码, 15 分钟窗口)` 合并 | **1,199** | 合并 424 条 = **26.1%** |
| 若按「单均时长 × 单数」统计工时 | — | 虚增 **35.4%** |

::: danger 去重键不能只用「设备 + 时间」
只用时间窗，会把「同一台设备 10 分钟内出现的两个不同故障」错误合并（例如先漏油后跳闸）。去重键至少三段：**设备 + 故障码 + 时间窗**。

反过来，只用 `(设备, 故障码)` 也不行——同一台泵一个月漏两次油是两次事件，合并了就把 MTBF 算大了。
:::

```sql
ALTER TABLE eq_wo ADD COLUMN dedup_key TEXT;
CREATE UNIQUE INDEX ux_wo_dedup ON eq_wo(dedup_key);
-- 写入键：asset_id|fault_code|yyyymmddHHMM（分钟向下取整到 15 分钟）
```

用「唯一索引 + 冲突忽略」比「先查再插」可靠：并发上报时先查再插会双开单，而唯一索引在数据库层只能成功一次。

## 三、停机与工单：一对多，不是一对一

一次停机可能包含多段动作：等备件 3 小时、拆装 1.5 小时、试机 0.5 小时。把它们压成一条「停机 5 小时」也能用，但从此无法回答「其中多少小时是在等件」——而等件时长正是备件策略的输入。

| 建模方式 | 能回答 | 不能回答 |
| --- | --- | --- |
| 工单表加 `down_start` / `down_end` | 总停机 | 等件占多少、是否跨班 |
| 独立停机表，一对多 | 分段归因、跨班切分 | — |

```sql
CREATE TABLE eq_downtime (
  dt_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id   TEXT NOT NULL REFERENCES eq_asset(asset_id),
  wo_id      TEXT REFERENCES eq_wo(wo_id),
  cause      TEXT NOT NULL CHECK (cause IN ('MECH','ELEC','SETUP','WAIT','PLANNED','OTHER')),
  is_planned INTEGER NOT NULL DEFAULT 0 CHECK (is_planned IN (0,1)),
  start_at   TEXT NOT NULL,
  end_at     TEXT,
  open_flag  INTEGER GENERATED ALWAYS AS (CASE WHEN end_at IS NULL THEN 1 ELSE NULL END) VIRTUAL,
  CHECK (end_at IS NULL OR end_at > start_at)
);
-- 同一设备同时只允许一条未闭合停机
CREATE UNIQUE INDEX ux_dt_open ON eq_downtime(asset_id, open_flag);
```

`ux_dt_open` 这条**部分唯一索引**是全表最有价值的一行：它让「同一台设备两条未闭合停机」在数据库层不可能出现。没有它，两次误点「停机」就会永久污染并集计算。

::: tip 为什么用生成列而不是 `WHERE end_at IS NULL`
SQLite 的部分索引支持 `WHERE`，但跨库（MySQL 不支持部分索引）时要靠生成列 + 复合唯一键达到同样效果。生成列 `open_flag` 在「已闭合」时为 `NULL`，而 SQL 唯一索引允许多个 `NULL`——于是「已闭合可以有多条、未闭合只能有一条」这个语义被自然表达出来。
:::

## 四、优先级：关键性 × 影响，不是「谁喊得响」

| 优先级 | 判定 | 响应时限 | 修复时限 |
| --- | --- | --- | --- |
| P1 | A 类设备 + 已断线 | 15 min 到场 | 4 h 或启动应急预案 |
| P2 | A 类降载 / B 类断线 | 30 min | 8 h |
| P3 | B 类降载 / C 类断线 | 4 h | 24 h |
| P4 | C 类不影响产出 | 下一班 | 72 h |

优先级必须由系统按 `criticality` 与 `impact` 计算，不能让人手填——手填的优先级会和喊得响的人正相关。

```sql
UPDATE eq_wo SET priority = (
  SELECT CASE
    WHEN a.criticality='A' AND w.impact='LINE_STOP' THEN 'P1'
    WHEN a.criticality='A' OR  w.impact='LINE_STOP' THEN 'P2'
    WHEN a.criticality='B' THEN 'P3'
    ELSE 'P4' END
  FROM eq_asset a WHERE a.asset_id = eq_wo.asset_id)
WHERE state IN ('OPEN','ASSIGNED');
```

## 五、关单的五个条件

关单不是一个按钮，是一次校验。五个条件缺一不可：

| 条件 | 字段 | 缺了会怎样 |
| --- | --- | --- |
| 完工时刻 | `finished_at` | MTTR 算不出 |
| 故障码 | `fault_code` | 失效分布无法拟合 |
| 停机区间已闭合 | `eq_downtime.end_at` | 可用率永久偏低 |
| 备件领用已记 | `eq_wo_part` | 备件消耗与库存对不上 |
| 根因或处置说明 | `resolution` | 下次同样的故障从零开始查 |

```sql
-- C3 自检：已关闭的纠正工单必须有停机记录
SELECT count(*) FROM eq_wo w
WHERE w.wo_type = 'CORRECTIVE' AND w.state = 'CLOSED'
  AND NOT EXISTS (SELECT 1 FROM eq_downtime d WHERE d.wo_id = w.wo_id);
-- 期望：0
```

::: warning 「先修好，单子明天补」的代价
补单时 `started_at` 只能凭记忆填，而这个字段是所有时长指标的源头：

- MTTR 变成「记忆中的时长」，通常偏短（人记不住等待时间）；
- 停机区间变成「整点」，跨班归属失真（第 [停机口径](../Downtime/index.md) 页实测班次差异 13.8% / 27.6%）；
- 等件时长消失，备件策略失去输入。

如果现场确实无法实时录单，**至少要求录入真实起止时刻**（而不是录入时刻），并标记 `backfilled = 1`，让分析时能区分。
:::

## 六、响应时长与修复时长要分开

| 指标 | 起止 | 谁负责 | 典型改善手段 |
| --- | --- | --- | --- |
| 响应时长 | 报修 → 到场 | 调度 | 值班表、就近派工、备件预置 |
| 诊断时长 | 到场 → 定位原因 | 技术 | 故障树、历史相似案例 |
| 修复时长 | 定位 → 完工 | 班组 + 备件 | 备件可得性、专用工具 |
| MTTR | 报修 → 完工 | 全链路 | 上述三项之和 |

把四个数合成一个 MTTR 之后，最常见的误判是「MTTR 高 → 培训维修工」。本机 MTTR 56.9 min 的构成里，如果等件占了 40%，培训一点用都没有。

## 七、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `EQW-A` | 工单六态，且 `CLOSED` 不可回退 | 触发器存在，且状态枚举为 6 个 |
| `EQW-B` | `DONE`/`CLOSED` 必须有 `finished_at` | `CHECK` 约束 |
| `EQW-C` | 报修有去重键且唯一 | `ux_wo_dedup` 存在 |
| `EQW-D` | 同一设备不允许两条未闭合停机 | `ux_dt_open` 存在 |
| `EQW-E` | 已关闭的纠正工单必须有停机记录 | C3 自检 = 0 |
| `EQW-F` | 优先级由关键性与影响计算，非手填 | 有计算逻辑，字段不可直接编辑 |
| `EQW-G` | 补单标记 `backfilled`，可被分析时剔除 | 字段存在且停机关联 |
| `EQW-H` | 响应 / 诊断 / 修复三段时长可分别统计 | 各段有独立时间戳 |

## 八、验证方式

```shell
# 1) 关单后回退应被拒
sqlite3 /tmp/mnt.db "UPDATE eq_wo SET state='WORKING' WHERE wo_id='WO-1001';"
# 期望：closed work order is immutable

# 2) 同一设备第二条未闭合停机应被拒
sqlite3 /tmp/mnt.db "INSERT INTO eq_downtime(asset_id,cause,start_at) VALUES('EQ-001','ELEC','2026-11-02T12:00');"
# 期望：UNIQUE constraint failed: eq_downtime.asset_id, eq_downtime.open_flag

# 3) 已关闭纠正工单缺停机记录应为 0
sqlite3 /tmp/mnt.db "SELECT count(*) FROM eq_wo w WHERE w.wo_type='CORRECTIVE' AND w.state='CLOSED'
  AND NOT EXISTS(SELECT 1 FROM eq_downtime d WHERE d.wo_id=w.wo_id);"
# 期望：0

# 4) 去重效果：重复上报应被唯一索引挡住
sqlite3 /tmp/mnt.db "INSERT INTO eq_wo(wo_id,asset_id,source,wo_type,fault_code,state,dedup_key)
  VALUES('WO-1002','EQ-001','REPORT','CORRECTIVE','LEAK','OPEN','EQ-001|LEAK|202611020810');"
# 期望：UNIQUE constraint failed: eq_wo.dedup_key

# 5) MTTR 与响应时长的差（示例：若两者接近，说明等待时间没被记录）
sqlite3 /tmp/mnt.db "SELECT wo_id,
   ROUND((julianday(finished_at)-julianday(started_at))*1440,1) AS repair_min
   FROM eq_wo WHERE state='CLOSED';"
# 期望：一条记录；若无记录，说明停机没有挂上工单
```

## 参考资料

- [停机口径、可用率与 OEE 分解](../Downtime/index.md)：停机区间如何汇总
- [备件、可修复件与安全库存](../SpareParts/index.md)：等件时长的来源
- [点检、状态监测与阈值](../Inspection/index.md)：NG 之后如何触发工单
- [工作流引擎](../../WorkflowEngine/Overview/index.md)：审批流与状态机的分工
- EN 13306:2017《维护 — 维护术语》：纠正性维护与预防性维护的界定
- ISO 14224:2016 §9：维修数据的最小字段集（含停机起止与原因分类）：<https://www.iso.org/standard/64076.html>
