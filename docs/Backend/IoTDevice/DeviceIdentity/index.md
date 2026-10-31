# 设备身份与凭证

一台设备要能被信任，得先回答一个问题：**这根网线另一头到底是谁**。服务端有 IP、有 MAC、有 `client_id`，这三样都能被改。真正能当身份的只有一件东西：**出厂时写进去、别人拿不走的那份凭证**。

::: tip 一句话定位
设备身份的目标不是「防黑客」，而是**让「同一份凭证被两台设备使用」这件事一定暴露**。做到这一点，克隆设备就从「无声的资损」变成「一条能报警的记录」。
:::

## 一、三种凭证形态

| 形态 | 设备侧携带 | 平台侧校验 | 成本 | 适用 |
| --- | --- | --- | --- | --- |
| **一型一密** | 产品级密钥（所有同型号共用） | `product_key` + `secret` | 最低 | 原型、内测；**量产禁用** |
| **一机一密** | `product_key` / `device_name` / `device_secret` | 按 `device_name` 查密钥后比对 | 低（要管理 N 份密钥） | 绝大多数消费级设备 |
| **一机一证**（mTLS） | X.509 客户端证书 + 私钥 | 校验证书链 + 提取 CN/SAN 作身份 | 高（要 PKI） | 工业、支付、门禁 |

一型一密的问题不在密码学，而在**运维**：一份密钥泄露，等于整批设备全部可被冒充，而平台**无法区分**哪台是真的。它唯一合理的用法是「出厂前烧录一机一密之前」的过渡期，且必须配一条「该产品下设备数超过 N 即拒绝一型一密接入」的闸门。

## 二、三元组与派生

一机一密的凭证关系：

```text
product_key   Pk9m2fA1        # 产品维度，公开，可出现在日志里
device_name   SN2026103100071 # 设备维度，公开，是业务主键
device_secret s3cr3t...       # 设备维度，机密，只在产线与设备内存在
```

平台侧**不存明文** `device_secret`，只存 `HMAC-SHA256(pepper, secret)`。理由是「库被读走」比「单台设备被拆」概率高得多。

MQTT 接入时，两种做法都能落地：

| 做法 | 连接参数 | 优点 | 缺点 |
| --- | --- | --- | --- |
| 密钥直传 | `username=device_name`，`password=secret` | 简单，模组都支持 | 密码明文在 TLS 之内，但会进 Broker 日志 |
| 挑战应答 | `username=device_name`，`password=HMAC(secret, ts+nonce)` | 密码一次一用，日志泄露无害 | 需要时钟；`ts` 漂移超窗即失败 |

挑战应答的实现要点：`ts` 允许 **±300 s**（设备时钟不可信，见[遥测接入](../TelemetryIngest/index.md)），`nonce` 由 Broker 侧插件从 `$CONTROL` 或 REST 接口按 `device_name` 下发并**单次有效**，窗口内重放直接拒。

```python
# 设备侧（伪代码，烧进固件）
def build_password(secret: bytes, ts: int, nonce: str) -> str:
    msg = f"{ts}\n{nonce}".encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()

# 平台侧
def verify(device_name: str, ts: int, nonce: str, got: str) -> bool:
    if abs(time.time() - ts) > 300:          # 时钟窗口
        return False
    if not nonce_store.consume(nonce, ttl=300):  # 单次有效
        return False
    want = hmac.new(secret_of(device_name), f"{ts}\n{nonce}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(want, got)     # 必须常数时间比较
```

::: warning `nonce` 单次有效 ≠ 安全
如果 `nonce` 由**设备**生成，重放窗口内仍然可以重放。`nonce` 必须由**平台**签发并与 `device_name` 绑定，否则「单次有效」只是防了自己人。
:::

## 三、产线烧录：唯一性必须在入库前校验

身份体系最容易出的事故不在密码学，在产线：**两台设备烧了同一份凭证**。它们都能连上，数据混在一起，等发现时已经积累了几个月的数据。

| 校验点 | 做法 | 失败后果 |
| --- | --- | --- |
| 密钥生成 | 服务端生成，**不复用随机源**，一设备一份 | 两台同密钥，云端不可区分 |
| 烧录回执 | 设备回读 `device_name` 与密钥指纹（`sha256(secret)[:8]`）上报产线系统 | 烧错无法发现 |
| 入库 | `device_name` 全局唯一 + `secret_fp` 全局唯一（**两个唯一键都要**） | 重复入库被静默忽略 |
| 首连校验 | 设备首连时上报 `secret_fp`，平台比对 | 张冠李戴长期存在 |

```sql
-- 产线入库：两个唯一键，任一冲突即整批回滚
CREATE TABLE device (
  device_id     TEXT PRIMARY KEY,
  product_key   TEXT NOT NULL,
  device_name   TEXT NOT NULL,
  secret_hash   BLOB NOT NULL,
  secret_fp     TEXT NOT NULL,           -- sha256(secret) 前 8 字节，用于首连比对
  state         TEXT NOT NULL DEFAULT 'PROVISIONED',
  created_at    TEXT NOT NULL,
  UNIQUE (product_key, device_name),
  UNIQUE (secret_fp)                      -- 同一份密钥不许出现在两台设备上
);
```

## 四、mTLS：把身份放进证书

用 X.509 时，**身份来自证书的 CN（或 SAN）**，而不是 `client_id`。Broker 必须配置成「要求客户端证书 + 拒绝匿名」，并把 CN 映射为 `username`，再用 ACL 按 `username` 授权主题。

```conf
# mosquitto.conf 片段（2.1.x）
listener 8883
allow_anonymous false
cafile   /etc/mosquitto/ca.crt
certfile /etc/mosquitto/server.crt
keyfile  /etc/mosquitto/server.key
require_certificate true
use_identity_as_username true      # CN → username，ACL 才有主语
```

::: danger 本页特有的坑
1. **把 `device_secret` 写进固件镜像**。一份固件发给一万台设备 = 一万台共用一份密钥，且镜像可被解包。正确做法是「密钥在产线单独写入安全区（Secure Element / eFuse），固件里只有读取接口」。
2. **证书有效期照抄站点证书的 90 天**。设备装在现场天花板里，没有 90 天换一次的能力。客户端证书应按「设备寿命」签发（5~10 年），并用**短期会话凭证**（平台签发的 token，7 天）降低私钥泄露的影响面。
3. **设备时钟没同步就去校验证书有效期**。证书 `notBefore` 是 2026-01-01，设备时钟停在 1970，TLS 握手直接失败，而设备侧日志只有一行 `SSL_ERROR`。修法：设备侧允许「首次连接不校时」+ 连接后立刻 NTP/HTTP `Date` 校准，再校验证书。
4. **把 `client_id` 当身份**。`client_id` 是客户端自选的字符串，任何人都能填别人的。身份只能来自凭证（密钥或证书），`client_id` 只用于会话寻址。
:::

## 五、轮换：现场换不了密钥怎么办

设备装在现场，密钥泄露后不能上门。可用的三条路：

| 方案 | 怎么做 | 前提 | 代价 |
| --- | --- | --- | --- |
| **双凭证窗口** | 平台同时接受新旧两把密钥，14 天后停用旧的 | 设备支持远程写入新密钥 | 需要设备端可写安全区 |
| **短期令牌** | 设备用长期密钥换 7 天 token，token 泄露只影响 7 天 | 设备能存 token 并刷新 | 多一次换取往返 |
| **证书续期（EST/SCEP）** | 设备用旧证书申请新证书 | PKI + 设备支持 | 实现复杂，回滚难 |

无论哪种，**必须有一条「轮换完成后旧凭证真的失效」的验证**：

```shell
# 轮换后：旧密钥必须连不上
mosquitto_pub -h mqtt.example.com -p 8883 --cafile ca.crt \
  -u SN2026103100071 -P "$OLD_SECRET" -t 'up/SN2026103100071' -m '{}' -q 1
# 期望：Connection Refused: not authorised.

# 新密钥必须连得上
mosquitto_pub -h mqtt.example.com -p 8883 --cafile ca.crt \
  -u SN2026103100071 -P "$NEW_SECRET" -t 'up/SN2026103100071' -m '{}' -q 1
# 期望：exit=0，无输出
```

## 六、判据

| 判据 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `IOK-A` | 是否存在「同型号共用密钥」的量产设备 | 存在即不合格 | 产线改一机一密；`secret_fp` 加唯一键 |
| `IOK-B` | `device` 表是否同时有 `(product_key, device_name)` 与 `secret_fp` 两个唯一键 | 缺一即不合格 | 补 DDL；存量按 `secret_fp` 分组查重 |
| `IOK-C` | 库中 `device_secret` 是明文还是哈希 | 明文即不合格 | 改存 `HMAC(pepper, secret)`，并用 `secret_fp` 支持首连比对 |
| `IOK-D` | 首连时是否校验设备上报的 `secret_fp` | 不校验即不合格 | 接入回调里比对，不一致拒绝并告警 |
| `IOK-E` | mTLS 是否 `require_certificate true` 且 `use_identity_as_username true` | 缺一即不合格 | 改 Broker 配置；补 ACL 按 `username` 授权 |
| `IOK-F` | 客户端证书有效期是否覆盖设备寿命，或是否有短期令牌机制 | 都没有即不合格 | 二者择一：长证书 + 短期 token，或 EST 续期 |
| `IOK-G` | 轮换后旧凭证是否被验证过失效 | 未验证即不合格 | 把本文第五节的两条命令写进发布检查单 |
| `IOK-H` | 退役设备的凭证是否在拒绝名单且不可复活 | 仍能连上即不合格 | 吊销证书 + 撤销 token + `device.state='RETIRED'` 三重校验 |

## 七、验证方式

```shell
# 1. 同一份密钥是否出现在两台设备上（应为 0）
sqlite3 /tmp/iot.db "SELECT secret_fp, count(*) c FROM device GROUP BY secret_fp HAVING c > 1;"

# 2. 证书链与 CN 是否正确（设备证书）
openssl x509 -in device.crt -noout -subject -dates
# 期望：subject 含 CN=SN2026103100071；notAfter 覆盖设备寿命

# 3. Broker 是否真的要求客户端证书（不带证书应失败）
mosquitto_pub -h mqtt.example.com -p 8883 --cafile ca.crt -t 'up/x' -m '{}'
# 期望：报错退出（而不是静默成功）
```

## 参考资料

- MQTT 5.0 §3.1.2.2（CONNECT 中的 `username`/`password` 字段）与 §3.1.2.11（会话过期）
- [Eclipse Mosquitto 手册](https://mosquitto.org/man/mosquitto-conf-5.html)——`require_certificate`、`use_identity_as_username`
- [证书生命周期](../../../Ops/CertificateLifecycle/index.md)——站点证书与设备证书的差异
- [连接与会话](../ConnectionSession/index.md)——拿到身份之后，会话怎么建
