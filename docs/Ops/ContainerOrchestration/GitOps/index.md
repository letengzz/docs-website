# GitOps：声明式持续交付

<p style="text-align:center;"><img src="../assets/argocd-logo.png" style="zoom:75%;" /></p>

GitOps 是**以 Git 为唯一事实来源（Single Source of Truth）的持续交付模式**：环境的期望状态全部写成声明式清单放进 Git 仓库，由运行在集群内的控制器（Argo CD、Flux）持续对比「Git 里声明的状态」与「集群实际的状态」，发现漂移就自动对齐。本专题基于 **Argo CD 3.5** 与 **Flux 2.9**（2026-10 口径）编写，覆盖工具选型、配置仓库设计、多环境管理、密钥管理、渐进发布与回滚。

::: tip 一句话理解
传统 CD 是「**推**」——CI 流水线拿着凭据把变更 `kubectl apply` 进集群；GitOps 是「**拉**」——集群里的控制器盯着 Git，自己把状态拉齐。凭据不出集群、变更全有审计、人手改的东西会被改回去，这三件事同时成立，就是 GitOps。
:::

## 版本状态（2026-10 口径）

| 工具 | 当前主线 | 维护中 | 已 EOL | 说明 |
| --- | --- | --- | --- | --- |
| Argo CD | **3.5**（3.5.3 / 2026-09-14） | 3.4、3.3（至 3.6 GA） | 3.2（2026-08-04 EOL） | 每季度一个 minor，**仅最近 3 个 minor 收补丁**；3.6 计划 2026-11-03 GA；内置 Helm 4.2.1 / Kustomize 5.8.1，测试 K8s 1.33~1.36 |
| Flux | **2.9**（v2.9.5 / 2026-08-31） | 2.8、2.7 | 2.6（随 2.9 宣布） | 升级前先跑 `flux migrate` 清理弃用 API；helm-controller 已支持 Helm v4；测试 K8s 1.34~1.36 |
| External Secrets Operator | **2.11**（2026-09-18） | 2.10、2.9 | 更早版本（每个 minor 支持窗口很短） | 密钥同步事实标准，`external-secrets.io/v1` 稳定 API，约 41 个 Provider |
| Sealed Secrets | **0.40**（2026-09-10） | 0.39.x | 更早版本 | 0.40 修复了 `/v1/rotate` 解密预言机安全问题，务必升级 |

::: warning 关于版本窗口
Argo CD 与 ESO 的支持窗口都很短（Argo CD 只保 3 个 minor；ESO 每个 minor 的 EOL 就是下一个 minor 发布日）。**不要攒大版本升级**，把「跟随 minor 升级」本身做成一条自动化流水线，才是 GitOps 团队管理自己的方式。
:::

## 快速上手（最小可用）

```shell
# 1. 安装 Argo CD
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
kubectl create ns argocd
helm install argocd argo/argo-cd -n argocd

# 2. 获取初始密码并登录 CLI
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
argocd login <SERVER-ADDRESS> --insecure

# 3. 创建第一个 Application（指向你的清单仓库）
kubectl apply -f application.yaml

# 4. 验证同步状态
argocd app get web
# 期望：Sync Status: Synced、Health Status: Healthy
```

完整安装、Application 字段逐项解释与漂移自愈演练见 [Argo CD：安装与核心对象](ArgoCD/index.md)。

## 专题地图

| 页面 | 内容 | 你将学会 |
| --- | --- | --- |
| [GitOps 理念与工作原理](Overview/index.md) | 四原则、推 vs 拉、适用边界 | 判断什么该进 GitOps、什么不该 |
| [Argo CD：安装与核心对象](ArgoCD/index.md) | Application、Project、同步策略、RBAC | 从零装好并管住一个 Argo CD |
| [Flux：另一条主线](FluxCD/index.md) | GitOps Toolkit、Kustomization、HelmRelease | 选型 Argo CD 还是 Flux |
| [配置仓库设计与多环境](RepoStructure/index.md) | monorepo vs 分仓、overlay、晋级 | 设计一套不烂尾的清单仓库 |
| [密钥管理](Secrets/index.md) | ESO、Sealed Secrets、SOPS 三路线 | 密钥进 Git 又不泄密 |
| [渐进发布与回滚](ProgressiveDelivery/index.md) | Sync Waves、Hooks、Canary、git revert | 发布分波走，回滚一条命令 |
| [镜像更新与 CI 分工](ImageUpdate/index.md) | CI 只构建、谁改镜像标签 | 划清 CI 与 CD 的责任边界 |
| [实战：博客平台 GitOps 交付](Practice/index.md) | 多环境 + 密钥 + 发布 + 回滚闭环 | 照着做完一套完整落地 |
| [常见问题与最佳实践](FAQ/index.md) | 排错决策树、六类高频坑 | 出问题知道从哪查 |

## 与相邻专题的分工

| 专题 | 它讲什么 | 与本专题的边界 |
| --- | --- | --- |
| [Kubernetes](../../Kubernetes/index.md) | 平台自带能力：Pod、Deployment、Service | 本专题讲这些清单**怎么被交付进集群** |
| [Terraform](../../Terraform/index.md) | 基础设施层的声明式交付（集群、网络、存储本身） | IaC 建**机器与集群**，GitOps 交付**集群里跑的应用**；两套事实来源不要混在一个仓库 |
| [Helm](../Helm/index.md) | 把应用打包成 Chart | Helm 负责**渲染出清单**，Argo CD/Flux 负责**把清单同步进集群**——GitOps 里 Helm 是渲染引擎不是部署工具 |
| [服务网格 Istio](../ServiceMesh/index.md) | 流量与安全治理的运行时行为 | 网格全部配置都是 CRD，天然适合进 Git；渐进发布的每个中间状态都要落盘 |
| [多集群](../MultiCluster/index.md) | 集群联邦与跨集群形态 | ApplicationSet 按集群生成 Application，是跨集群配置分发的落点 |
| [CI/CD（工具）](../../../Tools/CICD/index.md) | 流水线设计与执行 | CI 在流水线里跑，CD 的「最后一公里」从流水线挪进集群内控制器 |

::: tip 阅读路径
第一次接触 GitOps：Overview → ArgoCD → Practice，两天可以跑通闭环。要给团队做选型：Overview → FluxCD → RepoStructure → Secrets。已在生产：直接看 ProgressiveDelivery 与 FAQ。
:::

## 参考资料

- Argo CD 官方文档：<https://argo-cd.readthedocs.io/>
- Flux 官方文档：<https://fluxcd.io/flux/>
- GitOps 原则（OpenGitOps，CNCF）：<https://opengitops.dev/>
- Argo CD 发布与支持策略：<https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/>
- External Secrets Operator：<https://external-secrets.io/>
