# 应用与凭证签名

开放平台的第一道门不是「登录」，而是「证明这串字节确实是你发的」。这一页讲凭证怎么发、签名怎么算、密钥怎么换，以及为什么 90% 的「签名错误」其实不是签名算错了。

本页判据族 `OPC-A` ~ `OPC-H`，共 8 条。定义表在第七节。

## 一、三类凭证，别混着用

| 凭证 | 谁的 | 存哪儿 | 泄漏后的半径 | 能否自助重置 |
| --- | --- | --- | --- | --- |
| `app_id` + `app_secret` | 应用（服务端） | 客户的密钥管理服务 | 该应用的全部接口 | 能（轮换） |
| `access_token` | 一次授权会话 | 内存 / Redis | 该 token 的 scope，最长几小时 | 能（撤销） |
| 用户凭据（code / refresh_token） | 一个自然人 | 客户的应用服务器 | 该用户在该应用下的数据 | 能（用户解除授权） |

**混用的典型症状**：把 `app_secret` 打进前端 bundle。浏览器里的东西都是公开的——`app_secret` 出现在前端，等于该应用的签名能力公开。所以**公共客户端（SPA、移动 App、CLI）不能持有 `app_secret`**，它们必须走 PKCE 授权码（见[授权与令牌](../GrantToken/index.md)）。

## 二、密钥的四个状态

```text
created ──► active ──► rotating ──► revoked
              │            │
              └────────────┴──► expired（到期自动失效，不可恢复）
```

| 状态 | 能验签 | 能签发新令牌 | 典型停留时长 |
| --- | --- | --- | --- |
| `active` | ✅ | ✅ | 长期 |
| `rotating` | ✅ | ❌（新令牌只用新密钥签） | 7~30 天（双活窗口） |
| `revoked` | ❌（立即） | ❌ | 永久 |
| `expired` | ❌ | ❌ | 永久 |

`rotating` 是整套设计的核心：**旧密钥不立刻失效，只是不再用于签发**。这样客户可以「先部署新密钥 → 观察 24 小时无误 → 再删旧的」，而不是「凌晨三点同时改两端」。

::: danger 轮换做错的三次典型事故
1. **一次性替换**：控制台点「重置密钥」后旧密钥立刻失效，客户线上 500，回滚要重新发版。正确做法：生成新密钥后进入 `rotating`，旧密钥保留可验签。
2. **密钥唯一索引建在 `app_id` 上**：导致一个应用只能有一把密钥，双活根本没法做。正确约束：`UNIQUE(app_id, key_id)`，且 `status='active'` 的行可以有 2 条。
3. **轮换不通知**：客户不知道自己在用旧密钥。正确做法：`rotating` 期间每次用旧密钥调用都返回 `Warning: 299 - "credential deprecated, expires 2026-12-01"` 响应头。
:::

## 三、签名串：顺序也是协议

![签名串五段与两端验签](../assets/op-sign.svg)

国内主流开放平台（微信支付 APIv3、支付宝、多家银行的开放网关）用的都是「把若干字段按固定顺序拼接，再对整串做一次 HMAC 或非对称签名」。微信支付的五段就是：

```text
HTTP方法\nURL\n时间戳\n随机串\n请求体\n
```

四个最容易踩的坑，全部来自「两侧对同一段字节的理解不同」：

| 坑 | 一侧的做法 | 另一侧的做法 | 症状 |
| --- | --- | --- | --- |
| URL 编码 | `URLEncoder.encode`（空格→`+`） | `%20` | 只有带空格的参数签名错 |
| query 顺序 | 按加入顺序拼 | 按字典序拼 | 多参数时偶发失败 |
| 请求体 | 用**原始字节**算 SHA-256 | 反序列化再 `json.dumps` | 字段顺序/空格一变就错 |
| 大小写 | `sha256` 输出小写 hex | 大写 hex | 签名长度对、内容全错 |

**唯一可靠的做法**：签名串的构造规则写进文档，并提供一个**能打印中间串**的调试开关——客户自己就能看出是哪一段不一样，而不是把两端代码贴给你猜。

```python
# sign.py（调用方）——注意：body 用原始字节，不做任何反序列化
import hashlib, hmac, time, uuid, sys

def build_string(method: str, path_qs: str, body: bytes, ts: str, nonce: str) -> str:
    body_hash = hashlib.sha256(body).hexdigest()
    return "\n".join([method.upper(), path_qs, ts, nonce, body_hash]) + "\n"

def sign(secret: str, s: str) -> str:
    return hmac.new(secret.encode(), s.encode(), hashlib.sha256).hexdigest()

if __name__ == "__main__":
    body = sys.stdin.buffer.read()
    ts, nonce = str(int(time.time())), uuid.uuid4().hex
    s = build_string("POST", "/v1/orders?dry_run=1", body, ts, nonce)
    print("SIGN_STRING_BEGIN"); print(repr(s)); print("SIGN_STRING_END")
    print(sign("demo_secret", s))
```

## 四、验签五步：顺序错了会白查一天

```python
def verify(headers, method, path_qs, body) -> None:
    app_id = headers["X-App-Id"]
    key = load_key(app_id, headers["X-Key-Id"])       # 1. 查密钥（含 rotating 的旧密钥）
    if key is None or key.status in ("revoked", "expired"):
        raise ApiError(401, "invalid_credential")

    ts = int(headers["X-Timestamp"])
    if abs(time.time() - ts) > 300:                   # 2. 时钟窗口 ±300s
        raise ApiError(401, "timestamp_out_of_window")

    if not nonce_store.claim(app_id, headers["X-Nonce"], ttl=600):   # 3. 防重放
        raise ApiError(409, "duplicate_nonce")

    expect = sign(key.secret, build_string(method, path_qs, body, headers["X-Timestamp"], headers["X-Nonce"]))
    if not hmac.compare_digest(expect, headers["X-Signature"]):       # 4. 常量时间比较
        raise ApiError(401, "invalid_signature")

    check_scope(headers, method, path_qs)             # 5. 通过之后才谈权限
```

两个细节决定了这套代码在生产里能不能用：

- **`hmac.compare_digest` 不是洁癖**。用 `==` 比较字符串会在第一个不同字节处提前返回，攻击者能靠时间差逐字节猜出正确签名（时序侧信道）。
- **nonce 的 TTL 必须 ≥ 时间窗口**。窗口是 ±300s，nonce 只留 60s，那么第 61~300 秒之间的重放会被放行。

## 五、本机读数：签名从来不是瓶颈

在 2 KB / 8 KB / 64 KB 请求体上各跑 20,000 次 HMAC-SHA256（Python 3.13.12，单核，非压测环境）：

| 请求体 | 中位耗时 | p99 |
| --- | --- | --- |
| 2 KB | **7.3 µs** | 28.4 µs |
| 8 KB | 19.8 µs | 61.3 µs |
| 64 KB | 127.1 µs | 329.3 µs |

**读法**：一次签名 7 微秒，而一次 Redis 往返通常 200~500 微秒。所以「加了签名会不会拖慢接口」这个问题的答案是**不会**——真正的成本在验签**之前**的那两次 IO：按 `app_id` 查密钥、nonce 去重。

这也解释了为什么很多平台的性能问题是「上了签名之后 p99 涨了 8 毫秒」：涨的不是 CPU，是**密钥查询没走缓存**，每次请求多了一次数据库往返。

## 六、密钥怎么存

| 位置 | 能不能放 `app_secret` | 说明 |
| --- | --- | --- |
| 源码 / Git | ❌ | 一旦进了历史，删除提交也没用 |
| 环境变量 | ⚠️ | 比源码好，但会出现在 `ps`、崩溃转储、子进程环境里 |
| 密钥管理服务（KMS / Vault） | ✅ | 推荐；应用启动时取一次，内存缓存 + 定期刷新 |
| 数据库明文列 | ❌ | 拖库即全泄漏 |
| 数据库（加密列 + KMS 托管主密钥） | ✅ | 平台侧存客户密钥的常见做法 |
| 哈希后存 | ❌ | 签名需要**原文**，不能只存哈希（这点和密码不同） |

::: tip 一条硬规则
`app_secret` 只在**创建时展示一次**，之后任何接口都只能返回「前 4 位 + 后 4 位」。这条规则同时解决三件事：拖库损失、客服被骗、审计可追溯。
:::

## 七、判据族

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `OPC-A` | 控制台能否同时存在两把可用密钥 | 不能即无法轮换 | 唯一约束改 `UNIQUE(app_id, key_id)` |
| `OPC-B` | 旧密钥在 `rotating` 期间是否仍可验签 | 不可即会造成轮换即宕机 | 验签查询放宽到 `status in ('active','rotating')` |
| `OPC-C` | 签名串是否用原始 body 字节 | 用反序列化后的 JSON 即偶发失败 | 验签在反序列化**之前**完成 |
| `OPC-D` | 时间戳窗口与 nonce TTL 的大小关系 | TTL < 2×窗口即存在重放缝隙 | nonce TTL = 2×窗口 |
| `OPC-E` | 签名比较是否常量时间 | 用 `==` 即有时序侧信道 | 改 `hmac.compare_digest` |
| `OPC-F` | `app_secret` 是否只在创建时可见一次 | 可反复查看即扩大泄漏面 | 存储改为加密列，接口只回掩码 |
| `OPC-G` | 401 是否区分「密钥不存在」与「签名不对」 | 不区分即无法自助排障 | 用 `invalid_credential` / `invalid_signature` 两个子码 |
| `OPC-H` | 是否存在可打印签名串的调试开关 | 无则每次排障都要贴代码 | 加 `X-Debug-Sign: 1`（仅沙箱环境生效） |

## 八、验证方式

```shell
# 1. 正常签名
echo -n '{"sku":"A1","qty":1}' | python3 sign.py
# 期望：打印 SIGN_STRING_BEGIN/END 之间的五段串，以及 64 位小写 hex

# 2. 篡改请求体后再签，观察服务端拒绝
echo -n '{"sku":"A1","qty":2}' | python3 sign.py | tail -1
# 期望：服务端返回 401 invalid_signature，且 usage 表不新增行
```

**结果读法**：如果两次签名得到的 hex **完全相同**，说明 body 根本没进签名串——这是最危险的一种「看起来能用」的实现。

## 参考资料

- 微信支付 · APIv3 签名生成与验签：https://pay.weixin.qq.com/doc/v3/merchant/4012365334
- Python `hmac` 文档（`compare_digest`）：https://docs.python.org/3/library/hmac.html
- RFC 2104 · HMAC: Keyed-Hashing for Message Authentication：https://www.rfc-editor.org/rfc/rfc2104
- OWASP · Authentication Cheat Sheet：https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
