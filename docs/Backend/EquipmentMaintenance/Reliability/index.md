# 可靠性：MTBF、Weibull 与冗余

<p style="text-align:center;"><img src="../assets/em-logo.png" alt="设备维护与可靠性工程" style="zoom:75%;" /></p>

维护报表里最常见的两个数——MTBF 与可用率——经常被当成同一件事。它们不是：**MTBF 说的是「多久坏一次」，可用率说的是「有多少时间能用」**。一台设备可以 MTBF 很长（很少坏），但每次坏都要修三天（可用率很低）；也可以 MTBF 很短（老坏），但每次十分钟换好（可用率很高）。改善方向完全相反。

本页判据族 `EQR-A` ~ `EQR-H`，共 8 条，定义在第七节。

## 一、四个指标的定义与适用边界

| 指标 | 定义 | 适用 | 不适用 |
| --- | --- | --- | --- |
| MTTF | 平均失效前时间（不可修件） | 备件、密封圈、电子模块 | 可修设备 |
| MTBF | 平均故障间隔（可修设备） | 可修设备 | 一次性件 |
| MTTR | 平均修复时间（含等待） | 维修组织效率 | 单看会掩盖等件 |
| 可用度 A | 可工作 / 应工作 | 产能与交付 | 口径必须写清（见上一页） |

四个指标的关系：

```text
MTBF = 运行时间 / 失效次数
MTTR = 停机时间 / 修复次数
A    = MTBF / (MTBF + MTTR)          ← 仅稳态、单台、可修
```

本机读数：5,012 条事件、运行时间 85,939,298 min：

| 指标 | 数值 |
| --- | --- |
| MTTR | **56.9 min** |
| MTBF | **285.8 h**（17,147 min） |
| A（MTBF 口径） | **99.67%** |

::: danger MTBF 的三个陷阱
1. **短停机被过滤**：剔除 `< 5 min` 的事件后 MTBF 从 285.8 h 涨到 350.3 h（**+22.6%**），而可用率几乎不变。报 MTBF 必须说明是否含短停。
2. **把「运行时间」当成日历时间**：设备闲置的时间不该进分母，否则 MTBF 被人为拉长。
3. **多台设备混算**：把 200 台的失效次数加总、除以总运行时间，得到的是「车队平均」，不能代表任何一台。
:::

## 二、Weibull：β 决定策略，η 决定量级

![可靠性：β 决定策略，冗余买不到共因](../assets/em-reliability.svg)

Weibull 分布的两个参数：

- **β（形状）**：失效随时间的变化趋势。`β < 1` 早期失效、`β ≈ 1` 随机、`β > 1` 磨损。
- **η（尺度）**：特征寿命，`t = η` 时可靠度降到 `e⁻¹ ≈ 36.8%`。

```text
R(t) = exp(−(t/η)^β)
F(t) = 1 − exp(−(t/η)^β)
λ(t) = (β/η) · (t/η)^(β−1)
```

`β = 2.2`、`η = 900 h` 时，`R(900) = e⁻¹ = 36.8%`——也就是说 **900 小时的时候，这批件里只有三分之一还活着**。这个数与「平均寿命」不是一回事：平均寿命 `η·Γ(1+1/β) ≈ 900 × 0.886 ≈ 797 h`。

参数估计用中位秩 + 最小二乘（可复跑）：

```python
import math, random

def fit_beta(xs):
    xs = sorted(xs)
    n = len(xs)
    sx = sy = sxx = sxy = 0.0
    for i, x in enumerate(xs, 1):
        F = (i - 0.3) / (n + 0.4)          # 中位秩
        y = math.log(-math.log(1 - F))
        xx = math.log(x)
        sx += xx; sy += y; sxx += xx * xx; sxy += xx * y
    return (n * sxy - sx * sy) / (n * sxx - sx * sx)

random.seed(7)
sample = lambda n: [900 * (-math.log(1 - random.random())) ** (1 / 2.2) for _ in range(n)]
for n in (10, 30, 100, 400):
    print(n, round(fit_beta(sample(n)), 2))
# 期望：随样本量增大，估计值逐步收敛到 2.2 附近
```

## 三、β 的估计必须带样本量

同一批真值 `β = 2.2` 的数据，不同样本量下估计的稳定性差别巨大：

| 样本量 | β 估计中位数 | 90% 区间 | 能不能下结论 |
| --- | --- | --- | --- |
| 10 件 | 2.04 | **[1.23, 3.25]** | **不能**——区间跨过 1，可能该做 PM，也可能完全不该做 |
| 30 件 | 2.09 | [1.56, 2.82] | 勉强，能判断 β > 1 |
| 100 件 | 2.16 | [1.82, 2.54] | 可以 |
| 400 件 | 2.18 | [1.99, 2.37] | 稳定 |

::: danger 「10 个样本算出 β=2.0，所以做定期更换」是错的
样本量 10 时，`β` 的 90% 区间是 `[1.23, 3.25]`。区间下界 1.23 仍大于 1，看似支持 PM——但你要意识到：**这个区间是假设「样本独立同分布」算出来的下界**，真实工程数据里还混着批次差异、安装质量、工况差异，实际不确定性更大。

工程上的做法是：**样本 < 30 时不做 β 结论，改用厂家建议或行业基准**，并把「样本累积中」写进计划备注。
:::

## 四、删失数据：没坏的样本不能扔

统计失效分布时，最容易犯的错误是只统计「已经坏了的件」。正在运行、还没坏的件被丢掉，会让 β 被系统性高估（因为长寿命样本消失了）。

| 数据类型 | 含义 | 处理 |
| --- | --- | --- |
| 完整失效 | 观察到从投用到失效 | 直接进拟合 |
| 右删失 | 到统计日仍在运行 | 只知道寿命 > 已运行时间，必须进似然 |
| 左删失 | 投用前就已老化（库存件） | 单独标注，或从投用时刻起算 |
| 区间删失 | 只知道在两次点检之间坏了 | 用区间中值或区间似然 |

用中位秩法时，删失样本要按「有效样本数」修正；用最大似然（MLE）时直接进似然函数。**简化做法（可接受）**：只对完整失效拟合，但必须在报告里写明「样本 n = X，另有 Y 个右删失未计入」——让读者知道这个 β 是偏高的。

## 五、系统可用度：单台 99.7%，整线只有 96.5%

可用度不会「平均」，它按结构**级联**：

| 结构 | 公式 | 数值 |
| --- | --- | --- |
| 串联（12 台各 99.70%） | `0.997^12` | **96.46%** |
| 并联（2 台各 99.70%，独立） | `1 − (1−0.997)²` | **99.9991%** |
| 并联（计共因 2%） | `1 − [p²(1−c) + c·p]`，`p = 0.003` | **99.9931%** |

这就是为什么「我们每台设备可用率 99.7%」和「这条线一个月停两次」可以同时成立：**12 台串联，整线只剩 96.46%**。

::: warning 冗余只对「独立失效」有效
单台 0.90 的两台泵并联，独立假设下是 99.00%；加上 2% 的共因失效（同一路电源、同一根冷却水管、同一个控制器），实际是 **98.82%**。

差 0.18 个百分点看起来很小，但共因那一部分是**永远修不好**的——它不随冗余数量增加而下降。所以做冗余设计时，第一个要问的不是「备几台」，而是「这两台共用什么」。
:::

| 单台可用度 | 独立并联 | 计共因（2%） | 差 |
| --- | --- | --- | --- |
| 0.90 | 99.0000% | 98.8200% | 0.1800 点 |
| 0.95 | 99.7500% | 99.6550% | 0.0950 点 |
| 0.99 | 99.9900% | 99.9702% | 0.0198 点 |

## 六、可靠性数据的最低字段集

想拟合 β，至少要这几列。缺任何一列，数据就只能用来「数次数」，不能用来「算分布」：

| 字段 | 作用 | 缺失后果 |
| --- | --- | --- |
| `asset_id` / `part_id` | 同一对象的多次失效才能成组 | 无法按对象拟合 |
| `installed_at` | 投用时刻 | 算不出已运行时间 |
| `failed_at` | 失效时刻 | 算不出寿命 |
| `failure_mode` | 失效模式（轴承、密封、电气） | 不同模式混在一起，β 无意义 |
| `censored` | 是否右删失 | 丢弃在运行样本，β 偏高 |
| `repair_action` | 修复 / 更换 / 调整 | 无法区分「修过」与「换过」 |

```sql
CREATE TABLE eq_failure (
  fail_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id     TEXT NOT NULL REFERENCES eq_asset(asset_id),
  part_id      TEXT,
  failure_mode TEXT NOT NULL,          -- ISO 14224 的失效模式词表
  installed_at TEXT NOT NULL,
  failed_at    TEXT,                   -- NULL 表示右删失
  censored     INTEGER NOT NULL DEFAULT 0 CHECK (censored IN (0,1)),
  repair_action TEXT CHECK (repair_action IN ('REPAIR','REPLACE','ADJUST')),
  CHECK ( (censored = 1 AND failed_at IS NULL)
       OR (censored = 0 AND failed_at IS NOT NULL AND failed_at > installed_at) )
);
```

最后那条 `CHECK` 把「删失」与「失效」的语义钉死了：**删失的记录不能有失效时刻，失效的记录不能没有时刻**。这一条能挡掉大量「时间填 0」的脏数据。

## 七、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `EQR-A` | MTBF 与可用率分别计算，不互相替代 | 两个指标各有字段或视图 |
| `EQR-B` | MTBF 报表标注是否含短停机 | 有 `include_short` 标记 |
| `EQR-C` | β 估计附样本量与置信区间 | 参数记录含 `n` 与 `ci_low/ci_high` |
| `EQR-D` | 样本 < 30 时不输出 β 结论，改用基准值 | 有 `sample_insufficient` 标记 |
| `EQR-E` | 失效记录支持右删失 | `censored` 字段 + `CHECK` |
| `EQR-F` | 失效按 `failure_mode` 分组，不混算 | 拟合按模式分组 |
| `EQR-G` | 系统可用度按串联/并联结构计算，不取平均 | 有结构定义表 |
| `EQR-H` | 冗余设计评估共因失效 | 有 `common_cause` 参数 |

## 八、验证方式

```shell
# 1) 删失记录不得有失效时刻
sqlite3 /tmp/mnt.db "INSERT INTO eq_failure(asset_id,failure_mode,installed_at,failed_at,censored)
  VALUES('EQ-001','BEARING','2026-01-01T00:00','2026-05-01T00:00',1);"
# 期望：CHECK constraint failed

# 2) 失效记录必须有失效时刻且晚于投用
sqlite3 /tmp/mnt.db "INSERT INTO eq_failure(asset_id,failure_mode,installed_at,failed_at,censored)
  VALUES('EQ-001','BEARING','2026-01-01T00:00',NULL,0);"
# 期望：CHECK constraint failed

# 3) MTBF 两种口径（含/不含短停）应不同
sqlite3 /tmp/mnt.db "SELECT ROUND(286560.0/count(*)/60,1) AS mtbf_all,
  ROUND(286560.0/sum(CASE WHEN (julianday(end_at)-julianday(start_at))*1440 >= 5 THEN 1 ELSE 0 END)/60,1) AS mtbf_ge5
  FROM eq_downtime WHERE end_at IS NOT NULL;"
# 期望：mtbf_ge5 明显大于 mtbf_all（若相等，说明没有短停记录）

# 4) 串联系统可用度
python3 -c "print(round(0.997**12*100,2), round((1-(1-0.997)**2)*100,4))"
# 期望：96.46 99.9991

# 5) β 估计随样本量收敛
python3 - <<'PY'
import math, random
def fit(xs):
    xs=sorted(xs); n=len(xs); sx=sy=sxx=sxy=0.0
    for i,x in enumerate(xs,1):
        F=(i-0.3)/(n+0.4); y=math.log(-math.log(1-F)); xx=math.log(x)
        sx+=xx; sy+=y; sxx+=xx*xx; sxy+=xx*y
    return (n*sxy-sx*sy)/(n*sxx-sx*sx)
random.seed(7)
print(round(fit([900*(-math.log(1-random.random()))**(1/2.2) for _ in range(400)]),2))
PY
# 期望：2.0~2.4 之间（真值 2.2）
```

## 参考资料

- [停机口径、可用率与 OEE 分解](../Downtime/index.md)：可用率的分母
- [维护策略与间隔：BM / PM / CBM / PdM](../Strategy/index.md)：β 如何决定间隔
- [点检、状态监测与阈值](../Inspection/index.md)：征兆与失效的对应
- [数据库内核与存储引擎](../../../DB/DatabaseInternals/Overview/index.md)：大规模失效数据的存储与聚合
- ISO 14224:2016：失效模式词表与可靠性数据的最小字段集：<https://www.iso.org/standard/64076.html>
- ISO 55000:2024：资产绩效与生命周期的关系：<https://committee.iso.org/TC251>
