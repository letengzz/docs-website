# 优惠与凑整：顺序、分摊与余数

「满 200 减 30，我买了 210，那这 30 块是按什么比例分到每件商品上的？」顾客不会问这个问题，但系统必须回答——因为三个月后他来退其中一件，退多少钱取决于这个答案。

优惠是门店系统里**唯一一个「算术上没有唯一解」**的模块。同样一批商品，按不同顺序算、按不同方式分摊余数，会得到相差几分钱的结果。几分钱在单笔上看不出，在 30,000 笔上就是几百上千元。

::: tip 一句话理解
优惠必须先定**顺序**（谁先谁后）、再定**余数归谁**（分摊闭合），最后才轮到**凑整**（为了收现金方便）——顺序一变，结果就变。
:::

## 一、四类优惠的固定顺序

| 顺序 | 类型 | 作用对象 | 计算方式 | 谁承担 |
| --- | --- | --- | --- | --- |
| 1 | 单品特价 | 单行 | 替换 `unit_price` | 门店 |
| 2 | 整单满减 | 整票 | 按门槛一次减 | 门店 |
| 3 | 会员折扣 | 整票 | 按折率 | 门店 / 品牌 |
| 4 | 支付立减 | 支付 | 渠道侧减 | 渠道 |

顺序为什么不能变：**满减按原价算，会员折按满减后的价算**。如果反过来（先会员折再满减），满 200 的门槛会因为打折而达不到，顾客实际拿到的优惠变少。

```text
原价 210 → 满减 −30 → 180 → 会员 95 折 → 171 → 支付立减 −5 → 实付 166
原价 210 → 会员 95 折 → 199.5 → 满减不触发（<200）→ 199.5 → −5 → 194.5
```

两条路径差 **28.5 元**。这不是「算法不同」，而是**促销规则本身的定义问题**——必须在活动配置里写死，不能让收银端「看哪个便宜用哪个」。

::: danger 三种「叠加」的实现错误
1. **让收银员手动选优惠**：同一件商品不同顾客不同价，且无法复现。
2. **按「最优组合」自动枚举**：枚举成本高，且会让「限时特价」变成「永久最优价」（因为系统总选最便宜的）。
3. **优惠顺序跟着代码执行顺序走**：新增一种优惠时，插入位置变了，历史单据的重算结果也变了。
:::

## 二、整单优惠必须落到行上

一张票的优惠是整单的，但**退货是按行退的**。所以整单优惠必须分摊到每一行：

```sql
-- 分摊后每行实付 = line_amt - discount_share
SELECT line_no, sku, line_amt, discount_share, line_amt - discount_share AS net
FROM ticket_line WHERE ticket_id = 'T1' ORDER BY line_no;
```

不分摊会怎样：整单满减 30 元，退一件 80 元的商品。该退 80 还是 68？

| 做法 | 退给顾客 | 问题 |
| --- | --- | --- |
| 退原价 80 | 80 | 顾客赚了：他实际只付了 68 |
| 按比例退 68 | 68 | 正确 |
| 不退优惠，只退 80 − 30 = 50 | 50 | 把整单优惠全压在这一件上 |

正确答案是 68，即 `80 × (170 / 200)`。**这个比例只有在优惠落到了行上才算得出来。**

## 三、余数：一个必须自己算一遍的例子

优惠 10 元，三行各 33.33 / 33.33 / 33.34。三种分摊：

| 做法 | 第 1 行 | 第 2 行 | 第 3 行 | 合计 | 差 |
| --- | --- | --- | --- | --- | --- |
| 独立四舍五入 | 3.33 | 3.33 | 3.33 | 9.99 | **−0.01** |
| 全部给第一行 | 3.34 | 3.33 | 3.33 | 10.00 | 0（但歧视第一行） |
| 最大余数法 | 3.33 | 3.33 | **3.34** | 10.00 | 0 |

最大余数法（Largest Remainder）的三步：

1. 每行算精确分摊额 `raw = line_amt / total × discount`；
2. 全部**向下取整到分**，得到 `floor_i`，并算出缺口 `rem = (discount − Σfloor) × 100`（以分为单位的整数）；
3. 按 `raw_i` 的小数部分从大到小排序，前 `rem` 行各补 1 分。

```python
def allocate(lines, discount):
    total = sum(lines)
    raw = [x / total * discount for x in lines]
    cents = [int(x * 100) for x in raw]           # 向下取整到分
    rem = round(discount * 100) - sum(cents)      # 缺口（分）
    order = sorted(range(len(lines)), key=lambda i: -(raw[i] * 100 - cents[i]))
    for i in order[:max(0, rem)]:
        cents[i] += 1
    return [c / 100 for c in cents]
```

本机实测：7,700 笔含整单优惠的单据里，**独立四舍五入有 1,059 笔（13.75%）分摊不闭合**，累计差 10.75 元，单笔最大 0.02 元；同一批用最大余数法，**不闭合 0 笔**。

::: warning 0.02 元的差不是「小问题」
单笔差 2 分，看起来无所谓。但它会同时破坏三件事：
1. **行实付之和 ≠ 整单实付**：退货按行退，累计退出来的钱比实收多 2 分。
2. **优惠报表与财务口径不一致**：营销部门统计的让利总额，比财务账上的多。
3. **对账永远差几分**：日结时找不到差在哪，只能人工调平。
:::

## 四、凑整（抹零）：第五类优惠

凑整是「为了收现金方便，把金额调到角」。它有三个必须守住的边界：

| 边界 | 规则 | 违反后果 |
| --- | --- | --- |
| 只作用于现金部分 | 电子支付不凑整 | 电子单多收 5 分，渠道对账差 |
| 单独字段 `rounding` | 不并进 `discount` | 退货时把凑整的钱也退给顾客 |
| 可正可负 | 四舍五入到角，不是一律舍 | 一律舍会让门店每天少收几十元 |

本机实测：2,064 笔发生凑整（6.88%），合计 **−1.63 元**，单笔均值 0.030 元；其中向上 957 笔、向下 1,107 笔。

「合计 −1.63 元」这个读数很说明问题：**如果一律舍去**，30,000 笔里 9,000 多笔现金单每笔平均舍 3 分，合计约 −270 元。四舍五入让正负相抵，总额接近 0——这才是「凑整」与「让利」的区别。

```sql
-- 凑整金额：现金部分才凑，且记在独立字段
UPDATE ticket
SET rounding = ROUND(payable_after_discount * 10) / 10.0 - payable_after_discount,
    payable  = ROUND(payable_after_discount * 10) / 10.0
WHERE has_cash_tender;   -- 由支付方式决定，不是无条件执行
```

::: danger 凑整必须在「支付方式确定之后」
收银流程是「点单 → 算钱 → 选支付方式 → 收款」。如果算钱时就把金额凑整到角，而顾客最后选了扫码，就会出现「应收 87.5，扫码付了 87.5」但票面写 87.5（凑整后）的假象——实际上没凑整。**凑整是支付方式的函数，不是金额的函数。**
:::

## 五、优惠的三种「不可见损失」

| 损失形态 | 例子 | 谁承担 | 怎么发现 |
| --- | --- | --- | --- |
| 顺序错 | 先折后满减，门槛达不到 | 顾客（少拿优惠） | 对比两种顺序的应优惠额 |
| 分摊错 | 独立四舍五入 | 门店（多退几分） | 行实付之和 vs 整单实付 |
| 重复叠加 | 会员折与特价同时生效 | 门店（让利翻倍） | 检查互斥规则是否落库 |

第三种最难查，因为它「看起来很合理」：会员价 9 折遇上特价商品，到底按哪个？如果两个都生效，就是 0.9 × 特价，门店让利 10% 而不自知。

```sql
CREATE TABLE promotion (
  promo_id    TEXT PRIMARY KEY,
  promo_type  TEXT NOT NULL,             -- ITEM_SPECIAL / ORDER_THRESHOLD / MEMBER / PAY
  priority    INTEGER NOT NULL,          -- 1..4，与上表顺序一致
  stackable   INTEGER NOT NULL DEFAULT 0,-- 是否可与同优先级叠加
  exclusive_with TEXT,                   -- 互斥的 promo_id 列表（JSON）
  effective_from TEXT NOT NULL,
  effective_to   TEXT,
  CONSTRAINT ck_priority CHECK (priority BETWEEN 1 AND 4)
);
```

互斥关系落库而不是写在代码里，好处是**运营可以自己调**，且每次变更都能被审计。

## 六、判据

本页判据族 `RSD-A` ~ `RSD-H`，共 8 条。

| 判据 | 断言 | 验证方式 |
| --- | --- | --- |
| `RSD-A` | 四类优惠有固定 `priority` 1~4 | `promotion.priority` 有 `CHECK`，取值域恰为 1~4 |
| `RSD-B` | 优惠顺序由 `priority` 决定，不由代码顺序 | 调整 `priority` 后重算结果变化可解释 |
| `RSD-C` | 整单优惠分摊到行，且分摊额之和 = 整单优惠 | `SUM(discount_share) = discount` 违例 0 |
| `RSD-D` | 分摊用最大余数法，不闭合率为 0 | 对含优惠票据重算，不闭合笔数 0 |
| `RSD-E` | 凑整单独字段，不进 `discount` | `rounding` 列存在且非空票据上 `discount` 不变 |
| `RSD-F` | 凑整只作用于含现金的票据 | 纯电子票据 `rounding = 0` |
| `RSD-G` | 互斥规则落库可配置 | `promotion.exclusive_with` 非空时两条优惠不并发生效 |
| `RSD-H` | 行实付之和 = 整单实付 | `Σ(line_amt − discount_share) + rounding = payable` 违例 0 |

## 七、验证方式

```shell
# 1. 最大余数法 vs 独立四舍五入（三行 33.33/33.33/33.34，优惠 10）
python3 - <<'PY'
lines = [33.33, 33.33, 33.34]; d = 10.0
naive = [round(x / sum(lines) * d, 2) for x in lines]
raw = [x / sum(lines) * d for x in lines]
cents = [int(x * 100) for x in raw]
rem = round(d * 100) - sum(cents)
order = sorted(range(len(lines)), key=lambda i: -(raw[i] * 100 - cents[i]))
for i in order[:max(0, rem)]: cents[i] += 1
print("独立四舍五入", naive, sum(naive))
print("最大余数法  ", [c / 100 for c in cents], sum(cents) / 100)
PY
# 期望：独立 [3.33, 3.33, 3.33] 9.99 / 最大余数 [3.33, 3.33, 3.34] 10.0

# 2. 分摊闭合率（在实战库上跑，期望 0 行）
sqlite3 rp.db "
select count(*) from (
  select t.ticket_id from ticket t join ticket_line l using(ticket_id)
  group by t.ticket_id
  having abs(sum(l.discount_share) - max(t.discount)) > 0.01);"

# 3. 凑整方向分布（期望一笔向上、一笔向下都不是「全部舍去」）
sqlite3 rp.db "
select sum(case when rounding > 0 then 1 else 0 end) as up,
       sum(case when rounding < 0 then 1 else 0 end) as down,
       round(sum(rounding),2) as total from ticket;"
```

第 1 步的两行输出就是整个分摊模块的分水岭：**差 1 分与不差 1 分**。写完这段代码，务必要用「行实付之和 = 整单实付」跑一遍全量，而不是只看单笔。

## 参考资料

- 《中华人民共和国价格法》第十四条：经营者不得利用虚假的或者使人误解的价格手段，诱骗消费者交易。
- 商务部《零售商促销行为管理办法》（2006 年第 18 号令）第十条：零售商开展促销活动，应当明示促销原因、方式、规则、期限及限制条件。
- 与本页相邻：[营销计价与优惠分摊](../../PricingPromotion/Allocation/index.md)、[价目下发](../PriceSync/index.md)、[退货与冲红](../ReturnRefund/index.md)。
