# 备件、可修复件与安全库存

<p style="text-align:center;"><img src="../assets/em-logo.png" alt="设备维护与可靠性工程" style="zoom:75%;" /></p>

备件库最尴尬的一幕：货架上堆着三十万的件，停机时偏偏缺那一个三百块的密封圈。原因不是「买少了」，而是**备件的库存水平从来没有按停机代价算过**——它多半是按「上次缺过就多买点」的经验在漂移。

本页判据族 `EQP-A` ~ `EQP-H`，共 8 条，定义在第七节。

## 一、ABC：钱集中在少数 SKU 上

![备件的两条曲线：ABC 集中度与服务水平成本](../assets/em-parts.svg)

本机模拟 300 个备件 SKU（单价三档：5~50 / 200~2,000 / 5,000~60,000 元，年用量按帕累托分布）：

| 类别 | SKU 数 | 年耗用金额占比 | 管理方式 |
| --- | --- | --- | --- |
| A | **31** | 约 80% | 逐件定安全库存、月度盘点、双供应商 |
| B | **40** | 约 15% | 季度盘点、按服务水平补货 |
| C | **229** | 约 5% | 定量订货、年度盘点、允许缺货 |

::: tip ABC 只解决「先管谁」，不解决「备多少」
ABC 是按**金额**分类，而安全库存要按**缺货后果**定。一个 300 元的密封圈属于 C 类，但它一缺就停线 8 小时——它的库存水平应该按停机损失算，不是按金额算。

所以真正的分类是二维的：**金额 ABC × 关键性 ABC**。只有「金额 A + 关键性 A」才值得做精细的库存模型，其余用规则即可。
:::

## 二、安全库存：从「感觉」换成公式

```text
SS = z × σ_d × √L
```

- `z`：服务水平对应的标准正态分位数（90% → 1.28，95% → 1.65，99% → 2.33）
- `σ_d`：日需求的标准差
- `L`：采购提前期（天）

本机算例（关键件：日均需求 0.12 件、`σ_d = 0.4`、提前期 21 天、均价 18,000 元、持有率 22%、停机损失 4,200 元/h、每次缺件平均停 8 h）：

| 服务水平 | 安全库存 | 库存金额 | 年持有成本 | 年缺件损失 | 合计 |
| --- | --- | --- | --- | --- | --- |
| 80% | 1.54 件 | 73,075 元 | 16,077 元 | 294,336 元 | **310,413 元** |
| 90% | 2.35 件 | 87,593 元 | 19,270 元 | 147,168 元 | **166,438 元** |
| 95% | 3.02 件 | 99,801 元 | 21,956 元 | 73,584 元 | **95,540 元** |
| 99% | 4.27 件 | 122,237 元 | 26,892 元 | 14,717 元 | **41,609 元** |

这张表最反直觉的一行是最后一行：**服务水平从 95% 提到 99%，总成本反而再降 56%**。因为库存多花的 4,936 元，换来的是少停 58,867 元的机。

::: danger 什么时候不该按这张表算
1. **停机损失 < 持有成本** 时（便宜的 C 类件、不影响产出的备机），最优解是「允许缺货」，服务水平定在 60~80% 就够。
2. **提前期不可信** 时（进口件、单一供应商），`√L` 里的 `L` 是方差极大的随机变量，按点估计算出来的安全库存会系统性偏低——此时应改用「提前期分布」而不是「平均提前期」。
3. **件有保质期**（密封圈、油脂、电池）时，服务水平不能无限拉高，必须叠加「到期报废成本」。
:::

```sql
CREATE TABLE eq_part (
  part_id      TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  abc          TEXT NOT NULL CHECK (abc IN ('A','B','C')),
  criticality  TEXT NOT NULL CHECK (criticality IN ('A','B','C')),
  unit_price   REAL NOT NULL CHECK (unit_price >= 0),
  lead_time_d  INTEGER NOT NULL CHECK (lead_time_d >= 0),
  on_hand      INTEGER NOT NULL DEFAULT 0 CHECK (on_hand >= 0),
  safety_stock INTEGER NOT NULL DEFAULT 0 CHECK (safety_stock >= 0),
  reorder_pt   INTEGER NOT NULL DEFAULT 0,
  service_lvl  REAL NOT NULL DEFAULT 0.95 CHECK (service_lvl BETWEEN 0 AND 1),
  repairable   INTEGER NOT NULL DEFAULT 0 CHECK (repairable IN (0,1))
);
```

`criticality` 与 `abc` 分开存，就是为了让「金额 C、关键性 A」这一类能被单独筛出来——它们是备件管理里最容易被漏掉的一群。

## 三、可修复件：周转池怎么算

电机、伺服驱动、液压泵这类件坏了不报废，修好回库。它们的库存逻辑与消耗件完全不同：

| 项 | 消耗件 | 可修复件 |
| --- | --- | --- |
| 补充方式 | 采购 | 修复回库 |
| 关键参数 | 提前期 | **修复周期**（拆检 + 送修 + 返厂 + 验收） |
| 库存形态 | 单池 | **周转池**（在库 / 在修 / 在机 三态） |
| 缺件后果 | 等采购 | 等修复，通常更长 |

周转池的最小数量：

```text
N = ceil(修复周期 / 平均失效间隔) + 1（安全冗余）
```

举例（口径演示）：某型号伺服驱动 12 台在机、平均 18 个月坏一台、修复周期 45 天：

```text
N = ceil(45 / 540) + 1 = ceil(0.083) + 1 = 1 + 1 = 2
```

即备 2 台（1 台覆盖在修，1 台冗余）。如果修复周期涨到 120 天，`N` 仍是 2——因为瓶颈是「在修的那一台」，不是数量。真正需要加备件的是**同时坏两台**的概率，那要按泊松分布算，而不是线性外推。

## 四、呆滞：不是「没用到」，是「买错了」

本机读数：

| 指标 | 数值 |
| --- | --- |
| 全年零动支 SKU | **13 个**，账面占压 **117,239 元** |
| 高价低动支（年用 ≤ 1 且单价 > 1,000） | **15 个**，占压 **295,349 元 = 0.8%** |
| 备件即时满足率（A 95% / B 80% / C 60% 模拟） | **71.9%**（2,400 次需求缺 674 次） |

呆滞件通常有三个来源，处理方式完全不同：

| 来源 | 特征 | 处置 |
| --- | --- | --- |
| 设备已退役 | 关联设备 `RETIRED` | 直接报废或转售，别等「万一还用得上」 |
| 过量采购 | 一次买够三年 | 设 `max_level`，超过即停采 |
| 型号选错 | 装上不匹配 | 退货 / 改制，同时修采购规格书 |

::: warning 「零动支」不等于「可以清掉」
安全库存的本质是「为不发生的事付费」。一个件全年零动支，恰恰可能是它该在的证据。判断标准不是「用了没有」，而是「**它对应的设备是不是还在运行、缺了会不会停线**」。

正确做法：零动支 + 设备仍运行 + 关键性 A → **保留并复核服务水平**；零动支 + 设备已退役 → 清理。
:::

## 五、领用与退库：库存准确率的两个漏洞

| 动作 | 常见错法 | 后果 |
| --- | --- | --- |
| 领用 | 只记「领了一个」，不记挂哪张工单 | 备件成本无法归到设备/工单 |
| 领用 | 先领后补单，实际已装 | 库存与实物差一天 |
| 退库 | 修好不用了直接放回货架，不扫码 | 库存虚低，下次重复采购 |
| 以旧换新 | 旧件不回收 | 可修复件池永远是空的 |

```sql
CREATE TABLE eq_wo_part (
  wo_id   TEXT NOT NULL REFERENCES eq_wo(wo_id),
  part_id TEXT NOT NULL REFERENCES eq_part(part_id),
  qty     INTEGER NOT NULL CHECK (qty > 0),
  issued_at TEXT NOT NULL,
  returned_qty INTEGER NOT NULL DEFAULT 0 CHECK (returned_qty >= 0),
  core_returned INTEGER NOT NULL DEFAULT 0 CHECK (core_returned IN (0,1)),
  PRIMARY KEY (wo_id, part_id),
  CHECK (returned_qty <= qty)
);
```

`core_returned`（旧件是否回收）是一个常被忽略但极有价值的字段：可修复件的周转池能不能转起来，全靠它。

## 六、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `EQP-A` | 备件同时有金额 ABC 与关键性分级 | `abc` 与 `criticality` 两列 |
| `EQP-B` | 关键件（A 类）安全库存按服务水平算，有 `service_lvl` | 字段非空且 ∈ (0,1) |
| `EQP-C` | 库存不得为负 | `CHECK (on_hand >= 0)` |
| `EQP-D` | 领用必须挂工单 | `eq_wo_part.wo_id` 非空 |
| `EQP-E` | 可修复件有 `repairable` 标记与周转池数量 | 标记存在，且有在修数量 |
| `EQP-F` | 呆滞件可查询（零动支 + 设备状态） | 有 `v_idle_part` 视图 |
| `EQP-G` | 退库数量不超过领用数量 | `CHECK (returned_qty <= qty)` |
| `EQP-H` | 旧件回收状态可查 | `core_returned` 字段 |

## 七、验证方式

```shell
# 1) 库存不得为负：发料冲负应被拒
sqlite3 /tmp/mnt.db "UPDATE eq_part SET on_hand = on_hand - 99 WHERE part_id='SP-0001';"
# 期望：CHECK constraint failed: on_hand >= 0

# 2) 安全库存与服务水平必须同时存在
sqlite3 /tmp/mnt.db "SELECT count(*) FROM eq_part WHERE criticality='A' AND (service_lvl IS NULL OR safety_stock=0);"
# 期望：0（A 类备件不允许零安全库存）

# 3) 呆滞件清单（零动支且设备仍运行）
sqlite3 /tmp/mnt.db "SELECT p.part_id, p.name, p.unit_price FROM eq_part p
  WHERE p.on_hand > 0 AND NOT EXISTS (
    SELECT 1 FROM eq_wo_part wp WHERE wp.part_id = p.part_id
      AND wp.issued_at >= date('now','-365 day'));"
# 期望：一份短名单；逐条确认对应设备是否仍在运行

# 4) 退库不得超过领用
sqlite3 /tmp/mnt.db "UPDATE eq_wo_part SET returned_qty = qty + 1 WHERE wo_id='WO-1001';"
# 期望：CHECK constraint failed

# 5) 服务水平对应的成本（复算页面表格的第一行）
python3 - <<'PY'
import math
z, sd, L, price, hold, dc, hr = 0.84, 0.4, 21, 18000, 0.22, 4200, 8
ss = z*sd*math.sqrt(L); val = (0.12*L+ss)*price
loss = (1-0.80)*365*0.12*hr*dc
print(round(ss,2), round(val), round(val*hold), round(loss), round(val*hold+loss))
PY
# 期望：1.54 73075 16077 294336 310413
```

## 参考资料

- [报修、工单状态机与停机登记](../WorkOrder/index.md)：领用挂工单
- [停机口径、可用率与 OEE 分解](../Downtime/index.md)：缺件停机如何归因
- [维护策略与间隔：BM / PM / CBM / PdM](../Strategy/index.md)：BM 策略的前提是备件可得
- [仓储作业与波次拣选](../../WarehouseOps/Overview/index.md)：库内作业的通用方法
- [容量与成本](../../../Ops/CapacityCost/Overview/index.md)：停机损失的单小时成本口径
- ISO 55000:2024：资产全生命周期成本（LCC）与备件策略的关系：<https://committee.iso.org/TC251>
