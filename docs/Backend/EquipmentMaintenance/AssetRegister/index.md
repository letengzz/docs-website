# 设备台账、功能位置与关键性分级

<p style="text-align:center;"><img src="../assets/em-logo.png" alt="设备维护与可靠性工程" style="zoom:75%;" /></p>

台账最常见的做法是拉一张 Excel：一列设备名、一列型号、一列位置。它能把「有多少台设备」数清楚，却回答不了维护真正要问的三个问题：**这条产线一年停了多少小时、这台机器的停机该记在谁头上、换了一台新机器之后历史数据还在不在原位**。

本页判据族 `EQA-A` ~ `EQA-H`，共 8 条，定义在第七节。

## 一、两个号不能合成一个号

![功能位置 → 设备 → 部件：三层各有各的号](../assets/em-asset.svg)

设备管理里最值钱的一条建模决定，是把「**装在哪**」和「**是哪台**」分成两个编号：

| 编号 | 回答的问题 | 什么时候变 | 举例 |
| --- | --- | --- | --- |
| 功能位置号 | 这个位置是干什么的 | 工艺改造才变 | `PLANT1/LINE2/INJ`（二号产线注塑工位） |
| 设备号 | 这是哪一台机器 | 换机器才变 | `EQ-001`（注塑机 A，2023 年购入） |
| 资产号 | 这台机器在财务账上是哪一项 | 资本化 / 转移才变 | `FA-2023-0417` |
| 部件号 | 这台机器上的哪个可换件 | 换件才变 | `EQ-001/PUMP-01` |

四个号各管一段，混用会立刻出问题：

- **只有位置号**：换了一台新机器，历史停机全部跟着旧机器走丢——新机器「看起来从没坏过」。
- **只有设备号**：想知道「二号产线一年停了多少」，得手工把七台设备的数加一遍，且每次产线调整都要重算。
- **设备号 = 资产号**：一次大修换了主电机（资本化），财务要拆资产，维护侧却不想换设备号，两边从此对不上。

::: tip 一句话记住
**位置是「坑」，设备是「萝卜」。** 坑不动，萝卜会换。停机要记在萝卜上，汇总要落在坑上。
:::

## 二、三层结构：位置树、设备、部件

```sql
CREATE TABLE eq_asset (
  asset_id     TEXT PRIMARY KEY,           -- 设备号，如 EQ-001
  name         TEXT NOT NULL,
  func_loc     TEXT NOT NULL,              -- 功能位置号，如 PLANT1/LINE2/INJ
  parent_id    TEXT REFERENCES eq_asset(asset_id),  -- 上位设备（部件挂在设备下）
  criticality  TEXT NOT NULL CHECK (criticality IN ('A','B','C')),
  status       TEXT NOT NULL DEFAULT 'RUNNING'
                 CHECK (status IN ('RUNNING','DOWN','MAINT','RETIRED')),
  asset_no     TEXT,                       -- 财务资产号，可空（C 类常常不建卡）
  installed_at TEXT,
  retired_at   TEXT,
  CHECK (retired_at IS NULL OR installed_at IS NULL OR retired_at > installed_at)
);
CREATE INDEX ix_asset_loc ON eq_asset(func_loc);
CREATE INDEX ix_asset_parent ON eq_asset(parent_id);
```

三层各自的职责：

| 层 | 存什么 | 不存什么 | 谁维护 |
| --- | --- | --- | --- |
| 功能位置 | 层级、工艺归属、产能 | 设备型号、购置日期 | 工艺 / 生产 |
| 设备 | 型号、铭牌参数、关键性、状态 | 财务原值、折旧 | 设备科 |
| 部件 | 可换件的寿命、上次更换时间 | 独立资产卡（除非单独资本化） | 维修班组 |

::: danger 三个常见建模错误
1. **把部件建成独立设备**：一个轴承也开一条 `eq_asset`，结果「设备总数」从 200 涨到 3,000，可用率分母直接失真。部件只在需要**单独记寿命或单独备件**时才建。
2. **用 `func_loc` 字符串做层级判断**：`LIKE 'PLANT1/LINE2%'` 在位置改名（`LINE2` → `LINE-B`）时全线失效。层级必须落在 `parent_id` 或独立的 `func_loc` 表上。
3. **状态字段与工单状态联动写死**：设备停在 `DOWN` 只能由「未闭合停机」推导，不能由人手工设——手工设的状态一定会忘记改回来。
:::

## 三、停机记在设备上，汇总落在位置上

这是本页最核心的一条：**明细记在最细的层，报表沿着树向上卷**。

```sql
-- 沿 parent_id 向上汇总某台设备及其所有子设备的停机小时
WITH RECURSIVE subtree(id) AS (
  SELECT asset_id FROM eq_asset WHERE asset_id = :root
  UNION ALL
  SELECT a.asset_id FROM eq_asset a JOIN subtree s ON a.parent_id = s.id
)
SELECT ROUND(sum((julianday(d.end_at) - julianday(d.start_at)) * 24), 2) AS down_h
FROM eq_downtime d JOIN subtree s ON d.asset_id = s.id
WHERE d.end_at IS NOT NULL;
```

反过来，只按父设备汇总会漏掉大量停机。一个口径演示（非实测，用来说明量级）：

| 汇总方式 | 算到的停机 | 说明 |
| --- | --- | --- |
| 只统计主机 `EQ-001` | 150 min | 主机本体故障 |
| 统计主机 + 6 台辅机（子树） | 610 min | 加上传送带、冷却泵、上料机 |
| 差额 | **460 min = 75.4%** | 全部落在「辅机不算产线停机」的口径漏洞里 |

::: warning 停机归属的三个层次要想清楚
- **设备层**：这条停机发生在哪台设备上（唯一、必须）。
- **产线层**：这条停机是否造成整线停（可以是「否」——辅机坏了但主机还能跑）。
- **订单层**：这条停机是否延误了某张工单（交给 [生产执行](../../Manufacturing/Overview/index.md) 判）。

三层不能用一个字段表达。常见做法是：`eq_downtime.asset_id` 必填，`eq_downtime.impact` 取 `LINE_STOP` / `CAPACITY_LOSS` / `NONE`，订单影响由生产侧关联。
:::

## 四、关键性分级：按后果，不按价格

关键性分级决定后面所有的资源分配——A 类才做状态监测、才配冗余、才备关键件。分级最容易犯的错是「按设备价格分」，而价格与停机代价基本无关：一台 8 万元的冷却泵停线，损失远大于一台 200 万元的备用加工中心闲置。

四个维度打分，取最高档而不是平均分（**短板决定关键性**）：

| 维度 | 问题 | A 级 | B 级 | C 级 |
| --- | --- | --- | --- | --- |
| 安全 / 环境 | 失效会不会伤人、超标排放 | 有可能 | 有轻微风险 | 无 |
| 交付 | 停了能不能在 4 小时内恢复产出 | 不能，且断线 | 可切换或缓冲 | 有替代 |
| 质量 | 失效会不会造成批量不良 | 会，且不可拦截 | 会，可拦截 | 不会 |
| 成本 | 单次停机损失（元/小时） | > 2 万 | 2 千 ~ 2 万 | < 2 千 |

```sql
CREATE TABLE eq_criticality (
  asset_id   TEXT PRIMARY KEY REFERENCES eq_asset(asset_id),
  safety     TEXT NOT NULL CHECK (safety IN ('A','B','C')),
  delivery   TEXT NOT NULL CHECK (delivery IN ('A','B','C')),
  quality    TEXT NOT NULL CHECK (quality IN ('A','B','C')),
  cost       TEXT NOT NULL CHECK (cost IN ('A','B','C')),
  level      TEXT NOT NULL CHECK (level IN ('A','B','C')),
  reason     TEXT NOT NULL,
  reviewed_at TEXT NOT NULL,
  -- 短板定级：任一项为 A 即 A，否则任一项为 B 即 B
  CHECK ( level = CASE
            WHEN 'A' IN (safety, delivery, quality, cost) THEN 'A'
            WHEN 'B' IN (safety, delivery, quality, cost) THEN 'B'
            ELSE 'C' END )
);
```

`CHECK` 里用 `IN` 做「任一为 A」的判定在 SQLite 里可行；PostgreSQL 需改成 `safety='A' OR delivery='A' OR ...`。这条约束的价值是：**分级不能靠人记得按短板取**。

::: danger 分错级的两个方向，代价不对称
1. **C 类按 A 类养**：多花维护费。振动监测、冗余、关键备件全套上，一年多花几十万——**可承受**。
2. **A 类按 C 类养**：坏了再修。省下的维护费在一次停线里全部吐回去，而且往往伴随交付违约——**不可承受**。

所以分级存疑时一律往上取一档，并写下 `reason`：半年后回看，理由比分数有用。
:::

## 五、设备号与资产号：四个号的对齐表

| 场景 | 位置号 | 设备号 | 资产号 | 部件号 |
| --- | --- | --- | --- | --- |
| 新设备安装 | 不变 | 新建 | 财务建卡 | 按需建 |
| 同型号换机（旧机报废） | 不变 | **新建**（旧机置 `RETIRED`） | 旧卡清理、新卡建立 | 随新机重建 |
| 设备搬到另一条线 | 不变（旧位置腾空） | 不变 | 不变 | 不变 |
| 大修更换主电机（资本化） | 不变 | 不变 | **拆分**（原值部分转出） | 电机作为部件记寿命 |
| 部件更换（非资本化） | 不变 | 不变 | 不变 | 换件、记上次更换时间 |

::: tip 「换机新建号」这条要写进制度
同型号换机时图省事沿用旧设备号，会让新机器的 MTBF 从一开始就被旧机器的失效历史污染——历史越长，新机看起来越不可靠。**判断标准是「这台物理实体是不是同一个」**，不是「型号是否相同」。
:::

## 六、状态字段的正确用法

| 状态 | 谁能写 | 依据 |
| --- | --- | --- |
| `RUNNING` | 系统推导 | 无未闭合停机、无进行中工单 |
| `DOWN` | 系统推导 | 存在 `end_at IS NULL` 的停机记录 |
| `MAINT` | 系统推导 | 存在 `state IN ('WORKING')` 的计划工单 |
| `RETIRED` | 人工 + 审批 | 有退役单，且无未闭合工单 |

```sql
-- 设备状态视图：不从字段读，从事实推导
CREATE VIEW v_asset_status AS
SELECT a.asset_id,
       CASE
         WHEN a.retired_at IS NOT NULL THEN 'RETIRED'
         WHEN EXISTS (SELECT 1 FROM eq_downtime d
                       WHERE d.asset_id = a.asset_id AND d.end_at IS NULL) THEN 'DOWN'
         WHEN EXISTS (SELECT 1 FROM eq_wo w
                       WHERE w.asset_id = a.asset_id AND w.state = 'WORKING') THEN 'MAINT'
         ELSE 'RUNNING'
       END AS status
FROM eq_asset a;
```

## 七、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `EQA-A` | 位置号与设备号是两个字段，不是同一个 | `eq_asset` 同时有 `func_loc` 与 `asset_id` |
| `EQA-B` | 位置层级可用递归查询向上汇总 | 存在 `parent_id` 且能跑通递归 CTE |
| `EQA-C` | 部件不建独立资产卡（除非单独资本化） | 部件行 `asset_no IS NULL` 或有明确资本化理由 |
| `EQA-D` | 关键性分级取短板，且有 `reason` | `CHECK` 约束 + `reason` 非空 |
| `EQA-E` | A 类设备必须有冗余或状态监测之一 | A 类设备在 `eq_plan` 中有 `CBM`/`PdM` 或标记冗余 |
| `EQA-F` | 设备状态由事实推导，不手工设 | 状态来自视图或触发器，无人工直写接口 |
| `EQA-G` | 换机新建设备号，旧号置 `RETIRED` 而非删除 | 退役设备仍在表中且 `retired_at` 非空 |
| `EQA-H` | 停机明细挂设备，报表可按位置汇总 | `eq_downtime.asset_id` 必填，且能 join 到 `func_loc` |

## 八、验证方式

```shell
# 1) 位置树能向上汇总（应有结果，且大于单台设备）
sqlite3 /tmp/mnt.db "WITH RECURSIVE sub(id) AS (
    SELECT 'EQ-001' UNION ALL SELECT a.asset_id FROM eq_asset a JOIN sub s ON a.parent_id=s.id)
  SELECT count(*) FROM sub;"
# 期望：≥ 2（主机 + 至少一台辅机）

# 2) 不存在既无位置号又无设备号的孤儿记录
sqlite3 /tmp/mnt.db "SELECT count(*) FROM eq_asset WHERE func_loc IS NULL OR func_loc='';"
# 期望：0

# 3) 关键性短板约束生效：给一台 C 类设备塞一个 A 项应被拒
sqlite3 /tmp/mnt.db "UPDATE eq_criticality SET safety='A' WHERE level='C';"
# 期望：CHECK constraint failed（level 必须同步变 A）

# 4) 退役设备仍可查（不是物理删除）
sqlite3 /tmp/mnt.db "SELECT count(*) FROM eq_asset WHERE retired_at IS NOT NULL;"
# 期望：≥ 0，且历史停机仍能 join 到该设备

# 5) 状态视图与未闭合停机一致
sqlite3 /tmp/mnt.db "SELECT count(*) FROM v_asset_status WHERE status='DOWN'
                      AND asset_id NOT IN (SELECT asset_id FROM eq_downtime WHERE end_at IS NULL);"
# 期望：0
```

## 参考资料

- [维护策略与间隔：BM / PM / CBM / PdM](../Strategy/index.md)：分级之后怎么选策略
- [停机口径、可用率与 OEE 分解](../Downtime/index.md)：位置树如何影响汇总口径
- [资产台账与折旧摊销](../../FixedAsset/AssetCard/index.md)：同一个「萝卜」在财务侧的建模
- [主数据与标准](../../../DB/DataGovernance/StandardsMasterData/index.md)：编码规则的通用治理
- ISO 55000:2024《资产管理 — 词汇、概览与原则》：资产、资产体系与生命周期价值的定义：<https://committee.iso.org/TC251>
- ISO 14224:2016 附录 A：设备分类层级（设备类别 / 设备单元 / 子单元）与本文三层结构的对应关系：<https://www.iso.org/standard/64076.html>
