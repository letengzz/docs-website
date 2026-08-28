# 安装与连接

MongoDB 提供社区版（Community Server）与服务器端驱动工具。这一篇覆盖 Linux/Docker/Windows 安装、mongosh 连接与连接串。

## 安装 MongoDB Community Server

### Ubuntu（官方 apt 源）

```shell
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt update
sudo apt install -y mongodb-org
```

### Docker（推荐快速体验）

```shell
docker run -d --name mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -v mongo-data:/data/db \
  mongo:8.0
```

### macOS / Windows

```shell
# macOS
brew tap mongodb/brew
brew install mongodb-community@8.0

# Windows：下载 MSI 安装包
# https://www.mongodb.com/try/download/community
```

## 启动服务

```shell
# Linux（systemd）
sudo systemctl start mongod
sudo systemctl enable mongod

# Docker 方式
docker start mongo
```

## 安装 mongosh

```shell
sudo apt install -y mongodb-mongosh
# 或 Docker 内直接使用：docker exec -it mongo mongosh
```

## 连接数据库

```shell
mongosh
mongosh "mongodb://localhost:27017"
mongosh "mongodb://admin:secret@localhost:27017/?authSource=admin"
```

连接成功提示符：

```text
test>
```

## 连接串组成

```text
mongodb://[用户名:密码@]主机:端口[/数据库][?参数]
```

常用参数：

| 参数 | 作用 |
| --- | --- |
| `authSource` | 认证库（通常 admin） |
| `replicaSet` | 副本集名称 |
| `ssl=true` | 开启 TLS |
| `w=majority` | 写关注（多数派确认） |

## 图形工具

- MongoDB Compass：官方图形客户端
- VS Code MongoDB 插件
- IDEA Database 面板（连接串方式）

## 易错点

::: danger 常见错误
1. 连接被拒（Connection refused）：服务未启动或端口被防火墙挡，`ss -lntp | grep 27017` 排查。
2. 认证失败：用户名密码 + `authSource` 写错，管理员账号认证库是 admin。
3. Docker 不挂卷：容器删除后数据丢失，必须 `-v mongo-data:/data/db`。
4. 首次启动报 dbpath 权限：`/data/db` 目录属主应为 mongod 用户，或指定 `--dbpath`。
5. 安装 6.0+ 后找不到 mongod 命令：确认安装了 `mongodb-org-server` 且 PATH 正确。
6. 生产裸奔无认证：必须开启 `--auth` 或配置文件 `security.authorization: enabled`。
:::

## 验证方式

1. `mongosh --eval "db.runCommand({ ping: 1 })"` 返回 `ok: 1`。
2. `mongosh` 中执行 `db.version()` 查看版本。
3. Docker 方式：`docker exec -it mongo mongosh --eval "db.runCommand({ ping: 1 })"`。

## 参考资料

- 安装指南：https://www.mongodb.com/docs/manual/installation/
- 连接串说明：https://www.mongodb.com/docs/manual/reference/connection-string/
- mongosh：https://www.mongodb.com/docs/mongodb-shell/
