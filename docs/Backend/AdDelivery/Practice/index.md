# 实战：一条能跑起来的竞价链路

前面八页讲的是「哪里会错」，这一页把它们拼成一条能跑的最小链路：**接收请求 → 定向过滤 → 频控 → 预算检查 → 算 eCPM → 定价 → 记账**。目标不是「功能齐全」，而是**每一步都有可执行的验收命令**，并且负向用例全部有明确返回。

![最小竞价链路的七步流水](../assets/ad-practice.svg)

本页判据族 `ADX-A` ~ `ADX-H`，共 8 条。定义表在第六节。

## 一、目标与验收边界

| 项 | 目标值 | 怎么验 |
| --- | --- | --- |
| 单次竞价延迟 | p50 ≤ 25 ms、p99 ≤ 40 ms | 压测脚本输出分位数 |
| 计费幂等 | 同一事件重放 10 次，金额不变 | 唯一键 + 断言 |
| 预算不超投 | 并发 50 下花费 ≤ 预算 | 条件更新 + 断言 |
| 频控不越界 | 跨零点 12 次请求，放行 ≤ 3 次 | 滑动窗口用例 |
| 定价正确 | 成交价 ≤ 赢家出价 且 ≥ 第二名 | 结算断言 |
| 失败可归因 | 每种失败有独立状态码 | 状态码枚举 + 计数 |

## 二、表结构：六张表就够

```sql
-- 1) 计划与计费口径
create table campaign (
  campaign_id     bigserial primary key,
  advertiser_id   bigint      not null,
  name            text        not null,
  billing_event   text        not null check (billing_event in ('IMPRESSION','CLICK','CONVERSION')),
  optimize_goal   text        not null check (optimize_goal in ('CLICK','CONVERSION','VALUE')),
  target_cpa      numeric(12,2),                 -- oCPM 用
  bid_cap         numeric(12,4) not null,        -- 单次出价上限（元/千次）
  daily_budget    numeric(14,2) not null,
  timezone        text        not null default 'Asia/Shanghai',
  status          text        not null default 'ACTIVE'
);

-- 2) 预算（按日一行，原子扣减）
create table campaign_budget (
  campaign_id  bigint not null,
  stat_date    date   not null,
  total_cents  bigint not null,
  spent_cents  bigint not null default 0,
  reserved_cents bigint not null default 0,      -- 赢了但未计费的冻结额
  primary key (campaign_id, stat_date),
  constraint budget_not_over check (spent_cents + reserved_cents <= total_cents)
);

-- 3) 频控（四层共用一张表，scope 区分）
create table frequency_counter (
  user_key   text   not null,
  scope      text   not null check (scope in ('CREATIVE','CAMPAIGN','ADVERTISER','GLOBAL')),
  scope_id   text   not null,
  win_start  timestamptz not null,
  hits       int    not null default 0,
  primary key (user_key, scope, scope_id, win_start)
);

-- 4) 计费明细（唯一键 = 计费事件，不重复收钱）
create table billing_detail (
  impression_id  text primary key,
  campaign_id    bigint not null,
  request_id     text   not null,
  bid_cpm        numeric(12,4) not null,
  settle_cpm     numeric(12,4) not null,
  cost_cents     bigint not null,
  event_time     timestamptz not null,
  traffic_status text not null default 'CLEAN' check (traffic_status in ('CLEAN','SUSPECT','FILTERED')),
  billed_at      timestamptz not null default now()
);

-- 5) 竞价审计（可重放）
create table auction_log (
  request_id     text primary key,
  imp_id         text not null,
  candidates     jsonb not null,     -- 参与排序的候选（脱敏）
  winner_id      bigint,
  settle_cpm     numeric(12,4),
  outcome        text not null check (outcome in ('WIN','NO_BID','NO_CANDIDATE','TIMEOUT','BUDGET_CAPPED','FREQ_CAPPED')),
  latency_ms     numeric(8,2) not null,
  created_at     timestamptz not null default now()
);

-- 6) 报表定版快照
create table report_snapshot (
  stat_date date    not null,
  version   int     not null,
  final     boolean not null default false,
  metrics   jsonb   not null,
  primary key (stat_date, version)
);
```

三处设计要点：

1. **`campaign_budget` 用 `check` 约束兜底**。即使代码写错，数据库也会拒绝超投；这是「最后一道门」。
2. **`frequency_counter` 用 `win_start` 做窗口起点**，滑动窗口时按时间为键查询，不需要定时清零。
3. **`auction_log` 存候选与 `outcome`**。没有它，你无法回答「为什么这次没赢」——而这是广告主最常问的问题。

## 三、七步流水

```text
① parse      解析 OpenRTB 请求，校验 tmax 与必填字段
② targeting  上下文 + 人群 + 地理，先算排除
③ frequency  四层频控，命中则换候选
④ budget     原子扣减冻结额，超限返回 BUDGET_CAPPED
⑤ score      eCPM = bid × pCTR × pCVR，排序（并列用 bid_id）
⑥ pricing    一价取自己的出价、二价取 min(second+tick, bid)
⑦ billing    记 auction_log；曝光渲染回调后写 billing_detail
```

### 3.1 关键实现：预算原子扣减

```python
# 关键实现：先冻结再竞价，超限直接返回（不是赢了再丢）
def reserve_budget(conn, campaign_id, stat_date, cost_cents):
    cur = conn.execute(
        """
        update campaign_budget
           set reserved_cents = reserved_cents + %s
         where campaign_id = %s and stat_date = %s
           and spent_cents + reserved_cents + %s <= total_cents
        """,
        (cost_cents, campaign_id, stat_date, cost_cents),
    )
    return cur.rowcount == 1          # False 表示超限，调用方必须返回 NO_BID
```

`rowcount == 1` 是唯一的成功判据；不要用「先 select 再判断」，那在并发下必错。

### 3.2 关键实现：频控（滑动窗口）

```python
# 四层频控：任一超限即不可投；命中后应换下一个候选，而不是返回空
def freq_ok(conn, user_key, scopes, window_seconds):
    for scope, scope_id, limit in scopes:
        n = conn.execute(
            """
            select coalesce(sum(hits), 0) from frequency_counter
             where user_key = %s and scope = %s and scope_id = %s
               and win_start > now() - (%s || ' seconds')::interval
            """,
            (user_key, scope, scope_id, window_seconds),
        ).fetchone()[0]
        if n >= limit:
            return False
    return True
```

## 四、负向用例：十二条必须拒绝的请求

| # | 场景 | 期望返回 | 断言点 |
| --- | --- | --- | --- |
| P1 | `tmax` 缺失 | `400 INVALID_REQUEST` | 不进入竞价，不打点 `WIN` |
| P2 | `imp` 为空数组 | `400 INVALID_REQUEST` | 不产生 `auction_log` 的 `WIN` |
| P3 | `bidfloor` 高于 `bid_cap` | `NO_BID` | 不浪费预算冻结 |
| P4 | 定向全不命中 | `NO_CANDIDATE` | 与 `NO_BID` 分列统计 |
| P5 | 命中排除人群（已购买） | `NO_CANDIDATE` | 排除优先于包含 |
| P6 | 四层频控任一超限 | `FREQ_CAPPED` | 返回下一候选而非空 |
| P7 | 预算不足 | `BUDGET_CAPPED` | `spent + reserved ≤ total` |
| P8 | 素材尺寸与广告位不符 | `NO_BID` | 不产生「渲染失败」曝光 |
| P9 | 同一 `impression_id` 重复计费 | 第二次忽略 | `billing_detail` 行数不变 |
| P10 | 成交价 > 赢家出价 | 拒绝该次竞价 | `settle_cpm <= bid_cpm` |
| P11 | 跨零点 12 次请求 | 放行 ≤ 3 次 | 滑动窗口生效 |
| P12 | `pCVR` 为 0 的 oCPM 计划 | `NO_BID` | 不出现「出价 0 却赢」 |

## 五、验收 SQL：六条查询与目标输出

```sql
-- Q1 预算不超投（期望：0 行）
select campaign_id, stat_date, spent_cents, reserved_cents, total_cents
  from campaign_budget
 where spent_cents + reserved_cents > total_cents;

-- Q2 计费与竞价一一对应（期望：0 行）
select b.impression_id
  from billing_detail b
  left join auction_log a on a.request_id = b.request_id
 where a.request_id is null;

-- Q3 失败原因分布（期望：每类都有计数，且 TIMEOUT 占比 < 1%）
select outcome, count(*) from auction_log
 group by outcome order by 2 desc;

-- Q4 成交价不得高于出价（期望：0 行）
select request_id, bid_cpm, settle_cpm from billing_detail
 where settle_cpm > bid_cpm;

-- Q5 频控越界（期望：0 行；单用户单日单 scope 不超过上限）
select user_key, scope, scope_id, sum(hits) as n
  from frequency_counter
 group by 1,2,3 having sum(hits) > 100;

-- Q6 待核流量占比（期望：< 5%，且 FILTERED 不计入结算）
select traffic_status, count(*), sum(cost_cents)
  from billing_detail group by 1;
```

## 六、本页判据

| 判据 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `ADX-A` | 六张核心表齐备，且 `billing_detail` 以 `impression_id` 为主键 | 结构可支撑幂等 | 按第二节 DDL 建表，补唯一约束 |
| `ADX-B` | 预算扣减用条件更新，`rowcount` 是唯一成功判据 | 并发不超投 | 替换「先查后改」，加 `check` 约束兜底 |
| `ADX-C` | 七步流水每步有独立状态码，`auction_log.outcome` 覆盖六种 | 失败可归因 | 补 `NO_CANDIDATE` / `FREQ_CAPPED` 等枚举 |
| `ADX-D` | P1~P12 十二条负向用例全部有自动化断言 | 边界有防线 | 按第四节逐条写测试 |
| `ADX-E` | 频控用滑动窗口，跨零点用例放行 ≤ 3 | 频控不越界 | 换窗口实现，或对齐用户时区 |
| `ADX-F` | 结算只读 `billing_detail`，不读点击/曝光日志 | 金额可复现 | 结算任务改为读宽表 |
| `ADX-G` | `auction_log` 存候选快照，可按 `request_id` 重放 | 可自证 | 落候选的 `(bid, pctr, pcvr, ecpm)` |
| `ADX-H` | 报表有定版快照（`final=1`），且与实时数并列 | 结算与优化分离 | 建 `report_snapshot`，T+7 写定版 |

## 七、验证方式

```shell
# 1) 起一个最小环境（PostgreSQL 16+，或 SQLite 做原型）
docker run --rm -d --name addemo -e POSTGRES_PASSWORD=demo -p 5432:5432 postgres:16
psql "postgresql://postgres:demo@127.0.0.1:5432/postgres" -c "select version();"
```

预期输出：一行包含 `PostgreSQL 16.x`。若端口被占用，改 `-p 5433:5432` 并同步连接串。

```shell
# 2) 建表后跑负向用例 P9：同一 impression 计费两次，金额不变
psql "postgresql://postgres:demo@127.0.0.1:5432/postgres" <<'SQL'
create table if not exists billing_detail(
  impression_id text primary key, cost_cents bigint not null);
insert into billing_detail values ('imp-1', 42) on conflict do nothing;
insert into billing_detail values ('imp-1', 42) on conflict do nothing;
select count(*), sum(cost_cents) from billing_detail;
SQL
```

预期输出：`1 | 42`。若得到 `2 | 84`，说明 `on conflict do nothing` 缺失或主键没建。

```shell
# 3) 跑 Q1（预算不超投）与 Q4（成交价不高于出价），两者都应返回 0 行
psql "postgresql://postgres:demo@127.0.0.1:5432/postgres" -c \
  "select count(*) from campaign_budget where spent_cents + reserved_cents > total_cents;"
psql "postgresql://postgres:demo@127.0.0.1:5432/postgres" -c \
  "select count(*) from billing_detail where settle_cpm > bid_cpm;"
```

预期输出：两条都是 `0`。任何一条非 0，都**不要继续上线**——这两条是钱的门。

```shell
# 4) 压测 p99（用 wrk 或 hey，目标 p99 <= 40ms）
hey -n 20000 -c 50 -m POST -T application/json \
  -D /tmp/bid_request.json http://127.0.0.1:8080/bid
```

预期输出：`99%` 那一行的延迟 ≤ 40 ms。若 p99 超线，先看[竞价与排序](../Auction/index.md)第五节的五段耗时分解，重点查特征拉取。

## 八、参考资料

- IAB Tech Lab《OpenRTB 2.6》（请求/响应结构，`tmax` 与 `imp` 语义）：<https://github.com/InteractiveAdvertisingBureau/openrtb2.x>
- PostgreSQL 文档《Constraints》（`check` 约束与唯一索引，超投兜底）：<https://www.postgresql.org/docs/current/ddl-constraints.html>
- PostgreSQL 文档《INSERT ... ON CONFLICT》（计费幂等的标准写法）：<https://www.postgresql.org/docs/current/sql-insert.html>
- Prebid Server 文档《Auction Endpoint》（一个可对照的开源实现）：<https://docs.prebid.org/prebid-server/endpoints/openrtb2.html>
- IAB Tech Lab《Supply Chain Foundations》（`schain` 校验在实战里的接入点）：<https://iabtechlab.com/standards/supply-chain-foundations/>
