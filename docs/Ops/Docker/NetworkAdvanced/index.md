# Docker 网络模式深入

Docker 网络解决的是容器之间、容器与宿主机之间、容器与外部世界之间如何通信的问题。本节在基础网络命令之上，深入讲解网络模式原理、嵌入式 DNS、防火墙后端以及排障方法。

::: info 适用版本
本节基于 Docker Engine 29.x（当前最新稳定版 29.7.2）。Docker 支持 iptables（默认）与 nftables 两种防火墙后端，可通过 daemon 配置切换。
:::

## 容器网络模型

Docker 使用 libnetwork 实现 CNM（Container Network Model，容器网络模型）。核心概念：

| 概念 | 说明 |
| --- | --- |
| Sandbox | 容器的网络命名空间，隔离网卡、路由、防火墙规则 |
| Endpoint | 容器接入网络的连接点（veth 的一端） |
| Network | 一组 Endpoint 的集合，决定连通性和隔离性 |

每个容器默认有独立的网络命名空间，所以容器内的 `eth0`、`localhost` 与宿主机不共享。

## 网络驱动对比

| 驱动 | 使用场景 | 是否跨主机 | 容器是否直接暴露到局域网 |
| --- | --- | --- | --- |
| `bridge` | 单机默认，端口映射访问 | 否 | 否（NAT 转发） |
| `host` | 追求性能、需要直接复用宿主机端口 | 否 | 是（共享宿主网络栈） |
| `none` | 完全禁用网络，用于离线任务 | 否 | 否 |
| `overlay` | Swarm 跨主机服务 | 是 | 否 |
| `macvlan` / `ipvlan` | 容器使用物理网段独立 IP | 部分 | 是 |

## bridge：默认与自定义

默认 `bridge` 网络只有一个，容器之间靠 IP 通信，不能直接用容器名解析。生产建议创建用户自定义 bridge 网络：

```shell
docker network create --driver bridge --subnet=172.28.0.0/16 app-net
```

```shell
docker run -d --name web --network app-net nginx:stable-alpine
docker run -d --name api --network app-net myapp:1.4.2
```

用户自定义 bridge 网络的两个关键增强：

1. **内嵌 DNS**：同网络内的容器可以直接用容器名访问，如 `http://api:8080`。
2. **自动清理**：容器退出时自动从网络断开，默认 bridge 不会。

端口映射的本质是在宿主机上做 DNAT（目标地址转换）：

```shell
docker run -d -p 127.0.0.1:8080:80 --name web nginx:stable-alpine
```

只绑定到 `127.0.0.1` 可以避免端口暴露到整个网卡，生产环境值得养成习惯。

## host：共享宿主网络栈

`--network host` 让容器直接使用宿主机的网络命名空间，没有 NAT 和 veth 开销，性能最好，但：

- 容器监听端口直接占用宿主端口，端口冲突由应用自己负责。
- 没有网络隔离，容器可以访问宿主机所有网络接口。
- 只支持 Linux；macOS 的 Docker Desktop 是虚拟机，`host` 网络行为不同。

适合对延迟敏感、端口本来就要直通的场景，如部分网关和高性能代理。

## none：彻底断网

```shell
docker run --rm --network none alpine sleep 30
```

容器没有网络接口，适合离线计算、签名验证等安全敏感任务，也可以配合 `--cap-drop=ALL` 做加固。

## macvlan / ipvlan：容器直连物理网段

让容器拥有局域网内独立 IP，像普通主机一样被访问：

```shell
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 macvlan-net
```

```shell
docker run -d --network macvlan-net --ip 192.168.1.100 nginx:stable-alpine
```

注意：macvlan 下容器与宿主机之间默认无法直接通信（宿主机没有对应 MAC），需要额外建子接口。ipvlan 基于 IP 而不是 MAC 地址，对交换机 MAC 表更友好，但两种模式都要求物理网络配合，生产使用前先在测试网段验证。

## overlay：跨主机（Swarm）

Swarm 集群中，`overlay` 网络让不同节点上的服务通过服务名互通：

```shell
docker network create -d overlay --attachable app-overlay
```

VXLAN 封装流量，默认带加密选项（`-o encrypted=true` 需要额外配置）。Kubernetes 场景通常由 CNI 插件实现类似能力，普通单机部署不需要 overlay。

## 防火墙后端：iptables 与 nftables

Docker 通过宿主防火墙规则实现端口映射和网络隔离：

- 默认使用 `iptables`。
- 可在 `/etc/docker/daemon.json` 中切换为 `nftables`：

```json [daemon.json]
{
  "firewall-backend": "nftables"
}
```

```shell
sudo systemctl restart docker
```

使用 nftables 时，Docker 不再自行开启 IP 转发，需要系统自己配置转发规则，否则容器出网会异常。Docker 29.7 系列持续修复 nftables 兼容性问题，选择 nftables 时建议保持引擎更新。

## 排障工具与方法

查看网络和连接：

```shell
docker network ls
docker network inspect app-net
docker network inspect app-net --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}'
```

进入网络命名空间抓包、测连通性，推荐使用 netshoot 工具箱：

```shell
docker run --rm -it --network app-net nicolaka/netshoot
```

在工具箱里：

```shell
ping api
dig api
tcpdump -i eth0 -n port 8080
```

## 易错点

::: danger 常见错误
1. 两个容器分别挂在默认 bridge 网络上，以为能像自定义网络一样用容器名互访，结果 DNS 解析失败。
2. `--network host` 下容器内 `localhost` 就是宿主机，端口冲突后排查半天。
3. macvlan 容器无法访问宿主机服务，误以为是网络故障。
4. 修改 `daemon.json` 的防火墙后端后不重启引擎，配置不生效。
5. 自定义网络没有规划子网，多个项目网络 IP 段重叠，静态 IP 互相冲突。
6. 生产端口映射写成 `-p 8080:80` 而非 `-p 127.0.0.1:8080:80`，服务暴露到公网。
:::

## 验证方式

1. `docker network ls` 能看到新建的 `app-net`。
2. 同一网络内 `docker exec api ping web` 能通。
3. `docker network inspect app-net` 能看到两个容器都在线。
4. 宿主机 `curl http://127.0.0.1:8080` 返回容器服务内容。
5. `docker run --rm -it --network app-net nicolaka/netshoot` 内 `getent hosts web` 能解析出容器 IP。

## 参考资料

- Docker 网络概述：https://docs.docker.com/engine/network/
- 数据包过滤与防火墙：https://docs.docker.com/engine/network/packet-filtering-firewalls/
- macvlan 驱动：https://docs.docker.com/engine/network/drivers/macvlan/
- 使用 bridge 网络：https://docs.docker.com/engine/network/drivers/bridge/
