# 存储与 PV/PVC

容器文件系统在 Pod 重建后消失，持久化数据需要**卷（Volume）**。K8s 通过 **PV（PersistentVolume）与 PVC（PersistentVolumeClaim）** 解耦“存储资源”和“存储申请”。

![PV/PVC 存储体系](../assets/pv-pvc.svg)

## Volume 类型

| 类型 | 说明 |
| --- | --- |
| emptyDir | 临时目录，Pod 生命周期内有效 |
| hostPath | 宿主机目录（仅测试/单节点） |
| configMap / secret | 配置注入 |
| PV/PVC | 持久化存储 |

## PV / PVC / StorageClass 关系

```text
StorageClass（动态供应模板）
        │ 自动创建
        ▼
PV（持久卷：真实存储）
        │ 绑定
        ▼
PVC（存储申请）→ 挂载到 Pod
```

## 示例：PVC 申请存储

```yaml [pvc.yaml]
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard
```

```yaml [pod-pvc.yaml]
spec:
  containers:
    - name: app
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: data-pvc
```

## 访问模式

| 模式 | 含义 |
| --- | --- |
| ReadWriteOnce（RWO） | 单节点读写 |
| ReadOnlyMany（ROX） | 多节点只读 |
| ReadWriteMany（RWX） | 多节点读写（NFS 等） |

## StorageClass

```yaml [storageclass.yaml]
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
```

常见 provisioner：

- 云厂商：aws-ebs、azure-disk、gce-pd
- 自建：NFS（nfs.csi.k8s.io）、Rook Ceph、local-path

## 生命周期

| 阶段 | 含义 |
| --- | --- |
| Available | PV 空闲可绑定 |
| Bound | 已绑定 PVC |
| Released | PVC 删除后待回收 |
| Failed | 回收失败 |

回收策略：`Retain`（保留数据）、`Delete`（删除存储）、`Recycle`（已弃用）。

## 易错点

::: danger 常见错误
1. 有状态应用不声明 PVC：Pod 重建数据丢失。
2. `accessModes` 不匹配：PVC 无法绑定到 PV。
3. 多副本共享写：默认 RWO 不支持多节点同时写，需要 RWX 存储。
4. 删除 PVC 导致数据被删：取决于回收策略 `Delete`，重要数据用 `Retain` 或先备份。
5. 本地磁盘误当持久化：hostPath 只在单节点测试可用。
6. StatefulSet 的 PVC 模板写错：每个副本的卷无法正确创建。
:::

## 验证方式

1. `kubectl get pvc` 确认 STATUS 为 Bound。
2. 在 Pod 中写入文件，删除 Pod 后重建，确认数据仍在。
3. `kubectl describe pvc data-pvc` 查看绑定详情。

## 相关专题

- [备份与容灾](../../BackupDR/index.md)：**PV 存在 ≠ 数据可恢复**。卷只解决「Pod 重建后数据还在」，解决不了「误删了数据想回到昨天」。集群侧的备份（Velero + CSI 快照、etcd 快照）与不可变存储见 [备份工具矩阵](../../BackupDR/Toolchain/index.md)。
- [监控与运维](../Monitoring/index.md)：容量与 PVC 异常需要告警，否则会静默写满。
- [容器编排进阶](../../ContainerOrchestration/index.md)：有状态工作负载的跨集群迁移与多集群容灾。

## 与「对象存储工程」专题的分工（第 173 天补充）

| 问题 | 归本页 | 归[文件与对象存储工程](../../../Backend/ObjectStorage/index.md) |
| --- | --- | --- |
| PV/PVC、StorageClass、CSI 驱动 | ✅ | — |
| 对象存储为什么不该被当 POSIX 文件系统挂载 | — | ✅ [总览](../../../Backend/ObjectStorage/Overview/index.md) |
| 块/文件存储挂进 Pod 的访问模式 | ✅ | — |
| 对象存储的 key 设计、预签名直传、生命周期 | — | ✅ [键空间](../../../Backend/ObjectStorage/KeysLayout/index.md) · [上传路径](../../../Backend/ObjectStorage/UploadPaths/index.md) |

一句话边界：本页解决「Pod 怎么拿到一块可读写的盘」，专题解决「不让应用把对象存储当盘用之后，该怎么改」。

::: danger 本页特有的坑：用 CSI 把对象存储挂成数据目录
对象存储的 CSI 驱动（s3fs / mountpoint 类）能让 Pod 里出现一个「目录」，但语义完全不同：
- `ls` 一次 = 一次 `LIST`（按请求计费，且 1000 条一页）；
- 打开一个小文件可能触发整对象的 `GET`；
- 编辑器/数据库的「truncate + write」会把对象整个重写；
- 没有 `rename`、没有文件锁、没有 `fsync` 语义。

正确形状是「应用直接用 SDK 读写对象」，把「目录」这件事留给真正的文件存储。要用 CSI，只用于**只读、顺序读、大文件**的场景（如模型权重、静态资源），并在 StorageClass 注释里写死这个约束。
:::

## 参考资料

- 卷：https://kubernetes.io/zh-cn/docs/concepts/storage/volumes/
- PV/PVC：https://kubernetes.io/zh-cn/docs/concepts/storage/persistent-volumes/
- StorageClass：https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/
