# Docker 概述

Docker 是一个基于 LXC 的开源应用容器引擎，基于 Go 语言 并遵从 Apache2.0 协议开源。

Docker 可以让开发者打包他们的应用以及依赖包到一个轻量级、可移植的容器中，然后发布到任何流行的 Linux 机器上，也可以实现虚拟化。

Docker 从 17.03 版本之后分为 CE (Community Edition: 社区版) 和 EE (Enterprise Edition: 企业版)

Docker 官网：https://www.docker.com

Docker 中文库：https://www.docker.org.cn/

::: info 版本现状（2026-08 核对）
当前最新稳定版为 Docker Engine 29.7.x（29.7.2，2026-08-05 发布），Docker Compose 为 v2.40+。BuildKit 已是默认构建器；Docker Engine 29.2 起全新安装默认使用 containerd 镜像存储。
:::

![](assets/img202406071302358.png)

## Docker 应用场景

Docker 应用场景：

- Web 应用的自动化打包和发布。
- 自动化测试和持续集成、发布。
- 在服务型环境中部署和调整数据库或其他的后台应用。
- 从头编译或者扩展现有的 OpenShift 或 Cloud Foundry 平台来搭建自己的 PaaS 环境。

![](assets/img202406062310340.png)

## Docker 架构

![](assets/img202406062312498.png)

- Docker Daemon：Docker Daemon，即 Dockerd，Docker 守护进程，其监听着 Docker API 请求并管理Docker对象，例如镜像、容器、网络和卷。

  守护进程还可以与其他守护进程通信以管理 Docker 服务。

- 镜像 Image：Docker 镜像是用于创建 Docker 容器的模板。一个镜像可以创建很多容器。

- 容器 Container：Docker 容器是镜像运行时的实体。就像面向对象编程中类的实例。一个类可以创建出 N多个实例，那么一个镜像同样也可以创建出 N 多个容器。每个处于运行状态的容器中都包含着一个或多个相关的应用，且它的运行不会干扰到其它容器。因为它们之间是相互隔离的。

- 仓库 Repository：Docker 镜像仓库用来保存相关的一组镜像，这组镜像具有相同的镜像名称，都与镜像仓库名称相同。仓库根据其中的镜像是否可以被公开共享，可以分为公开库(Public)与私有库(Private)。

- 标签 Tag：通过`<repository>:<tag>`即可唯一定位一个镜像。即镜像标签其实就是镜像仓库中用于区分各个镜像的一种标识，同一仓库中的镜像具有不同的标签。

- 镜像中心 Registry：Docker 的镜像中心中存放着很多由官方、其他机构或个人创建的 Docker 仓库，
  Docker用户可以直接从这些仓库中 pull 需要的镜像，也可以将自己制作的镜像 push 到 Docker 镜像中心相应的仓库中。
  最常用的镜像中心是Docker官方的Docker Hub：https://hub.docker.com

## Docker Hub

Docker Hub (https://hub.docker.com) 提供了庞大的镜像集合供使用。一个 Docker Registry 中可以包含多个仓库(Repository)，每个仓库可以包含多个标签 (Tag)，每个标签对应一个镜像。通常，一个仓库会包含同一个软件不同版本的镜像，而标签就常用于对应该软件的各个版本。
可以通过 `<仓库名>:<标签>` 的格式来指定具体是这个软件哪个版本的镜像。如果不给出标签，将以 latest 作为默认标签。

## Docker和VM的区别

1. Docker有着比虚拟机更少的抽象层
2. Docker利用的是宿主机的内核，VM需要的是Guest OS
3. VM(VMware)在宿主机器、宿主机器操作系统的基础上创建虚拟层、虚拟化的操作系统、虚拟化的仓库，然后再安装应用
4. Container(Docker容器)，在宿主机器、宿主机器操作系统上创建Docker引擎，在引擎的基础上再安装应用。
5. 新建一个容器的时候，docker不需要像虚拟机一样重新加载一个操作系统，避免引导。docker是利用宿主机的操作系统，省略了这个复杂的过程，秒级，虚拟机是加载Guest OS ，这是分钟级别的

![](assets/img202406062317947.png)

## Docker 特性

- 文件系统隔离：每个进程容器运行在一个完全独立的根文件系统里。
- 资源隔离：系统资源，像CPU和内存等可以分配到不同的容器中，使用cgroup。
- 网络隔离：每个进程容器运行在自己的网路空间，虚拟接口和IP地址。
- 日志记录：Docker将收集到和记录的每个进程容器的标准流（stdout/stderr/stdin），用于实时检索或者批量检索。
- 变更管理：容器文件系统的变更可以提交到新的镜像中，并可重复使用以创建更多的容器。无需使用模板或者手动配置。
- 交互式shell：Docker可以分配一个虚拟终端并且关联到任何容器的标准输出上，例如运行一个一次性交互shell。

## Docker 局限性

Docker用于应用程序时是最有用的，但并不包含数据。日志、数据库等通常放在Docker容器外。一个容器的镜像通常都很小，不用和存储大量数据，存储可以通过外部挂载等方式使用，比如：NFS、ipsan、MFS等 ，或者docker命令 ，-v映射磁盘分区。
总之，docker只用于计算，存储交给别人。

## Docker 引擎

### 引擎架构

- Docker Client：Docker 客户端，Docker 引擎提供的 CLI 工具，用于用户向 Docker 提交命令请求。
- Dockerd：Dockerd，即 Docker Daemon。在现代 Dockerd 中的主要包含的功能有镜像构建、镜像管理、REST API、核心网络及编排等。其通过 gRPC 与 Containerd 进行通信。
- Containerd：Containerd，即 Container Daemon，该项目的主要功能是管理容器的生命周期。不过，其本身并不会去创建容器，而是调用 Runc 来完成容器的创建。
  Docker 公司后来将 Containerd 项目捐献给了 CNCF（云原生基金会）。
- Runc：Runc，Run Container，是 OCI（开放容器倡议基金会）容器运行时规范的实现，Runc 项目的目标之一就是与 OCI 规范保持一致。
  所以，Runc 所在层也称为 OCI 层。这使得 Docker Daemon 中不用再包含任何容器运行时的代码了，简化了 Docker Daemon。
  Runc 只有一个作用—创建容器，其本质是一个独立的容器运行时 CLI 工具。其在 fork 出一个容器子进程后会启动该容器进程。在容器进程启动完毕后，Runc 会自动退出。

![](assets/img202406062327486.png)

### Shim

Shim (垫片) 是实现"Daemonless Container (无 Docker Daemon 与 Container Daemon 容器)"不可或缺的工具，使容器与 Docker Daemon 解耦，使得 Docker Daemon 的维护与升级不会影响到运行中的容器。
每次创建容器时，Containerd 同时会 fork 出 Runc 进程与 Shim 进程。当 Runc 自动退出之前，会先将新容器进程的父进程指定为相应的 Shim 进程。

- 保持所有 STDIN 与 STDOUT 流的开启状态，从而使得当 Docker Daemon 重启时，容器不会因为 Pipe 的关闭而终止。

- 将容器的退出状态反馈给 Docker Daemon。

## Docker 底层技术

Linux 命名空间、控制组和 UnionFS 三大技术支撑了目前 Docker 的实现，也是 Docker 能够出现的最重要原因。

- 命名空间(namespace)：命名空间（namespaces）是 Linux 为我们提供的用于分离进程树、网络接口、挂载点以及进程间通信等资源的方法。在日常使用 Linux 或者 macOS 时，我们并没有运行多个完全分离的服务器的需要，但是如果我们在服务器上启动了多个服务，这些服务其实会相互影响的，每一个服务都能看到其他服务的进程，也可以访问宿主机器上的任意文件，这是很多时候我们都不愿意看到的，我们更希望运行在同一台机器上的不同服务能做到完全隔离，就像运行在多台不同的机器上一样。

- 控制组(cgroups)：Linux 的 CGroup 能够为一组进程分配资源，也就是我们在上面提到的 CPU、内存、网络带宽等资源
  实际上 Docker 是使用了很多 Linux 的隔离功能，让容器看起来像一个轻量级虚拟机在独立运行，容器的本质是被限制了的 Namespaces，cgroup，具有逻辑上独立文件系统，网络的一个进程。

- 联合文件系统(UnionFS)：UnionFS 是一种分层、轻量级并且高性能为 Linux 操作系统设计的用于把多个文件系统『联合』到同一个挂载点的文件系统服务。它支持对文件系统的修改作为一次提交来一层层的叠加，同时可以将不同目录挂载到同一个虚拟文件系统下(unite several directories into a single virtual filesystem)。

Union 文件系统是 Docker 镜像的基础。镜像可以通过分层来进行继承，基于基础镜像（没有父镜像），可以制作各种具体的应用镜像。

AUFS 即 Advanced UnionFS 其实就是UnionFS 的升级版，它能够提供更优秀的性能和效率。
AUFS 作为先进联合文件系统，它能够将不同文件夹中的层联合（Union）到了同一个文件夹中，这些文件夹在 AUFS 中称作分支，整个『联合』的过程被称为联合挂载（Union Mount）。

简单来说，一个 Image 是通过一个 DockerFile 定义的，然后使用 docker build 命令构建它。
DockerFile 中的每一条命令的执行结果都会成为 Image 中的一个 Layer。

Docker Image 是有一个层级结构的，最底层的 Layer 为 BaseImage（一般为一个操作系统的 ISO 镜像），然后顺序执行每一条指令，生成的 Layer 按照入栈的顺序逐渐累加，最终形成一个 Image。

每一次都是一个被联合的目录：

![](assets/img202406062336855.png)

![](assets/img202406062337979.png)

## Docker 运行原理

Docker 使用客户端-服务器 (C/S) 架构模式，使用远程API来管理和创建Docker容器。

- Docker守护进程运行在主机上， 然后通过Socket连接从客户端访问Docker守护进程。
- Docker守护进程从客户端接受命令，并按照命令，管理运行在主机上的容器。

Docker 容器通过 Docker 镜像来创建。

![](assets/img202410212153144.png)

## Docker 操作步骤

1. 启动Docker
2. 下载镜像到本地
3. 启动Docker容器实例

![image-20240615141451958](assets/img202406151414719.png)

## 相关专题

- [Kubernetes 集群](../Kubernetes/index.md)
