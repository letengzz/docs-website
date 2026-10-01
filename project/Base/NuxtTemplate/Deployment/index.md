# 部署与上线

初始化产物是一份 Nuxt 工程，它的部署方式取决于**渲染模式**：SSG 产物是静态文件，SSR 产物是一个 Node 服务。这一步把它们分别送到对应的地方，并配好「谁能上线、怎么回滚」。

![部署拓扑：静态产物走 CDN，SSR 产物走 Node 容器](../assets/deploy-topology.svg)

## 1. 三种部署形态

| 形态 | 渲染模式 | 产物 | 运行时 | 典型场景 |
| --- | --- | --- | --- | --- |
| **静态托管** | SSG / SPA | `.output/public/` | 无（CDN/对象存储） | 文档站、营销页、纯前端后台 |
| **Node 服务** | SSR / 混合 | `.output/`（含 `server/index.mjs`） | Node 24 LTS | 需要 SEO + 个性化内容 |
| **边缘 / Serverless** | SSR | 平台专用产物 | 平台运行时 | 全球低延迟、流量波动大 |

::: tip 形态是渲染模式的函数，不是另一个选择
引导页已经问过渲染模式了，部署形态就随之确定——两者一致才不会出现「选了 SSG 却想跑 Node 服务」这种错配。选 SSG 时 [构建篇](../Build/index.md) 的 `pnpm generate` 才是主命令。
:::

## 2. Docker 多阶段构建（Node 服务形态）

### 2.1 Dockerfile

```dockerfile [Dockerfile]
# ---------- 阶段 1：依赖 ----------
FROM node:24-alpine AS deps
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# ---------- 阶段 2：构建 ----------
FROM node:24-alpine AS builder
WORKDIR /app
RUN corepack enable
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# 构建期变量：只放会进客户端产物的公开值
ARG NUXT_PUBLIC_SITE_URL
ENV NUXT_PUBLIC_SITE_URL=$NUXT_PUBLIC_SITE_URL
RUN pnpm build

# ---------- 阶段 3：运行时 ----------
FROM node:24-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

# 非 root 运行
RUN addgroup -S app && adduser -S app -G app

# 只复制构建产物：不要把整个 node_modules 带进镜像
COPY --from=builder --chown=app:app /app/.output ./.output

USER app
EXPOSE 3000

# 容器内存上限内自适应（不要写死 -Xmx 这类固定值）
ENV NODE_OPTIONS="--max-old-space-size=384"

# 用 exec 形式，保证信号可达 → docker stop 能秒级优雅退出
CMD ["node", ".output/server/index.mjs"]
```

配套的 `.dockerignore`：

```text
node_modules
.nuxt
.output
.git
.init-backup
template.init.lock
test
coverage
*.log
.env*
!.env.example
```

::: danger 镜像构建的五个必须

1. **只拷 `.output`**。复制整个 `node_modules` 会把 devDependencies 与构建工具一起打进镜像，体积可能翻十倍。
2. **`--frozen-lockfile`**。不加意味着容器里可能解析出与本地不同的依赖版本，「构建通过、线上白屏」的经典来源。
3. **非 root 用户**。Node 镜像默认 root，一旦进程被攻破后果放大。
4. **`CMD` 用 exec 形式（JSON 数组）**。shell 形式会让 `node` 成为 shell 的子进程，`SIGTERM` 到不了它，`docker stop` 只能等超时强杀。
5. **`ENV NODE_OPTIONS` 设一个合理上限**。注意这里必须是**运行期**变量，而不是构建期。
:::

### 2.2 编排

```yaml [compose.yaml]
services:
  web:
    build:
      context: .
      args:
        NUXT_PUBLIC_SITE_URL: ${NUXT_PUBLIC_SITE_URL:?必须在 .env 中提供}
    image: registry.example.com/nuxt-app:${IMAGE_TAG:?必须显式指定镜像标签，禁止 latest}
    env_file:
      - .env.production
    environment:
      # 运行期变量：同一镜像可部署到多环境
      NUXT_PUBLIC_API_BASE: ${NUXT_PUBLIC_API_BASE:?}
      NUXT_API_SECRET: ${NUXT_API_SECRET:?}
    ports:
      - '127.0.0.1:3000:3000'
    healthcheck:
      test: ['CMD', 'node', '-e', "fetch('http://127.0.0.1:3000/api/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 20s
    restart: unless-stopped
```

::: warning `${VAR:?}` 的意义
它让「缺配置」变成**启动失败**而不是「用默认值悄悄跑起来」。生产环境的密钥缺失如果被默认值兜住，你会得到一个「能访问但功能全错」的站点——比直接起不来难排查得多。
:::

### 2.3 反向代理与缓存

| 场景 | 规则 |
| --- | --- |
| 静态资源（`/_nuxt/*`） | 强缓存（`Cache-Control: public, max-age=31536000, immutable`），文件名含哈希可放心 |
| HTML | 短缓存或不缓存（SSR 内容可能随时变） |
| API（`/api/*`） | 不缓存 |
| 压缩 | 已由 `nitro.compressPublicAssets` 预压缩，Nginx 只需 `gzip_static on` |

```nginx [nginx 片段]
location /_nuxt/ {
  proxy_pass http://127.0.0.1:3000;
  gzip_static on;
  add_header Cache-Control "public, max-age=31536000, immutable";
}

location / {
  proxy_pass http://127.0.0.1:3000;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;      # SSE / HMR 需要
}
```

::: danger 反代的三条必配
1. **`X-Forwarded-For` / `X-Forwarded-Proto`**：不传的话 Nuxt 拿到的都是 `127.0.0.1` 与 `http`，会导致重定向循环、cookie secure 判定错误。
2. **`proxy_http_version 1.1` + `Upgrade`**：不配则 SSE 与 WebSocket 不可用（注意：引导器只在开发模式存在，生产不需要，但业务可能用）。
3. **超时**：SSR 首次渲染可能超过默认 60 秒（冷启动 + 慢接口），需要显式设 `proxy_read_timeout`。
:::

## 3. 环境变量注入

| 变量 | 何时注入 | 说明 |
| --- | --- | --- |
| `NUXT_PUBLIC_*` | 构建期或运行期均可 | 运行期注入更灵活：同一个镜像可部署多环境 |
| 服务端秘密（`NUXT_API_SECRET` 等） | **只能运行期** | 绝不能进构建产物 |
| `PORT` / `HOST` | 运行期 | 交给编排层 |

```shell
# 本地验证运行期变量生效（同一个构建产物，两个环境）
docker build -t nuxt-app:test .
docker run --rm -p 3000:3000 -e NUXT_PUBLIC_API_BASE=https://a.example.com nuxt-app:test &
curl -s http://localhost:3000 | grep -o 'a\.example\.com' | head -1
# 期望：能匹配到（说明运行期变量真的被读取）
```

::: danger 两类变量不要混
- `NUXT_PUBLIC_*` → `runtimeConfig`，**运行期**读取，改值不用重新构建。
- `VITE_*` → Vite 构建期变量，会**内联进客户端 JS**，改值必须重新构建，且值会出现在源码里。

需要保密的、需要按环境切换的，一律走前者。这条在 [应用基线](../AppBaseline/index.md) 里也强调过——因为它是 Nuxt 项目最常见的一类安全事故。
:::

## 4. CI/CD 流水线

五阶段，按**失败代价**排序（秒级检查前置）：

```yaml [.github/workflows/ci.yml]
name: ci
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  static:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 11 }
      - uses: actions/setup-node@v4
        with: { node-version: 24, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm dlx nuxi typecheck
      - run: pnpm test

  template:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 24 }
      # 引擎零依赖，不需要 pnpm install
      - run: node scripts/selftest.mjs
      - run: node scripts/init.mjs --check
```

```yaml [.github/workflows/release.yml（节选）]
  build-and-push:
    needs: [static, template]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ vars.REGISTRY }}
          username: ${{ secrets.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          # 标签分层：身份标签（不可变）+ 版本标签；不生成 latest
          tags: |
            ${{ vars.REGISTRY }}/nuxt-app:sha-${{ github.sha }}
            ${{ vars.REGISTRY }}/nuxt-app:${{ github.ref_name }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true
```

### 4.1 标签策略

| 层 | 例子 | 会不会变 | 用途 |
| --- | --- | --- | --- |
| 身份 | `sha-9ecce75a1b2c` | 永不变 | 部署、回滚、审计引用 |
| 版本 | `1.2.0` | 永不变 | 对外沟通 |
| 环境指针 | `prod` | **会变** | 只能用来问「现在跑的是什么」 |
| 便利 | `latest` | 会变 | **不生成** |

::: danger 部署命令里只能出现身份标签
`IMAGE_TAG=prod` 会被后续任何一次发布静默改写，于是「线上跑的是哪次提交」这个问题永远没有答案。部署必须写 `IMAGE_TAG=sha-<commit>`；`prod` 指针只用于查询当前版本。
:::

### 4.2 两处缓存与「无缓存周检」

| 缓存 | 键 | 失效风险 |
| --- | --- | --- |
| pnpm store | `pnpm-lock.yaml` 哈希 | 锁文件不变但依赖树变了（罕见） |
| Docker GHA | 镜像层 + 构建上下文 | 缓存命中导致「改了代码产物没变」 |

**每周跑一次无缓存流水线**（`cache-from` 全部去掉），确认缓存没有掩盖问题。这条纪律的价值在于：缓存出问题时，症状是「莫名其妙」而不是「明确报错」。

## 5. 健康检查与可观测

```ts [server/api/health.get.ts]
export default defineEventHandler(() => ({
  status: 'ok',
  uptime: Math.round(process.uptime()),
}));
```

| 探针 | 判据 | 频率 | 失败动作 |
| --- | --- | --- | --- |
| **存活（liveness）** | 进程能响应 `/api/health` | 15s | 重启容器 |
| **就绪（readiness）** | 依赖（后端 API / 数据库）可用 | 15s | **摘掉流量**，不重启 |

::: warning 存活与就绪必须分开
混用的后果很具体：当后端接口抖动时，就绪探针失败会被当成存活失败 → 容器被反复重启 → 冷启动叠加抖动 → 雪崩。存活只问「进程还活着吗」，就绪才问「能不能服务」。
:::

## 6. 部署流程（可照做）

```shell
# ① 本地先过全部门禁
pnpm lint && pnpm dlx nuxi typecheck && pnpm test
node scripts/selftest.mjs && node scripts/init.mjs --check

# ② 生产构建 + 本地预览（关键的一步，别省）
pnpm build && pnpm preview
# 期望：http://localhost:3000 页面正常、控制台 0 error

# ③ 构建并推送镜像（身份标签）
docker build -t registry.example.com/nuxt-app:sha-$(git rev-parse --short=12 HEAD) .
docker push registry.example.com/nuxt-app:sha-$(git rev-parse --short=12 HEAD)

# ④ 部署（用身份标签）
IMAGE_TAG=sha-$(git rev-parse --short=12 HEAD) docker compose up -d
docker compose ps          # 期望：healthy

# ⑤ 冒烟
bash scripts/smoke.sh http://127.0.0.1:3000
# 期望：5/5 通过（首页 200、静态资源 200、health ok、404 正常、无引导器路由）

# ⑥ 回滚（如需）
IMAGE_TAG=sha-<上一个提交> docker compose up -d
```

## 7. 验证方式

```shell
# ① 镜像体积与用户
docker images registry.example.com/nuxt-app:sha-xxx --format '{{.Size}}'
docker run --rm registry.example.com/nuxt-app:sha-xxx whoami
# 期望：体积在几百 MB 量级（不是 GB）；whoami 输出 app（非 root）

# ② 优雅退出
docker stop <container>   # 期望：1 秒内退出，不是等 10 秒超时

# ③ 运行期变量
# 见第 3 节的 docker run 验证

# ④ 健康检查
curl -s http://127.0.0.1:3000/api/health
# 期望：{"status":"ok","uptime":...}

# ⑤ 引导器不存在于生产
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/api/wizard/schema
# 期望：404

# ⑥ 静态资源缓存头
curl -sI http://127.0.0.1:3000/_nuxt/entry.xxx.js | grep -i cache-control
# 期望：含 immutable 与 max-age=31536000
```

## 相关页面

- [构建与产物形态](../Build/index.md)：`.output/` 里到底是什么
- [验收与上线检查](../Acceptance/index.md)：部署之后的验收清单
- [质量门禁与自测](../Quality/index.md)：流水线里各条门禁的来源
- [后端通用模板 · 容器化与 Compose](../../BackendTemplate/Deployment/index.md)：同一套容器化思路的服务端版本

## 参考资料

- Nuxt 部署指南：[nuxt.com/docs/getting-started/deployment](https://nuxt.com/docs/getting-started/deployment)
- Nitro 部署预设：[nitro.build/deploy](https://nitro.build/deploy)
- Docker 多阶段构建：[docs.docker.com/build/building/multi-stage](https://docs.docker.com/build/building/multi-stage/)
- K8s 存活与就绪探针：[kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
