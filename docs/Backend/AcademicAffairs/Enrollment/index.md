# 选课、容量与抽签：抢课的失败不只在「超选」

选课开放三分钟，一门 45 人的专业选修课报了 181 人。系统没崩，页面也没报错，只是第二天教务发现：这门课的名单有 **120 行**，而课表上写着「容量 45」。

更奇怪的是数据库里另一个数：`used = 14`。**名单 120 行，计数器 14**——这个系统连自己都说不出「到底收了多少人」。

::: tip 一句话理解
选课的容量不是一个数，是**三个数的减法**：名义容量 − 已确认 − 已占位 = 可放出的余量。三个数任何一个没有唯一写入点，超选与「计数器与名单不一致」就会同时发生。
:::

## 一、三个「还有没有位置」

| 口径 | 定义 | 本机取值（最热班） | 说错了会怎样 |
| --- | --- | --- | --- |
| 名义容量 | `section.capacity` | 45 | 与实际教室座位不一致（见[考试页](../Exam/index.md)） |
| 已确认 | `COUNT(enrollment WHERE state='confirmed')` | 45（正确实现） | 用 `used` 计数器代替，就会得到 14 这种数 |
| 已占位 | 选中但未确认（待缴费、待审核） | 0（本机不建模） | 漏算占位 = 超发 |
| 可放余量 | 容量 − 已确认 − 已占位 | 0 | 用「容量 − 已确认」而漏占位，等于给每个人多发一个位 |

**三个数必须来自同一张表的同一时刻**。一旦「已确认」用 `COUNT` 算、「已占位」用计数器读，两个数就永远对不上——不是因为并发，是因为**它们本来就不是同一件事**。

## 二、本机读数：需求、容量与落选

| 指标 | 读数 | 说明 |
| --- | --- | --- |
| 选课请求 | 18,000 条，去重 17,708 | 292 条是重复提交（同一人同一班点两次） |
| 总容量 | 320 班 × 45 = 14,400 | —— |
| 一轮满足 | 10,878 / 17,708 = **61.43%** | 落选 6,830 人次 |
| 爆满班 | 65 / 320 = **20.31%** | 需求 > 容量的班 |
| 需求集中度 | 64 个热门班吃 **55.56%** 请求 | 最热 181 人，中位 33 人 |

61.43% 这个数不是「系统差」，是**课程供给不足**：17,708 条需求对 14,400 个位，缺 3,308 个位，本来就不可能全满足。**但系统必须能说清「谁没选上、为什么」**——这正是抽签规则要解决的问题。

## 三、并发：120 个人是怎么坐进 45 个位的

12 个线程、每个线程抢 10 次，都抢同一个 45 人的班：

| 写法 | 成功 | 失败 | `used` | 明细行 | 结论 |
| --- | --- | --- | --- | --- | --- |
| 先查后改（`SELECT` 后 `UPDATE`） | 120 | 0 | **14** | **120** | 超发 106，且计数器与明细自相矛盾 |
| 条件更新（`UPDATE ... WHERE used < cap`） | 45 | 75 | 45 | 45 | 正确 |
| 先插后判（唯一键 + 事务内回滚） | 45 | 75 | 45 | 45 | 正确 |

第一行是这一页的核心证据：**不是「多收了 75 个人」，而是「120 行明细配一个 14 的计数器」**。因为 12 个线程各自读到 `used=13`，都判断「还有位」，都执行 `used = 14`——**最后一次写覆盖了前面 11 次**（lost update）。明细是 `INSERT`，每次都成功，所以有 120 行。

::: danger 超选的两个来源，缺一不可
1. **读-改-写之间的时间窗**：这是经典竞态，条件更新或行锁能解决。
2. **「判断」与「写入」不在同一个事务里**：即使加了锁，如果「查容量」在事务外、「写名单」在事务内，锁也保护不了那次判断。
:::

三种写法的取舍：

| 写法 | 优点 | 代价 | 适用 |
| --- | --- | --- | --- |
| 条件更新 | 一条 SQL 完成判断与写入，天然原子 | 计数器必须与明细同步维护，否则会漂移 | 容量是「单行热点」的常规做法 |
| 唯一键 + 回滚 | 不依赖计数器，明细本身就是真相 | 冲突时要回滚，事务开销略大 | 容量可以由 `COUNT` 实时算的场景 |
| 分布式锁 | 能跨库、跨服务 | 锁超时、锁续期、锁失效三件事都要处理 | 多实例且容量在缓存里 |

本机的结论是：**只要容量能从明细算出来，就不要维护计数器**。计数器是性能优化，不是事实来源；本机 `used=14` 与 120 行明细的对比，就是「把优化当事实」的代价。

## 四、抽签：规则决定谁被牺牲

爆满班必须抽签。300 人抢 45 个位，两种规则下高年级的中签率：

| 规则 | 高年级中签率 | 整体中签率 | 说明 |
| --- | --- | --- | --- |
| 纯随机 | **16.48%** | 15.0% | 高年级占比 30.3%，中签率与整体接近（差 1.5 个点是抽样波动） |
| 年级优先（高年级先抽） | **49.45%** | 15.0% | 高年级中签率是整体的 3.3 倍 |

两行都是「公平」的，但公平的对象不同：纯随机对**每个人**公平，年级优先对**培养计划**公平（高年级不选上就毕不了业）。**规则必须写在页面上**，否则学生会用「我同班同学选上了」来质疑。

```sql
-- 选课记录：状态机 + 唯一键（同一人同一班只能有一条）
CREATE TABLE enrollment (
  student_id  TEXT NOT NULL,
  section_id  TEXT NOT NULL,
  state       TEXT NOT NULL CHECK (state IN ('applied','won','confirmed','dropped','lost')),
  priority    INTEGER NOT NULL DEFAULT 0,   -- 年级、是否毕业班、是否重修
  applied_at  TEXT NOT NULL,
  PRIMARY KEY (student_id, section_id)
);

-- 抽签结果落表：带规则版本，事后能复算
CREATE TABLE lottery_run (
  section_id TEXT NOT NULL,
  rule       TEXT NOT NULL,                 -- 'random-v1' / 'grade-first-v1'
  quota      INTEGER NOT NULL,
  run_at     TEXT NOT NULL,
  PRIMARY KEY (section_id, rule, run_at)
);
```

`PRIMARY KEY (student_id, section_id)` 顺带解决了 292 条重复提交：重复的那条直接撞主键，不需要业务代码去重。

## 五、先修校验：放在「选的那一刻」，还是「审的那一刻」

本机的 1,286 条「有先修要求」的选课记录里，**819 条**（63.69%）的先修课并未通过。这个数看起来荒谬，但它测的是一件真事：**这批选课请求与修读顺序无关**，所以先修几乎必然不满足。

::: warning 63.69% 是一个上界，不是「学生爱违规」
真实系统里，选课页面会按「已修课程」过滤可选列表，这个数会掉到个位数。本机这组数据是**不做任何过滤时的上界**，它的价值不在数值，而在它证明的那件事：

- 先修校验如果放在**毕业审核**那一刻，代价是「四年后告诉学生这门课白修了」；
- 放在**选课**那一刻，代价是「当下少一个选项」。

同一件事，两个时点，成本差四年。
:::

## 六、错峰：把峰值削掉三分之二

18,000 条请求集中在开放后的 3 分钟：

| 策略 | 峰值 | 说明 |
| --- | --- | --- |
| 全放开 | 100 rps | 平均值 100，但前 10 秒可能是 10 倍 |
| 按年级三段错峰 | 33 rps | 高年级先开 20 分钟，每段只放一个年级 |

错峰不是性能优化，是**公平性设计**：全放开时，网速快的人赢；按年级错峰时，最需要这门课的人先选。

## 七、本页判据族

本页判据族 `AFE-A` ~ `AFE-H`，共 8 条。

| 判据 | 要求 | 验证方式 |
| --- | --- | --- |
| `AFE-A` | 容量判定与写入在同一条语句或同一事务内完成 | 代码里不存在「先 `SELECT used` 再 `UPDATE`」的路径 |
| `AFE-B` | 已确认人数以明细 `COUNT` 为准，计数器只作缓存且可重建 | 一条 SQL 能从 `enrollment` 重算出 `used` |
| `AFE-C` | 同一人同一班唯一，重复提交撞主键 | `PRIMARY KEY (student_id, section_id)` |
| `AFE-D` | 选课状态机五态，非法迁移被拒 | `CHECK (state IN (...))` + 迁移校验 |
| `AFE-E` | 抽签规则版本化并落表，结果可复算 | `lottery_run.rule` 非空，同规则同数据可重放 |
| `AFE-F` | 落选学生可见「为什么没选上」 | `lost` 状态带 `reason`（容量/先修/时间冲突） |
| `AFE-G` | 先修校验发生在选课时刻，且可解释 | 选课接口返回 `prereq_missing` 明细 |
| `AFE-H` | 开放时段按年级错峰，配置可查 | 开放窗口表含 `grade` 与起止时间 |

## 八、验证方式

```shell
# 1. 并发抢课：两种写法的「明细行 vs 计数器」（期望：条件更新 45 45；先查后改 明细 > 45）
python3 - <<'PY'
import os, sqlite3, tempfile, threading
def race(mode):
    path = tempfile.mktemp(suffix=".db")
    c0 = sqlite3.connect(path); c0.execute("PRAGMA journal_mode=WAL")
    c0.executescript("""CREATE TABLE sec(id TEXT PRIMARY KEY, cap INT, used INT);
                        INSERT INTO sec VALUES('S',45,0);
                        CREATE TABLE enr(stu TEXT PRIMARY KEY, sec TEXT);""")
    c0.commit(); c0.close()
    ok, bad = [0], [0]
    def w(tid):
        c = sqlite3.connect(path, timeout=30); c.execute("PRAGMA busy_timeout=30000")
        for k in range(10):
            stu = f"T{tid}-{k}"
            try:
                if mode == "rtw":
                    used, cap = c.execute("SELECT used, cap FROM sec WHERE id='S'").fetchone()
                    if used < cap:
                        c.execute("INSERT INTO enr VALUES(?, 'S')", (stu,))
                        c.execute("UPDATE sec SET used=? WHERE id='S'", (used + 1,))
                        c.commit(); ok[0] += 1
                    else:
                        bad[0] += 1
                else:
                    cur = c.execute("UPDATE sec SET used=used+1 WHERE id='S' AND used<cap")
                    if cur.rowcount == 1:
                        c.execute("INSERT INTO enr VALUES(?, 'S')", (stu,)); c.commit(); ok[0] += 1
                    else:
                        c.commit(); bad[0] += 1
            except Exception:
                c.rollback(); bad[0] += 1
        c.close()
    ts = [threading.Thread(target=w, args=(i,)) for i in range(12)]
    [t.start() for t in ts]; [t.join() for t in ts]
    c = sqlite3.connect(path)
    used = c.execute("SELECT used FROM sec").fetchone()[0]
    rows = c.execute("SELECT count(*) FROM enr").fetchone()[0]
    c.close(); os.unlink(path)
    return ok[0], used, rows
print("conditional", *race("cond"))
print("read-then-write", *race("rtw"))
PY

# 2. 抽签规则对高年级命中率的影响（期望：16.48 49.45）
python3 - <<'PY'
import random
random.seed(20261105)
pool = [{"id": f"S{i}", "grade": 2022 if i < 91 else 2023} for i in range(300)]
senior = [s for s in pool if s["grade"] == 2022]
rnd = {s["id"] for s in random.sample(pool, 45)}
pri = {s["id"] for s in sorted(pool, key=lambda s: (s["grade"], random.random()))[:45]}
print(round(sum(1 for s in senior if s["id"] in rnd)/len(senior)*100, 2),
      round(sum(1 for s in senior if s["id"] in pri)/len(senior)*100, 2))
PY
```

第 1 步的两种写法应给出**结构性差异**：条件更新那行三个数满足 `成功 = used = 明细`；先查后改那行 `明细 > used`（本机 120 对 14）。若两者相等，说明线程没真正并发起来（GIL 下也可能出现），把线程数提到 32 再跑一次。

第 2 步的两个数应与正文一致（`16.48 49.45`）：纯随机接近 45/300 = 15%，年级优先把高年级推到约 49%——**同一个容量，两套规则，两种命运**。

## 参考资料

- 教育部《普通高等学校学生管理规定》（教育部令第 41 号）第三章第四节：课程考核与成绩记载，含重修、免修的申请。
- 《普通高等学校本科专业类教学质量国家标准》：选修课比例要求，是「容量不足」的结构性原因。
- IMS Global *OneRoster 1.2*：`enrollment` 资源的状态与角色定义。
- 与本页相邻：[排课与三资源冲突](../Scheduling/index.md)、[考试安排与考场容量](../Exam/index.md)、[成绩、重修与绩点换算](../Grade/index.md)。
