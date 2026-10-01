# 备份工具矩阵：从 mysqldump 到 Velero

**没有「一个工具备份所有东西」。** 备份工具的分化是由数据形态决定的：关系库有事务日志可以做 PITR，对象存储天生版本化，去重工具擅长海量小文件，集群工具要同时管「资源对象」和「卷数据」。本页按数据形态给出选型矩阵、可复制命令与版本状态，让你在任何一个组件上都能立刻动手。

![按数据形态划分的备份工具矩阵](../assets/toolchain-map.svg)

## 1. 选型总览

| 数据形态 | 逻辑备份 | 物理 / 在线备份 | 持续日志（PITR） | 版本状态（2026-10 核对） |
| --- | --- | --- | --- | --- |
| MySQL | `mysqldump`、MySQL Shell `util.dumpInstance()` | Percona XtraBackup | binlog | XtraBackup **8.4.0-7**（2026-09-17） |
| PostgreSQL | `pg_dump` / `pg_dumpall` | `pg_basebackup`、**pgBackRest** | WAL | pgBackRest **2.59.2**（2026-09-27） |
| Redis | `redis-cli --rdb`、`BGSAVE` | RDB 文件复制、AOF | AOF | 跟随 Redis 8.x |
| MongoDB | `mongodump` / `mongorestore` | 文件系统/卷快照 | oplog | 跟随 MongoDB 版本 |
| 文件 / 对象 | `tar` / `rclone` | **restic**、**borg** | — | restic **0.19.1**（2026-07-05）；borg **1.4.5**（2026-07-19） |
| Kubernetes | `kubectl get -o yaml`（不完整） | **Velero** + CSI 快照 | — | Velero **v1.18.3**（2026-09-21） |
| etcd | `etcdctl snapshot save` | — | — | 跟随 etcd 版本 |

:::danger 版本对齐是这类工具的第一号事故源
1. **Percona XtraBackup 8.4 明确不支持 MySQL 8.0 与 9.x 服务端**（官方 Quickstart 写明「does not support backups on MySQL 8.0 or 9.x servers」）。工具大版本必须与服务端大版本对齐，装错版本往往在恢复时才发现，而不是备份时。
2. **MySQL 8.4 移除了 `mysqlpump`**（8.0.34 弃用、8.4.0 移除，连带 `lz4_decompress` / `zlib_decompress` 一起删除）。照抄旧教程会直接报「command not found」。替代品是 `mysqldump` 或 MySQL Shell 的 dump 工具。
3. **pgBackRest 支持 PostgreSQL 18 主线，并对 19 beta 提供支持**；从旧版本升级前先读发布说明的兼容性段落。
:::

## 2. MySQL：逻辑与物理两条路

### 2.1 逻辑备份 `mysqldump`

```shell
# 单库，一致性快照（不锁表），记录 binlog 坐标以便 PITR 对齐
mysqldump --single-transaction --quick --routines --triggers \
          --source-data=2 \
          -h 127.0.0.1 -u backup_user -p blog \
  | zstd -3 > blog_$(date -u +%Y%m%dT%H%M%SZ).sql.zst

# 恢复：先建库，再灌入
mysql -h 127.0.0.1 -u root -p -e "CREATE DATABASE IF NOT EXISTS blog DEFAULT CHARSET utf8mb4;"
zstd -d -c blog_20261001T030000Z.sql.zst | mysql -h 127.0.0.1 -u root -p blog
```

| 参数 | 作用 | 少写了会怎样 |
| --- | --- | --- |
| `--single-transaction` | InnoDB 下用一致性事务快照导出，不锁表 | 备份期间表被锁，业务写入被阻塞 |
| `--quick` | 逐行取出而不全量缓存到内存 | 大表可能把服务器内存打爆 |
| `--routines` / `--triggers` / `--events` | 一并导出存储过程、触发器、事件 | 恢复后逻辑缺失，服务行为改变 |
| `--source-data=2` | 以注释形式写入 binlog 坐标 | 无法与日志归档对齐，PITR 做不了 |
| `--set-gtid-purged=OFF` | 不写 GTID 相关语句 | 在开 GTID 的实例上恢复会报冲突 |

:::warning `mysqldump` 不适合大库
单线程逐行生成 SQL，几百 GB 的库可能要跑十几个小时，且恢复需要重建索引，时间更长。大库应当走物理备份（XtraBackup），把 PITR 交给 binlog 归档。详见 [恢复与演练](../Recovery/index.md) 的 PITR 一节。
:::

### 2.2 物理热备 `XtraBackup`

```shell
# 全量：备份期间不阻塞写入
xtrabackup --backup --target-dir=/backup/mysql/full_$(date -u +%Y%m%d) \
           --user=backup_user --password="${DB_PASS}"

# prepare：把 redo 应用到备份上，使其成为一致状态（恢复前必须做）
xtrabackup --prepare --target-dir=/backup/mysql/full_20261001

# 增量：基于上一次全量
xtrabackup --backup --target-dir=/backup/mysql/incr_20261002 \
           --incremental-basedir=/backup/mysql/full_20261001

# 校验产物：确认存在 xtrabackup_checkpoints，且状态为 prepared
cat /backup/mysql/full_20261001/xtrabackup_checkpoints
# 期望：backup_type = full-prepared（prepare 之后）
```

:::danger 忘记 `--prepare` 是最常见的「备份不可用」
XtraBackup 的原始产物是**不一致**的（备份过程数据库仍在写）。只有执行 `--prepare`（把 redo 日志应用上去）之后，这份备份才是可用状态。**把 `--prepare` 写进备份脚本的最后一个步骤，而不是留到恢复时才想起来。**
:::

## 3. PostgreSQL：`pg_dump` 与 pgBackRest

### 3.1 逻辑备份

```shell
# 自定义格式（-Fc）：支持并行恢复、可选择性恢复单表
pg_dump -Fc -h 127.0.0.1 -U backup_user -d blog \
  -f blog_$(date -u +%Y%m%dT%H%M%SZ).dump

# 恢复（-j 并行，需自定义格式）
pg_restore -j 4 -h 127.0.0.1 -U postgres -d blog_new blog_20261001T030000Z.dump
```

### 3.2 企业级方案 pgBackRest

```ini [pgbackrest.conf]
[global]
repo1-path=/var/lib/pgbackrest
repo1-retention-full=2          # 保留 2 次全量
repo1-retention-diff=7          # 差异保留 7 份
repo1-cipher-type=aes-256-cbc   # 仓库加密
repo1-cipher-pass=<从 vault 注入，不写明文>
compress-type=zst
process-max=4
log-level-console=info

[blog]
pg1-path=/var/lib/postgresql/18/main
```

```shell
# 初始化仓库与 stanza（首次）
pgbackrest --stanza=blog stanza-create

# 全量备份
pgbackrest --stanza=blog --type=full backup
# 差异备份
pgbackrest --stanza=blog --type=diff backup

# 一致性校验（重要：这是「零未验证备份」原则的落地）
pgbackrest --stanza=blog check
# 期望：输出 "check command end: completed successfully" 之类，无 error 行

# 查看备份清单与依赖关系
pgbackrest --stanza=blog info --output=json
```

pgBackRest 相较于手写脚本的核心价值在于：**自带 WAL 归档、自带备份链管理与保留策略、自带校验和与 `check` 命令**。如果你的备份脚本里出现了「自己管理增量依赖」，就应当评估是否换成它。

## 4. Redis 与 MongoDB：区分「可重算」与「不可丢」

```shell
# Redis：触发后台快照并等待完成
redis-cli -h 127.0.0.1 BGSAVE
redis-cli -h 127.0.0.1 INFO persistence | grep -E 'rdb_last_bgsave_status|aof_last_write_status'
# 期望：rdb_last_bgsave_status:ok

# 复制 RDB 到备份目录（注意：直接在写 RDB 的目录里拷贝会拿到半截文件）
redis-cli -h 127.0.0.1 CONFIG GET dir
cp "$(redis-cli -h 127.0.0.1 CONFIG GET dir | tail -1)/dump.rdb" \
   /backup/redis/dump_$(date -u +%Y%m%dT%H%M%SZ).rdb

# MongoDB：一致性导出
mongodump --uri="mongodb://backup_user:${DB_PASS}@127.0.0.1:27017/blog" \
          --archive=/backup/mongo/blog_$(date -u +%Y%m%dT%H%M%SZ).archive \
          --gzip

# 恢复
mongorestore --uri="mongodb://127.0.0.1:27017" --archive=/backup/mongo/blog_xxx.archive --gzip
```

:::danger Redis 备份的三个陷阱
1. **对着 `dump.rdb` 直接 `cp`**：`BGSAVE` 会先写临时文件再原子改名，但如果你在改名瞬间拷贝，可能拿到上一份或半截文件。正确做法是先 `CONFIG GET dir` 定位，再在 `rdb_last_bgsave_status:ok` 之后复制。
2. **以为 RDB 就够**：RDB 是时间点快照，两次快照之间的写全会丢。若 RPO 要求到秒级，必须开启 AOF（`appendonly yes`）并归档 AOF 文件。
3. **把缓存和真实数据混在一个实例**：如 [体系概述](../Overview/index.md) 所说，点赞计数这类「不可丢」的数据必须单独规划持久化，不能和可重算的缓存共享同一个快照策略。
:::

Redis 持久化的原理与参数细节见 [Redis 持久化](../../../DB/NoRelational/Redis/Persistence/index.md)。

## 5. 文件与对象：restic / borg

文件级备份的核心诉求是**去重 + 加密 + 增量**，三者同时满足的成熟工具就是 restic 与 borg。

```shell
# restic：初始化仓库（仓库可以是本地目录、SFTP、S3 等）
export RESTIC_REPOSITORY=s3:s3.amazonaws.com/my-backup-bucket/blog
export RESTIC_PASSWORD_FILE=/etc/restic/password      # 密码放文件，不要进命令行
restic init

# 备份（自动去重、自动增量、客户端加密）
restic backup /data/uploads --tag daily --exclude-caches

# 校验仓库结构（不是校验数据内容，但能发现大部分损坏）
restic check
# 期望：no errors were found

# 深度校验（重新读取并校验所有数据的哈希，耗时长，建议每周一次）
restic check --read-data-subset=5%

# 按 GFS 保留（先看再删：--dry-run）
restic forget --keep-daily 7 --keep-weekly 8 --keep-monthly 12 --dry-run
restic forget --keep-daily 7 --keep-weekly 8 --keep-monthly 12 --prune
```

```shell
# borg：等效流程
export BORG_REPO=ssh://backup@nas/./repo/blog
export BORG_PASSPHRASE_FILE=/etc/borg/passphrase
borg init --encryption=repokey-blake2
borg create --stats --compression zstd,3 "::daily-{utcnow}" /data/uploads
borg check
borg prune --keep-daily 7 --keep-weekly 8 --keep-monthly 12 --list
```

| 对比项 | restic | borg |
| --- | --- | --- |
| 语言 / 依赖 | Go 单二进制，零依赖 | Python + C 扩展，依赖较多 |
| 仓库存储后端 | 原生支持 S3 / Azure / GCS / B2 / SFTP / rclone | 本地、SSH、rclone 桥接 |
| 当前稳定版（2026-10） | 0.19.1（2026-07-05） | 1.4.5（2026-07-19，含 CVE-2026-62268 修复） |
| 注意 | 0.19.0 起**源码构建要求 Go 1.25+** | **2.0 仍在 beta，不要用于生产** |

:::tip 选哪个
两者都能满足 3-2-1-1-0 的工程要求。选择依据通常是团队环境：**要「一个二进制到处跑、直连对象存储」选 restic；已有 Python 运维栈、预算敏感（borg 压缩比略优）选 borg。** 不要为了选型纠结太久——先有备份、再有更好的备份。
:::

## 6. Kubernetes：Velero 与 etcd 快照

Kubernetes 的备份有特殊性：**资源对象（YAML）与卷数据（PV）是两套东西**，而且「代码在 Git 里」不等于「集群可重建」——运行期生成的 Secret、证书、CR 状态都不在 Git 里。

```shell
# 安装 Velero CLI 后，配置对象存储与卷快照
velero install \
  --provider aws \
  --bucket blog-velero-backups \
  --backup-location-config region=ap-east-1 \
  --snapshot-location-config region=ap-east-1 \
  --use-node-agent                  # 文件级备份卷数据（无 CSI 快照时使用）

# 按命名空间备份
velero backup create blog-daily --include-namespaces blog --wait

# 查看备份状态与错误
velero backup describe blog-daily --details
# 期望：Phase: Completed，Errors: 0

# 恢复（可恢复到同集群或其他集群）
velero restore create --from-backup blog-daily --wait
```

```shell
# etcd 快照：集群自身状态的兜底（与 Velero 互补）
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd/snap_$(date -u +%Y%m%dT%H%M%SZ).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# 校验快照完整性
etcdctl snapshot status /backup/etcd/snap_xxx.db --write-out=table
# 期望：输出 db 大小、revision、total keys 等，无报错
```

:::warning Velero 的版本与治理变更
Velero 已加入 **CNCF Sandbox**，仓库从 `vmware-tanzu/velero` 迁移到 **`velero-io/velero`**（旧地址 301 跳转）。拉取插件与查文档时注意地址变化。当前主线为 **v1.18.3**（2026-09-21），v1.17 仍在支持窗口，v1.16 及更早已停止支持。
:::

## 7. 对象存储：把「不可变」变成配置

第 4 位（1 份离线/不可变）最便宜的实现方式就是对象存储的能力：

| 能力 | 含义 | 用途 |
| --- | --- | --- |
| **版本控制（Versioning）** | 覆盖不删除旧版本 | 误删可回滚，但**不防**「删除整个桶」 |
| **对象锁 / 保留策略（Object Lock）** | 在保留期内任何人都删不掉对象 | 真正防勒索与误删 |
| **生命周期（Lifecycle）** | 到期转归档层或删除 | 控制成本 |
| **跨区域复制（CRR）** | 自动复制到另一地域 | 满足「异地」一位 |

```shell
# 用 AWS CLI 演示对象锁的最小配置（其他云厂商能力等价、参数名不同）
aws s3api put-object-lock-configuration \
  --bucket blog-backups \
  --object-lock-configuration \
  'ObjectLockEnabled=Enabled,Rule={DefaultRetention={Mode=COMPLIANCE,Days=30}}'
# 期望：无输出即成功；此后 30 天内该桶内对象无法被删除（含 root 账号）
```

:::danger COMPLIANCE 模式是真锁
对象锁分为 `GOVERNANCE`（特权账号可绕过）与 `COMPLIANCE`（**任何账号、任何权限都删不掉，直到过期**）。用 COMPLIANCE 前必须想清楚：保留期内你的桶容量只增不减，配错周期会导致成本失控。建议先在非生产桶上演练一次。
:::

## 8. 验证方式

工具是否「装对了、跑得通」，用下面的最小检查一次性覆盖：

```shell
# ① 工具版本与数据库大版本是否对齐（以 MySQL 为例）
xtrabackup --version
mysql --version
# 期望：XtraBackup 8.4.x 搭配 MySQL 8.4.x（不要用 8.4 工具备份 8.0/9.x 服务端）

# ② mysqldump 关键参数是否生效（在测试库上跑一次并检查输出）
mysqldump --single-transaction --source-data=2 -h 127.0.0.1 -u root -p blog | grep -m1 'CHANGE REPLICATION SOURCE TO'
# 期望：输出 binlog 坐标注释行；若为空，说明 --source-data 没生效

# ③ restic 仓库是否健康
restic check
# 期望：no errors were found

# ④ pgBackRest 的备份链是否完整
pgbackrest --stanza=blog info
# 期望：列出 full/diff 备份与 WAL 归档区间，无 "missing" 提示

# ⑤ Velero 备份是否零错误
velero backup get
# 期望：STATUS 列全部为 Completed
```

## 参考资料

- Percona XtraBackup 8.4 文档与 Quickstart（含「不支持 MySQL 8.0 / 9.x 服务端」的支持范围说明）：https://docs.percona.com/percona-xtrabackup/8.4/
- MySQL 8.4 官方 · 相较 8.0 的移除项（含 `mysqlpump` 移除）：https://dev.mysql.com/doc/refman/8.4/en/mysql-nutshell.html
- pgBackRest 官网与用户指南：https://pgbackrest.org/ ｜ https://pgbackrest.org/user-guide.html
- restic 官方文档：https://restic.readthedocs.io/en/stable/
- BorgBackup 官方文档与发布系列：https://borgbackup.readthedocs.io/en/stable/ ｜ https://www.borgbackup.org/releases/
- Velero 官方文档（版本兼容矩阵与支持策略）：https://velero.io/docs/
- Redis 持久化官方文档：https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
- MongoDB 备份方法（`mongodump` / 快照）：https://www.mongodb.com/docs/manual/core/backups/
- 本专题其余章节：[恢复与演练](../Recovery/index.md) ｜ [容灾架构](../DisasterRecovery/index.md) ｜ [实战](../Practice/index.md)
