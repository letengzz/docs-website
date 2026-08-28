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
1. 使用外部密钥管理（Vault、云厂商 KMS）+ External Secrets Operator。
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

## 参考资料

- ConfigMap：https://kubernetes.io/zh-cn/docs/concepts/configuration/configmap/
- Secret：https://kubernetes.io/zh-cn/docs/concepts/configuration/secret/
- 密钥管理最佳实践：https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/encrypt-data/
