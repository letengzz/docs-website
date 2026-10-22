# ConfigMap 与 Secret

ConfigMap 保存**非敏感配置**，Secret 保存**敏感信息**（密码、密钥、证书）。二者都可以通过环境变量或文件挂载注入到 Pod。

## ConfigMap 创建

```shell
# 从字面量
kubectl create configmap app-config --from-literal=APP_ENV=prod --from-literal=LOG_LEVEL=info

# 从文件
kubectl create configmap app-config --from-file=application.properties
```

```yaml [configmap.yaml]
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: prod
  LOG_LEVEL: info
  config.properties: |
    server.port=8080
```

## Secret 创建

```shell
kubectl create secret generic db-secret \
  --from-literal=DB_USER=admin \
  --from-literal=DB_PASSWORD=passw0rd

# TLS 证书
kubectl create secret tls app-tls --cert=server.crt --key=server.key
```

Secret 的 value 在 YAML 中必须是 **base64 编码**：

```yaml [secret.yaml]
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  DB_USER: YWRtaW4=        # admin
  DB_PASSWORD: cGFzc3cwcmQ=  # passw0rd
```

## 注入方式

### 环境变量

```yaml
spec:
  containers:
    - name: app
      env:
        - name: APP_ENV
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: APP_ENV
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: DB_PASSWORD
```

### 文件挂载

```yaml
spec:
  containers:
    - name: app
      volumeMounts:
        - name: config
          mountPath: /etc/app/config
  volumes:
    - name: config
      configMap:
        name: app-config
    - name: secret
      secret:
        secretName: db-secret
```

## 更新与生效

1. 环境变量方式：修改 ConfigMap 后需要**重启 Pod** 才生效。
2. 挂载方式：文件会更新，但**不是热更新**（需要应用自己监听或使用 subPath 时注意：subPath 挂载不会更新）。
3. 使用 `kubectl rollout restart deployment/app` 强制滚动重启。

## Secret 的安全性

::: danger 注意
Secret 只是**不是明文**，base64 不是加密，任何有权限读取 API 的人都能解码。生产建议：
1. 使用外部密钥管理（Vault、云厂商 KMS）+ External Secrets Operator；密钥如何安全参与 GitOps 交付（ESO / Sealed Secrets / SOPS 三路线选型），见 [GitOps · 密钥管理](../../ContainerOrchestration/GitOps/Secrets/index.md)。
2. 开启 RBAC 限制 Secret 读取权限。
3. 开启 etcd 加密存储（EncryptionConfiguration）。
:::

## 易错点

::: danger 常见错误
1. 把密码明文写进 ConfigMap：敏感信息必须用 Secret。
2. base64 编码错误：Secret 创建时报错或解码失败。
3. 改了 ConfigMap 以为自动生效：环境变量注入需要重启 Pod。
4. 挂载整个 ConfigMap 覆盖目录：会覆盖挂载点原内容，注意设计目录结构。
5. Secret 存大量数据：etcd 有大小限制（默认 1MiB）。
6. 在镜像里内置密钥：密钥应通过 Secret 注入，不能打进镜像。
:::

## 验证方式

1. `kubectl get configmap app-config -o yaml` 查看内容。
2. `kubectl exec -it <pod> -- env | grep APP_ENV` 确认环境变量注入。
3. `kubectl exec -it <pod> -- cat /etc/app/config/config.properties` 确认文件挂载。

## 与「配置管理与动态配置」专题的分工（第 188 天补充）

ConfigMap 是「K8s 原生的配置载体」，配置中心是「跨集群、跨运行时的配置服务」。两者最常见的错误用法是**双写**：CI 既推配置中心、又 `kubectl apply` 一份 ConfigMap，于是同一份配置有两个权威。

三条边界：

| 场景 | 用哪个 | 理由 |
| --- | --- | --- |
| 应用跑在 K8s 里，配置与镜像同生命周期 | ConfigMap | 声明式、随 Deployment 一起回滚 |
| 多集群 / 混合运行时（VM + 容器）共用一份配置 | 配置中心 | ConfigMap 跨不了集群边界 |
| 需要灰度到部分实例、需要变更审计 | 配置中心 | ConfigMap 没有"发给谁"的维度 |

一个必须知道的事实：**ConfigMap 的更新不是实时的**。kubelet 按 `--sync-frequency`（默认 1 分钟）与 ConfigMap 缓存 TTL 决定何时重新拉取，再叠加写入挂载卷的延迟，整体是**分钟级**；而用 `subPath` 挂载的单文件**永远不会更新**——这是"改了没生效"的第一大原因。验证方式：

```shell
# 看挂载方式：出现 subPath 就说明这个文件不会热更
kubectl get deploy <name> -o jsonpath='{range .spec.template.spec.containers[*].volumeMounts[*]}{.name}{"\t"}{.subPath}{"\n"}{end}'

# 看容器内文件的实际修改时间（与环境变量注入对比：env 注入的值永不更新）
kubectl exec <pod> -- stat -c '%y %n' /etc/app/application.yaml
```

判据沿用新专题的 `CFF-D`（启动期与运行期兜底分开）与 `CFL-G`（环境隔离方式唯一）：**ConfigMap 与配置中心只能有一个权威**，另一个必须是渲染产物或不存在。

## 参考资料

- ConfigMap：https://kubernetes.io/zh-cn/docs/concepts/configuration/configmap/
- Secret：https://kubernetes.io/zh-cn/docs/concepts/configuration/secret/
- 密钥管理最佳实践：https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/encrypt-data/
- Secret 的集中托管、动态凭据与轮换：[密钥与凭据治理](../../SecurityHardening/SecretGovernance/index.md)
