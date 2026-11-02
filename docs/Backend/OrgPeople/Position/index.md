# 岗位与编制：占编的四种口径

「这个部门有几个人？」这个问题在周会上被问一次，就会得到至少四个答案：编制上是 30 个，主岗在岗 28 个，加上兼岗 31 个，折算成全职当量 29.5 个。四个数字都真实，四个数字都不能直接比较。

编制是唯一一个「有上限」的组织属性，也是唯一一个能挡住业务方的：招聘要占编、转正要占编、借调不占编、兼岗不占编。**一旦口径没写死，编制就变成了一个谁都能解释的软约束**。

::: tip 一句话理解
编制是**授权**，在岗是**事实**，兼岗是**工时**。三个数各自成立，混在一起就都不成立。
:::

## 一、三层：岗位、编制、任职

![岗位、编制与任职](../assets/og-position.svg)

| 层 | 表 | 回答什么 | 谁维护 | 变更频率 |
| --- | --- | --- | --- | --- |
| 岗位 | `position(org_id, code, plan)` | 这个组织有哪些坑 | HRBP + 财务 | 每季度 |
| 编制 | `position.plan` | 每个坑允许几个人 | 预算委员会 | 每年 / 每季 |
| 任职 | `assignment(emp_id, pos_id)` | 谁占了这个坑 | 入转调离流程 | 每天 |

三者的关系不是「1:1:1」：一个岗位可以有多个编制（`plan = 3`），一个编制在同一时刻至多被一条 `primary` 任职占用，兼岗（`concurrent`）可以额外挂但**不占编**。

## 二、四种口径，四个数

本机 2026-06-30 的读数（405 个叶子组织、计划 7,033 个编制）：

| 口径 | 定义 | 读数 | 用途 |
| --- | --- | --- | --- |
| 计划（编制） | `SUM(position.plan)` | **7,033** | 预算、招聘额度 |
| 主岗在岗 | `kind='primary'` 且区间覆盖该日 | **6,852（97.4%）** | 编制占用率、超编判断 |
| 含兼岗 | 加上 `kind='concurrent'` | **7,042（100.1%）** | 工时与人效，不用于编制 |
| 去重人头 | `COUNT(DISTINCT emp_id)` | **6,852** | 花名册、社保、工资 |

第二行与第三行差 190 条，就是兼岗人数：**同一个人在两个组织各占一条任职**。按任职条数求和会得到 7,042，比真实人数多 2.7%——这个误差在部门级报表里会变成「两个部门都说这个人是我的人」。

### 为什么「占用率 97.4%」不能直接汇报

97.4% 是公司级汇总，它掩盖了两个方向的偏差：

| 分组 | 组织数 | 计划 | 实到 | 差 |
| --- | --- | --- | --- | --- |
| 超编 | 138 | 2,177 | 2,394 | **+217** |
| 缺口 | 191 | 3,668 | 3,270 | **−398** |
| 刚好占满 | 76 | 1,188 | 1,188 | 0 |
| 合计 | 405 | 7,033 | 6,852 | −181 |

超编 217 人与缺口 398 人在总数上互相抵消，于是公司级数字看起来「基本健康」（97.4%）。**编制管理必须看分布，不能看均值**——这条与容量规划里「平均负载 60%、P99 打满」是同一个道理。

::: danger 三个编制口径的坑
1. **用「含兼岗」判超编**。兼岗不占编，用它判超编会让 171 个组织（而不是 138 个）被判红，被误判的 33 个组织里全是「一人在两个组帮忙」的正常情况。
2. **用「在职人数」当占用**。在职包含已提离职但还没到最后工作日的人；这些人仍占编，但如果按 `leave_date` 提前剔除，就会出现「编制空着但招不进来」。
3. **编制没有生效日**。编制按季度调整，`plan` 只有一个当前值，于是「Q1 超编了吗」永远查不出来。编制表要带 `valid_from/valid_to`。
:::

## 三、编制也要有时间

编制是按预算周期给的，天然带时间：

```sql
CREATE TABLE position(
  pos_id     INTEGER PRIMARY KEY,
  org_id     INTEGER NOT NULL REFERENCES org(org_id),
  code       TEXT NOT NULL,
  valid_from TEXT NOT NULL,          -- 编制生效日（通常是预算期首日）
  valid_to   TEXT NOT NULL,
  plan       INTEGER NOT NULL CHECK (plan >= 0),
  UNIQUE (org_id, code, valid_from)
);

-- 某一天某岗位的计划编制
SELECT plan FROM position
 WHERE pos_id = ? AND valid_from <= ? AND valid_to > ?;
```

没有 `valid_from` 时，编制调整只能覆盖，于是「去年为什么招了 12 个人」这个问题无法回答——预算表说批了 8 个，编制表说现在是 10 个，两边都不算错，只是不在同一个时点上。

## 四、占编的唯一写入点

占编判断必须收在一处，否则并发招聘会超发 offer。三种写法：

| 写法 | 并发下 | 代价 |
| --- | --- | --- |
| 先查后插（应用层判断） | **超发**：两个事务同时查到「还剩 1 个」 | 最常用，也最错 |
| 触发器（插入时校验） | 正确，但报错在提交时才暴露 | 推荐，见实战页 `T3` |
| 计数列 + 条件更新 | 正确，`UPDATE ... WHERE used < plan` | 高并发首选 |

本机实战页的 `T3` 触发器就是第二种写法：

```sql
CREATE TRIGGER trg_headcount BEFORE INSERT ON assignment
WHEN NEW.kind='primary' AND (
  SELECT count(*) FROM assignment a
   WHERE a.pos_id=NEW.pos_id AND a.kind='primary' AND a.superseded_by IS NULL
     AND a.valid_from < NEW.valid_to AND NEW.valid_from < a.valid_to
) >= (SELECT plan FROM position WHERE pos_id=NEW.pos_id)
BEGIN SELECT RAISE(ABORT, 'E_OVER_ESTABLISHMENT'); END;
```

注意这里的重叠判定用的是**半开区间相交**（`a.from < NEW.to AND NEW.from < a.to`），而不是「当天在岗」——后者只能拦住同一天的超编，拦不住「下个月 1 号开始的三个人同时入职」。

## 五、判据

本页判据族 `OGP-A` ~ `OGP-H`，共 8 条：

| 编号 | 判据 | 怎么判 |
| --- | --- | --- |
| `OGP-A` | 岗位、编制、任职三层分表，`plan` 挂在岗位上 | 三张表都在，`plan` 不出现在 `assignment` |
| `OGP-B` | 占编只认 `primary`，兼岗不占编 | 触发器条件含 `kind='primary'` |
| `OGP-C` | 编制有生效区间，不只存当前值 | `position` 有 `valid_from/valid_to` |
| `OGP-D` | 超编在写入时被拦，不靠事后报表发现 | 触发器或条件更新存在 |
| `OGP-E` | 部门人数报表声明口径（主岗/含兼岗/去重） | 报表字段名带 `_primary` / `_incl_concurrent` |
| `OGP-F` | 超编与缺口按组织看分布，不只报公司级占用率 | 存在组织级超编清单 |
| `OGP-G` | 编制调整保留历史，不覆盖 | 调编走新行或版本列 |
| `OGP-H` | 招聘、转正、借调三类事件对占编的影响有明文规则 | 三类各有一条说明 |

## 六、验证方式

```shell
python3 - <<'PY'
import sqlite3
con = sqlite3.connect(":memory:")
con.executescript("""
CREATE TABLE position(pos INT PRIMARY KEY, plan INT);
CREATE TABLE asg(emp INT, pos INT, kind TEXT, vf TEXT, vt TEXT);
INSERT INTO position VALUES (1,3);
INSERT INTO asg VALUES (1,1,'primary','2026-01-01','2026-12-31'),
                       (2,1,'primary','2026-01-01','2026-12-31'),
                       (3,1,'primary','2026-01-01','2026-12-31'),
                       (4,1,'concurrent','2026-01-01','2026-12-31');
""")
d = '2026-06-30'
primary = con.execute("SELECT count(*) FROM asg WHERE pos=1 AND kind='primary' AND vf<=? AND vt>?", (d,d)).fetchone()[0]
allrow  = con.execute("SELECT count(*) FROM asg WHERE pos=1 AND vf<=? AND vt>?", (d,d)).fetchone()[0]
heads   = con.execute("SELECT count(DISTINCT emp) FROM asg WHERE pos=1 AND vf<=? AND vt>?", (d,d)).fetchone()[0]
print("主岗=%d 含兼岗=%d 去重人头=%d 计划=%d" % (primary, allrow, heads,
      con.execute("SELECT plan FROM position WHERE pos=1").fetchone()[0]))
PY
```

预期输出：`主岗=3 含兼岗=4 去重人头=4 计划=3`。

这一行把四种口径一次说清：主岗 3 个正好占满编制 3 个；含兼岗 4 条但编制没被突破；去重人头 4 人（兼岗那位是第 4 个人）。**如果报表只报「4 人 / 编制 3」，会得出「超编」的错误结论。**

```shell
grep -o 'OGP-[A-H]' docs/Backend/OrgPeople/Position/index.md | sort -u | wc -l
python3 utils/audit/judgeidcheck.py --root . | tail -1
```

预期输出：`8` 与 `E=0`。

## 参考资料

- [组织单元：三种存法与搬迁代价](../OrgModel/index.md)
- [异动：一次原子替换，不是两次更新](../Transfer/index.md)
- [全面预算：授权与占用](../../Budgeting/Overview/index.md)
- SAP SuccessFactors 职位管理与编制（Position Management 的公开概念说明）：<https://help.sap.com/docs/successfactors>
- SQLite 触发器文档（`RAISE(ABORT)` 与 `WHEN` 子句）：<https://www.sqlite.org/lang_createtrigger.html>
