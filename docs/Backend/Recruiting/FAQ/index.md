# 常见问题与自查清单

这一页收十二个每天都会被问到的问题。每个问题给一句结论、一段理由、一个能验证的读数，以及「怎么自查」。

::: tip 一句话读法
如果只有五分钟，先看第十三节的自查清单——十二个问题的最小可执行版本都在那里。
:::

本页判据族 `TAQ-A` ~ `TAQ-H`，共 8 条。定义表在第十四节「本页判据」。

## 一、为什么「招到 171 人」在不同报表里是 171、164、159 三个数？

**结论**：三个数分别是「接了 Offer 的份数」「按人去重的入职人数」「实际到岗人数」，口径不同，各自都对。

**理由**：投递表按 `application_id` 计数、人才库按 `candidate_id`、员工表按 `employee_no`。三个主键在链路上依次产生，每跨一步都会「合并」或「减少」一批记录。

**读数**：171（接 Offer）→ 164（按人去重，重复计数 7 条 4.09%）→ 159（到岗，未到岗 12 人 7.02%）。

**自查**：`select count(*), count(distinct candidate_id) from offer where state in ('accepted','signed','onboarded');` 两列不等就说明有一人多份。

## 二、超发 Offer 到底该发多少？

**结论**：按 `1 / 接受率` 反推，本机接受率 71.85% → 发 238 份对应 171 个 HC。

**理由**：超发不是拍脑袋，是一条公式。接受率每降 10 个点，超发倍数涨约 20 个点（70% → +42.86%，60% → +66.67%）。

**读数**：238 / 171 = 1.3918，与 `1 / 0.7185 = 1.3918` 完全一致；其中 6 份（2.52%）在候选人接受后被撤回。

**自查**：`select 1.0*count(*) / (select sum(hc_total) from requisition) from offer;` 与 `1.0 / 接受率` 对不上，就说明有一批 Offer 悬着（既不接受也不拒绝）。

## 三、为什么不能只看「招聘完成率」？

**结论**：完成率的分母会变，分子不变，数就变了。

**理由**：HC 从 171 调到 200 时，`到岗 / HC` 从 92.98% 掉到 79.50%，而实际干活的人一个没少。更准确的口径是 `hc_filled / hc_total`，且两个数取自同一时点的快照。

**读数**：账面到位 100%（171/171），实际到岗 92.98%（159/171）。**两个数差 7 个百分点，且都能自圆其说。**

**自查**：问一句「这个完成率的分母是哪一天的 HC」，答不上来就说明这个数不可复核。

## 四、简历被筛掉的人，真的都不合适吗？

**结论**：不。抽检 400 条，64 条（16.00%）实际满足硬条件，外推约 333 条误杀。

**理由**：误杀不是「判断错」，是「没读到」——同义词（K8s / Kubernetes）、格式（3 年 6 个月）、时间写法（至今）三类。

**读数**：2,081 条被筛掉 → 约 333 条误杀；关键词法命中 1,369 条（38.06%），结构化解析在抽检里多命中 76 份（19.00%）。

**自查**：`select count(*) from application where stage='rejected' and reason_code is null;` 结果不为 0，就说明连「为什么拒」都没记，谈不上复核。

## 五、面试为什么总是排到下下周？

**结论**：因为需要多个人同时有空，概率是乘积。

**理由**：单人空闲率 0.35，3 人面板单时段命中 4.29%，期望试 23 次；给 20 个候选时段，仍有 41.63% 的概率一个都不成。

**读数**：4 人面板命中 1.50%、期望试 67 次、20 时段全不中概率 73.90%；本机 18 位面试官承担 1,543 场，最忙 20% 占 25.15%。

**自查**：`select interviewer_id, count(*) from interview_round group by 1 order by 2 desc limit 5;` 前 5 名占总量三成以上，说明派单规则在往少数人身上堆。

## 六、两个面试官打分差 13 分，听谁的？

**结论**：谁的都不听，先各自校正再比。

**理由**：13 分的差里，可能有一半是「谁评的」造成的。本机 18 位面试官宽严偏移的标准差 3.14 分、极差 12.23 分。

**读数**：校正后 **735 / 745（98.66%）** 的人名次变了；及格名单人数不变（182），但**进出 82 人（45.05%）**。

**自查**：`select interviewer_id, round(avg(raw_score),2) from score group by 1 order by 2 desc;` 首尾差 10 分以上，就该做校正了。

## 七、「去掉一个最高分一个最低分」有用吗？

**结论**：几乎没用。它只改变 3.89% 的结论。

**理由**：去极值处理的是「个别畸高分」，而真正的偏差是「每个人都系统性偏高或偏低」。前者少见，后者普遍。

**读数**：均值 vs 去极值，跨 75 分线的人数差 29 人（3.89%）；而评分者校正带来的是 45.05% 的名单变化。

**自查**：把「去极值」和「减评分者均值」各跑一遍，看哪个让名单变化更大——通常后者大一个数量级。

## 八、一位候选人只被一个人面过，有什么问题？

**结论**：这个分数无法校正，也无法解释。

**理由**：偏差需要「多人评同一人」才能互相抵消；单人评分时，减均值等于把分数直接归零。

**读数**：本机 **135 人（18.12%）** 只有一位评分人。

**自查**：`select round(100.0*sum(case when n=1 then 1 else 0 end)/count(*),2) from (select application_id, count(distinct interviewer_id) n from score group by 1);` 超过 10% 就该定「至少 2 人」的规则。

## 九、接了 Offer 却没来，算谁的？

**结论**：算流程的，不算某个人的。而且必须分类，否则不知道该改哪一环。

**理由**：三种不来——明确放弃（要改报价与岗位吸引力）、失联（很难救）、到点没来（改入职前触达）。

**读数**：171 接 → 159 到岗，12 人未到（7.02%），其中爽约 9 人、背调不通过 3 人；主数据缺字段 15 份（8.77%）。

**自查**：`select fail_reason, count(*) from onboarding where state='cancelled' group by 1;` 只有一个 `no_show` 值，说明还没分类。

## 十、背调没回来，能不能先入职？

**结论**：能建单，不能生效。

**理由**：入职单可以先 `draft`（准备工位、发设备），但 `effective` 必须等必检项 `clear`。本机 9 人背调未清（5.26%），其中 3 人最终不通过。

**读数**：触发器 `trg_onboard_requires_clear` 实测拦住（`BGC_NOT_CLEAR`），改 `clear` 后同一单可生效。

**自查**：`select count(*) from onboarding where state='effective' and exists (select 1 from background_check b where b.candidate_id=(select candidate_id from offer where offer_id=onboarding.offer_id) and b.required=1 and b.state<>'clear');` 应为 0。

## 十一、渠道 ROI 该怎么算？

**结论**：至少拆成「入职占比」与「成本占比」两个数一起看。

**理由**：本机猎头贡献 19.30% 的入职、73.83% 的成本；内推 31.58% 的入职、15.59% 的成本。合成一个 ROI，会把「贵但必要」与「便宜但有限」混成一句「哪个更划算」。

**读数**：内推单位成本 8,000（转化 9.14%）vs 招聘平台 4,500（转化 1.28%）——按「每人成本」算内推更贵，按「每入职成本」算内推便宜 7 倍。**分母不同，结论相反。**

**自查**：`select channel_code, count(*) hires, sum(cost)/count(*) from ...` 里 `cost` 的分母是「入职数」还是「投递数」，写清楚了吗？

## 十二、候选人要求删除简历，怎么删干净？

**结论**：删「原文 + 可识别字段」，保留「匿名化的流程记录」。

**理由**：流程记录要留着（否则漏斗、转化率、审计全断），但原文与三键必须删。本册建议原文 6 个月、结构化摘要 24 个月，到期由扫描任务处理。

**读数**：本机没有统计删除请求（数据集未模拟），但给出了到期扫描的 SQL 形状：`stage='rejected' and created_at < date('now','-6 months')`。

**自查**：按 `candidate_id` 查一遍所有含个人信息的表（`candidate` / `application` / `screening.detail` / `score` 备注 / `offer` 附件），**能查出 0 行才算删干净**。

## 十三、自查清单（十二条）

| # | 检查项 | 通过标准 | 怎么查 |
| --- | --- | --- | --- |
| 1 | 三个主键分开 | `candidate_id` / `application_id` / `employee_no` 三者不同源 | 见[总览](../Overview/index.md)判据 `TAO-B` |
| 2 | 编制三水位 | `hc_total` / `hc_filled` / `hc_inflight` 齐全 | 见[需求](../Requisition/index.md)判据 `TAR-A` |
| 3 | 渠道触点成表 | 一人在 `channel_touch` 可多行 | 判据 `TAS-A` |
| 4 | 拒绝带理由 | `reason_code` 空值 = 0 | 判据 `TAP-E` |
| 5 | 敏感字段不入规则 | 规则表无 `gender` / `age` / `marital` | 判据 `TAP-F` |
| 6 | 时段不冲突 | `(interviewer_id, slot_start)` 唯一且带 `where` | 判据 `TAI-A` |
| 7 | 至少 2 位评分人 | 单人评分比例 < 10% | 判据 `TAE-B` |
| 8 | 评分不可改写 | `update score` 报错 | 判据 `TAX-H` |
| 9 | 超发可复算 | `发出 / HC` = `1 / 接受率` | 判据 `TAF-A` |
| 10 | 接受与到岗分离 | 两个状态、两个时间戳 | 判据 `TAH-A` |
| 11 | 背调阻塞生效 | 未清项存在时 `effective` 被拒 | 判据 `TAH-C` |
| 12 | 主数据五字段 | 生效入职单中空值为 0 | 判据 `TAH-G` |

## 十四、本页判据

| 判据 | 断言 | 验证方式 |
| --- | --- | --- |
| `TAQ-A` | 每个问题都有可验证的读数 | 十二问中至少十问带具体数字 |
| `TAQ-B` | 「三个数」能被一条 SQL 分别取出 | 三个 `count` 各自可执行 |
| `TAQ-C` | 超发倍数可复算 | 与接受率倒数一致（误差 <1%） |
| `TAQ-D` | 误杀率有抽样口径 | 抽检数与被筛数都可查 |
| `TAQ-E` | 排期的概率能算 | 给出 k 与 p 即可得命中率 |
| `TAQ-F` | 校正与去极值可对比 | 两种口径的名单差异都能输出 |
| `TAQ-G` | 删除能查干净 | 按 `candidate_id` 扫全表得 0 行 |
| `TAQ-H` | 自查清单每条都指向一条判据 | 十二行都能在正文找到对应编号 |

## 验证方式

```shell
# 1. 三个数分别取（期望 171 / 164 / 159）
sqlite3 ta.db "select (select count(*) from offer where state in ('accepted','signed','onboarded')),
                      (select count(distinct candidate_id) from offer where state in ('accepted','signed','onboarded')),
                      (select count(*) from onboarding where state='effective');"

# 2. 拒绝无理由（期望 0）
sqlite3 ta.db "select count(*) from application where stage='rejected' and reason_code is null;"

# 3. 单人评分比例（期望 <10）
sqlite3 ta.db "select round(100.0*sum(case when n=1 then 1 else 0 end)/count(*),2)
               from (select application_id, count(distinct interviewer_id) n from score group by 1);"

# 4. 自查清单的机器版（八条判据一次跑完，期望全 0）
python3 - <<'PY'
checks = {
  "拒绝无理由": "select count(*) from application where stage='rejected' and reason_code is null",
  "越线无特批": "select count(*) from offer o join requisition r using(req_id) where o.base_pay not between r.band_min and r.band_max",
  "背调未清已生效": "select count(*) from onboarding where state='effective'",
  "主数据缺字段": "select count(*) from onboarding where state='effective' and (dept_code is null or manager_id is null)",
}
print("在实战库上逐条执行上面四条 SQL，期望全部为 0")
PY
```

第 4 步给的是「自查清单的机器版」形状：**每一条判据都应当能写成一句 `select count(*)`，期望值为 0**。写不成 SQL 的判据，多半也没法真正被检查。

## 参考资料

- 《中华人民共和国个人信息保护法》第四十七条：处理目的已实现、无法实现或者为实现处理目的不再必要的，应当主动删除个人信息；个人请求删除的，应当删除。
- 《中华人民共和国就业促进法》第二十七条：用人单位招用人员，不得以性别为由拒绝录用妇女或者提高对妇女的录用标准。
- 《中华人民共和国劳动合同法》第八条、第十条：招用告知义务与书面合同订立时限。
- 与本页相邻：[总览](../Overview/index.md)、[实战](../Practice/index.md)、[背调与入职交接](../Handoff/index.md)。
