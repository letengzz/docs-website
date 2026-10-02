# 常见问题与最佳实践

GitOps 落地一两年后的团队，问题会从「怎么装」变成「为什么越来越慢、越来越没人信」。本页按「决策 → 排障 → 纪律」三层组织高频问题：先用决策树定位你的阶段，再按症状排障，最后是一份上线自查表。

## 三个决策问题

### 我们到底需不需要 GitOps？

三问定位：① 集群里的应用是否超过 5 个？② 是否有 2 个以上环境需要保持一致？③ 是否需要回答「上周三谁改了 prod 什么」？**三问有两个「是」，GitOps 的收益就大于成本**；只管一个玩具集群，一条 `kubectl apply -f` 脚本更诚实。

### Argo CD 还是 Flux？

一句话判据：**要给多个团队一个可视化交付平台 → Argo CD；平台组自管集群、一切配置走 Git → Flux**。详细对照见 [Flux：另一条主线](FluxCD/index.md)。两者都满足 OpenGitOps 四原则，选错的主要代价是迁移，不是灾难——但迁移很痛，先看组织再选。

### 密钥方案怎么选？

已有 Vault/云 KMS → ESO；从零小团队 → Sealed Secrets 先跑；整文件加密托管 → SOPS。详细判据与迁移路径见 [密钥管理](Secrets/index.md)。

## 排障决策树

```text
应用没更新？
├─ argocd app get 状态是 OutOfSync？
│  ├─ 是 → 看 diff：Git 有变更没同步 → 手动 sync 或等 automated 窗口
│  │        Git 无变更 → 检查 CI 是否真的提交了晋级 PR（九成在这）
│  └─ 否（Synced 但版本不对）→ overlay 里的 tag 是不是旧的？
│         → 查 ImagePolicy 排序 / 晋级 workflow 是否跑成功
├─ 同步失败（Sync Failed）？
│  ├─ 渲染错误 → 本地 kustomize build 复现，九成是 patch 字段拼错
│  └─ 应用错误 → 看 Events：镜像拉不到？探针不过？配额不足？
└─ 同步成功但应用异常？
   └─ Health: Degraded → 看 readinessProbe 与日志；
      数据库类 → 检查迁移 Wave 是否先行、迁移是否向后兼容
```

## 六类高频问题

| 类别 | 症状 | 根因与解法 |
| --- | --- | --- |
| 事实源失守 | Git 改了集群没变 / 集群变了 Git 不知道 | 控制器失联（凭证过期）或有人绕过 Git 改集群且没开 selfHeal。先恢复对齐，再补「集群只读」纪律 |
| 漂移拉锯 | 手工改动反复被改回 / 或永远改不回 | 不是 bug：开 selfHeal 就必须接受「集群只读」；有合法漂移（HPA、webhook 注入）要配 `ignoreDifferences` |
| 密钥泄露 | 明文 Secret 出现在 Git 历史 | 立即轮换密钥（唯一根治手段）→ `git filter-repo` 清理历史 → 引入 pre-commit 扫描防复发 |
| 多环境腐化 | dev 与 prod 差异越积越多、说不清哪些是刻意的 | overlay 只写差异的纪律失守。做一轮「差异盘点」，把散落配置收进 base/overlay |
| 升级事故 | 控制器升级后 API 报错、清单失效 | 跳 minor 升级撞上弃用 API（Argo CD 只保 3 个 minor、Flux 需先 `flux migrate`）。恢复旧版本后按 minor 逐个升 |
| 交付变慢 | 每次发布要人肉点很多次同步 | automated 关太多 / PR 审批链太长。dev 全自动、prod 只审 PR，发布动作收敛为「合并一次 PR」 |

## 纪律清单：让事实源永远可信

::: tip 上线自查（十二条）
1. 所有环境变更都有对应的 Git 提交（包括紧急热修，事后补）；
2. prod overlay 挂分支保护 + CODEOWNERS，合并即发布；
3. selfHeal 开启的环境，人类账号的集群写权限收敛到仅白名单操作；
4. 合法漂移（HPA/webhook）已配置 `ignoreDifferences`；
5. 密钥零明文入库，pre-commit 扫描在位，泄露响应流程有演练；
6. 数据库迁移向后兼容（先加后删），迁移 Job 编排在最前 Wave；
7. PreSync 备份在位，回滚演练最近三个月内跑过一次；
8. CI 对所有集群零凭据，机器人 token 只写配置仓；
9. 镜像 tag 用 commit-sha，`latest` 全库禁用（CI 校验）；
10. 控制器升级窗口固定、按 minor 走，弃用 API 提前迁移；
11. Argo CD/Flux 自身配置也在 Git 里（自举），重建集群可从 Git 恢复全部交付；
12. 同步/回滚事件接通知（飞书/Slack），Degraded 不留过夜。
:::

## 一页速查

| 想做的事 | 去哪个页面 |
| --- | --- |
| 从零安装、看懂 Application | [Argo CD：安装与核心对象](ArgoCD/index.md) |
| 评估不用 Argo CD 的选项 | [Flux：另一条主线](FluxCD/index.md) |
| 设计仓库与多环境 | [配置仓库设计与多环境](RepoStructure/index.md) |
| 密钥安全进 Git | [密钥管理](Secrets/index.md) |
| 发布编排与回滚 | [渐进发布与回滚](ProgressiveDelivery/index.md) |
| 镜像 tag 谁来改 | [镜像更新与 CI 分工](ImageUpdate/index.md) |
| 完整可复现落地 | [实战：博客平台 GitOps 交付](Practice/index.md) |

## 参考资料

- OpenGitOps 原则：<https://opengitops.dev/>
- Argo CD FAQ（官方）：<https://argo-cd.readthedocs.io/en/stable/faq/>
- Flux 故障排查：<https://fluxcd.io/flux/flux-ctlint/>
- Argo CD 安全与披露：<https://argo-cd.security-docs.io/>（以官方 SECURITY.md 为准）
