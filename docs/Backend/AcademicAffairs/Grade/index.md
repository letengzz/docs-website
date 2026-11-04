# 成绩、重修与绩点换算：四个绩点口径，四个排名

学院换了教务系统，公示的专业排名重新发了一遍。一个学生从第 12 名掉到第 66 名，成绩一分没变。

他去问，教务处给了两个说法：旧系统用「4.0 分段、学分加权」，新系统用「5 分制、学分加权」。**两套都是标准算法，都写进了学生手册**——只是手册的第 37 页写着「绩点按 4.0 制计算」，第 41 页的示例表用的是 5 分制。

::: tip 一句话理解
绩点不是成绩的函数，是 **「成绩 + 换算表 + 重选取舍 + 分母口径」四个变量的函数**；四个变量里任意一个变了，排名就变，而成绩一分没动。
:::

## 一、四个口径，四个数

同一批 3,000 名学生 / 150,000 条成绩（均值 79 分左右）：

| 口径 | 算法 | 本机读数 | 与前一个的差 |
| --- | --- | --- | --- |
| 4.0 分段（学分加权） | `Σ(绩点 × 学分) / Σ学分` | **2.763** | —— |
| 4.0 分段（门数平均） | `Σ绩点 / 门数` | **2.762** | −0.001 |
| 5 分制（`(分数−50)/10`） | `Σ(绩点 × 学分) / Σ学分` | **2.907** | +0.144 |
| 百分制（学分加权） | `Σ(分数 × 学分) / Σ学分` | **79.05** | 量纲不同，不可比 |

两个观察：

1. **加权与不加权只差 0.001**：因为本机的学分（2~4）与成绩几乎不相关。一旦「学分高的课恰好分数低」，这个差会放大——**加权与否不是细节，是口径**。
2. **5 分制比 4.0 制高 0.144**：不是错，是刻度不同。把 5 分制当 4.0 制用（比如拿去申请海外院校），会得到一个「看起来很好」的数。

## 二、口径一换，排名就变

| 指标 | 读数 |
| --- | --- |
| 两口径（4.0 ⇄ 5 分制）排名差 ≥ 30 名 | **1,302 / 3,000 = 43.4%** |
| 前 10% 学生里排名差 ≥ 30 名 | 约 1/4 |
| 前 100 名内最大位移 | **66 名** |
| 因口径切换被挤出前 100 名 | **8 人** |

43.4% 这个数说明：**口径不是「换算」，是「重排」**。同一个学生在两套口径下可能相差 66 名，而这 66 名决定了保研资格、奖学金等级、交流项目名额。

::: danger 三件必须固定下来的事
1. **换算表必须版本化**：`gpa_rule(rule_id, version, mapping_json, effective_from)`。学生的绩点必须记录「按哪一版算的」，否则三年后无法复算。
2. **分母口径必须写死**：是「所有修过的课」还是「方案内的课」？是「含重修两次」还是「只算一次」？本机「两行全算」比「取最高」低 0.088，涉及 31,946 学分的分母差。
3. **排名必须与绩点同源**：排名用一条 SQL 从绩点表现算，不要另存一份「排名表」——两份数一定会在某次补考后分叉。
:::

## 三、重修：三种取舍，三个绩点

本机 9,880 条重修与刷分记录（占 6.18%），三种取舍方式：

| 取舍 | 规则 | 绩点 | 计入分母的学分 | 行数 |
| --- | --- | --- | --- | --- |
| 取最高 | 同一课多次成绩取最高分 | **2.830** | 487,176 | 150,000 |
| 取最新 | 取最后一次（含刷分失败） | **2.812** | 487,176 | 150,000 |
| 两行全算 | 每次成绩都进分母 | **2.742** | 519,122 | 159,880 |

三种都是「有据可依」的做法，差别在**对谁有利**：

- **取最高**：对学生最有利，也最常见；副作用是「刷分」动机强，一门课可以考五次取最好。
- **取最新**：抑制刷分，但惩罚「想学好却考砸了」的学生；本机比取最高低 0.018。
- **两行全算**：分母里同一门课算两次，等于**重修一次就稀释一次绩点**；本机低 0.088，是三种里最狠的。

::: warning 「两行全算」还会让学分总数虚高
本机两行全算的分母是 519,122 学分，比取最高多 **31,946 学分**。如果毕业审核也用这个数，学生会「因为重修而多出学分」——总学分够了，实际一门课没过。
:::

## 四、绩点重算的时点：谁先谁后

成绩不是一次到齐的：正考、补考、缓考、重修、申诉改分，最晚的可能在毕业前一周才落库。每一次落库都可能改变绩点，而绩点又被排名、奖学金、保研、毕业审核引用。

| 时点 | 谁在用 | 用错了会怎样 |
| --- | --- | --- |
| 成绩发布 T+1 | 学生查分、排名公示 | 补考成绩晚到，公示的排名是错的 |
| 每学期末 | 奖学金评定 | 用学期绩点还是累计绩点，结果不同 |
| 毕业前 | 学位审核 | 缓考未出分，被算成 0 分 |
| 出证后 | 成绩单、学历注册 | 改分后纸质成绩单与系统不一致（见[成绩单页](../Transcript/index.md)） |

工程上的做法是**让绩点永远能被重算**，而不是「存一份算好的」：`gpa_snapshot(student_id, rule_id, term, computed_at, value)` 只作为留痕，任何对外数字都从 `grade` 现算。

## 五、数据模型

```sql
-- 成绩：追加式，attempt_no 区分正考/补考/重修/刷分
CREATE TABLE grade (
  grade_id   INTEGER PRIMARY KEY,
  student_id TEXT NOT NULL,
  course_id  TEXT NOT NULL,
  attempt_no INTEGER NOT NULL CHECK (attempt_no BETWEEN 1 AND 9),
  term       TEXT NOT NULL,
  score      REAL CHECK (score BETWEEN 0 AND 100),
  state      TEXT NOT NULL DEFAULT 'scored'
             CHECK (state IN ('scored','deferred','absent','exempt')),
  UNIQUE (student_id, course_id, attempt_no)
);

-- 换算表：一版一行，mapping 存 JSON，生效期不可重叠
CREATE TABLE gpa_rule (
  rule_id        TEXT NOT NULL,
  version        INTEGER NOT NULL,
  name           TEXT NOT NULL,          -- '4.0 分段' / '5 分制'
  mapping_json   TEXT NOT NULL,          -- [{"min":90,"gp":4.0}, ...]
  effective_from TEXT NOT NULL,
  PRIMARY KEY (rule_id, version)
);

-- 留痕：算过一次就留一条，但对外数字仍以现算为准
CREATE TABLE gpa_snapshot (
  student_id  TEXT NOT NULL,
  rule_id     TEXT NOT NULL,
  rule_version INTEGER NOT NULL,
  term        TEXT,                      -- NULL = 累计
  value       REAL NOT NULL,
  computed_at TEXT NOT NULL,
  PRIMARY KEY (student_id, rule_id, rule_version, term, computed_at)
);
```

`state` 这一列是关键：`deferred`（缓考）与 `absent`（缺考）都不进绩点分母，而 `scored` 里的 0 分要进。**只用一个 `score` 列时，这三件事无法区分。**

## 六、绩点重算的一条 SQL

```sql
-- 累计绩点（4.0 分段、学分加权、取最高、排除缓考与缺考）
WITH best AS (
  SELECT g.student_id, g.course_id, MAX(g.score) AS score
    FROM grade g
   WHERE g.state = 'scored'
   GROUP BY g.student_id, g.course_id
),
pt AS (
  SELECT b.student_id, c.credit,
         CASE WHEN b.score >= 90 THEN 4.0 WHEN b.score >= 85 THEN 3.7
              WHEN b.score >= 82 THEN 3.3 WHEN b.score >= 78 THEN 3.0
              WHEN b.score >= 75 THEN 2.7 WHEN b.score >= 72 THEN 2.3
              WHEN b.score >= 68 THEN 2.0 WHEN b.score >= 64 THEN 1.5
              WHEN b.score >= 60 THEN 1.0 ELSE 0.0 END AS gp
    FROM best b JOIN course c ON c.course_id = b.course_id
)
SELECT student_id,
       ROUND(SUM(gp * credit) * 1.0 / SUM(credit), 4) AS gpa,
       SUM(credit) AS credits
  FROM pt GROUP BY student_id;
```

`MAX(g.score)` 就是「取最高」，`state = 'scored'` 就是「排除缓考缺考」，`JOIN course` 取学分就是「学分加权」。**三个口径选择都体现在这三行里**，换任一版本都要改这一处——所以它必须只有一处。

## 七、本页判据族

本页判据族 `AFG-A` ~ `AFG-H`，共 8 条。

| 判据 | 要求 | 验证方式 |
| --- | --- | --- |
| `AFG-A` | 成绩追加式，`(student, course, attempt_no)` 唯一 | 同一课多次成绩可共存 |
| `AFG-B` | 换算表版本化，绩点可追溯到 `rule_version` | `gpa_rule` 有 `(rule_id, version)` 主键 |
| `AFG-C` | 重选取舍（最高/最新/全算）写在一处 SQL，且可切换 | 一处 `WITH best`，改 `MAX` 或 `ORDER BY` 即可切换 |
| `AFG-D` | 缓考、缺考、免修与 0 分可区分 | `grade.state` 四值，绩点分母排除前三者 |
| `AFG-E` | 加权与不加权是两个明确口径，不混用 | 报表注明「学分加权」或「门数平均」 |
| `AFG-F` | 排名与绩点同源（同一条 SQL 结果） | 排名表由绩点现算，不另存 |
| `AFG-G` | 对外数字可重算，快照只作留痕 | `gpa_snapshot` 存在但查询不用它 |
| `AFG-H` | 成绩变更留痕（原值、新值、操作人、时间） | 变更表或审计日志，含 `old_score` |

## 八、验证方式

```shell
# 1. 四口径（期望：2.763 2.762 2.907 79.05）
python3 - <<'PY'
import random, statistics as st
random.seed(20261105)
def gp4(x):
    for lo, g in [(90,4.0),(85,3.7),(82,3.3),(78,3.0),(75,2.7),(72,2.3),(68,2.0),(64,1.5),(60,1.0)]:
        if x >= lo: return g
    return 0.0
def gp5(x): return max(0.0, min(5.0, (x-50)/10))
rows = []
for s in range(3000):
    base = random.gauss(79, 7)
    for c in range(50):
        rows.append((s, c, random.choice([2,3,4,4]), max(0, min(100, random.gauss(base, 9)))))
def gpa(rs, fn, w=True):
    tot = sum(r[2] for r in rs)
    return sum(fn(r[3])*r[2] for r in rs)/tot if w else st.mean(fn(r[3]) for r in rs)
print(round(gpa(rows,gp4),3), round(gpa(rows,gp4,False),3), round(gpa(rows,gp5),3), round(gpa(rows,lambda x:x),2))
PY

# 2. 重修三口径（期望：2.83 2.812 2.742 150000 159880）
python3 - <<'PY'
import random, statistics as st
from collections import defaultdict
random.seed(20261105)
def gp4(x):
    for lo, g in [(90,4.0),(85,3.7),(82,3.3),(78,3.0),(75,2.7),(72,2.3),(68,2.0),(64,1.5),(60,1.0)]:
        if x >= lo: return g
    return 0.0
rows = []
for s in range(3000):
    base = random.gauss(79, 7)
    for c in range(50):
        rows.append((s, c, random.choice([2,3,4,4]), max(0, min(100, random.gauss(base, 9))), 1))
random.seed(20261106)
fails = [r for r in rows if r[3] < 60]
for r in random.sample(fails, int(len(fails)*0.6)):
    rows.append((r[0], r[1], r[2], min(100, max(0, random.gauss(73, 7))), 2))
passed = [r for r in rows if r[3] >= 60 and r[4] == 1]
for r in random.sample(passed, int(len(passed)*0.04)):
    rows.append((r[0], r[1], r[2], min(100, max(0, random.gauss(r[3]-3, 8))), 2))
def pick(pol):
    if pol == "all": return rows
    agg = {}
    for r in rows:
        k = (r[0], r[1])
        if k not in agg: agg[k] = r
        elif pol == "max": agg[k] = max(agg[k], r, key=lambda x: x[3])
        else: agg[k] = r
    return list(agg.values())
def gpa(rs, fn):
    tot = sum(r[2] for r in rs)
    return sum(fn(r[3])*r[2] for r in rs)/tot
out = []
for pol in ("max", "latest", "all"):
    rs = pick(pol); out.append(round(gpa(rs, gp4), 3))
print(*out, len(pick("max")), len(rows))
PY
```

第 1 步的四个数应与正文一致；如果第二、三个数恰好相等，说明学分与成绩无关，加权在这组数据上不起作用。第 2 步的三个绩点差 **0.088**，就是「重修一次稀释一次」的价格——它不是算法差别，是**规则选择**。

## 参考资料

- 《普通高等学校学生管理规定》（教育部令第 41 号）第三章第四节：考核成绩记载与重修。
- 教育部《关于加强普通高等学校学生学业成绩管理的通知》相关条款：成绩记载应真实、完整、可追溯。
- 各高校《学分制管理办法》通行做法：4.0 制或 5 分制、学分加权、重修取最高。
- IMS Global *OneRoster 1.2*：`result` 资源与 `scoreScale` 的建模方式。
- 与本页相邻：[考试安排与考场容量](../Exam/index.md)、[学分构成与毕业审核](../CreditAudit/index.md)、[成绩单、证明与快照](../Transcript/index.md)。
