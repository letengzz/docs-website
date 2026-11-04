# 学籍异动与状态机：休学一年，学籍停在原地，成绩还在往里写

一个学生大二下学期办了休学，一年后复学。复学时系统提示「已自动编入 2024 级」，他很高兴——直到毕业审核时发现，自己有 **4 个学分**是休学那个学期产生的。

那 4 学分来自一门「缓考后补录」的课程：成绩在休学期间录进系统，因为**成绩录入页只校验「这门课他选过没有」，不校验「那个学期他在不在籍」**。

::: tip 一句话理解
学籍状态不是一个字段，是**一串带起止日期的区间**；当前状态是「最后一条没写结束日期的区间」，而所有与时间有关的判定（能不能选课、成绩算不算、够不够最长年限）都必须回到区间上去查。
:::

## 一、六态九边：能走的和不能走的

| 从 | 到 | 触发 | 是否允许 |
| --- | --- | --- | --- |
| 在籍 | 休学 | 申请 + 审批 | ✅ |
| 休学 | 复学 | 期满或提前申请 | ✅ |
| 在籍 | 转专业 | 申请 + 考核 + 审批 | ✅ |
| 在籍 | 退学 | 申请或按规定处理 | ✅ |
| 休学 | 退学 | 逾期未复学 | ✅ |
| 在籍 | 毕业 | 审核通过 | ✅ |
| 在籍 → 休学 → 在籍 | 复学后再次休学 | 允许多次，但有累计上限 | ✅（有上限） |
| 退学 | 任何状态 | —— | ❌ |
| 毕业 | 任何状态 | —— | ❌ |

本机 520 条异动事件：休学 210、复学 180、转专业 96、退学 34；覆盖 333 人（11.10% 的学生四年内至少一次异动）。期末状态分布：在籍 2,936、休学 30、退学 34。

::: danger 状态字段的三种错法
1. **用 `status` 单字段存当前值**：改一次就丢一次历史，事后答不出「他什么时候休的学、休了多久」。正确做法是区间表，当前状态由「`to_date IS NULL`」推出。
2. **允许两条区间并存**：`2023-03-01 起休学` 与 `2023-03-15 起转专业` 同时开放，等于这个人同时在两个状态里。必须有部分唯一索引或触发器拦住。
3. **迁移不做白名单**：`UPDATE status='在籍'` 一行就能把退学的人「复活」。状态迁移必须是显式动作，不是一个可以被随便赋值的字段。
:::

## 二、休学期内的成绩：5.71% 的漏洞

本机 210 名休学生里，**12 人**（5.71%）在休学区间内有成绩记录。这个数不大，但它揭示的结构问题很大：

| 校验点 | 校验了什么 | 漏了什么 |
| --- | --- | --- |
| 选课页 | 这个人有没有选这门课 | 那个学期他在不在籍 |
| 成绩录入页 | 这门课有没有他的选课记录 | 成绩发生的时间是否落在在籍区间 |
| 毕业审核 | 学分够不够 | 这些学分是不是「有效期间」获得的 |

三处都只校验了「关系」，没有校验「时间」。**时间维度的约束必须写在库层**，因为任何一个录入入口都可能绕过页面。

```sql
-- 触发器：成绩的发生学期必须落在在籍区间内
CREATE TRIGGER trg_grade_in_status
BEFORE INSERT ON grade
FOR EACH ROW
WHEN NOT EXISTS (
  SELECT 1 FROM student_status s
   WHERE s.student_id = NEW.student_id
     AND s.status IN ('在籍','复学','转专业')
     AND NEW.term_start >= s.from_date
     AND (s.to_date IS NULL OR NEW.term_start < s.to_date)
)
BEGIN
  SELECT RAISE(ABORT, 'grade outside enrolled interval');
END;
```

## 三、转专业：换的不是班级，是方案

转专业这件事，很多人以为改的是「班级字段」。真正要改的是**方案版本**——新专业有新的模块要求、新的先修关系、新的学位课。已修学分要重新认定：

| 认定方式 | 含义 | 本机条数 | 占比 |
| --- | --- | --- | --- |
| 本专业课程 | 新专业方案内的课，直接计入 | 1,625 | 33.9% |
| 直接认定 | 课程名与学分都对得上，等价替换 | 1,371 | 28.6% |
| 替代 | 用 A 课替代 B 课（需审批） | 933 | 19.4% |
| 不认 | 与原专业强相关，新方案不认 | **871** | **18.15%** |

**18.15% 的已修学分不被承认**——这个数必须在转专业**之前**告诉学生，而不是毕业审核时。工程上的做法是把认定规则做成一张表，转专业申请页实时算一遍「你已修的 X 学分里，预计可认定 Y 学分」：

```sql
CREATE TABLE credit_recognize (
  student_id   TEXT NOT NULL,
  from_course  TEXT NOT NULL,
  to_course    TEXT,                    -- NULL = 不认，只留记录
  module       TEXT,                    -- 认定到哪个模块
  credit       REAL NOT NULL CHECK (credit >= 0),
  basis        TEXT NOT NULL CHECK (basis IN ('same','substitute','reject')),
  approved_by  TEXT NOT NULL,
  approved_at  TEXT NOT NULL,
  PRIMARY KEY (student_id, from_course)
);
```

`basis = 'reject'` 也留一行，是这张表最重要的设计：**「不认」也是一个决定，也要有批准人和时间**。只记「认了的」，等于把争议留给四年后。

## 四、最长学习年限：一个必须能算的数

本科基本学制 4 年，最长学习年限通常 6 年（含休学）。这意味着：

```text
最晚毕业时间 = 入学日期 + 6 年
休学 1 年 → 可用在校时间 5 年
休学 2 年 → 可用在校时间 4 年 → 与基本学制相等，没有任何缓冲
```

本机 210 名休学生里，有 30 人仍在休学中（复学 180 人）。按「累计休学不超过 2 年」的口径，只要有人休第二次就会进入倒计时——**而这个倒计时如果不在每次审批时算出来，就只能等学生大五时才发现「你不能再休了」**。

```sql
-- 累计休学天数：从区间表算，不存冗余字段
SELECT s.student_id,
       SUM(julianday(COALESCE(s.to_date, date('now'))) - julianday(s.from_date)) AS days
  FROM student_status s
 WHERE s.status = '休学'
 GROUP BY s.student_id
HAVING days > 365 * 2;
```

## 五、数据模型与两条硬约束

```sql
CREATE TABLE student_status (
  status_id  INTEGER PRIMARY KEY,
  student_id TEXT NOT NULL,
  status     TEXT NOT NULL
             CHECK (status IN ('在籍','休学','复学','转专业','退学','毕业')),
  from_date  TEXT NOT NULL,
  to_date    TEXT,
  reason     TEXT NOT NULL,
  approved_by TEXT,
  CHECK (to_date IS NULL OR to_date > from_date)
);

-- 约束一：同一学生最多一条开放区间
CREATE UNIQUE INDEX ux_status_open ON student_status(student_id) WHERE to_date IS NULL;

-- 约束二：区间不许重叠（用触发器，因为 SQLite 没有 EXCLUDE）
CREATE TRIGGER trg_status_no_overlap
BEFORE INSERT ON student_status
FOR EACH ROW
WHEN EXISTS (
  SELECT 1 FROM student_status s
   WHERE s.student_id = NEW.student_id
     AND NEW.from_date < COALESCE(s.to_date, '9999-12-31')
     AND COALESCE(NEW.to_date, '9999-12-31') > s.from_date
)
BEGIN
  SELECT RAISE(ABORT, 'status interval overlap');
END;
```

两条约束一起，才把「一个人同时处于两个状态」这件事挡在库外。只做第一条，会出现「休学 2023-03-01~2023-07-01」与「复学 2023-06-01~NULL」并存——复学早于休学结束。

::: warning PostgreSQL 有 `EXCLUDE USING gist (student_id WITH =, daterange(from_date, to_date) WITH &&)`，SQLite 没有
这就是为什么本册的示例一定要给触发器版本：换库时约束的写法会变，但**约束本身不能少**。把「不许重叠」写在应用层，等于让它依赖每一个写入路径的自觉。
:::

## 六、本页判据族

本页判据族 `AFN-A` ~ `AFN-H`，共 8 条。

| 判据 | 要求 | 验证方式 |
| --- | --- | --- |
| `AFN-A` | 学籍状态以区间存储，当前状态由开放区间推出 | `ux_status_open` 唯一索引存在 |
| `AFN-B` | 同一学生的状态区间不允许重叠 | 触发器或 `EXCLUDE` 约束存在，重叠插入报错 |
| `AFN-C` | 状态迁移走白名单，退学/毕业为终态 | 迁移表九边可查，终态无出边 |
| `AFN-D` | 成绩的发生学期必须落在在籍区间内 | 触发器 `trg_grade_in_status` 存在，负向用例失败 |
| `AFN-E` | 转专业的学分认定逐条留痕，含「不认」 | `credit_recognize.basis` 三值，`reject` 也入库 |
| `AFN-F` | 累计休学时长从区间算，不存冗余字段 | 一条 `SUM(julianday(...))` 可算出 |
| `AFN-G` | 异动必须带审批人与理由 | `approved_by`、`reason` 非空 |
| `AFN-H` | 异动后方案版本按规则更新（转专业换版、休学不换） | 转专业记录能查出 `program_version` 变更 |

## 七、验证方式

```shell
# 1. 区间重叠必须被拒（期望：overlap / ok）
python3 - <<'PY'
import sqlite3
c = sqlite3.connect(":memory:")
c.executescript("""
CREATE TABLE student_status(student_id TEXT, status TEXT, from_date TEXT, to_date TEXT);
CREATE TRIGGER trg_no_overlap BEFORE INSERT ON student_status
FOR EACH ROW WHEN EXISTS (
  SELECT 1 FROM student_status s WHERE s.student_id = NEW.student_id
    AND NEW.from_date < COALESCE(s.to_date,'9999-12-31')
    AND COALESCE(NEW.to_date,'9999-12-31') > s.from_date)
BEGIN SELECT RAISE(ABORT,'overlap'); END;
INSERT INTO student_status VALUES('S1','休学','2023-03-01','2023-07-01');
""")
try:
    c.execute("INSERT INTO student_status VALUES('S1','复学','2023-06-01',NULL)")
    print("ok")            # 不该出现
except sqlite3.IntegrityError as e:
    print("overlap")       # 期望
PY

# 2. 休学累计时长（期望：366.0 与 >365 的名单）
python3 - <<'PY'
import sqlite3
c = sqlite3.connect(":memory:")
c.execute("CREATE TABLE student_status(student_id TEXT, status TEXT, from_date TEXT, to_date TEXT)")
c.executemany("INSERT INTO student_status VALUES(?,?,?,?)", [
    ("S1","休学","2023-03-01","2024-03-01"),
    ("S1","复学","2024-03-01",None),
    ("S2","休学","2024-09-01","2025-01-10"),
])
q = """SELECT student_id, SUM(julianday(COALESCE(to_date, date('now'))) - julianday(from_date)) d
         FROM student_status WHERE status='休学' GROUP BY student_id HAVING d > 365"""
print(*c.execute(q).fetchone(), sep=" ")
PY
```

第 1 步期望输出 `overlap`：复学日期落在休学区间内，被触发器拦下。若输出 `ok`，说明触发器没建成，这套数据里「一个人同时在两个状态」只是时间问题。

第 2 步期望 `S1 366.0`：S1 休了整一年（2023 年是闰年后的平年，`julianday` 差 366 天），S2 只有 131 天，不进名单。

## 参考资料

- 《普通高等学校学生管理规定》（教育部令第 41 号）第三章第二节：休学、复学与退学的条件；第三节：转专业与转学。
- 各高校《学籍管理规定》通行条款：最长学习年限一般为基本学制加两年，休学累计不超过两年。
- PostgreSQL 文档 *Range Types*：`EXCLUDE USING gist` 与 `daterange` 的重叠约束写法。
- 与本页相邻：[培养方案与课程库](../Program/index.md)、[学分构成与毕业审核](../CreditAudit/index.md)、[总览：八段链](../Overview/index.md)。
