# Docker 数据卷

::: info 进阶指引
推荐使用 `--mount` 键值对语法替代 `-v`；命名卷、绑定挂载与 tmpfs 的选型、备份恢复和权限问题见「数据卷与挂载最佳实践」。
:::

数据卷是宿主机中的一个目录或文件。当容器目录和数据卷目录绑定后，对方的修改会立即同步，一个数据卷可以被多个容器同时挂载，一个容器也可以被挂载多个数据卷。数据卷完全独立于容器的生存周期。

**作用**：

- 容器数据持久化
- 外部机器和容器间接通信
- 容器之间数据交换

## 配置数据卷

创建启动容器时，使用 –v 参数 设置数据卷：

```shell
docker run ... –v 宿主机目录(文件):容器内目录(文件) ...
```

- 匿名挂载：-v 容器内路径

- 具名挂载 (卷映射)：-v 卷名：容器内路径(此方式Docker会自动创建一个位置，把容器内部的初始启动内容放入到该为止)

  创建卷的位置：`/var/lib/docker/volumes/<volume-name>/_data`

- 指定路径挂载 (目录挂载)：-v /宿主机路径：容器内路径(此方式Docker 会自动创建路径，但不会将容器内的数据放入到该文件夹)

**注意**：

- 容器目录必须是绝对路径
- 如果目录不存在，会自动创建
- 可以挂载多个数据卷
- $PWD 表示宿主机当前目录
- 在容器中不能写 ~

![image-20240615163725142](assets/img202406151637749.png)

数据卷持久化：

- 创建c1挂载/root/data到/root/data_container

  ```shell
  docker run -it --name=c1 -v /root/data:/root/data_container centos:7 /bin/bash
  ```

- 关闭容器，可以看到数据卷数据文件还在：

  ```shell
  docker stop c1
  ```

- 删除容器c1，后发现宿主机目录还在

  ```shell
  docker rm c1
  ```

- 重新恢复c1：

  ```shell
  docker run -it --name=c1 -v ~/data:/root/data_container centos:7 /bin/bash
  ```

**例**：

- 一个容器挂载一个数据卷

  ```shell
  docker run -it --name=c1 -v ~/data:/root/data_container centos:7 /bin/bash
  ```

- 一个容器挂载多个数据卷

  ```shell
  docker run -it --name=c2 \
  -v ~/data2:/root/data2 \
  -v ~/data3:/root/data3 \
  centos:7
  ```

- 两个容器挂载同一个数据卷

  ```shell
  docker run -it --name=c3
  -v /root/data:/root/data_container centos:7 /bin/bash
  docker run -it --name=c4
  -v /root/data:/root/data_container centos:7 /bin/bash
  ```

- 具名挂载与匿名挂载：

  - 具名挂载：

    ```shell
    docker run -it --name=c1 -v data_container:/root/data_container centos:7 /bin/bash
    ```

  - 匿名挂载：

    ```shell
    docker run -it --name=c1 -v /root/data_container centos:7 /bin/bash
    ```

Docker挂载主机目录访问如果出现`cannot open directory .: Permission denied`
解决办法：在挂载目录后多加一个`--privileged=true`参数即可

如果是CentOS7安全模块会比之前系统版本加强，不安全的会先禁止，所以目录挂载的情况被默认为不安全的行为，

在SELinux里面挂载目录被禁止掉了，如果要开启，一般使用`--privileged=true`命令，扩大容器的权限解决挂载目录没有权限的问题，也即使用该参数，container内的root拥有真正的root权限，否则，container内的root只是外部的一个普通用户权限。

```shell
docker run -it --privileged=true -v /宿主机绝对路径目录:/容器内目录 镜像名|镜像id
```

## 查看容器挂载情况

使用 docker inspect 容器ID或名称 [|less(使用/name查找内容)] 查看容器挂载情况：

```
docker inspect 容器ID或名称 [|less(使用/name查找内容)]
```

- Mounts：代表着挂载
- type：类型(绑定)
- source：源，也就是把什么挂载到哪里
- destination：挂载的目标路径

## 查看所有数据卷

查看所有卷的情况：

```shell
docker volume ls
```

## 改变读写权限

只读 (ro readonly)：

```shell
docker run -it --name=c1 -v ~/data:/root/data_container:ro centos:7 /bin/bash
```

可写可读 (rw readwrite)：

```shell
docker run -it --name=c1 -v ~/data:/root/data_container:rw centos:7 /bin/bash
```

## 配置数据卷容器

多容器进行数据交换，多个容器挂载同一个数据卷容器，完成数据交互。

![](assets/img202406151644479.png)

通过简单方式实现数据卷配置：创建一个容器，挂载一个目录，让其他容器继承自该容器( --volume-from )

**例**：

1. 创建启动c3数据卷容器，使用 –v 参数 设置数据卷
   没有指定宿主机目录，默认生成一个宿主机目录

   ```shell
   docker run –it --name=c3 –v /volume centos:7 /bin/bash
   ```

2. 查看c3：

   ```shell
   docker inspect c3
   ```

3. 创建启动 c1 c2 容器，使用 –-volumes-from 参数 设置数据卷

   ```shell
   docker run -it --name=c1 --volumes-from c3 centos:7 /bin/bash
   docker run -it --name=c2 --volumes-from c3 centos:7 /bin/bash
   ```

4. 使用 c3数据卷容器创建c1,c2，这时即使c3关闭不影响c1 c2交互

## 数据卷的继承和共享

```shell
docker run -it --privileged=true  --volumes-from 父类(容器id|容器名)  镜像名|镜像id
```

示例：

```shell
docker run -it --name u1 --privileged=true -v /opt/ubuntumap:/opt/dockerubuntu ubuntu /bin/bash
docker run -it --name u2 --privileged=true --volumes-from u1 ubuntu /bin/bash
```
