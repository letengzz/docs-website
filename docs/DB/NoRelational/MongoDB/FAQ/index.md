# 常见问题与最佳实践

这一篇汇总 MongoDB 高频问题与工程实践，覆盖连接、认证、性能、副本集、分片与安全。

## 常见问题

### 1. 连接不上数据库

排查顺序：

```shell
ss -lntp | grep 27017          # 端口是否监听
mongosh --eval "db.runCommand({ ping: 1 })"
```

再看：服务是否启动、防火墙/安全组、认证配置。

### 2. 认证失败

管理员账号认证库是 `admin`：

```text
mongodb://admin:密码@host:27017/?authSource=admin
```

普通用户按创建时指定的库认证。

### 3. 内存占用为什么很高

MongoDB 使用**内存映射文件**，会尽量用满内存做缓存（WiredTiger 缓存默认约 50% RAM）。高内存是正常现象，关键是**工作集（热数据）能否放进缓存**，不要只看 RSS。

### 4. 查询慢怎么办

1. `explain("executionStats")` 看是否 `IXSCAN`。
2. 为查询模式建复合索引。
3. 检查 `$or`、正则、`$expr` 等索引失效场景。
4. 大分页改游标/排序字段分页。

### 5. 写入慢 / 写入丢更新

1. 批量写入用 `insertMany` / `bulkWrite`。
2. 计数用 `$inc`，避免先查后写。
3. 检查写关注（w）与磁盘性能。

### 6. 副本集主节点切换后连接失败

连接串必须带 `replicaSet=rs0`，驱动才能自动发现新主节点；客户端直连某个节点 IP 的方式无法故障转移。

### 7. 分片数据倾斜

分片键选择不当（低基数、写热点）。用哈希分片键改善分布；上线后分片键不可改，前期设计是关键。

### 8. 误删数据怎么恢复

先停止写入，从最近备份恢复；有 oplog 可做时间点恢复。教训：配置自动备份 + 异地存储。

### 9. 单文档 16MB 限制

BSON 文档最大 16MB。大对象用 GridFS 或对象存储，文档内不要无限塞数组。

### 10. 安全基线

```text
1. 开启认证（authorization: enabled）
2. 绑定内网 IP，不暴露 0.0.0.0
3. 创建最小权限用户（避免 root 直连）
4. 开启 TLS 传输加密
5. 审计日志（企业版）或访问日志
```

## 最佳实践清单

::: tip 可直接落地的清单
1. 生产使用副本集（3 节点），不用单机。
2. 为高频查询建索引，用 explain 验证 IXSCAN。
3. 计数/累加用 `$inc`，避免竞态。
4. 数据模型按查询设计，减少 $lookup。
5. 开启认证 + TLS，最小权限账号。
6. 定期备份 + 恢复演练（RPO/RTO 明确）。
7. 分片键在项目初期设计好，避免后期重构。
8. 监控：mongostat、mongosh db.serverStatus()、Prometheus exporter。
9. 升级前看版本说明，生产用稳定版 8.x。
10. 字段命名规范（小驼峰）、索引命名规范，团队统一。
:::

## 验证方式

1. 对 FAQ 10 个问题各构造场景验证。
2. 用 `mongostat --discover` 观察读写与连接数。
3. 在测试副本集上做一次故障转移演练。

## 参考资料

- MongoDB 官方文档：https://www.mongodb.com/docs/manual/
- 性能最佳实践：https://www.mongodb.com/docs/manual/core/query-optimization/
- MongoDB 运维检查清单：https://www.mongodb.com/docs/manual/administration/production-notes/
