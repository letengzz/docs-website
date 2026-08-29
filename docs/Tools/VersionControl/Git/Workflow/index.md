# Git 协作工作流

多人协作不是「会用命令」就行，而是约定：分支怎么开、提交怎么写、PR 怎么合、冲突怎么解。本节给出一套可直接落地的协作规范。

::: info 适用版本
以下内容基于 GitHub/GitLab/Gitee 的通用能力；命令适用于 Git 2.2x+。
:::

## 标准协作流程

```text
1. 从 main 拉最新 → 开功能分支
2. 小步提交，遵循提交规范
3. 推送分支 → 开 Pull Request / Merge Request
4. CI 自动检查 → 至少 1 人 Review
5. 通过后合并 → 删除功能分支
```

## 提交规范：Conventional Commits

```text
<type>(<scope>): <description>
```

常用类型：

| 类型 | 场景 |
| --- | --- |
| `feat` | 新功能 |
| `fix` | 缺陷修复 |
| `docs` | 文档 |
| `refactor` | 重构（不改变行为） |
| `test` | 测试 |
| `chore` | 构建、配置、依赖 |
| `perf` | 性能优化 |

示例：

```text
feat(auth): 支持邮箱登录
fix(payment): 修复超时未回调问题
docs(git): 补充协作工作流章节
```

配合工具：`commitlint` 校验格式、`husky` 拦截提交、`commitizen` 生成规范提交。

## PR 描述模板

建议包含：

1. 背景：为什么做。
2. 改动：改了什么模块。
3. 测试：怎么验证、测试结果。
4. 截图/演示（前端）。
5. 关联：issue 链接。

## 代码审查要点

- 功能正确性、边界条件。
- 命名与可读性。
- 是否有重复代码。
- 是否缺测试。
- 安全与性能风险。

Review 意见用「问题 + 建议」表述，避免人身化；阻塞性问题标 Blocking。

## 合并策略

| 策略 | 历史效果 | 适合 |
| --- | --- | --- |
| Merge commit | 保留合并节点 | 团队想看「何时合并」 |
| Squash and merge | 一个 PR 一个提交 | 功能分支提交杂乱时 |
| Rebase and merge | 线性历史 | 追求整洁历史 |

推荐：功能分支用 **Squash and merge**，`main` 保持线性、每个提交可回滚。

## 冲突解决

```shell
# 拉取最新 main 并合并到功能分支
git switch feature/xxx
git fetch origin
git merge origin/main

# 或变基
git rebase origin/main
```

解决冲突的原则：

- 先理解双方意图，再决定保留哪边。
- 不要盲目「以我为准」或「以他为准」。
- 解决后跑测试再提交。

## 分支保护与 CI

在 `main` 上开启：

- 禁止直推。
- 要求 PR。
- 要求 CI 通过（lint、测试、构建）。
- 要求至少 1 人 Review。
- 禁止 force push。

## 团队规范落地清单

- [ ] 分支命名规范写入 README/AGENTS
- [ ] 提交规范接入 commitlint + husky
- [ ] PR 模板已配置
- [ ] main 分支保护已开启
- [ ] CI 覆盖 lint / test / build
- [ ] 每周复盘冲突与合并问题

## 易错点

::: danger 常见错误
1. 提交信息随意（`update`、`fix bug`），无法回溯。
2. 功能分支与 main 脱节太久，合并时冲突爆炸。
3. PR 没有 Review 就合并，质量完全靠自觉。
4. 直接往 main 推送，绕过所有检查。
5. 合并后不删除分支，仓库堆满几十个 feature 分支。
6. 冲突时直接 `--ours`/`--theirs` 全选，把对方代码静默覆盖。
:::

## 验证方式

1. 配置 commitlint 后，非法提交信息被 husky 拦截。
2. 提交一个 PR，确认 CI 与 Review 流程都走通。
3. 合并后用 `git log --oneline` 确认 main 历史符合约定。
4. 模拟冲突，按流程解决并跑通测试。

## 相关专题

- [CI/CD 专题](../../../CICD/index.md)：提交与 MR 如何自动触发流水线（GitHub Actions / GitLab CI / Jenkins）
- [Git 分支模型](../BranchModel/index.md)：与 CI/CD 分支策略配合的分支规范

## 参考资料

- Conventional Commits：https://www.conventionalcommits.org/zh-hans/
- GitHub 协作文档：https://docs.github.com/zh/pull-requests
- GitLab Merge Request：https://docs.gitlab.com/ee/user/project/merge_requests/
