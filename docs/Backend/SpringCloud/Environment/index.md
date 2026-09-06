# 环境搭建与项目脚手架

跑通 Spring Cloud 不需要重型环境：本地开发只需要 **JDK + Maven/Gradle + 一个注册中心**（Nacos 单机或 Eureka 服务端）。本页给出从零到“两个服务互相发现”的完整环境步骤与版本清单。

::: info 当前推荐环境（2026-09 核对）
| 工具 | 版本 | 说明 |
| --- | --- | --- |
| JDK | 17+（推荐 25 LTS） | Spring Boot 4 最低 Java 17 |
| Maven | 3.9+ | 也可以换 Gradle 8.x |
| Spring Boot | 4.0.x/4.1.x | 当前稳定大版本 |
| Spring Cloud | 2025.1.x（Oakwood） | 对应 Boot 4 |
| Nacos Server | 3.1.x/3.2.x | 开发用 standalone 单机即可 |
| Docker | 任意较新版本 | 用于快速启动 Nacos 等中间件 |
| 前端构建 | Node 20+（本库文档站用） | 与 Java 环境无关 |
:::

## 1. 安装 JDK 与构建工具

```shell [shell]
# Windows 可用 winget 安装（或用 Oracle/Adoptium 安装包）
winget install EclipseAdoptium.Temurin.25.JDK

# 检查版本
java -version
mvn -version
```

验证结果应看到类似输出：`openjdk version "25.x" ...` 与 `Apache Maven 3.9.x`。

::: danger JDK 版本坑
Spring Boot 4 + Spring Cloud 2025.1 最低要求 Java 17。若本机默认 JDK 是 8，启动会直接报 `UnsupportedClassVersionError`；请用 IDE 或环境变量把项目指向 JDK 17+。
:::

## 2. 启动注册中心 Nacos（单机）

Nacos 3.x 官方镜像直接支持单机模式：

```shell [shell]
docker run -d --name nacos \
  -p 8848:8848 -p 9848:9848 -p 9849:9849 \
  -e MODE=standalone \
  nacos/nacos-server:v3.1.1

# 查看启动日志
docker logs -f nacos
```

验证方式：

1. 访问 `http://127.0.0.1:8848/nacos`，看到 Nacos 控制台登录页。
2. 默认账号密码均为 `nacos`（3.x 首次登录会提示修改，本地开发可跳过或修改后记住）。
3. 日志出现 `Nacos started successfully in stand alone mode` 即启动成功。

::: danger 端口说明
**8848（HTTP）+ 9848/9849（gRPC）都要映射**。Nacos 2.x/3.x 客户端通过 gRPC 长连接通信，只开 8848 会导致服务间歇性掉线。Docker 部署建议显式映射三个端口，避免后续排查半天。
:::

## 3. 创建项目骨架

两种方式任选：

### 方式一：start.spring.io

访问 https://start.spring.io 或 IDE 内置 Initializr，选择：

| 项目 | 依赖 |
| --- | --- |
| provider | Spring Web、Nacos Service Discovery（Spring Cloud Alibaba） |
| consumer | Spring Web、Nacos Service Discovery、OpenFeign |

生成后在 `pom.xml` 中加入 SCA BOM：

```xml [pom.xml]
<properties>
    <spring-cloud.version>2025.1.2</spring-cloud.version>
    <spring-cloud-alibaba.version>2025.1.0.0</spring-cloud-alibaba.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>${spring-cloud.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-alibaba-dependencies</artifactId>
            <version>${spring-cloud-alibaba.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 方式二：命令行手工创建

用 Maven 骨架生成基本工程，再按上文加入两个 BOM 与依赖（依赖写法见 [服务注册与发现](../Discovery/index.md)）。

## 4. 最小配置

每个服务只需配置应用名与注册中心地址：

```yaml [application.yml]
spring:
  application:
    name: provider          # 注册到 Nacos 的服务名
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
server:
  port: 8080
```

## 5. 启动与验证

```shell [shell]
# 在 provider 与 consumer 目录分别执行
mvn spring-boot:run
```

启动后打开 Nacos 控制台 →「服务管理 → 服务列表」，应看到：

| 服务名 | 集群 | 实例数 | 健康实例 |
| --- | --- | --- | --- |
| provider | DEFAULT | 1 | 1/1 |
| consumer | DEFAULT | 1 | 1/1 |

::: tip 补充建议
1. 本地联调时建议关闭注册中心的心跳告警噪音：开发期 Nacos 实例健康检查周期默认即可，不用额外调参。
2. 一个服务多实例验证负载均衡时，用 `-Dserver.port=8081` 启动第二个实例，确认 Nacos 中出现两个实例。
:::

## 常见问题速查

| 现象 | 原因与处理 |
| --- | --- |
| 启动报 `No spring.config.import property` | 用 SCA 2025.x 时 bootstrap 已移除，参考 [配置中心](../ConfigCenter/index.md) 加 `spring.config.import=nacos:` |
| 服务列表一直空 | 检查 `spring.cloud.nacos.discovery.server-addr` 拼写与 9848 端口映射 |
| 注册成功但 30 秒后被摘除 | gRPC 端口不通或网络防火墙拦截，检查 9848 |
| `mvn dependency:tree` 出现两个 spring-cloud 版本 | 两个 BOM 顺序或版本冲突，统一用父 POM 管理 |

## 参考资料

- Spring Initializr：https://start.spring.io
- Nacos 官方快速开始：https://nacos.io/docs/latest/quickstart/quick-start/
- Spring Cloud 快速开始：https://docs.spring.io/spring-cloud/reference/spring-cloud.html
