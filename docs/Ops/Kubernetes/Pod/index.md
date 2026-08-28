# Pod 详解

Pod 是 Kubernetes 的**最小调度单元**：一个 Pod 内可以有一个或多个容器，它们共享网络命名空间、存储卷和生命周期。理解 Pod 是理解 K8s 一切对象的基础。

## Pod 与容器的关系

```text
Pod（最小调度单元）
├── 容器 A（业务主容器）
├── 容器 B（sidecar：日志、代理）
└── initContainer（启动前初始化）
```

一个 Pod 内的容器：

1. 共享同一个 IP 与端口空间（通过 localhost 互访）。
2. 共享存储卷（Volume）。
3. 一起调度、一起销毁。

## Pod 示例

```yaml [pod.yaml]
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    app: web
spec:
  containers:
    - name: nginx
      image: nginx:1.28
      ports:
        - containerPort: 80
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 500m
          memory: 256Mi
      readinessProbe:
        httpGet:
          path: /
          port: 80
        initialDelaySeconds: 3
        periodSeconds: 5
      livenessProbe:
        httpGet:
          path: /health
          port: 80
        initialDelaySeconds: 10
        periodSeconds: 10
```

## 生命周期与状态

| 状态 | 含义 |
| --- | --- |
| Pending | 已创建，等待调度或镜像拉取 |
| Running | 至少一个容器在运行 |
| Succeeded | 所有容器正常退出（任务类） |
| Failed | 容器异常退出 |
| Unknown | 无法获取状态 |

## 探针（Probe）

| 探针 | 作用 | 失败后果 |
| --- | --- | --- |
| livenessProbe | 存活检查：容器是否还活着 | 重启容器 |
| readinessProbe | 就绪检查：能否接收流量 | 从 Service 摘除 |
| startupProbe | 启动检查：慢启动应用 | 启动期不执行其他探针 |

探针支持三种方式：`httpGet`、`tcpSocket`、`exec`。

## 资源请求与限制

```yaml
resources:
  requests:   # 调度依据（保证）
    cpu: 100m        # 0.1 核
    memory: 128Mi
  limits:     # 上限（超限可能被杀）
    cpu: 500m
    memory: 256Mi
```

- `requests` 决定 Pod 被调度到哪个节点。
- `limits` 决定运行期上限，超过 CPU limit 被限流，超过内存 limit 被 OOMKill。

## initContainer 与 sidecar

```yaml [pod-init.yaml]
spec:
  initContainers:
    - name: wait-db
      image: busybox:1.36
      command: ["sh", "-c", "until nc -z db-svc 5432; do sleep 1; done"]
  containers:
    - name: app
      image: my-app:1.0
```

- initContainer：主容器启动前按顺序执行，全部成功后主容器才启动。
- sidecar：与主容器常驻并行，如日志采集（Filebeat）、网络代理（Envoy）。

## 易错点

::: danger 常见错误
1. 生产直接 `kubectl run` 建裸 Pod：没有自愈和滚动更新，用 Deployment。
2. 忘记探针：应用假死后流量照打，故障不自动恢复。
3. 探针路径写错：`/health` 不存在导致 readiness 失败，Service 一直无可用后端。
4. limits 设置过小：Pod 反复 OOMKilled。
5. 在 Pod 里跑多个“业务主进程”：一个 Pod 应只有一个主进程，其他用 sidecar/init 模式。
6. 用 `latest` 镜像标签：拉取策略与回滚都不可控。
:::

## 验证方式

1. `kubectl apply -f pod.yaml && kubectl get pod -w` 观察状态变化。
2. `kubectl describe pod web-pod` 查看事件与探针结果。
3. `kubectl exec -it web-pod -- curl localhost` 验证容器内访问。

## 参考资料

- Pod 概念：https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/
- Pod 生命周期：https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/pod-lifecycle/
- 容器探针：https://kubernetes.io/zh-cn/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
