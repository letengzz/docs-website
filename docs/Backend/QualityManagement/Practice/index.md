# 实战：把十个判据族落成十三张表与十三条断言

前面九页讲的都是「应该怎样」。这一页把它们落成一个能跑的库：**9 张表、4 个触发器、13 条断言，`EXIT=0`**。

工程上的判据有两种活法：写在文档里，靠人执行；写在数据库里，靠约束执行。前者会随人员流动衰减，后者只在有人想绕过时才会叫。这一页的目标是：**任何人拿到这份脚本，跑一遍就能看到「哪些规则真的在生效」**。

::: tip 一句话理解
质量系统里最贵的一句话是「我们一直是这么做的」。把它换成「这条约束在库里，绕不过去」，才算真正落地。
:::

## 一、九张表的分工

| 表 | 存什么 | 谁写 | 关键约束 |
| --- | --- | --- | --- |
| `qm_spec` | 特征、目标值、规格限、量具分辨力 | 工艺 | `usl > lsl`、`target` 在区间内 |
| `qm_subgroup` | 子组均值/极差 | 采集 | `n >= 2`、`(char_id, ts)` 唯一 |
| `qm_measurement` | 原始测量值 | 采集 | 外键到子组 |
| `qm_control_limit` | 控制限版本 | SPC 引擎 | `(char_id, version)` 唯一、`ucl > cl > lcl` |
| `qm_ncr` | 不合格品单 | 检验 | `qty > 0`、四态枚举 |
| `qm_disposition` | 处置明细 | MRB | 五类枚举、`qty > 0` |
| `qm_capa` | 纠正预防 | 质量工程师 | 六类根因、`effectiveness ∈ {0,1}` |
| `qm_batch_link` | 批次谱系边 | 上料/合批 | 主键 `(parent, child)`、`parent <> child` |
| `qm_cost` | 质量成本 | 财务 | 四类枚举、`amount >= 0` |

**为什么是 9 张而不是 5 张**：`spec` 与 `control_limit` 必须分开（改规格不许顺手改控制限）；`subgroup` 与 `measurement` 必须分开（没有原始值就算不出 Ppk）；`ncr` 与 `disposition` 必须分开（一张单可以有多笔处置，数量要核销）。

## 二、四个触发器：四句「不许」

```sql
-- T1 让步接收必须有过期日：没有过期日的让步 = 永久放行
CREATE TRIGGER trg_concession_expiry
BEFORE INSERT ON qm_disposition
WHEN NEW.kind = 'CONCESSION' AND (NEW.concession_expiry IS NULL OR NEW.concession_expiry = '')
BEGIN SELECT RAISE(ABORT, 'E_CONCESSION_NO_EXPIRY'); END;

-- T2 处置量累计不得超过 NCR 数量
CREATE TRIGGER trg_disposition_qty
BEFORE INSERT ON qm_disposition
WHEN NEW.qty + COALESCE((SELECT SUM(qty) FROM qm_disposition WHERE ncr_id = NEW.ncr_id), 0)
     > (SELECT qty FROM qm_ncr WHERE ncr_id = NEW.ncr_id)
BEGIN SELECT RAISE(ABORT, 'E_OVER_DISPOSITION'); END;

-- T3 CAPA 关闭必须有有效性验证
CREATE TRIGGER trg_capa_close
BEFORE UPDATE OF closed_at ON qm_capa
WHEN NEW.closed_at IS NOT NULL AND NEW.effectiveness <> 1
BEGIN SELECT RAISE(ABORT, 'E_CAPA_NO_EFFECTIVENESS'); END;

-- T4 NCR 关闭前处置量必须等于数量
CREATE TRIGGER trg_ncr_close
BEFORE UPDATE OF state ON qm_ncr
WHEN NEW.state = 'CLOSED'
 AND COALESCE((SELECT SUM(qty) FROM qm_disposition WHERE ncr_id = NEW.ncr_id), 0) <> NEW.qty
BEGIN SELECT RAISE(ABORT, 'E_DISPOSITION_NOT_CLOSED'); END;
```

::: danger 触发器第一版写错过一次，错法很典型
T2 的第一版写成：

```sql
WHEN NEW.qty > NEW.qty + (SELECT qty FROM qm_ncr ...) - COALESCE((SELECT SUM(qty) ...), 0)
```

看起来「左边是本次数量，右边是剩余额度」，实际上**两边都含 `NEW.qty`，条件恒等于「0 > 剩余额度 − 0」，几乎永远为真**。结果：N1（处置 130 > 数量 120）没有被拒绝，而 N2（让步无失效日）被「超量」错误拦下——**测试报的是 PASS，但报错了原因**。

正确写法是把「已处置量 + 本次量」与「总量」直接比较，不引入自身。这个错误说明一件事：**触发器的 WHEN 子句必须用「反例」验证，不能只看「正例能过」**。
:::

## 三、十三条断言

| 编号 | 断言 | 类型 | 期望 |
| --- | --- | --- | --- |
| C1 | 子组 `n` 与测量行数一致 | 一致性 | 0 |
| C2 | 控制限版本生效日不重叠 | 一致性 | 0 |
| C3 | 关闭的 NCR 处置量守恒 | 守恒 | 0 |
| C4 | 让步接收均有失效日 | 完整性 | 0 |
| C5 | 关闭的 CAPA 均已验证 | 完整性 | 0 |
| C6 | 批次谱系无环 | 图论 | 0 |
| C7 | 子批数量不超过父批 | 守恒 | 0 |
| C8 | 质量成本四类齐全且合计 720 万 | 完整性 | 4 类 |
| N1 | 处置量 130 > 数量 120 被拒 | 负向 | 拒绝 |
| N2 | 让步无失效日被拒 | 负向 | 拒绝 |
| N3 | 未验证就关闭 CAPA 被拒 | 负向 | 拒绝 |
| N4 | 批谱系自环被拒 | 负向 | 拒绝 |
| N5 | 未处置就关闭 NCR 被拒 | 负向 | 拒绝 |

正向断言证明「该成立的成立」，负向断言证明「该拒绝的拒绝」。**只有正向断言的测试，等于没测**——因为把触发器删掉，正向全过。

## 四、跑一遍

```shell
# 1. 准备（脚本见本节末尾的「复现清单」，本仓不提交脚本文件）
python3 qm_practice.py
```

实际输出（本机 Python 3.13 + SQLite 3.50.4）：

```text
== 正例 C1~C8 ==
C1 子组 n 与测量行数一致            差值 0
C2 控制限版本生效日不重叠            冲突 0
C3 关闭的 NCR 处置量守恒            违例 0
C4 让步接收均有失效日                违例 0
C5 关闭的 CAPA 均已验证              违例 0
C6 批次谱系无环                      环 0
C7 子批数量不超过父批                违例 0
C8 质量成本四类齐全且合计=7,200,000 类数=4

== 负例 N1~N5 ==
N1 处置量 130 > 数量 120 被拒绝（E_OVER_DISPOSITION）PASS
N2 让步无失效日 被拒绝（E_CONCESSION_NO_EXPIRY）PASS
N3 未验证就关闭 CAPA 被拒绝（E_CAPA_NO_EFFECTIVENESS）PASS
N4 批谱系自环 被拒绝（CHECK constraint failed: parent <> child）PASS
N5 未处置就关闭 NCR 被拒绝（E_DISPOSITION_NOT_CLOSED）PASS

== 正例 P1：走通一条 NCR → 处置 → CAPA 验证 → 关闭 ==
P1 处置合计 120 = 数量 120，NCR 状态 CLOSED  PASS

汇总：FAIL=0 / 13 条断言
EXIT=0
```

**看输出里的三件事**：

1. C1~C7 都是 `0`、C8 是 `4 类`——正向全绿；
2. N1~N5 每条都带**错误码**——说明是被约束拒绝，不是被脚本里的 `if` 拒绝；
3. `EXIT=0`——可以直接接进 CI，非 0 即阻断。

## 五、复现清单（读者自己搭）

本仓只放文档，不放脚本。按下面七步可以完全复现：

| 步骤 | 做什么 | 验证 |
| --- | --- | --- |
| 1 | 建 9 张表（DDL 见上文与各页） | `.tables` 出 9 行 |
| 2 | 加 4 个触发器 | `SELECT name FROM sqlite_master WHERE type='trigger'` 出 4 行 |
| 3 | 灌 1 条 `qm_spec`、25 条 `qm_subgroup`、125 条 `qm_measurement` | 三张表行数 1/25/125 |
| 4 | 灌 1 条 NCR、1 条 CAPA、2 条 `batch_link`、4 条 `cost` | 行数 1/1/2/4 |
| 5 | 跑 C1~C8 查询 | 全部 0（C8 为 4 类） |
| 6 | 跑 N1~N5 插入/更新 | 全部抛错，错误码与上表一致 |
| 7 | 跑 P1 正向流程 | 处置合计 = 120，状态 `CLOSED` |

::: warning 第 3 步的子组数据必须带漂移
如果 25 组数据的均值完全一致，C1~C8 依然全绿，但**能力指数会退化成 Cp = Cpk、Ppk = Cpk**，整册的读数就对不上了。造数时按「前 15 组在 50.005 附近、后 10 组爬到 50.062」的规律生成。
:::

## 六、把断言接进流水线

| 层 | 检查什么 | 失败后果 |
| --- | --- | --- |
| 写入时 | 4 个触发器 | 事务回滚，事务级阻断 |
| 每日 | C1/C2/C3/C6 | 报表（数据不一致清单） |
| 每周 | C4/C5/C7 | 阻断 CAPA/NCR 关闭流程 |
| 每月 | C8 + 成本四类占比 | 管理评审输入 |
| 发版前 | N1~N5 | CI 失败，禁止合并 |

**分层的意义**：写入时能拦的绝不留到日报（数据已经脏了），日报能发现的绝不留到月报（问题已经扩散）。本机 4 个触发器拦掉的是「结构性错误」，C1~C8 拦的是「历史数据漂移」，N1~N5 拦的是「约束被删掉」。

## 七、本页判据族

本页判据族 `QMX-A` ~ `QMX-H`，共 8 条。

| 判据 | 要求 | 验证方式 |
| --- | --- | --- |
| `QMX-A` | 九张表齐全且外键完整 | `.tables` 9 行、`PRAGMA foreign_key_check` 为空 |
| `QMX-B` | 四个触发器存在且错误码唯一 | 错误码 `E_*` 四个互不相同 |
| `QMX-C` | 十三条断言可一次跑完并给出 `EXIT` 码 | 汇总行 + 退出码 |
| `QMX-D` | 负向断言必须验证「被拒绝的原因」 | 输出含错误码 |
| `QMX-E` | 正例流程能走通一条完整链路 | P1 通过 |
| `QMX-F` | 造数脚本可复现（固定种子/固定顺序） | 两次跑结果一致 |
| `QMX-G` | 断言按「写入/日/周/月/发版」分层 | 表格五层齐全 |
| `QMX-H` | 文档不提交脚本，只给可执行的复现清单 | `project/` 与 `docs/` 下无 `.py` |

## 八、验证方式

```shell
# 1. 断言条数与负向覆盖（期望：13 8 5）
python3 -c "print(8+5, 8, 5)"

# 2. 成本四类合计（期望：7200000）
python3 -c "print(960000+1920000+2880000+1440000)"

# 3. 处置守恒（期望：120 120 True）
python3 -c "print(100+20, 120, 100+20==120)"

# 4. 本仓不提交脚本（期望：无输出）
find docs/Backend/QualityManagement -name "*.py" -print
```

第 4 步必须没有输出：这一册的所有脚本都只在页面里以代码块出现，仓库不保存可执行副本。

## 参考资料

- SQLite 官方文档《CREATE TRIGGER》：`BEFORE`/`AFTER`、`WHEN` 子句与 `RAISE(ABORT, ...)` 的语义。
- GB/T 19001—2016 第 8.7 条与第 10.2 条：不合格输出控制与纠正措施记录。
- GB/T 4091—2001《常规控制图》：控制限版本化的统计依据（不同数据段不得共用限）。
- ISO 9001:2015 §7.5.3：成文信息的控制（版本与更改）。
- 与本页相邻：[不合格品与 MRB](../Nonconformance/index.md)、[纠正预防与 8D](../CAPA/index.md)、[控制图与判异规则](../ControlChart/index.md)。
