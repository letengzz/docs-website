# 监控与运维

Kubernetes 日常运维围绕 `kubectl` 展开：查看资源、诊断故障、查看日志与事件。生产环境再叠加 Metrics Server、Prometheus、Grafana 形成完整监控体系。

## kubectl 常用命令

| 命令 | 作用 |
| --- | --- |
| `kubectl get pods -A` | 查看所有命名空间 Pod |
| `kubectl describe pod <name>` | 查看详情与事件（诊断首选） |
| `kubectl logs -f <pod> [-c 容器]` | 查看日志（多容器指定 -c） |
| `kubectl exec -it <pod> -- sh` | 进入容器 |
| `kubectl port-forward svc/<svc> 8080:80` | 端口转发（本地调试） |
| `kubectl top node` / `kubectl top pod` | 资源占用（需 Metrics Server） |
| `kubectl get events --sort-by=.lastTimestamp` | 查看集群事件 |

## 诊断流程

```text
1. kubectl get pods        # 看状态
2. kubectl describe pod    # 看事件与探针
3. kubectl logs -f pod     # 看应用日志
4. kubectl exec -it pod    # 进容器排查
```

## Metrics Server 与 HPA

```shell
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl top nodes
kubectl top pods
```

Metrics Server 采集节点与 Pod 的 CPU/内存，是 `kubectl top` 和 HPA 自动扩缩容的数据来源。

## 日志方案

1. 单容器：`kubectl logs -f <pod>`。
2. 多容器：`kubectl logs -f <pod> -c <container>`。
3. 生产：应用日志写 stdout，由节点上的采集器（Fluent Bit/Filebeat）收集到 Loki/ELK。

## 生产监控体系

| 组件 | 作用 |
| --- | --- |
| Prometheus | 指标采集与告警（Kube-Prometheus-Stack） |
| Grafana | 可视化面板 |
| Alertmanager | 告警通知 |
| Kube-state-metrics | 暴露资源对象指标 |

```shell
# 常用一键安装（kube-prometheus-stack）
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus prometheus-community/kube-prometheus-stack
```

## 备份与升级

1. **etcd 备份**：集群状态的关键，定期 `etcdctl snapshot save`。
2. **升级**：先升级控制平面，再逐批升级节点，一次一个次要版本。
3. **应用备份**：用 Velero 备份 K8s 对象与 PV 数据。

## 易错点

::: danger 常见错误
1. 只看 `get pods` 不看 describe/events：真正原因都在事件里。
2. 日志只看当前 Pod：Deployment 有多个副本，加 `-l app=xxx` 或 `--all-containers`。
3. 没装 Metrics Server 就用 `kubectl top`：报 `metrics.k8s.io not available`。
4. 端口转发忘了 Ctrl+C：端口占用，调试完及时清理。
5. 生产不做 etcd 备份：一次误删/损坏就丢整个集群状态。
6. 升级直接跨多个大版本：必须逐版本升级并参考官方支持矩阵。
:::

## 验证方式

1. `kubectl get pods -A` 确认核心组件正常。
2. 部署一个故障应用，按「诊断流程」四步走一遍。
3. 安装 Metrics Server 后执行 `kubectl top nodes` 确认输出。

## 参考资料

- kubectl 速查表：https://kubernetes.io/zh-cn/docs/reference/kubectl/cheatsheet/
- Metrics Server：https://github.com/kubernetes-sigs/metrics-server
- Kube-Prometheus-Stack：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack
- Velero 备份：https://velero.io/docs/
