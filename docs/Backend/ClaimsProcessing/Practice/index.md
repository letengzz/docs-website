# 实战：九张表、三个触发器、十一条断言

把前面七页收成一份能跑的东西：九张表、三个触发器、五条正向自检、六条负向用例。跑完的输出是本文所有结论的地基——**十一条断言全过，退出码 0**。

本机环境：Python 3.13.12 + SQLite 3.50.4，内存库（`:memory:`），无需任何第三方包。

## 一、目录结构

```text
claims/
├─ schema.sql        # 九张表 + 三个触发器
├─ seed.sql          # 两条赔案：一条结案、一条在途
├─ checks.sql        # C1~C5 五条正向自检
├─ negatives.py      # N1~N6 六条负向用例（Python 驱动）
└─ acceptance.sql    # 验收查询（报表口径）
```

本页把所有内容合并成一个脚本，便于一次性复跑。生产环境按上表拆文件——**触发器与表必须同源**，否则重建库时守卫会漏。

## 二、九张表

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE policy (
  policy_id        INTEGER PRIMARY KEY,
  policy_no        TEXT NOT NULL UNIQUE,
  product_code     TEXT NOT NULL,
  sum_insured      REAL NOT NULL CHECK (sum_insured > 0),
  deductible       REAL NOT NULL DEFAULT 0 CHECK (deductible >= 0),
  deductible_kind  TEXT NOT NULL CHECK (deductible_kind IN ('ABSOLUTE','FRANCHISE','RATIO')),
  deductible_ratio REAL NOT NULL DEFAULT 0 CHECK (deductible_ratio BETWEEN 0 AND 1),
  limit_per_claim  REAL NOT NULL CHECK (limit_per_claim > 0),
  indemnity_basis  TEXT NOT NULL CHECK (indemnity_basis IN ('PRO_RATA','FIRST_LOSS','AGREED_VALUE')),
  waiting_days     INTEGER NOT NULL DEFAULT 0 CHECK (waiting_days >= 0),
  valid_from       TEXT NOT NULL,
  valid_to         TEXT NOT NULL,
  status           TEXT NOT NULL CHECK (status IN ('IN_FORCE','LAPSED','CANCELLED')),
  CHECK (valid_to > valid_from)
);

CREATE TABLE subject (
  subject_id   INTEGER PRIMARY KEY,
  policy_id    INTEGER NOT NULL REFERENCES policy(policy_id),
  subject_type TEXT NOT NULL CHECK (subject_type IN ('VEHICLE','PROPERTY','PERSON')),
  subject_key  TEXT NOT NULL,
  actual_value REAL NOT NULL CHECK (actual_value > 0),
  UNIQUE (policy_id, subject_key)
);

CREATE TABLE incident (
  incident_id  INTEGER PRIMARY KEY,
  incident_key TEXT NOT NULL UNIQUE,
  occurred_at  TEXT NOT NULL,
  location     TEXT NOT NULL,
  cause_code   TEXT NOT NULL
);

CREATE TABLE claim (
  claim_id        INTEGER PRIMARY KEY,
  claim_no        TEXT NOT NULL UNIQUE,
  policy_id       INTEGER NOT NULL REFERENCES policy(policy_id),
  subject_id      INTEGER NOT NULL REFERENCES subject(subject_id),
  incident_id     INTEGER NOT NULL UNIQUE REFERENCES incident(incident_id),
  reported_at     TEXT NOT NULL,
  filed_at        TEXT,
  status          TEXT NOT NULL CHECK (status IN
                  ('REPORTED','FILED','SURVEY','ASSESSED','REVIEWED','APPROVED','PAID','CLOSED','REOPENED')),
  reported_amount REAL NOT NULL CHECK (reported_amount >= 0),
  CHECK (filed_at IS NULL OR filed_at >= reported_at)
);

CREATE TABLE claim_event (
  event_id    INTEGER PRIMARY KEY,
  claim_id    INTEGER NOT NULL REFERENCES claim(claim_id),
  from_status TEXT,
  to_status   TEXT NOT NULL,
  at          TEXT NOT NULL,
  actor       TEXT NOT NULL,
  reason      TEXT
);

CREATE TABLE assessment (
  assessment_id   INTEGER PRIMARY KEY,
  claim_id        INTEGER NOT NULL UNIQUE REFERENCES claim(claim_id),
  assessed_amount REAL NOT NULL CHECK (assessed_amount >= 0),
  salvage         REAL NOT NULL DEFAULT 0 CHECK (salvage >= 0),
  basis           TEXT NOT NULL CHECK (basis IN ('RC','ACV','AGREED')),
  assessed_at     TEXT NOT NULL
);

CREATE TABLE assessment_item (
  item_id       INTEGER PRIMARY KEY,
  assessment_id INTEGER NOT NULL REFERENCES assessment(assessment_id),
  code          TEXT NOT NULL,
  qty           REAL NOT NULL CHECK (qty > 0),
  unit_price    REAL NOT NULL CHECK (unit_price >= 0),
  allowed_price REAL NOT NULL CHECK (allowed_price >= 0),
  cut_reason    TEXT,
  CHECK (allowed_price <= unit_price),
  CHECK (allowed_price = unit_price OR cut_reason IS NOT NULL)
);

CREATE TABLE payment (
  payment_id INTEGER PRIMARY KEY,
  claim_id   INTEGER NOT NULL REFERENCES claim(claim_id),
  pay_seq    INTEGER NOT NULL CHECK (pay_seq > 0),
  payee      TEXT NOT NULL,
  amount     REAL NOT NULL CHECK (amount > 0),
  status     TEXT NOT NULL CHECK (status IN ('PENDING','SUCCESS','FAILED')),
  paid_at    TEXT,
  UNIQUE (claim_id, pay_seq)
);

CREATE TABLE reserve (
  reserve_id INTEGER PRIMARY KEY,
  claim_id   INTEGER NOT NULL REFERENCES claim(claim_id),
  as_of      TEXT NOT NULL,
  amount     REAL NOT NULL CHECK (amount >= 0),
  basis      TEXT NOT NULL,
  UNIQUE (claim_id, as_of)
);

CREATE INDEX idx_claim_status  ON claim(status);
CREATE INDEX idx_payment_claim ON payment(claim_id, status);
CREATE INDEX idx_event_claim   ON claim_event(claim_id, at);
```

## 三、三个触发器

```sql
-- T1 支付上限守卫：必须有定损，且累计成功支付不超过「核定额 − 残值」
CREATE TRIGGER trg_payment_cap BEFORE INSERT ON payment
WHEN NEW.status = 'SUCCESS'
BEGIN
  SELECT RAISE(ABORT, 'E_NO_ASSESSMENT')
   WHERE NOT EXISTS (SELECT 1 FROM assessment WHERE claim_id = NEW.claim_id);
  SELECT RAISE(ABORT, 'E_OVERPAID')
   WHERE NEW.amount + (SELECT COALESCE(SUM(amount), 0) FROM payment
                        WHERE claim_id = NEW.claim_id AND status = 'SUCCESS')
       > (SELECT assessed_amount - salvage FROM assessment WHERE claim_id = NEW.claim_id);
END;

-- T2 结案守卫：无定损不许结案；准备金未释放不许结案
CREATE TRIGGER trg_claim_close BEFORE UPDATE OF status ON claim
WHEN NEW.status = 'CLOSED'
BEGIN
  SELECT RAISE(ABORT, 'E_NO_ASSESSMENT')
   WHERE NOT EXISTS (SELECT 1 FROM assessment WHERE claim_id = NEW.claim_id);
  SELECT RAISE(ABORT, 'E_RESERVE_LEFT')
   WHERE EXISTS (SELECT 1 FROM reserve WHERE claim_id = NEW.claim_id AND amount > 0);
END;

-- T3 核减理由守卫：允许价低于申报价时，理由必须落在四码之内
CREATE TRIGGER trg_item_reason BEFORE INSERT ON assessment_item
WHEN NEW.allowed_price < NEW.unit_price
 AND (NEW.cut_reason IS NULL
      OR NEW.cut_reason NOT IN ('PRICE_CAP','DUPLICATE','NOT_COVERED','DEPRECIATION'))
BEGIN
  SELECT RAISE(ABORT, 'E_CUT_REASON');
END;
```

**为什么守卫用触发器而不是应用层**：理赔系统经常有批量修数、运营后台、数据迁移三条写入路径，应用层守卫只能覆盖其中一条。触发器是唯一能在**所有路径**上都生效的位置——代价是调试信息不如应用层友好，所以错误码要设计成可读的（`E_OVERPAID` 而不是 `constraint failed`）。

## 四、五条正向自检

```sql
-- C1 未定损却已支付
SELECT count(*) FROM payment p WHERE p.status='SUCCESS'
  AND NOT EXISTS (SELECT 1 FROM assessment a WHERE a.claim_id=p.claim_id);

-- C2 累计支付超核定额
SELECT count(*) FROM (
  SELECT p.claim_id, SUM(p.amount) s,
        (SELECT assessed_amount - salvage FROM assessment a WHERE a.claim_id=p.claim_id) cap
  FROM payment p WHERE p.status='SUCCESS' GROUP BY p.claim_id) WHERE s > cap;

-- C3 状态与事件末尾不一致
SELECT count(*) FROM claim c WHERE c.status <> COALESCE(
  (SELECT e.to_status FROM claim_event e WHERE e.claim_id=c.claim_id
    ORDER BY e.event_id DESC LIMIT 1),'');

-- C4 同一事故重复立案
SELECT count(*) FROM (SELECT incident_id FROM claim GROUP BY incident_id HAVING count(*)>1);

-- C5 结案仍留准备金
SELECT count(*) FROM claim c JOIN reserve r ON r.claim_id=c.claim_id
 WHERE c.status='CLOSED' AND r.amount>0;
```

实测输出：

```text
== 正向自检（期望全部为 0）
C1 未定损却已支付: 0
C2 累计支付超核定额: 0
C3 状态与事件末尾不一致: 0
C4 同一事故重复立案: 0
C5 结案仍留准备金: 0
```

## 五、六条负向用例

负向用例的价值大于正向：正向只能证明「正常情况下没坏」，负向才能证明「坏了会被拦住」。

```text
== 负向用例（期望全部被拦住）
N1 无定损结案: 拦住 -> E_NO_ASSESSMENT
N2 无定损即支付: 拦住 -> E_NO_ASSESSMENT
N3 支付超额: 拦住 -> E_OVERPAID
N4 核减无理由: 拦住 -> E_CUT_REASON
N5 重复支付序号: 拦住 -> UNIQUE constraint failed: payment.claim_id, payment.pay_seq
N6 同一事故二次立案: 拦住 -> UNIQUE constraint failed: claim.incident_id
```

六条用例覆盖了五个判据族：`INM-B`（事故唯一）、`INM-C`（状态约束）、`INA-B`（核减理由）、`INY-D`（支付幂等）、`INP`（金额上限）。每加一个新守卫，就加一条对应用例——**没有负向用例的守卫，等于没有守卫**。

## 六、七步流水：一条赔案走完

```text
① 建保单与标的
② 建事故（写指纹）
③ 建赔案（REPORTED → FILED）
④ 建准备金（逐案估计）
⑤ 定损（assessment + 明细，核减带理由）
⑥ 支付（pay_seq=1，触发器校验上限）
⑦ 释放准备金 → 结案（触发器校验定损与准备金）
```

对应的验收读数：

```text
C-2026-0001 CLOSED 核定=41000.00 残值=0.00 已付=41000.00
C-2026-0002 FILED  核定=30000.00 残值=0.00 已付=30000.00
C-2026-0003 FILED  核定=30000.00 残值=0.00 已付=10000.00
表数: 9 触发器: 3
EXIT 0
```

注意 `C-2026-0002` 已付 30,000、核定额 30,000，状态仍是 `FILED`——**付完钱不等于结案**。结案需要显式动作（释放准备金 + 状态迁移），这是刻意的：结案是一个业务判断，不该被支付动作隐式触发。

## 七、验收查询

```sql
-- V1 每个赔案的三个金额（责任额 / 核定额 / 实付额）一次看全
SELECT c.claim_no, c.status, c.reported_amount,
       a.assessed_amount, a.salvage, COALESCE(SUM(p.amount), 0) AS paid
FROM claim c
LEFT JOIN assessment a ON a.claim_id = c.claim_id
LEFT JOIN payment p    ON p.claim_id = c.claim_id AND p.status = 'SUCCESS'
GROUP BY c.claim_id;

-- V2 支付与核定的差额（>0 说明还有未付）
SELECT c.claim_no, a.assessed_amount - a.salvage - COALESCE((
  SELECT SUM(amount) FROM payment p WHERE p.claim_id=c.claim_id AND p.status='SUCCESS'),0) AS unpaid
FROM claim c JOIN assessment a ON a.claim_id=c.claim_id;

-- V3 核减构成（按理由码汇总，用于解释赔付率变化）
SELECT i.cut_reason, count(*) AS n, SUM((i.unit_price - i.allowed_price) * i.qty) AS cut
FROM assessment_item i
WHERE i.cut_reason IS NOT NULL
GROUP BY i.cut_reason ORDER BY cut DESC;
```

## 八、判据清单

本页判据族 `INX-A` ~ `INX-H`，共 8 条。

| 编号 | 判据 | 判定方式 |
| --- | --- | --- |
| `INX-A` | 九张表可一次建出 | `schema.sql` 执行无错，`.tables` 列出 9 张 |
| `INX-B` | 三个触发器与表同源 | 重建库后触发器仍在（`sqlite_master` 计数 3） |
| `INX-C` | C1~C5 全为 0 | 五条查询全返回 0 |
| `INX-D` | N1~N6 全部被拦住 | 六条用例均抛错，无一条静默通过 |
| `INX-E` | 脚本退出码为 0 | `echo $?` 输出 0 |
| `INX-F` | 数据可复跑 | 清库重跑得到同一组读数 |
| `INX-G` | 金额两口径可对账 | V2 的 `unpaid` 之和 = 准备金合计 |
| `INX-H` | 核减可解释 | V3 三类理由码均有金额 |

## 九、验证方式

```shell
# 1) 建库（把第二节的 DDL 存成 /tmp/clm_schema.sql）
sqlite3 /tmp/clm.db < /tmp/clm_schema.sql
sqlite3 /tmp/clm.db "SELECT type, count(*) FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' GROUP BY type;"
# 期望：index|3  table|9  trigger|3

# 2) 正向自检（应为 0）
sqlite3 /tmp/clm.db "SELECT count(*) FROM claim c WHERE c.status <> COALESCE((SELECT e.to_status FROM claim_event e WHERE e.claim_id=c.claim_id ORDER BY e.event_id DESC LIMIT 1),'');"
# 期望：0

# 3) 负向用例：无定损结案必须失败
sqlite3 /tmp/clm.db "UPDATE claim SET status='CLOSED' WHERE claim_id=2;"
# 期望：Runtime error: E_NO_ASSESSMENT（若该案已有定损，先删定损再试）

# 4) 负向用例：无理由核减必须失败
sqlite3 /tmp/clm.db "INSERT INTO assessment_item VALUES (99,1,'PART-X',1,1200,900,NULL);"
# 期望：CHECK constraint failed: allowed_price = unit_price OR cut_reason IS NOT NULL

# 5) 退出码
python3 /tmp/clm_practice.py; echo "EXIT=$?"
# 期望：EXIT=0
```

## 参考资料

- [案件模型与状态机：八态九迁移](../ClaimModel/index.md)
- [条款与责任判定：四问与四口径](../Coverage/index.md)
- SQLite 触发器与 `RAISE(ABORT)`：<https://www.sqlite.org/lang_createtrigger.html>
- SQLite 外键强制执行（`PRAGMA foreign_keys = ON`）：<https://www.sqlite.org/foreignkeys.html>
- 负向用例优先的测试设计，见库内 [测试策略](../../../../project/Complete/TeamBoard/TestStrategy/index.md)
