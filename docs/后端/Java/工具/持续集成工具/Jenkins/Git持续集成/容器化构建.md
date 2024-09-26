# 自动化部署到docker容器

## 部署方式

1. **外挂目录方式**(适合小型团队)：使用Docker镜像内置JDK，运行的JAR在宿主主机某个目录下，把宿主主机的目录和Docker容器相互关联(外部挂载目录)，当访问Docker 内部的某个路径目录时，会映射到宿主主机的目录。部署时，将JAR包扔到宿主主机的目录中，由Docker来启动容器即可。停止时，只需要将宿主主机目录中的JAR清理掉，重启一下Docker容器即可。

2. **打包JAR镜像方式**(适合云原生环境)：在存在Docker运行环境的机器中，通过推送JAR包和Dockerfile的方式，使用Dockerfile通过引入JDK镜像等执行后生成一个镜像，这个新的镜像中包含JAR包。用新的镜像来生成容器。

3. **生成新镜像并推送到私服中**(适合大型团队)：除了Docker 环境外，还需要连接内网私服的能力。Docker环境的机器只做构建，构建完成后连接Docker私服(harbor或dockerhub)，搭载Docker环境的机器接收到dockerfile和JAR包生成新的镜像，将新的镜像推送到Docker私服中，由K8s集群从私服中拉取镜像生成多个容器来运行

## 外挂目录方式

外挂目录方式不需要构建镜像。

```sh
docker pull openjdk:17-alpine

docker run -d -p 9999:9999 --name demo-out -v /root/jarfile/demo-0.0.1-SNAPSHOT.jar:/app.jar openjdk:17-alpine java -jar app.jar
```

在全局配置System中添加Docker环境目标远程服务器地址：

![image-20240402210057852](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404022101276.png)

添加运行之前的步骤：

**说明**：生产环境不建议使用`rm -rf` 清理

![image-20240402224715605](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404022247756.png)

添加运行之后的步骤：

![image-20240402224755945](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404022247515.png)

## Jar打包到容器内

1. 准备一台测试服务器 docker环境，将Jar包上传

2. 准备支持jdk的镜像，创建Dockerfile：

   ```sh
   # 使用OpenJDK 17
   FROM openjdk:17-alpine
   # 设置工作目录 (容器内路径)
   WORKDIR /root
   # 相对于工作目录
   ADD demo*.jar /root/app.jar
   # 指定默认执行程序和参数
   ENTRYPOINT ["java","-jar","/root/app.jar"]
   ```

3. 在Dockerfile目录下，执行打包构建命令：

   ```sh
   # 在.当前Dockerfile的路径下构建名为demo的镜像
   docker build -t mydemo .
   ```

4. 运行：

   ```
   docker run -d --name mdemo -p 9999:9999 mydemo
   ```

在项目上创建Dockerfile：

![image-20240402233228987](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404022332729.png)

在全局配置System中添加Docker环境目标远程服务器地址：

![image-20240402210057852](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404022101276.png)

添加运行之前的步骤：

**说明**：生产环境不建议清理，可以通过tag的方式区别镜像，出了问题才能及时回滚

![image-20240402235330916](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404022353930.png)

添加运行之后的步骤：

![image-20240403001619656](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404030016947.png)

![image-20240403001631339](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404030016015.png)

