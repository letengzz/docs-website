# 云原生

<p style="text-align:center;"><img src="./assets/cloudnative-logo.png" style="zoom:75%;" /></p>

托管云服务怎么选、Serverless 怎么落地、云账单怎么治。

- [概述与选型](Overview/index.md)
- [Serverless 与函数计算](Serverless/index.md)
- [云函数工程化](FunctionEngineering/index.md)
- [托管容器服务](ContainerService/index.md)
- [云成本治理（FinOps）](FinOps/index.md)
- [实战：迁移与验收](Practice/index.md)
- [常见问题与排错](FAQ/index.md)

## 本专题讲什么

本专题只解决一个问题：**把应用跑在云厂商的托管服务上，怎么选、怎么落地、怎么控成本**。三条主线：

- **选型**：从 IaaS、CaaS、PaaS、FaaS 到 BaaS 的五层服务光谱，每一种都讲清「你管什么、云管什么」。
- **落地**：函数即服务（Function as a Service，FaaS）的运行原理、工程化治理（冷启动、幂等、本地调试、基础设施即代码）。
- **成本**：云成本治理（FinOps）的三阶段闭环、统一账单口径（FOCUS），以及可量化的降本杠杆。

:::tip
不知道从哪页开始？先读[概述与选型](Overview/index.md)，它给出选型四维度与四种典型架构组合，其余页面都是它的展开。
:::

## 与相邻专题的分工

云原生这个词很大，本专题刻意只负责「云托管服务」这一层。边界如下：

- [概述与选型](Overview/index.md) → [Kubernetes](../Kubernetes/index.md)：K8s 专题讲**集群内部的对象模型**（Pod、Deployment、Service、Ingress 怎么写、怎么调）；本专题的[托管容器服务](ContainerService/index.md)只讲**云上怎么买控制面、节点怎么弹、成本怎么降**，不重复 K8s 语法。
- [概述与选型](Overview/index.md) → [Docker](../Docker/index.md)：Docker 专题讲**镜像与运行时本身**（Dockerfile 写法、层缓存、多阶段构建）；本专题只讲镜像如何进云端仓库、函数如何按需拉取与缓存。
- [概述与选型](Overview/index.md) → [容器编排进阶](../ContainerOrchestration/index.md)：编排进阶专题讲 **Helm 打包与 Argo CD 声明式交付**；本专题在弹性与计费层面与其衔接，不重复交付工具用法。
- [云函数工程化](FunctionEngineering/index.md) → [CI/CD 自动部署与回滚](../../Tools/CICD/DeployRollback/index.md)：CI/CD 专题讲通用的**发布流水线与回滚策略**；函数同样需要灰度与回滚，但打包产物是部署包/镜像、发布单元是版本与别名，差异在本专题单独说明。
- [概述与选型](Overview/index.md) → [Terraform](../Terraform/index.md)：Terraform 专题讲 **IaC 的 state、模块与工作流**；本专题只给出函数与托管集群的最小 IaC 片段，完整工程化请回到 Terraform 专题。
- [云函数工程化](FunctionEngineering/index.md) → [数据库](../../DB/Relational/index.md) 与 [NoSQL 数据库](../../DB/NoRelational/index.md)：数据库专题讲**选型与建模**；本专题只讲函数侧怎么建连接、怎么保证幂等写入。
- [托管容器服务](ContainerService/index.md) → [服务网格：Istio](../ContainerOrchestration/ServiceMesh/index.md)：网格专题讲**自建流量治理层**——Sidecar 与 Ambient 两种数据面怎么装、VirtualService 怎么写、mTLS 怎么开、可观测性数据从哪来；本专题只回答**这笔能力该自建还是托管**：厂商的托管网格把控制面变成按 Pod 数或按请求量计费的资源，省掉控制面运维，但数据面（每个 Pod 一个 Sidecar 的 CPU/内存）仍记在你的账单上。要算清这笔账，配合[云成本治理（FinOps）](FinOps/index.md)的单位成本口径一起看。
- [概述与选型](Overview/index.md) → [云上架构](../CloudArchitecture/index.md)：本专题回答「**用云托管服务的哪种形态**」（IaaS → BaaS 五层光谱、选型四维度）；云上架构专题回答「**形态定了之后，在资源编排层怎么摆**」（VPC 与网段、入口层数与健康检查、可用区拓扑、弹性与计费模型）。两者的交接处正是[云成本治理（FinOps）](FinOps/index.md)：治理口径在本专题，而**哪些架构决定会在账单上留下不可逆痕迹**（网段选小了无法打通 IDC、入口按量却未设告警、单 NAT 是隐性单点）在云上架构专题。

## 学习路径建议

1. 先读[概述与选型](Overview/index.md)，建立五层光谱与选型决策的认知。
2. 准备做 Serverless：读[Serverless 与函数计算](Serverless/index.md)，再读[云函数工程化](FunctionEngineering/index.md)。
3. 已经在用 K8s：读[托管容器服务](ContainerService/index.md)。
4. 账单压力大：直接跳[云成本治理（FinOps）](FinOps/index.md)。
5. 要动手迁一次：跟[实战：迁移与验收](Practice/index.md)完整走一遍。
6. 线上出问题：查[常见问题与排错](FAQ/index.md)。

## 服务网格在云原生栈里的位置（第 187 天补充）

网格经常被排错位置：有人把它当网络方案（以为装了就不用管 CNI），有人把它当 API 网关（以为能挡住外部流量）。准确的位置是——**它坐在「服务发现」之上、「业务代码」之下，只负责服务之间的那次调用**。

| 层 | 组件 | 网格是否替代它 |
| --- | --- | --- |
| 网络与可达性 | CNI、NetworkPolicy、Service/EndpointSlice | ❌ 不替代，网格依赖它们 |
| 流量入口 | Ingress / Gateway API / API 网关 | ❌ 不替代（南北向归网关） |
| 服务间治理 | Sidecar / ztunnel + waypoint | ✅ 这一层才是网格 |
| 业务语义 | 幂等、状态机、配额 | ❌ 永远不替代 |

所以判断「要不要上网格」，等价于问：**这一层（服务间治理）现在有没有人负责、用什么方式负责**。答案若是「每个团队各自引 SDK」，网格是把这个责任收敛到平台层的一种方式，代价与替代方案见 [服务网格 · 概述](../../Backend/ServiceMesh/Overview/index.md)。

::: warning 本页特有的坑：把网格算进「迁移到云原生」的第一步
网格建立在「服务发现已经稳定、Pod 网络已经可靠」之上。集群还在频繁改 CNI、EndpointSlice 还在抖动时上网格，遇到的问题会被归因成「网格不稳」，实际是下层没稳。顺序应当是：**网络与调度稳定 → 可观测（指标/日志）→ 入口网关 → 网格**。反过来做，每一层都会替下一层背锅。
:::
