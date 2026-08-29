# 网络编程常见问题与最佳实践

本页汇总网络编程中最常遇到的问题：连接不上、半包、CLOSE_WAIT/TIME_WAIT 堆积、Netty 内存泄漏、长连接保活等，并给出排查路径与最佳实践清单。

## 连接不上，怎么排查

```text
症状：connect 超时 / connection refused
```

按层排查：

1. **网络层**：`ping 目标IP` 是否通。
2. **传输层**：`telnet 目标IP 端口` 是否通；不通查防火墙/安全组。
3. **服务层**：服务是否监听（`ss -lntp | grep 端口`）、是否满连接。
4. **应用层**：协议/握手是否匹配（HTTP 打到了 TCP 端口等）。
5. **DNS**：`nslookup 域名` 解析是否正确。

## 服务端出现大量 TIME_WAIT

```text
原因：服务端主动关闭大量短连接，等待 2MSL（约 60s）
```

处理：

1. 客户端复用连接（连接池/Keep-Alive）。
2. 减少主动关闭：让客户端先关闭。
3. 调优（谨慎）：`tcp_tw_reuse`（客户端）、缩短 TIME_WAIT 需评估安全。
4. 监控连接状态，区分“正常波动”与“异常堆积”。

## 大量 CLOSE_WAIT

```text
原因：对端关闭连接，本地没调用 close（Socket 泄漏）
```

排查：

1. `ss -ant | grep CLOSE_WAIT | wc -l` 统计。
2. 找持有该 Socket 的进程与线程栈（jstack/lsof）。
3. 检查代码：输入流读完是否关闭、异常路径是否遗漏 close。
4. 用 try-with-resources 或统一连接管理。

## TCP 粘包/拆包导致数据错乱

1. 确认使用了解码器（定长/分隔符/长度字段）。
2. 长度字段协议是推荐方案，能应对二进制数据。
3. 编解码器单元测试：一次写多条、分多次写。
4. 检查 LengthFieldBasedFrameDecoder 参数是否与协议一致。

详见 [粘包拆包与编解码](../StickyHalf/index.md)。

## Netty 内存泄漏

```text
症状：内存持续增长，日志出现 LEAK: ByteBuf.release()
```

1. 打开泄漏检测：`-Dio.netty.leakDetectionLevel=paranoid`。
2. 检查自定义 Handler 是否 release 了读到的 ByteBuf。
3. 用 `SimpleChannelInboundHandler` 自动释放。
4. 出站写完后引用计数归零，别重复 release。
5. 长连接长时间运行后观察堆外内存（Direct Memory）。

## 长连接如何保活

| 手段 | 说明 |
| --- | --- |
| TCP keepalive | 系统级保活，探测周期长 |
| 应用心跳 | 定期发心跳包，超时判死（推荐） |
| Netty IdleStateHandler | 读写空闲触发，自动断连 |
| 断线重连 | 客户端指数退避重连 |

```java
// Netty 心跳：60s 未读触发 userEventTriggered
ch.pipeline().addLast(new IdleStateHandler(60, 0, 0, TimeUnit.SECONDS));
```

## 高并发连接的选择

```text
1 万并发连接：
  BIO：1 万线程 → 不可行
  NIO/Netty：少量 EventLoop → 可行
```

要点：

1. 用 Netty 而非裸 NIO（生产级封装）。
2. EventLoop 数量 = CPU×2 起步，压测调优。
3. 业务耗时操作必须移出 IO 线程。
4. 监控连接数、内存、EventLoop 队列长度。

## 网络编程最佳实践清单

::: tip 网络编程十诫
1. 排查从底层到上层：ping → telnet → curl。
2. TCP 是字节流，必须处理粘包拆包。
3. 服务端 Socket 异常路径必须 close，防 CLOSE_WAIT。
4. 高并发用 Netty，业务逻辑不进 IO 线程。
5. 长连接用心跳保活 + 断线重连。
6. 连接池复用，减少握手与 TIME_WAIT。
7. ByteBuf 用后即 release，防内存泄漏。
8. 协议设计：魔数 + 版本 + 长度 + 消息体。
9. 超时与背压：读写超时、写缓冲水位。
10. 压测 + 监控连接状态与线程模型。
:::

## 验证方式

1. 压测 1 万连接，观察线程数与内存是否符合预期。
2. 模拟对端断开，确认服务端 CLOSE_WAIT 不堆积。
3. 长时间运行聊天服务器，确认无 ByteBuf 泄漏、心跳正常。

## 参考资料

- 本专题章节入口：[网络编程目录](../index.md)
- Java IO/NIO 常见问题：[IO/NIO FAQ](../../Java/JavaSE/IO/FAQ/index.md)
- tcpdump 手册：https://www.tcpdump.org/
- Netty 内存泄漏排查：https://netty.io/wiki/reference-counted-objects.html
