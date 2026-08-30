# Navicat：多库统一管理

Navicat Premium 是商业级**多数据库管理客户端**：一套界面管理 MySQL、PostgreSQL、SQL Server、Oracle、MariaDB、MongoDB、Redis 等数据源，以「连接树 + 对象面板 + 查询编辑器 + 传输同步」组织全部日常操作。本页基于 **Navicat Premium 17.3** 编写。

## 产品定位

![Navicat 工作流](./../assets/navicat-flow.svg)

Navicat 的核心优势不是某一个功能，而是**一致性**：无论连哪种数据库，新建连接、建表、查询、导入导出的交互完全一致，学习一次即可覆盖多个数据库。

## 安装与授权

### 下载安装

1. 访问官网下载页，选择对应系统安装包（Windows/macOS/Linux）。
2. 安装完成后打开，进入「注册」或「登录」页。
3. 输入购买的产品密钥或登录订阅账号，激活 Premium。

```shell
# Ubuntu（Debian 系）安装示例
sudo apt update
sudo apt install -y ./navicat17-premium-en.AppImage
chmod +x navicat17-premium-en.AppImage
./navicat17-premium-en.AppImage
```

### 版本选择

| 版本 | 适用 |
| --- | --- |
| Navicat Premium | 全功能，推荐 |
| Navicat for MySQL / PostgreSQL 等单库版 | 只需一种库时更省钱 |
| Navicat 订阅版 | 按年付费，含更新与支持 |

## 新建连接

### 以 MySQL 为例

1. 顶部工具栏点击「连接」→ 选择 MySQL。
2. 填写参数：

| 参数 | 示例 | 说明 |
| --- | --- | --- |
| 连接名 | 本地开发库 | 显示在左侧连接树的名字 |
| 主机 | 127.0.0.1 | IP 或域名 |
| 端口 | 3306 | 默认端口 |
| 用户名 | root / dev | 最小权限账号优先 |
| 密码 | 输入后勾选保存 | 存储在客户端加密库 |
| 数据库 | 初次可留空 | 留空则连接后浏览全部库 |

3. 点击「测试连接」，弹出成功提示后保存。

```text
连接成功后可看到：
连接树 → 数据库 → 表 / 视图 / 函数 / 存储过程 / 事件
```

### 其他数据源

- **PostgreSQL**：默认端口 5432，注意「数据库」必填（默认 postgres）。
- **SQL Server**：可选 Windows 认证或 SQL Server 认证。
- **MongoDB**：连接串形式，如 `mongodb://user:pass@host:27017/admin`。
- **Redis**：主机 + 端口 + 密码，支持 Sentinel/Cluster。

## 常用操作

### 表结构与数据

1. 双击表名打开表设计器：增删字段、改类型、建索引、设置默认值。
2. 右键表 →「打开表」：数据网格，可直接编辑行。
3. 右键表 →「复制表」/「复制表结构」：快速建同构表。
4. 右键表 →「查看 DDL」：一键复制建表语句。

```sql
-- 在 Navicat 查询编辑器执行
SHOW CREATE TABLE user_tbl;
SELECT COUNT(*) FROM user_tbl;
```

### 查询编辑器

1. 「查询」→「新建查询」，在编辑器中写 SQL。
2. 选中部分语句只执行选中内容（Ctrl+Enter 执行）。
3. 顶部「解释」按钮查看执行计划（EXPLAIN）。
4. 查询结果支持排序、过滤、导出为 CSV/Excel。

```sql
EXPLAIN SELECT u.id, u.name, o.amount
FROM user_tbl u
JOIN order_tbl o ON o.user_id = u.id
WHERE u.status = 1
ORDER BY o.amount DESC;
```

### 导入导出

| 操作 | 入口 | 支持格式 |
| --- | --- | --- |
| 导出 | 右键库/表 → 导出向导 | SQL、CSV、Excel、JSON、XML |
| 导入 | 右键库/表 → 导入向导 | CSV、Excel、JSON、XML、SQL |
| 备份 | 右键库 → 备份 → 新建备份 | 自定义备份格式（含结构+数据） |
| 恢复 | 右键库 → 备份/还原 → 还原备份 | 备份文件 |

```text
导出向导要点：
1. 选择导出范围（仅结构 / 结构+数据 / 仅数据）
2. 字段映射与类型
3. 编码选择 UTF-8，避免中文乱码
```

### 数据同步与结构同步

「工具」→「数据同步」：选择源库与目标库，按表对比，勾选差异记录执行：

```text
适用场景：测试库刷新数据、从生产同步部分表到预发
注意：同步前先备份目标库，数据同步是「覆盖性操作」
```

## 计划任务（自动化）

「自动化」→「新建计划任务」：把备份、同步、导入导出做成可重复执行的任务，支持定时：

```text
示例：每天 02:00 备份生产库 → 每周日把生产数据同步到测试库
```

计划任务对 DBA 很有价值：不需要写 CronJob，客户端内即可编排。

## 连接安全设置

1. **密码保存**：勾选「保存密码」，密码存入客户端加密存储。
2. **SSH 隧道**：高级设置中可走跳板机。
3. **SSL**：云数据库（RDS/Cloud SQL）开启 SSL 时，在 SSL 页选择 CA 证书。
4. **HTTP 隧道**：仅当网络只开放 HTTP 端口时使用，生产少用。

## 易错点与最佳实践

::: danger 常见问题
1. **误把生产当测试**：连接名写清楚（如「生产-订单库-只读」），用颜色区分环境。
2. **直接编辑线上数据**：先 `SELECT` 确认条件，再用事务包裹并限制影响行数。
3. **导入时编码选错**：CSV 乱码大多因为没选 UTF-8。先导入 10 行预览。
4. **备份只导数据不导结构**：恢复时缺表。备份时勾选「结构+数据」。
5. **多个同事共享一个管理员账号**：无法审计。每个账号最小权限，操作留痕。
:::

::: tip 最佳实践
- 每个环境单独建连接并分组（开发/测试/生产），生产连接用**只读账号**日常查询。
- 大批量更新拆小批：`UPDATE ... LIMIT 1000` 循环执行，避免长事务锁表。
- 定期用「表维护/分析」更新统计信息，配合查询执行计划优化。
- 导出敏感数据时脱敏（姓名、手机号、身份证打码），文件加密存放。
:::

## 实战：从 Excel 导入并查询

```text
1. 新建连接 → 测试连接 → 保存
2. 新建数据库 demo_db，字符集 utf8mb4
3. 右键 demo_db → 导入向导 → 选择 Excel 文件
4. 勾选「新建表」→ 字段映射确认类型 → 下一步执行
5. 打开导入的表，确认行数与 Excel 一致
6. 查询验证：
```

```sql
SELECT COUNT(*) AS total FROM imported_tbl;
SELECT * FROM imported_tbl LIMIT 20;
```

预期：`total` 与 Excel 数据行数一致，中文无乱码。

## 验证方式

1. 新建连接测试成功，连接树可见库表。
2. 查询编辑器执行 `SELECT 1;` 返回 1。
3. 对一张测试表完成「导出 CSV → 修改少量数据 → 导入」闭环，行数不丢失。
4. 执行一次备份与还原演练，确认备份文件可恢复。

## 参考资料

- Navicat 官方文档：<https://www.navicat.com.cn/manual/>
- Navicat 17 新特性：<https://www.navicat.com.cn/products/navicat-premium-release-note>
- Navicat 导入导出指南：<https://www.navicat.com.cn/company/resources>
