# 实战：一个能跑起来的最小决策服务

这一页把前六页的约定装进一个能真正跑起来的东西：**PostgreSQL 存名单与决策日志、Redis 存计数、进程内规则引擎 + 评分卡、一个 `/decide` 接口**。目标不是生产可用，而是**可验收**——每一步都有能复跑的命令和确定的输出。

按 S1~S10 顺序做，最后跑第 11 节的验收清单。全部命令在你自己的工程目录里执行，本库不提供可执行副本。

本页判据族 `RDP-A` ~ `RDP-H`，共 8 条。定义表见文末「本页判据」一节。

::: info 环境与版本
- macOS / Linux，Docker 24+，Python 3.12+
- PostgreSQL **18.6**（容器 `postgres:18.6`）
- Redis **8.2**（容器 `redis:8.2`）
- FastAPI + Uvicorn + psycopg 3 + redis-py
:::

## 一、验收标准（先定判据，再写代码）

| 编号 | 验收项 | 判定方式 |
| --- | --- | --- |
| P1 | 服务能起、`/healthz` 返回 200 | `curl -s -o /dev/null -w '%{http_code}'` |
| P2 | 四个动作都能被触发 | 四条固定请求各返回预期动作 |
| P3 | 名单命中优先于一切 | 黑名单请求返回 `REJECT` 且 `hits=["R_CARD_BLACK"]` |
| P4 | 同一 `decision_id` 重放结论一致 | 调两次，响应体除 `cached` 外完全相同 |
| P5 | 决策日志九列齐全 | `SELECT` 一行，九个字段非空 |
| P6 | 特征缺失走 `REVIEW` 而不是 `PASS` | 省略 `pay_fail_cnt_1h` 时返回 `REVIEW` |
| P7 | 规则版本可追溯 | 响应与日志都含 `rule_version=2026.10.1` |
| P8 | 决策 p99 < 30 ms（本机） | 100 次循环取 p99 |
| P9 | 名单过期后不再命中 | 把 `expire_at` 改到过去，再调一次 |
| P10 | 规则语法错误不会生效 | 改坏 YAML 后 reload 返回 422，旧版本仍工作 |
| P11 | 分数与分箱一致 | 同一输入两次算分相同，且能列出三个分箱贡献 |
| P12 | 无 `degraded` 以外的兜底静默 | 强制 `score=None` 时响应带 `degraded=true` |

## 二、S1 目录结构

```text
risk-svc/
├─ app/
│  ├─ main.py            # FastAPI 入口 + /decide
│  ├─ engine.py          # 规则引擎（YAML → 编译 → 求值）
│  ├─ scorecard.py       # 评分卡算分
│  ├─ store.py           # PG / Redis 访问
│  └─ runtime.py         # 单指针热更新
├─ rules/
│  └─ pay_risk.yaml      # 规则集（版本化文件）
├─ sql/
│  └─ 001_init.sql
├─ docker-compose.yaml
└─ requirements.txt
```

## 三、S2 依赖

```text
# requirements.txt
fastapi==0.115.*
uvicorn[standard]==0.32.*
psycopg[binary]==3.2.*
redis==5.2.*
pyyaml==6.0.*
pytest==8.3.*
httpx==0.28.*
```

```shell
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "import fastapi, psycopg, redis, yaml; print('ok')"   # 预期输出 ok
```

## 四、S3 起两个容器

```yaml
# docker-compose.yaml
services:
  pg:
    image: postgres:18.6
    environment:
      POSTGRES_PASSWORD: risk
      POSTGRES_DB: risk
    ports: ["5432:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d risk"]
      interval: 3s
      retries: 20
  redis:
    image: redis:8.2
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      retries: 20
```

```shell
docker compose up -d
docker compose ps        # 预期：pg 与 redis 都是 healthy
```

::: danger 注意
`docker compose ps` 里出现 `(health: starting)` 时不要急着建表——`pg_isready` 通过只代表进程在监听，**初始化脚本可能还在跑**。等到 `healthy` 再执行下一步，否则会随机遇到 `database "risk" does not exist`。
:::

## 五、S4 建表

```sql
-- sql/001_init.sql
CREATE TABLE IF NOT EXISTS risk_list (
  list_type   text NOT NULL,
  dimension   text NOT NULL,
  value_hash  text NOT NULL,
  source      text NOT NULL,
  reason_code text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  expire_at   timestamptz NOT NULL,
  hit_count   bigint NOT NULL DEFAULT 0,
  PRIMARY KEY (list_type, dimension, value_hash)
);
CREATE INDEX IF NOT EXISTS idx_risk_list_expire ON risk_list (expire_at);

CREATE TABLE IF NOT EXISTS decision_result (
  decision_id  text PRIMARY KEY,
  subject_id   text NOT NULL,
  scene        text NOT NULL,
  action       text NOT NULL,
  score        numeric(6,2),
  hits         text[] NOT NULL DEFAULT '{}',
  rule_version text NOT NULL,
  list_version text NOT NULL,
  degraded     boolean NOT NULL DEFAULT false,
  feature_missing text[] NOT NULL DEFAULT '{}',
  latency_ms   integer NOT NULL DEFAULT 0,
  created_at   timestamptz NOT NULL DEFAULT now(),
  expire_at    timestamptz NOT NULL DEFAULT now() + interval '24 hours'
);
```

```shell
docker compose exec -T pg psql -U postgres -d risk < sql/001_init.sql
docker compose exec -T pg psql -U postgres -d risk -c '\dt'   # 预期：risk_list、decision_result 两张表
```

## 六、S5 规则集

```yaml
# rules/pay_risk.yaml
version: 2026.10.1
scene: PAY
first_hit: true
rules:
  - id: R_CARD_BLACK
    group: BLOCK_LIST
    priority: 10
    when: [{ field: card_hash, op: in_list, args: { list: CARD_BLACK } }]
    action: REJECT
    reason: CARD_BLACKLIST

  - id: R_PAY_FAIL_1H
    group: BEHAVIOR
    priority: 50
    when:
      - { field: pay_fail_cnt_1h, op: gte, args: { value: 3 } }
      - { field: amount, op: gte, args: { value: 500 } }
    action: CHALLENGE
    reason: REPEATED_FAIL

  - id: R_NEW_DEVICE_BIG
    group: BEHAVIOR
    priority: 60
    when:
      - { field: device_first_seen_days, op: lte, args: { value: 1 } }
      - { field: amount, op: gte, args: { value: 3000 } }
    action: REVIEW
    reason: NEW_DEVICE_LARGE_AMOUNT
```

## 七、S6 引擎（关键实现）

完整实现约 120 行，这里给结构与关键片段：

```python
# app/engine.py
from dataclasses import dataclass
import yaml

MISSING = "MISSING"
OPS = {
    "gte": lambda v, a: v >= a["value"],
    "lte": lambda v, a: v <= a["value"],
    "eq":  lambda v, a: v == a["value"],
    "in_list": lambda v, a, lists=None: (v in lists.get(a["list"], set())),
}

@dataclass(frozen=True)
class Rule:
    id: str
    priority: int
    action: str
    reason: str
    when: tuple

def compile_rules(path: str, lists: dict):
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    rules = []
    for r in raw["rules"]:
        conds = []
        for c in r["when"]:
            op = OPS[c["op"]]
            args = c.get("args", {})
            conds.append((c["field"], op, args))
        rules.append(Rule(r["id"], r["priority"], r["action"], r["reason"], tuple(conds)))
    rules.sort(key=lambda x: x.priority)
    return raw["version"], tuple(rules)

def evaluate(rules, feats: dict, lists: dict, first_hit: bool = True):
    hits, missing = [], []
    for r in rules:
        ok = True
        for field, op, args in r.when:
            v = feats.get(field, MISSING)
            if v is MISSING:
                missing.append(field)
                ok = False                      # 缺失不命中，但记录
                break
            if "list" in args:
                if not op(v, args, lists):
                    ok = False
                    break
            elif not op(v, args):
                ok = False
                break
        if ok:
            hits.append(r.id)
            if first_hit:
                break                           # first-hit：命中即停
    return hits, sorted(set(missing))
```

两个容易写错的点：**`first_hit` 必须是参数而不是硬编码**（`all-match` 场景要用同一个函数）；**`missing` 要 `set` 去重后再返回**，否则同一缺失字段会被计多次，缺失率统计直接失真。

## 八、S7 评分卡

```python
# app/scorecard.py
BASE = 600
BINS = {
    "amount": [(100, 30), (1000, 18), (5000, 2), (None, -25)],
    "device_first_seen_days": [(1, -22), (30, -8), (365, 6), (None, 14)],
    "pay_fail_cnt_1h": [(0, 12), (2, 0), (None, -30)],
}

def _points(name: str, value):
    for limit, pts in BINS[name]:
        if limit is None or value < limit:
            return pts
    return 0

def score(feats: dict):
    if any(feats.get(k) is None for k in BINS):
        return None, {}
    parts = {k: _points(k, feats[k]) for k in BINS}
    return BASE + sum(parts.values()), parts
```

分箱边界与训练侧必须**同一份定义**（这里是 `BINS` 常量），上线前按[评分卡](../Scorecard/index.md)第七节做一次零差异对拍。

## 九、S8 接口与决策流程

```python
# app/main.py（节选）
@app.post("/decide")
def decide(req: DecideReq):
    t0 = time.perf_counter()
    cached = store.get_decision(req.decision_id)
    if cached:
        return {**cached, "cached": True}

    lists = store.load_lists()                     # 内存快照，带版本
    hits, missing = engine.evaluate(rules, req.features(), lists)
    sc, parts = scorecard.score(req.features())

    action = compose(hits, sc)                     # REJECT > REVIEW > CHALLENGE > PASS
    if missing and action == "PASS":
        action = "REVIEW"                          # 缺失即不确定
    resp = build_resp(req, action, hits, sc, parts, missing,
                      rule_version=VERSION,
                      degraded=(sc is None))
    store.save_decision(resp, latency_ms=int((time.perf_counter() - t0) * 1000))
    return {**resp, "cached": False}
```

三处必须按前几页的约定写：

1. **`get_decision` 在计算之前**，`save_decision` 用 `ON CONFLICT DO NOTHING`。
2. **`missing` 非空且本来是 PASS 时升级为 REVIEW**（第一页必失点 2）。
3. **`degraded` 在 `score is None` 时为真**，并透传到响应与日志（第七页降级矩阵）。

## 十、S9 起服务

```shell
uvicorn app.main:app --port 8000 --reload
curl -s http://127.0.0.1:8000/healthz        # 预期 {"status":"ok"}
```

## 十一、S10 验收：五条请求跑完 P1~P7

先把一条黑名单塞进去：

```shell
docker compose exec -T pg psql -U postgres -d risk -c \
"INSERT INTO risk_list(list_type,dimension,value_hash,source,reason_code,expire_at)
 VALUES ('BLACK','CARD','c_black_1','MANUAL','STOLEN_CARD', now() + interval '90 days');"
```

| # | 请求 | 预期 `action` | 预期 `hits` | 覆盖判据 |
| --- | --- | --- | --- | --- |
| Q1 | `amount=4800, card_hash=c_black_1, device_first_seen_days=420, pay_fail_cnt_1h=0` | `REJECT` | `["R_CARD_BLACK"]` | P2 P3 P7 |
| Q2 | `amount=520, card_hash=c_ok_2, device_first_seen_days=420, pay_fail_cnt_1h=3` | `CHALLENGE` | `["R_PAY_FAIL_1H"]` | P2 |
| Q3 | `amount=3500, card_hash=c_ok_3, device_first_seen_days=0, pay_fail_cnt_1h=0` | `REVIEW` | `["R_NEW_DEVICE_BIG"]` | P2 |
| Q4 | `amount=80, card_hash=c_ok_4, device_first_seen_days=900, pay_fail_cnt_1h=0` | `PASS` | `[]` | P2 |
| Q5 | 同 Q3 但不传 `pay_fail_cnt_1h` | `REVIEW` | `[]`，`feature_missing=["pay_fail_cnt_1h"]` | **P6** |

```shell
curl -s -X POST http://127.0.0.1:8000/decide -H 'content-type: application/json' -d '{
  "decision_id":"d-q1","subject_id":"u-1","scene":"PAY","amount":4800,
  "card_hash":"c_black_1","device_first_seen_days":420,"pay_fail_cnt_1h":0}'
# 预期：{"decision_id":"d-q1","action":"REJECT","hits":["R_CARD_BLACK"],
#        "score":628,"rule_version":"2026.10.1","degraded":false,"cached":false,...}
```

**注意 Q1 的 `score` 是 628 而不是「因为黑名单所以为 0」**——评分照算，只是动作被黑名单覆盖。这就是第一页「规则不能短路评分」的可执行形态：日志里必须能看到分数，否则事后无法评估「如果只靠模型会怎样」。

剩下五条（P4、P8~P12）用一个小脚本跑：

```python
# tests/test_gates.py（节选）
def test_p4_idempotent(client):
    a = client.post("/decide", json=Q1).json()
    b = client.post("/decide", json=Q1).json()
    assert a["action"] == b["action"] and b["cached"] is True

def test_p10_bad_yaml_keeps_old(client, tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("rules: [", encoding="utf-8")
    r = client.post("/admin/reload", json={"path": str(bad)})
    assert r.status_code == 422
    assert client.post("/decide", json=Q1).json()["action"] == "REJECT"
```

```shell
pytest -q      # 预期：全部通过；若 P8 抖动，先确认机器没在跑其他重活
```

## 十二、这一版刻意不做的事

- **不做特征平台**：请求体直接带特征，是为了让「决策」这一层可以被单独验收。接 Feast 见[信号与特征](../Signals/index.md)。
- **不做规则可视化**：YAML 就是唯一真相源，先保证可回滚，再谈编辑器。
- **不做模型服务**：评分卡是常量表，一次点积；换成模型服务要补超时与降级（第七页）。
- **不做多租户**：单场景 `PAY`，多场景用 `scene` 字段扩展，但规则文件的隔离要另外设计。

## 本页判据

| 编号 | 判据 | 看什么现象 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `RDP-A` | 先有 P1~P12 验收清单再写代码 | 仓库里有验收表，且每条能指到命令 | 补表，禁止「跑起来就算完」 |
| `RDP-B` | 每条验收都有确定性输入与输出 | 五条固定请求各自的预期 JSON | 固化 fixtures，别靠手输 |
| `RDP-C` | 黑名单优先且评分照算 | 黑名单请求的 `score` 非空 | 去掉「拦截即 return」的短路 |
| `RDP-D` | 幂等先读后算 | 代码顺序：读缓存 → 算 → 落库 | 调整顺序，落库用 `ON CONFLICT` |
| `RDP-E` | 缺失升级为 REVIEW | 缺特征时 `action=REVIEW` 且有 `feature_missing` | 加哨兵分支 |
| `RDP-F` | 坏配置不生效 | reload 失败返回 4xx，旧版本继续工作 | 编译失败保留旧引用 |
| `RDP-G` | 决策日志九列齐全 | `SELECT` 一行九列非空 | 补列，设为必填 |
| `RDP-H` | 刻意不做的四件事写清楚 | 页面有「不做」清单与原因 | 补清单，防范围蔓延 |

## 参考资料

- FastAPI 官方文档（依赖注入与后台任务）：<https://fastapi.tiangolo.com/>
- PostgreSQL 18 文档（`timestamptz`、`ON CONFLICT`）：<https://www.postgresql.org/docs/18/>
- Redis 8 文档（String / Hash / TTL 语义）：<https://redis.io/docs/latest/>
- Docker Compose 健康检查与启动顺序：<https://docs.docker.com/compose/how-tos/startup-order/>
- OWASP ASVS 4.0（输入校验与日志要求）：<https://owasp.org/www-project-application-security-verification-standard/>
