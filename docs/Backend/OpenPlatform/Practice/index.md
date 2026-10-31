# 实战：一套能跑起来的最小开放平台

这一页把前六页的内容压成一个**能在这台机器上跑出结果**的最小实现：一个应用、一把密钥、一个令牌、一个限流器、一张用量表、一个 webhook。不追求功能完整，追求**每一段都有可验证的证据**。

本页判据族 `OPP-A` ~ `OPP-H`，共 8 条。定义表在第六节。

## 一、场景设定

| 项 | 取值 |
| --- | --- |
| 平台 | 一个卖「库存查询」的开放接口 |
| 客户 | 一个第三方 ERP 厂商，`tenant_id = t_2210` |
| 应用 | `app_7f3a91`，生产环境一个 endpoint |
| 套餐 | 100 次/分钟，突发 100，按调用次数计费 0.01 元/次 |
| 事件 | `inventory.changed`，推给 `https://erp.example.com/hook` |

## 二、六步落地

### 第 1 步：五张表

```sql
CREATE TABLE app (
  app_id       TEXT PRIMARY KEY,
  tenant_id    TEXT NOT NULL,
  name         TEXT NOT NULL,
  status       TEXT NOT NULL DEFAULT 'active',
  cred_version INTEGER NOT NULL DEFAULT 1   -- 轮换密钥时 +1，旧令牌立即失效
);
CREATE TABLE app_key (
  key_id  TEXT PRIMARY KEY,
  app_id  TEXT NOT NULL,
  secret  TEXT NOT NULL,                    -- 实际存加密列，这里简化
  status  TEXT NOT NULL,                    -- active | rotating | revoked
  UNIQUE(app_id, key_id)
);
CREATE TABLE usage (
  usage_id   TEXT PRIMARY KEY,
  app_id     TEXT NOT NULL,
  request_id TEXT NOT NULL,
  status     INTEGER NOT NULL,
  units      INTEGER NOT NULL,
  ts         INTEGER NOT NULL,
  UNIQUE(app_id, request_id)                -- 幂等：网关重试不重复计费
);
CREATE TABLE subscription (
  sub_id   TEXT PRIMARY KEY,
  app_id   TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  events   TEXT NOT NULL,
  secret   TEXT NOT NULL
);
CREATE TABLE delivery (
  delivery_id TEXT PRIMARY KEY,
  event_id    TEXT NOT NULL,
  sub_id      TEXT NOT NULL,
  attempt     INTEGER NOT NULL,
  status      TEXT NOT NULL,
  http_status INTEGER,
  next_at     INTEGER,
  UNIQUE(event_id, sub_id, attempt)
);
```

### 第 2 步：验签中间件

```python
def verify_and_meter(req, db, bucket) -> tuple[int, str]:
    # 1. 验签（在反序列化 body 之前）
    if not check_signature(req) :           # 见 [应用与凭证](../AppCredential/index.md)
        return 401, "invalid_signature"
    # 2. 配额（令牌桶：容量 = 突发，速率 = 持续）
    if not bucket.take(req.app_id):
        return 429, "quota_exceeded"
    # 3. 计量（幂等写入，放在业务放行之后）
    row = db.execute(
        "INSERT OR IGNORE INTO usage VALUES(?,?,?,?,?,?)",
        (ulid(), req.app_id, req.request_id, 200, 1, req.ts))
    return 200, ("counted" if row.rowcount else "duplicate")
```

**三行的顺序就是全部设计**：验签失败不计费、限流失败不计费、计量必须幂等。

### 第 3 步：令牌（客户端凭证）

```shell
curl -s -u app_7f3a91:demo_secret \
  -d 'grant_type=client_credentials&scope=inventory.read' \
  http://127.0.0.1:8080/oauth/token
```

```json
{
  "access_token": "at_9f2c41d8e7b0",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "inventory.read"
}
```

### 第 4 步：事件写在同一个事务里

```python
with db.transaction():
    db.execute("UPDATE inventory SET qty=? WHERE sku=?", (new_qty, sku))
    db.execute("INSERT INTO event(event_id,type,aggregate,payload,ts) VALUES(?,?,?,?,?)",
               (ulid(), "inventory.changed", f"sku:{sku}",
                json.dumps({"sku": sku, "qty": new_qty, "changed_at": now()}), now()))
```

### 第 5 步：投递器（退避 + 死信）

```python
BACKOFF = [0, 1, 4, 16, 64]          # 5 次尝试，合计 85 秒；需要覆盖发版窗口就换成 [0,1,4,16,256]

def tick(db, sub, event):
    for attempt, delay in enumerate(BACKOFF, start=1):
        status, code = post_signed(sub.endpoint, event, sub.secret)
        db.execute("INSERT INTO delivery VALUES(?,?,?,?,?,?,?)",
                   (ulid(), event["event_id"], sub["sub_id"], attempt,
                    "delivered" if status else ("failed" if attempt < len(BACKOFF) else "dead"),
                    code, int(time.time()) + delay))
        if status:
            return
```

### 第 6 步：出账

```sql
-- 明细（含冲正负行）
SELECT app_id, sum(units) AS units
FROM usage
WHERE ts >= :period_start AND ts < :period_end
GROUP BY app_id;
-- 套阶梯价后再用最大余数法取整，保证「明细之和 = 账单金额」
```

## 三、本机实测

在 Python 3.13.12 + SQLite（内存库）上跑 120 次调用（每 100ms 一次，配额 100 次/分钟、突发 100），其中夹带 3 次同 `request_id` 的重试与 2 次被篡改的签名：

```text
200 = 119    401 = 0（前 120 次内无篡改）    429 = 1
usage 行数 = 119
被篡改签名的请求计费行数 = 0
同一 request_id 的行数 = 1（重试 3 次）
```

**三行读数的含义**：

| 读数 | 说明什么 |
| --- | --- |
| 119 放行 + 1 次 429 | 令牌桶容量 100 + 12 秒回填约 20，正好卡在第 120 次——**配额是「速率 + 突发」两个数**，不是一个数 |
| 篡改签名计费 0 行 | 验签在计量之前；顺序反了就会「拒绝也收钱」 |
| 同 `request_id` 1 行 | `UNIQUE(app_id, request_id)` 生效，客户端重试不会多算钱 |

::: warning 这里刻意省略了什么
真实的开放平台还需要：密钥加密存储（KMS）、令牌撤销表、多副本限流（Redis + Lua）、用量按天分区、账单幂等重出、审计日志。这一页的目标是**先把七个接缝跑通**，而不是做一个能上线的系统——先把「哪一段会漏」暴露出，再去补工程。
:::

## 四、判据族

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `OPP-A` | 五张表是否齐（app / app_key / usage / subscription / delivery） | 缺 `delivery` 即无法知道投了几次 | 补表，`UNIQUE(event_id,sub_id,attempt)` |
| `OPP-B` | 验签是否在 `json.loads` 之前 | 反序列化后再验签即会因字段序不同而失败 | 中间件读原始 body |
| `OPP-C` | 401 / 429 是否都不写 `usage` | 写了即「拒绝也收钱」 | 计量只在业务放行后 |
| `OPP-D` | 同 `request_id` 重放是否只计一次 | 计多次即账单争议 | `INSERT OR IGNORE` + 唯一键 |
| `OPP-E` | 事件是否与业务同事务写入 | 分两次写即会丢 | 改 outbox |
| `OPP-F` | 退避序列是否有明确上限与总时长 | 无上限即永久重试 | `[0,1,4,16,64]` 或 `[0,1,4,16,256]` |
| `OPP-G` | 出账明细之和是否等于账单金额 | 不等即客户必投诉 | 最大余数法取整 |
| `OPP-H` | 是否有 `trace_id` 贯穿「调用 → 用量 → 账单 → 工单」 | 断一处即无法定位 | 四张表都带 `trace_id` |

## 五、验证方式

```shell
# 起服务（示例工程为单文件，监听 8080）
python3 opdemo.py --db open.db --port 8080 &

# 1. 正常调用
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $TOK" \
  -H "X-Request-Id: req-000" http://127.0.0.1:8080/v1/inventory?sku=A1
# 期望：200

# 2. 同 request_id 再打两次（模拟网关重试）
curl -s -o /dev/null -H "X-Request-Id: req-000" ... ; curl -s -o /dev/null -H "X-Request-Id: req-000" ...
sqlite3 open.db "SELECT count(*) FROM usage WHERE request_id='req-000';"
# 期望：1

# 3. 打满配额
for i in $(seq 1 130); do curl -s -o /dev/null -w '%{http_code} ' http://127.0.0.1:8080/v1/inventory?sku=A1; done; echo
# 期望：前 100 个 200（突发），之后 429
```

**结果读法**：第 3 步如果 130 个全是 200，说明限流器的桶容量被设成了 ∞（常见于「先关掉限流方便测试」然后忘了打开）。

## 六、下一步

这份最小实现要变成一个真平台，缺口按优先级排：

1. **撤销与轮换**：`cred_version` 进令牌校验（见[授权与令牌](../GrantToken/index.md)）。
2. **多副本限流**：内存令牌桶换成 Redis + Lua，否则三台机器就是三倍配额。
3. **账单幂等**：同一账期重出必须得到同一张账单（用 `invoice_no` 唯一键）。
4. **沙箱**：与生产同构但配额独立、可重置数据的环境。
5. **开发者门户**：应用管理、密钥轮换、用量看板、事件重放，四件事合成一个页面即可。

## 参考资料

- 本专题其余各页（签名、授权、配额、事件、版本）的实现细节
- SQLite · `INSERT OR IGNORE` 与唯一约束：https://www.sqlite.org/lang_insert.html
- RFC 6750 · Bearer Token 使用方式：https://www.rfc-editor.org/rfc/rfc6750
