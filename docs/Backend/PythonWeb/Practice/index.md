# 实战：可部署的 API 服务

一句话定位：这一页把一个 FastAPI 应用从「`uvicorn main:app` 能在本机跑」推到「能进容器、能滚动更新、能被压测、能被定位」。差别全在四件事上：**配置从环境变量来、日志是结构化的、镜像是多阶段构建的、进程由 Gunicorn 托管**。

![Python API 服务的四种部署形态与选型](../assets/deploy-matrix.svg)

## 一、目标与验收

### 要做成什么

一个 `shop-api`，提供：

| 接口 | 语义 | 关键要求 |
| --- | --- | --- |
| `GET /health` | 存活探针 | **不查 DB**，纯进程健康，响应 < 5 ms |
| `GET /ready` | 就绪探针 | **要查 DB + Redis**，任一不可用返回 503 |
| `POST /order/create` | 创建订单 | 幂等、事务、Pydantic 强校验 |
| `GET /order/{order_id}` | 查订单 | 走 Redis 缓存 |
| `GET /metrics` | Prometheus 指标 | 与业务端口分离（独立端口或独立路径 + 内网白名单） |

### 验收判据

| 步骤 | 命令 | 期望 |
| --- | --- | --- |
| 1. 本地可跑 | `uvicorn app.main:app --reload` | 日志出现 `Application startup complete.` |
| 2. 探针正确 | `curl -s :8000/health` / `curl -s :8000/ready` | 200；把 Redis 停掉后 `/ready` 变 503 而 `/health` 仍 200 |
| 3. 打开数据库后能创建订单 | `curl -X POST :8000/order/create` | 201，返回 `order_id` |
| 4. 幂等生效 | 同 `Idempotency-Key` 再调 | 返回同一 `order_id`；DB 只有一行 |
| 5. 镜像可构建且体积合理 | `docker build -t shop-api:dev .` | 构建成功，镜像 < 250 MB |
| 6. 容器内可跑 | `docker run -p 8000:8000 shop-api:dev` | `/health` 200 |
| 7. 指标可抓 | `curl -s :9090/metrics \| head` | 有 `http_requests_total` 等指标 |

::: tip 第 2 步是「可部署」与「能跑」的分水岭
`/health` 与 `/ready` **必须是两个接口**，这是 K8s 滚动更新正确性的前提：
- `/health` 挂 `livenessProbe`：失败 → **重启容器**。所以它绝不能查 DB——DB 抖动会导致全部容器被重启，把小故障放大成雪崩。
- `/ready` 挂 `readinessProbe`：失败 → **摘掉流量，但不重启**。所以它要查依赖，让实例在依赖恢复前不接流量。
:::

## 二、工程布局

```text [目录结构]
shop-api/
├─ app/
│  ├─ __init__.py
│  ├─ main.py                 # FastAPI 实例 + lifespan + 中间件 + 路由挂载
│  ├─ core/
│  │  ├─ config.py            # pydantic-settings 配置（唯一来源）
│  │  ├─ logging.py           # 结构化日志 + trace_id 注入
│  │  ├─ metrics.py           # Prometheus 指标注册
│  │  └─ errors.py            # 统一异常处理器与错误码
│  ├─ api/
│  │  ├─ deps.py              # DbSession / CurrentUser / 分页依赖
│  │  └─ v1/
│  │     ├─ order.py          # 路由：只做参数→服务调用→响应
│  │     └─ health.py         # /health 与 /ready
│  ├─ schemas/                # Pydantic 模型（In / Out 分离）
│  │  └─ order.py
│  ├─ models/                 # SQLAlchemy 模型
│  │  └─ order.py
│  ├─ repositories/           # 数据访问（只依赖 models）
│  │  └─ order_repo.py
│  └─ services/               # 业务逻辑（只依赖 repositories 接口）
│     └─ order_service.py
├─ migrations/                # Alembic
├─ tests/
│  ├─ conftest.py
│  ├─ test_order_api.py
│  └─ test_idempotency.py
├─ deploy/
│  ├─ Dockerfile
│  ├─ docker-compose.yml
│  └─ k8s/deployment.yaml
├─ pyproject.toml             # 依赖与工具配置（ruff / pytest / mypy）
└─ .env.example               # 配置项清单（不含真实值）
```

分层依赖方向：`api → services → repositories → models`，**单向**。`services` 不 import `fastapi`，因此可以直接被单测调用，不需要起 ASGI 服务器。

## 三、配置管理：`pydantic-settings`

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # 环境标识
    env: str = Field(default="dev", pattern="^(dev|staging|prod)$")
    debug: bool = False

    # 数据库（必填，没有默认值 → 启动即失败）
    db_url: str
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_recycle: int = 1800
    db_echo: bool = False

    # Redis（可缺省 → 降级为不走缓存）
    redis_url: str | None = None

    # 服务
    host: str = "0.0.0.0"
    port: int = 8000
    metrics_port: int = 9090
    log_level: str = "INFO"

    # 安全
    jwt_secret: str
    jwt_expire_seconds: int = 3600

settings = Settings()          # 导入时就校验；缺失必填项会立刻抛错
```

::: danger 注意：`settings = Settings()` 要放在导入期，并且不要用默认值兜住必填项
- **放导入期**：配置错误在进程启动的第一秒就暴露，而不是等第一个请求。这条与 Go 侧的 `conf.MustLoad` 是同一个道理。
- **必填项不给默认值**：`db_url: str = ""` 会让服务「启动成功但每个请求都 500」。**宁可起不来，也不要带错误配置运行**——起不来是 30 秒能发现的问题，带错配置运行是上线后才发现的问题。

另外：**`.env` 只用于本地开发，不要提交真实值**；仓库里只放 `.env.example`。生产环境用 K8s Secret / 配置中心注入环境变量。
:::

## 四、可观测：日志、指标、trace_id

### 结构化日志

```python
import json, logging, sys, uuid
from contextvars import ContextVar

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "trace_id": trace_id_var.get(),
        }
        # 额外字段（如 path / method / cost_ms）通过 extra={} 传入
        for k, v in getattr(record, "extra_fields", {}).items():
            base[k] = v
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)

def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
```

中间件里注入 trace_id（**必须在最外层**，否则日志里没有它）：

```python
@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    tid = request.headers.get("x-trace-id") or uuid.uuid4().hex[:16]
    trace_id_var.set(tid)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        cost = (time.perf_counter() - start) * 1000
        logger.info("request", extra={"extra_fields": {
            "method": request.method, "path": request.url.path,
            "cost_ms": round(cost, 2),
        }})
    response.headers["x-trace-id"] = tid          # 回传给调用方，便于对账
    return response
```

### 指标

```python
from prometheus_client import Counter, Histogram, make_asgi_app

REQ = Counter("http_requests_total", "Total requests",
              ["method", "path", "status"])
LAT = Histogram("http_request_duration_seconds", "Request latency",
                ["method", "path"],
                buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5))
```

::: tip 指标标签要克制
`path` 标签**不能直接用原始 URL**（`/order/12345`），否则每个订单号都生成一条时间序列，指标基数爆炸（Prometheus 会 OOM）。做法：用**路由模板**作为标签（`/order/{order_id}`），FastAPI 里可以从 `request.scope["route"].path` 取到。

原则：**标签的取值集合必须是有界的**（方法名、状态码、路由模板、租户类型），**绝不能是无界的 ID、时间戳、URL**。
:::

## 五、多阶段 Dockerfile

```dockerfile [deploy/Dockerfile]
# ---------- 构建阶段 ----------
FROM python:3.14-slim AS builder

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# 先拷依赖清单，利用层缓存：只改业务代码时不会重装依赖
COPY pyproject.toml ./
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install .

# ---------- 运行阶段 ----------
FROM python:3.14-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 10001 appuser

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser migrations ./migrations
COPY --chown=appuser:appuser alembic.ini ./

USER appuser
EXPOSE 8000 9090

# 用 http 接口做容器级健康检查（与 /health 语义一致）
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# 生产用 Gunicorn 托管 uvicorn worker
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", "-b", "0.0.0.0:8000", \
     "--timeout", "60", "--graceful-timeout", "30", \
     "--access-logfile", "-", "--error-logfile", "-"]
```

::: danger 注意：五个必须做到的镜像实践
1. **必须以非 root 运行**（`USER appuser`）。容器以 root 跑时，一旦有文件写入漏洞，逃逸影响面完全不同。
2. **`PYTHONUNBUFFERED=1` 必须设**。不设时 stdout 被缓冲，容器日志会**延迟甚至丢失**（进程被 kill 时缓冲区里的日志全没了）——这是「容器里看不到日志」的第一原因。
3. **依赖层与代码层分开 COPY**。否则改一行代码就要重装全部依赖，构建时间从 20 秒变成 5 分钟。
4. **不要 `COPY . .`**。会把 `.env`、`.git`、测试数据一起打进镜像。用 `.dockerignore` 显式排除。
5. **不要把 `--reload` 带进镜像**。它会启文件监听，既浪费资源又是安全风险。
:::

## 六、部署形态矩阵

| 形态 | 命令 / 配置 | 适用 | 关键取舍 |
| --- | --- | --- | --- |
| **开发** | `uvicorn app.main:app --reload` | 本机 | 单进程、热重载，**不可用于生产** |
| **单机生产** | `gunicorn -k uvicorn.workers.UvicornWorker -w N` | 虚机 / 单容器 | 进程托管的健壮性（worker 挂了自动重启） |
| **K8s Deployment** | 见下方 YAML | 主力形态 | 探针配置决定滚动更新质量 |
| **Serverless / 容器实例** | 平台托管 | 流量波动大的场景 | 冷启动；需控制依赖体积与启动耗时 |
| **CPU 密集任务** | **独立进程 / 任务队列** | 报表、图像处理 | 不能放在 Web 进程里（会阻塞事件循环） |

```yaml [deploy/k8s/deployment.yaml]
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0            # 先起新的再停旧的，保证容量不掉
  template:
    spec:
      terminationGracePeriodSeconds: 45
      containers:
        - name: api
          image: registry.example.com/shop-api:sha-abc1234
          ports:
            - { name: http, containerPort: 8000 }
            - { name: metrics, containerPort: 9090 }
          envFrom:
            - secretRef: { name: shop-api-secrets }
          readinessProbe:
            httpGet: { path: /ready, port: http }
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet: { path: /health, port: http }
            initialDelaySeconds: 15
            periodSeconds: 10
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["sh", "-c", "sleep 8"]    # 等端点摘除完成
          resources:
            requests: { cpu: "200m", memory: "256Mi" }
            limits:   { cpu: "1000m", memory: "512Mi" }
```

::: warning 说明：`preStop` 的 `sleep 8` 不是可选项
K8s 删除 Pod 时，`SIGTERM` 发送与 Endpoint 摘除是**并发**进行的，不保证先摘后停。此时若进程立刻开始拒绝新请求，而调用方还没收到端点更新，就会有一小批 5xx。`preStop` 的 `sleep` 让容器**继续正常服务几秒**，覆盖端点传播的窗口。这个值与 Python 服务的优雅停止能力配合使用——Gunicorn 的 `--graceful-timeout 30` 给的是处理存量请求的时间。
:::

## 七、可验证步骤（照着做）

```shell
# 1. 本地起依赖与迁移
docker compose -f deploy/docker-compose.yml up -d
alembic upgrade head

# 2. 起服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
# 期望日志：Application startup complete.

# 3. 探针语义验证（关键：停 Redis 后只有 ready 变红）
curl -s -o /dev/null -w 'health=%{http_code}\n' http://127.0.0.1:8000/health   # 期望 200
curl -s -o /dev/null -w 'ready=%{http_code}\n'  http://127.0.0.1:8000/ready    # 期望 200
docker stop deploy-redis-1
sleep 2
curl -s -o /dev/null -w 'health=%{http_code}\n' http://127.0.0.1:8000/health   # 期望仍 200
curl -s -o /dev/null -w 'ready=%{http_code}\n'  http://127.0.0.1:8000/ready    # 期望 503
docker start deploy-redis-1

# 4. 创建订单 + 幂等
curl -s -X POST http://127.0.0.1:8000/order/create \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: k-001' \
  -d '{"user_id":1,"sku_id":1,"quantity":2}'
curl -s -X POST http://127.0.0.1:8000/order/create \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: k-001' \
  -d '{"user_id":1,"sku_id":1,"quantity":2}'
# 期望：两次返回同一个 order_id

# 5. 确认幂等的最终判据（数据库只有一行）
docker exec -i deploy-mysql-1 mysql -uroot -ppass shop \
  -e "SELECT COUNT(*) FROM t_order WHERE idem_key='k-001';"
# 期望：1

# 6. 镜像构建与体积
docker build -f deploy/Dockerfile -t shop-api:dev .
docker images shop-api:dev --format '{{.Size}}'
# 期望：< 250 MB

# 7. 容器内跑起来 + 指标
docker run --rm -d --name api -p 8000:8000 -p 9090:9090 \
  -e DB_URL='mysql+asyncmy://root:pass@host.docker.internal:3306/shop' \
  -e JWT_SECRET=dev-secret shop-api:dev
curl -s http://127.0.0.1:9090/metrics | grep -E '^http_requests_total' | head
```

::: danger 注意：第 3 步是最容易「以为自己做了其实没做」的一步
很多人写了 `/ready` 但也顺手查了 DB 到 `/health` 里，本地测起来「都返回 200」，看起来没问题。**必须真的把依赖停掉观察**：如果 `/health` 也变 503，K8s 会把所有副本一起重启——依赖抖动会直接升级成服务全挂。
:::

## 八、压测与排错

### 压测

```shell
# 先打同步版本建立基线，再对比 async 版本
hey -z 60s -c 50 -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: bench-$(date +%s)' \
  -m POST -d '{"user_id":1,"sku_id":1,"quantity":1}' \
  http://127.0.0.1:8000/order/create
```

### 排错速查

| 现象 | 高概率原因 | 定位手段 |
| --- | --- | --- |
| 并发上不去、所有请求一起慢 | `async def` 里有同步阻塞 | 压测期间 `time curl :8000/health`；若也慢 → 事件循环被占 |
| 容器日志看不到 | `PYTHONUNBUFFERED` 未设，输出被缓冲 | 加环境变量；或用 `python -u` |
| 镜像 1 GB+ | 单阶段构建，编译工具链进了运行镜像 | 改多阶段；加 `.dockerignore` |
| 滚动更新零星 5xx | `preStop` 缺失 / `readinessProbe` 不查依赖 | 看 5xx 与发布时间的相关性 |
| `Too many connections` | 连接池 × 副本数 > DB 上限 | 算端到端预算；调 `db_pool_size` |
| 指标接口把 Prometheus 打挂 | `path` 标签用了原始 URL，基数爆炸 | 改路由模板；查 `prometheus_tsdb_head_series` |
| 内存持续上涨 | 全局缓存无上限 / 循环引用 | 用 `tracemalloc` 或 `objgraph` 对比两次快照 |

### 内存排查的最小流程

```python
# 在 /debug/{token}/mem 端点里手动触发（仅内网、仅临时开启）
import tracemalloc, linecache

@router.get("/debug/{token}/mem")
async def mem(token: str, limit: int = 15):
    if token != settings.debug_token:
        raise HTTPException(404)
    if not tracemalloc.is_tracing():
        tracemalloc.start(25)
    snap = tracemalloc.take_snapshot()
    top = snap.statistics("lineno")[:limit]
    out = []
    for st in top:
        f = st.traceback[0]
        out.append({"file": f"{f.filename}:{f.lineno}",
                    "line": linecache.getline(f.filename, f.lineno).strip(),
                    "size_kb": round(st.size / 1024, 1),
                    "count": st.count})
    return out
```

::: tip 快照要采两次才有意义
单次快照只告诉你「谁占内存多」（很可能就是正常的数据缓存）。**两次快照做差值**（`snap2.compare_to(snap1, "lineno")`）才能区分「一直在涨的泄漏」与「一次分配后稳定的缓存」。间隔取 10 分钟，间隔内打同样强度的流量。
:::

## 参考资料

- [FastAPI 官方：部署概念（含 Gunicorn + uvicorn worker）](https://fastapi.tiangolo.com/deployment/concepts/)
- [uvicorn 官方：Deployment](https://www.uvicorn.org/deployment/)
- [Gunicorn 官方：Settings 全量说明](https://docs.gunicorn.org/en/stable/settings.html)
- [pydantic-settings 官方文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [prometheus_client：Python 客户端](https://prometheus.github.io/client_python/)
- [Kubernetes：Pod 生命周期与探针](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Docker 官方：多阶段构建](https://docs.docker.com/build/building/multi-stage/)

## 相关页面

- [框架选型：FastAPI / Django / Flask](../Overview/index.md) —— 部署形态影响选型
- [FastAPI 进阶：类型、异步与依赖注入](../FastAPI/index.md) —— 本篇里 `get_db` 与 lifespan 的展开
- [数据层：SQLAlchemy 2.0 与 Alembic](../DataLayer/index.md) —— 迁移在部署流水线里的位置
- [Go 微服务实战](../../GoMicroservices/Practice/index.md) —— 同场景的另一套实现与验收口径
- [Docker](../../../Ops/Docker/index.md) —— 多阶段构建与镜像瘦身
- [Kubernetes](../../../Ops/Kubernetes/index.md) —— 探针、滚动更新与资源限制
- [性能测试](../../../../project/Base/BackendTemplate/PerformanceTest/index.md) —— 容量拐点的完整方法论
