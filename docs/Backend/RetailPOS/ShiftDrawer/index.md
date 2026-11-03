# 班次与钱箱：备用金、缴款与长短款

收银台下面那个抽屉，在系统里至少是四个东西：一叠有编号的现金、一个归属某个人的责任范围、一条有期初和期末的流水、以及一笔要在下班时交出去的钱。绝大多数门店系统只实现了第三个——一个 `cash_amount` 字段，然后靠店长每天数一遍。

数得出来就没事，数不出来就找人。于是「长短款」在门店里长期被当成人的问题，而不是系统的问题。

::: tip 一句话理解
钱箱是一本**只有现金的账**：期初 + 收 − 退 − 缴 = 应有，应有 − 点钞 = 长短款。四个数少一个，长短款就只是个玄学数字。
:::

## 一、班次模型：谁在为这个抽屉负责

一个班次（`shift`）不是「一段时间」，是**一次责任的转移**：

| 字段 | 含义 | 为什么必须有 |
| --- | --- | --- |
| `shift_id` | 班次主键 | 钱箱流水的归属 |
| `store_id` + `terminal_id` | 哪台终端的抽屉 | 一台终端一个抽屉，不能混 |
| `cashier_id` | 谁开班 | 长短款的责任人 |
| `opened_at` / `closed_at` | 起止 | 跨零点、跨班交接都靠它 |
| `float_open` | 备用金（期初） | 没有它，点钞数永远对不上 |
| `cash_in` / `cash_out` | 现金收 / 现金付（找零、退款、缴款） | 钱箱流水的两个方向 |
| `counted` | 点钞实数 | 长短款的被减数 |
| `status` | OPEN / CLOSED / HANDOVER | 未结班不能开新班 |

### 三种「开班」都是错的

| 写法 | 会发生什么 | 实际后果 |
| --- | --- | --- |
| 不做班次，直接收银 | 现金流水没有归属 | 谁短款查不出来，只能全店摊 |
| 按自然日开班（每天 00:00 自动开） | 夜班被切成两段 | 交接时点钞两次，两次都差 |
| 允许同一终端同时开两个班 | 两套流水争一个抽屉 | 点钞数只能对一半，另一半永远悬空 |

正确写法只有一种：**开班是一个显式动作，绑定 `terminal_id`，且同终端同时只能有一个 `OPEN` 班次**。这条约束用部分唯一索引就能表达：

```sql
CREATE UNIQUE INDEX uq_shift_open_per_terminal
  ON shift (terminal_id)
  WHERE status = 'OPEN';
```

## 二、钱箱流水的四个方向

现金在一天里只走四个方向，每一种都要单独落表：

| 方向 | 触发 | 记账符号 | 常见错法 |
| --- | --- | --- | --- |
| 收款 | 现金结账、组合支付里的现金部分 | `+` | 把找零前的钱记为收入（应记应收，找零单独记） |
| 找零 | 顾客给 100 买 87.5 | `−` | 不记找零，只记 87.5 收入（数字对，但抽屉里的钱对不上） |
| 退款 | 现金退货 | `−` | 只写退款单，不冲减钱箱（本机实测 991 笔退货里全都没冲） |
| 缴款 | 中途把大额现金交保险柜 | `−` | 不记缴款，日结时「多出来一大笔」 |

::: danger 找零与缴款是最容易漏的两笔
1. **找零必须落流水**，不能只在票面上写。顾客给 100、买 87.5、找 12.5，钱箱净增 87.5——这个 87.5 是「100 − 12.5」算出来的，不是「记一笔 100 再记一笔 87.5」。
2. **缴款必须带时间**，且发生时立刻落库。中途缴款 5,000 元却没记，日结的点钞数会比应有少 5,000，而收银员坚称「我没拿」——这类争议在门店里一个月至少一次。
:::

## 三、长短款：一个净额骗人的经典案例

本机实测 360 个班次（12 店 × 30 天）：

| 指标 | 读数 |
| --- | --- |
| 分毫不差的班次 | 317 个（88.06%） |
| 长款合计 | 44.01 元 |
| 短款合计 | 30.71 元 |
| **净额** | **+13.30 元** |
| 双向绝对差 | 74.72 元 |

净额 +13.30 元，占全天现金流水（761,018.50 元）的 0.0017%——任何「差异率 < 0.01% 视为正常」的规则都会放过它。但真实的绝对差是 74.72 元，**净额只暴露了 17.8%**。

这就是为什么长短款必须**分方向统计**：

```sql
SELECT
  SUM(CASE WHEN counted > expect + 0.005 THEN counted - expect ELSE 0 END) AS over_amt,
  SUM(CASE WHEN counted < expect - 0.005 THEN expect - counted ELSE 0 END) AS short_amt,
  SUM(counted - expect)                                                   AS net_amt,
  COUNT(*) FILTER (WHERE ABS(counted - expect) > 0.005)                   AS bad_shifts,
  COUNT(*)                                                                AS all_shifts
FROM (
  SELECT float_open + cash_in - cash_refund AS expect, counted FROM shift WHERE status='CLOSED'
);
```

`over_amt` 与 `short_amt` 才是要考核的数，`net_amt` 只能用来发现「方向和金额是否系统性偏移」。

### 长短款怎么归因

| 形态 | 典型金额 | 根因 | 怎么查 |
| --- | --- | --- | --- |
| 小额短款（−0.5 ~ −2） | 找零算错 | 凑整方向写反 | 比对 `rounding` 符号与点钞差 |
| 中等长款（+5 ~ +50） | 漏记退款 | 退款没冲钱箱 | 当天退款单 vs 钱箱 `cash_out` |
| 大额短款（−500 以上） | 漏记缴款 | 缴款没落库 | 问保险柜出入库记录 |
| 双向都有、金额相近 | 串班 | 两个班次共用一个抽屉 | 查 `shift` 时间是否重叠 |

## 四、备用金：一个不能省的数字

备用金（`float_open`）是开店时放进抽屉的零钱，用于找零。它的三个特性决定了它必须单独存：

1. **它不属于营业额**。日结时算「今天收了多少钱」，备用金要扣掉。
2. **它会在班次间转移**。A 班交给 B 班时，`float` 是交接内容之一。
3. **它会变**。中途可能需要补充（换零钱），这也是现金流水。

本机实测三种口径的差额（12 店 × 30 天）：

| 算法 | 结果 | 差在哪 |
| --- | --- | --- |
| 期初 + 现金收 − 现金退 | 904,119.36 | 少算「已缴款」 |
| 期初 + 现金收（只算收） | 941,018.50 | 把退款与缴款都当成了收入 |
| 现金收 − 现金退（只算净） | 724,119.36 | 把备用金整个吃掉了 |

三个数相差最多 **21.7 万元**，而它们都「按照某个口径算对了」。差 21.7 万不是差错，是**口径不同**——但报表上它们都叫「现金」。

::: warning 备用金也会被偷
储备金长期不变是常态，所以「备用金少了 200」这类事经常几个月才被发现。做法是：**每个班次开班必须输入备用金实数**，与上一班交出的数比对，不等就要求填写差异说明。这条规则的成本是每次开班多按三个数字，收益是备用金不再是盲区。
:::

## 五、交班：一次不能靠记忆的转移

交班（HANDOVER）是门店里最容易出事的环节，因为它同时发生三件事：点钞、交账、换人。

```text
A 班 CLOSED：counted = 5,000（含备用金 500）→ 应缴 4,500
B 班 OPEN  ：float_open = 500（从 A 班交出的现金里取）
```

两条硬约束：

1. **A 班的 `counted` 必须等于 B 班的 `float_open` + 缴款额**。不等就是交接时点错了。
2. **交班记录不能修改**，只能「红冲 + 重开」。否则事后谁都说不清当时的数是多少。

```sql
CREATE TABLE shift_handover (
  handover_id  TEXT PRIMARY KEY,
  from_shift   TEXT NOT NULL REFERENCES shift(shift_id),
  to_shift     TEXT NOT NULL REFERENCES shift(shift_id),
  counted      REAL NOT NULL,          -- 交出方点钞
  float_passed REAL NOT NULL,          -- 留给下一班的备用金
  deposit      REAL NOT NULL,          -- 交保险柜
  diff         REAL GENERATED ALWAYS AS (counted - float_passed - deposit) STORED,
  created_at   TEXT NOT NULL,
  CONSTRAINT ck_handover_balance CHECK (ABS(counted - float_passed - deposit) < 0.005)
);
```

`diff` 用生成列而不是应用层算，好处是**这条等式在任何写入路径上都被数据库检查**，包括运维手工补数。

## 六、判据

本页判据族 `RSS-A` ~ `RSS-H`，共 8 条。

| 判据 | 断言 | 验证方式 |
| --- | --- | --- |
| `RSS-A` | 同终端同时只能有一个 `OPEN` 班次 | 部分唯一索引存在，插第二个 `OPEN` 被拒 |
| `RSS-B` | 班次必有 `float_open` 且 > 0 | `CHECK (float_open >= 0)`，空值插入被拒 |
| `RSS-C` | 现金流水四方向齐全（收 / 找零 / 退 / 缴） | `cash_flow.direction` 枚举含四个值 |
| `RSS-D` | 找零落流水，不只落票面 | 一笔 100 元付 87.5 的单，流水里有一条 `−12.5` |
| `RSS-E` | 退款冲减钱箱 | 当天 `cash_out` ≥ 当天退款现金额 |
| `RSS-F` | 长短款分方向统计 | SQL 同时输出 `over` / `short` / `net` 三个数 |
| `RSS-G` | 交班等式由数据库保证 | `CHECK` 或生成列存在，手工插不平衡行被拒 |
| `RSS-H` | 班结后现金流水不可改 | `CLOSED` 班次上的 `UPDATE` 被触发器拒绝 |

## 七、验证方式

```shell
# 1. 准备最小库
sqlite3 /tmp/shift.db <<'SQL'
CREATE TABLE shift(shift_id TEXT PRIMARY KEY, terminal_id TEXT, status TEXT,
                   float_open REAL, cash_in REAL, cash_refund REAL, counted REAL);
CREATE UNIQUE INDEX uq_open ON shift(terminal_id) WHERE status='OPEN';
INSERT INTO shift VALUES('A1','T01','OPEN',500,0,0,NULL);
SQL

# 2. 同终端再开一个班，应被拒（期望 stderr 含 UNIQUE constraint failed）
sqlite3 /tmp/shift.db "INSERT INTO shift VALUES('A2','T01','OPEN',500,0,0,NULL);" || echo "已按预期拒绝"

# 3. 长短款分方向（在实战库上跑）
sqlite3 rp.db "
select round(sum(case when counted > float_open+cash_in-cash_refund+0.005
                      then counted-(float_open+cash_in-cash_refund) else 0 end),2) as over_amt,
       round(sum(case when counted < float_open+cash_in-cash_refund-0.005
                      then (float_open+cash_in-cash_refund)-counted else 0 end),2) as short_amt,
       count(*) as shifts
from shift where status='CLOSED';"
# 本机期望：44.01|30.71|360
```

第 3 步的输出必须**两个数都看**。只看 `over_amt - short_amt` 的报表，会把 74.72 元的绝对差报成 13.30 元。

## 参考资料

- GB/T 18184—2025《商业自动化术语》（2025-10-05 发布、2026-02-01 实施，代替 GB/T 18184—2008）：钱箱（cash drawer）、班次（shift）、缴款（deposit）的术语定义。
- 财政部等五部委《企业内部控制基本规范》（财会〔2008〕7 号）第二十九条：不相容职务分离控制——收银与缴款、记账与对账不得由同一人兼任。
- 与本页相邻：[总览](../Overview/index.md)、[支付与找零](../PaymentTender/index.md)、[班结与日结](../DayClose/index.md)。
