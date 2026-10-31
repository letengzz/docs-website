# 授权与令牌

授权回答的是「这个应用此刻能不能代表这个人做这件事」。它有三个相互独立的问题：**用什么模式拿令牌**、**令牌里装什么**、**令牌怎么作废**。三个问题里最容易做错的是第三个。

本页判据族 `OPA-A` ~ `OPA-H`，共 8 条。定义表在第七节。

## 一、四种模式：先问「有没有人」

![四种授权模式的选择路径](../assets/op-grant.svg)

| 模式 | 有用户吗 | 有可信后端吗 | 典型场景 | 现状 |
| --- | --- | --- | --- | --- |
| 授权码 + PKCE | ✅ | ✅ / ❌ 都可以 | 第三方系统代用户操作 | **默认选它** |
| 客户端凭证 | ❌ | ✅ | 服务端到服务端的数据同步 | 常用 |
| 设备码 | ✅ | ❌ | 电视、CLI、打印机 | 常用 |
| 隐式 | ✅ | ❌ | 老 SPA | **已废弃**，OAuth 2.1 移除 |
| 密码模式 | ✅ | ✅ | 老的自建 App | **已废弃**，OAuth 2.1 移除 |

::: warning 「有没有后端」不等于「是不是 SPA」
判断标准是**能不能安全保存一个长期秘密**。Electron 桌面端有「后端」（主进程），但它装在用户机器上，秘密随时可被读走——所以它属于**公共客户端**，必须走 PKCE。
:::

### 授权码 + PKCE 的六步

```text
① 客户端生成 code_verifier（43~128 字符随机），算出 code_challenge = BASE64URL(SHA256(verifier))
② 浏览器跳转 /authorize?response_type=code&client_id=...&code_challenge=...&code_challenge_method=S256&state=...
③ 用户在平台登录并同意 scope，平台回跳 redirect_uri?code=...&state=...
④ 客户端校验 state（防 CSRF），再 POST /token 带 code + code_verifier
⑤ 平台用存下的 challenge 校验 verifier：SHA256(verifier) 是否等于 challenge
⑥ 通过则发 access_token（+ refresh_token）
```

`state` 和 `code_challenge` 各自防一种攻击：`state` 防「攻击者把自己的 code 塞给受害者」，PKCE 防「code 在传输中被截获后直接被兑换」。**只做 state 不做 PKCE**，在有恶意 App 注册了同一 `redirect_uri` scheme 的移动端上，等于没防。

### 客户端凭证的三条纪律

```http
POST /oauth/token HTTP/1.1
Host: open.example.com
Authorization: Basic YXBwXzdmM2E5MTpzM2NyZXQ=
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&scope=order.read%20report.export
```

1. **不能用 `app_secret` 直接当 `access_token`**——那等于没有令牌生命周期，撤销就变成改密钥。
2. **scope 必须在请求里显式声明**，不能默认给全量。默认全量的直接后果是「客户多要了一个权限，你半年后才发现」。
3. **令牌 TTL ≤ 1 小时**，且不支持 refresh：机器对机器不需要「续期」，直接再要一个。

## 二、scope 怎么设计

三条原则，按重要性排序：

| 原则 | 做法 | 反例 |
| --- | --- | --- |
| **粗到能数清** | 一个资源一个动词：`order.read` / `order.write` | `order.read.by_sku.include_deleted` |
| **语义稳定** | 名字里**不带版本号** | `report.v2.export`（v3 来了要不要保留？） |
| **可审计** | 每个 scope 对应一句人话解释，写进文档 | `all`（客户看不懂，审计也看不懂） |

推荐的 12 个 scope 骨架：

| 资源 | 读 | 写 | 管理 |
| --- | --- | --- | --- |
| 订单 | `order.read` | `order.write` | `order.admin`（改状态、强制关单） |
| 库存 | `inventory.read` | `inventory.write` | — |
| 商品 | `product.read` | `product.write` | `product.publish` |
| 报表 | `report.export` | — | — |
| 事件 | — | `webhook.manage`（建/删订阅） | — |

**管理类 scope 单独拆出来**，是因为它的风险等级完全不同：`order.write` 错一次是一单，`order.admin` 错一次是一片。审计时按 scope 前缀统计调用量，能一眼看出谁在用高危权限。

## 三、令牌里装什么：JWT 还是不透明令牌

| 维度 | JWT（自包含） | 不透明令牌（随机串 + 查库/查缓存） |
| --- | --- | --- |
| 校验成本 | 本地验签（微秒级） | 一次 Redis 往返（亚毫秒） |
| 撤销 | ❌ 只能等过期，或维护黑名单 | ✅ 删 key 即失效 |
| 体积 | 大（含 claims） | 小（32 字节） |
| 跨服务 | 天然可传播 | 每个服务都要能查 |
| 适合 | 短 TTL、只读、内部服务间 | 对外开放、需要即时撤销 |

本机实测（Python，5 个 scope + 租户 + 过期时间，base64url 编码）：

```text
JWT（5 scope）          398 字节
不透明令牌（32B 随机）   约 40 字节
差                      358 字节/请求
按 100 万请求/天计      341.4 MiB/天的额外下行
```

**结论**：开放平台**默认用不透明令牌**。原因不是体积，而是撤销——客户密钥泄漏时你必须能「立刻」让它失效，而 JWT 的「立刻」指的是「最多一小时后」。

如果确实要用 JWT（比如网关要本地校验以省掉一次往返），退一步的做法是：**TTL 压到 5~15 分钟 + 用 `jti` 维护一个短黑名单**。黑名单的条目数 ≈ 每分钟签发量 × TTL，规模可控。

## 四、撤销：三种「失效」不是一回事

::: danger 三种失效的语义必须写清
1. **撤销单个令牌**（RFC 7009 `POST /oauth/revoke`）：只让这一个 `access_token` / `refresh_token` 失效。
2. **用户解除授权**：让该用户在该应用下的**所有**令牌失效，并删除 refresh_token。
3. **轮换/吊销密钥**：让该应用**新签发**的令牌停止签发；已签发的是否立即失效，取决于你有没有做「令牌版本号」。
:::

第 3 种是最容易被忽略的：客户说「密钥泄漏了」，你轮换了密钥，但攻击者手上那个**已经签发的 access_token 还能用一小时**。所以令牌里要带一个 `cred_version`，验签时与 `app.cred_version` 比对——轮换时把 `cred_version` 加一，所有旧令牌瞬间失效。

```sql
-- 令牌表：不透明令牌的落地形态
CREATE TABLE oauth_token (
  token_hash   TEXT PRIMARY KEY,          -- SHA-256(token)，明文不落库
  app_id       TEXT NOT NULL,
  tenant_id    TEXT NOT NULL,
  subject      TEXT,                      -- 用户 ID；client_credentials 为 NULL
  scopes       TEXT NOT NULL,             -- 空格分隔
  cred_version INTEGER NOT NULL,          -- 签发时的密钥版本
  issued_at    INTEGER NOT NULL,
  expires_at   INTEGER NOT NULL,
  revoked_at   INTEGER
);
CREATE INDEX idx_token_app ON oauth_token(app_id, expires_at);
```

`token_hash` 而不是明文，是因为「拖库」是这类系统最常见的失陷方式：拖走哈希表也换不出可用令牌。

## 五、判据族

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `OPA-A` | 公共客户端是否强制 PKCE | 未强制即存在 code 截获风险 | `/authorize` 对无 secret 的 client 拒绝 `plain` |
| `OPA-B` | `client_credentials` 是否必须显式声明 scope | 默认全量即越权 | `/token` 缺 `scope` 时拒绝 |
| `OPA-C` | 令牌 TTL 是否 ≤ 1 小时 | 超过即撤销窗口过宽 | 降 TTL，用 refresh 续期 |
| `OPA-D` | 是否存在 `cred_version` 与令牌的比对 | 无则轮换密钥后旧令牌仍可用 | 令牌表加列 + 验签时比对 |
| `OPA-E` | 令牌明文是否落库 | 落库即拖库可用 | 只存 `token_hash` |
| `OPA-F` | 撤销接口是否幂等（撤两次返回 200） | 非幂等会导致客户端重试报错 | RFC 7009 要求总是 200 |
| `OPA-G` | scope 名字里是否含版本号 | 含版本号即每年要拆一次 | 重命名 + 别名过渡 |
| `OPA-H` | 401 与 403 是否分清（令牌无效 / scope 不足） | 混用即无法自助排障 | 401 带 `WWW-Authenticate`，403 带 `error="insufficient_scope"` |

## 六、验证方式

```shell
# 1. 走一遍 client_credentials
curl -s -u app_7f3a91:demo_secret -d 'grant_type=client_credentials&scope=order.read' \
  http://127.0.0.1:8080/oauth/token | tee /tmp/tok.json
# 期望：{"access_token":"...","token_type":"Bearer","expires_in":3600,"scope":"order.read"}

# 2. 用这个令牌调一个超出 scope 的接口
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $(python3 -c 'import json;print(json.load(open("/tmp/tok.json"))["access_token"])')" \
  -X POST http://127.0.0.1:8080/v1/orders -d '{}'
# 期望：403（不是 401，也不是 500）

# 3. 撤销后立刻重试
curl -s -o /dev/null -w '%{http_code}\n' -d 'token=...' http://127.0.0.1:8080/oauth/revoke   # 期望 200
# 再调第 2 步的接口：期望 401
```

**结果读法**：第 3 步如果是 200 而不是 401，说明校验走的是本地 JWT 缓存或进程内缓存，没有落到撤销检查上。

## 参考资料

- RFC 6749 · 授权码与客户端凭证：https://www.rfc-editor.org/rfc/rfc6749#section-4
- RFC 7636 · PKCE：https://www.rfc-editor.org/rfc/rfc7636
- RFC 7009 · Token Revocation：https://www.rfc-editor.org/rfc/rfc7009
- RFC 7662 · Token Introspection：https://www.rfc-editor.org/rfc/rfc7662
- RFC 8628 · Device Authorization Grant：https://www.rfc-editor.org/rfc/rfc8628
- draft-ietf-oauth-v2-1 · OAuth 2.1：https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/
