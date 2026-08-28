# 备份与恢复

副本集保证**可用性**，但不等于**备份**：误删、逻辑损坏会同步复制。生产必须建立定期备份与恢复演练。常用工具：`mongodump` / `mongorestore`。

## mongodump 备份

```shell
# 全库备份（逻辑备份）
mongodump --uri "mongodb://admin:secret@localhost:27017" \
  --out /backup/$(date +%F)

# 单库
mongodump --db mydb --out /backup/mydb

# 单集合
mongodump --db mydb --collection users --out /backup/users
```

生成 `*.bson` 与 `*.metadata.json` 文件。

## mongorestore 恢复

```shell
# 恢复到新库/原库
mongorestore --uri "mongodb://admin:secret@localhost:27017" \
  /backup/2026-08-28

# 只恢复某个集合
mongorestore --nsInclude "mydb.users" /backup/2026-08-28
```

## mongosh 导出/导入

```shell
# JSON 导出
mongoexport --db mydb --collection users --out users.json

# JSON 导入
mongoimport --db mydb --collection users --file users.json
```

适合数据迁移与批量导入。

## 文件快照备份

对数据目录做文件系统快照（LVM、云盘快照）：

```text
1. 数据目录默认 /var/lib/mongodb
2. 使用 fsyncLock 冻结写入后快照，再 fsyncUnlock
```

快照恢复更快，但要求存储层支持一致性快照。

## 备份策略建议

1. **频率**：每天全量 + 高频 oplog 增量（或按业务 RPO 调整）。
2. **保留**：本地 N 天 + 异地/对象存储长期保留。
3. **验证**：定期在测试环境恢复演练，确认备份可用。
4. **加密**：敏感库备份加密存储。

## 增量思路

副本集的 oplog 可以用于时间点恢复：

```text
全量备份 + oplog 回放到指定时间点 = 时间点恢复
```

企业版/Atlas 提供官方时间点恢复；自建可用 oplog 工具（如 `mongodb-oplog-replay` 等社区方案）。

## 易错点

::: danger 常见错误
1. 只备份不恢复演练：备份文件损坏/版本不兼容时才发现，等于没备份。
2. `mongodump` 期间业务持续写入：逻辑备份不是完全一致快照，配合 oplog 或停机窗口。
3. 恢复目标版本不兼容：高版本 dump 到低版本可能失败，保持同版本。
4. 权限不足：备份账号需要 `backup` 角色。
5. 备份文件与数据放同一磁盘：磁盘故障一起丢，异地存放。
6. 分片集群直接 mongodump：要按分片处理或使用专用流程。
:::

## 验证方式

1. 执行 `mongodump` 生成备份，删除一条数据后 `mongorestore`，确认数据恢复。
2. 用 `mongostat` 观察备份期间负载。
3. 每月做一次恢复演练并记录耗时。

## 参考资料

- mongodump：https://www.mongodb.com/docs/database-tools/mongodump/
- mongorestore：https://www.mongodb.com/docs/database-tools/mongorestore/
- 备份策略：https://www.mongodb.com/docs/manual/core/backups/
