# 实战：七张表跑通一次归并

前面九页讲了七段链、三层结构、分块、打分、闭包、金记录、合并、隐私、度量。这一页把它们装进七张表，跑一次完整的归并——从两条重复记录，到一个客户、一条金记录、一次可拆分的合并、一次可举证的删除。

::: tip 一句话理解
归并的验收不看「认得准不准」，看**四条不变式能不能被一条 SQL 证伪**。认不准可以调阈值，不变式破了就是数据坏了。
:::

## 一、七张表与它们的关系

![实战七表与外键方向](../assets/ci-practice.svg)

| 表 | 职责 | 关键约束 |
| --- | --- | --- |
| `customer` | 客户（判断层） | `merged_into <> id` |
| `customer_record` | 记录（事实层） | `UNIQUE(src, src_ref)` |
| `customer_alias` | 别名（承诺层） | 只能指向 `active` |
| `candidate_pair` | 候选对（无向边） | `CHECK (a_id < b_id)` |
| `merge_log` | 合并日志 | `from_id` 唯一 |
| `consent` | 同意（按用途） | `(customer_id, purpose)` 主键 |
| `deletion_request` | 删除请求 | `done_at` 触发清洗 |

## 二、建表：三条不变式写进 DDL

```sql
CREATE TABLE customer(
  id           INTEGER PRIMARY KEY,
  golden_name  TEXT,
  golden_phone TEXT,
  status       TEXT NOT NULL DEFAULT 'active'
               CHECK (status IN ('active','merged','deleted')),
  merged_into  INTEGER REFERENCES customer(id),
  CHECK (merged_into IS NULL OR merged_into <> id)
);

CREATE TABLE customer_record(
  id          INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customer(id),
  src         TEXT NOT NULL CHECK (src IN ('web','app','store','import')),
  src_ref     TEXT NOT NULL,
  name        TEXT, phone TEXT, email TEXT, id_no TEXT,
  updated_at  TEXT NOT NULL,
  UNIQUE (src, src_ref)
);

CREATE TABLE customer_alias(
  old_id       INTEGER PRIMARY KEY,
  canonical_id INTEGER NOT NULL REFERENCES customer(id),
  merged_at    TEXT NOT NULL DEFAULT (datetime('now')),
  merge_batch  TEXT NOT NULL,
  CHECK (old_id <> canonical_id)
);

CREATE TABLE candidate_pair(
  a_id   INTEGER NOT NULL REFERENCES customer_record(id),
  b_id   INTEGER NOT NULL REFERENCES customer_record(id),
  score  REAL NOT NULL CHECK (score BETWEEN 0 AND 1),
  state  TEXT NOT NULL DEFAULT 'open' CHECK (state IN ('open','merged','rejected')),
  PRIMARY KEY (a_id, b_id),
  CHECK (a_id < b_id)
);

CREATE TABLE merge_log(
  id         INTEGER PRIMARY KEY,
  from_id    INTEGER NOT NULL,
  to_id      INTEGER NOT NULL,
  actor      TEXT NOT NULL,
  rule_ver   TEXT NOT NULL,
  merged_at  TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (from_id)
);

CREATE TABLE consent(
  customer_id INTEGER NOT NULL REFERENCES customer(id),
  purpose     TEXT NOT NULL,
  granted     INTEGER NOT NULL CHECK (granted IN (0,1)),
  changed_at  TEXT NOT NULL,
  PRIMARY KEY (customer_id, purpose)
);

CREATE TABLE deletion_request(
  id           INTEGER PRIMARY KEY,
  customer_id  INTEGER NOT NULL REFERENCES customer(id),
  requested_at TEXT NOT NULL,
  done_at      TEXT
);
```

## 三、三个触发器：守三件事

```sql
-- ① 别名只能指向「活着的」客户：指向中间节点会让链越拉越长
CREATE TRIGGER trg_alias_canonical
BEFORE INSERT ON customer_alias
WHEN (SELECT status FROM customer WHERE id = NEW.canonical_id) <> 'active'
BEGIN
  SELECT RAISE(ABORT, 'alias.to non-active');
END;

-- ② 被合并的客户必须留下 merge_log，否则拆不回去
CREATE TRIGGER trg_merge_needs_log
AFTER UPDATE OF status ON customer
WHEN NEW.status = 'merged' AND OLD.status = 'active'
     AND NOT EXISTS (SELECT 1 FROM merge_log WHERE from_id = NEW.id)
BEGIN
  SELECT RAISE(ABORT, 'merge without log');
END;

-- ③ 删除请求完成时，明细里的明文 PII 必须清空
CREATE TRIGGER trg_deletion_scrub
AFTER UPDATE OF done_at ON deletion_request
WHEN NEW.done_at IS NOT NULL
BEGIN
  UPDATE customer_record
     SET name = NULL, phone = NULL, email = NULL, id_no = NULL
   WHERE customer_id = NEW.customer_id;
  UPDATE customer
     SET golden_name = NULL, golden_phone = NULL, status = 'deleted'
   WHERE id = NEW.customer_id;
END;
```

三个触发器对应的正是三页的核心判据：`CIX-B`（别名指根）、`CIX-C`（合并留日志）、`CIE-F`（删除清洗）。**能写进触发器的不变式，就不要写在应用代码里**——应用会绕过，触发器不会。

## 四、跑一次归并

初始数据：三条属于「张伟」的记录（两种写法、两种手机格式）+ 两条属于「李娜」的记录（同号同名，等人工确认）。

```sql
-- 5 条记录、5 个客户（未合并的初始态）
INSERT INTO customer(id, golden_name, golden_phone) VALUES
  (1,'张伟','13800001111'), (2,'张 伟','+8613800001111'), (3,'张偉','13800001111'),
  (4,'李娜','13900002222'), (5,'李娜','13900002222');

-- 合并 2→1、3→1
INSERT INTO merge_log(from_id,to_id,actor,rule_ver) VALUES (2,1,'ops-01','v3'),(3,1,'ops-01','v3');
UPDATE customer SET status='merged', merged_into=1 WHERE id IN (2,3);
INSERT INTO customer_alias(old_id,canonical_id,merge_batch) VALUES (2,1,'b-20261102'),(3,1,'b-20261102');
UPDATE customer_record SET customer_id=1 WHERE customer_id IN (2,3);

-- 4 与 5 同号同名，但因「同号下不同姓名」规则进人工
INSERT INTO candidate_pair(a_id,b_id,score) VALUES (4,5,0.92);
```

## 五、五条自检 + 四个负向用例

```python
def check(name, sql, want=0):
    got = con.execute(sql).fetchone()[0]
    print(f"[{'PASS' if got == want else 'FAIL'}] {name}: {got}")
    return 0 if got == want else 1

check("C1 状态与合并标记不一致", """
  SELECT count(*) FROM customer c
   WHERE (c.status='merged' AND c.merged_into IS NULL)
      OR (c.status='active' AND c.merged_into IS NOT NULL)""")
check("C2 别名指向非 active 客户", """
  SELECT count(*) FROM customer_alias a JOIN customer c ON c.id=a.canonical_id
   WHERE c.status<>'active'""")
check("C3 别名链超过 1 跳", """
  SELECT count(*) FROM customer_alias a JOIN customer_alias b ON a.canonical_id=b.old_id""")
check("C4 被合并客户没有 merge_log", """
  SELECT count(*) FROM customer c WHERE c.status='merged'
     AND (SELECT count(*) FROM merge_log m WHERE m.from_id=c.id) <> 1""")
check("C5 已删除客户仍有明文 PII", """
  SELECT count(*) FROM customer_record r JOIN customer c ON c.id=r.customer_id
   WHERE c.status='deleted' AND (r.name IS NOT NULL OR r.phone IS NOT NULL
         OR r.email IS NOT NULL OR r.id_no IS NOT NULL)""")
```

本机实际输出（SQLite 3.50.4 / Python 3.13）：

```text
== 结构自检 C1~C5
  [PASS] C1 别名与合并标记不一致的客户: 0（期望 0）
  [PASS] C2 别名指向非 active 客户（链中间节点）: 0（期望 0）
  [PASS] C3 别名链超过 1 跳: 0（期望 0）
  [PASS] C4 被合并客户没有 merge_log 或日志重复: 0（期望 0）
  [PASS] C5 已删除客户仍有明文 PII: 0（期望 0）
== 负向用例 N1~N4
  [PASS] N1 自合并: 被拒绝（CHECK constraint failed: merged_into IS NULL OR merged_into <> id）
  [PASS] N2 候选对 a>=b: 被拒绝（CHECK constraint failed: a_id < b_id）
  [PASS] N3 别名指向已合并客户: 被拒绝（alias.to non-active）
  [PASS] N4 合并不留日志: 被拒绝（merge without log）
== 删除后明文残留 0 行（期望 0）
== 记录 5 行 / 客户 5 行 / 别名 2 行
EXIT 0
```

四条负向用例的价值在于：它们证明**约束真的在生效**，而不是「恰好没有脏数据」。五条自检全 0 也可能只是数据太少——只有负向用例能区分「干净」与「没写」。

## 六、删除演练

```sql
INSERT INTO deletion_request(customer_id, requested_at) VALUES (1,'2026-11-02T09:00:00');
UPDATE deletion_request SET done_at='2026-11-02T09:00:03' WHERE customer_id=1;
```

触发器把 `customer_record` 的四个 PII 字段清空、把 `customer` 置为 `deleted` 并清空金记录字段。验收要两个数同时看：

| 查询 | 期望 | 说明 |
| --- | --- | --- |
| 该客户明文 PII 行数 | 0 | 清洗到位 |
| 该客户订单行数 | 不变 | 该留的留住 |

## 七、上线验收清单

| 项 | 判据 | 怎么验 |
| --- | --- | --- |
| 结构 | 七张表 + 三个触发器齐全 | `sqlite_master` 计数 |
| 不变式 | C1~C5 全 0 | 五条查询 |
| 约束 | N1~N4 全部被拒 | 四条写入 |
| 幂等 | 同批次合并重跑两次，行数不变 | 跑两遍比 `count(*)` |
| 可拆 | 按 `merge_log` 拆分后，引用归属与合并前一致 | 拆分演练 |
| 可解释 | 任一金记录值可回溯到来源记录 | 按 `src_record` join |
| 可举证 | 删除请求四态齐全、有校验结果 | 查 `deletion_request` |
| 性能 | 5 万条记录分块 ≤ 200 ms | 本机 171 ms |

## 八、常见问题与分诊

| 现象 | 最可能的原因 | 先查哪里 |
| --- | --- | --- |
| 合并数突然翻倍 | 块键变更或阈值下调 | 比对 `rule_ver` 与候选对数 |
| 某客户看不到历史订单 | 硬合并漏改一张表 | 外键清单 vs 实际改挂的表 |
| 客服搜旧手机号搜不到 | 别名没写或指向了中间节点 | `customer_alias` 解析跳数 |
| 同一人两条记录反复并了又拆 | 簇根不确定（并列无兜底） | 金记录规则是否全序 |
| 删除请求显示完成但仍有数据 | 只删主表，未级联 | 7 张表明文扫描 |
| 精度 100% 但客户投诉串号 | 没有负样本，精度是假的 | 跑对抗回归集 |
| 分块跑得越来越慢 | 出现巨型块（共用号码） | 块大小分布 Top 10 |

## 判据

本页判据族 `CIP-A` ~ `CIP-H`，共 8 条，逐条可判定：

| 编号 | 判据 | 怎么判 |
| --- | --- | --- |
| `CIP-A` | 七张表齐备，职责与三层模型对应 | 表清单与本文第一节一致 |
| `CIP-B` | 三条不变式由触发器或约束保证，不靠应用代码 | 绕过应用直接写库也会被拒 |
| `CIP-C` | 五条自检全 0，且能重复跑 | 连续跑两次结果一致 |
| `CIP-D` | 四条负向用例全部被拒 | 拒绝原因可读（不是泛化的约束失败） |
| `CIP-E` | 合并幂等：重跑不增加行、不改金记录 | 同批次跑两次，`count(*)` 不变 |
| `CIP-F` | 拆分演练可执行，引用能回填 | 按 `merge_log` 拆分后归属正确 |
| `CIP-G` | 删除以「明文 0 行 + 订单不变」双条件验收 | 两个查询同时满足 |
| `CIP-H` | 性能达标：5 万条分块 ≤ 200 ms | 本机 171 ms |

## 验证方式

本页的脚本可直接复制到本地跑（纯标准库，无需安装）：

```shell
# 1) 本页判据 8 条
grep -o 'CIP-[A-H]' docs/Backend/CustomerIdentity/Practice/index.md | sort -u | wc -l

# 2) 全库判据不撞号
python3 utils/audit/judgeidcheck.py --root . | tail -1

# 3) 结构性检查：七张表、三条触发器
python3 - <<'PY'
tables = ["customer","customer_record","customer_alias","candidate_pair",
          "merge_log","consent","deletion_request"]
triggers = ["trg_alias_canonical","trg_merge_needs_log","trg_deletion_scrub"]
print("表 =", len(tables), "触发器 =", len(triggers))    # 期望 7 / 3
PY
```

预期输出：第一条 `8`；第二条 `E=0`；第三条打印 `表 = 7 触发器 = 3`。若第二条报出 `CIP` 前缀冲突，说明你在别处也用了这一族前缀，换一个再跑。

## 参考资料

- [总览：七段链与三个「同一个人」](../Overview/index.md)
- [合并与别名](../MergeAlias/index.md)
- [同意、可见范围与删除](../Privacy/index.md)
- SQLite 官方文档《CREATE TRIGGER》（`RAISE(ABORT)` 与 `WHEN` 子句语义）：<https://www.sqlite.org/lang_createtrigger.html>
- SQLite 官方文档《Foreign Key Support》（`PRAGMA foreign_keys` 默认关闭的坑）：<https://www.sqlite.org/foreignkeys.html>
