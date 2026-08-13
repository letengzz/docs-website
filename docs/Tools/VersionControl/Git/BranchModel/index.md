# Git 分支模型

分支模型是团队协作的「交通规则」：主分支怎么保护、功能分支怎么命名、何时合并、怎么发布。本节对比三种主流模型并给出选择建议。

::: info 适用版本
分支模型与 Git 版本无关；以下命令适用于 Git 2.2x+。
:::

## 为什么要统一分支模型

没有统一规则时，团队容易出现：

- 直接在 `main` 提交，发布前才发现一堆半成品。
- 分支长期不合并，冲突爆炸。
- 没有人知道「当前哪个分支是可发布状态」。

## 三种主流模型

### 1. GitHub Flow（推荐多数团队）

```text
main（始终可发布）
  └── feature/xxx ── PR ──▶ main
```

规则：

- `main` 始终保持可部署。
- 新功能开 `feature/xxx` 分支。
- 通过 Pull Request 合并，合并前必须通过 CI 与 Code Review。
- 发布频率高时直接从 `main` 部署。

适合：持续部署的 Web 项目、中小团队。

### 2. Git Flow（适合版本化发布）

```text
main（发布历史）
  ├── develop（集成分支）
  │     ├── feature/xxx
  │     └── release/x.y.z
  └── hotfix/xxx → main + develop
```

规则：

- `develop` 是日常集成分支。
- 功能分支从 `develop` 切出，合并回 `develop`。
- 发布前开 `release/x.y.z`，只做修复和收尾。
- 线上紧急问题走 `hotfix`，同时合并回 `main` 与 `develop`。

适合：有明确版本号、需要同时维护多个版本的软件。

### 3. Trunk-Based（主干开发）

```text
main（唯一长命分支）
  └── 短命分支（1~2 天） → 直接合并回 main
```

规则：

- 短命分支尽量小、尽快合并。
- 通过特性开关（Feature Flag）控制未完成功能。

适合：超大规模团队、每日多次发布、对 CI 要求极高。

## 分支命名建议

| 前缀 | 用途 | 示例 |
| --- | --- | --- |
| `feature/` | 新功能 | `feature/user-login` |
| `fix/` | 缺陷修复 | `fix/payment-timeout` |
| `hotfix/` | 线上紧急修复 | `hotfix/security-cve` |
| `release/` | 发布分支 | `release/1.4.0` |
| `docs/` | 文档 | `docs/git-guide` |
| `chore/` | 构建/配置 | `chore/update-deps` |

## 分支保护

托管平台（GitHub/GitLab/Gitee）上对 `main` 开启保护：

- 禁止直接推送，必须走 PR。
- 要求至少 1 人 Review。
- 要求 CI 通过。
- 禁止强制推送（force push）。

## 选择建议

| 团队情况 | 推荐模型 |
| --- | --- |
| Web 应用、持续发布 | GitHub Flow |
| 版本化软件、多版本维护 | Git Flow |
| 大型团队、高发布频率 | Trunk-Based |
| 个人项目 | GitHub Flow（简化为直接 main） |

## 易错点

::: danger 常见错误
1. 模型选完不写文档，规则停留在口头，很快失效。
2. 功能分支长期不合并，超过一周就应拆分或合并。
3. 直接在 `main` 上 `git commit`，绕过 PR 保护。
4. Git Flow 的小团队用起来太重，流程比代码还慢。
5. `main` 分支保护只开了「禁止直推」却没要求 Review 和 CI。
:::

## 验证方式

1. 在仓库设置中为 `main` 开启分支保护并验证直推被拒绝。
2. 按 `feature/xxx` 命名新建分支，完成功能后通过 PR 合并。
3. 用 `git log --graph --oneline --all` 观察分支合并历史是否符合模型。
4. 模拟一次 hotfix，确认同时合并回 `main` 与 `develop`（Git Flow）。

## 参考资料

- GitHub Flow：https://docs.github.com/zh/get-started/using-github/github-flow
- Git Flow：https://nvie.com/posts/a-successful-git-branching-model/
- Trunk-Based Development：https://trunkbaseddevelopment.com/
