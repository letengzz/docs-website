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

## 学习路径建议

1. 先读[概述与选型](Overview/index.md)，建立五层光谱与选型决策的认知。
2. 准备做 Serverless：读[Serverless 与函数计算](Serverless/index.md)，再读[云函数工程化](FunctionEngineering/index.md)。
3. 已经在用 K8s：读[托管容器服务](ContainerService/index.md)。
4. 账单压力大：直接跳[云成本治理（FinOps）](FinOps/index.md)。
5. 要动手迁一次：跟[实战：迁移与验收](Practice/index.md)完整走一遍。
6. 线上出问题：查[常见问题与排错](FAQ/index.md)。
