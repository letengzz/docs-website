# Linux 网络命令

## 查看 IP 与路由

```shell
ip addr              # 所有网卡 IP（推荐）
ip addr show eth0    # 指定网卡
ip link              # 网卡状态
ip route             # 路由表
```

老命令 `ifconfig` 仍可用，但新系统推荐 `ip`。

## 连通性测试

```shell
ping -c 4 baidu.com        # 测连通与延迟
curl -I https://example.com    # 测试 HTTP 响应头
curl -v https://example.com    # 详细调试
wget -q -O /dev/null https://example.com
```

## 端口监听

```shell
ss -lntp               # 所有监听端口（推荐）
ss -lntp | grep 3306   # 指定端口
netstat -tlnp          # 老命令
```

`-l` 监听、`-n` 不解析域名、`-t` TCP、`-p` 显示进程。

::: tip
`ss -lntp | grep 3306` 是排查「端口被占用 / 服务没起来」最常用的命令。
:::

## DNS 查询

```shell
cat /etc/resolv.conf       # 本机 DNS 配置
nslookup example.com       # 查询解析
dig example.com            # 更详细的 DNS 查询（需安装 dnsutils）
```

## 远程连接与传输

```shell
ssh user@10.0.0.5                  # SSH 登录
ssh -p 2222 user@10.0.0.5          # 指定端口
scp file.txt user@10.0.0.5:/tmp/   # 上传文件
scp user@10.0.0.5:/tmp/a.txt .     # 下载文件
rsync -av /data/ user@10.0.0.5:/backup/   # 增量同步
```

::: danger 注意
1. 生产环境优先使用**密钥登录**，禁用密码登录。
2. `scp` 大文件/增量同步用 `rsync`，支持断点续传。
:::

## 下载文件

```shell
wget https://example.com/a.tar.gz
curl -O https://example.com/a.tar.gz
```

## 防火墙（简要）

Ubuntu（ufw）：

```shell
sudo ufw allow 22/tcp
sudo ufw allow 80,443/tcp
sudo ufw enable
sudo ufw status
```

RHEL 系（firewalld）：

```shell
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

## 常见排查流程

1. `ping` 测网络通不通。
2. `ss -lntp` 看端口有没有监听。
3. `curl -v` 看 HTTP 层报错。
4. `cat /etc/resolv.conf` + `nslookup` 查 DNS。
5. `ip route` 看路由是否正确。

## 验证方式

```shell
ip addr
ss -lntp
ping -c 4 223.5.5.5
curl -I https://www.baidu.com
```

能拿到 IP、看到监听端口、ping 通、curl 返回 200，说明网络配置正常。
