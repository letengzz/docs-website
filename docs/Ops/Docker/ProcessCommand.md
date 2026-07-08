# Docker 进程命令

启动Docker服务：

```shell
systemctl start docker
```

```shell
service docker start 
```

停止Docker服务：

```shell
systemctl stop docker
```

```shell
service docker stop
```

停止在关闭状态下被访问自动唤醒机制：

```shell
systemctl stop docker
systemctl stop docker.socket
```

重启Docker服务：

```shell
systemctl restart docker
```

```shell
service docker restart
```

查看Docker服务状态：

```shell
systemctl status docker
```

```shell
service docker status
```

设置开机启动Docker服务：

```shell
systemctl enable docker
```

关闭开机启动Docker服务：

```shell
systemctl disable docker
```

查看Docker info引擎信息：

```shell
docker info
```

查看docker进程：

```shell
ps -ef | grep docker
```

查看所有的帮助信息：

```shell
docker --help
```

查看某个commond命令的帮助信息：

```shell
docker commond --help
```

