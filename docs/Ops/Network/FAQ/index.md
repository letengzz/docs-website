# 常见问题与最佳实践

汇总网络运维中最高频的问题：连通性、DNS、TCP 状态、MTU、抓包与监控，方便快速查阅。

## 连通性类

### ping 通但业务连不上？

ping 走 ICMP，业务走 TCP 端口。排查：

```shell
nc -vz 1.2.3.4 443
ss -tlnp | grep 443
# 防火墙：iptables / firewalld / 云安全组
```

常见原因：端口未监听、防火墙 drop、安全组未放行。

### 连接超时和拒绝有什么区别？

```text
超时（timeout）：包被丢弃/无响应 → 防火墙 DROP、目标不可达
拒绝（refused）：立即 RST → 端口未监听、防火墙 REJECT
```

抓包一眼可辨：无响应 vs 出现 RST。

## DNS 类

### 域名解析慢怎么排查？

```shell
time dig example.com
dig @223.5.5.5 example.com     # 换 DNS 对比
```

慢的可能：递归 DNS 延迟、权威 DNS 慢、本机 resolv.conf 配置了不可达服务器。

### 改了 DNS 为什么不生效？

1. TTL 未到（权威 + 递归缓存）；
2. 本地 hosts 覆盖；
3. 浏览器/系统 DNS 缓存；
4. 改了错误的记录类型（改 A 却查 CNAME）。

## TCP 状态类

### TIME_WAIT 很多要处理吗？

主动关闭方产生 TIME_WAIT（2MSL ≈ 60s），高并发短连接时数量大是**正常现象**。只有当连接数打满、新连接失败时才需优化：

- 客户端侧：连接复用（HTTP keep-alive/连接池）；
- 服务端侧：确认 `tcp_tw_reuse` 语义后谨慎使用；
- 优先从应用层减少新建连接。

### CLOSE_WAIT 堆积说明什么？

服务端收到 FIN 后**应用没调用 close()**——典型的资源泄漏/代码 bug：

```shell
ss -tan | grep CLOSE_WAIT | wc -l
```

排查对应服务的连接管理逻辑（响应未关闭、线程阻塞、异常未释放）。

## MTU 类

### 怎么判断 MTU 问题？

```shell
# 大包失败、小包成功
ping -s 1472 -M do 目标
ping -s 1400 -M do 目标
```

常见场景：VPN/隧道、云网络、PPPoE。调整 MTU 后要持久化并测试全部业务路径。

## 抓包类

### 抓包工具抓不到流量？

1. 抓错网卡（业务走 eth1 抓了 eth0）；
2. 过滤条件太严（先 `-nn port X` 收窄）；
3. 没有 root 权限；
4. 流量是加密隧道（如 WireGuard 内，抓外层看不到内层）。

### 抓包看到大量重传说明什么？

- 网络丢包（物理链路、拥塞）；
- 接收端缓冲区不足（窗口为 0）；
- 中间设备限速/丢包；
- MTU 分片问题。

结合 Wireshark TCP Stream Graph 与两端 `ss` 观察。

## 监控类

### 网络监控应该盯哪些指标？

| 指标 | 方式 |
| --- | --- |
| 存活 | ping 存活探测 |
| 端口 | TCP 探测（nc/脚本） |
| 丢包率 | ping 统计 / mtr |
| 带宽 | iftop / snmp |
| 证书到期 | openssl 脚本 |
| DNS 解析 | dig 定时探测 |
| 连接数 | ss 统计 + 告警 |

## 最佳实践清单

::: tip 网络运维检查清单
1. 是否先确认问题在哪一层（链路/网络/传输/应用）？
2. ping 通了是否还验证端口？
3. DNS 问题是否用 dig 对比公共 DNS？
4. 连接状态异常是否看 ss 统计与 CLOSE_WAIT？
5. 大包不通小包通是否排查 MTU？
6. 抓包是否限定条件、落盘留档、注意敏感数据？
7. 证书与域名是否纳入监控告警？
8. 每次故障是否产出排查记录与预防项？
9. 网络变更是否遵循「验证 → 回滚」流程？
10. 是否有一键收集脚本（ip/ping/ss/curl/dig）？
:::

## 参考资料

- [RFC 1122：主机网络需求](https://www.rfc-editor.org/rfc/rfc1122)
- [Linux iproute2 文档](https://www.kernel.org/doc/html/latest/networking/)
- [tcpdump / Wireshark 文档](https://www.tcpdump.org/)
