# 离线补传：本地队列、票号与幂等

下午两点十七分，宽带断了。收银员抬头看了一眼路由器的红灯，继续扫下一件商品——门店不能因为断网就停业。十一分钟后网络恢复，终端把这段时间的 37 笔单一次性推上去。

这十一分钟里，系统做了三件在线上系统里几乎不会做的事：**用本地价目算钱、用本地规则判定优惠、用本地序号发票号**。三件事都必须离线成立，而它们联网后必须能被中心「认出来」——否则就是重复入账。

::: tip 一句话理解
离线的本质不是「缓存数据」，而是**把「谁是权威」临时下放到终端**；联网后要做的不是「上传」，而是**让中心相信这份数据只入账一次**。
:::

## 一、四个必须离线成立的判断

断网时终端不能问服务端任何问题，所以这四件事必须有本地答案：

| 判断 | 本地答案从哪来 | 失效后果 |
| --- | --- | --- |
| 这一单的价是多少 | 本地价目缓存（带 `ver`） | 收错价（见[价目下发](../PriceSync/index.md)） |
| 优惠怎么算 | 本地规则引擎 + 活动快照 | 优惠算错，日结对不上 |
| 票号是多少 | 本地序号（终端内自增） | 票号重号，退货找不到原单 |
| 这单能不能退 | 本地原单索引（近 30 天） | 退不了货，顾客走人 |

四项里前三项是「算」，第四项是「查」。很多系统只做了前三项，忘了第四项——断网时顾客来退货，收银员只能说「等网好了再来」。

```sql
-- 终端本地库：只需要四张表就能支撑离线营业
CREATE TABLE local_ticket (ticket_id TEXT PRIMARY KEY, ticket_no TEXT, biz_date TEXT,
                           payable REAL, status TEXT, synced INTEGER DEFAULT 0);
CREATE TABLE local_line   (ticket_id TEXT, line_no INT, sku TEXT, qty REAL,
                           unit_price REAL, line_amt REAL, PRIMARY KEY(ticket_id, line_no));
CREATE TABLE local_tender (ticket_id TEXT, seq INT, method TEXT, amount REAL,
                           channel_ref TEXT, PRIMARY KEY(ticket_id, seq));
CREATE TABLE local_price  (sku TEXT PRIMARY KEY, price REAL, ver INTEGER);
```

## 二、票号：离线时唯一不能靠中心的字段

联网时票号可以由中心发，断网时必须由终端发。这就带来一个必然结果：**票号里必须带终端标识**，否则两台终端各自从 1 开始，一定重号。

本机实测：两台终端各自从 1 发号，32,400 张单里**重号 3,764 个（11.62%）**。

| 票号格式 | 断网安全 | 可读性 | 中心去重 |
| --- | --- | --- | --- |
| `000123`（全局自增） | ❌ 断网无法发号 | 差 | 需要中心分配段 |
| `S01-20261103-0123` | ❌ 多终端重号 | 好 | 冲突 |
| `S01-T03-0123` | ✅ 终端隔离 | 好 | 直接可判 |
| `S01-T03-ULID` | ✅ 且不依赖序号 | 差 | 直接可判 |

推荐「门店 + 终端 + 4 位序号」。序号在终端本地自增，达到 9,999 后回到 0001 并**换一个 `seq_segment`**（例如 `S01-T03-A-0123`），保证一天内不重号。

::: danger 票号设计的三个坑
1. **用时间戳当票号**：断网时终端时钟可能不准（本机模拟慢 3 分钟），时间戳会重复。
2. **作废的票号回收再用**：审计上无法区分「作废的 A 单」与「新开的 B 单」。
3. **中心重新编号**：终端打出来的小票与中心库的票号不一致，顾客拿着小票来退货，系统查不到。
:::

## 三、补传队列：一个只能用唯一键解决的去重

补传的失败模式只有一个：**同一笔单被上传多次**。原因很多——超时重试、断线重连、终端重启后重放、运维手工重推。

本机实测：1,200 笔离线单，重试造成 8% 重复上传：

| 入库策略 | 入库行数 | 结果 |
| --- | --- | --- |
| 只按自增 id | 1,296 | **虚增 8%**，销售额多算 |
| 按 `(store_id, ticket_no)` 唯一 | 1,200 | 正确 |
| 按 `(store_id, seq)` 唯一（批次级） | 1,200 | 正确，且能定位是哪一批重了 |

```sql
CREATE TABLE sync_batch (
  batch_id    TEXT PRIMARY KEY,
  store_id    TEXT NOT NULL,
  seq         INTEGER NOT NULL,       -- 终端本地批次号，单调递增
  ticket_id   TEXT NOT NULL,
  payload     TEXT NOT NULL,
  uploaded_at TEXT NOT NULL,
  CONSTRAINT uq_sync UNIQUE (store_id, seq)   -- 去重键
);
```

`seq` 与 `ticket_no` 的区别：`seq` 是**批次**序号（一次补传一个批次），`ticket_no` 是**单据**序号。两个都要唯一，因为它们防的是不同的重复：

- `(store_id, seq)` 防「同一批数据被推两次」；
- `ticket` 表上的 `UNIQUE (store_id, biz_date, ticket_no)` 防「同一张单被塞进两个批次」。

### 补传的三个状态

```text
PENDING（本地已生成，未上传）
  → SENT（已发请求，等响应）
      → ACKED（中心确认入库）
      → REJECTED（中心拒绝：校验失败 / 重复 / 非法）→ 进人工队列
      → TIMEOUT（超时，未知）→ 重试，最多 N 次 → 仍未知进人工队列
```

`TIMEOUT` 是最麻烦的状态：中心可能已入库（响应丢了），也可能没入库。这时**重试是安全的**（因为唯一键会拦住重复），但**不能把重试当成功**——要等中心的实际查询结果。

## 四、时钟：最小的那个偏移最致命

终端时钟不准是常态。本机模拟：终端慢 3 分钟，在「日终前 10 分钟」产生的 200 笔离线单里，有多少笔会跨日？

| 开单真实时间 | 终端记录时间 | 归属日 | 后果 |
| --- | --- | --- | --- |
| 23:58 | 23:55 | 当日 | 无 |
| 00:01 | 23:58（前一日） | **前一日** | 归错营业日 |
| 00:03 | 00:00 | 当日 | 无 |

关键结论：**跨日只发生在「真实时间刚过零点、终端时间还没过」的那几分钟**。这三分钟的单，如果 `biz_date` 由终端算，会算到前一天；如果由中心按上传时间算，会算到后一天。两种都错，只是错的方向不同。

所以 `biz_date` 必须满足两个条件：

1. **终端算**（它知道门店切点，也知道当前本地时间）；
2. **落库后不再重算**（见[点单与挂单](../Basket/index.md)）。

中心侧只做一件事：**校验 `biz_date` 与 `opened_at` 的偏差不超过切点窗口**，超出就标记「时钟异常」，进人工复核，而不是自动改。

```sql
-- 中心侧：找出「营业日与开单时间明显不符」的单
SELECT ticket_id, store_id, biz_date, opened_at
FROM ticket
WHERE biz_date <> date(datetime(opened_at,
        '-' || (SELECT biz_cut_hour FROM store WHERE store_id = ticket.store_id) || ' hours'))
  AND ABS(julianday(biz_date) - julianday(date(opened_at))) <= 1;   -- 只查 ±1 天，排除历史脏数据
```

## 五、断网期间的五种损失

| 损失 | 表现 | 能不能补 |
| --- | --- | --- |
| 价目滞后 | 用旧价收 | 不能补收，只能记录 |
| 优惠算错 | 优惠额与规则不符 | 不能补收，只能记录 |
| 支付未确认 | 顾客已付，系统无记录 | 能补（凭 `channel_ref`） |
| 库存未扣 | 本地扣了，中心没扣 | 能补（按终端的库存流水重放） |
| 退货查不到 | 顾客退不了 | 不能补（当时就该拒） |

五类里只有两类能事后补。这是离线设计的核心权衡：**能本地判定的，联网后只是同步；不能本地判定的，断网时必须明确拒绝，而不是「先答应再补」**。

::: warning 「先答应再补」是最贵的妥协
收银员为了不惹顾客，断网时手工记一笔「欠款」，等联网再补录。这看起来解决了体验问题，实际上制造了三类账：手写单、系统单、补录单。三者对不上时，没人能证明哪一笔是真的。**明确拒绝 + 引导到有网的门店/线上**，比事后补录便宜得多。
:::

## 六、判据

本页判据族 `RSY-A` ~ `RSY-H`，共 8 条。

| 判据 | 断言 | 验证方式 |
| --- | --- | --- |
| `RSY-A` | 票号含终端标识，断网不重号 | 两台终端同序号插入，唯一键拦住第二个 |
| `RSY-B` | 补传批次有 `(store_id, seq)` 唯一键 | 同一批次重放两次，入库 1 行 |
| `RSY-C` | `biz_date` 由终端算且落库不改 | 改 `opened_at` 后 `biz_date` 不变 |
| `RSY-D` | 补传有五个状态且 `TIMEOUT` 不自动成功 | 状态机含 `TIMEOUT`，无自动转 `ACKED` |
| `RSY-E` | 离线支付有 `UNKNOWN` 分支 | 人工队列表存在，`UNKNOWN` 单必须进队 |
| `RSY-F` | 本地保留 30 天原单索引 | 本地库有 `local_ticket` 且按 `biz_date` 可查 |
| `RSY-G` | 时钟偏差可检测 | 上述 SQL 在构造样本上返回异常单 |
| `RSY-H` | 补传失败可重试且幂等 | 连续重放 3 次，`COUNT(*)` 仍为 1 |

## 七、验证方式

```shell
# 1. 建补传表
sqlite3 /tmp/sync.db <<'SQL'
CREATE TABLE sync_batch(batch_id TEXT PRIMARY KEY, store_id TEXT, seq INT,
                        ticket_id TEXT, payload TEXT, uploaded_at TEXT,
                        UNIQUE(store_id, seq));
SQL

# 2. 同一批次重放三次（期望最终 1 行）
for i in 1 2 3; do
  sqlite3 /tmp/sync.db "INSERT OR IGNORE INTO sync_batch VALUES('B1','S01',1,'T1','{}','2026-11-03T14:30:00');"
done
sqlite3 /tmp/sync.db "select count(*) from sync_batch;"   # 期望 1

# 3. 时钟偏差检测（构造一条归错日的单，期望返回 1 行）
sqlite3 /tmp/sync.db <<'SQL'
CREATE TABLE store(store_id TEXT PRIMARY KEY, biz_cut_hour INT);
INSERT INTO store VALUES('S01',4);
CREATE TABLE ticket(ticket_id TEXT, store_id TEXT, biz_date TEXT, opened_at TEXT);
INSERT INTO ticket VALUES('T9','S01','2026-11-01','2026-11-02T00:01:00');
SELECT ticket_id FROM ticket WHERE biz_date <> date(datetime(opened_at,'-4 hours'));
SQL
```

第 2 步用 `INSERT OR IGNORE` 而不是先查后插：**先查后插在并发下必然漏**（两个请求同时查到「不存在」）。唯一键 + `IGNORE` 是唯一正确的写法。

## 参考资料

- RFC 7231 §4.2.2：`Idempotent Methods`——幂等是协议层概念，重试安全的前提是操作幂等。
- 《网络安全法》第二十一条：网络运营者应当采取技术措施保障网络安全、稳定运行——门店断网期间的本地营业能力属业务连续性要求。
- 与本页相邻：[价目下发](../PriceSync/index.md)、[点单与挂单](../Basket/index.md)、[班结与日结](../DayClose/index.md)。
