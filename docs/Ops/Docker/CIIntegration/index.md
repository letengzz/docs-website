# Docker 与 CI/CD 集成

把「构建镜像 → 扫描 → 推送 → 部署」串进流水线，是镜像交付从手工走向自动化的关键一步。本节以 GitHub Actions 为例，覆盖构建缓存、多架构、镜像标签、测试与远程部署。

::: info 适用版本
示例使用 GitHub Actions 官方 Docker 系列 Action（setup-buildx-action、build-push-action 等），Compose 相关命令需要 Docker Compose v2.17+（`--wait`）。
:::

## 典型流水线

一条完整的镜像 CI 流水线至少包含：

```text
代码变更 → 单元测试 → 构建镜像（BuildKit） → 漏洞扫描 → 推送镜像 → 部署（SSH/容器平台）
```

测试和扫描失败就阻断，不推送、不部署。

## GitHub Actions 完整示例

```yaml [.github/workflows/docker.yml]
name: Build and Push Image

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,format=long

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          platforms: linux/amd64,linux/arm64
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true
```

要点：

- PR 只构建不推送（workflow 中已通过 `push` 字段判断事件类型），防止合入前的镜像污染仓库。
- `permissions` 里声明最小权限，只用 `packages: write` 推送镜像。
- `type=semver` 在打 tag 时自动生成 `1.4.2` 这类版本标签，配合 release 流程。
- `platforms` 需要 QEMU 支持交叉模拟；纯原生构建可以去掉。

## 缓存策略

| 缓存类型 | 适用环境 | 说明 |
| --- | --- | --- |
| `type=gha` | GitHub Actions | 缓存存 GitHub 的缓存服务，速度快、无需额外存储 |
| `type=registry` | 自建 Runner | 缓存作为镜像层推到镜像仓库，跨机器共享 |
| `type=inline` | 单机简单场景 | 缓存内嵌镜像，无法跨架构复用 |

多平台构建时，`cache-to: type=gha,mode=max` 会缓存所有阶段，避免每个架构重新编译依赖。

## 在 CI 中跑集成测试

镜像构建后，先用 Compose 起依赖和应用，跑完测试再决定是否推送：

```yaml [docker-compose.ci.yml]
services:
  db:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: test
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 3s
      retries: 20

  app:
    build: .
    environment:
      DB_URL: jdbc:mysql://db:3306/app
    depends_on:
      db:
        condition: service_healthy
```

```shell
docker compose -f docker-compose.ci.yml up -d --build --wait
docker compose -f docker-compose.ci.yml ps
```

测试通过后再进入推送和部署阶段。

## 部署：远程主机与容器平台

### 通过 Docker Context 远程部署

在 CI 里创建远程 context 并直接部署：

```shell
docker context create remote --docker "host=ssh://deploy@prod.example.com"
docker --context remote compose -f docker-compose.prod.yml up -d --pull always
```

SSH 密钥通过 GitHub Secrets 注入，不要写死在仓库。

### 通过 SSH 脚本部署

适合已有部署脚本的团队：

```yaml
      - name: Deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /srv/app
            docker compose pull
            docker compose up -d
```

### 推送到容器平台

如果使用 Kubernetes，推送镜像后由 Argo CD / Flux 检测新 digest 并滚动更新；如果使用 Docker Swarm，直接 `docker service update --image <镜像> <服务>`。

## 安全要求

1. 所有密钥走 Secrets，绝不在 workflow 或 `docker build --build-arg` 里传密码。
2. 构建密钥用 BuildKit secret mount：`docker build --secret id=...,src=...`。
3. 扫描在推送前执行，`docker scout cves` 或 Trivy 任一命中高危就 `exit 1`。
4. Action 版本建议固定到具体 SHA 或至少主版本，避免上游意外变更。
5. 镜像仓库开启不可变标签（immutable tags），防止 tag 被覆盖。

## 易错点

::: danger 常见错误
1. PR 也推镜像，`main` 还没合并，`latest` 已被污染。
2. 忘记配置 `cache-to`，每次构建都全量重跑，CI 越来越慢。
3. 多平台构建没有 `setup-qemu-action`，arm64 直接失败。
4. 密码通过 `--build-arg` 传给 Dockerfile，最终留在镜像层里。
5. 部署时没有 `--pull always`，远程主机一直用旧镜像。
6. 把 `GITHUB_TOKEN` 权限设成 `write-all`，仓库被攻破时影响面过大。
:::

## 验证方式

1. 推送代码后，GitHub Actions 工作流全部步骤通过。
2. 镜像仓库能看到 `main`、`sha-xxxxxxxx` 等标签。
3. 本地 `docker run --rm ghcr.io/<org>/<repo>:<sha>` 能正常启动。
4. 远程主机执行 `docker compose ps` 确认服务使用新镜像。
5. 故意引入一个高危依赖，确认扫描步骤会阻断流水线。

## 参考资料

- docker/build-push-action：https://github.com/docker/build-push-action
- Docker Buildx GitHub Actions：https://docs.docker.com/build/ci/github-actions/
- 多平台镜像：https://docs.docker.com/build/multi-platform/
- GitHub Actions 安全加固：https://docs.github.com/actions/security-for-github-actions
