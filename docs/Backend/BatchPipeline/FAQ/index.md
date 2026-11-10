# 常见问题与分诊

这一页收的是「被问到最多次、且答案不是查文档能查到」的十个判断题。每个答案都指向本册里能验证它的那一页。

::: tip 一句话定位
本页回答「**遇到具体现象时，先看哪一条**」；原理与表格在各自章节，本页只给判断与动作。
:::

## 一、十个判断题

### 1. 昨天的报表是空的，先看哪里？

三个地方按顺序看，**不要先看 SQL**：

```sql
-- ① 分区存不存在（不存在 = 没跑或没登记；存在但 state 不对 = 门禁拦了）
SELECT job_id, data_date, row_cnt, state FROM partition_registry
WHERE data_date = '2026-09-10' ORDER BY job_id;
-- ② 运行记录（有没有 SUCCESS、attempt 几、trigger_type 是什么）
SELECT run_id, attempt, status, exit_code, is_current FROM batch_run
WHERE data_date = '2026-09-10' ORDER BY job_id, attempt;
-- ③ 判据（哪一条没过、读数多少）
SELECT job_id, rule_code, metric, threshold, passed FROM readiness_check
WHERE data_date = '2026-09-10';
```

三种典型组合：`无分区 + 有 SUCCESS 运行` → 提交逻辑没写登记；`有分区 + state=BLOCKED` → 判据拦了；`有分区 + state=READY + row_cnt=0` → 空分区被当成就绪，读[就绪与门禁](../ReadinessGate/index.md)。

### 2. 「今天的数据比昨天少 30%」，是故障吗？

先查日历，再查分布，最后才怀疑数据。

| 检查 | 命令 | 结论 |
| --- | --- | --- |
| 今天是不是节假日/大促/月末 | `SELECT * FROM batch_calendar WHERE cal_date=:d` | 有备案就按 `expect_ratio` 判 |
| 少的是「行数」还是「金额」 | 两个判据分开看 | 只少一个 → 口径问题，不是数据丢失 |
| 少的是「整天」还是「某个渠道/地区」 | 按维度下钻 | 单维度缺失 → 上游部分失败 |

本库实测：大促日真实 2.6× 会被 ±30% 的带宽拦住（误拦），漏推日 0.4× 也会被拦（正确）。**误拦要处理，但不能因此放宽阈值**——否则漏推那天就放过去了。

### 3. 重跑一次就够了吗？

不够。重跑只改一个分区，**下游不会自动跟着变**。实测：`dwd` 重跑一天后与源差 1,916 行，而 `ads` 仍是旧值。

正确动作是「重跑 + 级联」：先算闭包（3 个下游节点），再按日期升序把下游一并重算，最后重对账。见[补数与回刷](../Backfill/index.md)。

### 4. 补数要补几天，怎么算？

```text
要补的天数 = 出问题的那几天（按 data_date）
要重算的分区 = 天数 × (1 + 下游闭包大小)
```

本库闭包是 3，所以补 7 天 = 21 个分区。补之前先跑一次闭包查询并打印，见[依赖与就绪](../Dependency/index.md)第三节。

### 5. 能不能直接改数（`UPDATE` 生产表）？

不能，理由不是「不安全」，而是**改完就没人知道原来是什么**。

`partition_registry` 的 `checksum` 会在改数后与 `dwd` 不一致，`recon_result` 的对账结论失效，而 `batch_run` 里没有任何一次运行对应这次改动——三张表同时说谎。

要改就走「重跑」：新增一条 `attempt`，让改数这件事有运行记录、有 `trigger_type`、有审计。

### 6. 上游说「数据没问题」，我该信吗？

信，但要让它变成一条可验的判据。「没问题」的三种可验形态：

| 上游的承诺 | 落到判据 |
| --- | --- |
| 「昨天全量推了」 | 文件行数 = 上游侧行数（对账口径要写死） |
| 「只补了漏的 300 单」 | 重跑后行数增加 = 300（不是 300 的倍数） |
| 「口径没变」 | 同一批样本重算，金额差 = 0 |

第三条最有用：**拿 100 行样本重算一遍，比听十次「没问题」可靠**。

### 7. 为什么加了索引还是慢？

因为查询里给分区列套了函数。实测 106,747 行上：

| 写法 | 计划 | 相对 |
| --- | --- | --- |
| `dt = ?` | `SEARCH` | 1.0× |
| `dt LIKE '2026-09%'` | **`SCAN`** | 98.8× |
| `substr(dt,1,7) = ?` | **`SCAN`** | 129.7× |
| `date(dt) = ?` | **`SCAN`** | 176.1× |

改成范围条件（`dt >= ? AND dt < ?`）即可，见[分区写入](../PartitionWrite/index.md)第五节。

### 8. 空分区要不要跑下游？

要跑，但要带上「这是空的」这个事实。三种写法三种后果：

| 做法 | 下游看到 | 风险 |
| --- | --- | --- |
| 不跑 | 分区不存在 | 与「没跑」无法区分，只能干等 |
| 跑，产出 0 | 0 元 | 与「业务真为 0」无法区分 |
| 跑，标 `EMPTY` | 0 元 + 明确状态 | 正确 |

### 9. SLA 总差 20 分钟，加机器有用吗？

先算「超标幅度分布」，再算「加机器能省多少」。

本库实测：60 天超 SLA 8 天，最小超标幅度 35 分钟。把计算提速 50%（省 37.5 分钟）只救回 2 天；把轮询改事件驱动（省 30 分钟）**一天都救不回**——因为 30 < 35。

结论：**优化量小于最小超标幅度时，收益是 0**。见[SLA 与就绪预算](../SlaBudget/index.md)。

### 10. 什么时候可以不做批次，改成流式？

一个判据就够：**业务能不能接受「数据是逐条到达的」**。

| 场景 | 批次合适 | 流式合适 |
| --- | --- | --- |
| 日报、月报、结算 | 是 | 否（对流式是过度设计） |
| 风控拦截、实时推荐 | 否 | 是 |
| 「昨天的数」用于考核 | 是 | 否（流式的「昨天」需要水位，更难对账） |
| 跨系统对账 | 是 | 否（批次天然有边界） |

批次不会因为「流式更时髦」而消失——**只要存在「一天」这个业务概念，就存在批次**。

## 二、三步分诊

```text
现象
 ├─ ① 分区在不在？
 │    ├─ 不在 → 查 batch_run：有 SUCCESS 却没登记 → 提交逻辑；无运行 → 调度/上游文件
 │    └─ 在   → ② 状态对不对？
 │              ├─ BLOCKED → 查 readiness_check：哪条没过、读数 vs 阈值
 │              ├─ EMPTY   → 查日历：该不该是空的
 │              └─ READY   → ③ 数对不对？
 │                            ├─ 行数对、金额不对 → 口径
 │                            ├─ 行数是整数倍 → 追加写
 │                            └─ 只差一天 → 错日/迟到单
```

三步走完还没定位，问题多半不在批次层，而在上游文件本身——这时候该看的是「文件到达时刻」与「文件行数」，而不是库里的表。

## 三、判据清单

| 编号 | 判据 | 不满足时改哪里 |
| --- | --- | --- |
| `BPQ-A` | 十个判断题的答案都能在本册找到对应章节 | 本页链接 |
| `BPQ-B` | 「先看分区、再看状态、最后看数」的顺序被写进值班手册 | 值班文档 |
| `BPQ-C` | 分诊三步各有可执行 SQL，不是流程图 | 本页第二节 |
| `BPQ-D` | 空分区、追加写、错日三类现象各有「指纹」识别方式 | 分诊表 |
| `BPQ-E` | 「改数 vs 重跑」的选择有明确规则（只能重跑） | 运维规范 |
| `BPQ-F` | 上游承诺必须落成可验判据，不接受口头确认 | 协作流程 |
| `BPQ-G` | SLA 优化前必须给出「超标幅度分布」 | 优化记录 |
| `BPQ-H` | 批次与流式的边界有书面判据，不靠偏好 | 架构决策记录 |

## 四、验证方式

```shell
cd /tmp && python3 - <<'PY'
import sqlite3
con = sqlite3.connect("/tmp/bpprac.db")
q = lambda s: con.execute(s).fetchall()
d = "2026-09-05"
print("① 分区在不在：", q("SELECT job_id,state,row_cnt FROM partition_registry WHERE data_date=?", (d,)))
print("② 状态与判据：", q("SELECT rule_code,passed FROM readiness_check WHERE data_date=? AND job_id='ods_order'", (d,)))
print("③ 分诊汇总（BLOCKED 数应为 0）：",
      q("SELECT COUNT(*) FROM partition_registry WHERE state='BLOCKED'")[0][0])
PY
```

预期输出：

```text
① 分区在不在： [('ads_report_day','EMPTY',0), ('dwd_order','EMPTY',0), ('dws_order_day','EMPTY',0), ('ods_order','EMPTY',0)]
② 状态与判据： [('ROW_BAND',0), ('WATERMARK',0)]
③ 分诊汇总（BLOCKED 数应为 0）： 0
```

第 ② 段显示两条判据都是 0（未通过），但分区状态是 `EMPTY` 而不是 `BLOCKED`——因为这一天在日历上是节假日，空是允许的。**这正是「判据未通过」与「状态不可用」必须分开看的原因。**

## 参考资料

- [Apache Airflow 3: Troubleshooting](https://airflow.apache.org/docs/apache-airflow/stable/troubleshooting.html)
- [dbt: Debugging errors](https://docs.getdbt.com/docs/build/debugging-errors)
- [Google SRE Book: Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/)
- [SQLite: EXPLAIN QUERY PLAN](https://sqlite.org/eqp.html)
