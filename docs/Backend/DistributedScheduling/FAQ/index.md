# 常见问题与分诊

这一页按「症状」组织，而不是按知识点。遇到问题先查第一节的分诊表，再去看对应章节。

::: tip 一句话理解
定时任务的排查顺序永远是：**这一次该不该跑 → 有没有跑的记录 → 跑了几次 → 跑的结果对不对**。绝大多数人从第四步开始查，于是永远查不到根因。
:::

## 一、症状分诊表

| 症状 | 最可能的原因 | 先查什么 | 去哪一页 |
| --- | --- | --- | --- |
| 任务完全没跑 | 被暂停 / 时区差 8 小时 / 表达式段数不对 | `job_registry.enabled`、`tz`、表达式段数 | [Cron 语义](../CronSemantics/index.md) |
| 每天只差一点时间 | 用 `fixedRate` 冒充 cron | 注解类型 | [总览](../Overview/index.md) |
| 某一天没跑 | DST 跳变窗口 | 那天的本地时刻是否存在 | [Cron 语义](../CronSemantics/index.md) |
| 跑两次 | 认领无条件更新 / 双主 | `job_run` 里同一 `fire_time` 的行数 | [调度内核](../SchedulerCore/index.md) |
| 停机后下游被打挂 | 全量补跑无上限 | `is_backfill=true` 的数量 | [misfire 与补跑](../MisfireCatchup/index.md) |
| 数据翻倍 | 重复执行 + 非幂等副作用 | 幂等键是否存在 | [幂等与重试](../IdempotentRetry/index.md) |
| 任务卡在 `running` | 租约未回收 / 执行卡死 | `locked_until` | [调度内核](../SchedulerCore/index.md) |
| 下游一直 `blocked` | 上游永久失败 / 判定用「最新上游」 | 屏障表 | [依赖编排](../DagDependency/index.md) |
| 看板全绿但数据少 | 只监控失败数 | `last_success_at` | [可观测](../Observability/index.md) |
| 补跑越多缺口越大 | 时间窗用了 `now()` | 任务函数签名 | [misfire 与补跑](../MisfireCatchup/index.md) |

## 二、十二个高频问题

### 1. 为什么本地跑得好好的，上线就双跑？

因为本地只有一个进程。**「只有一个执行者」是单机环境免费送的**，集群里必须自己买：条件更新（认领）+ 选主/分片。见 [调度内核](../SchedulerCore/index.md)。

### 2. `@Scheduled` 和 Quartz 该选哪个？

| 场景 | 选择 |
| --- | --- |
| 单实例、任务少、不需要补跑 | `@Scheduled` 够用 |
| 多实例、需要「只跑一次」 | Quartz 集群（`JDBCJobStore`）或 XXL-JOB |
| 需要可视化管理和手动触发 | XXL-JOB / 调度平台 |
| 需要 DAG 依赖 | Airflow / 自研 DAG |

`@Scheduled` 在多实例下**每个实例都会跑**——这不是 bug，是它的语义。

### 3. cron 表达式到底该写 5 段还是 6 段？

看平台：Linux crontab / K8s 是 **5 段**（无秒），Spring / Quartz / XXL-JOB 是 **6 段**（秒在前）。跨平台复制前先数段数，K8s 会直接拒绝 6 段。

### 4. 为什么「每月最后一天」不能用 `31`？

因为 2 月没有 31 日，4/6/9/11 月也没有。用 `31` 一年只跑 **7 次**（实测）。要用 `L`（Quartz）或服务端计算月末日期。见 [Cron 语义](../CronSemantics/index.md)。

### 5. 停机 3 小时后，补跑会不会把数据库打挂？

取决于「补跑次数 × 单次耗时 / 并发」。1 分钟周期、单次 30 秒、并发 4 时，3 小时缺口要补 180 次、耗时 **22.5 分钟**，期间正常任务还在到达。必须设补跑上限。见 [misfire 与补跑](../MisfireCatchup/index.md)。

### 6. `misfireThreshold` 设多少？

Quartz 默认 **60 s**。它表示「迟到超过 60 秒才算 misfire」——设太小会把正常的调度抖动判成 misfire（然后触发补跑），设太大则真停机时补不回来。经验值：**2~3 个调度周期**。

### 7. 为什么 K8s CronJob 突然不跑了？

最常见三个原因：

1. `concurrencyPolicy: Forbid` 且上一个 Job 卡在 `Pending`/`Running`（例如镜像拉不下来），后续全部跳过。
2. 错过次数 > 100 且没设 `startingDeadlineSeconds`，控制器停止调度。
3. 没设 `timeZone`，按 UTC 跑，与你预期的本地时间差 8 小时。

### 8. 任务需要「上一次结束后再跑」怎么写？

用 `fixedDelay`（Spring）或 `concurrencyPolicy: Forbid`（K8s）。**不要用 cron 表达这个语义**——cron 不知道上一次有没有结束。

### 9. 分布式锁和调度器选主是一回事吗？

不是。锁是「互斥原语」，选主是「用锁实现的角色分配」。调度器选主还要额外解决 **fencing**：旧主恢复后不能再写。见 [高可用](../LeaderSharding/index.md)。

### 10. 为什么补跑的数据是错的？

因为任务内部用 `now()` 算时间窗。补跑必须把 `fire_time` 传进任务，用 `fire_time` 推导窗口。这是本专题出现频率最高的一条约束。

### 11. 幂等键用 `fire_time` 还是业务键？

- 防「同一次跑两遍」→ `(job_key, fire_time)`
- 防「两次不同触发产生同一效果」→ 业务键（如 `(tenant, biz_date)`）

L1 任务（计费、配额）**两个都要**。见 [实战](../Practice/index.md) 的 T3 踩坑。

### 12. 定时任务要不要拆成消息队列？

当满足以下任一条件时考虑拆：单次执行超过周期的一半、需要重试与死信、需要削峰、需要跨语言消费。否则定时任务 + 数据库队列足够，**多一个中间件就多一个半夜会挂的东西**。

## 三、五个「听起来对」的错误建议

| 建议 | 为什么错 |
| --- | --- |
| 「加个 `synchronized` 就不会重复执行了」 | 只在单 JVM 内有效，多实例无效 |
| 「用 Redis 锁包住任务就安全了」 | 锁过期后旧执行者还在跑 → 需要 fencing |
| 「任务写成幂等的就不用管重复触发了」 | 重复执行本身仍然消耗资源、放大下游调用 |
| 「补跑多一点没关系，反正幂等」 | 幂等只保证结果，不保证下游配额与限流不被击穿 |
| 「日志里有 `start` 就说明跑了」 | 日志轮转后无法证明；必须有事实表 |

## 四、上线前 14 项自查

| # | 检查项 | 通过标准 |
| --- | --- | --- |
| 1 | 每个任务声明语义（时间点/间隔/事件/依赖） | 登记表无空值 |
| 2 | 时区显式（IANA 名） | `grep -r "systemDefault\|timeZone"` 无隐式 |
| 3 | 表达式段数与平台匹配 | 5 段给 K8s、6 段给 Spring |
| 4 | 认领语句带 `AND state='pending'` | 代码评审确认 |
| 5 | 幂等键落库且有唯一索引 | `\d job_run` 看到主键 |
| 6 | 补跑策略与上限已配置 | 登记表有两列 |
| 7 | 任务函数接受 `fire_time` | 签名检查 |
| 8 | 租约 ≥ 执行时长 p99 × 2 | 有 p99 数据 |
| 9 | `last_success_at` 有指标与告警 | 面板可见 |
| 10 | 调度器心跳有 P1 告警 | 停一次验证 |
| 11 | 双实例启动不产生重复执行 | 验收用例 S7 |
| 12 | 补跑不污染统计（`is_backfill`） | 查询可分组 |
| 13 | L1 任务有日终对账且返回 0 行 | 对账 SQL 可执行 |
| 14 | 人工重跑必须指定 `fire_time` | CLI 参数存在 |

## 五、本页判据

本页判据族 `DSQ-A` ~ `DSQ-H`，共 8 条。

| 编号 | 判据 | 判定方式 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `DSQ-A` | 分诊表覆盖「没跑/跑两次/跑错数据」三类 | 查文档 | 补症状 |
| `DSQ-B` | 每个高频问题都有「怎么验证」而不只是解释 | 逐条检查 | 补验证方式 |
| `DSQ-C` | 「错误建议」表至少 5 条且有原因 | 查文档 | 补 |
| `DSQ-D` | 上线自查 ≥ 12 项，且每项可机械判定 | 逐项执行 | 补可执行判据 |
| `DSQ-E` | 自查项覆盖幂等、防重、补跑、观测四类 | 查清单 | 补缺类 |
| `DSQ-F` | 引用的相邻页链接全部有效 | `linkcheck` | 修链接 |
| `DSQ-G` | 常见问题里的阈值与正文一致 | 交叉核对 | 统一 |
| `DSQ-H` | 有「什么时候该拆到消息队列」的判断条件 | 查文档 | 补条件 |

## 六、验证：把自查项变成可执行检查

```shell
# 1) 找出没有显式时区的调度代码（Spring 场景）
grep -rn "@Scheduled" --include=*.java src/ | grep -v "zone" || echo "OK: 未见无 zone 的 @Scheduled"

# 2) 找出认领语句里缺少 state 条件的 SQL
grep -rn "SET state *= *'running'" --include=*.sql --include=*.java . | grep -v "state *= *'pending'" \
  || echo "OK: 认领语句均带 state 条件"

# 3) 找出用 now()/today() 算窗口的任务
grep -rn "now()\|LocalDate.now()\|date.today()" --include=*.java --include=*.py src/ \
  || echo "OK: 未发现直接取当前时间的任务"
```

预期输出（干净项目）：

```text
OK: 未见无 zone 的 @Scheduled
OK: 认领语句均带 state 条件
OK: 未发现直接取当前时间的任务
```

三条 `grep` 不能替代代码评审，但能在 3 秒内抓出「最常犯的三类错误」——比等一次线上事故便宜得多。

## 七、参考资料

- [Quartz 配置参考（`misfireThreshold` 等）](https://www.quartz-scheduler.org/documentation/quartz-2.5.x/configuration/)
- [Kubernetes CronJob 限制与注意事项](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/#cron-job-limitations)
- [总览：四种触发语义与五个必失点](../Overview/index.md)
- [可观测：五个口径与静默停摆](../Observability/index.md)
