# 网络编程

<p style="text-align:center;"><img src="./assets/net-logo.png" alt="网络编程" style="zoom:75%;" /></p>

网络编程是后端开发的核心能力：理解 TCP/IP 分层、HTTP 协议、Socket 与 IO 模型，才能写出高性能的通信服务。本专题覆盖网络分层、TCP/UDP、HTTP/HTTPS、Java Socket 与 Netty 框架、粘包拆包，以及完整实战。

- [网络分层与 TCP/IP 基础](Overview/index.md)
- [TCP 与 UDP 详解](TCPUDP/index.md)
- [HTTP 与 HTTPS 协议](HttpHttps/index.md)
- [Socket 与 IO 模型](SocketIO/index.md)
- [Netty 入门](Netty/index.md)
- [Netty 进阶：线程模型与性能调优](NettyAdvanced/index.md)
- [虚拟线程与高并发模型](VirtualThread/index.md)
- [自定义协议设计](ProtocolDesign/index.md)
- [粘包拆包与编解码](StickyHalf/index.md)
- [性能基准与压测](BenchmarkPractice/index.md)
- [实战：Netty 聊天服务器](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

::: tip 运维视角
网络分层、DNS 配置、抓包分析与故障排查的运维方法论见 [网络基础专题](../../Ops/Network/index.md)。
:::

## HTTP/2 与 gRPC：为什么它快，以及长连接带来的新问题

本专题讲了 TCP/UDP、HTTP/HTTPS、Socket 与 IO 模型、粘包拆包。这些是**传输层与协议解析**的基础。当协议换成 HTTP/2 时，两个结论会发生变化，值得单独记一笔。

### 为什么 gRPC 快：不只是「二进制编码小」

| 机制 | 作用 | 对照 HTTP/1.1 |
| --- | --- | --- |
| **二进制分帧（binary framing）** | 把请求/响应切成帧，帧头很短 | 文本协议，头部冗余大 |
| **多路复用（multiplexing）** | 同一 TCP 连接上并行跑成百上千个请求 | 一个连接同时只能处理一个请求（队头阻塞） |
| **头部压缩（HPACK）** | 重复头部只传索引 | 每次请求重复发送完整头部 |
| **Protobuf 编码** | 字段用编号 + 变长整数，比 JSON 小 | JSON 文本，字段名重复传输 |

**收益最大的场景是「长连接 + 高频小包」**；低频大包场景收益不明显（瓶颈在网络带宽而不是协议开销）。

### 长连接带来的三个新问题

| 问题 | 现象 | 解法 |
| --- | --- | --- |
| **L4 负载均衡失效** | 一条连接固定转发到一个后端，扩容后 QPS 不变 | 客户端轮询（需解析到多个地址，如 Headless Service）或换 L7 代理（Envoy / Nginx HTTP/2） |
| **连接被打断** | 滚动更新期间零星 `Unavailable` | keepalive 参数调优；`GracefulStop` + 优雅退出三步 |
| **连接数不再等于请求数** | 监控里的 `connections` metric 不能代表压力 | 用 QPS / 在途请求数做容量指标 |

::: danger 注意：HTTP/2 消灭了应用层的粘包问题，但没消灭「分帧边界」问题
本专题讲的「粘包拆包」在 HTTP/2 里由**帧头里的长度字段**解决，所以业务代码不再需要处理。但代价是：

- **自定义协议仍要自己处理边界**（长度字段 + 校验位，见 [自定义协议设计](../NetworkProgramming/ProtocolDesign/index.md)）；
- **gRPC 单条消息有 4 MB 默认上限**（`ResourceExhausted: grpc: received message larger than max`）。超限时的正确做法是**改分页或流式**，而不是把上限调大——调大只是把问题推迟到内存上。

协议层与代码生成的完整实践见 [gRPC 与 Protobuf 工程化](../GoMicroservices/GRPC/index.md)。
:::

