# 多阶段构建

多阶段构建（Multi-stage Build）允许在一个 Dockerfile 里定义多个 `FROM` 阶段，最终镜像只保留最后一个阶段的内容。它是当前缩小镜像体积、避免「构建环境 + 运行环境」混在一起的标准方案。

::: info 适用版本
多阶段构建是 BuildKit 的核心能力，Docker 23.0 之后 BuildKit 为默认构建器，可直接使用。
:::

## 为什么需要多阶段构建

编译型应用的经典困境：构建需要 JDK/Maven、Go 工具链、Node 等大型工具，但运行时根本不需要它们。传统做法是写两个 Dockerfile（一个构建、一个运行）再手动拷贝产物，容易出错、难维护。

多阶段构建把这件事放进同一个 Dockerfile：

1. 前一阶段负责下载依赖、编译、打包，环境可以很「重」。
2. 后一阶段只复制编译产物，使用精简运行镜像。
3. 构建阶段的中间层默认不会进入最终镜像。

## 基本语法

```dockerfile
FROM golang:1.26-alpine AS build
# 第一阶段：编译

FROM alpine:3.22
# 第二阶段：运行
```

关键点：

| 语法 | 作用 |
| --- | --- |
| `FROM xxx AS build` | 给阶段命名，后续用名字引用 |
| `COPY --from=build 源 目标` | 从指定阶段复制文件，也可以直接写阶段序号 |
| `--target build` | 构建到某个阶段就停止，用于调试 |
| `--output` | 只导出指定阶段的文件，不产出镜像 |

## 实战一：Go 静态二进制

```dockerfile [Dockerfile]
FROM golang:1.26-alpine AS build
WORKDIR /src

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/app ./cmd/app

FROM alpine:3.22
RUN addgroup -S app && adduser -S app -G app
COPY --from=build /out/app /usr/local/bin/app
USER app
ENTRYPOINT ["app"]
```

`CGO_ENABLED=0` 产出纯静态二进制，可以运行在没有 glibc 的精简镜像上。`-s -w` 去掉符号表和调试信息，进一步减小体积。

构建与验证：

```shell
docker build -t goapp:latest .
docker images goapp
docker run --rm --entrypoint id goapp:latest
```

## 实战二：Java（Maven）

```dockerfile [Dockerfile]
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace

COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline

COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /workspace/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

构建阶段使用完整的 Maven 镜像，运行阶段只保留 JRE 和 jar 包。示例使用 Java 21 LTS；生产项目按实际需要可切换到 Java 25 LTS 对应的 `eclipse-temurin:25-jre`。

## 实战三：Node.js 前端产物

```dockerfile [Dockerfile]
FROM node:24-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

COPY . .
RUN npm run build

FROM nginx:stable-alpine
COPY --link --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

前端项目通常只关心构建产物，最终镜像直接使用 nginx 官方镜像托管静态文件即可。

## 调试与产物导出

只构建到编译阶段，方便检查中间产物：

```shell
docker build --target build -t myapp:build .
docker run --rm -it myapp:build sh
```

只导出文件、不生成镜像（配合 `--output`）：

```shell
docker build --target=build --output type=local,dest=out .
```

`out` 目录里就是编译阶段的文件系统内容，适合在 CI 里提取产物归档。

## 多阶段与缓存对比

| 项目 | 单阶段构建 | 多阶段构建 |
| --- | --- | --- |
| 最终镜像 | 包含编译器、源码、缓存 | 只含运行文件和依赖 |
| 镜像体积 | 数百 MB 起 | 通常缩小 5~10 倍 |
| 构建环境 | 与运行环境混在一起 | 相互隔离 |
| 密钥泄露面 | 构建密钥可能留在镜像 | 密钥只出现在构建阶段 |
| 维护成本 | 两个 Dockerfile 难同步 | 一个 Dockerfile，逻辑清晰 |

## 易错点

::: danger 常见错误
1. `COPY --from=build` 写错阶段名（`AS` 名称拼写不一致），构建直接报错。
2. 编译阶段没有 `--mount=type=cache`，依赖每次都重新下载，多阶段只省体积、不省时间。
3. 运行阶段直接复制整个 `node_modules` 或 `target/`，把测试依赖、源码也带进镜像。
4. 忘记 `.dockerignore`，构建上下文把 `node_modules`、`.git` 全部传给构建器。
5. 多阶段只是「把命令分到两个 FROM」却没有精简运行镜像，最终体积仍然很大。
6. 用 `COPY --from=0` 这种序号引用阶段，一旦调整阶段顺序就失效，建议始终用阶段名。
:::

## 验证方式

1. `docker build -t <app> .` 构建成功。
2. `docker images <app>` 对比单阶段镜像，确认体积显著下降。
3. `docker run --rm <app>` 应用能正常启动并响应请求。
4. `docker history <app>` 查看层列表，确认只有运行阶段的内容。

## 参考资料

- Docker 官方多阶段构建：https://docs.docker.com/build/building/multi-stage/
- BuildKit 缓存：https://docs.docker.com/build/building/cache/
- Dockerfile `FROM --platform` 与阶段引用：https://docs.docker.com/reference/dockerfile/
