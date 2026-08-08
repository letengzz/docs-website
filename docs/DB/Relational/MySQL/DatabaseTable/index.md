# 库表操作（DDL）

DDL（Data Definition Language）用于定义和管理数据库、表的结构。

## 数据库操作

```sql
-- 创建数据库（指定字符集，避免默认 latin1）
CREATE DATABASE IF NOT EXISTS shop
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

-- 查看数据库
SHOW DATABASES;

-- 切换数据库
USE shop;

-- 查看当前库
SELECT DATABASE();

-- 修改数据库字符集
ALTER DATABASE shop CHARACTER SET utf8mb4;

-- 删除数据库（不可恢复，慎用）
DROP DATABASE IF EXISTS shop;
```

::: danger 注意
1. 库名、表名在 Linux 下区分大小写，Windows 下不区分，建议统一小写。
2. `DROP DATABASE` 会删除库内所有数据，生产环境必须先备份。
:::

## 创建表

```sql
CREATE TABLE IF NOT EXISTS user (
  id         BIGINT UNSIGNED AUTO_INCREMENT COMMENT '主键',
  username   VARCHAR(50)  NOT NULL COMMENT '用户名',
  email      VARCHAR(100) NOT NULL COMMENT '邮箱',
  age        TINYINT UNSIGNED DEFAULT 0 COMMENT '年龄',
  status     TINYINT      NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
             ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_username (username),
  KEY idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';
```

查看表结构：

```sql
SHOW TABLES;
DESC user;
SHOW CREATE TABLE user\G
```

## 修改表

```sql
-- 新增列
ALTER TABLE user ADD COLUMN phone VARCHAR(20) COMMENT '手机号';

-- 修改列类型
ALTER TABLE user MODIFY COLUMN age SMALLINT UNSIGNED DEFAULT 0 COMMENT '年龄';

-- 修改列名和类型
ALTER TABLE user CHANGE COLUMN age user_age INT COMMENT '年龄';

-- 删除列
ALTER TABLE user DROP COLUMN phone;

-- 重命名表
ALTER TABLE user RENAME TO users;

-- 修改表注释
ALTER TABLE users COMMENT = '用户表';
```

::: danger 注意
1. 大表执行 `ALTER TABLE` 会锁表，生产环境建议在低峰期执行，或使用 `gh-ost`、`pt-osc` 等在线变更工具。
2. `CHANGE` 需要写完整的新列定义，容易漏掉属性，能不用就不用。
:::

## 约束

| 约束 | 作用 |
| --- | --- |
| `PRIMARY KEY` | 主键，唯一且非空 |
| `NOT NULL` | 不允许为空 |
| `UNIQUE` | 值唯一 |
| `DEFAULT` | 默认值 |
| `CHECK` | 检查约束（MySQL 8.0.16+ 生效） |
| `FOREIGN KEY` | 外键（InnoDB 支持） |
| `AUTO_INCREMENT` | 自增，通常配合主键 |

CHECK 约束示例：

```sql
CREATE TABLE order_item (
  id  BIGINT PRIMARY KEY AUTO_INCREMENT,
  qty INT NOT NULL CHECK (qty > 0)
);
```

外键示例：

```sql
CREATE TABLE orders (
  id      BIGINT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES user (id)
);
```

::: tip
互联网业务通常由应用层保证数据关联，**不建议滥用数据库外键**：外键会带来额外的锁和性能开销，也增加分库分表的难度。
:::

## 删除表与清空表

```sql
-- 删除表（不可恢复）
DROP TABLE IF EXISTS user;

-- 清空表数据并重置自增（不可回滚）
TRUNCATE TABLE user;

-- 清空表数据（可回滚，但慢）
DELETE FROM user;
```

| 操作 | 可回滚 | 重置自增 | 速度 |
| --- | --- | --- | --- |
| `DELETE` | 可以 | 否 | 慢 |
| `TRUNCATE` | 不可以 | 是 | 快 |

## 验证方式

创建表后执行：

```sql
DESC user;
SHOW CREATE TABLE user\G
```

确认列名、类型、默认值、索引都与设计一致。
