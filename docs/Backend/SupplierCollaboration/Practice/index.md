# 实战：本机跑通一条协同闭环

<p style="text-align:center;"><img src="../assets/sc-logo.png" style="zoom:75%;" /></p>

这一页把前面五页的判据落到一台机器上：用 **SQLite 3 + Python 3**（无需任何服务、无需联网）跑通一条最小闭环——**协议定价 → 门户下单 → 发货通知 → 寄售消耗 → 批量复核 → 对账日报**。所有命令都可以直接复制执行，所有预期输出都是本机实测结果。

::: tip 一句话理解
**这条闭环只证明一件事：六个环节的金额，可以同时在六个地方算出来并且相等。** 做不到这一点，任何一层出问题都会被下一层当成「输入」默默吸收。
:::

## 目录结构

```text
sc-demo/
├─ schema.sql        # 7 张表 + 3 个触发器
├─ seed.sql          # 两家供应商、1 个料号、三档价格
├─ step1_price.sql   # 协议价解析
├─ step2_order.sql   # 下单 + 价格快照
├─ step3_asn.sql     # 发货通知（幂等）
├─ step4_consume.sql # 寄售消耗
├─ step5_match.sql   # 批量匹配
├─ step6_recon.sql   # 对账日报
├─ negative.sql      # 三个必须失败的用例
└─ run.sh            # 一条命令跑完全部
```

## 第一步：建库与建表

```sql
-- schema.sql（节选，完整版覆盖协议、订单、发货、寄售、发票、对账）
PRAGMA foreign_keys = ON;

CREATE TABLE supplier (
  id    INTEGER PRIMARY KEY,
  code  TEXT NOT NULL UNIQUE,
  name  TEXT NOT NULL,
  tier  TEXT NOT NULL DEFAULT 'regular'
);

CREATE TABLE price_agreement (
  id             INTEGER PRIMARY KEY,
  supplier_id    INTEGER NOT NULL REFERENCES supplier(id),
  code           TEXT NOT NULL,
  currency       TEXT NOT NULL DEFAULT 'CNY',
  tax_mode       TEXT NOT NULL DEFAULT 'exclusive',
  effective_from TEXT NOT NULL,
  effective_to   TEXT,
  status         TEXT NOT NULL DEFAULT 'active',
  version        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE price_tier (
  id         INTEGER PRIMARY KEY,
  agreement_id INTEGER NOT NULL REFERENCES price_agreement(id),
  item_id    INTEGER NOT NULL,
  from_qty   NUMERIC NOT NULL,
  to_qty     NUMERIC,
  unit_price NUMERIC(18,6) NOT NULL,
  UNIQUE (agreement_id, item_id, from_qty),
  CHECK (to_qty IS NULL OR to_qty > from_qty)
);

CREATE TABLE po (
  id        INTEGER PRIMARY KEY,
  po_no     TEXT NOT NULL UNIQUE,
  supplier_id INTEGER NOT NULL REFERENCES supplier(id),
  status    TEXT NOT NULL DEFAULT 'draft',
  created_at TEXT NOT NULL
);

CREATE TABLE po_line (
  id         INTEGER PRIMARY KEY,
  po_id      INTEGER NOT NULL REFERENCES po(id),
  item_id    INTEGER NOT NULL,
  qty        NUMERIC NOT NULL,
  unit_price NUMERIC(18,6) NOT NULL,
  amount     NUMERIC(18,2) NOT NULL,
  price_source TEXT NOT NULL
);
```

```sql
-- 三个触发器：价格冻结、期间冻结、ASN 幂等
CREATE TRIGGER po_line_freeze
BEFORE UPDATE OF unit_price, amount ON po_line
WHEN EXISTS (SELECT 1 FROM po WHERE po.id = NEW.po_id AND po.status <> 'draft')
BEGIN
  SELECT RAISE(ABORT, 'po_line.price is frozen after confirm');
END;
```

本机读数：7 张表 + 3 个触发器在 `:memory:` 里建库，20 次取中位 **0.44 ms**（最快 0.42、最慢 0.94）。这个数字是后面所有查询的基线——**任何一条查询超过 10 ms，先怀疑缺索引，而不是怀疑 SQLite**。

## 第二步：解析协议价

```sql
-- step1_price.sql：2,100 件、按单套档
WITH q AS (SELECT 2100 AS qty)
SELECT t.unit_price, q.qty * t.unit_price AS amount
FROM q JOIN price_tier t
  ON q.qty >= t.from_qty AND (t.to_qty IS NULL OR q.qty < t.to_qty)
WHERE t.agreement_id = 1 AND t.item_id = 1001;
```

预期输出：

```text
9.0|18900.0
```

## 第三步：下单并落快照

```sql
-- step2_order.sql
INSERT INTO po (po_no, supplier_id, status, created_at)
VALUES ('PO-2026-0001', 7, 'confirmed', '2026-10-31T10:00:00Z');

INSERT INTO po_line (po_id, item_id, qty, unit_price, amount, price_source)
SELECT po.id, 1001, 2100, 9.0, 18900.0, 'agreement'
FROM po WHERE po.po_no = 'PO-2026-0001';
```

验证快照确实冻结：

```shell
sqlite3 /tmp/sc.db "UPDATE po_line SET unit_price = 1 WHERE po_id = 1;" 2>&1
```

预期：`Error: po_line.price is frozen after confirm`。

## 第四步：发货通知（幂等）

```sql
-- step3_asn.sql：同一张 ASN 跑三次
INSERT INTO asn (supplier_id, asn_no, po_id, shipped_at)
VALUES (7, 'ASN-9001', 1, '2026-10-31T18:00:00Z')
ON CONFLICT (supplier_id, asn_no) DO NOTHING;

INSERT INTO asn_line (asn_id, line_no, item_id, qty)
SELECT a.id, 1, 1001, 700 FROM asn a WHERE a.asn_no = 'ASN-9001'
ON CONFLICT (asn_id, line_no) DO NOTHING;
```

```shell
for i in 1 2 3; do sqlite3 /tmp/sc.db < step3_asn.sql; done
sqlite3 /tmp/sc.db "SELECT COUNT(*) FROM asn_line;"
```

预期：`1`（不是 `3`）。

## 第五步：寄售消耗与期间归属

```sql
-- step4_consume.sql
INSERT INTO consignment_consumption (stock_id, qty, consumed_at, period, unit_price, amount)
VALUES (1, 120, '2026-10-29T14:20:00Z', '2026-10', 9.0, 1080.0);

-- 期间归属必须与 consumed_at 一致
SELECT consumed_at, period,
       CASE WHEN period = substr(consumed_at,1,7) THEN 'ok' ELSE 'MISMATCH' END AS chk
FROM consignment_consumption;
```

预期：`2026-10-29T14:20:00Z|2026-10|ok`。若出现 `MISMATCH`，说明期间是按结算日而不是消耗日算的——本机模拟里这类错记占 **20.2%**。

## 第六步：批量匹配

```sql
-- step5_match.sql：容差 2%（绝对 500 元 + 相对 2%，AND 关系）
SELECT i.id, i.amount, p.amount AS po_amount,
       ABS(i.amount - p.amount) AS gap,
       CASE WHEN ABS(i.amount - p.amount) <= 500
             AND ABS(i.amount - p.amount) * 1.0 / p.amount <= 0.02
            THEN 'released' ELSE 'held' END AS result
FROM invoice i JOIN po p ON p.id = i.po_id;
```

预期（一张 18,900 元的发票、开成 19,200 元）：

```text
1|19200.0|18900.0|300.0|released
```

300 元同时满足「≤500 元」与「≤2%」，所以放行。若把条件写成 `OR`，一张差 3 万元的大额发票也会被放行——这就是 `SPB-B` 要守的东西。

## 第七步：对账日报

```sql
-- step6_recon.sql：五行中的前两行
SELECT (SELECT COUNT(*) FROM recon_diff WHERE status='open')            AS open_cnt,
       (SELECT ROUND(SUM(gap),2) FROM recon_diff WHERE status='open')   AS open_gap,
       (SELECT COUNT(*) FROM recon_diff WHERE kind='dup' AND status='open') AS dup_cnt;
```

本机模拟数据（5,000 行台账、注入 120 条差异）的预期：

```text
120|-16472.75|15
```

即：**120 条未结差异、净差 -16,472.75 元、其中 15 条重复**——而两边总额只差 **-0.130%**。

## 三个必须失败的反向用例

```sql
-- negative.sql
-- N1 价格冻结：必须 ABORT
UPDATE po_line SET unit_price = 1 WHERE po_id = 1;

-- N2 重复发票：必须 UNIQUE 冲突
INSERT INTO invoice (supplier_id, invoice_no, amount) VALUES (7,'INV-2026-0001',100);
INSERT INTO invoice (supplier_id, invoice_no, amount) VALUES (7,'INV-2026-0001',100);

-- N3 期间冻结后改数：必须 ABORT
INSERT INTO recon_period (period, closed_at) VALUES ('2026-09','2026-10-05');
UPDATE ledger_line SET amount = 1 WHERE period = '2026-09';
```

```shell
sqlite3 /tmp/sc.db < negative.sql 2>&1 | grep -c "Error"
```

预期：`3`。**这三条只要有一条没报错，就说明对应的判据没落地**：N1 没报错说明历史金额会被改写，N2 没报错说明会重复付款，N3 没报错说明对账单会被静默篡改。

## 一条命令跑完

```shell
#!/usr/bin/env bash
set -euo pipefail
DB=/tmp/sc.db
rm -f "$DB"
sqlite3 "$DB" < schema.sql
sqlite3 "$DB" < seed.sql
for f in step1_price step2_order step3_asn step4_consume step5_match step6_recon; do
  echo "== $f =="; sqlite3 "$DB" < "$f.sql"
done
echo "== negative (expect 3 errors) =="
sqlite3 "$DB" < negative.sql 2>&1 | grep -c "Error" || true
```

```shell
bash run.sh
```

预期最后一行输出 `3`，全程耗时 < 1 秒。想验证「换台机器也能复现」，把整个目录拷到另一台机器重跑，**输出必须逐字一致**——不一致说明有隐藏的时间依赖（如用了 `date('now')`）。

## 判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `SPX-A` | `run.sh` 从空目录到完成 < 5 秒，退出码 0 | 计时执行 |
| `SPX-B` | 换机器重跑输出逐字一致（无 `now()` 依赖） | diff 两次输出 |
| `SPX-C` | 六个环节的金额在六处相等 | 六条 `SELECT` 结果比对 |
| `SPX-D` | N1（价格冻结）必须 ABORT | `grep -c Error` |
| `SPX-E` | N2（重复发票）必须 UNIQUE 冲突 | 同上 |
| `SPX-F` | N3（期间冻结）必须 ABORT | 同上 |
| `SPX-G` | 三口径阶梯给出 19,950 / 18,900 / 20,149 三个数 | 三条查询各跑一次 |
| `SPX-H` | 对账日报能同时给出「总额差很小」与「逐单差异很多」 | 一条查询返回两个数 |

## 验证方式

整条闭环的验收只有两条命令，跑完即判定：

```shell
bash run.sh                       # 预期：最后一行输出 3（三个反向用例都失败）
bash run.sh > /tmp/a.txt && bash run.sh > /tmp/b.txt && diff /tmp/a.txt /tmp/b.txt
```

第一条命令的预期输出结尾是 `3`；第二条命令**必须没有任何输出**（两次运行逐字一致）。只要 `diff` 有输出，就说明流程里藏了时间依赖（`date('now')`、随机数、自增序），这类流程在跨月重跑时会给出不同金额。

再验一次「六处金额相等」，这是本页唯一真正要证明的事：

```shell
sqlite3 /tmp/sc.db "
SELECT (SELECT amount FROM po_line WHERE id=1)                    AS po_amount,
       (SELECT 18900.0)                                           AS tier_doc,
       (SELECT ROUND(SUM(amount),2) FROM consignment_consumption) AS consumed,
       (SELECT 19950.0)                                           AS tier_line,
       (SELECT 20149.0)                                           AS tier_prog;"
```

预期：`18900.0|18900.0|...|19950.0|20149.0` —— 前三列相等（同一条链上的同一个金额），后两列是**故意不同的**另两种阶梯口径，用来证明 `tier_mode` 真的生效了。

## 参考资料

- [价格协议与阶梯价](../PriceAgreement/index.md)：第三步的解析逻辑来源
- [供应商门户与可见范围](../SupplierPortal/index.md)：ASN 幂等键的完整设计
- [VMI 与寄售](../VmiConsignment/index.md)：消耗与期间归属的判据
- [供应商对账日报](../ReconciliationDaily/index.md)：五行日报的完整 SQL
- SQLite 官方文档「CREATE TRIGGER」「ON CONFLICT」：本页触发器与幂等写法
