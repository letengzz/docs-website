# Docker 容器

## 容器启动流程

通过 docker run 命令可以启动运行一个容器。该命令在执行时首先会在本地查找指定的镜像，如果找到了，则直接启动，否则会到镜像中心查找。如果镜像中心存在该镜像，则会下载到本地并启动，如果镜像中心也没有，则直接报错。

![](assets/img202406151430759.png)

如果再与多架构镜像原理相整合，则就形成了完整的容器启动流程。

![](assets/img202406151431124.png)

## 容器运行本质

Docker 容器存在的意义就是为了运行容器中的应用，对外提供服务，所以启动容器的目的就是启动运行该容器中的应用。
容器中的应用运行完毕后，容器就会自动终止。所以，如果不想让容器启动后立即终止运行，则就需要使容器应用不能立即结束。通常采用的方式有两种，使应用处于与用户交互的状态或等待状态。

## 创建并启动容器

创建并启动容器(无镜像会先下载镜像)：

```shell
docker run 参数
```

参数：

- -c：后面跟待完成的命令

- -d：以分离模式(detached mode)运行容器。创建一个容器在后台运行，需要使用docker exec 进入容器。退出后，容器不会关闭

- -i：保持容器运行。通常与 -t 同时使用。加入it这两个参数后，容器创建后自动进入容器中，退出容器后，容器自动关闭

- -it 创建的容器一般称为交互式容器
  -id 创建的容器一般称为守护式容器

  **注意**：交互式容器，exit后容器自动关闭，守护式容器会在后台执行

- --name：为创建的容器命名

- -p：指定容器端口
  `-p 容器端口:物理机端口`：映射端口

- -P：随机端口

- -v：给容器挂载存储卷

/bin/bash 用于指定容器启动后需要运行的命令为/bin 下的 bash 命令，而该命令会启动一个 bash 终端。

例：

- 创建守护式容器：

  ```shell
  docker run -id --name=c2 centos:7
  ```

- 创建交互式容器：

  ```shell
  docker run -it --name=c1 centos:7 /bin/bash
  ```

## 仅创建容器

仅创建容器但不启动：

```shell
docker create 参数
```

参数：

- --name：为创建的容器命名
- -p：指定容器端口
  -p 容器端口:物理机端口：映射端口

**注意**：其没有 -d 选项。

## 进入容器

**注意**：只能对正在运行的容器进行操作

进入容器内部：

```shell
docker exec -it 容器ID或名称 /bin/bash
```

不进入容器执行命令：

```shell
docker exec -it 容器ID或名称 command
```

进入正在执行的终端：

```shell
docker attach 容器ID或名称
```

exec与attach的区别：

- attach连接终止会让容器退出后台运行，而exec不会。
- attach是进入正在执行的终端，不会情动新的进程，而docker exec则会开启一个新的终端，可以在里面操作。

## 退出容器

直接退出并停止容器容器：exit

退出不停止容器：CTRL + P + Q

## 停止容器

停止容器(若当前容器正在被其它进程访问，则在访问结束后再停止)：

```shell
docker stop 容器ID或名称
```

停止所有容器：

```shell
docker stop $(docker ps -qa)
```

## 重启容器

重启容器：

```shell
docker restart 容器ID或名称
```

## 启动容器

启动容器：

```shell
docker start 容器ID或名称
```

## 暂停容器

暂停容器：

```shell
docker pause 容器ID或名称
```

## 解除暂停容器

解除暂停容器：

```shell
docker unpause 容器ID或名称
```

## 删除容器

删除已经停止的容器：

```shell
docker rm 容器ID或名称
```

强制删除容器，可删除正在运行的容器：

```shell
docker rm -f 容器ID或名称
```

删除所有容器：

```shell
docker rm -f $(docker ps -a -q)
```

```shell
docker ps -a -q | xargs docker rm
```

## 杀掉容器

杀掉容器(无论容器当前是否被其它进程访问都直接停止)：

```shell
docker kill 容器ID或名称
```

杀掉所有容器：

```shell
docker kill $(docker ps -qa)
```

## 查看容器

查看正在运行的容器：

```shell
docker ps
```

查看所有容器：

```shell
docker ps -a
```

查看正在运行中的容器ID：

```shell
docker ps -q
```

查看所有的容器ID：

```shell
docker ps -qa
```

查看最后创建的容器(无论该容器是否处于运行状态)：

```shell
docker ps -l
```

查看最后创建的 n 个容器(无论该容器是否处于运行状态)：

```shell
docker ps –n 3
```

查看容器信息：

```shell
docker inspect 容器ID或名称
```

查看容器内进程：

```shell
docker top 容器ID或名称
```

如果容器中运行的进程较多，也可以通过 grep 对结果进行过滤：

```shell
docker top centos | grep bin
```

查看容器的状态：

```shell
docker stats 容器ID或名称
```

## 查看容器日志

查看容器日志：无论该容器是运行还是停止状态

```shell
docker logs 参数 容器ID或名称
```

**参数**：

- -n 或--tail：指定要显示的最后几条日志。

  ```shell
  docker logs -n 5 centos
  ```

  ```shell
  docker logs --tail 5 centos
  ```

- --since：指定要显示自从指定时间以来的日志。
  这个时间可以是一个绝对时间，也可以是一个相对时长。

  ```shell
  docker logs --since="2022-08-01" --tail=3 centos
  ```

  ```shell
  docker logs --since=30m --tail=3 centos
  ```

  - s：秒
  - m：分钟
  - h：小时

- --until：可以指定要显示截止到指定时间之前的日志。
  这个时间可以是一个绝对时间，也可以是一个相对时长。

  ```shell
  docker logs --until ="2022-08-01" --tail=3 centos
  ```

  ```shell
  docker logs --until =30m --tail=3 centos
  ```

  - s：秒
  - m：分钟
  - h：小时

- -t：查看某日志的详细时间戳。

  ```shell
  docker logs -t --tail=3 centos
  ```

- -f：查看动态日志

  ```shell
  docker logs -f --tail=3 centos
  ```

## 将容器保存为新镜像

将当前容器保存为新的镜像：

```shell
docker commit -a "作者" -m "描述"  容器ID或名称 镜像名称:版本号
```

例：

```shell
docker run -id --name=cent centos:7
docker exec -it cent bash
mkdir /root/data
cd /root/data
echo 'hello' > 1.txt
```

```shell
docker commit -a "hjc" -m "这是一个镜像" cent cent:1
docker images
docker run -it --name=ce1 cent:1 bash
cd /root/data
cat 1.txt
```

## 重命名容器

重命名容器：

```shell
docker rename 旧名称 新名称
```

## 导入/导出容器

导入容器：

```shell
docker import tomcat.tar mytomcat:1
```

导出容器：

```shell
docker export -o tomcat.tar mytomcat
```

与 save/load 命令的对比：

- export 与 save：

  export 作用于容器，save 作用于镜像，但它们导出的结果都为 tar 文件

  export 一次只能对一个容器进行导出，save 一次可以对多个镜像进行导出

  export 只是对当前容器的文件系统快照进行导出，其会丢弃原镜像的所有历史记录与元数据信息，save 则是保存了原镜像的完整记录

- import 与 load：

  import 导入的是容器包，load 加载的是镜像包，但最终都会恢复为镜像

  import 恢复为的镜像只包含当前镜像一层，load 恢复的镜像与原镜像的分层是完全相同的

  import 恢复的镜像就是新构建的镜像，与原镜像的 ImageID 不同；load 恢复的镜像与原镜像是同一个镜像，即 ImageID 相同

  import 可以为导入的镜像指定`<repository>`与`<tag>`，load 加载的镜像不能指定`<repository>`与`<tag>`，与原镜像的相同

- 与 docker commit 的对比：

  **相同点**：docker export + docker import 会将一个容器变为一个镜像，docker commit 也可以将一个容器变一个镜像。

  **不同点**：docker export + docker import 恢复的镜像仅包含原容器生成的一层分层，docker commit 生成的镜像中包含容器的原镜像的所有分层信息。

## 从容器内拷贝文件到主机上

容器 -> 主机：

```shell
docker cp 容器id:容器内路径 目的主机路径
```
