# 常见问题与最佳实践

## 连接与账号问题

1. `Access denied for user 'xxx'@'host'`：密码错误，或用户未被授权从该主机连接。

```sql
-- 允许指定主机
CREATE USER 'shop_app'@'10.0.0.%' IDENTIFIED BY '密码';
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'shop_app'@'10.0.0.%';
```

2. 远程连不上：检查 `bind-address`、防火墙/安全组、用户 host 是否包含客户端 IP。
3. 生产环境禁止 root 远程登录，使用最小权限业务账号。

## 中文乱码

乱码绝大多数是**字符集不一致**导致：

```shell
mysql -u root -p --default-character-set=utf8mb4
```

```ini [jdbc url]
jdbc:mysql://localhost:3306/shop?useUnicode=true&characterEncoding=utf8mb4
```

同时保证库、表、连接三层的字符集都是 `utf8mb4`：

```sql
SHOW VARIABLES LIKE 'character_set_server';
SHOW CREATE TABLE user\G
```

## 备份与恢复

```shell
# 备份单库
mysqldump -u root -p --single-transaction shop > shop.sql

# 恢复
mysql -u root -p shop < shop.sql
```

::: danger 注意
1. InnoDB 备份加 `--single-transaction`，在不锁表的前提下拿到一致性快照。
2. 备份要定期演练恢复，不能只备份不验证。
3. 生产环境建议「主从复制 + 定期备份」双保险。
:::

## 死锁

出现 `ERROR 1213` 时的处理：

1. 死锁会自动回滚其中一个事务，业务侧捕获后重试即可。
2. 查看死锁信息：

```sql
SHOW ENGINE INNODB STATUS\G
```

3. 预防：统一加锁顺序、缩短事务、走同一索引。

## 主从复制

主库配置（my.cnf）：

```ini [my.cnf]
[mysqld]
server-id = 1
log-bin = mysql-bin
binlog_format = ROW
```

从库操作（MySQL 8.0.22+ 语法）：

```sql
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='10.0.0.1',
  SOURCE_USER='repl',
  SOURCE_PASSWORD='密码',
  SOURCE_LOG_FILE='mysql-bin.000001',
  SOURCE_LOG_POS=1234;

START REPLICA;
SHOW REPLICA STATUS\G
```

从库建议开启只读：

```ini [my.cnf]
read_only = 1
```

## 高频踩坑清单

1. 不用 MyISAM，坚持 InnoDB。
2. 不用 `utf8`（它是 utf8mb3），统一 `utf8mb4`。
3. `UPDATE` / `DELETE` 不带 `WHERE`。
4. 滥用 `SELECT *`。
5. 隐式类型转换导致索引失效。
6. 事务里做慢查询或远程调用。
7. 金额用 `FLOAT`，应该用 `DECIMAL`。
8. 大表直接 `ALTER TABLE`，应该用在线变更工具。

## 监控与健康检查

```sql
SHOW PROCESSLIST;                       -- 当前连接与慢查询
SHOW ENGINE INNODB STATUS\G;            -- 锁、死锁、事务状态
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Slow_queries';
```

```shell
mysqladmin -u root -p status
```

## 相关链接

- MySQL 官方文档：https://dev.mysql.com/doc/
- MySQL 8.4 参考手册：https://dev.mysql.com/doc/refman/8.4/en/
- 备份工具文档：https://dev.mysql.com/doc/refman/8.4/en/mysqldump.html

## 相关专题

- [PostgreSQL](../PostgreSQL/index.md)：功能对比与迁移差异
- [MongoDB 文档数据库](../../../NoRelational/MongoDB/index.md)
- [SQL 优化](../../SQLOptimization/index.md)：慢查询治理与索引设计
