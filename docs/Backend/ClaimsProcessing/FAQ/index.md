# 常见问题与分诊

理赔系统出问题时的第一句话通常是「这个案子赔错了」。这句话信息量为零——赔错可能是条款、是定损、是分摊、是支付、是追偿，四种错法对应四个不同的修法。这一页先给分诊表，再给十二个高频问题。

## 一、十二行分诊表

| 症状 | 先看哪里 | 最可能的根因 | 一条命令定位 |
| --- | --- | --- | --- |
| 赔款比客户预期少 | `assessment_item` | 核减太多或漏项 | `SELECT cut_reason, SUM(unit_price-allowed_price) FROM assessment_item WHERE assessment_id=? GROUP BY 1` |
| 赔款比条款上限多 | `policy.limit_per_claim` | 限额取错（用了保额） | `SELECT sum_insured, limit_per_claim FROM policy WHERE policy_id=?` |
| 同一事故两条赔案 | `incident.incident_key` | 指纹不准，归并失败 | `SELECT incident_id, count(*) FROM claim GROUP BY 1 HAVING count(*)>1` |
| 客户说「我报过案了」 | `report.incident_id` | 报案未挂接 | `SELECT report_no, incident_id FROM report WHERE subject_key=?` |
| 钱付了但状态没变 | `claim_event` | 支付与状态迁移未同事务 | `SELECT status FROM claim WHERE claim_id=?` 对比事件末尾 |
| 同一笔赔款付了两次 | `payment.pay_seq` | 缺唯一键或序号复用 | `SELECT pay_seq, count(*) FROM payment WHERE claim_id=? GROUP BY 1 HAVING count(*)>1` |
| 赔付率突然跳升 | `payment` + `reserve` | 准备金一次性释放或追偿未冲减 | 按月的已付与准备金两列并排看 |
| 准备金不够 | 三角与假设 | 发展因子过时 | 重算 `f(k)`，对比去年 |
| 结案率突然下降 | 分母 | 换了分母（报案 vs 立案） | 查报表定义，不查数据 |
| 时效变差 | `filed_at` | 归并后重新计时 | `min(received_at)` 是否被使用 |
| 分摊后合计差一分 | 取整方式 | 逐方四舍五入 | 换最大余数法 |
| 反欺诈误杀投诉多 | 规则阈值 | 精度过低 | 算 `精度 × 案均 > 调查成本` |

## 二、十二个高频问题

**Q1：定损金额能不能超过申报金额？**
能。客户申报 30,000、实际损失 45,000 是常见情形（先估后修）。所以 `assessed_amount <= reported_amount` 不能做硬约束，见 [案件模型](../ClaimModel/index.md)。

**Q2：免赔额是在税前还是税后扣？**
先算赔款再扣免赔，与先扣免赔再算赔款，结果不同（本机差 7,300 元）。顺序由条款决定，写进解释文件，见 [条款与责任判定](../Coverage/index.md)。

**Q3：相对免赔的「悬崖」要不要抹平？**
不要。悬崖是条款定义的一部分，抹平等于改条款。要做的是**在系统里能解释**：客服输入损失 10,001，系统能弹出「相对免赔门槛 10,000，全赔」。

**Q4：一次事故两张保单，谁先赔？**
比例分摊或顺序赔付，二者选一并写进条款。不要在代码里用 `ORDER BY policy_id` 隐式决定，见 [赔付与支付](../Payment/index.md)。

**Q5：追偿回收冲减赔款还是费用？**
冲减赔款（`PAID_LOSS`）。冲费用会让赔付率虚高 1.6 个点，而赔付率是定价输入。

**Q6：准备金什么时候释放？**
结案时。释放与结案必须在同一事务，且用触发器守住（`E_RESERVE_LEFT`），见 [准备金](../Reserve/index.md)。

**Q7：链梯法和赔付率法用哪个？**
两个都算，交叉验证。只用一个时，赔付率法要把假设的敏感性一起报（本机 ±3 个点对应 2,160 万）。

**Q8：报案到立案的时效，归并后怎么算？**
取最早报案时间（`min(received_at)`）。用第二次报案时间会让归并后的时效变好看，这是自欺。

**Q9：结案率报哪个分母？**
两个都报。本机 68.0%（对报案）与 73.9%（对立案），差 5.9 个点。

**Q10：反欺诈规则要不要放宽？**
看边际：`多抓到的欺诈金额 > 多查的成本`。精度 57.5% 时值得查，放宽到 30% 就不值得。

**Q11：赔案能不能删？**
不能。作废用状态（`CANCELLED` 或 `VOID`），冲正用反向流水。删除会让银行流水与系统永久对不上。

**Q12：客户要求「先赔后补材料」怎么办？**
可以，但要落「待补清单」并计时。缺材料的部分挂准备金，不进入实付——否则材料永远补不上，赔款已经出去了。

## 三、止血五步

线上发现「赔错了」时，按顺序做五件事，不要跳步：

1. **冻结**：把相关赔案置为 `ON_HOLD`（或加 `hold_reason`），停止后续支付。
2. **定界**：用一条 SQL 圈出受影响范围（同一批核减规则？同一张保单？同一个时间段？），**先定界再修数**。
3. **留证**：导出受影响赔案的三额（责任 / 核定 / 实付）与事件链，落成一份不可改的快照。
4. **修数**：新增修正流水与新的定损版本，不覆盖原记录。
5. **回填**：把根因写进判据清单（本页或对应章节），并补一条负向用例——**没有用例的修复会复发**。

## 四、术语表

| 术语 | 含义 | 本册对应 |
| --- | --- | --- |
| 免赔额 | 保险公司不赔、由被保险人自担的部分 | `policy.deductible` |
| 相对免赔 | 损失未达门槛不赔，达到则全赔 | `deductible_kind='FRANCHISE'` |
| 责任限额 | 每次事故 / 每人 / 累计的最高赔付 | `policy.limit_per_claim` |
| 实际价值（ACV） | 重置成本扣折旧 | `assessment.basis='ACV'` |
| 残值 | 换下旧件的价值，应从赔款中扣 | `assessment.salvage` |
| 代位求偿 | 赔付后向责任方追偿 | `recovery` |
| 未决赔款准备金 | 已报案未结案 + 已发生未报案 | `reserve` |
| IBNR | 已发生未报案 | 三角与链梯法 |
| 赔付率 | 赔款 / 已赚保费 | [度量](../Metrics/index.md) |
| 案均赔款 | 赔款 / 案件数 | [度量](../Metrics/index.md) |

## 五、判据清单

本页判据族 `INQ-A` ~ `INQ-H`，共 8 条。

| 编号 | 判据 | 判定方式 |
| --- | --- | --- |
| `INQ-A` | 每种症状都有定位命令 | 分诊表 12 行，每行一条可执行 SQL |
| `INQ-B` | 症状不落到「系统有问题」 | 每一行都指向具体表或字段 |
| `INQ-C` | 止血五步有先后 | 冻结在定界之前，留证在修数之前 |
| `INQ-D` | 修数不覆盖原记录 | 修正走新版本 / 反向流水 |
| `INQ-E` | 每个修复补一条用例 | 负向用例数随修复递增 |
| `INQ-F` | 术语与字段一一对应 | 术语表右列均可点击或可查 |
| `INQ-G` | 常见问题不回链到空页 | 十二条问题的链接均可打开 |
| `INQ-H` | 本页不重复他页正文 | 每条回答 ≤ 3 行，细节指向专页 |

## 六、验证方式

```shell
# 1) 分诊表第一行的命令可直接跑（本机示例库）
sqlite3 /tmp/clm.db "SELECT cut_reason, SUM(unit_price-allowed_price) AS cut FROM assessment_item WHERE assessment_id=1 GROUP BY 1;"
# 期望：PRICE_CAP|400.0

# 2) 重复支付自检
sqlite3 /tmp/clm.db "SELECT pay_seq, count(*) FROM payment WHERE claim_id=1 GROUP BY 1 HAVING count(*)>1;"
# 期望：（空，无输出）

# 3) 同一事故双立案自检
sqlite3 /tmp/clm.db "SELECT incident_id, count(*) FROM claim GROUP BY 1 HAVING count(*)>1;"
# 期望：（空）
```

## 参考资料

- [总览：七段链与三个「赔多少」](../Overview/index.md)
- [实战：九张表、三个触发器、十一条断言](../Practice/index.md)
- SQLite 查询语法（分诊表里的命令均基于此）：<https://www.sqlite.org/lang_select.html>
- GB/T 36687—2018《保险术语》：<https://openstd.samr.gov.cn/>
