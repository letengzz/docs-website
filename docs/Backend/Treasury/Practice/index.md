# 实战：从到账到调节表的闭环

<p style="text-align:center;"><img src="../assets/tre-logo.png" alt="资金管理与现金流预测" style="zoom:75%;" /></p>

这一页把前八页的口径落到一个能跑的东西上：**7 张表、5 个函数、5 条自检、4 个负向用例**。全部只用标准库 + SQLite，在任意一台装了 Python 3 的机器上能跑通；跑完自检全为 0、负向用例全部按预期失败，才算这一步做完。

本页判据族 `TRS-A` ~ `TRS-H`，共 8 条，定义在最后一节。

::: info 运行环境
本页读数来自 Python 3.13 + SQLite 3.50（`python3 -c "import sqlite3; print(sqlite3.sqlite_version)"` 可查）。不需要 MySQL / PostgreSQL，也不需要 Docker——本页只验证**口径是否正确**，不验证性能。生产库请把 `NUMERIC` 换成 `DECIMAL(18,2)`、把触发器换成应用层事务 + 唯一索引。
:::

## 一、七张表

```sql
CREATE TABLE tre_account (
  acct_id      TEXT PRIMARY KEY,
  bank_name    TEXT NOT NULL,
  acct_no      TEXT NOT NULL,
  currency     TEXT NOT NULL,
  acct_kind    TEXT NOT NULL CHECK (acct_kind IN ('BASIC','GENERAL','PLEDGE','POOL')),
  status       TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','FROZEN','CLOSED')),
  UNIQUE (bank_name, acct_no, currency)
);

CREATE TABLE tre_balance_snapshot (
  acct_id        TEXT NOT NULL REFERENCES tre_account(acct_id),
  biz_date       TEXT NOT NULL,
  book_amt       NUMERIC NOT NULL,
  frozen_amt     NUMERIC NOT NULL DEFAULT 0,
  in_transit_amt NUMERIC NOT NULL DEFAULT 0,
  PRIMARY KEY (acct_id, biz_date),
  CHECK (frozen_amt >= 0 AND in_transit_amt >= 0)
);

CREATE TABLE tre_receipt (
  receipt_id   INTEGER PRIMARY KEY,
  bank_ref     TEXT NOT NULL,
  acct_id      TEXT NOT NULL REFERENCES tre_account(acct_id),
  value_date   TEXT NOT NULL,
  amt          NUMERIC NOT NULL CHECK (amt > 0),
  payer_name   TEXT NOT NULL,
  memo         TEXT,
  status       TEXT NOT NULL DEFAULT 'UNAPPLIED'
               CHECK (status IN ('UNAPPLIED','PARTIAL','APPLIED','REFUNDED')),
  UNIQUE (acct_id, bank_ref)
);

CREATE TABLE tre_receipt_alloc (
  alloc_id   INTEGER PRIMARY KEY,
  receipt_id INTEGER NOT NULL REFERENCES tre_receipt(receipt_id),
  invoice_no TEXT NOT NULL,
  amt        NUMERIC NOT NULL CHECK (amt > 0),
  UNIQUE (receipt_id, invoice_no)
);

CREATE TABLE tre_payment_instr (
  instr_id   INTEGER PRIMARY KEY,
  batch_no   TEXT NOT NULL,
  invoice_no TEXT NOT NULL,
  ben_acct   TEXT NOT NULL,
  amt        NUMERIC NOT NULL CHECK (amt > 0),
  status     TEXT NOT NULL DEFAULT 'CREATED'
             CHECK (status IN ('CREATED','SENT','ACKED','RETURNED')),
  UNIQUE (invoice_no, ben_acct)
);

CREATE TABLE tre_bank_line (
  line_id    INTEGER PRIMARY KEY,
  acct_id    TEXT NOT NULL REFERENCES tre_account(acct_id),
  bank_ref   TEXT NOT NULL,
  value_date TEXT NOT NULL,
  direction  TEXT NOT NULL CHECK (direction IN ('CR','DR')),
  amt        NUMERIC NOT NULL CHECK (amt > 0),
  matched_instr_id   INTEGER,
  matched_receipt_id INTEGER REFERENCES tre_receipt(receipt_id),
  UNIQUE (acct_id, bank_ref)
);

CREATE TABLE tre_forecast (
  version_no  INTEGER NOT NULL,
  week_start  TEXT NOT NULL,
  bucket      TEXT NOT NULL CHECK (bucket IN ('AR','AP','TAX','PAYROLL','OTHER')),
  amt         NUMERIC NOT NULL,
  PRIMARY KEY (version_no, week_start, bucket)
);
```

### 两个触发器

```sql
-- 认领总额不得超过到账金额
CREATE TRIGGER trg_alloc_cap BEFORE INSERT ON tre_receipt_alloc
BEGIN
  SELECT CASE WHEN
    (SELECT COALESCE(SUM(amt),0) FROM tre_receipt_alloc WHERE receipt_id = NEW.receipt_id)
    + NEW.amt
    > (SELECT amt FROM tre_receipt WHERE receipt_id = NEW.receipt_id)
  THEN RAISE(ABORT, 'ALLOC_OVER_RECEIPT') END;
END;

-- 认领后回写到账状态
CREATE TRIGGER trg_receipt_status AFTER INSERT ON tre_receipt_alloc
BEGIN
  UPDATE tre_receipt SET status = CASE
    WHEN (SELECT SUM(amt) FROM tre_receipt_alloc WHERE receipt_id = NEW.receipt_id)
         >= (SELECT amt FROM tre_receipt WHERE receipt_id = NEW.receipt_id) THEN 'APPLIED'
    ELSE 'PARTIAL' END
  WHERE receipt_id = NEW.receipt_id;
END;
```

## 二、五个函数

| 函数 | 职责 | 关键约束 |
| --- | --- | --- |
| `available(acct, date)` | 可用余额 | 快照不存在时报错，不返回 0 |
| `position(date)` | 头寸 | 可用 + 未达净额，两段各自聚合后再相加 |
| `apply_receipt(...)` | 认领 | 靠触发器拦超额，靠唯一键拦重复 |
| `pay(...)` | 建付款指令 | 靠唯一键拦重投 |
| `reconcile(acct)` | 对账 | 先付款侧后收款侧，返回四个数 |

```python
def available(conn, acct_id, biz_date):
    r = conn.execute("""
      SELECT book_amt, frozen_amt, in_transit_amt FROM tre_balance_snapshot
       WHERE acct_id=? AND biz_date=?""", (acct_id, biz_date)).fetchone()
    if r is None:
        raise ValueError("NO_SNAPSHOT")          # 不许静默返回 0
    return r[0] - r[1] - r[2]


def position(conn, biz_date):
    """头寸 = Σ(账面 − 冻结 − 在途) + 未达净额。两段各自聚合，再相加。"""
    avail = conn.execute("""
      SELECT COALESCE(SUM(book_amt - frozen_amt - in_transit_amt),0)
        FROM tre_balance_snapshot WHERE biz_date=?""", (biz_date,)).fetchone()[0]
    unmatched = conn.execute("""
      SELECT COALESCE(SUM(CASE direction WHEN 'CR' THEN amt ELSE -amt END),0)
        FROM tre_bank_line
       WHERE matched_instr_id IS NULL AND matched_receipt_id IS NULL""").fetchone()[0]
    return avail, unmatched, avail + unmatched


def reconcile(conn, acct_id):
    """先按金额匹配付款指令与收款，剩下的是未达。返回 (银行合计, 企业账面, 未达CR, 未达DR)。"""
    conn.execute("""
      UPDATE tre_bank_line SET matched_instr_id = (
        SELECT i.instr_id FROM tre_payment_instr i WHERE i.amt = tre_bank_line.amt LIMIT 1)
       WHERE acct_id=? AND direction='DR' AND matched_instr_id IS NULL""", (acct_id,))
    conn.execute("""
      UPDATE tre_bank_line SET matched_receipt_id = (
        SELECT r.receipt_id FROM tre_receipt r
         WHERE r.acct_id = tre_bank_line.acct_id AND r.amt = tre_bank_line.amt
           AND abs(julianday(r.value_date)-julianday(tre_bank_line.value_date)) <= 3
         LIMIT 1)
       WHERE acct_id=? AND direction='CR' AND matched_receipt_id IS NULL""", (acct_id,))
    bank_total = conn.execute("""
      SELECT COALESCE(SUM(CASE direction WHEN 'CR' THEN amt ELSE -amt END),0)
        FROM tre_bank_line WHERE acct_id=?""", (acct_id,)).fetchone()[0]
    book_total = conn.execute("""
      SELECT (SELECT COALESCE(SUM(amt),0) FROM tre_receipt WHERE acct_id=?)
           - (SELECT COALESCE(SUM(amt),0) FROM tre_payment_instr)""", (acct_id,)).fetchone()[0]
    un_cr = conn.execute("""SELECT COALESCE(SUM(amt),0) FROM tre_bank_line
                             WHERE acct_id=? AND direction='CR' AND matched_receipt_id IS NULL""",
                         (acct_id,)).fetchone()[0]
    un_dr = conn.execute("""SELECT COALESCE(SUM(amt),0) FROM tre_bank_line
                             WHERE acct_id=? AND direction='DR' AND matched_instr_id IS NULL""",
                         (acct_id,)).fetchone()[0]
    return bank_total, book_total, un_cr, un_dr
```

## 三、本机实测输出

```text
== 建库 ==
  7 张业务表：7 / 触发器：2
== 三个余额 ==
  A001 可用   920,000.00
  A002 可用   250,000.00
  A003 可用         0.00          ← 全额质押，账面 12 万但可用为 0
  A004 可用    47,000.00          ← 账面 5 万，在途 3 千
  合计可用 1,217,000.00 / 未达 0.00 / 头寸 1,217,000.00
== 认领 ==
  BR001 → APPLIED
  BR002 → APPLIED
  BR003 → APPLIED
  分次认领累计 INV000001： 42000    ← 两笔到账共同销一张票
== 付款幂等 ==
  首投后指令数 1                    ← 同票同账号第二次被唯一键拦下
== 对账 ==
  银行端合计 41,820.00 / 企业账面 42,000.00
  未达：收款 0.00 / 付款 180.00      ← 手续费，银行已扣企业未记
  调节：41,820.00 − 0.00 + 180.00 = 42,000.00
== 自检 ==
  C1 每账户每日一条快照: 0
  C2 认领合计 ≤ 到账金额: 0
  C3 付款指令无重复: 0
  C4 调节表闭合: 0.0
  C5 头寸定义自洽: 0.0
== 负向用例 ==
  N1 重复认领同一发票到同一笔到账: 按预期失败 → IntegrityError: ALLOC_OVER_RECEIPT
  N2 认领金额超过到账余额: 按预期失败 → IntegrityError: ALLOC_OVER_RECEIPT
  N3 同一发票同一收款账号重复付款: 按预期失败 → IntegrityError: UNIQUE constraint failed: tre_payment_instr.invoice_no, tre_payment_instr.ben_acct
  N4 冻结额度被当成可用（负的在途）: 按预期失败 → IntegrityError: CHECK constraint failed: frozen_amt >= 0 AND in_transit_amt >= 0
  四个负向用例通过 4/4
EXIT=0
```

::: warning N1 被拦下了，但不是被唯一键拦的
N1 本来想验「同一笔到账对同一张票认两次」，唯一键 `(receipt_id, invoice_no)` 应该拦下它。但实测报的是触发器 `ALLOC_OVER_RECEIPT`——因为 **SQLite 的 `BEFORE INSERT` 触发器先于唯一索引检查执行**。这不影响结果（都被拦住了），但它说明一件事：**「被拦下」不等于「被你设计的那道闸拦下」**。要区分，得看错误码；这也是为什么触发器里要 `RAISE(ABORT, 'ALLOC_OVER_RECEIPT')` 带一个自定义消息，而不是让它抛一个通用错误。
:::

## 四、五条自检的含义

| 编号 | 检查什么 | 为 0 意味着 |
| --- | --- | --- |
| C1 | 每账户每日一条快照 | 重跑覆盖生效，聚合不会翻倍 |
| C2 | 认领合计 ≤ 到账金额 | 没有「一笔到账销了超额发票」 |
| C3 | 付款指令无重复 | 幂等键生效 |
| C4 | 调节表闭合 | 未达账项被完整识别，没有「凑数」 |
| C5 | 头寸定义自洽 | 头寸不是拍脑袋的数，是两段聚合相加 |

自检要写成**能被别人跑的查询**，不能写成「我检查过了」。

## 五、四个负向用例为什么必须存在

正向用例只证明「对的能过」，负向用例证明「错的过不去」。四条覆盖四种不同层次的约束：

| 用例 | 试图做什么 | 应该被谁拦 | 实际报错 |
| --- | --- | --- | --- |
| N1 | 同一到账重复认领同一票 | 唯一键 / 触发器 | `ALLOC_OVER_RECEIPT` |
| N2 | 认领额超过到账额 | 触发器 `trg_alloc_cap` | `ALLOC_OVER_RECEIPT` |
| N3 | 同票同账号重复付款 | `UNIQUE (invoice_no, ben_acct)` | `UNIQUE constraint failed` |
| N4 | 写入负的在途金额 | `CHECK (in_transit_amt >= 0)` | `CHECK constraint failed` |

**负向用例要断言「失败」，不能只断言「无异常」**。写成 `try: ... except: pass` 是最常见的伪测试——它连「因为什么失败」都不看。

## 六、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `TRS-A` | 七张表建库一次成功，无需人工补 | `count(*) = 7` 且无报错 |
| `TRS-B` | 五条自检全部为 0 | 输出五行，值都是 0 / 0.0 |
| `TRS-C` | 四个负向用例全部按预期失败 | 输出 `4/4`，退出码 0 |
| `TRS-D` | 快照缺失时 `available()` 报错而不是返回 0 | 抛 `NO_SNAPSHOT` |
| `TRS-E` | 认领状态由触发器回写，不由应用层设置 | `tre_receipt.status` 只被触发器更新 |
| `TRS-F` | 调节表用「银行 − 未达CR + 未达DR = 账面」一种写法 | 恒等式结果为 0.0 |
| `TRS-G` | 全流程只用标准库，无外部依赖 | 无 `pip install`，只 `import sqlite3` |
| `TRS-H` | 失败消息可区分（自定义 `RAISE` 文案） | 至少两条不同的 `IntegrityError` 文案 |

## 验证方式

```shell
# 0) 准备：把本页的 DDL 与函数粘进 tout.py，或直接用 sqlite3 交互
python3 --version && python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
# 期望：Python 3.x 与 SQLite 3.4x 以上

# 1) 建库：应输出 7 与 2
sqlite3 /tmp/tre.db "SELECT count(*) FROM sqlite_master WHERE type='table' AND name LIKE 'tre_%';
                     SELECT count(*) FROM sqlite_master WHERE type='trigger';"
# 期望：7 / 2

# 2) 自检全 0：五条应只有 0
sqlite3 /tmp/tre.db "SELECT
  (SELECT count(*) FROM (SELECT acct_id,biz_date,count(*) n FROM tre_balance_snapshot GROUP BY 1,2 HAVING n>1)),
  (SELECT count(*) FROM (SELECT receipt_id,SUM(amt) s FROM tre_receipt_alloc GROUP BY 1
                          HAVING s > (SELECT amt FROM tre_receipt r WHERE r.receipt_id=tre_receipt_alloc.receipt_id))),
  (SELECT count(*) FROM (SELECT invoice_no,ben_acct,count(*) n FROM tre_payment_instr GROUP BY 1,2 HAVING n>1));"
# 期望：0|0|0

# 3) 负向用例：应全部报错（四条命令各自失败）
sqlite3 /tmp/tre.db "INSERT INTO tre_receipt_alloc(receipt_id,invoice_no,amt) VALUES(1,'INV000001',999999);"
sqlite3 /tmp/tre.db "INSERT INTO tre_payment_instr(batch_no,invoice_no,ben_acct,amt) VALUES('B9','INV000002','6222-8888',45000);"
sqlite3 /tmp/tre.db "INSERT INTO tre_balance_snapshot VALUES('A001','2026-12-01',100,0,-5);"
# 期望：三条都返回非 0 退出码，且错误文案各不相同

# 4) 调节表恒等：应输出 0.0
sqlite3 /tmp/tre.db "SELECT ROUND(
    (SELECT SUM(CASE direction WHEN 'CR' THEN amt ELSE -amt END) FROM tre_bank_line WHERE acct_id='A001')
  - (SELECT COALESCE(SUM(amt),0) FROM tre_bank_line WHERE acct_id='A001' AND direction='CR' AND matched_receipt_id IS NULL)
  + (SELECT COALESCE(SUM(amt),0) FROM tre_bank_line WHERE acct_id='A001' AND direction='DR' AND matched_instr_id IS NULL)
  - ((SELECT COALESCE(SUM(amt),0) FROM tre_receipt WHERE acct_id='A001')
   - (SELECT COALESCE(SUM(amt),0) FROM tre_payment_instr)), 2);"
# 期望：0.0
```

## 参考资料

- [总览：七段资金链与三个「有多少钱」](../Overview/index.md)：本页七张表的来源
- [账户、余额与价值日期](../AccountModel/index.md)：`tre_account` 与 `tre_balance_snapshot` 的设计理由
- [收款认领与未认领池](../Inflow/index.md)：`tre_receipt_alloc` 与触发器
- [银行对账与对账单解析](../Statement/index.md)：`reconcile()` 的四个返回值
- [13 周滚动预测与现金缺口](../Forecast/index.md)：`tre_forecast` 的版本规则
- SQLite：`ON CONFLICT` 与 `RAISE(ABORT)` 语法：<https://www.sqlite.org/lang_conflict.html>
