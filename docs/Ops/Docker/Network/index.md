# Docker 网络

::: info 进阶指引
用户自定义网络支持容器名 DNS 解析；Docker 防火墙后端支持 iptables（默认）与 nftables（可在 daemon.json 配置 `firewall-backend` 切换）。深入原理与排障见「网络模式深入」。
:::

容器间的互联和通信以及端口映射，容器IP变动时可以通过服务名直接网络通信而不受到影响。

本机网络：使用ifconfig查看本地网络：

- docker0：docker的网络
- eth0：本机的外网地址
- lo口：本地环回地址

使用brctl命令来查看docker0(没有这个命令的下载`yum -y install bridge-utils`)

```shell
brctl show
```

清空本机docker环境：

```shell
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -aq)
```

## veth-pair 技术

veth-pair 就是一堆的虚拟设备接口，他们都是成对出现的，一端连接着协议，一端连接着彼此。使得它充当了一个桥梁的作用。

1. 首先来启动两个tomcat容器：

   提示：选择tomcat7是因为这个镜像包含了ip addr 等常用命令！

   ```shell
   docker run -d -P --name=tomcat01 tomcat:7
   docker run -d -P --name=tomcat02 tomcat:7
   ```

2. 启动机器之后，查看容器ip，通过容器的ip 去ping宿主机ip，发现是通的。

   ```shell
   docker exec -it tomcat01 ip addr
   ```

   ![img202406152222328](assets/img202406152222328.png)

   ```shell
   ping 172.17.0.2
   ```

   ![img202406152222629](assets/img202406152222629.png)

每启动一个docker容器，docker就会给docker容器分配一个ip，安装docker之后，会产生一个叫docker0的网卡，这里使用的就是veth-pair技术。

使用ip addr命令，查看网卡：

![img202406152223442](assets/img202406152223442.png)

## Docker 网络

tomcat01和tomcat02是共用的同一个路由器，即docker0。所有的容器在不指定我网络的情况下，都是docker0路由的，docekr会给容器分配一个默认IP。

docker网络就是下面这个网络模型所描述的。（docker所有的网络接口都是虚拟的，虚拟的转发效率高）

![img202406152233999](assets/img202406152233999.png)

![img202406152233576](assets/img202406152233576.png)

查看网络：

```shell
docker container inspect tomcat1
```

Docker 为每个容器分配唯一IP，使用 **容器ip+容器端口**可以互相访问。

## 网络模式

- **Host模式**：使用`--network host`指定，容器不会虚拟出自己的网卡，配置主机的IP等，而是使用宿主机的IP和端口
- **Container模式**：使用`--network container:Name`或者容器ID指定，新创建的容器不会创建自己的网卡，配置自己的IP，而是和一个指定的容器共享IP、端口范围等 (一般不用)
- **None模式**：使用`--network none`指定，该模式关闭了容器的网络功能。容器有独立的Network namespace，但并没有对其进行任何网络设置，如分配veth pair和网桥连接，IP等 (一般不用)
- **Bridge模式**：使用`--network bridge`指定，默认为该模式 (桥接，自己创建也是用它)，此模式会为每一个容器分配，设置IP等，并将容器连接到一个docker0 的虚拟网桥，通过docker 0 网桥以及iptables nat 表配置与宿主机通信。

**注意**：docker容器内部的ip是有可能发生变化的

## 列出docker网卡

列出docker网卡：

```shell
docker network ls
```

## 查看网卡详细信息

查看网卡详细信息：

```shell
docker network inspect 网卡名字
```

## 创建自定义网络的容器

直接启动命令， --net bridge，就是docker0（默认）

```shell
docker run -d -P --name=tomcat01 --net bridge tomcat
```

docker0特点：默认，域名不能访问，--link不建议使用

创建一个bridge：

```shell
docker network create --driver bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 testnet
docekr network ls
```

![img202406152235748](assets/img202406152235748.png)

发布两个在自己创建的网络里的容器：

```shell
docker run -d -P --name=tomcat01-net --net=testnet tomcat:7
docker run -d -P --name=tomcat02-net --net testnet tomcat:7
```

![img202406152235730](assets/img202406152235730.png)

```shell
docker exec -it tomcat01-net ping -c 3 IP
docker exec -it tomcat01-net ping -c 3 tomcat02-net
```

提示，ping -c可以自定义ping的次数

![img202406152236368](assets/img202406152236368.png)

## 连接一个容器到网络

```shell
docker network connect [参数] NETWORK CONTAINER
```

## 断开一个容器与网络的连接

```shell
docker network disconnect [参数] NETWORK CONTAINER
```

## 删除网络

```shell
docker network rm xxx网络名字
```

::: tip 进阶阅读
Docker 网络基于 Linux 网络命名空间与 iptables 等机制，网络分层与排查方法见 [网络基础](../Network/Layering/index.md) 与 [网络排查方法论](../Network/Troubleshoot/index.md)。
:::
