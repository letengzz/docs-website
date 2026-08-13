# Docker Compose

::: info 版本现状
Compose 当前为 V2（命令 `docker compose`，v2.40+），V1 的 `docker-compose` 已停止维护。健康检查、资源限制、secrets、profiles、watch 等进阶用法见「Docker Compose 进阶」。
:::

Docker-Compose 项目是Docker官方的开源项目，负责实现对Docker容器集群的快速编排。Docker-Compose 项目由 Python 编写，调用 Docker 服务提供的API来对容器进行管理。因此，只要所操作的平台支持 Docker API，就可以在其上利用Compose 来进行编排管理。

通过 Docker-Compose ，不需要使用shell脚本来启动容器，而使用 YAML 文件来配置应用程序需要的所有服务，然后使用一个命令，根据 YAML 的文件配置创建并启动所有服务。

Compose允许用户通过一个docker-compose.yml模板文件 (YAML 格式) 来定义一组相关联的应用容器为一个项目 (project)。Compose模板文件是一个定义服务、网络和卷的YAML文件。

Compose模板文件默认路径是当前目录下的docker-compose.yml，可以使用.yml或.yaml作为文件扩展名。

Docker-Compose标准模板文件应该包含version、services、networks 三大部分，最关键的是services和networks两个部分。

Compose 是 Docker 公司推出的一个工具软件，可以管理多个 Docker 容器组成一个应用。你需要定义一个 YAML 格式的配置文件**docker-compose.yml**，写好多个容器之间的调用关系。然后，只要一个命令，就能同时启动/关闭这些容器

## 安装

Docker Compose下载：https://docs.docker.com/compose/install/linux/

下载插件：

```shell
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
```

添加权限：

```shell
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
```

查看是否安装成功：

```shell
docker compose version
```

## 使用步骤

编写Dockerfile定义各个微服务应用并构建出对应的镜像

使用docker-compose.yml定义个完整业务单元，安排好整体应用中的各个容器服务。

执行docker compose up命令，启动并运行整个应用程序，完成一键部署上线。

## 语法

## 常用命令

- Docker Compose：

  ```shell
  docker compose [-f ...] [options] [COMMAND] [ARGS...]
  ```

  参数：

  - -f，–file：FILE指定Compose模板文件，默认为docker-compose.yml，可以多次指定。

  - -p，–project-name：NAME指定项目名称，默认将使用所在目录名称作为项目名。

  - -x-network-driver：使用Docker的可拔插网络后端特性（需要Docker 1.9+版本） -x-network-driver DRIVER指定网络后端的驱动，默认为bridge（需要Docker 1.9+版本）

  - -verbose：输出更多调试信息

  - -v，–version：打印版本并退出

- 获取指令的帮助：

  ```shell
  docker compose 命令 --help
  ```

  ```shell
  docker compose -h
  ```

- 构建容器：

  ```shell
  docker compose up [options] [--scale SERVICE=NUM...] [SERVICE...]
  ```

  参数：

  - -d：在后台运行服务容器

  - –no-color：不使用颜色来区分不同的服务的控制输出

  - –no-deps：不启动服务所链接的容器

  - –force-recreate：强制重新创建容器，不能与–no-recreate同时使用 –no-recreate 如果容器已经存在，则不重新创建，不能与–force-recreate同时使用

  - –no-build：不自动构建缺失的服务镜像

  - –build：在启动容器前构建服务镜像

  - –abort-on-container-exit：停止所有容器，如果任何一个容器被停止，不能与-d同时使用

  - -t, –timeout：TIMEOUT 停止容器时候的超时（默认为10秒）

  - –remove-orphans：删除服务中没有在compose文件中定义的容器

  - –scale SERVICE=NUM：设置服务运行容器的个数，将覆盖在compose中通过scale指定的参数

  - -f：指定使用的Compose模板文件，默认为docker-compose.yml，可以多次指定。

    ```shell
    docker compose -f docker-compose.yml up -d
    ```

  启动所有服务：

  ```shell
  docker compose up
  ```

  在后台所有启动服务：

  ```text
  docker compose up -d
  ```

  构建启动nginx容器：

  ```shell
  docker compose up -d nginx
  ```

- 查看容器：

  ```shell
  docker-compose ps [options] [SERVICE...]
  ```

  列出项目中目前的所有容器：

  ```shell
  docker compose ps
  ```

  查看各个服务容器内运行的进程：

  ```shell
  docker compose top
  ```

  查看Compose文件包含的镜像：

  ```shell
  docker compose images
  ```

- 停止正在运行的容器：可以通过`docker-compose start` 再次启动

  ```shell
  docker compose stop [options] [SERVICE...]
  ```

  参数：

  - -t, –timeout：TIMEOUT 停止容器时候的超时（默认为10秒）

  停止nignx容器：

  ```shell
  docker compose stop nginx
  ```

- 停止和删除容器、网络、卷、镜像：

  ```shell
  docker compose down [options]
  ```

  参数：

  - –rmi type：删除镜像，类型必须是：
    - all，删除compose文件中定义的所有镜像
    - local，删除镜像名为空的镜像
  - -v, –volumes：删除已经在compose文件中定义的和匿名的附在容器上的数据卷
  - –remove-orphans：删除服务中没有在compose中定义的容器

  停止up命令所启动的容器，并移除网络：

  ```shell
  docker compose down
  ```

- 查看实时日志：

  ```shell
  docker compose logs [options] [SERVICE...]
  ```

  参数：

  - --no-color：产生单色输出。默认情况下，docker-compose将对不同的服务输出使用不同的颜色来区分。可以通过–no-color来关闭颜色。
  - -f, --follow：实时输出日志，最后一行为当前时间戳的日志
  - -t, --timestamps：显示时间戳
  - --tail="all"：显示最后多少行日志， 默认是all （如： -tail=10 : 查看最后的 10 行日志。）

  全屏滚到底部显示最后10行并继续持续输出日志并显示时间戳：

  ```shell
  docker compose logs -f -t --tail=10
  ```

  查看nginx实时日志：

  ```shell
  docker compose logs -f nginx
  ```

- 构建（重新构建）项目中的服务容器：

  ```shell
  docker compose build [options] [--build-arg key=val...] [SERVICE...]
  ```

  参数：

  - –compress：通过gzip压缩构建上下环境
  - –force-rm：删除构建过程中的临时容器
  - –no-cache：构建镜像过程中不使用缓存
  - –pull：始终尝试通过拉取操作来获取更新版本的镜像
  - -m, –memory：MEM为构建的容器设置内存大小
  - –build-arg key=val：为服务设置build-time变量

  服务容器一旦构建后，将会带上一个标记名。可以随时在项目目录下运行docker-compose build来重新构建服务

  构建镜像：

  ```shell
  docker compose build nginx
  ```

  不带缓存的构建：

  ```shell
  docker compose build --no-cache nginx
  ```

- 为服务创建容器：

  ```shell
  docker compose create [options] [SERVICE...]
  ```

  参数：

  - –force-recreate：重新创建容器，即使配置和镜像没有改变，不兼容–no-recreate参数
  - –no-recreate：如果容器已经存在，不需要重新创建，不兼容–force-recreate参数
  - –no-build：不创建镜像，即使缺失
  - –build：创建容器前，生成镜像

- 拉取服务依赖的镜像：

  ```shell
  docker compose pull [options] [SERVICE...]
  ```

  参数：

  - –ignore-pull-failures：忽略拉取镜像过程中的错误
  - –parallel：多个镜像同时拉取
  - –quiet：拉取镜像过程中不打印进度信息

- 启动已经存在的服务容器：

  ```shell
  docker compose start [SERVICE...]
  ```

  启动nignx容器：

  ```shell
  docker compose start nginx
  ```

- 在指定服务上执行一个命令：

  ```shell
  docker compose run [options] [-v VOLUME...] [-p PORT...] [-e KEY=VAL...] SERVICE [COMMAND] [ARGS...]
  ```

  在指定容器上执行一个ping命令：

  ```shell
  docker compose run ubuntu ping www.baidu.com
  ```

  在php-fpm中不启动关联容器，并容器执行php -v 执行完成后删除容器：

  ```shell
  docker compose run --no-deps --rm php-fpm php -v
  ```

- 进入服务容器：

  ```shell
  docker compose exec [options] SERVICE COMMAND [ARGS...]
  ```

  参数：

  - -d：分离模式，后台运行命令。

  - –privileged：获取特权。

  - –user：USER 指定运行的用户。

  - -T：禁用分配TTY，默认docker-compose exec分配TTY。

  - –index=index：当一个服务拥有多个容器时，可通过该参数登陆到该服务下的任何服务

    web服务中包含多个容器：

    ```shell
    docker compose exec –index=1 web /bin/bash
    ```

  登录到nginx容器：

  ```shell
  docker compose exec nginx bash
  ```

- 停止服务容器：

  ```shell
  docker compose kill [options] [SERVICE...]
  ```

  通过发送SIGKILL信号来强制停止服务容器。 支持通过-s参数来指定发送的信号

  例如通过如下指令发送SIGINT信号：

  ```shell
  docker compose kill -s SIGINT
  ```

- 重启项目中的服务：

  ```shell
  docker compose restart [options] [SERVICE...]
  ```

  参数：

  - -t, –timeout TIMEOUT：指定重启前停止容器的超时（默认为10秒）

  重新启动nginx容器：

  ```shell
  docker compose restart nginx
  ```

- 删除所有（停止状态的）服务容器：

  ```shell
  docker compose rm [options] [SERVICE...]
  ```

  参数：

  - –f, –force：强制直接删除，包括非停止状态的容器
  - -v：删除容器所挂载的数据卷

  删除所有（停止状态的）服务容器。推荐先执行docker-compose stop命令来停止容器。

  ```shell
  docker compose rm
  ```

  删除容器（删除前必须关闭容器，执行stop）：

  ```shell
  docker compose rm nginx
  ```

- 暂停服务容器：

  ```shell
  docker compose pause [SERVICE...]
  ```

  暂停nignx容器：

  ```shell
  docker compose pause nginx
  ```

- 恢复处于暂停状态中的服务：

  ```shell
  docker compose unpause [SERVICE...]
  ```

  恢复ningx容器：

  ```shell
  docker compose unpause nginx
  ```

- 显示某个容器端口所映射的公共端口：

  ```shell
  docker compose port [options] SERVICE PRIVATE_PORT
  ```

  参数：

  - –protocol=proto：指定端口协议，TCP（默认值）或者UDP
  - –index=index：如果同意服务存在多个容器，指定命令对象容器的序号（默认为1）

- 验证并查看compose文件配置：

  ```shell
  docker compose config [options]
  ```

  参数：

  - –resolve-image-digests：将镜像标签标记为摘要
  - -q, –quiet：只验证配置，不输出。 当配置正确时，不输出任何内容，当文件配置错误，输出错误信息
  - –services：打印服务名，一行一个
  - –volumes：打印数据卷名，一行一个

  验证文件配置(当配置正确时，不输出任何内容，当文件配置错误，输出错误信息)：

  ```shell
  docker compose config
  ```

- 设置指定服务运行的容器个数

  通过service=num的参数来设置数量：

  ```shell
  docker compose scale web=3 db=2
  ```

- 打印版本信息：

  ```shell
  docker compose version
  ```

- 以json的形式输出nginx的docker日志：

  ```shell
  docker compose events --json nginx
  ```

## 使用compose编排微服务

**准备应用程序所需镜像**

使用Dockerfile构建jar的镜像

jar包配置项所需ip的位置可以使用服务名

![img202410212155039](assets/img202410212155039.png)

配置运行jar所需镜像的配置

**编写docker-compose.yml文件**：

```shell
version: "3"
services:
  microService:
    image: docker_boot:1.2
    container_name: ms01
    ports:

      - "8899:8899"
        volumes:
            - /app/microService:/data
            networks:
                  - compose_net
                depends_on:
                        - redis
                              - mysql

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - /opt/app/redis/redis.conf:/etc/redis/redis.conf
      - /opt/app/redis/data:/data
    networks:
      - compose_net
    command: redis-server /etc/redis/redis.conf
  mysql:
    image: mysql:8.0.33
    environment:
      MYSQL_ROOT_PASSWORD: 'abc123'
      MYSQL_ALLOW_EMPTY_PASSWORD: 'no'
      MYSQL_DATABASE: 'compose'
      MYSQL_USER: 'tute'
      MYSQL_PASSWORD: 'abcd1234'
    ports:
       - "3306:3306"
    volumes:
       - /opt/app/mysql/log:/var/log/mysql
       - /opt/app/mysql/data:/var/lib/mysql
       - /opt/app/mysql/conf:/etc/mysql/conf.d
    networks:
      - compose_net
    command: --default-authentication-plugin=mysql_native_password #解决外部无法访问

networks:
   compose_net:
```

**启动应用程序**：

```shell
docker compose up 或 docker compose up -d
```

**测试**：

发送请求，查看返回结果
