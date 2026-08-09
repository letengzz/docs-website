# Docker Compose 进阶

Compose 进阶内容解决多服务编排中的真实问题：启动顺序、健康检查、资源限制、环境变量管理、敏感信息、多环境复用。本节默认使用 Compose V2（`docker compose` 命令，当前 v2.40+），不再讨论已停止维护的 V1 写法。

::: info 适用版本
当前 Docker Compose 为 v2.40 以上版本。`docker compose watch` 需要 v2.22+，`include` 需要 v2.20+，`docker compose up --wait` 需要 v2.17+。
:::

## 启动顺序与健康检查

`depends_on` 控制服务启动顺序。短语法只保证「先启动」，不保证依赖服务已就绪；要等服务真正可用，用长语法配合 `healthcheck`：

```yaml [compose.yaml]
services:
  db:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-root}
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  app:
    build: .
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8080:8080"
```

`depends_on` 条件：

| 条件 | 含义 |
| --- | --- |
| `service_started` | 依赖服务已启动（默认，等同于短语法） |
| `service_healthy` | 依赖服务健康检查通过 |
| `service_completed_successfully` | 依赖服务成功运行完毕后退出（适合一次性任务） |

等待所有依赖健康后再启动：

```shell
docker compose up -d --wait
docker compose ps
```

## 资源限制与重启策略

```yaml
services:
  app:
    image: myapp:1.4.2
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 256M
    restart: unless-stopped
```

- `deploy.resources.limits` 是 Compose 规范的推荐写法，新版 Compose 会在本地容器生效；老项目也常见 `mem_limit: 256m`、`cpus: 0.5` 的旧字段。
- `restart` 建议生产用 `unless-stopped`；`on-failure:3` 适合只想在失败时重启的任务。
- `healthcheck` 失败不会自动重启容器，重启策略和健康检查是两件事，不要混用。

## 环境变量与 .env

Compose 支持在 `compose.yaml` 中使用 `${VAR}` 插值，并从 `.env` 文件读取默认值：

```yaml
services:
  nginx:
    image: nginx:${NGINX_TAG:-1.27-alpine}
    environment:
      APP_ENV: ${APP_ENV:-development}
    env_file:
      - ./env/${APP_ENV}.env
```

优先级从低到高：

1. Compose 内置默认值（`${VAR:-default}` 中的 default）。
2. `.env` 文件。
3. shell 环境中已导出的变量。
4. 命令行 `--env-file` 指定的文件（可覆盖 `.env`）。

注意：`.env` 是「给 Compose 插值用的」，不会自动进入容器；容器环境变量要写 `environment` 或 `env_file`。

## 敏感信息：secrets

密码、token 不要写死在 `environment` 里，优先使用 Compose secrets：

```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt

services:
  app:
    image: myapp:1.4.2
    secrets:
      - db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
```

容器内默认挂载到 `/run/secrets/db_password`，应用按需读取，避免镜像层残留密钥。`secrets/` 目录应加入 `.gitignore`。

## 多环境复用：profiles 与 include

`profiles` 让默认不启动的「可选服务」按需启用：

```yaml
services:
  debug:
    image: nicolaka/netshoot
    profiles: ["debug"]
```

```shell
docker compose --profile debug up -d
```

`include` 可以把其他 Compose 文件合并进来，适合拆分配置：

```yaml
include:
  - path: ./compose.d/redis.yaml
```

## 开发模式：docker compose watch

Compose v2.22+ 支持 `watch` 配置，文件变化后自动同步、重建或重启：

```yaml
services:
  web:
    build: .
    develop:
      watch:
        - path: ./src
          action: sync
          target: /app/src
        - path: ./package.json
          action: rebuild
```

```shell
docker compose watch
```

## 网络与卷的复用

```yaml
services:
  api:
    image: myapp:1.4.2
    networks:
      - app-net
    volumes:
      - app-data:/data

networks:
  app-net:
    driver: bridge

volumes:
  app-data:
```

同网络内的服务可以用服务名互相访问（如 `http://api:8080`），这是 Compose 最常见的服务发现方式。

## 易错点

::: danger 常见错误
1. 只有 `depends_on` 短语法，没有 healthcheck，MySQL 还没就绪应用就连库失败。
2. 把密码直接写进 `compose.yaml` 并提交 Git，泄露到仓库历史。
3. 以为 `.env` 里的变量会自动进入容器，结果应用拿到空值。
4. `docker compose up -d` 后立刻访问服务，没有用 `--wait` 等待健康。
5. 修改了 `compose.yaml` 后只执行 `docker compose start`，配置不生效；应执行 `docker compose up -d` 重建。
6. 在 `deploy.resources` 与 `mem_limit` 混用，两者并存时行为依赖版本，建议只保留一种。
:::

## 验证方式

1. `docker compose config --quiet` 校验文件语法（新版也可用 `docker compose config` 查看渲染结果）。
2. `docker compose up -d --wait` 启动并等待健康。
3. `docker compose ps` 显示全部服务为 healthy/running。
4. `docker compose top` 查看容器内进程。
5. `docker compose down` 停止后，命名卷数据默认保留，可用 `docker compose down -v` 显式删除（谨慎）。

## 参考资料

- Compose 规范：https://compose-spec.io/
- Docker Compose 官方文档：https://docs.docker.com/compose/
- 启动顺序控制：https://docs.docker.com/compose/how-tos/startup-order/
- Compose secrets：https://docs.docker.com/compose/how-tos/use-secrets/
