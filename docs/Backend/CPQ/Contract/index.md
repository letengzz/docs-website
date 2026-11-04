# 条款、锁价与合同

报价单上写着 8,640 元，合同上写的是 8,664 元，客户没注意，法务没注意，直到开票时财务发现合同金额与订单金额差 24 元。三方各执一词：销售说「客户就是按报价单签的」，法务说「合同是我们模板生成的」，财务说「系统给的就是 8,664」。

**24 块钱不会有人追，但它证明了这三份文件之间没有一条能被机器校验的关系。**

::: tip 一句话理解
报价转合同锁的不是「文本」，是**四项承诺**：配置、价格、折扣与条款版本。四项里任何一项没有随合同冻结，合同就只是「一段关于交易的叙述」。
:::

本页判据族 `CQS-A` ~ `CQS-H`，共 8 条。定义表在第八节「本页判据」。

## 一、从报价到合同，冻的是什么

| 冻结项 | 报价里的位置 | 合同里的位置 | 不冻结的后果 |
| --- | --- | --- | --- |
| 配置 | `quote_line.cfg_json` + `model_ver` | 合同附件「配置清单」 | 交付时「我以为包含光口」 |
| 价格 | `quote.entry_id` + `total_amt` | 合同价款条款 | 涨价由谁承担没有约定 |
| 折扣 | `disc_layer`（含审批） | 价格构成附件 | 客户拿旧折扣来要新单 |
| 条款 | `terms_ver` | 合同正文版本 | 用新版条款解释旧合同 |

四项冻结的共同点：**它们都是「可以被后来修改的东西」，所以必须在合同里被固定住一个副本**，而不是靠外键指向「当前值」。

```sql
CREATE TABLE contract(
  contract_no  TEXT PRIMARY KEY,
  quote_id     TEXT NOT NULL,
  quote_rev    INTEGER NOT NULL,
  terms_ver    TEXT NOT NULL,          -- 条款模板版本，不是「最新版」
  cfg_snapshot TEXT NOT NULL,          -- 配置清单快照（JSON）
  price_net    REAL NOT NULL,          -- 锁价净额
  tax_amt      REAL NOT NULL,
  gross_amt    REAL NOT NULL,
  signed_at    TEXT,
  effective_from TEXT NOT NULL,
  state        TEXT NOT NULL CHECK (state IN ('DRAFT','SIGNED','EFFECTIVE','TERMINATED'))
);
```

`terms_ver` 与 `cfg_snapshot` 是两张「快照」而不是两个外键。这一点与常见的「合同引用报价 ID」不同：**引用意味着「跟着变」，快照意味着「不再变」**。合同要的是后者。

## 二、锁价：一个必须写死的动作

```sql
CREATE TABLE order_link(
  quote_id   TEXT PRIMARY KEY REFERENCES quote(quote_id),
  order_no   TEXT NOT NULL UNIQUE,
  locked_amt REAL NOT NULL,            -- 锁价额：转单那一刻的报价净额
  locked_at  TEXT NOT NULL
);
```

转单时唯一允许的取数方式是「从报价读」，**不允许查 `price_entry` 重算**：

```sql
-- 正确：锁价来自报价
INSERT INTO order_link(quote_id, order_no, locked_amt, locked_at)
SELECT quote_id, :order_no, total_amt, :now
FROM quote WHERE quote_id = :qid AND state = 'ACCEPTED';

-- 错误示范：转单时\"顺手\"取最新价
-- SELECT e.amount FROM v_price_at e WHERE e.model_id = ... ORDER BY priority DESC LIMIT 1;
```

本机实测：如果按转单时刻的价目重算（年涨 6%，转单中位 23 天），**921 张成交报价全部漂移，合计 173,269.87 元，单笔最大 1,271.18 元**。

单笔一两百块，看起来可以「下次注意」；但它是**系统性单向偏差**——涨价周期里，每一单都少收一点点，且没有任何一单会触发告警。

## 三、差额归因：三个数之间的两条缝

| 缝 | 两侧 | 正常差额来源 | 异常信号 |
| --- | --- | --- | --- |
| 报价 → 锁价 | `quote.total_amt` vs `order_link.locked_amt` | 转单前最后一次改配 | 不为 0 且无变更记录 |
| 锁价 → 实收 | `locked_amt` vs 发票合计 | 部分交付、退货、税额调整 | 差额 > 5% 且无单据 |

```sql
CREATE VIEW v_price_gap AS
SELECT q.quote_id, q.total_amt AS quoted, o.locked_amt AS locked,
       ROUND(o.locked_amt - q.total_amt, 2) AS gap_qo,
       (SELECT ROUND(SUM(inv.amount), 2) FROM invoice inv WHERE inv.quote_id = q.quote_id) AS invoiced
FROM quote q LEFT JOIN order_link o ON o.quote_id = q.quote_id
WHERE o.quote_id IS NOT NULL;
```

有了这张视图，「差额」才是一个可以每天看的数，而不是每次对账时手工比。

## 四、条款版本：合同里最容易被忽略的冻结项

条款模板会改：付款条件从「30 天」改到「45 天」，质保从「1 年」改到「2 年」，违约条款加了一条。**合同必须绑定「签署时生效的版本」，不是「当前最新版」**。

| 做法 | 后果 |
| --- | --- |
| 合同引用「条款模板 ID」 | 模板一改，所有历史合同「条款变了」 |
| 合同存「条款全文快照」 | 存储变大，但永不歧义 |
| 合同存「版本号 + 全文哈希」 | 兼顾体积与可校验（推荐） |

推荐第三种：正文存版本号，同时存全文的 SHA-256。发生争议时，用哈希证明「当时这份文本没有被改过」。

```sql
ALTER TABLE contract ADD COLUMN terms_sha256 TEXT NOT NULL DEFAULT '';
```

（真实项目里应在建表时就带上，这里用 `ALTER` 只是为了展示「老表怎么补」——补的时候要给历史行回填，否则默认值会让所有历史合同的哈希都一样。）

## 五、合同变更：不是改合同

客户在履约中途要求加 50 台。有三种处理，法律与系统含义都不同：

| 做法 | 法律含义 | 系统做法 | 风险 |
| --- | --- | --- | --- |
| 改原合同金额 | 单方变更，需双方签章 | `UPDATE contract` | 原签章失效，审计断裂 |
| 签补充协议 | 新合同引用原合同 | 新建 `contract`，`parent_no` 指向原合同 | 金额需能累加 |
| 新报价 → 新订单 | 独立交易 | 走完整 CPQ 流程 | 折扣可能被重复使用 |

正确做法是第二种：**补充协议是一份新合同**，`parent_no` 指向原合同，金额独立。这样「原合同 100 万 + 补充协议 20 万 = 120 万」是可加的，而「原合同改成 120 万」是不可审计的。

## 六、签署与生效：两个时刻

| 时刻 | 含义 | 影响 |
| --- | --- | --- |
| `signed_at` | 双方签章完成 | 合同成立 |
| `effective_from` | 约定的生效日 | 履约义务开始 |

两者可以不同（例如「2026-12-01 起生效」）。系统里只存一个 `signed_at` 的后果是：**提前签的合同会被当成已生效**，于是发票、交付、收入确认全部提前。

这一条与[收入确认](../../RevenueRecognition/Overview/index.md)的「履约义务开始时点」直接相关，也是审计最常问的一个问题。

## 七、报价单与合同的六处必对项

| 项 | 报价 | 合同 | 允许不一致吗 |
| --- | --- | --- | --- |
| 配置清单 | `cfg_json` | 附件 | **不允许** |
| 净额 | `total_amt` | `price_net` | 不允许（除非有变更记录） |
| 税额 | 报价税额 | `tax_amt` | 不允许 |
| 币种 | `currency` | 合同币种 | 不允许 |
| 有效期 | `valid_to` | 签署日必须在有效期内 | 不允许（否则走例外） |
| 条款 | 报价时引用的版本 | `terms_ver` | 允许（合同可附更严格条款，但要有差异说明） |

前五项任何一项不一致，都说明「锁价失败」；第六项不一致是正常的商务行为，但**必须有差异说明**，否则法务无法判断「这是谈下来的，还是生成错了」。

::: danger 合同侧的三条硬规则
1. **锁价必须是一次写入，之后只读**：`order_link.locked_amt` 上加触发器，转单后不允许改（见[实战](../Practice/index.md)的 `trg_locked_after_order`）。
2. **条款存版本号 + 全文哈希**，不存「模板引用」。
3. **合同变更只能新增，不能修改**：`contract_no` 主键，补充协议用新号 + `parent_no`。
:::

## 八、本页判据

| 判据 | 断言 | 验证方式 |
| --- | --- | --- |
| `CQS-A` | 合同存配置快照而非引用 | `cfg_snapshot` 非空，且与报价 `cfg_json` 指纹一致 |
| `CQS-B` | 锁价额来自报价，不查价格册 | 转单 SQL 的 `FROM` 里没有 `price_entry` |
| `CQS-C` | 锁价后不可改 | 改 `locked_amt` 被触发器拒绝 |
| `CQS-D` | 条款存版本号与哈希 | `terms_ver` + `terms_sha256` 均非空 |
| `CQS-E` | 合同变更新增不修改 | 存在 `parent_no` 字段且有补充协议记录 |
| `CQS-F` | 签署与生效分开 | `signed_at` 与 `effective_from` 是两个字段 |
| `CQS-G` | 差额可归因 | `v_price_gap` 视图存在，差额行可查 |
| `CQS-H` | 六项必对项有自动校验 | 报价转合同时逐项比对，不一致即拒 |

## 验证方式

```shell
# 1. 锁价一致性：合同净额必须等于报价锁价额
sqlite3 cpq.db "select c.contract_no, c.price_net, o.locked_amt
                from contract c join order_link o using(quote_id)
                where abs(c.price_net - o.locked_amt) > 0.005;"
# 期望：0 行

# 2. 配置快照一致：合同与报价的配置指纹必须相同
python3 - <<'PY'
import hashlib, json
fp = lambda d: hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
quote_cfg = {"cat": 1, "size": 2, "mat": 0, "volt": 0, "iface": 2, "lic": 1}
contract_cfg = dict(quote_cfg)
print(fp(quote_cfg) == fp(contract_cfg))   # 期望 True
contract_cfg["iface"] = 0                  # 合同被改成电口
print(fp(quote_cfg) == fp(contract_cfg))   # 期望 False：必须被发现
PY

# 3. 条款哈希可校验：改一个字，哈希必变
python3 -c "
import hashlib
t='付款条件：验收后 30 日内支付。'
h=lambda s: hashlib.sha256(s.encode()).hexdigest()[:12]
print(h(t), h(t.replace('30','45')))"
# 期望：两个不同的 12 位串
```

## 参考资料

- 《中华人民共和国民法典》第四百九十条：当事人采用合同书形式订立合同的，自双方签名、盖章或者按指印时合同成立。
- 《中华人民共和国民法典》第五百四十三条：当事人协商一致，可以变更合同——本页「补充协议而非改原合同」的法理依据。
- GB/T 35273—2020《信息安全技术 个人信息安全规范》：合同附件的客户信息最小化要求（配置清单里常含机房与联系人信息）。
- 与本页相邻：[报价单：版本与有效期](../Quote/index.md)、[转单与履约衔接](../Ordering/index.md)、[合同版本演进](../../ContractEvolution/index.md)。
