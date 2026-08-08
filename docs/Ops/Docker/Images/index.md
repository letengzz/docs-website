# Docker 镜像

镜像是一种轻量级、可执行的独立软件包，也可以说是一个精简的操作系统。

镜像中包含应用软件及应用软件的运行环境。

具体来说镜像包含运行某个软件所需的所有内容，包括代码、库、环境变量和配置文件等。几乎所有应用，直接打包为 Docker 镜像后就可以运行。

由于镜像的运行时是容器，容器的设计初衷就是快速和小巧，所以镜像通常都比较小，镜像中不包含内核，其共享宿主机的内核；镜像中只包含简单的 Shell，或没有 Shell。

## 镜像仓库分类

镜像中心中存储着大量的镜像仓库 Image Repository，每个镜像仓库中包含着大量相关镜像。根据这些镜像发布者的不同，形成了四类不同的镜像仓库。

### Docker Official Image

Docker 官方镜像仓库。该类仓库中的镜像由 Docker 官方构建发布，代码质量较高且安全，有较完善的文档。该类仓库中的镜像会及时更新。一般常用的系统、工具软件、中间件都有相应的官方镜像仓库。例如，Zookeeper、Redis、Nginx 等。
官方镜像仓库的名称`<repository>`一般直接为该类软件的名称`<software-name>`。

### Verified Publisher

已验证发布者仓库。该类仓库中的镜像由非 Docker 官方的第三方发布。但该第三方是由 Docker 公司审核认证过的，一般为大型企业、团体或组织。审核通过后，Docker 公司会向其颁发"VERIFIED PUBLISHER"标识。这种仓库中镜像的质量还有有保证的。
除了官方镜像仓库，其它都是非官方镜像仓库。非官方镜像仓库名称`<repository>`一般由发布者用户名与软件名称两部分构成，
形式为：`<username>/<software-name>`。

### Sponsored OSS

由 Docker 公司赞助开发的镜像仓库。该类仓库中的镜像也由非 Docker 官方的第三方发布，但该镜像的开发是由 Docker 公司赞助的。该类型的第三方一般为个人、团队或组织。这种仓库中镜像的质量也是有保证的。

### 无认证仓库

没有以上任何标识的仓库。这种仓库中镜像的质量良莠不齐，质量上无法保证，在使用时需谨慎。

## 第三方镜像中心

镜像中心默认使用的都是 Docker 官方的 Docker Hub。不过，镜像中心是可配置的，可以使用指定的第三方镜像中心。
对于第三方镜像中心中的仓库名称`<repository>`由三部分构成：`<domain-name>/<username>/<software-name>`。
其中的`< domain-name >`指的是第三方镜像中心的域名或 IP。

## 镜像定位

对于任何镜像，都可通过`<repository>:<tag>`进行唯一定位。其中`<tag>`一般称为镜像的版本号。

`<tag>`中有一个比较特殊的版本——latest。如果不指定，默认`<tag>`即为 latest。

不过，虽然其字面意思是最新版，一般其也的确存放的是最新版，但并不能保证其真的就是最新版。

## 搜索镜像

可以使用http://hub.docker.com，搜索想要的镜像

从网络中搜索镜像：

```shell
docker search 镜像名称
```

- NAME：镜像名称
- DESCRIPTION：描述
- STARS：点赞数
- OFFICIAL：是否为官方
- AUTOMATED：是否是自动构建的

过滤检索结果：

- 仅查询出官方提供的镜像：

  ```shell
  docker search 镜像名称 --filter is-official=true
  ```

- 限制检索数量 (默认 docker search 显示 25 条检索结果)：

  ```shell
  docker search 镜像名称 --limit=检索数量
  ```

## 拉取镜像

从Docker仓库下载镜像到本地，镜像名称格式为 docker pull 名称:版本号，如果版本号不指定则是最新的版本lastest。

**格式**：

```shell
docker pull 镜像名称:版本号
```

**例**：

- 下载最新版本centos：

  ```shell
  docker pull centos
  ```

- 下载centos版本7：

  ```shell
  docker pull centos:7
  ```

- 下载tomcat：

  ```shell
  docker pull hub.c.163.com/library/tomcat:latest
  ```

报错`TLS handshake timeout`：网络原因导致超时，尝试多pull几次。

**可简化拉取过程中的日志输出**：

```shell
docker pull -q 镜像名称
```

**通过digest拉取**：digest，是镜像内容的一个 Hash 值，即所谓的 Content Hash（内容散列）。只要镜像内容发生了变更，其内容散列值就一定会发生改变。

注意：digest 是包含前面的 sha256 的，表示该 digest 的产生所采用的 Hash 算法是 SHA256。

```shell
docker pull <repository>@<digest>
```

从 Docker Hub 中具体镜像中可查看到其 digest：

![](assets/img202406151345000.png)

![](assets/img202406151345750.png)

## 删除本地镜像

镜像通过`<repository>:<tag>`指定。如果省略要删除镜像的 tag，默认删除的是 lastest 版本。

删除指定本地镜像：

```shell
docker rmi 镜像ID或名称
```

删除所有本地镜像：

```shell
docker rmi -f  `docker images -q`
```

删除多个镜像：多个要删除的镜像间使用空格分隔

删除包含某个字符的所有容器：

```shell
docker rm $(docker ps -a | grep 'demo'| awk '{print $1 }')
```

强制删除镜像：

```shell
docker rmi -f 镜像ID或名称
```

## 提交镜像

格式：

```shell
docker commit  -a "xxx"  -c "xxx" 镜像ID或名字 : 版本
```

参数：

- -a：提交的镜像作者
- -c：使用Dockerfile指令来创建镜像
- -m：提交时的说明文字

## 复制镜像并修改名称

```shell
docker tag  镜像名:版本   新镜像名:版本
```

## 压缩镜像

```shell
docker save -o centos.tar centos:7
```

## 加载镜像

```shell
docker load -i /root/centos.tar
```

## 查看镜像

说明：查看镜像按照镜像被创建的时间由近及远排序

查看镜像的变更历史：

```shell
docker history 镜像ID或名称
```

查看本地所有的镜像：

```shell
docker images
```

- REPOSITORY：镜像名称
- TAG：标签(版本版本号)
- IMAGE ID：镜像ID
- CREATED：创建时间
- SIZE：镜像大小

查看指定镜像的信息：

```shell
docker images 镜像名称
```

查看完整镜像ID：默认的 docker images 显示的镜像 id 是经过截取后的显示结果，仅显示了前 12 位。使用 `--no-trunc` 参数后显示的是完成的镜像 id。

```shell
docker images --no-trunc
```

查看镜像 digest：

- 查看所有镜像 digest：

  ```shell
  docker images --digests
  ```

- 查看指定镜像 digest：

  ```shell
  docker images  镜像名称 --digests
  ```

仅显示镜像 ID：-q 选项可仅显示本地所有镜像的 ImageID。该主要是将来与其它命令联合使用。

```shell
docker images -q
```

过滤镜像：

```shell
docker images -f 过滤条件
```

- dangling=true：用于过滤出悬虚镜像，即没有 Repository 与 Tag 的镜像。对于悬虚镜像的REPOSITORY 与 TAG，显示的是`<none>`。
- before：用于列举出本地镜像中指定镜像创建时间之前创建的所有镜像。
- since：用于列举出本地镜像中指定镜像创建时间之后的创建的所有镜像。
- reference：用于列举出`<repository>:<tag>`与指定表达式相匹配的所有镜像。

格式化显示：项用于格式化输出 docker images 的内容，格式需要使用 GO 模板指定。

```shell
docker images --format {{.Repository}}:{{.Tag}}:{{.Size}}
```

查看镜像/容器/数据卷所占空间：

```shell
docker system df
```

## 镜像分层

Docker 镜像由一些松耦合的只读镜像层组成，Docker Daemon 负责堆叠这些镜像层，并将它们关联为一个统一的整体，即对外表现出的是一个独立的对象。

通过 docker pull 命令拉取指定的镜像时，每个 Pull complete 结尾的行就代表下载完毕了一个镜像层。

redis:latest 镜像就包含 6 个镜像层：

![](assets/img202406151401994.png)

![](assets/img202406151401845.png)

采用分层结构的优势很多，例如，每个分层都是只读的，所有对分层的修改都是以新分层的形式出现，并不会破坏原分层内容；再如，每个分层只记录变更内容，所以有利于节省存储空间等。

分层结构的最大的好处：在不同镜像间实现资源共享，即不同镜像对相同下层镜像的复用。对于 docker pull 命令，其在拉取之前会先获取到其要拉取镜像的所有 ImageID，然后在本地查找是否存在这些分层。如果存在，则不再进行拉取，而是共享本地的该分层。大大节点的存储空间与网络带宽，提升了拉取效率。

## 镜像层构成

每个镜像层由两部分构成：镜像文件系统与镜像 json 文件。这两部分具有相同的 ImageID。
镜像文件系统就是对镜像占有的磁盘空间进行管理的文件系统，拥有该镜像所有镜像层的数据内容。而镜像 json 文件则是用于描述镜像的相关属性的集合，通过 docker inspect [镜像]就可以直观看到。

## 镜像FS构成

一个 docker 镜像的文件系统 FS 由多层只读的镜像层组成，每层都完成了特定的功能。

而这些只读镜像层根据其位置与功能的不同可分为两类：基础镜像层与扩展镜像层。

![](assets/img202406151403720.png)

- 基础镜像层：所有镜像的最下层都具有一个可以看得到的基础镜像层 Base Image，基础镜像层的文件系统称为根文件系统 rootfs。而 rootfs 则是建立在 Linux 系统中“看不到的”引导文件系统bootfs 之上。

- 扩展镜像层：在基础镜像层之上的镜像层称为扩展镜像层。顾名思义，其是对基础镜像层功能的扩展。
  在 Dockerfile 中，每条指令都是用于完成某项特定功能的，而每条指令都会生成一个扩展镜像层。

- 容器层：一旦镜像运行了起来就形成了容器，而容器就是一个运行中的 Linux 系统，其也是具有文件系统的。
  容器的这个文件系统是在 docker 镜像最外层之上增加了一个可读写的容器层，对文件的任何更改都只存在于容器层。因此任何对容器的操作都不会影响到镜像本身。
  容器层如果需要修改某个文件，系统会从容器层开始向下一层层的查找该文件，直到找到为止。任何对于文件的操作都会记录在容器层。例如，要修改某文件，容器层会首先把在镜像层找到的文件 copy 到容器层，然后再进行修改。删除文件也只会将存在于容器层中的文件副本删除。

  ![](assets/img202406151406894.png)

- Docker 容器就是一个叠加后的文件系统，而这个容器层称为 Union File System，联合文件系统。

## 镜像摘要

每个镜像都有一个长度为 64 位的 16 进制字符串作为其摘要 digest。

在 docker pull 镜像结束后会给出该拉取的镜像的摘要 digest。

![](assets/img202406151407790.png)

查看摘要：

```shell
docker images 镜像名称 --digests
```

通过 docker inspect 命令可以查看指定镜像的详细信息。其中就包含该镜像的摘要信息。

![](assets/img202406151408573.png)

摘要的作用：

摘要的主要作用是区分相同`<repository>:<tag>`的不同镜像。

例如镜像 xxx:2.8 在生产运行过程中发现存在一个 BUG。现对其进行了修复，并使用原标签将其 push 回了仓库，那么原镜像被覆盖。但生产环境中遗留了大量运行中的修复前镜像的容器。此时，通过镜像标签已经无法区分镜像是修复前的还是修复后的了，因为它们的标签是相同的。此时通过查看镜像的 digest 就可以区分出修改前后版本，因为内容发生了变化，digest 一定会变。

为了确保再次拉取到的是修复后的镜像，可通过 digest 进行镜像拉取。其用法是：

```shell
docker pull <repository>@<digest>
```

先查出 zookeeper:3.8 镜像的 digest，然后将该镜像删除，然后再通过digest 对其进行拉取。

![](assets/img202406151409741.png)

不过，不方便的是，镜像的摘要需要由运维人员在本地进行手工维护。

## 分发散列值

在 push 或 pull 镜像时，都会对镜像进行压缩以减少网络带宽和传输时长。但压缩会改变镜像内容，会导致经过网络传输后，镜像内容与其 digest 不相符。出现问题。为了避免该问题，Docker 又为镜像配置了 Distribution Hash（分发散列值）。在镜像被压缩后立即计算分发散列值，然后使该值随压缩过的镜像一同进行发送。在接收方接收后，立即计算压缩镜像的分发散列值，再与携带的分发散列值对比。如果相同，则说明传输没有问题。

## 多架构镜像

Multi-architecture Image，即多架构镜像，是某`<repository>`中的某`<tag>`镜像针对不同操作系统/系统架构的不同镜像实现。即多架构镜像中包含的镜像的`<repository>:<tag>`都是相同的，但它们针对的操作系统/系统架构是不同的。

多架构镜像原理：

无论用户使用的是什么操作系统/系统架构，其通过 docker pull 命令拉取到的一定是针对该操作系统/系统架构的镜像，无需用户自己考虑操作系统/系统架构问题。Docker Hub 能够根据提交 pull 请求的 Docker 系统的架构自动选择其对应的镜像。

在 Docker Hub 中，镜像的多架构信息保存在 Manifest 文件中。在拉取镜像时，Docker会随着 pull 命令将当前 Docker 系统的 OS 与架构信息一并提交给 Docker Hub。Docker Hub 首先会根据镜像的`<repository>:<tag>`查找是否存在 Manifest。如果不存在，则直接查找并返回`<repository>:<tag>`镜像即可；如果存在，则会在 Manifest 中查找是否存在指定系统/架构的镜像。如果存在该系统/架构，则根据 Manifest 中记录的地址找到该镜像的位置。

![](assets/img202406151404029.png)

## 悬空镜像

悬虚镜像，即没有`<repository>`与`<tag>`的镜像。悬虚镜像一般都是由于某些失误操作或其它一些操作而生成的副产物，一般是要被清除掉的。如果非要使用悬虚镜像，那只能通过其 ImageID 来使用了。

![](assets/img202406151356764.png)
