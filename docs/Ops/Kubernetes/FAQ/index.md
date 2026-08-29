# 常见问题与最佳实践

这一篇汇总 Kubernetes 高频问题与团队工程实践，覆盖排障、网络、存储、安全与升级。

## 常见问题

### 1. Pod 一直 Pending

原因多为**资源不足或调度限制**：

```shell
kubectl describe pod <name>
```

看 Events 中的 `0/2 nodes are available`，检查 requests 是否超过节点可用资源、是否有污点/容忍（taint/toleration）不匹配。

### 2. CrashLoopBackOff

容器启动后反复崩溃。排查顺序：

```shell
kubectl logs <pod> --previous   # 看上次崩溃日志
kubectl describe pod <pod>      # 看 OOMKilled / 探针失败
```

常见原因：启动命令错误、配置文件缺失、探针失败、内存超限被杀。

### 3. ImagePullBackOff

镜像拉取失败：镜像名/标签写错、私有仓库未配置 `imagePullSecrets`、节点无法访问镜像源。用 `kubectl describe pod` 查看具体错误。

### 4. Service 访问不通

按顺序检查：

```shell
kubectl get endpoints <svc>     # Endpoints 是否为空
kubectl describe svc <svc>      # selector 是否正确
kubectl exec -it <pod> -- curl <svc>  # 集群内访问
```

### 5. kubeadm join 报错

令牌过期或证书不匹配。重新生成：

```shell
kubeadm token create --print-join-command
```

### 6. 节点 NotReady

```shell
kubectl describe node <node>
journalctl -u kubelet -f
```

常见原因：kubelet 未启动、cgroup 驱动不一致、网络插件异常、节点资源耗尽。

### 7. 数据丢失

Pod 文件系统是非持久的；有状态数据必须用 PVC，并注意回收策略与备份（Velero/etcd snapshot）。

### 8. 如何做滚动发布

Deployment + 镜像新 tag，`kubectl set image` 或更新 YAML 后 `kubectl apply`；配合 readinessProbe 保证流量切换安全，失败用 `kubectl rollout undo`。

### 9. 权限与安全怎么管

1. RBAC：最小权限，禁止把 cluster-admin 给普通账号。
2. Secret：不提交仓库，用外部密钥管理。
3. 镜像：来源可信 + 扫描漏洞 + 非 root 运行。
4. 网络策略：默认拒绝 + 白名单放行。

### 10. 资源配额怎么设

Namespace 级别配置 ResourceQuota 与 LimitRange，防止某个团队打爆集群。

## 最佳实践清单

::: tip 可直接落地的清单
1. 所有工作负载用 Deployment/StatefulSet，不用裸 Pod。
2. 每个容器配置 requests/limits 与 readiness/liveness 探针。
3. 镜像使用固定 tag，不用 latest；私有仓库配 imagePullSecrets。
4. 配置走 ConfigMap、密钥走 Secret，不写进镜像。
5. 有状态数据用 PVC + 备份，重要集群定期备份 etcd。
6. 生产监控：Metrics Server + Prometheus + Grafana + Alertmanager。
7. 日志统一 stdout，由 Fluent Bit 采集到 Loki/ELK。
8. RBAC 最小权限，Secret 加密，开启网络策略。
9. 升级前看官方版本支持矩阵，逐版本升级并提前备份。
10. 用 Helm/Kustomize 管理清单，避免手工 kubectl apply 散落。
:::

## 验证方式

1. 按 FAQ 10 个问题各构造一个场景走一遍排障。
2. 用 `kubectl get events -A --sort-by=.lastTimestamp` 复盘一次故障。
3. 在测试集群练习滚动发布与回滚，记录每步命令。

## 相关专题

- [消息队列集群部署](../../../Backend/MessageQueue/Cluster/index.md)：Kafka / RabbitMQ 高可用集群在容器环境中的部署要点
- [Docker Compose 进阶](../../Docker/ComposeAdvanced/index.md)：从 Compose 到 K8s 的部署演进
- [微服务专题](../../../Backend/Microservices/index.md)：K8s 是微服务运行时，与注册中心/网关的职责分工

## 参考资料

- Kubernetes 官方文档：https://kubernetes.io/zh-cn/docs/
- kubectl 速查表：https://kubernetes.io/zh-cn/docs/reference/kubectl/cheatsheet/
- 故障排查指南：https://kubernetes.io/zh-cn/docs/tasks/debug/
