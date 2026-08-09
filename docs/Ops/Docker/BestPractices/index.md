# Dockerfile 最佳实践

Dockerfile 是定义镜像构建过程的「配方」。本节面向已经会写基础 Dockerfile 的读者，目标是让镜像更小、更安全、构建更快、更可复现，并给出生产环境可以直接落地的写法。

::: info 适用版本
本节内容基于 Docker Engine 29.x（当前最新稳定版为 29.7.2，发布于 2026-08-05）与默认的 BuildKit 构建器。`docker build --check` 等命令需要 Docker 23.0 以上版本。
:::

## 为什么需要 Dockerfile 最佳实践

同样的应用，随手写的 Dockerfile 和经过设计的 Dockerfile，构建出的镜像体积可能相差数倍，构建耗时可能相差一个数量级，安全风险更是完全不同。最佳实践解决四类问题：

1. **可复现**：任何人在任何时间构建，得到的行为一致。
2. **小体积**：减少下载时间、磁盘占用和攻击面。
3. **快构建**：充分利用层缓存，减少重复下载依赖。
4. **安全**：默认以非 root 运行，最小化权限和泄露风险。

## 核心原则

| 原则 | 说明 |
| --- | --- |
| 一个容器一个职责 | 镜像只包含运行当前进程所需的最小文件集 |
| 按变化频率排序指令 | 变化少的指令放前面（依赖安装），变化多的放后面（业务代码） |
| 固定版本 | 基础镜像、依赖、包管理器锁文件都要固定版本 |
| 合并同类操作 | 把连续 `RUN` 合并，减少层数并便于统一清理 |
| 删除构建产物 | 临时文件、缓存、文档在构建过程中清理掉 |
| 默认非 root | 用 `USER` 切换到普通用户，降低逃逸后的影响 |

## 指令级最佳实践

### FROM：锁定基础镜像

不要直接使用 `FROM node:latest`。`latest` 会随上游更新而漂移，导致同一份 Dockerfile 在不同时间构建出不同行为。推荐固定大版本（如 `node:24-alpine`），对安全敏感的场景进一步固定到 digest：

```dockerfile
FROM node:24-alpine@sha256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

使用 `docker buildx imagetools inspect node:24-alpine` 可以查看镜像的 digest。

### LABEL：给镜像加元数据

记录维护者、版本、文档地址、许可证等信息，便于审计和自动化运维：

```dockerfile
LABEL org.opencontainers.image.authors="dev@example.com" \
      org.opencontainers.image.version="1.4.2" \
      org.opencontainers.image.source="https://github.com/example/app"
```

### RUN：合并命令并清理缓存

apt 场景的典型写法（注意最后清理包列表，避免把索引文件带进镜像）：

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

每条 `RUN` 会生成一层。合并命令一方面减少层数，另一方面让「安装 + 清理」发生在同一层，否则清理不掉前面层留下的文件。

### COPY 而不是 ADD

`ADD` 会自动解压本地 tar 包、支持远程 URL，行为隐式且容易误用；绝大多数场景用 `COPY` 就够了，可读性更好：

```dockerfile
COPY package.json package-lock.json ./
```

只有确实需要自动解压 tar 包时才用 `ADD`，且不要用 `ADD` 拉取远程文件——应该先用 `RUN curl` 下载再校验校验和。

### USER：非 root 运行

镜像里创建普通用户，并在最后切换：

```dockerfile
RUN addgroup -S app && adduser -S app -G app
USER app
```

`USER` 要放在安装依赖之后、启动命令之前，否则后续 `RUN` 装依赖会因为权限不足失败。

### ENTRYPOINT 与 CMD

推荐组合：`ENTRYPOINT` 固定进程，`CMD` 提供默认参数：

```dockerfile
ENTRYPOINT ["node"]
CMD ["server.js"]
```

这样运行 `docker run myapp --port 8080` 时，`--port 8080` 会追加到 `node` 之后，而不是替换整个命令。

### HEALTHCHECK：给容器健康状态

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
```

健康检查是编排系统（Compose、Swarm、K8s）滚动更新和自动恢复的前提。

### .dockerignore：缩小构建上下文

`docker build` 会把整个上下文（当前目录）发给构建器，`.git`、`node_modules`、`dist` 等都会拖慢构建甚至触发缓存失效。在项目根目录放 `.dockerignore`：

```text [.dockerignore]
.git
.gitignore
node_modules
dist
*.log
.env
.DS_Store
```

## 使用 BuildKit 高级特性

### docker build --check

Docker 23.0 开始可以只检查 Dockerfile 而不真正构建：

```shell
docker build --check .
```

它会提示指令是否已废弃、写法是否有问题，适合接入 CI 或提交前检查。

### 缓存挂载：加速依赖安装

普通层缓存只要依赖文件一变就会失效。BuildKit 提供 `--mount=type=cache`，把包管理器缓存目录挂到构建阶段：

```dockerfile
RUN --mount=type=cache,target=/root/.npm npm ci
```

```dockerfile
RUN --mount=type=cache,target=/root/.m2 mvn -B -DskipTests package
```

缓存不进入最终镜像，却能大幅减少重复下载。

### 密钥挂载：不把密钥写进镜像

构建私有依赖时，不要把 token 用 `ENV` 或 `COPY` 写进镜像：

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

构建时通过文件传入：

```shell
docker build --secret id=npmrc,src=$HOME/.npmrc .
```

密钥只存在于构建过程，不会出现在镜像层里。

### COPY --link

`COPY --link` 生成独立层，即使上游层变化，已经复制的层也可以复用缓存，还能避免层间依赖导致的缓存失效：

```dockerfile
COPY --link --from=build /app/dist /usr/share/nginx/html
```

## 实战：一个生产级 Node.js 镜像

综合上面的原则，写一个可复现、体积小、非 root 的 Node.js 镜像：

```dockerfile [Dockerfile]
FROM node:24-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

COPY . .
RUN npm run build

FROM node:24-alpine
ENV NODE_ENV=production
WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

COPY --chown=app:app --from=build /app/package.json /app/package-lock.json ./
COPY --chown=app:app --from=build /app/node_modules ./node_modules
COPY --chown=app:app --from=build /app/dist ./dist

USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:3000/healthz || exit 1
CMD ["node", "dist/server.js"]
```

构建并验证：

```shell
docker build --check .
docker build -t myapp:1.4.2 .
docker run --rm -p 3000:3000 myapp:1.4.2
```

打开 http://localhost:3000/healthz 确认返回正常，再看镜像里确实没有 root 用户：

```shell
docker run --rm --entrypoint id myapp:1.4.2
```

预期输出类似 `uid=100(app) gid=101(app)`。

## 易错点

::: danger 常见错误
1. 使用 `node:latest` 或 `FROM ubuntu` 不固定版本，导致「昨天能构建，今天不能」。
2. 每条 `RUN` 单独写、不清理缓存，镜像膨胀到几百 MB。
3. 把 `.env`、私钥、token 通过 `COPY . .` 带进镜像。
4. 忘记 `USER`，容器内始终是 root，一旦进程被攻破就是宿主 root 权限。
5. 把 `npm install` 放在 `COPY . .` 之后，业务代码一变就全部重新下载依赖。
6. `ADD https://...` 拉远程文件，无法断点续传也没有校验，应改为 `RUN curl -fSL ... && 校验`。
:::

## 验证方式

1. `docker build --check .` 无警告。
2. `docker build -t myapp:1.4.2 .` 构建成功。
3. `docker image inspect myapp:1.4.2` 查看 `Config.User` 为非 root。
4. `docker scout quickview myapp:1.4.2` 检查漏洞情况（需要 Docker Scout）。
5. 运行容器并访问健康检查地址，确认返回 200。

## 参考资料

- Docker 官方 Dockerfile 最佳实践：https://docs.docker.com/build/building/best-practices/
- BuildKit 缓存挂载：https://docs.docker.com/build/building/cache/
- Dockerfile 参考：https://docs.docker.com/reference/dockerfile/
- OCI Image Spec：https://github.com/opencontainers/image-spec
