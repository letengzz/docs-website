# 第 2 周第 3 步：`/oauth/token` 与 `/v1/ping`

前两步各自把一段路修好了：第 228 天定下「一次调用只被计一次」（`EOM`），第 229 天定下「还允不允许」（`EOU`）。但这两段一直是分开测的——计量用例直接构造 `app_id`，配额用例直接塞 `used`。今天要把它们串成一条真实链路：**一条令牌从签发到用完，验签、配额、计量、响应四个环节必须看到同一个身份**。

::: tip 一句话理解
**令牌不是「一串随机字符」，而是「一份被签了名的授权范围」**。它必须能回答三件事：这是哪个应用（`app_id`）、它能做什么（`scope`）、它什么时候失效（`exp`）。三件事缺一件，后面的配额与计量就无从挂账。
:::

本页判据族 `EOV-A` ~ `EOV-H`，共 8 条，定义在第七节。

## 一、这一步解决的问题

第 228 天的计量中间件要求「一次调用只被计一次」，第 229 天的配额判定要求「放行数 = 扣减数」。两条都建立在同一个前提上：**每个请求身上带着一个可解析、可验证、可信的身份**。

如果身份来自请求头里客户自己填的 `X-App-Id`，那么：

- 计量可以把 A 应用的调用记到 B 应用头上（伪造头即可）；
- 配额可以被绕过（每次换一个 `X-App-Id`，配额永远是新的）；
- 账单无法对账（谁调的说不清）。

所以这一步的产物不是「两个接口」，而是**一条身份链**：`client_id/client_secret` → `access_token` → `request_context`。前两步的中间件今天第一次拿到**真实令牌解析出来的** `app_id`，而不是参数里传进来的。

## 二、七段令牌链

| 段 | 做什么 | 产物 | 失败方式 | 是否安静 |
| --- | --- | --- | --- | --- |
| ① 识别应用 | `client_id` 查应用表 | `app` 行 | `401 auth.client_unknown` | 显性 |
| ② 校验密钥 | `secret` 的哈希与库中比对（常数时间） | 通过 / 拒绝 | `401 auth.client_invalid` | 显性 |
| ③ 求交范围 | 请求 `scope` ∩ 应用可授 `scope` | 有效 scope 集 | `403 scope.insufficient` | **安静**（交集为空时容易返 200 空令牌） |
| ④ 签发令牌 | 生成随机串，只把哈希落库 | `access_token`（明文只出现一次） | —— | —— |
| ⑤ 落库 | `(token_hash, app_id, scope, exp)` | `oauth_token` 行 | 写失败仍返回令牌 → **吊销失效** | **安静** |
| ⑥ 返回 | `access_token` + `expires_in` + `scope` | JSON | 少 `scope` 字段 → 客户端猜权限 | 安静 |
| ⑦ 后续验签 | 每个请求解析令牌 → `request_context` | 上下文 | 缓存不失效 → 吊销延迟 | **安静**（最常见） |

七段里三段是安静的，且都指向同一个后果：**授权边界与账务边界对不上**。

## 三、三个必须先定死的设计决定

### 决定一：不透明令牌 + 服务端哈希，不用 JWT

| 方案 | 吊销生效 | 降权生效 | 每请求成本 | 适用 |
| --- | --- | --- | --- | --- |
| JWT（自包含） | 要等过期，或维护黑名单 | 要等过期 | 验签（本地，快） | 高频、可容忍延迟吊销 |
| 不透明令牌（查库/查缓存） | **立即** | **立即** | 一次缓存查询 | 需要即时吊销的开放平台 |

选不透明令牌的理由只有一条：**开放平台的客户会要求「立刻停掉这个应用的访问」**。JWT 要做这件事必须维护黑名单，而黑名单本质上就是「查库」，等于放弃了 JWT 的唯一优势。既然迟早要查，不如一开始就查。

### 决定二：明文只出现一次，库里只存 `sha256`

```sql
CREATE TABLE oauth_token (
  token_hash   TEXT PRIMARY KEY,          -- sha256(明文)，不存明文
  app_id       TEXT NOT NULL,
  scope        TEXT NOT NULL,             -- 空格分隔，已求交后的有效范围
  issued_at    TEXT NOT NULL,
  expires_at   TEXT NOT NULL,
  revoked_at   TEXT,
  last_used_at TEXT
);
CREATE INDEX idx_oauth_token_app ON oauth_token (app_id, expires_at);
```

三条理由：① 库被读走时明文令牌不能直接被用；② 令牌是「凭据」不是「数据」，没有反查需求（反查靠 `app_id` 索引）；③ 哈希后才能用主键做等值查询，比在明文列上建索引更快也更安全。

::: danger 令牌存储的三个致命写法
1. **存明文**：一次备份泄露 = 所有客户的应用被接管，而且**无法区分「谁用的」**（大家都用同一个明文）。
2. **用可逆加密**：看起来安全，实际把风险从「库泄露」转移到了「密钥泄露」，而密钥通常就在同一台机器的环境变量里。
3. **用 `md5` 或加盐 bcrypt 存令牌**：`md5` 已被碰撞攻击；bcrypt 是**故意慢**的（防爆破口令），令牌每次请求都要校验，用它会让 P99 直接翻倍。令牌是**高熵随机串**，不需要慢哈希，`sha256` 足够。
:::

### 决定三：`scope` 求交，交集为空就拒绝

```python
def effective_scope(requested: set[str], granted: set[str]) -> set[str]:
    eff = requested & granted
    if not eff:
        # 交集为空必须报错，不能返回一个「空权限但可用」的令牌
        raise ApiError(403, "scope.insufficient",
                       details={"requested": sorted(requested), "granted": sorted(granted)})
    return eff
```

这条判断看起来多余（空集也是合法集合），但它防的是一类真实事故：**客户端拿到一个能通过验签、但每个接口都 403 的令牌**，然后花两天排查签名。交集为空时应当**在签发环节就失败**，让错误出现在「拿令牌」这一步。

## 四、`/oauth/token` 契约

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=app_7f3c
&client_secret=sk_live_...
&scope=inventory.read%20inventory.write
```

成功响应（`200`）：

```json
{
  "access_token": "at_9f2c1e7ab3d54c10b8a4",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "inventory.read inventory.write",
  "app_id": "app_7f3c"
}
```

| 字段 | 为什么必须有 | 缺了会怎样 |
| --- | --- | --- |
| `access_token` | 凭据本体 | —— |
| `token_type` | 客户端拼接 `Authorization` 头时要用 | 客户端硬编码 `Bearer`，将来换方案就全改 |
| `expires_in` | 秒数，不是绝对时间 | 客户端按本机时间算绝对时间，时钟偏了就提前/延后失效 |
| `scope` | **服务端求交后的结果** | 客户端按请求的 scope 猜权限，猜错就 403 |
| `app_id` | 便于客户自查「这条令牌是哪个应用的」 | 多应用客户无法区分 |

::: warning `expires_in` 不要给绝对值
给 `expires_at: "2026-11-01T16:00:00Z"` 看似更明确，但客户的服务器时钟可能与平台差几分钟，导致「刚拿到就过期」或「过期后还能用」。**相对秒数 + 客户端按收到响应的时刻起算**是唯一不会因时钟偏差出错的形态。
:::

## 五、`/v1/ping`：一条只验身份的业务无关接口

`ping` 的语义必须写死，否则它会慢慢变成一个「什么都能查」的后门：

| 它做 | 它不做 |
| --- | --- |
| 校验 `Authorization` 头的令牌有效性 | 不查任何业务数据（库存、订单、账单） |
| 返回 `app_id` 与令牌剩余有效期 | 不返回客户名称、余额、配额用量 |
| 返回 `X-Request-Id` 供报障对齐 | 不写 `usage` 表、不扣配额 |
| 走与业务接口**完全相同**的中间件链 | 不做特殊旁路（旁路 = 下一处漏计量的入口） |

```json
{
  "pong": true,
  "app_id": "app_7f3c",
  "scope": "inventory.read inventory.wirte",
  "expires_in": 3487,
  "request_id": "req_9f2c1e7ab3d54c10"
}
```

上面这个 `scope` 里有一个拼写错误（`wirte`），那是刻意留的反例：**`ping` 回显的 `scope` 必须与令牌落库的值逐字一致**，不要在这里做「修正」「排序」「去重」——一旦回显与鉴权用的不是同一个来源，客户会按回显去调接口，然后收到 403。

::: danger `ping` 的三个误用
1. **让 `ping` 扣配额**：客户会用 `ping` 做健康检查（每分钟几十次），扣配额等于把额度浪费在探活上。**`ping` 必须显式豁免计量**，且这个豁免要写进契约。
2. **让 `ping` 变成「查余额」**：一旦返回用量，它就承担了业务语义，后续改动会牵动计费逻辑。
3. **给 `ping` 开验签旁路**（为了「探活更快」）：旁路一旦存在，就会有人把它复制到别的接口上，而**漏掉验签的接口不会报错**，只会让伪造请求成功。
:::

## 六、端到端：一条令牌走完四段

```text
① 客户 POST /oauth/token（client_id + secret + scope）
   → 校验 secret 哈希 → 求交 scope → 生成 at_xxx → 存 sha256 → 返回 200

② 客户 GET /v1/ping  Authorization: Bearer at_xxx
   → 取 sha256(at_xxx) 查缓存/库 → 命中且未过期未吊销 → 构造 request_context
   → 返回 200（不写 usage，不扣配额）

③ 客户 GET /v1/inventory（第 4 步才实现）
   → 同一中间件链 → 配额判定 → 计量写入（billed=1）→ 业务处理

④ 平台侧吊销：UPDATE oauth_token SET revoked_at = now WHERE app_id = 'app_7f3c'
   → 缓存 TTL 内最迟 60 秒生效 → 之后 ping 返回 401 auth.token_revoked
```

第 ④ 段是「不透明令牌」的价值所在，也是**唯一需要专门设计**的地方：缓存必须有 TTL 上限（建议 60 秒），且吊销操作要能主动失效缓存（发布一条失效消息），不能只等 TTL 过期。

## 七、判据族

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `EOV-A` | 库里只有 `token_hash`，任何表都查不到明文令牌 | `SELECT` 全表，无 `at_` 前缀字段值 |
| `EOV-B` | `scope` 为「请求 ∩ 可授」的交集，交集为空时签发失败 | 请求越权 scope，返回 `403 scope.insufficient` |
| `EOV-C` | 响应含 `token_type` / `expires_in` / `scope` / `app_id` 四字段 | `jq` 断言四键齐全 |
| `EOV-D` | 后续请求的 `app_id` 来自令牌解析，不读请求头里的 `X-App-Id` | 伪造 `X-App-Id` 后计量仍记到令牌所属应用 |
| `EOV-E` | `ping` 不写 `usage`、不扣配额 | 调 10 次 ping，`usage` 行数不变、`used` 不变 |
| `EOV-F` | `ping` 与业务接口共用同一中间件链（无旁路） | 用失效令牌调 ping，返回 `401` |
| `EOV-G` | 吊销后 60 秒内失效 | 吊销后轮询，≤60 s 出现 `401 auth.token_revoked` |
| `EOV-H` | 错误体仍是四字段形状（`code`/`message`/`request_id`/`details`） | 任一失败响应 `jq` 断言 |

## 八、验证方式

前置：起本地服务（第 2 周的最小可跑集，`sqlite3 + FastAPI`）。

```shell
# 1) 签发：应返回 200，且四字段齐全
curl -s -X POST http://127.0.0.1:8000/oauth/token \
  -d 'grant_type=client_credentials' \
  -d 'client_id=app_7f3c' -d 'client_secret=sk_test_123' \
  -d 'scope=inventory.read' | jq -e 'has("access_token") and has("token_type") and has("expires_in") and has("scope") and has("app_id")'
# 期望：true

# 2) 交集为空必须失败：应返回 403 且 code 以 scope. 开头
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:8000/oauth/token \
  -d 'grant_type=client_credentials' -d 'client_id=app_7f3c' -d 'client_secret=sk_test_123' \
  -d 'scope=billing.admin'
# 期望：403

# 3) 库里没有明文：应输出 0
sqlite3 /tmp/oph.db "SELECT count(*) FROM oauth_token WHERE token_hash LIKE 'at_%';"
# 期望：0

# 4) ping 不计量：调 10 次前后 usage 行数相同、配额 used 不变
before=$(sqlite3 /tmp/oph.db "SELECT count(*) FROM usage;")
for i in $(seq 1 10); do
  curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/v1/ping > /dev/null
done
after=$(sqlite3 /tmp/oph.db "SELECT count(*) FROM usage;")
echo "$before $after"
# 期望：两个数相同

# 5) 吊销后失效：应返回 401
sqlite3 /tmp/oph.db "UPDATE oauth_token SET revoked_at = datetime('now') WHERE app_id='app_7f3c';"
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/v1/ping
# 期望：401（60 秒内）

# 6) 伪造 X-App-Id 无效：计量仍记到令牌所属应用
curl -s -H "Authorization: Bearer $TOKEN" -H "X-App-Id: app_other" http://127.0.0.1:8000/v1/ping > /dev/null
sqlite3 /tmp/oph.db "SELECT DISTINCT app_id FROM usage ORDER BY app_id;"
# 期望：只有 app_7f3c，不出现 app_other
```

六条里 1、3、4 是正向，2、5、6 是反向。**第 6 条是这一步最重要的一条**：它证明身份只有一条来源。

## 九、当日做了什么 / 如何验证 / 下一步

**做了什么**：把「身份」从参数变成令牌。新增 `oauth_token` 表（第 14 张表），确定三件事：不透明令牌 + `sha256` 存储、`scope` 求交后再签发、`ping` 显式豁免计量但**不豁免验签**。中间件链第一次拿到真实令牌解析出的 `app_id`，计量与配额的表结构一行没改——这正好验证了前两步的接口设计是对的。

**如何验证**：见第八节六条命令。核心是第 4 条（ping 不计量）与第 6 条（伪造头无效），前者守住额度不被探活吃掉，后者守住身份的唯一来源。

**下一步**：第 2 周第 4 步「`/v1/inventory` 与 `/webhooks/replay`」——第一个真实业务接口（走完整配额 + 计量），以及第一个**写接口**的幂等重放（复用 `idempotency` 表，判据族占位 `EOY`）。到这一步，四条链（验签 → 配额 → 计量 → 幂等）才算全部接通。

## 参考资料

- [计量中间件的唯一写入点](../Metering/index.md)：`usage` 的唯一写入者，今天第一次拿到真实 `app_id`
- [配额与限流的判定点](../QuotaLimit/index.md)：`429` 与 `billed=0` 的口径来源
- [接口契约与错误码](../Contracts/index.md)：错误体四字段与 `auth.` / `scope.` 前缀
- [数据库设计：十二张表与四条重复防线](../DatabaseDesign/index.md)：`oauth_token` 是第 14 张表
- [开放平台与 API 产品化工程](../../../../docs/Backend/OpenPlatform/Overview/index.md)：文档底座的对应章节
