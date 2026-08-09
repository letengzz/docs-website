# Docker 常见问题与最佳实践

本节汇总生产环境中最高频的 Docker 问题，并给出一份可以直接对照的自查清单。单条报错的完整处理可继续参考本站 [Docker 常见错误](../Errors/index.md)。

## 生产环境自查清单

发布前逐项核对：

- [ ] 基础镜像固定版本或 digest，不用 `latest`
- [ ] 使用多阶段构建，镜像只含运行所需文件
- [ ] 容器内以非 root 用户运行
- [ ] 配置了 `HEALTHCHECK` 与 `restart: unless-stopped`
- [ ] 设置了 CPU/内存/pids 限制
- [ ] 数据通过命名卷持久化，数据库容器不丢数据
- [ ] 密码、token 使用 secrets，不写进镜像和环境变量明文
- [ ] 端口只绑定需要暴露的地址（`127.0.0.1` 或公网 IP 按需）
- [ ] 镜像做过漏洞扫描，高危已处理
- [ ] 日志配置了轮转，磁盘不会被打满
- [ ] 构建产物和 `.env` 已被 `.dockerignore` 排除

## 常见问题

### 1. 容器一启动就退出，看不到报错

先看日志和退出码：

```shell
docker ps -a
docker logs <容器名>
docker inspect <容器名> --format '{{.State.ExitCode}} {{.State.Error}}'
```

常见原因：进程前台运行失败（守护型命令导致容器认为无事可做）、端口被占、配置路径错误。

### 2. 退出码 137

通常是被 OOM Killer 杀掉，或者手动 `docker kill`。先查资源限制：

```shell
docker inspect <容器名> --format '{{.HostConfig.Memory}} {{.HostConfig.NanoCpus}}'
dmesg | grep -i oom
```

解决办法：调大 `--memory`，或优化应用内存占用；确认宿主机内存充足。

### 3. Permission denied：无法连接 Docker 守护进程

把用户加入 docker 组（需要重新登录）：

```shell
sudo usermod -aG docker $USER
```

注意：docker 组等同于 root 权限，生产环境更推荐 rootless 模式或使用 sudo。

### 4. 容器内访问宿主机服务

Linux 下把宿主地址映射为 `host.docker.internal`：

```shell
docker run -d --add-host=host.docker.internal:host-gateway myapp
```

容器内访问 `http://host.docker.internal:3306`。Docker Desktop（macOS/Windows）默认已提供该主机名。

### 5. 容器间用 localhost 访问不到

`localhost` 只属于容器自己的网络命名空间。容器互访要用服务名或容器名（同一自定义网络内）：

```shell
docker network create app-net
docker run -d --name api --network app-net myapi
docker run -d --name web --network app-net myweb
```

在 `web` 容器里访问 `http://api:8080`。

### 6. 端口提示 already allocated

```shell
sudo netstat -tlnp | grep 8080
docker ps -a | grep 8080
```

换端口，或先停掉占用该端口的容器/进程。

### 7. 镜像构建缓存总是不生效

检查三点：

1. `.dockerignore` 是否排除了 `node_modules`、`dist` 等大目录；
2. 依赖安装指令是否放在 `COPY . .` 之前；
3. 是否用了 `--no-cache` 或 BuildKit 缓存配置不正确。

### 8. 磁盘被容器日志和镜像占满

先看占用，再安全清理：

```shell
docker system df
docker system prune          # 清理停止的容器、悬空镜像等
docker system prune -a      # 谨慎：清理所有未使用镜像
docker volume prune         # 谨慎：清理未使用卷
```

日志轮转应在 `daemon.json` 全局配置：

```json [daemon.json]
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 9. 容器时间与宿主不一致

```shell
docker run -d -e TZ=Asia/Shanghai myapp
```

部分镜像没有安装 tzdata，需要额外处理；对时区敏感的应用应显式设置 `TZ` 而不是依赖镜像默认值。

### 10. docker compose 修改配置后不生效

`docker compose start` 不会重新读取配置变化，应使用：

```shell
docker compose up -d
```

### 11. 容器一直 Restarting

```shell
docker logs --tail 100 <容器名>
```

通常应用启动崩溃或健康检查失败。`restart: always` 会无限重启，排障时先改成手动启动。

### 12. 拉取镜像超时或 DNS 解析失败

检查网络与镜像源：

```shell
docker info | grep -i "registry mirrors"
docker pull hello-world
```

国内网络可配置 registry mirror 或使用内网镜像仓库；排查时先确认宿主机 DNS 正常。

## 易错点

::: danger 常见错误
1. 数据库容器不挂卷，`docker compose down` 后数据消失。
2. 直接把 `.env` 提交到 Git，密钥进入仓库历史。
3. 生产用 `-p 80:80` 而不是按需绑定地址，服务意外暴露。
4. 所有容器都开 `--privileged` 或挂 docker.sock，安全基线形同虚设。
5. 日志不轮转，一个月后磁盘 100%，服务全线崩溃。
6. 只会在出问题时 `docker system prune -a`，把还在用的镜像也删了。
:::

## 验证方式

1. 对照上面的自查清单逐项确认生产服务。
2. 执行 `docker system df` 确认磁盘占用在预期范围。
3. 随机停掉一个服务容器，确认 `restart` 策略能自动拉起且健康检查通过。
4. 检查 `docker logs` 无新增报错，指标曲线正常。
5. 用 `docker compose config` 校验所有 Compose 文件语法。

## 参考资料

- Docker 官方 FAQ：https://docs.docker.com/engine/faq/
- Docker 日志与日志驱动：https://docs.docker.com/engine/logging/
- Docker 资源限制：https://docs.docker.com/engine/containers/resource_constraints/
- Docker 官方博客：https://www.docker.com/blog/
