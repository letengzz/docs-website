# SpringBoot Docker编排支持

Docker Compose是一种流行的技术，可用于定义和管理应用程序所需服务的多个容器。通常，在应用程序旁边创建一个`compose.yml`文件，该文件定义并配置服务容器。

使用Docker Compose的典型工作流程是运行`docker compose up`，使用它与启动的服务一起处理应用程序，然后在完成后运行`docker compose down`。

可以将`spring-boot-docker-compose`模块包含在项目中，以提供使用Docker Compose与容器一起工作的支持。将模块依赖项添加到构建中。

spring-boot-docker-compose核心功能：

1. 协助管理(启动、停止)Docker Compose 服务
2. 读取docker-compose 文件，自动配置application.yml

官方说明：https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.1-Release-Notes#docker-compose

官方文档：https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/features.html#features.docker-compose

:::danger 注意

为了使Spring Boot的支持能够正常工作，`docker compose`或`docker-compose` CLI应用程序需要在你的路径中。

:::

将此模块作为依赖项包含时，Spring Boot将执行以下操作：

- 在应用程序目录中搜索`compose.yml`和其它常见的compose文件名
- 使用找到的`compose.yml`调用`docker compose up`
- 为每个受支持的容器创建服务连接bean
- 当应用程序关闭时，调用`docker compose stop`

如果在启动应用程序时Docker Compose服务已经正在运行，则Spring Boot将只为每个受支持的容器创建服务连接bean。它不会再次调用`docker compose up`，并且在应用程序关闭时也不会调用`docker compose stop`。

:::danger 注意

默认情况下，在运行测试时，Spring Boot的Docker Compose支持被禁用。要启用它，请将`spring.docker.compose.skip.in-tests`设置为`false`。

:::

添加spring-boot-docker-compose依赖：

```xml
<dependency>
	<groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-docker-compose</artifactId>
	<scope>runtime</scope>
	<optional>true</optional>
</dependency>
```

Docker Compose启动后，spring-boot-docker-compose会自动识别Docker Compose中的服务，然后自动完成对应的服务连接配置，如Redis服，会自动配置 `spring.redis.host` 和 `spring.redis.port`，MySQL服务会自动配置 `spring.datasource.url`、`spring.datasource.username` 和 `spring.datasource.password`等。如果在application.yaml/application.properties 中已经进行了配置，那么spring-boot-docker-compose会覆盖对应的配置，确保应用连接到Docker Compose中的服务上。

在docker-compose.yml文件，不需要设置端口映射，只需要设置暴露端口，然后使用随机端口进行映射。不用担心随机端口的问题，spring-boot-docker-compose会自动识别随机端口，然后自动完成对应的配置的。

添加compose.yaml文件：

```yaml [compose.yaml]
services:
  mysql:
    image: 'mysql:latest'
    environment:
      - 'MYSQL_DATABASE=mydatabase'
      - 'MYSQL_PASSWORD=secret'
      - 'MYSQL_ROOT_PASSWORD=verysecret'
      - 'MYSQL_USER=myuser'
    ports:
      - '13306:3306'
```

配置文件添加docker配置文件的路径：

```yaml [application.yaml]
spring:
  application:
    name: springboot_docker
  docker:
    compose:
      file: ./compose.yaml
```

此时会自动构建容器：

![image-20240804124232389](assets/img202408041242871.png)

测试MySQL连接：

![image-20240804124837196](assets/img202408041248820.png)

![image-20240804124957752](assets/img202408041249386.png)

## 服务连接

服务连接是到任何远程服务的连接。Spring Boot的自动配置可以消耗服务连接的详细信息，并使用它们来建立与远程服务的连接。在这样做时，连接详细信息优先于任何与连接相关的配置属性。

当使用Spring Boot的Docker Compose支持时，将建立与服务容器映射的端口的连接。

:::danger 注意

Docker Compose通常以这样的方式使用，即将容器内部的端口映射到计算机上的临时端口。例如，PostgreSQL服务器可能在容器内部使用端口5432运行，但在本地映射到完全不同的端口。服务连接将始终发现和使用本地映射的端口。

:::

通过使用容器的镜像名称来建立服务连接。目前支持以下服务连接：

![image-20240804125423330](assets/img202408041254219.png)

## 自定义镜像

有时你可能需要使用自己的镜像版本来提供服务。只要行为与标准镜像相同，就可以使用任何自定义镜像。具体来说，标准镜像支持的所有环境变量也必须在自定义镜像中使用。

如果镜像使用不同的名称，则可以在`compose.yml`文件中使用标签，以便Spring Boot可以提供服务连接。使用名为`org.springframework.boot.service-connection`的标签来提供服务名称。

```yaml
services:
  redis:
    image: 'mycompany/mycustomredis:7.0'
    ports:
      - '6379'
    labels:
      org.springframework.boot.service-connection: redis
```

## 跳过特定容器

如果在`compose.yml`中定义了一个容器镜像，并且不想将其连接到你的应用程序，则可以使用标签来忽略它。带有`org.springframework.boot.ignore`标签的任何容器都将被Spring Boot忽略。

```yaml
services:
  redis:
    image: 'redis:7.0'
    ports:
      - '6379'
    labels:
      org.springframework.boot.ignore: true
```

## 使用特定的Compose文件

如果compose 文件与应用程序不在同一目录中，或者名称不同，则可以在`application.properties`或`application.yaml`中使用`spring.docker.compose.file`指向不同的文件。可以将属性定义为确切的路径或相对于应用程序的路径。

```yaml
spring.docker.compose.file=../my-compose.yml
```

## 等待容器就绪

通过Docker Compose启动的容器可能需要一些时间才能完全就绪。检查就绪状态的推荐方法是在`compose.yml`文件中的服务定义下添加`healthcheck`部分。

由于`compose.yml`文件中省略健康检查配置并不罕见，因此Spring Boot还会直接检查服务就绪状态。默认情况下，当可以建立到其映射端口的TCP/IP连接时，容器被视为已就绪。

可以通过在`compose.yml`文件中添加`org.springframework.boot.readiness-check.tcp.disable`标签来按容器禁用此功能。

```yaml
services:
  redis:
    image: 'redis:7.0'
    ports:
      - '6379'
    labels:
      org.springframework.boot.readiness-check.tcp.disable: true
```

还可以在`application.properties`或`application.yaml`文件中更改超时值：

```yaml
spring.docker.compose.readiness.tcp.connect-timeout=10s
spring.docker.compose.readiness.tcp.read-timeout=5s
```

整体超时可以通过`spring.docker.compose.readiness.timeout`进行配置。

## 控制Docker Compose的生命周期

默认情况下，当应用程序启动时，Spring Boot会调用`docker compose up`，而当其关闭时会调用`docker compose stop`。如果希望使用不同的生命周期管理，则可以使用`spring.docker.compose.lifecycle-management`属性。

支持以下值：

- none - 不启动或停止Docker Compose
- start-only - 当应用程序启动时启动Docker Compose并让其保持运行状态
- start-and-stop - 当应用程序启动时启动Docker Compose，当JVM退出时停止它

此外，还可以使用`spring.docker.compose.start.command`属性来更改是使用`docker compose up`还是`docker compose start`。`spring.docker.compose.stop.command`允许配置是使用`docker compose down`还是`docker compose stop`。

以下示例显示了如何配置生命周期管理：

```yaml
spring.docker.compose.lifecycle-management=start-and-stop
spring.docker.compose.start.command=start
spring.docker.compose.stop.command=down
spring.docker.compose.stop.timeout=1m
```

## 激活Docker Compose profile

Docker Compose profile类似于Spring profile，它允许你为特定环境调整Docker Compose配置。如果要激活特定的Docker Compose profile，可以在`application.properties`或`application.yaml`文件中使用`spring.docker.compose.profiles.active`属性：

```yaml
spring.docker.compose.profiles.active=myprofile
```
