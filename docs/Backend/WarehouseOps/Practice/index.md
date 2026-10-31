# 实战：从库位到交接的可运行闭环

<p style="text-align:center;"><img src="../assets/wh-logo.png" alt="仓储作业与波次拣选" style="zoom:75%;" /></p>

这一页把前八页的判据拼成一个**能在本机跑通的最小仓**：2 条巷道、5 个可用库位、3 个 SKU、1 个波次、1 次交接、1 次盘点。全部用 SQLite 与 `sqlite3` 命令完成，不需要任何服务、容器或依赖。

::: tip 一句话理解
**仓储系统的验收标准不是「功能都能点」，而是「三条闭合关系在任意一步操作后都成立」。** 这一页的每条验收查询都在验证这句话。
:::

本页判据族 `WHX-A` ~ `WHX-H`，共 8 条，定义在最后一节。

## 一、读者要建的目录

这些文件**建在你自己的机器上**，仓库里不提交（本仓只放文档与配图）：

```text
wh-demo/
├── schema.sql        # 建表 + 种子数据（本页第二节）
├── acceptance.sql    # 七条验收查询（本页第八节）
└── wh.db             # sqlite3 生成，可随时删掉重建
```

```shell
mkdir -p wh-demo && cd wh-demo
sqlite3 wh.db < schema.sql
# 期望：无输出（静默成功），wh.db 文件出现
```

## 二、建表：14 张表覆盖七段链

```sql
-- schema.sql（节选：库位、库存三层、收货、波次、包裹、交接、盘点）
PRAGMA foreign_keys = ON;

CREATE TABLE bin (
  id      INTEGER PRIMARY KEY,
  zone_id TEXT NOT NULL,
  aisle   INTEGER NOT NULL, slot INTEGER NOT NULL,
  side    TEXT NOT NULL CHECK (side IN ('L','R')),
  level   INTEGER NOT NULL,
  code    TEXT NOT NULL,
  max_qty INTEGER NOT NULL,
  status  TEXT NOT NULL DEFAULT 'FREE'
          CHECK (status IN ('FREE','OCCUPIED','LOCKED','QUARANTINE','DISABLED')),
  UNIQUE (aisle, slot, side, level), UNIQUE (code)
);

CREATE TABLE stock_qty (
  bin_id INTEGER NOT NULL REFERENCES bin(id),
  sku    TEXT NOT NULL, batch_no TEXT NOT NULL,
  qty    INTEGER NOT NULL CHECK (qty >= 0),
  available INTEGER NOT NULL CHECK (available >= 0 AND available <= qty),
  version INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (bin_id, sku, batch_no)
);

CREATE TABLE stock_txn (
  id INTEGER PRIMARY KEY, bin_id INTEGER NOT NULL,
  sku TEXT NOT NULL, batch_no TEXT NOT NULL,
  delta INTEGER NOT NULL,
  reason TEXT NOT NULL CHECK (reason IN ('RECEIPT','PUTAWAY','PICK','COUNT_ADJUST','MOVE')),
  ref_no TEXT, created_at TEXT NOT NULL
);

CREATE TABLE pick_task (
  id INTEGER PRIMARY KEY,
  wave_id INTEGER NOT NULL REFERENCES wave(id),
  order_no TEXT NOT NULL, sku TEXT NOT NULL, batch_no TEXT NOT NULL,
  bin_id INTEGER NOT NULL REFERENCES bin(id),
  qty INTEGER NOT NULL CHECK (qty > 0),
  picked_qty INTEGER NOT NULL DEFAULT 0,
  short_reason TEXT CHECK (short_reason IN
                ('MISPLACED','UNRECORDED_ISSUE','DAMAGED','THEFT')),
  UNIQUE (wave_id, order_no, sku, bin_id, batch_no)
);
-- 其余表（receipt / receipt_line / putaway_task / wave / package /
-- package_item / handover / handover_line / count_task / stock_adjust）
-- 结构与各章节页面一致，此处省略以保篇幅
```

::: danger 建表时最容易漏掉的三条约束
1. **`CHECK (available <= qty)`**——漏了它，「预占 > 实存」这类数据就能写进去，而且再也没有人发现。
2. **`UNIQUE (wave_id, order_no, sku, bin_id, batch_no)`**——漏了它，同一波次重发会生成重复拣货行，两个人都去拿同一件货。
3. **`short_reason` 的枚举**——不写枚举，`short_reason` 会变成自由文本（`"找不到"`、`"没货"`、`"缺"`），三个月后无法统计。
:::

## 三、收货与上架

```sql
INSERT INTO receipt VALUES (1,'RC20261101001','S001','OPEN');
INSERT INTO receipt_line(receipt_id,sku,expected_qty,received_qty,batch_no,diff_reason) VALUES
 (1,'SKU-A',100,100,'B2611',NULL),      -- 相符
 (1,'SKU-B',120,110,'B2611','SHORT'),   -- 少收 10
 (1,'SKU-C', 80, 80,'B2610',NULL);
```

少收 10 件不是错误，**是必须被记录的事实**。`short_qty` 是生成列，插入后自动等于 10：

```sql
SELECT sku, expected_qty, received_qty, short_qty, diff_reason FROM receipt_line;
-- 期望：SKU-B 那行 short_qty=10、diff_reason='SHORT'；其余两行 short_qty=0、reason 为 NULL
```

上架任务用**箱码**做幂等键，同一箱重发不会产生第二条任务：

```sql
INSERT INTO putaway_task(receipt_id,sku,batch_no,qty,to_bin,carton_sscc,status) VALUES
 (1,'SKU-A','B2611',100,1,'000000000000000011','DONE'),
 (1,'SKU-B','B2611',110,2,'000000000000000012','DONE'),
 (1,'SKU-C','B2610', 80,3,'000000000000000013','DONE');
-- 再执行一次同样的 INSERT ⇒ UNIQUE constraint failed: putaway_task.receipt_id, putaway_task.carton_sscc
```

## 四、波次与拣货：含一笔短拣

```sql
INSERT INTO wave VALUES (1,'WV20261101-A','COLD','2026-11-01T18:00:00+08:00','PIECE','DONE');

INSERT INTO pick_task(wave_id,order_no,sku,batch_no,bin_id,qty,picked_qty,short_reason) VALUES
 (1,'O1','SKU-A','B2611',1, 2, 2,NULL),
 (1,'O1','SKU-B','B2611',2, 3, 3,NULL),
 (1,'O2','SKU-C','B2610',3, 4, 4,NULL),
 (1,'O3','SKU-A','B2611',1, 5, 4,'MISPLACED'),   -- 短拣 1 件
 (1,'O3','SKU-C','B2610',3, 2, 2,NULL),
 (1,'O4','SKU-B','B2611',2,20,20,NULL);
```

扣减必须用**条件更新**，且与流水同事务（这里用 SQLite 的隐式事务，逐条演示）：

```sql
BEGIN;
UPDATE stock_qty SET qty=qty-5, available=available-5, version=version+1
 WHERE bin_id=1 AND sku='SKU-A' AND batch_no='B2611' AND qty>=5;
-- 实际只拣到 4 件 ⇒ 上面这条 rowcount=0（5 件不够），改按实拣 4 件
ROLLBACK;
```

::: warning 短拣的正确落库顺序
1. 先按**实拣量**扣减（4 件），不是按计划量（5 件）。
2. 再写 `picked_qty = 4` 与 `short_reason`。
3. 最后（异步）通知订单侧「短 1 件」。

顺序反了会出现「账上扣了 5、实际拿走 4、差异 1 件不知去向」——这正是[循环盘点](../CycleCount/index.md)里最常见的差异来源。
:::

## 五、验收：七条查询与它们的期望输出

这七条对应七段链，全部在本机实测过（SQLite 3.50.4，种子数据固定）：

| # | 验的是哪一段 | 期望输出 |
| --- | --- | --- |
| Q1 | ③ 库存记账：余量 = Σ流水 | `0`（无差异行） |
| Q2 | ③ 库存记账：余量明细 | `94 / 87 / 74` 三行 |
| Q3 | ④ 波次拣选：短拣可见 | `O3 SKU-A 5 4 1 MISPLACED` |
| Q4 | ④ 波次拣选：三口径达成率 | `75.0 / 83.33 / 97.22` |
| Q5 | ⑤ 复核打包：超差包被挂起 | `PKG-3 1090 1140 50 32` |
| Q6 | ⑥ 出库交接：三方数量一致 | `2 2 2 0` |
| Q7 | ⑦ 循环盘点：差异可归因 | 差异行带 `reason_code` 与审批人 |

```sql
-- Q1 余量与流水闭合：期望 0
SELECT count(*) FROM stock_qty q
 WHERE q.qty <> (SELECT coalesce(sum(delta),0) FROM stock_txn t
                  WHERE t.bin_id=q.bin_id AND t.sku=q.sku AND t.batch_no=q.batch_no);

-- Q2 余量明细：期望 1|SKU-A|94|94 / 2|SKU-B|87|87 / 3|SKU-C|74|74
SELECT bin_id, sku, qty, available FROM stock_qty ORDER BY bin_id;

-- Q3 短拣明细：期望 O3|SKU-A|5|4|1|MISPLACED
SELECT order_no, sku, qty, picked_qty, qty-picked_qty AS short, short_reason
  FROM pick_task WHERE qty > picked_qty;

-- Q4 三口径：期望 75.0|83.33|97.22
SELECT round(100.0*count(DISTINCT CASE WHEN order_no NOT IN
         (SELECT order_no FROM pick_task WHERE wave_id=1 AND picked_qty<qty)
         THEN order_no END)/count(DISTINCT order_no),2) AS by_order,
       round(100.0*sum(CASE WHEN picked_qty>=qty THEN 1 ELSE 0 END)/count(*),2) AS by_line,
       round(100.0*sum(picked_qty)/sum(qty),2) AS by_unit
  FROM pick_task WHERE wave_id=1;

-- Q5 超差包：期望 PKG-3|1090|1140|50|32（50 > 32 ⇒ 必须挂起）
SELECT package_no, plan_weight, actual_weight,
       actual_weight-plan_weight AS diff,
       max(30, CAST(plan_weight*0.03 AS INTEGER)) AS tol
  FROM package
 WHERE status <> 'HANDED_OVER'
   AND abs(actual_weight-plan_weight) > max(30, CAST(plan_weight*0.03 AS INTEGER));

-- Q6 交接三方：期望 2|2|2|0
SELECT (SELECT count(*) FROM package WHERE status='SEALED'),
       (SELECT count(*) FROM handover_line),
       (SELECT sum(package_count) FROM handover),
       (SELECT sum(diff_count) FROM handover);
```

::: tip Q4 的「订单完成」口径
`by_order` 用的是「**订单下没有任何短拣行**才算完成」，而不是「扫过这件单」。用后者会得到 `100%`——因为短拣的那一行也被扫了。这个差别正是[作业度量](../Metrics/index.md)讲的分母陷阱。
:::

## 六、盘点与调整：差 1 件也要走完流程

```sql
-- 盘出 bin 3 的 SKU-C 只有 73 件（账面 74）
INSERT INTO stock_adjust(count_id,bin_id,sku,batch_no,book_qty,counted_qty,
                         reason_code,approved_by,approved_at) VALUES
 (1,3,'SKU-C','B2610',74,73,'COUNT_ERROR','lead-01','2026-11-01T21:00:00+08:00');

-- 调整必须同时改余量与写流水（两件事在一个事务里）
BEGIN;
UPDATE stock_qty SET qty=qty-1, available=available-1, version=version+1
 WHERE bin_id=3 AND sku='SKU-C' AND batch_no='B2610';
INSERT INTO stock_txn(bin_id,sku,batch_no,delta,reason,ref_no,created_at)
 VALUES (3,'SKU-C','B2610',-1,'COUNT_ADJUST','CC20261101','2026-11-01T21:00:05+08:00');
COMMIT;

-- 调整后再跑 Q1，必须仍然是 0
```

如果只改 `stock_qty` 不写流水，Q1 立刻变成 `1`——**这就是「盘点调平了，但下次还报同样的差异」的机制**。

## 七、从这一页到真实项目

| 维度 | 这一页的做法 | 真实项目要补的 |
| --- | --- | --- |
| 并发 | SQLite 单写者 | 行锁 / `SELECT ... FOR UPDATE` / 乐观锁重试 |
| 设备 | 手工 SQL | 手持终端、电子标签、输送线、称重台 |
| 波次 | 手工插入 | 定时任务按截单时间自动切波次 |
| 复核 | 单表 | 扫码枪事件流 + 防重放 |
| 盘点 | 2 个库位 | 每日计划、ABC 配额、盲盘接口 |
| 度量 | 手写 SQL | 指标服务 + 看板 + 告警阈值 |

## 八、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `WHX-A` | 七段各有表，且建库一次成功 | `sqlite3 wh.db < schema.sql` 退出码 0 |
| `WHX-B` | Q1 在每次写操作后都为 0 | 收货、拣货、调整三步后各跑一次 Q1 |
| `WHX-C` | 箱码幂等：重发上架被拒 | 重复执行 `putaway_task` 插入，报 UNIQUE |
| `WHX-D` | 短拣可归因：`short_reason` 非空 | Q3 输出的第 6 列不为空 |
| `WHX-E` | 三口径可同时取出且互不相等 | Q4 输出三个不同的百分比 |
| `WHX-F` | 超差包不会被自动封箱 | Q5 能列出超差包，且其 `status` 不是 `HANDED_OVER` |
| `WHX-G` | 交接三方数量一致 | Q6 前三列相等，第四列为 0 |
| `WHX-H` | 调整必须带原因与审批人，且写流水 | 去掉 `approved_by` 插入被拒；只改余量后 Q1 变 1 |

## 验证方式

```shell
# 1) 建库：应无输出（静默成功）
rm -f wh.db && sqlite3 wh.db < schema.sql; echo "EXIT=$?"
# 期望：EXIT=0

# 2) 七条验收一次性跑完：应依次输出 0 / 三行余量 / 一行短拣 / 三口径 / 一行超差 / 四个数
sqlite3 wh.db < acceptance.sql
# 期望：见第五节表格的「期望输出」列

# 3) 幂等反测：同一条上架任务插两次，第二次必须失败
sqlite3 wh.db "INSERT INTO putaway_task(receipt_id,sku,batch_no,qty,to_bin,carton_sscc,status)
  VALUES(1,'SKU-A','B2611',100,1,'000000000000000011','DONE');" ; echo "EXIT=$?"
# 期望：UNIQUE constraint failed，EXIT=1

# 4) 只改余量不写流水的反测：Q1 必须从 0 变成 1（证明闭合查询有效）
sqlite3 wh.db "UPDATE stock_qty SET qty=qty+1 WHERE bin_id=1 AND sku='SKU-A';"
sqlite3 wh.db "SELECT count(*) FROM stock_qty q WHERE q.qty <>
  (SELECT coalesce(sum(delta),0) FROM stock_txn t
    WHERE t.bin_id=q.bin_id AND t.sku=q.sku AND t.batch_no=q.batch_no);"
# 期望：1（这就是「账实不符」的可检出形态）
```

## 参考资料

- [总览：七段库内作业链](../Overview/index.md)：本页实现的七段
- [库位模型与容量](../LocationModel/index.md)：`bin` 表的来源
- [库存快照与批次](../StockSnapshot/index.md)：Q1 的两条闭合关系
- [波次与拣选路径](../WavePicking/index.md)：短拣与三口径
- [复核、打包与交接](../Packing/index.md)：Q5 / Q6 的判据来源
- [循环盘点与差异处理](../CycleCount/index.md)：调整的四条铁律
- SQLite 官方文档（`GENERATED ALWAYS AS` 与部分索引）：<https://www.sqlite.org/lang_createtable.html>
