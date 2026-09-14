# Kubernetes

<p style="text-align:center;"><img src="./assets/kubernetes-logo.png" alt="Kubernetes 官方 Logo" style="zoom:75%;" /></p>

Kubernetes（K8s）是容器编排平台的事实标准，负责容器的部署、扩缩容、服务发现与自愈，是云原生架构的核心。

- [核心概念与架构](Overview/index.md)
- [安装与集群搭建](Install/index.md)
- [Pod 详解](Pod/index.md)
- [Deployment 与工作负载](Deployment/index.md)
- [Service 与网络](Service/index.md)
- [Ingress 入口](Ingress/index.md)
- [ConfigMap 与 Secret](ConfigMapSecret/index.md)
- [存储与 PV/PVC](Storage/index.md)
- [监控与运维](Monitoring/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [Terraform](../Terraform/index.md)：**集群本身怎么建**交给 IaC。Terraform 的 `kubernetes` / `helm` provider 也能管 K8s 资源，但高频变化的业务负载建议交给 GitOps（见下一条）。
- [容器编排进阶](../ContainerOrchestration/index.md)：集群建成后，用 Helm 打包应用、用 Argo CD 做声明式交付。
- [Docker](../Docker/index.md)：从单机容器到集群编排的起点。
