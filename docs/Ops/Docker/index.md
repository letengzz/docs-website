# Docker

- [Docker 概述](Overview/index.md)
- [Docker 容器与沙盒](ContainersSandboxes/index.md)
- [Docker 安装与卸载](InstallUninstall/index.md)
- [Docker 进程命令](ProcessCommand/index.md)
- [Docker 镜像](Images/index.md)
- [Docker 容器](Containers/index.md)
- [Docker 数据卷](Volumes/index.md)
- [Dockerfile](Dockerfile/index.md)
- [Docker 网络](Network/index.md)
- [Docker Compose](DockerCompose/index.md)
- [Docker 管理平台](ManagePlatform/index.md)
- [Docker 监控平台](CIG/index.md)

拓展：

- [Docker镜像To阿里云](DockerToAli/index.md)
- [Docker 常见错误](Errors/index.md)

进阶：

- [Dockerfile 最佳实践](BestPractices/index.md)
- [多阶段构建](Multistage/index.md)
- [Docker Compose 进阶](ComposeAdvanced/index.md)
- [网络模式深入](NetworkAdvanced/index.md)
- [数据卷与挂载最佳实践](VolumesAdvanced/index.md)
- [容器监控](Monitor/index.md)
- [安全加固](Security/index.md)
- [Docker 与 CI/CD 集成](CIIntegration/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 两种典型应用的镜像形态：Go 与 Python

镜像体积与构建速度的差异，主要来自**运行时依赖**。同一套多阶段构建思路，对编译型语言与解释型语言的效果差别很大。

| | Go（编译型） | Python（解释型） |
| --- | --- | --- |
| 运行阶段需要什么 | **静态二进制 + 证书** | 解释器 + 依赖包 + 部分编译工具链（安装期） |
| 基础镜像 | `scratch` 或 `gcr.io/distroless/static` | `python:*-slim` |
| 典型体积 | **5~20 MB** | 100~250 MB |
| 依赖内联 | 编译进二进制 | 若用 Nitro（Nuxt），服务端依赖也能内联 |
| 冷启动 | 毫秒级 | 数百毫秒~秒级 |

::: danger 注意：三个跨语言都必须做到的点
1. **非 root 运行**（`USER`）：容器以 root 跑时，一旦有文件写入漏洞，逃逸影响面完全不同。
2. **`PYTHONUNBUFFERED=1`（Python）/ 不缓冲 stdout**：不设时容器日志会被缓冲，**进程被 kill 时缓冲区里的日志全部丢失**——这是「容器里看不到日志」的第一原因。
3. **依赖层与代码层分开 `COPY`**：否则改一行业务代码就要重装全部依赖，构建时间从 20 秒变成 5 分钟。

另加一条常被忽略的：**不要 `COPY . .`**，用 `.dockerignore` 排除 `.env`、`.git`、测试数据——否则凭据会被打进镜像层，且**即使后续删除也在历史层里可恢复**。
:::

::: tip 两个可对照的完整 Dockerfile
- [Go 微服务实战](../../Backend/GoMicroservices/Practice/index.md)：从 `docker-compose` 起依赖，到静态二进制镜像
- [Python Web 实战](../../Backend/PythonWeb/Practice/index.md)：多阶段构建、`HEALTHCHECK`、Gunicorn + uvicorn worker 的启动命令

两者的共同点是**构建阶段与运行阶段严格分离**，运行镜像里只留运行时需要的东西。
:::

## 相关专题

- [Ansible 自动化运维](../Ansible/index.md)：批量安装 Docker 引擎、下发 compose 文件与容器状态验收
- [Terraform](../Terraform/index.md)：把「云主机 + 网络 + 对象存储」这类底座资源交给 IaC，机器建好后再由 CI/CD 拉起容器
- [Kubernetes](../Kubernetes/index.md)：从单机容器到集群编排
- [IDE 配置 · 远程开发与容器化环境](../../Tools/IDE/RemoteDev/index.md)：用 `devcontainer.json` 把开发环境也容器化——注意**开发容器 ≠ 生产镜像**，两者追求的目标相反（开发要全，生产要小）

## 相关专题与分工

- [云原生与服务托管](../CloudNative/index.md)：本专题讲**镜像与运行时本身**——Dockerfile 怎么写、层缓存怎么利用、多阶段构建怎么把镜像做小；云原生专题讲**镜像构建好之后的事**——镜像怎么推进云仓库、函数按需拉取与缓存怎么配，以及**为什么有些负载不该上容器**（长连接、极高并发、需要特殊内核能力的场景）。一句话：本专题负责「造镜像」，该专题负责「用镜像」。
