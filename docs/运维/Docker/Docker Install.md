## 方式一
### Docker安装

- yum安装gcc相关
yum -y install gcc
yum -y install gcc-c++
- 安装需要的软件包
yum install -y yum-utils
- 设置stable镜像仓库
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
- 更新yum软件包索引
yum makecache fast
- 安装Docker ce
yum install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
- 启动docker
systemctl start docker
- 测试
docker --version 查看docker版本
docker run hello-world 运行hello world

> 注意 **--setopt=obsoletes=0，否则yum会自动安装更高版本**

安装指定版本 docker-ce  
yum install --setopt=obsoletes=0 -y docker-ce-19.03.10-3.el7 docker-ce-cli-19.03.10-3.el7 containerd.io
查看当前仓库支持的docker-ce版本
yum list docker-ce --showduplicates | sort -r

20.10.14-3.el7
yum install --setopt=obsoletes=0 -y docker-ce-20.10.20-3.el7 docker-ce-cli-20.10.20-3.el7 containerd.io
### 卸载docker
- 停止服务
systemctl stop docker
- 卸载docker ce
yum remove docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
- 删除所有image,container and volumes
rm -rf /var/lib/docker
rm -rf /var/lib/containerd

### 设置镜像加速器
```
mkdir -p /etc/docker
tee /etc/docker/daemon.json <<-'EOF' 
{ 
    "registry-mirrors": ["https://k53d2wn3.mirror.aliyuncs.com"]
}
EOF
# 启动docker服务
/usr/sbin/iptables -F && /usr/sbin/iptables -X && /usr/sbin/iptables -F -t nat && /usr/sbin/iptables -X -t nat
/usr/sbin/iptables -P FORWARD ACCEPT
systemctl daemon-reload && systemctl enable docker && systemctl restart docker
```

## 方式二
### 安装依赖包
```shell
yum install -y epel-release conntrack ipvsadm ipset jq iptables curl sysstat libseccomp && /usr/sbin/modprobe ip_vs
```
### 下载二进制文件
[https://download.docker.com/linux/static/stable/x86_64/](https://download.docker.com/linux/static/stable/x86_64/)
```shell
mkdir -p /root/download
cd /root/download

wget https://download.docker.com/linux/static/stable/x86_64/docker-20.10.7.tgz
tar -xvf docker-20.10.7.tgz
```
安装
```shell
mkdir -p /opt/docker/bin

cp docker/*  /opt/docker/bin/
chmod +x /opt/docker/bin/*

vim /etc/profile
export PATH=/opt/docker/bin:$PATH

source /etc/profile
```
### 创建 systemd unit 文件
```shell
cd /root/download

# 创建文件
cat > docker.service <<"EOF"
[Unit]
Description=Docker Application Container Engine
Documentation=http://docs.docker.io

[Service]
WorkingDirectory=/data/docker
Environment="PATH=/opt/docker/bin:/bin:/sbin:/usr/bin:/usr/sbin"
ExecStart=/opt/docker/bin/dockerd 
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity
Delegate=yes
KillMode=process

[Install]
WantedBy=multi-user.target
EOF

# 复制文件
cp docker.service  /etc/systemd/system/
```
**注意事项**

- EOF 前后有双引号，这样 bash 不会替换文档中的变量，如 $DOCKER_NETWORK_OPTIONS；
- dockerd 运行时会调用其它 docker 命令，如 docker-proxy，所以需要将 docker 命令所在的目录加到 PATH 环境变量中；
- docker 需要以 root 用于运行；
- docker 从 1.13 版本开始，可能将 **iptables FORWARD chain的默认策略设置为DROP**，从而导致 ping 其它 Node 上的 Pod IP 失败，遇到这种情况时，需要手动设置策略为 **ACCEPT**
```shell
iptables -P FORWARD ACCEPT
```
并且把以下命令写入 /etc/rc.local 文件中，防止节点重启**iptables FORWARD chain的默认策略又还原为DROP**
```shell
/sbin/iptables -P FORWARD ACCEPT
```
### 配置 docker 配置文件
使用国内的仓库镜像服务器以加快 pull image 的速度，同时增加下载的并发数 (需要重启 dockerd 生效)：
```shell
cd /root/download
mkdir -p /data/docker/data
mkdir -p /data/docker/exec

cat > daemon.json <<EOF
{
    "registry-mirrors": [ "https://477njxek.mirror.aliyuncs.com", "https://registry.docker-cn.com/", "https://hub-mirror.c.163.com", "https://docker.mirrors.ustc.edu.cn"],
    "insecure-registries": [],
    "max-concurrent-downloads": 20,
    "live-restore": true,
    "max-concurrent-uploads": 10,
    "debug": true,
    "data-root": "/data/docker/data",
    "exec-root": "/data/docker/exec",
    "log-opts": {
      "max-size": "100m",
      "max-file": "5"
    }
}
EOF
```
分发 docker 配置文件到所有 work 节点：
```shell
cd /root/download
mkdir -p  /etc/docker/

cp daemon.json /etc/docker/
```
### 启动docker服务
```shell
# systemctl stop firewalld && systemctl disable firewalld
/usr/sbin/iptables -F && /usr/sbin/iptables -X && /usr/sbin/iptables -F -t nat && /usr/sbin/iptables -X -t nat
/usr/sbin/iptables -P FORWARD ACCEPT
systemctl daemon-reload && systemctl enable docker && systemctl restart docker
```

- 关闭 firewalld(centos7)/ufw(ubuntu16.04)，否则可能会重复创建 iptables 规则；
- 清理旧的 iptables rules 和 chains 规则；
- 开启 docker0 网桥下虚拟网卡的 hairpin 模式;
### 检查服务运行状态
```shell
systemctl status docker|grep Active
```
确保状态为 active (running)，否则查看日志，确认原因：
```shell
journalctl -u docker
```
### 常见问题
```shell
10月 20 14:22:48 server194 dockerd[18145]: time="2022-10-20T14:22:48.470249898+08:00" level=warning msg="grpc: addrConn.createTransport failed to connect to {unix:///data_prod/docker/exec/containerd/containerd.sock  <nil> 0 <nil>}. Err :connection error: desc =>
10月 20 14:22:50 server194 dockerd[18145]: time="2022-10-20T14:22:50.917075452+08:00" level=warning msg="grpc: addrConn.createTransport failed to connect to {unix:///data_prod/docker/exec/containerd/containerd.sock  <nil> 0 <nil>}. Err :connection error: desc =>
```
解决方案
/data_prod/docker/exec 目录备份后，重新创建创建exec文件夹
