# MySQL 安装与配置

## 版本选择

- 生产环境推荐 **MySQL 8.4 LTS**（支持到 2031 年）。
- 新项目也可以直接使用 **MySQL 9.7 LTS**（2026 年 4 月发布）。
- 8.0 已停止维护，不要新装；存量 8.0 尽快升级。

## Windows 安装

1. 打开 [MySQL 下载页](https://dev.mysql.com/downloads/installer/)，下载 MySQL Installer。
2. 安装类型选择 **Server only**（只装服务端）或 Developer Default。
3. 配置要点：
   - 端口保持 `3306`
   - 设置 root 密码
   - 服务名建议使用 `MySQL84`（便于多版本共存）
4. 安装完成后验证：

```shell
mysql --version
mysql -u root -p
```

登录成功后执行 `SELECT VERSION();` 应输出 `8.4.x` 或 `9.7.x`。

## macOS 安装（Homebrew）

```shell
brew install mysql@8.4
brew services start mysql@8.4
mysql --version
```

Homebrew 安装后 root 默认无密码，建议立即设置：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '新密码';
```

## Linux 安装（Ubuntu / Debian）

```shell
sudo apt update
sudo apt install mysql-server
sudo systemctl status mysql
```

Debian 系默认 root 使用 `auth_socket` 认证，需要先 `sudo mysql` 进入，再改成密码认证：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '新密码';
```

## 初始化安全设置

安装后执行安全初始化向导：

```shell
mysql_secure_installation
```

建议选项：

- 设置密码强度校验
- 删除匿名用户
- 禁止 root 远程登录
- 删除 test 数据库

## 配置文件（my.cnf / my.ini）

Linux 常见位置：`/etc/mysql/mysql.conf.d/mysqld.cnf`；Windows 为安装目录下的 `my.ini`。

常用配置：

```ini [my.cnf]
[mysqld]
port = 3306
character-set-server = utf8mb4
collation-server = utf8mb4_0900_ai_ci
max_connections = 500
innodb_buffer_pool_size = 1G
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 1
```

::: danger 注意
1. 修改配置后必须重启服务：`sudo systemctl restart mysql`。
2. 字符集务必使用 `utf8mb4`；`utf8` 是 `utf8mb3` 的别名，已弃用，无法完整支持 emoji 等字符。
3. `innodb_buffer_pool_size` 通常设为物理内存的 50%~70%，但先确认机器规格。
:::

## 创建业务账号（生产规范）

生产环境不要用 root 跑业务，创建专用账号并只授权需要的库：

```sql
CREATE USER 'shop_app'@'%' IDENTIFIED BY '强密码';
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'shop_app'@'%';
FLUSH PRIVILEGES;
```

## 验证清单

```shell
mysql --version
mysql -u root -p -e "SELECT VERSION(); SHOW VARIABLES LIKE 'character_set_server';"
```

预期结果：

```text
VERSION()              8.4.9
character_set_server   utf8mb4
```

看到版本号和 `utf8mb4` 即表示安装配置成功。
