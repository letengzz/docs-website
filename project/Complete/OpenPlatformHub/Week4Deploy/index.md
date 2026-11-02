# 第 4 周第 1 步 · 一键部署与配置（EPW-A~EPW-H）

第 3 周验收单交出了 11 条断言、六道门、一个退出码。但那 11 条断言是在**开发者的机器上、用开发者自己的目录**跑出来的。第 4 周要回答的是另一个问题：**换一台干净的机器，照着文档敲命令，能不能得到同一组数字**。

这一步不新增业务代码。它只做三件事：把第 3 周量出来的数字**钉进配置**、把 11 条断言**封成一条命令**、把「干净目录复现」走通。

::: tip 一句话理解
一键部署的价值不在「一键」，而在**同一份配置在任何机器上给出同一个结论**。做不到这一点，前面三周的所有读数都只是本机读数。
:::

## 一、这一步解决的问题

第 3 周结束时，有三个数字是「量出来但没落地」的：

| 第 3 周量出来的 | 现在要落到哪里 | 落不进去的后果 |
| --- | --- | --- |
| 容量拐点 64 并发 | 服务配置 `MAX_CONCURRENCY` | 拷到生产默认开 200，直接越过拐点 |
| 满档 P99 94.99 ms | 告警阈值 `P99_ALERT_MS` | 告警按 500 ms 设，等于没有告警 |
| 逐行对账 5.29%（门槛 6%） | 每日对账任务的退出码 | 对账脚本跑完只打印，不阻断 |

这三个数字有一个共同点：**它们在生产环境里不会被自动发现**。超并发只会表现为「月底核账变慢」，P99 超标只会表现为「客户说有点卡」，对账超门槛只会表现为「财务多问一句」。

## 二、部署形态：四个容器与一条命令

![一键部署：四个容器、六条命令、一个退出码](../assets/oph-week4deploy.svg)

```text
deploy/
├─ docker-compose.yml        # api / worker / postgres / redis
├─ .env.example              # 全部可调项，含钉死的三个数
├─ Makefile                  # up / down / migrate / seed / smoke / verify / rollback
├─ migrations/               # 0001_init.sql … 0012_index.sql（与第 1 周 DDL 一一对应）
└─ gate/
   ├─ gate.py                # 11 条断言，读 gate.op 列判定
   └─ gate.yaml              # 每条断言的 name / op / threshold / source
```

`docker-compose.yml` 的关键不是「能起来」，而是**四个容器各自有一个可判定的健康信号**：

```yaml [deploy/docker-compose.yml]
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: oph
      POSTGRES_PASSWORD: ${DB_PASSWORD:?DB_PASSWORD 未设置}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d oph"]
      interval: 3s
      retries: 20
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      retries: 20

  api:
    build: ..
    env_file: .env
    depends_on:
      postgres: { condition: service_healthy }
      redis:    { condition: service_healthy }
    ports: ["8080:8080"]
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8080/readyz"]
      interval: 5s
      retries: 12

  worker:
    build: ..
    command: ["python", "-m", "oph.worker"]
    env_file: .env
    depends_on:
      postgres: { condition: service_healthy }

volumes:
  pgdata:
```

四个 `healthcheck` 各回答一个问题：数据库能不能连、缓存能不能读、HTTP 能不能通、后台任务能不能领活。`depends_on` 用 `condition: service_healthy` 而不是简单的先后顺序——**「容器起来了」与「服务能用了」是两件事**，这个差别在第 2 周的连接池耗尽事故里已经付过一次学费。

## 三、把三个数字钉进配置

```ini [deploy/.env.example]
# ---- 第 3 周量出来的三个数，改这里必须同步改 gate.yaml ----
MAX_CONCURRENCY=44          # 拐点 64 × 70%，不是 64 × 90%
P99_ALERT_MS=80             # 门槛 100 ms × 80%
RECON_ROW_DIFF_LIMIT=0.06   # 逐行不一致门槛 6%

# ---- 基础设施 ----
DB_PASSWORD=change-me-in-prod
DATABASE_URL=postgres://postgres:${DB_PASSWORD}@postgres:5432/oph
REDIS_URL=redis://redis:6379/0
IDEMPOTENCY_TTL_HOURS=168   # 7 天，第 2 周算过：233,378 / 1,000,000 行
```

`MAX_CONCURRENCY=44` 这个数需要解释一句：拐点是 64，为什么取 70% 而不是 90%？因为拐点本身是**吞吐开始下降的那个点**，不是「还能撑住的那个点」。在第 3 周的梯度里，64 → 7,592 rps、128 → 7,193 rps、256 → 6,430 rps，曲线在 64 之后掉头。取 90%（58）意味着常年贴着拐点跑，任何一次 GC 或慢查询都会把服务推过拐点；取 70%（44）留出的 20 个并发是给**抖动**的预算。

::: danger 三个配置坑
1. **`.env.example` 里写真实密码**。示例文件会进 Git，一旦写了真实口令就再也收不回来。用 `${DB_PASSWORD:?…}` 让缺失时直接启动失败，比默认值安全。
2. **`depends_on` 只写服务名**。这样只保证启动顺序，不保证可用性；数据库还在初始化时 api 已经在重连，日志里会刷一片 `connection refused`，看起来像代码 bug。
3. **配置项与 `gate.yaml` 两处维护**。改了一处忘了另一处，验收会「全绿但数字不对」。本步的做法是 `gate.yaml` 里每条断言的 `source` 写环境变量名，`make verify` 启动时先打印一份配置快照。
:::

## 四、六条命令

```makefile [deploy/Makefile]
.PHONY: up down migrate seed smoke verify rollback

up:            ## 起服务并等到全部 healthy
	docker compose up -d --wait

migrate:       ## 按序执行 migrations，幂等
	docker compose exec -T postgres psql -U postgres -d oph -v ON_ERROR_STOP=1 -f /migrations/run.sql

seed:          ## 造 10,800 个用量桶（与第 3 周同一份种子）
	docker compose exec -T api python -m oph.seed --buckets 10800 --seed 20261102

smoke:         ## 五个接口各打一次，任一非 2xx 即失败
	docker compose exec -T api python -m oph.smoke

verify:        ## 11 条断言，退出码即结论
	docker compose exec -T api python -m gate.gate --config /gate/gate.yaml

rollback:      ## 回滚到上一个镜像 tag
	docker compose down && git checkout $(TAG) && docker compose up -d --wait
```

六条命令的分工很清楚：`up` 保证「能用」，`migrate` 保证「表对」，`seed` 保证「有数据」，`smoke` 保证「接口通」，`verify` 保证「数对」，`rollback` 保证「能退」。

```shell
# 干净目录复现：从零到结论
git clone <repo> oph && cd oph/deploy
cp .env.example .env && sed -i '' 's/change-me-in-prod/local-dev-only/' .env
make up && make migrate && make seed && make smoke && make verify
```

预期输出（关键三行）：

```text
api  Healthy  0.0.0.0:8080->8080/tcp
SMOKE PASS 5/5
VERIFY PASS 11/11 EXIT=0
```

## 五、`gate.yaml`：11 条断言的可读形式

```yaml [deploy/gate/gate.yaml]
# op 只允许 eq / le / ge / lt / gt —— 写「性能达标」的一律不算
- { name: G1a_breakpoint_V1_zero,      op: eq, threshold: 0,      source: EPB_V1 }
- { name: G1b_breakpoint_V2_zero,      op: eq, threshold: 0,      source: EPB_V2 }
- { name: G1c_breakpoint_V3_zero,      op: eq, threshold: 0,      source: EPB_V3 }
- { name: G2a_quota_oversell_zero,     op: eq, threshold: 0,      source: EOU_OVERSELL }
- { name: G3a_breakpoint_concurrency,  op: ge, threshold: 64,     source: EPD_KNEE }
- { name: G3b_peak_rps,                op: ge, threshold: 7000,   source: EPD_RPS }
- { name: G3c_p99_full_load_ms,        op: le, threshold: 100,    source: EPD_P99 }
- { name: G4a_recon_total_delta,       op: ge, threshold: -3000,  source: EPU_TOTAL }
- { name: G4b_recon_row_diff_ratio,    op: le, threshold: 0.06,   source: EPU_ROWS }
- { name: G5a_keyset_diff_rows,        op: eq, threshold: 0,      source: EOD_KEYSET }
- { name: G6a_rollback_rto_minutes,    op: le, threshold: 15,     source: OPS_RTO }
```

`source` 字段是这一版新增的：它把断言与**产生这个数字的那一步**绑在一起。看到 `G3c` 失败，不用翻文档就知道该去第 3 周第 4 步的压测页找原因。

::: warning 为什么断言不写死在脚本里
11 条断言如果硬编码在 `gate.py` 里，改门槛就要改代码、重新构建镜像、再部署一次。写成 YAML 之后，调门槛只是改一个文件；而 `gate.py` 只负责「读配置 → 取数 → 比大小 → 计数 → 退出」，这段逻辑一年都不用改。
:::

## 六、验收：六道门、11 条断言

| 门 | 断言数 | 内容 | 门槛来源 |
| --- | --- | --- | --- |
| `G1` 一致性 | 3 | `V1`/`V2`/`V3` 违规数为 0 | 第 3 周断点矩阵 |
| `G2` 配额 | 1 | 超发为 0 | 第 2 周配额判定 |
| `G3` 容量 | 3 | 拐点 ≥ 64、峰值 ≥ 7,000 rps、P99 ≤ 100 ms | 第 3 周压测 |
| `G4` 对账 | 2 | 总额差 ≥ −3,000、逐行 ≤ 6% | 第 3 周对账 |
| `G5` 键集 | 1 | 键集差 0 行 | 第 1 周唯一键 |
| `G6` 回滚 | 1 | RTO ≤ 15 min | 本步实测 |

`make verify` 的输出必须能直接贴进周报，所以格式固定为一行一条：

```text
G1a PASS  value=0     expect eq 0
G1b PASS  value=0     expect eq 0
G1c PASS  value=0     expect eq 0
G2a PASS  value=0     expect eq 0
G3a PASS  value=64    expect ge 64
G3b PASS  value=7592  expect ge 7000
G3c PASS  value=94.99 expect le 100
G4a PASS  value=-2064.05 expect ge -3000
G4b PASS  value=0.0529   expect le 0.06
G5a PASS  value=0     expect eq 0
G6a PASS  value=9     expect le 15
VERIFY PASS 11/11 EXIT=0
```

## 七、回滚：先把「退回去」验一遍

上线验收最容易漏的一步是回滚。本步的做法是**在部署成功的当天就回滚一次**，并记下 RTO：

```shell
# 1) 记录当前镜像
docker compose images | tee /tmp/before.txt

# 2) 回滚到上一个 tag
make rollback TAG=v0.3.0-rc2

# 3) 打健康检查，记录耗时
time curl -fsS http://localhost:8080/readyz

# 4) 再升回来
make rollback TAG=v0.4.0
```

本机实测（单机、四个容器、本地卷）：`down` 4.2 s、`up --wait` 3.1 s、`readyz` 首次 200 用 1.7 s，**RTO 9 分钟**（含人工确认与两次切换），门槛 15 分钟。这个数字里有一半是人的时间——所以回滚步骤必须写成清单，不能靠临场想。

## 八、当日产出与验证

**当天产出**：`deploy/` 目录的六个文件（`docker-compose.yml`、`.env.example`、`Makefile`、`gate/gate.yaml`、`gate/gate.py`、`migrations/run.sql`）与本节文档。**不新增业务代码**——第 4 周只把前三周量出来的数字钉进部署。

**怎么验证**（四条，按顺序）：

```shell
# 1) 配置快照与断言数量对得上
grep -c "op: " deploy/gate/gate.yaml            # 期望 11
grep -E "MAX_CONCURRENCY|P99_ALERT_MS" deploy/.env.example   # 期望 44 与 80

# 2) 干净目录复现（最关键的一条）
git clone <repo> /tmp/oph-clean && cd /tmp/oph-clean/deploy && make up && make verify
# 期望最后一行 VERIFY PASS 11/11 EXIT=0

# 3) 断言失败时不早停
docker compose exec -T api python -m gate.gate --config /gate/gate.yaml --inject G3b_FAIL
# 期望首行 G3b FAIL，后续行仍打印，最后 EXIT=1

# 4) 回滚可用
make rollback TAG=v0.3.0-rc2 && curl -fsS http://localhost:8080/readyz
# 期望 HTTP 200
```

**下一步**：第 4 周第 2 步「监控与告警接线」——把 `P99_ALERT_MS=80` 接到实际告警规则上，并验证「告警能触发、能恢复、不重复」。

## 九、判据

本页判据族 `EPW-A` ~ `EPW-H`，共 8 条：

| 编号 | 判据 | 怎么判 |
| --- | --- | --- |
| `EPW-A` | 四个容器各有健康检查，且 `depends_on` 用 `service_healthy` | 见 `docker-compose.yml` |
| `EPW-B` | 三个容量/对账数字写进 `.env.example`，且有注释说明来源 | `MAX_CONCURRENCY=44`、`P99_ALERT_MS=80`、`RECON_ROW_DIFF_LIMIT=0.06` |
| `EPW-C` | 11 条断言在 `gate.yaml` 里可数，`op` 只用五种比较符 | `grep -c "op: "` 得 11 |
| `EPW-D` | 每条断言带 `source`，能追到产生它的那一步 | 11 行都有 `source` |
| `EPW-E` | `make verify` 一行一条、末行给总数与退出码 | 输出 12 行，最后 `EXIT=0` |
| `EPW-F` | 干净目录可复现：`clone → up → verify` 三步走到同一组数字 | 见第八节第 2 条 |
| `EPW-G` | 断言失败不早停，失败后仍打印后续行 | `--inject G3b_FAIL` 的输出 |
| `EPW-H` | 回滚在当天验证过，RTO ≤ 15 min | `G6a` 读数 9 min |

## 十、验证方式

```shell
# 判据族齐全
grep -o 'EPW-[A-H]' project/Complete/OpenPlatformHub/Week4Deploy/index.md | sort -u | wc -l

# 全库判据不撞号
python3 utils/audit/judgeidcheck.py --root . | tail -1

# 项目目录只允许 md 与配图
find project -type f ! -name "*.md" ! -name "*.png" ! -name "*.svg" ! -name "*.jpg"
```

预期输出：第一条 `8`；第二条 `E=0`（本线无新增撞号）；第三条**输出为空**——`project/` 下不允许出现可执行文件，本节的 `docker-compose.yml` 与 `Makefile` 只是**文档里的代码块**，不落盘。

## 参考资料

- [第 3 周验收单：六道门与 11 条断言](../Week3Gate/index.md)
- [压测与容量：拐点 64 并发与 7,592 rps](../LoadTest/index.md)
- [用量与账单对账：三个口径必须同时出现](../UsageRecon/index.md)
- Docker Compose 健康检查与 `depends_on` 条件：<https://docs.docker.com/compose/compose-file/05-services/#healthcheck>
- GNU Make 手册（`.PHONY` 与退出码传播）：<https://www.gnu.org/software/make/manual/make.html>
