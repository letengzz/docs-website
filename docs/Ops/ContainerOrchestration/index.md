# 容器编排进阶

<p style="text-align:center;"><img src="./assets/orchestration-logo.png" style="zoom:75%;" /></p>

容器编排进阶是 Kubernetes 之上的「生产化能力层」：用 **Helm** 打包分发应用，用 **Operator** 把运维经验写成代码，用 **服务网格** 治理流量与安全，用 **弹性伸缩** 应对流量波动，用 **多集群与 GitOps** 支撑规模化交付。本专题面向已有 K8s 基础、想进入生产落地的运维与平台工程师。

## 专题导航

- [Helm：Kubernetes 应用包管理](Helm/index.md)
- [Operator：把运维经验变成代码](Operator/index.md)
- [服务网格：Istio 流量与安全治理](ServiceMesh/index.md)
- [弹性伸缩：HPA、VPA 与 KEDA](Autoscaling/index.md)
- [多集群：联邦、MCS 与容灾](MultiCluster/index.md)
- [GitOps：Argo CD 声明式交付](GitOps/index.md)
- [容器与集群安全加固](Security/index.md)
- [实战：GitOps + 弹性伸缩交付闭环](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 阅读建议

1. 未接触过 Kubernetes 的读者，先看 [Kubernetes 专题](../Kubernetes/index.md) 的基础章节。
2. 想快速落地生产：按顺序读 Helm → GitOps → Security → Practice。
3. 关注流量治理与多集群容灾：重点读 ServiceMesh → MultiCluster。

## 相关专题

- [Terraform](../Terraform/index.md)：**基础设施层**的声明式交付——集群、节点池、网络与存储由 IaC 建好，本专题讲的 Helm/Argo CD 负责**应用层**交付。二者的边界与配合见 [Terraform 概述与选型](../Terraform/Overview/index.md)。
- [Kubernetes](../Kubernetes/index.md)：本专题的前置基础。
- [CI/CD 自动部署与回滚](../../Tools/CICD/DeployRollback/index.md)：发布策略与回滚演练。

## 相关专题与分工

- [云原生 · 容器服务](../CloudNative/ContainerService/index.md)：本专题讲**交付工具链本身**——Helm 怎么打包与分发、Operator 怎么把运维经验写成控制器、服务网格怎么治理流量与安全、GitOps（Argo CD）怎么把 Git 当唯一事实来源；该页讲**云上的托管控制面怎么买**——控制面按什么计费、节点怎么弹、Spot 与承诺折扣怎么用。两者是「工具怎么用」与「资源从哪来、钱怎么花」的关系：本专题负责应用层交付，该页负责承载它的托管底座，比如本专题的 Helm/Argo CD 交付目标，往往就是该页讲的托管集群。
