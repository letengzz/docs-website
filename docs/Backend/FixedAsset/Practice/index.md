# 实战：从建卡到处置的可运行闭环

<p style="text-align:center;"><img src="../assets/fa-logo.png" alt="资产台账与折旧摊销" style="zoom:75%;" /></p>

前面九页讲了判据，这一页把它们压成一条能跑的流水：**建库 → 建卡 → 计提 → 变更 → 处置 → 勾稽**。全程只用 SQLite 与 Python 标准库，不需要装任何依赖，跑完能拿到一组确定的数字。

::: tip 一句话理解
**验收不是「看代码写得对不对」，而是「六条查询全是 0」。** 这一页的产物是六条闭合查询与四个必须失败的用例。
:::

本页判据族 `FAX-A` ~ `FAX-H`，共 8 条，定义在最后一节。

## 一、目录结构

```text
fa-demo/
├─ schema.sql        # 建库：7 张表 + 5 个索引
├─ seed.py           # 造数：3 张卡（含 1 张组件）+ 2 期折旧 + 1 次变更 + 1 次处置
├─ run_month.py      # 月度流水：计提 → 凭证 → 勾稽
├─ checks.sql        # 六条闭合查询
└─ must_fail.py      # 四个必须失败的用例
```

## 二、建库：七张表

```sql [schema.sql]
PRAGMA foreign_keys = ON;

CREATE TABLE asset_card (
  card_id        TEXT PRIMARY KEY,
  asset_name     TEXT NOT NULL,
  category_id    TEXT NOT NULL,
  parent_card_id TEXT REFERENCES asset_card(card_id),
  original_cost  NUMERIC(18,2) NOT NULL CHECK (original_cost > 0),
  salvage_value  NUMERIC(18,2) NOT NULL DEFAULT 0
                 CHECK (salvage_value >= 0 AND salvage_value < original_cost),
  useful_life    INTEGER NOT NULL CHECK (useful_life > 0),
  dep_method     TEXT NOT NULL CHECK (dep_method IN ('STRAIGHT','DDB','SYD')),
  in_service_date DATE NOT NULL,
  dept_id        TEXT NOT NULL,
  location       TEXT,
  status         TEXT NOT NULL DEFAULT 'IN_SERVICE'
                 CHECK (status IN ('IN_SERVICE','IDLE','TO_DISPOSE','DISPOSED')),
  disposed_on    DATE,
  CHECK (parent_card_id IS NULL OR parent_card_id <> card_id)
);

CREATE TABLE dep_schedule (
  card_id  TEXT NOT NULL REFERENCES asset_card(card_id),
  seq      INTEGER NOT NULL,
  period   TEXT NOT NULL,                 -- 2026-01
  amount   NUMERIC(18,2) NOT NULL,
  status   TEXT NOT NULL DEFAULT 'PLANNED'
           CHECK (status IN ('PLANNED','POSTED','VOID')),
  PRIMARY KEY (card_id, seq)
);

CREATE TABLE dep_run (
  period  TEXT NOT NULL,
  card_id TEXT NOT NULL REFERENCES asset_card(card_id),
  dept_id TEXT NOT NULL,
  amount  NUMERIC(18,2) NOT NULL,
  PRIMARY KEY (period, card_id)
);

CREATE TABLE asset_change (
  change_id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_id   TEXT NOT NULL REFERENCES asset_card(card_id),
  change_type TEXT NOT NULL
              CHECK (change_type IN ('TRANSFER','IMPROVE','REVISE_LIFE','IMPAIR','SPLIT','DISPOSE')),
  old_value TEXT, new_value TEXT,
  effective_period TEXT NOT NULL,
  reason    TEXT NOT NULL CHECK (length(trim(reason)) > 0)
);

CREATE TABLE asset_impair (
  card_id TEXT NOT NULL REFERENCES asset_card(card_id),
  period  TEXT NOT NULL,
  amount  NUMERIC(18,2) NOT NULL CHECK (amount > 0),
  recoverable NUMERIC(18,2) NOT NULL,
  PRIMARY KEY (card_id, period)
);

CREATE TABLE asset_disposal (
  disposal_id TEXT PRIMARY KEY,
  card_id     TEXT NOT NULL UNIQUE REFERENCES asset_card(card_id),
  disposed_on DATE NOT NULL,
  reason      TEXT NOT NULL,
  price       NUMERIC(18,2) NOT NULL DEFAULT 0,   -- 不含税
  fee         NUMERIC(18,2) NOT NULL DEFAULT 0
);

CREATE TABLE gl_entry (
  entry_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  voucher_no   TEXT NOT NULL,
  period       TEXT NOT NULL,
  account_code TEXT NOT NULL,
  dept_id      TEXT,
  debit        NUMERIC(18,2) NOT NULL DEFAULT 0,
  credit       NUMERIC(18,2) NOT NULL DEFAULT 0,
  source       TEXT NOT NULL,
  source_ref   TEXT NOT NULL,
  CHECK (debit >= 0 AND credit >= 0),
  CHECK (debit = 0 OR credit = 0)
);

CREATE INDEX idx_sched_period ON dep_schedule(period, status);
CREATE INDEX idx_run_dept ON dep_run(period, dept_id);
CREATE INDEX idx_card_dept ON asset_card(dept_id, status);
CREATE UNIQUE INDEX ux_component ON asset_card(parent_card_id, asset_name)
  WHERE parent_card_id IS NOT NULL;
```

跑一遍，确认七张表都在：

```shell
sqlite3 /tmp/fa.db < schema.sql
sqlite3 /tmp/fa.db "SELECT count(*) FROM sqlite_master WHERE type='table';"
# 期望：7（不含 sqlite_sequence）
```

## 三、造数：三张卡 + 两期折旧

```python [seed.py]
import sqlite3
from decimal import Decimal as D, ROUND_HALF_UP

def q(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

con = sqlite3.connect("/tmp/fa.db")
cards = [
    # card_id, 名称, 分类, 父卡, 原值, 残值, 寿命, 方法, 起用日, 部门
    ("FA-0001", "主机",   "MACH", None,   "240000", "0", 120, "STRAIGHT", "2026-01-10", "D01"),
    ("FA-0002", "电机",   "MACH", "FA-0001", "40000", "0",  60, "STRAIGHT", "2026-01-10", "D01"),
    ("FA-0003", "安装费", "MACH", "FA-0001", "20000", "0", 120, "STRAIGHT", "2026-01-10", "D01"),
]
con.executemany("INSERT INTO asset_card(card_id,asset_name,category_id,parent_card_id,"
                "original_cost,salvage_value,useful_life,dep_method,in_service_date,dept_id) "
                "VALUES(?,?,?,?,?,?,?,?,?,?)", cards)

# 生成全生命周期计划：末期取差额（FAD-C）
for cid, _, _, _, cost, salv, life, method, start, _ in cards:
    base = D(cost) - D(salv)
    per = q(base / life)
    paid = D(0)
    for seq in range(1, life + 1):
        amt = per if seq < life else base - paid
        paid += amt
        m = 1 + seq            # 2026-01 起用 → 第 seq 期落在 2026-01 之后的第 seq 个月
        period = f"{2026 + (m - 1) // 12}-{(m - 1) % 12 + 1:02d}"
        con.execute("INSERT INTO dep_schedule(card_id,seq,period,amount) VALUES(?,?,?,?)",
                    (cid, seq, period, str(amt)))
con.commit()
print("计划行数:", con.execute("SELECT count(*) FROM dep_schedule").fetchone()[0])  # 300
```

::: warning 起用日与首期的关系
`in_service_date = 2026-01-10`，按「当月增加次月提」，首期是 2026-02。上面的 `period` 生成逻辑刻意从次月开始，**不要**用「起用月 + seq - 1」——那会多做一期，末期直接越过寿命。
:::

## 四、月度流水：三期，每期四步

```python [run_month.py]
import sqlite3
from decimal import Decimal as D, ROUND_HALF_UP

def q(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

def run(period):
    con = sqlite3.connect("/tmp/fa.db")
    con.execute("BEGIN")
    # ① 取本期应提的计划行（跳过已处置、已作废）
    rows = con.execute("""
        SELECT s.card_id, s.amount, c.dept_id FROM dep_schedule s
          JOIN asset_card c ON c.card_id = s.card_id
         WHERE s.period = ? AND s.status = 'PLANNED'
           AND c.status IN ('IN_SERVICE','IDLE')
    """, (period,)).fetchall()
    # ② 落 run 明细：唯一键保证重跑幂等
    con.executemany("INSERT OR IGNORE INTO dep_run(period,card_id,dept_id,amount) VALUES(?,?,?,?)",
                    [(period, r[0], r[2], r[1]) for r in rows])
    # ③ 计划行置 POSTED
    con.execute("UPDATE dep_schedule SET status='POSTED' WHERE period=? AND status='PLANNED'", (period,))
    # ④ 按部门汇总出一张凭证
    for dept, amt in con.execute("""
        SELECT dept_id, round(sum(amount),2) FROM dep_run WHERE period=? GROUP BY dept_id
    """, (period,)).fetchall():
        vno = f"DEP-{period}-{dept}"
        con.execute("INSERT INTO gl_entry(voucher_no,period,account_code,dept_id,debit,source,source_ref)"
                    " VALUES(?,?,?,?,?,?,?)", (vno, period, "660203", dept, amt, "DEP", f"{period}/{dept}"))
        con.execute("INSERT INTO gl_entry(voucher_no,period,account_code,dept_id,credit,source,source_ref)"
                    " VALUES(?,?,?,?,?,?,?)", (vno, period, "1602", dept, amt, "DEP", f"{period}/{dept}"))
    con.commit()
    n = con.execute("SELECT count(*) FROM dep_run WHERE period=?", (period,)).fetchone()[0]
    tot = con.execute("SELECT round(sum(amount),2) FROM dep_run WHERE period=?", (period,)).fetchone()[0]
    print(period, "卡片", n, "金额", tot)

for p in ("2026-02", "2026-03", "2026-04"):
    run(p)
```

跑出来应该是：

```text
2026-02 卡片 3 金额 2833.34
2026-03 卡片 3 金额 2833.34
2026-04 卡片 3 金额 2833.34
```

`2,833.34` 正是组件法的月折旧合计（2,000.00 + 666.67 + 166.67）。整体法会得到 2,500.00，差 **333.34**。

## 五、六条闭合查询

```sql [checks.sql]
-- ① 计划总额 = 原值 − 残值（逐卡）
SELECT card_id FROM asset_card c
 WHERE round((SELECT sum(amount) FROM dep_schedule d WHERE d.card_id=c.card_id),2)
       <> round(c.original_cost - c.salvage_value, 2);

-- ② 计提过的不重复提（同一 period 一张卡一行）
SELECT card_id, period, count(*) c FROM dep_run GROUP BY card_id, period HAVING c > 1;

-- ③ 应提未提（本期有计划但没落 run）
SELECT s.card_id FROM dep_schedule s
 WHERE s.period='2026-04' AND s.status='PLANNED'
   AND NOT EXISTS (SELECT 1 FROM dep_run r WHERE r.period=s.period AND r.card_id=s.card_id);

-- ④ 折旧明细 ⇄ 累计折旧科目（差额）
SELECT round((SELECT sum(amount) FROM dep_run),2)
     - round((SELECT sum(credit-debit) FROM gl_entry WHERE account_code='1602'),2);

-- ⑤ 凭证借贷平衡（任一凭证借方合计 = 贷方合计）
SELECT voucher_no FROM gl_entry GROUP BY voucher_no
 HAVING round(sum(debit),2) <> round(sum(credit),2);

-- ⑥ 已处置卡片不得再计提
SELECT r.card_id, r.period FROM dep_run r JOIN asset_card c ON c.card_id=r.card_id
 WHERE c.status='DISPOSED' AND r.period > strftime('%Y-%m', c.disposed_on);
```

①~③、⑤、⑥ 期望 **0 行**，④ 期望 **0.0**。

```shell
sqlite3 /tmp/fa.db < checks.sql
# 期望：除 ④ 输出 0.0 外，其余无输出
```

## 六、四个必须失败的用例

正向跑通只说明「路能走」，负向跑失败才说明「门关着」。四个用例都用标准库断言，失败才打印 PASS：

```python [must_fail.py]
import sqlite3, sys

con = sqlite3.connect("/tmp/fa.db")
con.execute("PRAGMA foreign_keys = ON")
fails = []

def must_fail(sql, label, args=()):
    try:
        con.execute(sql, args)
        con.commit()
    except Exception as e:
        print(f"PASS {label} -> {type(e).__name__}")
        return
    fails.append(label)
    print(f"FAIL {label} 未失败（门没关）")

must_fail("INSERT INTO asset_card(card_id,asset_name,category_id,original_cost,salvage_value,"
          "useful_life,dep_method,in_service_date,dept_id) "
          "VALUES('FA-X','残值越界','MACH',1000,1000,60,'STRAIGHT','2026-01-01','D01')",
          "残值 >= 原值 必须被拒")

must_fail("INSERT INTO dep_run(period,card_id,dept_id,amount) VALUES('2026-02','FA-0001','D01','2000')",
          "同一 period + card 重复计提必须被拒")

must_fail("INSERT INTO asset_change(card_id,change_type,effective_period,reason) "
          "VALUES('FA-0001','REVISE_LIFE','2026-05','')",
          "空理由的变更必须被拒")

must_fail("INSERT INTO gl_entry(voucher_no,period,account_code,debit,credit,source,source_ref) "
          "VALUES('V-X','2026-02','1602',100,100,'DEP','x')",
          "借贷同时非 0 必须被拒")

sys.exit(1 if fails else 0)
```

```shell
python3 must_fail.py
# 期望：四行 PASS，退出码 0
echo $?
# 期望：0
```

## 七、变更与处置：接力验证

```shell
# 1) 跑满三期后（2026-04 期末）把 FA-0002（电机）寿命改成 84 期 → 未来适用
sqlite3 /tmp/fa.db "
INSERT INTO asset_change(card_id,change_type,old_value,new_value,effective_period,reason)
VALUES('FA-0002','REVISE_LIFE','60','84','2026-05','设备实际使用强度低于预期');
-- 已提 3 期（2026-02 ~ 2026-04），把第 4 期起的计划作废
UPDATE dep_schedule SET status='VOID' WHERE card_id='FA-0002' AND seq > 3;
"
sqlite3 /tmp/fa.db "SELECT round((40000 - (SELECT sum(amount) FROM dep_schedule
  WHERE card_id='FA-0002' AND status='POSTED')) / 81, 2);"
# 期望：469.14（新基数 37,999.99 ÷ 剩余 81 期；原 666.67，降 29.6%）

# 2) 处置 FA-0003（安装费随主机），售价 0，清理费 200
sqlite3 /tmp/fa.db "
INSERT INTO asset_disposal VALUES('D-0001','FA-0003','2026-06-15','SCRAP',0,200);
UPDATE asset_card SET status='DISPOSED', disposed_on='2026-06-15' WHERE card_id='FA-0003';"
sqlite3 /tmp/fa.db "SELECT count(*) FROM dep_run r JOIN asset_card c ON c.card_id=r.card_id
 WHERE c.status='DISPOSED' AND r.period > '2026-06';"
# 期望：0（处置次月起不再计提）
```

## 八、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `FAX-A` | `schema.sql` 一次执行成功，建出 7 张表 | 执行后 `count(*) = 7` |
| `FAX-B` | 计划生成满足「末期取差额」，逐卡合计 = 基数 | 查询 ① 返回 0 行 |
| `FAX-C` | 月度流水四步在一个事务里 | 中途异常时 `dep_run` 与 `dep_schedule` 状态一致 |
| `FAX-D` | 重跑同一期不改变行数与金额 | 连跑两次，`count(*)` 与 `sum` 不变 |
| `FAX-E` | 六条闭合查询全部为 0（或 0.0） | 跑 `checks.sql` 无输出 |
| `FAX-F` | 四个负向用例全部失败 | `must_fail.py` 输出四行 PASS，退出码 0 |
| `FAX-G` | 变更后旧计划置 VOID 而非删除 | `dep_schedule` 里能看到作废行 |
| `FAX-H` | 处置次月起不再计提 | 查询 ⑥ 返回 0 行 |

## 验证方式

```shell
# 1) 建库成功：应输出 7
sqlite3 /tmp/fa.db "SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
# 期望：7

# 2) 三期折旧合计：应输出 8500.02
sqlite3 /tmp/fa.db "SELECT round(sum(amount),2) FROM dep_run;"
# 期望：8500.02（2833.34 × 3）

# 3) 闭合查询：除差额 0.0 外应无输出
sqlite3 /tmp/fa.db < checks.sql
# 期望：仅一行 0.0

# 4) 负向用例全部失败：退出码应为 0
python3 must_fail.py; echo $?
# 期望：四行 PASS，退出码 0

# 5) 重跑幂等：再跑一次 2026-02，行数不变
sqlite3 /tmp/fa.db "SELECT count(*) FROM dep_run WHERE period='2026-02';"
# 期望：3（两次运行后仍是 3）
```

## 参考资料

- [资产卡片与组件拆分](../AssetCard/index.md)：`schema.sql` 里每条 CHECK 的来历
- [折旧方法与月度引擎](../Depreciation/index.md)：计划与执行分离
- [变更：转移、改良、减值](../Movement/index.md)：变更后计划重算
- [处置与清理](../Disposal/index.md)：处置的六步事务
- [与总账的勾稽与月结](../Ledger/index.md)：六条查询里的第 ④ ⑤ 条
- SQLite 文档（`INSERT OR IGNORE` 与唯一键）：<https://www.sqlite.org/lang_conflict.html>
