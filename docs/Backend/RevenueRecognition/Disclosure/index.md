# 披露口径与月结

<p style="text-align:center;"><img src="../assets/rv-logo.png" style="zoom:75%;" /></p>

披露最容易被认为是「财务写附注」的事，与工程无关。但附注里的每一个数都必须能追到一条明细——**分解表加起来要等于利润表那一行，合同余额表的期初期末要能对上本期变动，RPO 要能追到每一份未履约合同**。追不到，就是月结那晚手工补的一张 Excel，而它明年一定还在。

::: tip 一句话理解
**披露不是「把数字抄到附注」，而是证明「每个数都能追到一条明细」。** 三张表之所以存在，是因为它们各自守着一个恒等式；恒等式破了，说明明细层已经错了。
:::

![月结七步：把明细账压成三张披露表](../assets/rv-disclosure.svg)

本页判据族 `RVD-A` ~ `RVD-H`，共 8 条，定义在最后一节。

## 月结七步

| 步 | 动作 | 产物 | 可重跑吗 |
| --- | --- | --- | --- |
| ① 锁账期 | 冻结本期业务截止时点 | `period_lock` 记录 | 可（重复锁只更新时间） |
| ② 确认收入 | 按排期生成 `revenue_entry` | 确认明细 | **必须可重跑**（唯一键保证幂等） |
| ③ 结转成本 | 按配比结转 | 成本明细 | 可重跑 |
| ④ 对余额 | 算应收/合同资产/合同负债 | `contract_balance` | 可重跑（覆盖写） |
| ⑤ 出分解表 | 按维度汇总收入 | 披露表 1 | 只读，随时可跑 |
| ⑥ 写附注 | 余额变动、RPO、政策 | 披露表 2、3 | 只读 |
| ⑦ 留痕归档 | 记录行数、金额、批次 | `close_run` | 每次一条，不覆盖 |

```sql
CREATE TABLE close_run (
  id          INTEGER PRIMARY KEY,
  period      TEXT NOT NULL,
  step        TEXT NOT NULL,       -- lock / recognize / cost / balance / report / note / archive
  rows_affected INTEGER NOT NULL,
  amount_sum  NUMERIC(18,2) NOT NULL,
  started_at  TEXT NOT NULL,
  finished_at TEXT NOT NULL,
  operator    TEXT NOT NULL,
  run_no      INTEGER NOT NULL,    -- 同一期间的第几次运行
  UNIQUE (period, step, run_no)
);
```

`run_no` 是给审计看的：**同一期间第 2 次运行必须有原因**（差错了、补单了）。没有这一列，就分不清「重跑了一次」和「改了数」。

## 三张披露表与它们的恒等式

### 表 1：收入分解表

要按「产品 / 地区 / 时点」多维拆，且**每个维度的合计都要等于利润表里的收入**。

```sql
-- 按产品分解（去重是关键，见下一节的扇出坑）
SELECT p.prod, sum(r.amt) AS revenue
FROM rev r
JOIN (SELECT DISTINCT cid, prod FROM rev) p ON p.cid = r.cid
GROUP BY p.prod
UNION ALL
SELECT '合计', sum(amt) FROM rev;
```

恒等式：`Σ 各维度明细 = 利润表收入`。

本机读数：5,000 条收入、每条打 1~2 个标签，直接 `JOIN tag` 后合计从 **22,539,179.36** 变成 **33,891,186.10**，虚增 **50.37%**；先去重再加总，差 **0.00**。

::: danger 扇出（fan-out）是分解表的第一杀手
一条收入打两个标签，`JOIN` 后它出现两次——**而每个维度的合计都「看起来对」**，因为它确实等于「该标签下的收入之和」。错的是「合计」：它变成了各维度之和，而各维度之间有重叠。

三条防线：
1. **每条分解查询都必须先 `DISTINCT` 到主键粒度**，再汇总；
2. 分解表的「合计」行**单独从主表算**，不从明细加总；
3. 月结时跑一条断言：`SUM(各维度) = 主表合计`，不等就中止。
:::

### 表 2：合同余额变动表

| 行 | 计算 |
| --- | --- |
| 期初余额 | 上期 `contract_balance` |
| 本期增加 | 本期新产生的合同资产 / 负债 |
| 本期减少（转收入 / 转应收） | 本期释放的部分 |
| 期末余额 | 期初 + 增加 − 减少 |

恒等式：`期末 = 期初 + 增加 − 减少`，且 `期末` 必须等于余额表的当期值。

```sql
SELECT b.period,
       sum(b.contract_asset) - sum(p.contract_asset) AS asset_delta,
       sum(b.contract_liability) - sum(p.contract_liability) AS liab_delta
FROM contract_balance b
JOIN contract_balance p ON p.contract_id = b.contract_id AND p.period = :prev_period
WHERE b.period = :period
GROUP BY b.period;
```

### 表 3：剩余履约义务（RPO）

RPO = 尚未履行（或部分未履行）的履约义务对应的交易价格。两个口径必须分开说清：

| 口径 | 金额（本机示例） | 差异来源 |
| --- | --- | --- |
| 按合同总额 − 已确认 | 420,000.00 | 含尚未开始的部分与未受约束的可变对价 |
| 按已分摊未确认 | **345,000.00** | 只算已分摊到义务、尚未确认的部分 |
| 差额 | 75,000.00 | 可变对价约束、尚未开始的合同、未分摊的溢价 |

对外披露通常用「已分摊未确认」口径，并说明是否包含可变对价与是否包含原始期限 ≤ 1 年的合同（实务上常允许简化）。

```sql
-- RPO：已分摊 − 已确认，只到分
SELECT sum(a.allocated_amount) - coalesce((
         SELECT sum(e.amount) FROM revenue_entry e
         WHERE e.contract_id = a.contract_id AND e.obligation_id = a.obligation_id), 0) AS rpo
FROM po_allocation a
JOIN contract c ON c.id = a.contract_id
WHERE c.status = 'active';
```

::: warning RPO 不能直接拿「合同总额 − 已确认」
合同总额里可能含**未分摊的溢价**、**未受约束的可变对价**、以及**已取消但还没关账的合同**。三者都会让 RPO 偏高，而偏高不会被任何人质疑——它只会让「未来收入储备」看起来更漂亮。
:::

## 期间切点：月结里最贵的一行代码

本机读数：20,000 条业务记录，`< '2026-02-01'` 与 `<= '2026-01-31'` 两种写法合计相差 **164,521.32 元**；落在 1 月 31 日当天的记录 **654 条**，被整段丢掉。

```sql
-- 错：会漏掉 1 月 31 日当天带时刻的所有记录
WHERE done_at <= '2026-01-31'

-- 对：边界写「下期开始」，且用严格小于
WHERE done_at < '2026-02-01'
```

更深一层的做法是**根本不在查询里做时间比较**：确认明细只存 `period`（`YYYY-MM`），期间归属在写入时决定一次，之后所有查询都按 `period` 分组。这样「切点」从一个散落各处的隐患，收敛成一处可单测的逻辑。

## 会计政策要落成开关，不是注释

披露里的「会计政策」段，每一条都对应系统里的一个开关：

| 政策表述 | 系统开关 | 取值 |
| --- | --- | --- |
| 不超过 1 年的合同不考虑融资成分 | `financing_policy` | `expedient_1y` / `always_discount` |
| 质保按保证类处理 | `warranty_type` | `assurance` / `service` |
| 运输费作为履约成本 | `shipping_treatment` | `fulfilment_cost` / `separate_obligation` |
| 收入按净额法列示（代理） | `gross_or_net` | `gross` / `net` |

开关的价值不在「可配置」，而在**审计可以问「你的政策是什么」，答案在数据库里而不是在某个人脑子里**。

## 判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `RVD-A` | 分解表各维度合计 = 利润表收入（先去重再汇总） | 跑断言 SQL，差必须为 0 |
| `RVD-B` | 分解表的「合计」行从主表算，不从明细加总 | 看 SQL：合计来自主表 |
| `RVD-C` | 余额变动表满足「期末 = 期初 + 增 − 减」 | 逐期断言，差 = 0 |
| `RVD-D` | RPO 用「已分摊 − 已确认」口径，并注明是否含可变对价 | RPO 可逐合同复算 |
| `RVD-E` | 期间以 `YYYY-MM` 存储，切点比较不在业务查询中出现 | 全库搜 `<= '20` |
| `RVD-F` | 每次月结留 `close_run` 记录（含 `run_no`） | 同期同步骤出现 run_no = 2 时必须附原因 |
| `RVD-G` | 会计政策落成开关，附注表述与开关取值一一对应 | 四组开关存在且被读取 |
| `RVD-H` | 三张表都能由明细重跑得到，结果与归档一致 | 重跑一次，diff = 0 |

## 验证方式

```shell
# 1) 分解表合计 = 主表（预期：两列相等）
sqlite3 /tmp/rv.db "SELECT (SELECT sum(amt) FROM rev) AS base,
  (SELECT sum(a) FROM (SELECT sum(r.amt) AS a FROM rev r
     JOIN (SELECT DISTINCT cid, prod FROM rev) p ON p.cid=r.cid GROUP BY p.prod));"

# 2) 余额恒等式（预期 0 行）
sqlite3 /tmp/rv.db "SELECT b.contract_id, b.period FROM contract_balance b
  JOIN contract_balance p ON p.contract_id=b.contract_id AND p.period=:prev
  WHERE b.period=:cur
    AND b.contract_asset <> p.contract_asset + :asset_increase - :asset_release;"

# 3) 月结留痕完整（预期 0 行缺失）
sqlite3 /tmp/rv.db "SELECT period, step FROM close_run WHERE rows_affected IS NULL OR amount_sum IS NULL;"
```

## 参考资料

- [合同资产、合同负债与应收](../ContractBalance/index.md)：余额表的三个科目从哪来
- [可变对价与退款负债](../VariableConsideration/index.md)：RPO 里要不要含未受约束的可变对价
- [实战：本机跑通一条确认闭环](../Practice/index.md)：三张表的可执行版本
- IFRS 15 第 110~122 段（分解、余额变动、剩余履约义务与重大判断）：<https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/>
- 财政部《企业会计准则第 14 号——收入》第四十一条至第四十三条（披露）：<https://kjs.mof.gov.cn/zhengcefabu/201707/t20170719_2653110.htm>
