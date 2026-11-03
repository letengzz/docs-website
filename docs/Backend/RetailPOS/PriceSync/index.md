# 价目下发：版本、生效时点与离线缓存

「顾客说标价 9.9，你们收了 12.9。」这句话在门店里几乎每周都会出现一次。查下去通常有两种结论：价签没换，或者终端没同步。**两种都不是收银员的问题，但都发生在收银台。**

价目是一个典型的「读多写少、但一旦错就直影响钱」的数据。它的难点不在存储，而在**同一时刻只能有一个生效版本，而这个版本必须在断网的终端上也成立**。

::: tip 一句话理解
收错价的根因几乎从不在收银端，而在「哪一版价目算数」——所以价目必须带**版本号**与**生效时点**，两者缺一，收银端就只能靠猜。
:::

## 一、五种价格，一个优先级

门店里的「价格」至少有五种，它们不是平级的：

| 价格类型 | 来源 | 生效范围 | 优先级 |
| --- | --- | --- | --- |
| 原价（吊牌价） | 商品主数据 | 全渠道 | 最低（兜底） |
| 门店价 | 门店差异化定价 | 单店 | 覆盖原价 |
| 会员价 | 会员等级 / 权益 | 人群 | 覆盖门店价 |
| 特价（促销） | 活动单 | 时间段 + 门店 | 覆盖会员价 |
| 协议价（团购） | 合同 | 客户 + 时段 | 覆盖特价 |

优先级必须**写死在代码里**，不能让收银员选。让收银员选价格的系统，最后一定会出现「同一件商品两个顾客两个价」的投诉，而且查不清是谁改的。

::: danger 三种「多价格」的实现错误
1. **用 `price` 一个字段存所有价**：会员价一改，原价就丢了，退货时算不出「按哪个价退」。
2. **用生效时间戳但没有版本号**：同一秒内两条变价单，谁生效取决于插入顺序。
3. **让客户端算「哪个价更低就取哪个」**：促销的本意是「限时」，取低会让过期的特价永远生效。
:::

## 二、版本模型：三个必须的字段

```sql
CREATE TABLE price_version (
  store_id     TEXT NOT NULL,
  sku          TEXT NOT NULL,
  ver          INTEGER NOT NULL,        -- 单调递增，永不复用
  price        REAL NOT NULL,
  member_price REAL,
  effective_at TEXT NOT NULL,           -- 生效时点（门店本地时间）
  expire_at    TEXT,                    -- 失效时点，空=长期
  change_id    TEXT NOT NULL,           -- 关联变价单，可追溯谁改的
  PRIMARY KEY (store_id, sku, ver),
  CONSTRAINT ck_price CHECK (price >= 0),
  CONSTRAINT ck_ver   CHECK (ver > 0)
);
```

三个字段各自解决一个问题：

| 字段 | 解决的问题 | 没有它的后果 |
| --- | --- | --- |
| `ver` | 「这一版算不算最新」 | 无法判断终端是否滞后 |
| `effective_at` | 「什么时候开始算」 | 提前生效或延迟生效 |
| `change_id` | 「谁改的、为什么改」 | 事后无法追责，也无法回滚 |

### 版本号必须单调、不可复用

```sql
-- 发布一个新版本：取当前最大值 + 1，不是 max(ver)+1 的临时计算
INSERT INTO price_version (store_id, sku, ver, price, effective_at, change_id)
SELECT 'S01', 'K0001',
       COALESCE(MAX(ver), 0) + 1,
       9.90, '2026-11-05 00:00:00', 'CHG-20261103-001'
FROM price_version WHERE store_id='S01' AND sku='K0001';
```

用 `MAX(ver)+1` 而不是时间戳，原因是**时间戳会重复**（批量变价几十个 SKU 在同一秒），而版本号不会。

::: warning 回滚不是「改回旧价」
有人把回滚理解成「把 price 改回旧值」，这会生成一个新版本（ver+1）而不是回到旧版本。两者在审计上的意义完全不同：前者是「又改了一次」，后者是「撤销上一次」。正确的回滚是**发布一个新版本，其价格等于旧版本的价格，`change_id` 指向回滚单**——版本号永远向前。
:::

## 三、下发链路：三道闸门

```text
变价单审批 → 价目库（带 ver）→ 门店快照 → 终端缓存
   ①            ②               ③          ④
```

| 环节 | 闸门 | 不设闸门会怎样 |
| --- | --- | --- |
| ① 审批 | 改价必须有人批，且记录生效时点 | 门店自行改价，毛利失控 |
| ② 发布 | `effective_at` 必须 ≥ 当前时间 + 缓冲 | 发布即生效，终端来不及拉 |
| ③ 同步 | 门店快照与中心对账，版本号必须连续 | 中间缺一版，终端跳到新价时缺失上下文 |
| ④ 缓存 | 终端启动先拉版本号，只拉增量 | 每次全量拉，弱网下永远拉不完 |

第 ④ 步是离线场景的关键：终端不能「拉全量价目」，必须能**只靠版本号判断自己是否最新**。

```text
GET /pos/price/versions?store_id=S01&since=17
→ { "current": 19, "items": [ {sku, ver:18, price}, {sku, ver:19, price} ] }
```

终端本地存 `last_ver`，每次开机与每 15 分钟比对一次。**比对失败不影响收银**——继续用本地价目，但要在票面上打一个标记（见下节）。

## 四、滞后：一个净额骗人的第二种形态

本机实测（30,000 笔，12 店 × 30 天，每版变价 25% 的 SKU）：

| 指标 | 读数 |
| --- | --- |
| 价目滞后单 | 1,837 笔（6.12%） |
| 受影响明细行 | 383 行 |
| 按当日应生效价 − 实收 | **−440.68 元** |
| 其中少收 | 2,145.95 元 |
| 其中多收 | 2,586.63 元 |
| 双向绝对值 | 4,732.59 元 |

净额 −440.68 元，对 272 万销售额来说是 0.016%。但真实影响是 4,732.59 元，**净额只暴露了 9.3%**。

::: danger 「净额接近 0」是最危险的信号
少收与多收同时存在时，净额会互相抵消。管理上看「差异率 0.016%，正常」，实际上：
- 少收的 2,145.95 元是**利润直接损失**；
- 多收的 2,586.63 元是**投诉与退款的来源**，而且退款时还要再赔一次体验。

这两类问题需要完全不同的处置（补价签 vs 补培训/补同步），但净额把它们混成了一个数。
:::

### 滞后检测怎么写

不要用「终端最后同步时间」判断——那只能说明终端活着，不能说明价目对。要用**成交价与应生效价的比对**：

```sql
-- 找出成交价与「开单时点应生效价」不一致的明细行
SELECT l.ticket_id, l.sku, l.unit_price AS sold, p.price AS should
FROM ticket_line l
JOIN ticket t USING (ticket_id)
JOIN price_version p
  ON p.store_id = t.store_id AND p.sku = l.sku
 AND p.ver = (SELECT MAX(ver) FROM price_version
              WHERE store_id = t.store_id AND sku = l.sku
                AND effective_at <= t.opened_at)
WHERE ABS(l.unit_price - p.price) > 0.001;
```

这条 SQL 有两个细节值得注意：

1. **用 `t.opened_at` 而不是 `now()`**：判的是「当时该收多少」，不是「现在该收多少」。
2. **用 `MAX(ver)` 而不是 `MAX(effective_at)`**：同一时点可能有多版（补发），版本号才是权威。

## 五、票面上的「价目版本」标记

一张小票上打印 `价目版本: v19`，看起来是技术细节，实际上是**争议处理的关键证据**。

| 场景 | 有版本号 | 没有版本号 |
| --- | --- | --- |
| 顾客投诉价格 | 一查就知道当时用的哪版 | 只能全表比对，最后不了了之 |
| 总部核查 | 抽样即可定位滞后门店 | 无法区分「价签错」与「终端错」 |
| 退货 | 按原版本价退，不按当前价 | 涨价后按新价退，亏差价 |

小票上不必打印版本号的完整值，可以打印一个短码（`v19`），但**数据库里必须存完整版本**。

## 六、判据

本页判据族 `RSP-A` ~ `RSP-H`，共 8 条。

| 判据 | 断言 | 验证方式 |
| --- | --- | --- |
| `RSP-A` | 价目表有 `ver` 且 `(store, sku, ver)` 唯一 | 插入重复版本被拒 |
| `RSP-B` | 发布新版本用 `MAX(ver)+1`，不复用 | 连续两次发布，版本号递增且不重复 |
| `RSP-C` | 每条价目都有 `effective_at` | 空值插入被 `NOT NULL` 拒绝 |
| `RSP-D` | 每条价目能追溯到 `change_id` | 随机抽 10 行，`change_id` 均能在变价单表找到 |
| `RSP-E` | 终端可仅凭版本号判断是否最新 | `GET /pos/price/versions?since=` 返回增量而非全量 |
| `RSP-F` | 小票记录 `price_ver` | `ticket.price_ver` 非空且 ≤ 当前版本 |
| `RSP-G` | 滞后检测按 `opened_at` 取应生效价 | 上述 SQL 在滞后样本上返回 383 行 |
| `RSP-H` | 回滚生成新版本而非改旧版本 | 回滚后 `ver` 递增，旧版本行未被 `UPDATE` |

## 七、验证方式

```shell
# 1. 建最小价目表并发布三版
sqlite3 /tmp/price.db <<'SQL'
CREATE TABLE price_version(store_id TEXT, sku TEXT, ver INTEGER, price REAL,
                           effective_at TEXT, change_id TEXT,
                           PRIMARY KEY(store_id, sku, ver));
INSERT INTO price_version VALUES('S01','K0001',1,12.0,'2026-10-01 00:00:00','CHG-1');
INSERT INTO price_version VALUES('S01','K0001',2,9.9 ,'2026-10-08 00:00:00','CHG-2');
INSERT INTO price_version VALUES('S01','K0001',3,15.0,'2026-10-15 00:00:00','CHG-3');
SQL

# 2. 取「2026-10-12 开单时应生效价」——期望 9.9
sqlite3 /tmp/price.db "
select price from price_version
where store_id='S01' and sku='K0001' and effective_at <= '2026-10-12 10:00:00'
order by ver desc limit 1;"

# 3. 增量下发：只要 ver > 1 的（期望两行）
sqlite3 /tmp/price.db "select ver, price from price_version where ver > 1 order by ver;"

# 4. 重发同一版本必须失败（期望 UNIQUE constraint failed）
sqlite3 /tmp/price.db "INSERT INTO price_version VALUES('S01','K0001',3,15.0,'2026-10-15 00:00:00','CHG-4');" \
  || echo "已按预期拒绝"
```

第 2 步的 `ORDER BY ver DESC LIMIT 1` 是整个价目模块最短、也最重要的 SQL：**按生效时点筛选，按版本号取最新**。写成 `ORDER BY effective_at DESC` 在补发场景下会取错版本。

## 参考资料

- 《中华人民共和国价格法》第十三条：经营者销售商品应当明码标价，注明商品的品名、产地、规格、等级、计价单位、价格。
- 国家市场监督管理总局《明码标价和禁止价格欺诈规定》（2022 年第 56 号令）第七条：经营者不得在标价之外加价出售商品。
- 与本页相邻：[总览](../Overview/index.md)、[优惠与凑整](../PromotionStack/index.md)、[点单与挂单](../Basket/index.md)。
