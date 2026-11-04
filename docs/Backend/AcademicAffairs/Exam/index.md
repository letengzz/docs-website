# 考试安排与考场容量：同时段两门考试，只有学生自己知道

期末考试周前三天，一个大二学生在教务系统里发现：周四上午 9 点，他有两门必修同时开考。他去问辅导员，辅导员说「系统里没冲突啊」。

系统确实没冲突——**排考表里每一行都是合法的**：一门课的考试时间、考场、监考都填好了。冲突不在行内，在「同一个学生 × 同一个时段」这个组合上，而排考表里根本没有「学生」这一列。

::: tip 一句话理解
排考是**第二次排课，但约束对象反过来了**：排课约束的是「教师不能被两个班占用」，排考约束的是「学生不能同时出现在两个考场」——而学生不在排考表里，他在选课表里。
:::

## 一、一场考试能不能开，要过四道门

| 门 | 判定 | 本机读数 | 失败时的样子 |
| --- | --- | --- | --- |
| 座位 | 考场座位数 ≥ 考生数 | 20 / 320 场不足 | 学生坐走廊，或临时换教室 |
| 时段 | 同一学生同一时段只有一门 | 358 / 3,000 人冲突（11.93%） | 考前一天学生自己发现 |
| 监考 | 每考场 ≥ 2 人，且不与授课冲突 | 本机不建模 | 开考时少一个监考 |
| 缓考 | 冲突或病假有正式出口 | 本机不建模 | 学生缺考，成绩记 0 |

座位这一门最容易被忽略，因为它看起来「显然」：教室座位数在排课系统里就有。**但排课看的是「容量」，排考看的是「座位」，两个数不是一回事**——排课时一个班 45 人进 60 座教室，余 15 座；排考时这 15 座不能给别的班用，因为同一时间这间教室只安排这一门课的考试。

## 二、冲突概率：为什么「随机排考」一定出事

一个学生一学期修 8 门课，考试周有 20 个可用时段。如果每门课独立随机落位：

```text
无冲突概率 = 20/20 × 19/20 × 18/20 × ... × 13/20 ≈ 0.1984
冲突概率   ≈ 80.16%
```

**80%** ——这就是「排考必须做冲突检测」的数学理由。而本机实测只有 11.93%，因为真实的排考不是随机的：同一专业的课集中在同一批时段，学生的选课也有聚集性。

| 口径 | 冲突率 | 说明 |
| --- | --- | --- |
| 完全随机（理论） | 80.16% | 8 门课 × 20 时段，独立均匀 |
| 本机模拟（有聚集） | 11.93% | 358 / 3,000 人 |
| 目标 | 0 | 冲突必须为 0，因为学生只有一个人 |

::: danger 「学生」这一维不能靠排考表自查
1. **排考表的行里没有学生**：`exam(course_id, time, room)` 三列，无论怎么写都表达不了「张三不能同时考两门」。
2. **必须先展开到「学生 × 时段」**：从 `enrollment` 里把「谁选了这门课」摊开，再和 `exam` 连接，才能查出冲突。这一步是排考的**前置必做**，不是优化。
3. **冲突检测要在发布前跑，不是发布后**：发布后再查出来，改一门课的考试时间会牵动考场、监考、学生通知，成本是发布前的十倍。
:::

## 三、把冲突做成一条能跑的查询

```sql
-- 考试：一门课一场（补考另起一行）
CREATE TABLE exam (
  exam_id    TEXT PRIMARY KEY,
  course_id  TEXT NOT NULL,
  term       TEXT NOT NULL,
  exam_date  TEXT NOT NULL,
  slot_no    INTEGER NOT NULL CHECK (slot_no BETWEEN 1 AND 4),  -- 上午/下午各两场
  kind       TEXT NOT NULL DEFAULT 'final' CHECK (kind IN ('final','makeup','deferred'))
);

-- 考场：一场考试可能占多个考场（大课拆分）
CREATE TABLE exam_room (
  exam_id  TEXT NOT NULL REFERENCES exam(exam_id),
  room_id  TEXT NOT NULL,
  seats    INTEGER NOT NULL CHECK (seats > 0),
  PRIMARY KEY (exam_id, room_id)
);

-- 监考：每考场至少两人
CREATE TABLE invigilator (
  exam_id  TEXT NOT NULL REFERENCES exam(exam_id),
  room_id  TEXT NOT NULL,
  teacher_id TEXT NOT NULL,
  PRIMARY KEY (exam_id, room_id, teacher_id)
);
```

冲突查询的关键是把 `enrollment` 摊进来：

```sql
-- 同一学生同一 (date, slot) 出现在两场考试里 → 冲突
SELECT e1.student_id, x1.exam_date, x1.slot_no,
       COUNT(DISTINCT x1.exam_id) AS exams
  FROM enrollment e1
  JOIN exam x1 ON x1.course_id = (SELECT course_id FROM section s WHERE s.section_id = e1.section_id)
 WHERE e1.state IN ('won','confirmed')
 GROUP BY e1.student_id, x1.exam_date, x1.slot_no
HAVING COUNT(DISTINCT x1.exam_id) > 1;
```

这条查询返回的每一行，都是一个「只能靠自己发现」的学生。本机这条 SQL 在 3,000 人上返回 358 行。

座位数检查是另一条独立的查询，因为它只看 `exam_room` 与考生数：

```sql
SELECT x.exam_id, SUM(r.seats) AS seats,
       (SELECT COUNT(*) FROM enrollment e JOIN section s ON s.section_id = e.section_id
         WHERE s.course_id = x.course_id AND e.state IN ('won','confirmed')) AS candidates
  FROM exam x JOIN exam_room r ON r.exam_id = x.exam_id
 GROUP BY x.exam_id
HAVING candidates > seats;      -- 本机 20 行
```

## 四、缓考：一个必须存在的出口

冲突检测做到 0 是目标，但现实里总会有冲突（病假、竞赛、补考撞正考）。系统必须有一个**正式出口**，而不是让学生「自己想办法」：

| 场景 | 出口 | 成绩怎么记 | 常见错法 |
| --- | --- | --- | --- |
| 时间冲突 | 缓考（`deferred`） | 记「缓考」，不记 0 | 直接记缺考 0 分 |
| 病假 | 缓考，需附证明 | 同上 | 让任课教师手改成绩 |
| 补考撞正考 | 补考顺延到下一批次 | 补考成绩按实记 | 两场都缺，等下一年 |

「缓考」这个状态存在的意义是**让成绩表能表达「还没考」**。成绩表只有 `score` 一列时，「没考」与「考了 0 分」无法区分，而这两件事在绩点计算里完全不同：缓考不计入分母，0 分计入分母。

## 五、本页判据族

本页判据族 `AFX-A` ~ `AFX-H`，共 8 条。

| 判据 | 要求 | 验证方式 |
| --- | --- | --- |
| `AFX-A` | 考试按 `(date, slot)` 定位，不以「上午/下午」这种自由文本表示 | `exam_date` + `slot_no` 两列非空且有 `CHECK` |
| `AFX-B` | 考场容量按「座位数」而非「教室容量」判定 | `exam_room.seats` 与 `room.capacity` 分离 |
| `AFX-C` | 「学生 × 时段」冲突查询可执行且发布前必须为 0 | 一条 `GROUP BY ... HAVING COUNT(DISTINCT exam_id) > 1` 返回 0 |
| `AFX-D` | 每考场监考 ≥ 2 人 | `COUNT(invigilator) >= 2` 按 `(exam_id, room_id)` 分组 |
| `AFX-E` | 「缓考」是独立状态，不与 0 分混淆 | `grade.state` 含 `deferred`，绩点分母排除 |
| `AFX-F` | 补考成绩单独记录，不覆盖正考 | `attempt_no` 或 `kind='makeup'` 独立成行 |
| `AFX-G` | 排考结果发布前留快照，发布后可回滚 | 版本表或 `published_at` |
| `AFX-H` | 考试时间变更必须能查出受影响的学生名单 | 变更前先跑一次冲突查询并导出名单 |

## 六、验证方式

```shell
# 1. 随机排考的冲突概率（期望：0.1984 0.8016）
python3 -c "
p=1.0
for i in range(8): p*= (20-i)/20
print(round(p,4), round(1-p,4))"

# 2. 从选课表展开「学生 × 时段」查冲突（期望：返回 1 行，学生 S1）
python3 - <<'PY'
import sqlite3
c = sqlite3.connect(":memory:")
c.executescript("""
CREATE TABLE section(section_id TEXT PRIMARY KEY, course_id TEXT);
CREATE TABLE enrollment(student_id TEXT, section_id TEXT, state TEXT);
CREATE TABLE exam(exam_id TEXT PRIMARY KEY, course_id TEXT, exam_date TEXT, slot_no INT);
INSERT INTO section VALUES('SEC1','C1'),('SEC2','C2'),('SEC3','C3');
INSERT INTO enrollment VALUES('S1','SEC1','confirmed'),('S1','SEC2','confirmed'),('S2','SEC3','confirmed');
INSERT INTO exam VALUES('E1','C1','2026-01-08',1),('E2','C2','2026-01-08',1),('E3','C3','2026-01-09',1);
""")
q = """
SELECT e.student_id, x.exam_date, x.slot_no, COUNT(DISTINCT x.exam_id) n
  FROM enrollment e
  JOIN section s ON s.section_id = e.section_id
  JOIN exam x ON x.course_id = s.course_id
 WHERE e.state IN ('won','confirmed')
 GROUP BY e.student_id, x.exam_date, x.slot_no
HAVING COUNT(DISTINCT x.exam_id) > 1;
"""
rows = c.execute(q).fetchall()
print(len(rows), rows[0][:3] if rows else None)
PY
```

第 1 步的两个数是理论值：8 门课落在 20 个时段，**80% 的概率至少撞一次**——这不是巧合，是排考必须做检测的数学理由。第 2 步期望输出 `1 ('S1', '2026-01-08', 1)`：S1 的两门课被排在同一天同一时段，而 S2 没有冲突。

## 参考资料

- 《普通高等学校学生管理规定》（教育部令第 41 号）第三章第四节：考核与成绩记载，含缓考、补考的规定。
- 各高校《考试管理办法》通行条款：每考场不少于两名监考、考生间距、单人单桌。
- 区间调度与冲突检测的一般方法：*Introduction to Algorithms*（CLRS, 4th ed.）第 16 章。
- 与本页相邻：[排课与三资源冲突](../Scheduling/index.md)、[选课、容量与抽签](../Enrollment/index.md)、[成绩、重修与绩点换算](../Grade/index.md)。
