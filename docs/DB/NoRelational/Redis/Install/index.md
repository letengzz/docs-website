# Redis 安装与配置

## 版本选择

- 学习与生产新项目推荐 **Redis 8.x**。
- 存量项目继续使用 7.x 时，先确认官方维护周期和升级计划。

## Docker 安装（最快速）

```shell
docker run -d --name redis \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:8

# 进入容器执行命令
docker exec -it redis redis-cli ping
```

预期输出：`PONG`。

## Linux 安装（Ubuntu / Debian）

```shell
sudo apt update
sudo apt install redis-server

sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl status redis-server
```

::: danger 注意
发行版自带的 Redis 版本可能较旧，如需 8.x 请使用官方 PPA、源码编译或 Docker。
:::

## macOS 安装（Homebrew）

```shell
brew install redis
brew services start redis
redis-cli ping
```

## Windows 安装

Redis 官方**不提供 Windows 版本**，推荐两种方式：

- WSL2 中安装 Linux 版。
- 使用 Docker Desktop 运行 `redis:8` 镜像。

## 配置文件 redis.conf

关键配置项：

```txt [redis.conf]
bind 127.0.0.1
protected-mode yes
port 6379

# 密码（生产必须设置）
requirepass your-strong-password

# 持久化
appendonly yes
appendfsync everysec

# 内存上限与淘汰策略
maxmemory 512mb
maxmemory-policy allkeys-lru
```

启动时指定配置文件：

```shell
redis-server /etc/redis/redis.conf
```

## 连接与验证

```shell
redis-cli -h 127.0.0.1 -p 6379
```

设置了密码时：

```shell
redis-cli -a 'your-strong-password'
```

或者进入交互模式后执行：

```shell
127.0.0.1:6379> AUTH your-strong-password
127.0.0.1:6379> PING
PONG
127.0.0.1:6379> SET name zhangsan
OK
127.0.0.1:6379> GET name
"zhangsan"
```

::: danger 注意
1. `-a` 明文传密码会出现在进程列表和历史记录中，生产环境推荐用 `REDISCLI_AUTH` 环境变量或交互式 `AUTH`。
2. 生产环境必须设置 `requirepass`，禁止默认无密码暴露公网。
3. 默认只监听 `127.0.0.1`；需要远程访问时再改 `bind` 并配合防火墙。
:::

## 生产安全建议

```txt [redis.conf]
# 只监听内网
bind 10.0.0.5

# 禁止高危命令（重命名为空即禁用）
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
```

## 验证清单

```shell
redis-cli ping          # PONG
redis-cli info server   # 查看版本、运行时间
redis-cli config get maxmemory
```

确认 `PING` 返回 `PONG`、版本为 8.x、密码认证生效，即安装配置成功。
