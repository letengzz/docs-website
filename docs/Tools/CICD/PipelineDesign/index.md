# 流水线设计最佳实践

流水线不是“把命令串起来”就行。设计糟糕的流水线：跑 40 分钟、失败原因不明、dev 与 prod 产物不一致、并发互相踩踏。本页给出阶段划分、并行、缓存、门禁、失败处理、环境治理的完整设计方法，适用于 GitHub Actions / GitLab CI / Jenkins 任意平台。

## 设计目标

| 目标 | 指标 |
| --- | --- |
| 快速反馈 | 提交流水线 ≤ 10 分钟 |
| 高稳定性 | 非代码原因失败率趋近 0（依赖下载、环境漂移可控） |
| 可追溯 | 每个产物能对应到 commit 与构建日志 |
| 可回滚 | 任何环境都能一键回到上一个好版本 |
| 安全 | 密钥不外泄、第三方组件可审计 |

## 流水线分层

不要把所有东西塞进一条流水线，按触发时机拆成多条：

| 流水线 | 触发 | 内容 | 目标耗时 |
| --- | --- | --- | --- |
| PR 校验 | PR 更新 | Lint、单元测试、构建、覆盖率 | ≤ 10 分钟 |
| 主干流水线 | main 合并 | 全量测试、质量门禁、制品 | ≤ 15 分钟 |
| 发布流水线 | tag / 手动 | 构建发布版制品、部署 staging、冒烟 | 按需 |
| 生产部署 | 人工确认 | 部署 prod、健康检查、回滚预案 | 分钟级 |
| 夜间流水线 | cron | 全量回归、性能测试、依赖安全扫描 | 小时级 |

## 阶段划分模板

```text
check（静态检查）
  ↓
build（构建）
  ↓
test（单元 + 集成）
  ↓
quality（覆盖率 + 扫描）    ← 门禁，不通过阻断
  ↓
package（制品 + 镜像）
  ↓
deploy-staging → smoke → deploy-prod（人工/自动）
```

原则：

1. **阶段内并行、阶段间串行**：同一阶段的 Job 并行跑，提高吞吐。
2. **耗时操作后置**：全量测试放发布/夜间，提交流水线只跑关键路径。
3. **门禁唯一**：质量门禁只在一个阶段判定，避免多个 Job 各自设阈值导致口径不一。

## 加速技巧

| 技巧 | 收益 | 实现 |
| --- | --- | --- |
| 依赖缓存 | 减少 50%+ 时间 | npm ci --cache / maven 缓存 / actions/cache |
| 并行矩阵 | 多版本同时测 | matrix / parallel stages |
| 增量构建 | 只测变更模块 | 路径过滤（paths / only.changes） |
| 构建缓存 | 编译产物复用 | Gradle build cache、Webpack cache |
| 测试分片 | 按文件拆分并行 | split tests / sharding |
| 避免重装 | 复用预装运行时 | 官方镜像已带 Node/Maven |

## 失败处理策略

| 场景 | 策略 |
| --- | --- |
| 依赖下载失败（网络抖动） | 自动重试 1~2 次，指数退避 |
| 单元测试失败 | 立即阻断，发通知，附报告 |
| 部署中途失败 | 自动回滚到上一个版本 |
| 健康检查失败 | 视为部署失败，摘流量 + 回滚 |
| 非关键检查（如 lint 警告） | `allow_failure: true`，不阻断但记录 |
| 超时 | Job 级 `timeout` 兜底，防止挂起占资源 |

::: danger 重试陷阱
重试只适合**幂等**操作：依赖下载、构建。**部署/发消息/扣费类步骤禁止自动重试**，否则会重复执行产生事故；部署失败应走“回滚”而不是“重试”。
:::

## 环境治理

### 多环境配置

```yaml
variables:
  DEV_URL: https://dev.example.com
  STAGING_URL: https://staging.example.com
  PROD_URL: https://example.com
```

按环境选择：

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "main"'
    variables:
      TARGET_ENV: staging
  - if: '$CI_COMMIT_TAG'
    variables:
      TARGET_ENV: prod
```

### 数据隔离

- dev 用测试数据，绝不连生产库。
- staging 尽量用脱敏数据，验证真实行为。
- prod 部署后跑只读冒烟，不产生脏数据。

### 密钥按环境隔离

```text
DEV_TOKEN / STAGING_TOKEN / PROD_TOKEN 分别存储，生产密钥只授权生产 Job 使用。
```

## 制品与版本规范

制品命名统一：

```text
{应用名}-{主版本}.{次版本}.{补丁}-{构建号}-{commit短SHA}
示例：order-service-1.2.0-45-a1b2c3d.jar
```

镜像 Tag 规范：

```text
latest（最新，仅 dev 使用）
1.2.0-45-a1b2c3d（不可变，部署用）
```

::: warning 不要覆盖历史 Tag
同一 Tag 多次 push 会让“回滚”指向错误镜像。发布镜像必须不可变：一个 SHA 只对应一个镜像。
:::

## 通知与可观测

1. 成功/失败通知到 IM（钉钉/企微/Slack），失败附构建链接。
2. 构建指标（时长、成功率、排队时间）接入监控，趋势恶化提前处理。
3. 流水线日志集中检索（如 ELK），排查历史构建。

## 企业级设计清单

::: tip 流水线设计十问
1. 提交流水线 10 分钟内能完成吗？
2. 每个产物都能对应 commit 与构建号吗？
3. dev/staging/prod 用的是同一个制品吗？
4. 质量门禁在合并前强制执行了吗？
5. 生产部署有人工确认（或等价的安全机制）吗？
6. 部署失败会自动回滚吗？
7. 密钥都存平台密钥库，没进代码库吗？
8. 并发部署会被互斥拦截吗？
9. 失败通知会第一时间到责任人吗？
10. 有定期备份流水线配置与制品吗？
:::

## 易错点与最佳实践

::: danger 高频翻车点
1. **阶段拆太多太碎**：每个阶段只有一条命令，调度开销大于收益；按业务阶段合并。
2. **用 `sleep` 等部署完成**：应该轮询健康检查接口（curl --retry）或等待 Deployment 就绪。
3. **并发部署互踩**：生产部署要加锁/互斥（`concurrency` / lockable resources）。
4. **流水线配置不评审**：修改 CI 配置不走过 MR，出了事故无从追溯。
5. **忽略本地复现**：流水线失败只能线上看日志，应提供本地可执行的同一脚本。
:::

## 验证方式

1. 用计时工具统计提交流水线各阶段耗时，找出最长阶段优化。
2. 做一次“模拟部署失败”，确认自动回滚与通知全流程。
3. 并发触发两次生产部署，确认第二次被拦截或排队。
4. 检查制品仓库：同一 SHA 只有一份不可变制品。

## 参考资料

- GitHub Actions 最佳实践：https://docs.github.com/zh/actions/writing-workflows/choosing-what-your-workflow-does/optimizing-workflow-performance
- GitLab CI 流水线设计：https://docs.gitlab.com/ci/pipelines/pipeline_architectures.html
- Jenkins Pipeline 最佳实践：https://www.jenkins.io/doc/book/pipeline/best-practices/
- 持续交付原则：https://continuousdelivery.com/principles/
