# Docker 安全加固

容器不是天然的沙箱：它共享宿主机内核，任何隔离配置的疏漏都可能放大为宿主级风险。安全加固的目标是让「镜像可信、权限最小、逃逸困难、密钥不落盘」。

::: info 适用版本
本节基于 Docker Engine 29.x。Docker 29.5 起，rootless 模式默认使用 gvisor-tap-vsock 网络驱动；Docker 29.6 提供镜像 attestation（SLSA provenance、SPDX SBOM）查询接口。
:::

## 威胁模型

在动手加固前，先明确要防什么：

| 威胁 | 示例 | 对应措施 |
| --- | --- | --- |
| 供应链攻击 | 恶意镜像、依赖投毒 | 锁版本/digest、镜像扫描、SBOM、签名 |
| 容器逃逸 | 漏洞利用后突破命名空间 | 非 root、cap-drop、seccomp、只读根文件系统 |
| 密钥泄露 | 环境变量里放密码 | secrets、不写进镜像层 |
| 横向移动 | 容器访问宿主机或内网其他机器 | 最小网络暴露、不用 host 网络 |
| 资源耗尽 | 容器吃满 CPU/内存拖垮宿主 | 资源限制、pids-limit |

## 镜像安全

### 固定版本与 digest

```dockerfile
FROM node:24-alpine@sha256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

`latest` 会漂移；发布前用固定 digest，升级时显式更新并重新扫描。

### 漏洞扫描

内置的 Docker Scout 可以查看镜像漏洞：

```shell
docker scout quickview myapp:1.4.2
docker scout cves myapp:1.4.2 --only-severity critical,high
docker scout sbom myapp:1.4.2
```

也可在 CI 中用 Trivy、Grype 等工具扫描，扫描结果不通过就阻断发布。

### 构建期 attestation

构建时生成 provenance（来源）和 SBOM（软件物料清单）：

```shell
docker build --provenance=true --sbom=true -t myapp:1.4.2 .
```

这些信息随镜像一起推送，审计时可以用 `docker buildx imagetools inspect` 查看，Docker 29.6 也提供了 attestation 查询接口。

### 镜像签名

签名保证「这个镜像是我们发布的」。推荐使用 Sigstore cosign 等现代方案：

```shell
cosign sign myregistry.example.com/team/app:1.4.2
```

部署侧校验签名后再拉取。旧的 Docker Content Trust（DCT）机制仍可配置 `DOCKER_CONTENT_TRUST=1`，但新项目建议直接上 cosign。

## 运行时加固

### 非 root 运行

```shell
docker run -d --user 10001:10001 myapp:1.4.2
```

更好的做法是在 Dockerfile 里声明 `USER`，让默认行为就是非 root。

### 最小化 capabilities

```shell
docker run -d \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  myapp:1.4.2
```

先丢弃全部能力，再按需加回（如监听 80 端口需要 `NET_BIND_SERVICE`）。不要轻易使用 `--privileged`，它等于关闭大部分隔离。

### 禁止提权与自定义 seccomp

```shell
docker run -d \
  --security-opt=no-new-privileges:true \
  --security-opt seccomp=/path/to/custom-seccomp.json \
  myapp:1.4.2
```

`no-new-privileges` 阻止容器内进程通过 setuid 等方式提权。默认 seccomp 已拦截常见危险系统调用；自定义 profile 需要先了解业务需要的 syscall，不要图省事直接 `seccomp=unconfined`。

### 只读根文件系统

```shell
docker run -d \
  --read-only \
  --tmpfs /tmp:rw,size=64m \
  myapp:1.4.2
```

根文件系统只读后，容器即使被攻破也无法篡改自身文件；需要写的地方用 tmpfs 或卷单独挂载。

### 资源限制

```shell
docker run -d \
  --memory=512m \
  --cpus=0.5 \
  --pids-limit=100 \
  --init \
  myapp:1.4.2
```

- `--memory` / `--cpus`：防止单容器拖垮宿主。
- `--pids-limit`：限制进程数，防 fork 炸弹。
- `--init`：让 init 进程回收僵尸进程，避免 PID 1 行为异常。

## 守护进程与宿主安全

### 不要给业务容器挂 Docker socket

```shell
# 高危，不要用于业务容器
docker run -v /var/run/docker.sock:/var/run/docker.sock ...
```

挂载 socket 等于把宿主机的 Docker 控制权交给容器。确有管理需求时，用受限 API 代理或管理平台，而不是直接暴露 socket。

### 限制远程 API 暴露

默认 Docker 只监听本地 Unix socket。需要远程访问时：

- 使用 TLS 证书认证（`--tlsverify --tlscacert --tlscert --tlskey`）；
- 或通过 SSH 访问：`docker context create remote --docker host=ssh://user@host`；
- 不要直接 `-H tcp://0.0.0.0:2375` 无认证暴露。

### Rootless Docker

以普通用户运行整个 Docker 引擎，守护进程本身也没有 root 权限：

```shell
dockerd-rootless-setuptool.sh install
```

前提是系统安装了 `uidmap`，并配置好 rootless 网络依赖（29.5 起默认 gvisor-tap-vsock）。rootless 适合个人开发机和无法信任 root 引擎的环境，生产环境要结合自己的安全基线评估。

### 用户命名空间重映射

在 `daemon.json` 开启 `userns-remap` 后，容器内 root 会映射为宿主普通用户，进一步降低逃逸影响：

```json [daemon.json]
{
  "userns-remap": "default"
}
```

注意：开启后卷的权限映射会变化，需要重新规划挂载目录属主。

## 网络加固

- 端口只绑定回环：`-p 127.0.0.1:8080:80`。
- 避免 `--network host`，缩小攻击面。
- 敏感服务放在自定义 bridge 网络，不发布端口，由反向代理统一入口。
- 生产环境配合宿主防火墙（ufw、nftables、云安全组）双保险。

## 易错点

::: danger 常见错误
1. 为了省事直接 `--privileged` 或 `seccomp=unconfined`，隔离形同虚设。
2. 密码、token 写进 `ENV` 或 `docker run -e` 命令历史，任何能读镜像层的人都能拿到。
3. 镜像只扫一次就完事，基础镜像和依赖每天都会爆新 CVE，需要持续扫描。
4. 给业务容器挂载 docker.sock，等于把宿主机交给容器。
5. `--read-only` 后没有给应用的数据目录挂可写卷，应用启动即报错。
6. 开启 `userns-remap` 前没测试卷权限，数据库写不进去。
:::

## 验证方式

1. 检查隔离配置，确认输出符合预期：

```shell
docker inspect myapp --format '{{.HostConfig.Privileged}} {{.HostConfig.CapDrop}} {{.HostConfig.ReadonlyRootfs}}'
```

2. `docker run --rm --security-opt=no-new-privileges:true --cap-drop=ALL alpine sh -c "id && capsh --print"`，确认能力列表为空。
3. `docker scout quickview myapp:1.4.2` 能看到漏洞概览。
4. 查看引擎安全选项，确认 seccomp/apparmor 已启用：

```shell
docker info --format '{{json .SecurityOptions}}'
```

5. 容器内 `touch /test` 在只读模式下应报错。

## 参考资料

- Docker 安全最佳实践：https://docs.docker.com/engine/security/
- Docker Scout：https://docs.docker.com/scout/
- Rootless 模式：https://docs.docker.com/engine/security/rootless/
- OCI 运行时安全（runC seccomp）：https://github.com/moby/moby/tree/master/profiles/seccomp
