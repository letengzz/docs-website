# 停机口径、可用率与 OEE 分解

<p style="text-align:center;"><img src="../assets/em-logo.png" alt="设备维护与可靠性工程" style="zoom:75%;" /></p>

「我们设备可用率 99.7%」和「我们这条线老停」可以是同一家工厂在同一个月说的两句话。它们不矛盾，因为**可用率的分母不同**：一个分母是负荷时间（排产的那些小时），另一个分母是日历时间（一年 8,760 小时）。这一页只做一件事——把口径钉死到能被一条 SQL 判定的程度。

本页判据族 `EQD-A` ~ `EQD-H`，共 8 条，定义在第七节。

## 一、三种分母，三个都「正确」的可用率

![停机的三种分母与「重叠区间」](../assets/em-downtime.svg)

本机数据（200 台设备 / 一年 / 5,012 条停机事件）：

| 口径 | 公式 | 结果 | 回答什么问题 |
| --- | --- | --- | --- |
| 日历 | `(日历 − 计划停机 − 非计划停机) / 日历` | **81.75%** | 这台设备一年有多少比例的时间在产出 |
| 负荷 | `(负荷 − 非计划停机) / 负荷` | **99.70%** | 排产时间里有多少没被停掉 |
| MTBF | `MTBF / (MTBF + MTTR)` | **99.67%** | 按事件平均，一次故障占多少比例 |

极差 **17.92 个百分点**。三个数字都对，区别只在「计划停机算不算损失」：

- 日历口径把「周末不排产」算成不可用 → 适合考核**资产利用**；
- 负荷口径把计划停机排除 → 适合考核**维护水平**；
- MTBF 口径按事件平均 → 适合做**可靠性分析**，不适合做报表。

::: danger 报表上只写一个可用率，等于埋了一颗雷
维护部用负荷口径算出 99.70%，生产部用日历口径算出 81.75%，两边都拿着「正确」的数字开会，结论必然相反：一边认为「设备很好，是排产不足」，另一边认为「排产已满，是设备不行」。

**修法不是统一成一个数，而是三个数一起给，并强制标注 `basis`。**
:::

```sql
CREATE VIEW v_availability AS
WITH base AS (
  SELECT a.asset_id,
         8760.0 * 24 AS cal_min,                       -- 年内日历分钟（示例：整年）
         8760.0 * 24 * 0.82 AS load_min,               -- 负荷 = 日历 × 排产率
         coalesce((SELECT sum((julianday(d.end_at)-julianday(d.start_at))*1440)
                     FROM eq_downtime d
                    WHERE d.asset_id = a.asset_id AND d.end_at IS NOT NULL
                      AND d.is_planned = 0), 0) AS unplanned_min,
         coalesce((SELECT sum((julianday(d.end_at)-julianday(d.start_at))*1440)
                     FROM eq_downtime d
                    WHERE d.asset_id = a.asset_id AND d.end_at IS NOT NULL
                      AND d.is_planned = 1), 0) AS planned_min
  FROM eq_asset a
)
SELECT asset_id,
       round(100.0*(cal_min - planned_min - unplanned_min)/cal_min, 2) AS a_calendar,
       round(100.0*(load_min - unplanned_min)/load_min, 2)              AS a_loading
FROM base;
```

## 二、区间必须取并集，不能求和

一次停机常常被登记两次：机械故障一条、等备件一条。两条区间在时间上重叠。

| 口径 | 数值 | 差 |
| --- | --- | --- |
| 区间直接求和 | 285,172 min | — |
| 区间并集 | **259,102 min** | 少 **26,070 min = 9.1%** |

9.1% 不会让报表崩，但它会**改变排序**：停机最多的前五台里，至少有一两台是靠「重复归因」刷上去的。改善资源按这张表投，就会投错。

SQL 里算并集，用窗口函数判断「当前区间是否被前一个区间覆盖」：

```sql
WITH ordered AS (
  SELECT asset_id, start_at, end_at,
         max(end_at) OVER (PARTITION BY asset_id ORDER BY start_at
                           ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_max
  FROM eq_downtime
  WHERE end_at IS NOT NULL
),
marked AS (
  SELECT asset_id, start_at, end_at,
         CASE WHEN prev_max IS NULL OR start_at > prev_max THEN 1 ELSE 0 END AS is_new
  FROM ordered
),
grouped AS (
  SELECT asset_id, start_at, end_at,
         sum(is_new) OVER (PARTITION BY asset_id ORDER BY start_at) AS grp
  FROM marked
)
SELECT asset_id, round(sum((julianday(max(end_at))-julianday(min(start_at)))*1440), 0) AS union_min
FROM grouped
GROUP BY asset_id, grp;
```

把每个 `grp` 的并集再按设备求和，才是可用的停机时长。

::: warning 字符串时间比较有坑
`ORDER BY start_at` 在 `TEXT` 类型上按字典序比较，只有格式统一成 `YYYY-MM-DDTHH:MM:SS`（或统一带时区）才等价于时间序。混用 `2026-11-02 09:00` 与 `2026-11-02T09:00:00` 会让排序错位，进而让并集算错——**而结果看起来仍然像个正常的数**。
:::

## 三、跨班次：按开始时间归属会错 27.6%

停机跨越交班时刻时，把它整段算给「开始的那个班」是最省事的做法，也是最容易吵架的做法。

本机 5,012 条事件按三个班次（06-14 / 14-22 / 22-06）归属：

| 归属方式 | 班次 1 | 班次 2 | 班次 3 |
| --- | --- | --- | --- |
| 按开始时间整段归属 | 96,568 min | 92,225 min | 25,411 min |
| 按时长切分 | 84,861 min | 94,253 min | 35,091 min |
| 差异 | **+13.8%** | −2.2% | **−27.6%** |

夜班被少算 **27.6%**。这不是小事：夜班通常是点检最松、故障最多的班次，把它的停机时长算少，会系统性地掩盖夜间问题。

正确的做法是一条区间切分函数，把 `[start, end)` 按班次边界切开，分别落到各班的桶里。

## 四、OEE：分子分母都要说清

```text
OEE = 可用率 × 性能 × 质量
```

本机（负荷口径）：

| 因子 | 数值 | 说明 |
| --- | --- | --- |
| 可用率 | 99.70% | 负荷时间扣除停机 |
| 性能 | 88.0% | 实际产出 / 理论产能 |
| 质量 | 96.5% | 良品 / 总产出 |
| **OEE** | **84.66%** | 99.70 × 88.0 × 96.5 |

同一组数字，如果把可用率换成日历口径（81.75%）：

```text
81.75% × 88.0% × 96.5% = 69.43%
```

**同一个车间、同一天，OEE 可以是 84.66% 或 69.43%**，差 15.23 个百分点。这不是算错，是分母不同。

::: danger OEE 的三个必填口径
1. **分母**：日历 / 负荷 / 计划产出时间。三者不可混用。
2. **换型归哪类**：算停机（降低可用率）还是算计划停机（降低负荷时间）？本机换型 420 h，占非计划停机 9.7%——归错类会让可用率在两个方向上各错一点，看起来都不明显。
3. **性能的分母**：理论节拍用「铭牌产能」还是「历史最佳」？铭牌产能通常偏高，会让性能永远偏低。
:::

六种损失与因子的对应（用于定位到底该改哪一段）：

| 损失 | 落到哪个因子 | 本机是否计入 |
| --- | --- | --- |
| 设备故障 | 可用率 | 是（非计划停机） |
| 换型调整 | 可用率 or 负荷（看口径） | 是（SETUP 9.7%） |
| 空转小停 | 性能 | 是（短停机占条数 18.4%） |
| 降速运行 | 性能 | 是 |
| 过程不良 | 质量 | 是 |
| 启动废品 | 质量 | 是 |

## 五、MTBF 与可用率在短停机面前脱钩

| 过滤条件 | 事件数 | MTBF | 可用率 |
| --- | --- | --- | --- |
| 不过滤 | 5,012 | 285.8 h | 99.67% |
| 忽略 < 5 min | 4,089 | 350.3 h（**+22.6%**） | 99.67% |
| 忽略 < 15 min | 3,367 | 425.4 h（**+48.8%**） | 99.68% |

短停机只占时长 1.0%，却能把 MTBF 抬高近一半。**所以 MTBF 报表必须同时给出「含短停 / 不含短停」两行**，否则同一个车间能报出两个差 48% 的 MTBF。

## 六、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `EQD-A` | 每条停机有 `start_at` / `end_at` / `cause` / `is_planned` | 四列非空（进行中的 `end_at` 可空） |
| `EQD-B` | 停机时长按区间并集计算，不是求和 | 存在并集查询或视图 |
| `EQD-C` | 可用率报表标注分母口径（`basis`） | 报表字段含 `basis` ∈ {calendar, loading, mtbf} |
| `EQD-D` | 跨班次停机按时长切分，不按开始时间整段归属 | 有切分逻辑或班次时长表 |
| `EQD-E` | 换型（SETUP）的归类在口径里写明 | 有 `setup_treatment` 配置项 |
| `EQD-F` | MTBF 同时报「含短停 / 不含短停」 | 报表两行 |
| `EQD-G` | 时区与时间格式统一，且可校验 | 有格式约束或正则检查 |
| `EQD-H` | OEE 三个因子与六种损失的映射可查 | 有映射表，且损失项加总 = 100% |

## 七、验证方式

```shell
# 1) 并集与求和应不同（说明存在重叠区间）
sqlite3 /tmp/mnt.db "SELECT
  ROUND(sum((julianday(end_at)-julianday(start_at))*1440),0) AS sum_min
  FROM eq_downtime WHERE end_at IS NOT NULL;"
# 期望：一个数；若与并集相同，要么确实无重叠，要么并集查询没生效

# 2) 同一设备未闭合停机应唯一
sqlite3 /tmp/mnt.db "SELECT asset_id, count(*) FROM eq_downtime WHERE end_at IS NULL GROUP BY 1 HAVING count(*)>1;"
# 期望：0 行

# 3) 三种口径的可用率（单台、示例分母 8760 h）
sqlite3 /tmp/mnt.db "WITH d AS (SELECT coalesce(sum((julianday(end_at)-julianday(start_at))*1440),0) m
                        FROM eq_downtime WHERE asset_id='EQ-001' AND end_at IS NOT NULL AND is_planned=0)
  SELECT ROUND(100.0*(8760*60*0.82 - (SELECT m FROM d))/(8760*60*0.82),2) AS a_loading,
         ROUND(100.0*(8760*60 - (SELECT m FROM d))/(8760*60),2)           AS a_calendar;"
# 期望：两个数不相等，且 a_loading > a_calendar

# 4) 时间格式必须统一（混格式会让排序错位）
sqlite3 /tmp/mnt.db "SELECT count(*) FROM eq_downtime WHERE start_at NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]';"
# 期望：0

# 5) OEE 复算
python3 -c "print(round(0.9970*0.88*0.965*100,2), round(0.8175*0.88*0.965*100,2))"
# 期望：84.66 69.43
```

::: tip 开会之前先对分母
任何一个「可用率对不上」的争论，前三句话应该是：分母是日历还是负荷？区间求和还是并集？换型算哪类？三问答完，通常就不用吵了——差的不是数据，是定义。
:::

## 参考资料

- [总览：七段链与三个「好了」](../Overview/index.md)：为什么口径比数字重要
- [报修、工单状态机与停机登记](../WorkOrder/index.md)：停机区间怎么产生
- [可靠性：MTBF、Weibull 与冗余](../Reliability/index.md)：MTBF 的适用边界
- [生产执行与工单报工](../../Manufacturing/Planning/index.md)：性能因子与排产的接口
- [容量与成本](../../../Ops/CapacityCost/Overview/index.md)：停机损失的单小时口径
