# Dockerfile

::: info 进阶指引
本文为基础指令入门。生产级写法（非 root、固定版本、缓存挂载、密钥挂载）与多阶段构建请参考「Dockerfile 最佳实践」和「多阶段构建」；Docker 23.0+ 可用 `docker build --check .` 先校验 Dockerfile。
:::

Dockerfile是用来构建Docker镜像的文本文件，是由一条条构建镜像所需的指令和参数构成的脚本。

## 构建执行流程

构建三步骤：

- 编写Dockerfile文件
- docker build命令构建镜像
- docker run用镜像运行容器实例

构建的过程就是执行 Dockerfile 文件中写入的命令。构建一共进行了7个步骤，每个步骤进行完都会生成一个随机的 ID，来标识这一 layer 中的内容。 最后一行为镜像的 ID。

对于没有任何修改的内容，Docker 会复用之前的结果。

如果 DockerFile 中的内容没有变动，那么相应的镜像在 build 的时候会复用之前的 layer，以便提升构建效率。并且，即使文件内容有修改，那也只会重新 build 修改的 layer，其他未修改的也仍然会复用。

## Dockerfile内容基础知识

- 每条保留字指令都必须为**大写字母**且后面要跟随至少一个参数
- 指令按照从上到下，顺序执行
- #表示注释
- 每条指令都会创建一个新的镜像层并对镜像进行提交

## Docker执行Dockerfile的大致流程

- docker从基础镜像运行一个容器
- 执行一条指令并对容器作出修改
- 执行类似docker commit的操作提交一个新的镜像层
- docker 再基于刚提交的镜像运行一个新容器
- 执行dockerfile中的下一条指令直到所有指令都执行完成

小总结

![img202410212154984](assets/img202410212154984-174296516575911.png)

## 保留字

- FROM：基础镜像，当前新镜像是基于哪个镜像的，第一条必须是from

- MAINTAINER：镜像维护者的姓名和邮箱地址

- RUN：容器构建时需要运行的命令（在docker build时运行）

  两种格式：shell格式 和 exec格式

- shell示例：RUN yum install -y vim\*

- exec示例：RUN["java","-jar","docker_boot.jar"] => java -jar docker_boot.jar

- EXPOSE：当前容器对外暴露出的端口

- WORKDIR：指定进入容器的工作目录

- USER：指定镜像以什么样的用户去执行，如果不指定默认是root

- ENV：用来在构建镜像过程中设置环境变量

- ADD：将宿主机目录下的文件保内进镜像且会自动处理URL和解压tar压缩包

- COPY:拷贝文件到镜像中。将从构建上下文目录中<源路径>的文件/目录复制到新的一层的镜像内的<目标路径>位置 COPY src dest 或COPY ["src","dest"]；目标路径不用事先创建，系统会自动创建。

- VOLUME：容器数据卷，用于数据保存和持久化工作

- CMD：指定容器启动后要干的事情

  注意：Dockerfile中可以有多个CMD指令，但只有最后一个生效，CMD会被docker run之后的参数替换

- ENTRYPOINT：也是一种指定容器启动时要运行的命令

  类似于CMD指令，但是ENTRYPOINT不会被docker run后面的命令覆盖，而且这些命令行参数会被当前参数送给ENTRYPOINT指令指定的程序。

  优点：在执行docker run时可以指定ENTRYPOINT运行所需的参数。

  注意：如果Dockerfile中如果存在多个ENTRYPOINT执行，仅最后一个生效

  ENTRYPOINT命令格式：ENTRYPOINT ["executeable","param1","param2"]

  当指定了ENTRYPOINT后，CMD的含义变成了为ENTRYPOINT提供参数

![image.png](assets/img202410212154799.png)

Dockerfile实例：

```shell
FROM centos:7
MAINTAINER hjc<hjc@xx.com>

ENV MYPATH /usr/local
WORKDIR $MYPATH

#安装vim编辑器
RUN yum -y install vim
#安装ifconfig命令查看网络IP
RUN yum -y install net-tools
#安装java8及lib库
RUN yum -y install glibc.i686
RUN mkdir /usr/local/java
#ADD 是相对路径jar,把jdk-8u171-linux-x64.tar.gz添加到容器中,安装包必须要和Dockerfile文件在同一位置
ADD jdk-8u171-linux-x64.tar.gz /usr/local/java/
#配置java环境变量
ENV JAVA_HOME /usr/local/java/jdk1.8.0_171
ENV JRE_HOME $JAVA_HOME/jre
ENV CLASSPATH $JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JRE_HOME/lib:$CLASSPATH
ENV PATH $JAVA_HOME/bin:$PATH

EXPOSE 80

CMD echo $MYPATH
CMD echo "success--------------ok"
CMD /bin/bash
```

编写完Dockerfile文件后，构建镜像文件
命令：`docker build -t image_name:tag .` =>`docker build -t centosjava8:1.0 .`
运行镜像：`docker run image_name:tag`

## Docker微服务实战

Dockerfile文件：

```shell
# 基础镜像使用java
FROM java:8

# 作者
MAINTAINER hjc

# VOLUME 指定临时文件目录为/tmp，在主机/var/lib/docker目录下创建了一个临时文件并链接到容器的/tmp
VOLUME /tmp

# 将jar包添加到容器中并更名为zzyy_docker.jar
ADD docker_boot-0.0.1-SNAPSHOT.jar hjc_docker.jar

# 运行jar包
RUN bash -c 'touch /hjc_docker.jar'
ENTRYPOINT ["java","-jar","/zzyy_docker.jar"]

#暴露5678端口作为微服务
EXPOSE 5678
```

构建镜像：

```shell
docker build -t docker_boot:1.0 .
```

启动容器：

```shell
docker run -d -p 5678:5678 docker_boot:1.0
```
