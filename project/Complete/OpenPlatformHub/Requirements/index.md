# 第 1 周第 1 步 · 需求拆分：八条用户故事与验收条件

周期 8 的第一步不是写代码，而是把「开放平台」这件模糊的事拆成**八条能被判定真假**的用户故事，再据此定下十张表与四条接口契约。

![四周里程碑与六个模块](../assets/oph-roadmap.svg)

本页判据族 `EOP-A` ~ `EOP-H`，共 8 条。定义表在第六节。

## 一、八条用户故事

| 编号 | 角色 | 故事 | 验收条件（可判定） |
| --- | --- | --- | --- |
| `US-01` | 集成方 | 我要在控制台建一个应用并拿到 `app_id` 与一次性可见的 `app_secret` | 建完再查接口，返回的是掩码（前 4 + 后 4）；`app_secret` 明文只出现在创建响应里一次 |
| `US-02` | 集成方 | 我要能自助轮换密钥而不停机 | 轮换后旧密钥仍可验签（`rotating`），新请求用新密钥签；30 天后旧密钥验签返回 401 |
| `US-03` | 集成方 | 我要用 `client_credentials` 换一个只能读库存的令牌 | 令牌 `scope` 只含 `inventory.read`；拿它调写接口必须是 403 而非 401 |
| `US-04` | 集成方 | 我要能撤销一个令牌并立刻生效 | 撤销后 1 秒内同一令牌调用返回 401（不是等 TTL 到期） |
| `US-05` | 平台运营 | 我要看到每个应用当月的调用量与配额余量 | `/admin/usage?app_id=...&month=2026-11` 返回 `units` 与 `quota_remaining`，且与 `usage` 表 `sum(units)` 相等 |
| `US-06` | 平台运营 | 我要能对超配额的应用返回 429 并告诉它等多久 | 429 响应含 `Retry-After`、`X-Quota-Limit`、`X-Quota-Remaining`、`X-Quota-Scope` 四个头 |
| `US-07` | 集成方 | 我要在库存变化时收到 webhook，且能去重 | 事件带 `event_id`；同一 `event_id` 重投 3 次，接收方按 `event_id` 只处理一次 |
| `US-08` | 财务 | 我要一张能下钻到每次调用的账单 | 账单金额 = `sum(invoice_line.amount)`；任一 `invoice_line` 能反查到 `usage_id` 列表 |

::: tip 为什么是这八条
八条覆盖了七段链的**每一个接缝**，且每条都对应一次「能被拒绝」的判定：`US-02` 判「轮换是否双活」、`US-04` 判「撤销是否真的立即」、`US-05` 判「计量是否与账单同源」、`US-06` 判「配额是否可解释」、`US-07` 判「重投是否可去重」、`US-08` 判「账单是否可下钻」。剩下的两条（`US-01`/`US-03`）是入口，但也都有硬判定。
:::

## 二、范围外（明确不做）

| 不做 | 原因 | 什么时候做 |
| --- | --- | --- |
| 发票开具与支付通道 | 与计费口径无关，属于财务系统 | 第 4 周之后 |
| 多副本限流 | 单进程足够验证口径 | 第 3 周 |
| OAuth 隐式模式 | 已被 OAuth 2.1 移除 | 永不做 |
| 客户自定义报表 | 需求未收敛 | 第 4 周视情况 |

## 三、十张表与六条不变量

```sql
-- ① 应用：配额与计费的粒度
CREATE TABLE app (
  app_id       TEXT PRIMARY KEY,
  tenant_id    TEXT NOT NULL,
  name         TEXT NOT NULL,
  status       TEXT NOT NULL DEFAULT 'active',   -- active | suspended
  cred_version INTEGER NOT NULL DEFAULT 1,       -- 轮换密钥 +1，旧令牌立即失效
  created_at   INTEGER NOT NULL
);

-- ② 密钥：一个应用可同时存在 active + rotating 两把
CREATE TABLE app_key (
  key_id     TEXT PRIMARY KEY,
  app_id     TEXT NOT NULL REFERENCES app(app_id),
  secret_enc TEXT NOT NULL,
  status     TEXT NOT NULL,                      -- active | rotating | revoked
  created_at INTEGER NOT NULL,
  expires_at INTEGER,
  UNIQUE(app_id, key_id)
);

-- ③ 防重放：nonce 存活期 = 2 × 时间窗口
CREATE TABLE nonce (
  app_id   TEXT NOT NULL,
  nonce    TEXT NOT NULL,
  seen_at  INTEGER NOT NULL,
  PRIMARY KEY (app_id, nonce)
);

-- ④ 令牌：只存哈希
CREATE TABLE oauth_token (
  token_hash   TEXT PRIMARY KEY,
  app_id       TEXT NOT NULL REFERENCES app(app_id),
  subject      TEXT,                             -- client_credentials 为 NULL
  scopes       TEXT NOT NULL,
  cred_version INTEGER NOT NULL,
  issued_at    INTEGER NOT NULL,
  expires_at   INTEGER NOT NULL,
  revoked_at   INTEGER
);

-- ⑤ 授权码（PKCE）
CREATE TABLE oauth_code (
  code_hash      TEXT PRIMARY KEY,
  app_id         TEXT NOT NULL,
  subject        TEXT NOT NULL,
  scopes         TEXT NOT NULL,
  code_challenge TEXT NOT NULL,
  redirect_uri   TEXT NOT NULL,
  expires_at     INTEGER NOT NULL,
  used_at        INTEGER
);

-- ⑥ 配额策略：速率与总量分开
CREATE TABLE quota_policy (
  app_id     TEXT PRIMARY KEY REFERENCES app(app_id),
  rate_per_s INTEGER NOT NULL,
  burst      INTEGER NOT NULL,
  total_month INTEGER NOT NULL
);

-- ⑦ 用量：一次成功调用一行
CREATE TABLE usage (
  usage_id   TEXT PRIMARY KEY,
  app_id     TEXT NOT NULL REFERENCES app(app_id),
  request_id TEXT NOT NULL,
  trace_id   TEXT NOT NULL,
  path       TEXT NOT NULL,
  status     INTEGER NOT NULL,
  units      INTEGER NOT NULL,
  ts         INTEGER NOT NULL,
  UNIQUE(app_id, request_id)
);
CREATE INDEX idx_usage_agg ON usage(app_id, ts);

-- ⑧ 订阅
CREATE TABLE subscription (
  sub_id   TEXT PRIMARY KEY,
  app_id   TEXT NOT NULL REFERENCES app(app_id),
  endpoint TEXT NOT NULL,
  events   TEXT NOT NULL,
  secret   TEXT NOT NULL,
  status   TEXT NOT NULL DEFAULT 'active',
  failure_streak INTEGER NOT NULL DEFAULT 0
);

-- ⑨ 事件（只追加）
CREATE TABLE event (
  event_id  TEXT PRIMARY KEY,
  type      TEXT NOT NULL,
  aggregate TEXT NOT NULL,
  payload   TEXT NOT NULL,
  ts        INTEGER NOT NULL
);

-- ⑩ 投递
CREATE TABLE delivery (
  delivery_id TEXT PRIMARY KEY,
  event_id    TEXT NOT NULL REFERENCES event(event_id),
  sub_id      TEXT NOT NULL REFERENCES subscription(sub_id),
  attempt     INTEGER NOT NULL,
  status      TEXT NOT NULL,                     -- pending | delivered | failed | dead
  http_status INTEGER,
  next_at     INTEGER,
  UNIQUE(event_id, sub_id, attempt)
);

-- 账单两表（第 4 周的挂点，先建出来保证外键可引用）
CREATE TABLE invoice (
  invoice_no TEXT PRIMARY KEY,
  app_id     TEXT NOT NULL REFERENCES app(app_id),
  period     TEXT NOT NULL,                      -- 2026-11
  amount_cents INTEGER NOT NULL,
  status     TEXT NOT NULL DEFAULT 'draft',      -- draft | issued | paid
  UNIQUE(app_id, period)
);
CREATE TABLE invoice_line (
  line_id    TEXT PRIMARY KEY,
  invoice_no TEXT NOT NULL REFERENCES invoice(invoice_no),
  usage_id   TEXT REFERENCES usage(usage_id),
  units      INTEGER NOT NULL,
  amount_cents INTEGER NOT NULL
);
```

六条不变量（用 SQL 就能查，违反即缺陷）：

| # | 不变量 | 违反时的 SQL 现象 |
| --- | --- | --- |
| `INV-1` | 每条 `usage` 的 `app_id` 必须存在 | 左连接 `app` 出现空行 |
| `INV-2` | 同一 `(app_id, request_id)` 只有一行 | `GROUP BY ... HAVING count(*) > 1` 非空 |
| `INV-3` | 每条 `invoice_line` 的 `units` 之和 = `invoice` 对应期间 `usage.units` 之和 | 两个 `sum` 不相等 |
| `INV-4` | `delivery.attempt` 单调递增且 ≤ 5 | 存在 `attempt > 5` |
| `INV-5` | `oauth_token.cred_version` ≤ `app.cred_version` | 存在大于的行（意味着轮换没生效） |
| `INV-6` | `quota_policy` 每个 `app_id` 最多一行 | 出现重复行 |

## 四、四条接口契约

```text
POST /oauth/token          客户端凭证 / 授权码换令牌
POST /v1/inventory:read    受签名保护的业务接口（示例）
GET  /admin/usage          用量与配额余量（运营）
POST /webhooks/replay      事件重放（运营）
```

契约的公共部分（所有接口都遵守）：

```http
POST /v1/inventory:read HTTP/1.1
X-App-Id: app_7f3a91
X-Key-Id: k_2026_11
X-Timestamp: 1790000000
X-Nonce: 7c1e9a04b2
X-Request-Id: req-000123
X-Signature: 5f2b...（64 位小写 hex）
Content-Type: application/json

{"sku":"A1"}
```

| 字段 | 谁生成 | 生命周期 | 缺了会怎样 |
| --- | --- | --- | --- |
| `X-App-Id` | 平台 | 永久 | 401 `invalid_credential` |
| `X-Timestamp` | 客户端 | 单次 | 签名串对不上 |
| `X-Nonce` | 客户端 | 单次（每次重试都要换） | 409 `duplicate_nonce` |
| `X-Request-Id` | 客户端 | 整个重试过程不变 | 重复计费 |
| `X-Signature` | 客户端 | 单次 | 401 `invalid_signature` |

## 五、验收：今天这一步怎么算做完

```shell
# 1. 建库并执行 DDL（把上一节的代码块存成 /tmp/ddl.sql）
sqlite3 /tmp/oph.db < /tmp/ddl.sql
sqlite3 /tmp/oph.db ".tables"
# 期望：app app_key delivery event invoice invoice_line nonce oauth_code oauth_token quota_policy subscription usage

# 2. 六条不变量逐条跑（此时表为空，全部应为 0）
sqlite3 /tmp/oph.db <<'SQL'
SELECT 'INV-1', count(*) FROM usage u LEFT JOIN app a ON a.app_id=u.app_id WHERE a.app_id IS NULL;
SELECT 'INV-2', count(*) FROM (SELECT 1 FROM usage GROUP BY app_id, request_id HAVING count(*)>1);
SELECT 'INV-4', count(*) FROM delivery WHERE attempt > 5;
SQL
# 期望：三行都是 0

# 3. 契约能被 mock 跑通：签一次名，服务端按同样规则重算
echo -n '{"sku":"A1"}' | python3 sign.py --app app_7f3a91 --path /v1/inventory:read
# 期望：打印五段签名串与 64 位小写 hex
```

**结果读法**：第 1 步如果 `.tables` 少于 12 张，说明 DDL 中途失败（外键顺序或保留字）；第 3 步如果打印的串不足五段，说明 `body_sha256` 没参与拼接——这条到了第 2 周会变成「客户签名永远对不上」的工单。

## 六、判据族

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `EOP-A` | `app_key` 能否同时存在 `active` 与 `rotating` 两行 | 不能即无法不停机轮换 | 唯一约束用 `UNIQUE(app_id, key_id)` |
| `EOP-B` | `usage` 是否有 `(app_id, request_id)` 唯一键 | 无则重试会重复计费 | 加唯一索引，写入用 `INSERT OR IGNORE` |
| `EOP-C` | `quota_policy` 是否把速率、突发、总量分成三列 | 合成一列即无法解释 429 | 拆 `rate_per_s` / `burst` / `total_month` |
| `EOP-D` | `oauth_token` 是否存哈希且带 `cred_version` | 存明文或缺少版本即无法即时撤销 | 加 `token_hash` 与 `cred_version` |
| `EOP-E` | 事件与投递是否分表且 `attempt` 有上限 | 合表即无法统计重投次数 | `event` / `delivery` 两张表 |
| `EOP-F` | 账单行是否可反查 `usage_id` | 不可反查即无法解释账单 | `invoice_line.usage_id` 外键 |
| `EOP-G` | 八条用户故事是否都有「可判定」的验收条件 | 出现「体验良好」即不合格 | 改成数字、布尔或错误码 |
| `EOP-H` | 六条不变量是否都有对应 SQL | 只有文字描述即无法验证 | 每条写一条 `count(*)` 查询 |

## 七、下一步

第 1 周第 2 步（第 223 天）：**技术选型与版本基线**。把 Python / SQLite / PostgreSQL / 令牌方案的候选写成「候选 → 判据 → 结论」三段，并实测三个数：本机 Python 启动耗时、SQLite `INSERT OR IGNORE` 的冲突判定耗时、一次 HMAC 签名耗时（已有读数 7.3 µs，见[应用与凭证](../../../../docs/Backend/OpenPlatform/AppCredential/index.md)）。

## 参考资料

- [开放平台与 API 产品化工程](../../../../docs/Backend/OpenPlatform/index.md)
- [配额、限流与用量](../../../../docs/Backend/OpenPlatform/QuotaUsage/index.md)（`quota_policy` 三列的由来）
- [总览：七段链与四条边界](../../../../docs/Backend/OpenPlatform/Overview/index.md)（三处断点与本页八条故事的对应关系）
