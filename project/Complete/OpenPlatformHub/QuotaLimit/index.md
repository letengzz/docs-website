# 配额与限流的判定点

计量回答「**发生了什么**」，配额回答「**还允不允许**」。这两句话如果不用同一个时间口径，就会出现一个永远说不清的问题：**被限流的那 449 次请求，算不算用量？** 不算，客户觉得「我发了 6,000 次你只认 5,551 次」；算，客户觉得「你没让我用还收我钱」。

::: tip 一句话理解
**判定点只能有一个，时间窗也只能有一个。** 三个地方都做判断，就等于三套口径；三个地方各用一个 `window_start`，就等于三张账单。
:::

本页是周期 8 第 2 周第 2 步（第 229 天），判据族 `EOU-A` ~ `EOU-H`，共 8 条，定义在最后一节。

::: info 为什么前缀是 `EOU`
`EOQ` 在库内已被占用（228 个文件命中），`EOR` 属于 `EventOrderHub/OrderFlow`，所以本步选 `EOU`（U = Usage cap）。**先 `judgeidcheck` 再动笔**是这十几天踩出来的纪律。
:::

## 一、三处判定点：只能信一处

一个请求进来，链路上有三处「可以拦」：

| 位置 | 优点 | 致命缺点 | 本项目取值 |
| --- | --- | --- | --- |
| 网关（前置） | 拦得早，不打到后端 | **看不到业务语义**（哪个套餐、哪个接口组） | 只做「全局熔断」，不做配额 |
| 应用（`/v1/*` 处理函数） | 能看到 `app_id`、路径、套餐 | 每个接口都要记得调一次 | **唯一的配额判定点** |
| 异步（消费者 / 批处理） | 能补算、能对账 | **已经执行完了**，只能事后扣钱 | 不做判定，只做核对 |

真正的坑不在「选哪个」，而在**三个都做了**。三个都做时，实际放行量由**最宽松的那一处**决定：

- 网关按 100/分钟拦、应用按 100/分钟扣、异步再补扣一次；
- 用户看到的 429 来自网关，但账单上的用量来自应用；
- 网关重启后计数清零，应用还在扣——两边的「这个窗口用了多少」从这一刻起就不同了。

## 二、`window_start`：一个必须共享的字段

计量表 `usage` 与配额表 `quota_counter` 都要落 `window_start`，而且**必须是同一个值**。

```sql
-- 计量：一次调用一行，window_start 由服务端统一算
CREATE TABLE usage (
  app_id       TEXT    NOT NULL,
  request_id   TEXT    NOT NULL,          -- 客户端生成并复用（第 228 天的 EOM）
  window_start TEXT    NOT NULL,          -- 2026-11-01T13:00:00Z（整分钟对齐）
  units        INTEGER NOT NULL CHECK (units > 0),
  status_code  INTEGER NOT NULL,          -- 200 / 429 / 4xx / 5xx
  billed       INTEGER NOT NULL CHECK (billed IN (0,1)),   -- 是否计入账单
  PRIMARY KEY (app_id, request_id)
);

-- 配额：一个 (app_id, 窗口) 一行，条件更新扣减
CREATE TABLE quota_counter (
  app_id       TEXT    NOT NULL,
  window_start TEXT    NOT NULL,
  used         INTEGER NOT NULL DEFAULT 0,
  limit_units  INTEGER NOT NULL,
  PRIMARY KEY (app_id, window_start),
  CHECK (used >= 0 AND used <= limit_units)   -- 最后一道闸门
);
```

`CHECK (used <= limit_units)` 这条约束是**最后一道闸门**：即使应用层写错，数据库也不会让 `used` 超过上限。它挡住的是「代码里判断用了 `>` 而不是 `>=`」这类经典错误。

### 三种窗口口径实测

配额 100/分钟，两种流量形态，三种算法（本机读数，Python 3.13.12，非压测）：

| 流量形态 | 固定窗口 | 滑动窗口 | 令牌桶（速率 100/60，容量 100） |
| --- | --- | --- | --- |
| 第 59 秒 100 次 + 第 61 秒 100 次（临界双突发） | **200** | 100 | 103 |
| 均匀 48 次/分钟 | 48 | 48 | 48 |

固定窗口在临界点放行了 **200**——正好是配额的两倍，因为两批请求落在两个不同的窗口里。这就是本项目在契约里写死「**配额按令牌桶口径**」的原因：突发要能用（客户确实会批量同步），但持续速率要有上界。

::: danger 换了窗口口径，历史数据不能直接比
从固定窗口换成滑动窗口之后，同一个客户「上个月的用量」在两个口径下不是一个数。切换时必须**双跑一个月**，把两个口径的差写进账单说明，否则第一次账单出来就是一场争议。
:::

## 三、被限流的请求算不算用量

答案是**两个字段，不是两个答案**：`usage` 表里既有 `status_code`，也有 `billed`。

| 请求结果 | 落 `usage` | `billed` | 理由 |
| --- | --- | --- | --- |
| 200 正常返回 | 是 | 1 | 正常计费 |
| 429 被限流 | 是 | **0** | 有记录、不计费（可解释、可申诉） |
| 4xx 参数错 | 是 | 0 | 有记录，帮助客户排查 |
| 5xx 服务端错 | 是 | 0 | 不算客户的账 |

本机读数（1 小时 6,000 次请求，配额按滑动 100/60s）：

| 口径 | 计入的请求数 | 与「全部计入」的差 |
| --- | --- | --- |
| 全部计入（含 429） | 6,000 | — |
| 只计放行（200） | 5,551 | **−7.48%** |

差 7.48%，在账单上就是「客户认为他买了 6,000 次，你只认 5,551 次」。**两种口径都能自圆其说，但必须在契约里写死一种，并且在门户上让客户能看到 429 的次数**。

## 四、扣减的唯一写入点：条件更新

配额扣减是高并发下最容易写错的一行代码。本机读数（200 并发、配额 100、SQLite WAL）：

| 写法 | 报成功的请求 | 实际 `used` | 超发 |
| --- | --- | --- | --- |
| 先查后改 | **200** | **8** | **192** |
| 条件更新 | 100 | 100 | 0 |

```sql
-- 唯一正确的扣减：一条语句完成「判断 + 写入」
UPDATE quota_counter
   SET used = used + :units
 WHERE app_id = :app AND window_start = :w
   AND used + :units <= limit_units;
-- rowcount = 0 ⇒ 超配额，返回 429，不写 billed=1 的 usage
```

::: danger 三个必看细节
1. **`rowcount = 0` 不是异常，是正常分支。** 它意味着「配额用完了」，要走 429 而非 500——抛 500 会让客户端重试，重试会继续扣配额，形成「越重试越被限」的死循环。
2. **`used + :units <= limit_units` 不能写成 `used < limit_units`。** 后者在 `units > 1` 时会放行超额（配额 100、已用 99、本次要 5，`99 < 100` 成立，扣完变成 104）。
3. **窗口不存在时要先插入再扣。** `INSERT ... ON CONFLICT DO NOTHING` 建行，再执行上面的条件更新；两步都在同一事务里，否则并发下会出现「行不存在 → 扣减失败 → 全部 429」。
:::

## 五、429 的四个头：让客户端能自己退避

被限流不是失败，是**协调**。响应必须给足信息，否则客户端只能盲目重试：

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 17
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 2026-11-01T13:07:00Z
```

| 头 | 含义 | 客户端该怎么用 |
| --- | --- | --- |
| `Retry-After` | 建议等待秒数 | 等这么久再重试，**不要指数退避**（退避会撞上同一窗口） |
| `X-RateLimit-Limit` | 本窗口上限 | 展示与自适应 |
| `X-RateLimit-Remaining` | 本窗口剩余 | 提前减速 |
| `X-RateLimit-Reset` | 窗口重置时刻 | 定时任务按这个时刻对齐批量任务 |

`Retry-After` 从 `window_start + 窗口长度 − 现在` 算出来，**不要复用请求头里的任何客户端时间**——客户端时钟不可信。

## 六、与计量的三处对齐

配额和计量共用 `window_start`，所以三处对齐变成可查的 SQL：

```sql
-- ① 同一窗口内，billed=1 的用量不得超过配额上限
SELECT c.app_id, c.window_start, c.used, c.limit_units
  FROM quota_counter c
 WHERE c.used > c.limit_units;
-- 期望：0 行（CHECK 已保证，这条是双保险）

-- ② 同一窗口内，放行的请求数不得超过 used（否则有请求绕过了扣减）
SELECT u.app_id, u.window_start, count(*) AS passed,
       (SELECT used FROM quota_counter c
         WHERE c.app_id=u.app_id AND c.window_start=u.window_start) AS used
  FROM usage u
 WHERE u.status_code < 400
 GROUP BY u.app_id, u.window_start
HAVING passed > used;
-- 期望：0 行

-- ③ 被限流的请求必须有记录、且 billed=0
SELECT count(*) FROM usage WHERE status_code = 429 AND billed = 1;
-- 期望：0
```

第 ② 条是这套设计的核心断言：**「放行的请求数」与「扣减的次数」必须是同一个数**。它一旦不为 0，说明有一条路径能绕过扣减——通常是新加的接口忘了调中间件。

## 七、判据清单

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `EOU-A` | 配额判定只发生在应用层一处，网关只做熔断 | 网关代码里无 `quota` 相关读写 |
| `EOU-B` | `usage.window_start` 与 `quota_counter.window_start` 由同一函数生成 | 两表同窗口值完全一致 |
| `EOU-C` | 扣减用条件更新，`rowcount=0` 走 429 | 200 并发下 `used` 恰为上限 |
| `EOU-D` | `CHECK (used <= limit_units)` 存在于表结构 | 直接 `UPDATE` 超额被拒 |
| `EOU-E` | 429 响应四头齐全，`Retry-After` 由服务端算 | 抓包或断言四个头都存在 |
| `EOU-F` | 被限流请求落 `usage` 且 `billed=0` | 查询 ③ 返回 0 |
| `EOU-G` | 放行请求数 = 扣减数（查询 ② 为 0 行） | 跑查询 ②，期望 0 行 |
| `EOU-H` | 窗口切换有双跑期，差异可解释 | 切换月有两套口径的对照查询 |

## 八、当日做了什么 / 如何验证 / 下一步

**做了什么**：把「配额判定」收敛到应用层唯一写入点（条件更新 + `CHECK` 双闸门），把 `window_start` 统一成一个函数生成，并定下「429 落库但 `billed=0`」的计费口径。配额表新增 1 张（`quota_counter`），`usage` 新增 1 列（`billed`），契约新增 4 个响应头。

**如何验证**：

```shell
# 1) 建表：应为 13 张（第 1 周 12 张 + quota_counter）
sqlite3 /tmp/oph.db < db/schema.sql
sqlite3 /tmp/oph.db "SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
# 期望：13

# 2) 条件更新不可超发：并发 200 次、上限 100，最终 used=100，成功 100 次
sqlite3 /tmp/oph.db "SELECT used, limit_units FROM quota_counter WHERE app_id='app1';"
# 期望：100|100

# 3) CHECK 是双闸门：直接写超额应报错
sqlite3 /tmp/oph.db "UPDATE quota_counter SET used = limit_units + 1 WHERE app_id='app1';"
# 期望：Error: CHECK constraint failed

# 4) 被限流请求不得计费：应输出 0
sqlite3 /tmp/oph.db "SELECT count(*) FROM usage WHERE status_code=429 AND billed=1;"
# 期望：0

# 5) 放行数 = 扣减数：应输出 0 行
sqlite3 /tmp/oph.db "SELECT u.app_id, u.window_start, count(*) passed,
  (SELECT used FROM quota_counter c WHERE c.app_id=u.app_id AND c.window_start=u.window_start) used
  FROM usage u WHERE u.status_code<400 GROUP BY u.app_id,u.window_start HAVING passed > used;"
# 期望：0 行
```

**下一步**：第 2 周第 3 步「`/oauth/token` 与 `/v1/ping` 两个最小接口」——用一条真实令牌把「验签 → 配额 → 计量」三段串起来，判据族占位 `EOV`（先 `judgeidcheck` 再动笔）。

## 参考资料

- [计量中间件的唯一写入点](../Metering/index.md)：`window_start` 的上游
- [数据库设计：十二张表与四条重复防线](../DatabaseDesign/index.md)：`usage` 的原始形态
- [接口契约与错误码](../Contracts/index.md)：429 的契约位置
- [开放平台 · 配额与限流](../../../../docs/Backend/OpenPlatform/QuotaUsage/index.md)：文档底座的对应章节
- [网关与流量治理](../../../../docs/Backend/GatewayDeep/Overview/index.md)：前置层该做什么、不该做什么
