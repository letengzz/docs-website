# 数据卷与挂载最佳实践

容器文件系统是临时的：容器删除后，写在容器层里的数据会消失。数据卷（Volume）和绑定挂载（Bind Mount）是让数据「活到容器之外」的两种主要方式，本节讲清它们的区别、现代 `--mount` 语法、备份恢复与权限问题。

::: info 适用版本
本节基于 Docker Engine 29.x。Docker 29.7 起，`image` 类型挂载已不再是实验特性，可以直接把镜像内容挂载到容器。
:::

## 三类挂载对比

| 类型 | 数据存哪 | 适用场景 | 特点 |
| --- | --- | --- | --- |
| 命名卷（volume） | `/var/lib/docker/volumes/`（由 Docker 管理） | 数据库、应用数据 | 可备份、可跨容器共享、跨平台一致 |
| 绑定挂载（bind） | 宿主机任意路径 | 配置文件、开发热更新 | 直接访问宿主机文件，受路径和权限影响 |
| tmpfs | 内存 | 临时文件、密钥、缓存 | 速度快、不落盘，容器停止即清空 |

## 推荐使用 --mount 语法

`-v` / `--volume` 写法历史悠久，但用 `:` 分隔多个选项，可读性差；`--mount` 用键值对显式声明类型，推荐在新项目中使用：

```shell
docker run -d \
  --name mysql \
  --mount type=volume,src=mysql-data,dst=/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=secret \
  mysql:8.4
```

等价对比：

| `-v` 写法 | `--mount` 写法 |
| --- | --- |
| `-v mysql-data:/var/lib/mysql` | `--mount type=volume,src=mysql-data,dst=/var/lib/mysql` |
| `-v /host/data:/app/data` | `--mount type=bind,src=/host/data,dst=/app/data` |
| `-v /app/data`（匿名卷） | `--mount type=volume,dst=/app/data` |
| `-v /tmp:/tmp` | `--mount type=tmpfs,dst=/tmp` |

## 命名卷的管理

显式创建卷，避免依赖匿名卷：

```shell
docker volume create app-data
docker volume ls
docker volume inspect app-data
```

清理不再使用的卷：

```shell
docker volume prune
```

清理前先确认没有容器引用：`docker ps -a --filter volume=app-data`。`docker system prune -a --volumes` 会同时删除所有未使用的卷，属于高危操作，谨慎执行。

## 备份与恢复

用临时容器把命名卷打包：

```shell
docker run --rm \
  --mount type=volume,src=app-data,dst=/data \
  --mount type=bind,src=$(pwd),dst=/backup \
  alpine tar czf /backup/app-data.tar.gz -C /data .
```

恢复：

```shell
docker run --rm \
  --mount type=volume,src=app-data,dst=/data \
  --mount type=bind,src=$(pwd),dst=/backup \
  alpine sh -c "rm -rf /data/* /data/.[!.]* && tar xzf /backup/app-data.tar.gz -C /data"
```

数据库建议使用数据库自身的导出工具（如 `mysqldump`）做逻辑备份，文件级打包适合整体迁移。

## tmpfs：内存盘

```shell
docker run -d \
  --name redis \
  --mount type=tmpfs,dst=/data,tmpfs-size=100m \
  redis:7.4
```

tmpfs 适合 `/tmp`、缓存、session 等不需要持久化的数据；注意它占用宿主内存，写入超过 `tmpfs-size` 会报错。

## 只读挂载与权限

配置目录只读挂载，容器内不能篡改宿主机文件：

```shell
docker run -d \
  --name nginx \
  --mount type=bind,src=/etc/nginx/conf.d,dst=/etc/nginx/conf.d,readonly \
  nginx:stable-alpine
```

绑定挂载默认以宿主机文件的属主为准。容器内进程以普通用户（如 UID 1000）运行时，如果宿主机文件属主是 root，会出现 Permission denied。解决思路：

1. 挂载目录的属主改成容器内用户 UID（`chown -R 1000:1000 ./data`）。
2. 在 Dockerfile 里用 `COPY --chown` 或 `USER` 匹配 UID。
3. 只在开发环境用绑定挂载，生产尽量用命名卷。

## 卷驱动：NFS 与远程存储

```shell
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.10,rw,nfsvers=4 \
  --opt device=:/srv/docker-data \
  nfs-data
```

创建后像普通命名卷一样使用。NFS 适合多机共享，但延迟和可用性取决于网络，数据库等对 IO 敏感的应用要谨慎。

## 镜像挂载（Docker 29.7+）

直接把某个镜像的内容挂载进容器，适合做只读工具镜像、初始化任务：

```shell
docker run --rm \
  --mount type=image,src=busybox:latest,dst=/toolbox \
  alpine ls /toolbox
```

该挂载类型在 Docker 29.7 起不再是实验特性。

## 易错点

::: danger 常见错误
1. 用绑定挂载把整个项目目录（含 `node_modules`）挂进容器，权限和性能都出问题。
2. 挂载单个文件（如配置文件）时宿主机路径写错，Docker 会把它当成目录创建，启动直接失败。
3. 忘记只读挂载，容器内进程可以随意修改宿主机挂载目录。
4. 把 `/var/run/docker.sock` 挂给业务容器，容器等于获得了宿主机的 Docker 控制权，属于严重安全风险。
5. 数据库容器没有挂载命名卷，`docker compose down` 后数据全部丢失。
6. Windows 下把路径写成 `D:\data:/data`，`--mount` 需要正确转义，建议统一使用绝对路径并用反斜杠转义或正斜杠。
:::

## 验证方式

1. `docker volume ls` 能看到创建的命名卷。
2. `docker run --rm -v app-data:/data alpine sh -c "echo test > /data/hello.txt"` 写入成功。
3. 删除该容器后，再挂载同一卷执行 `cat /data/hello.txt`，文件仍在。
4. 备份命令执行后，宿主机当前目录出现 `app-data.tar.gz`，`tar tzf` 能列出数据。
5. `docker inspect <容器>` 的 `Mounts` 字段能正确显示挂载类型、源和目的。

## 参考资料

- Docker 存储概述：https://docs.docker.com/engine/storage/
- 使用卷：https://docs.docker.com/engine/storage/volumes/
- 绑定挂载：https://docs.docker.com/engine/storage/bind-mounts/
- tmpfs 挂载：https://docs.docker.com/engine/storage/tmpfs/
