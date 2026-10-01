# 网络基础

<p style="text-align:center;"><img src="./assets/network-logo.png" style="zoom:75%;" /></p>

网络基础是运维的必备底层能力：从**分层模型**理解「问题出在哪一层」，掌握 **DNS、TCP/IP、HTTP/HTTPS** 的核心机制，用 **tcpdump/Wireshark** 抓包定位问题。本专题以运维视角组织，与后端的网络编程专题互补。

- [网络分层与 TCP/IP 模型](Layering/index.md)
- [DNS 解析与配置](Dns/index.md)
- [TCP/IP 核心机制](TcpIp/index.md)
- [HTTP 与 HTTPS](HttpHttps/index.md)
- [网络排查方法论](Troubleshoot/index.md)
- [抓包分析：tcpdump 与 Wireshark](Capture/index.md)
- [实战：网络故障排查全流程](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [Terraform](../Terraform/index.md)：本专题讲"网络怎么工作"，Terraform 讲"网络怎么被声明出来"——VPC 网段切分（`cidrsubnet`）、子网、路由表、安全组都由 IaC 管理，并有可复现的完整示例见 [实战：交付一套云上环境](../Terraform/Practice/index.md)。
- [Nginx](../Nginx/index.md)：应用层的代理、负载均衡与 TLS 终止。
- [Docker 网络模式深入](../Docker/NetworkAdvanced/index.md)：容器网络的实现细节。
- [服务网格：Istio 流量与安全治理](../ContainerOrchestration/ServiceMesh/index.md)：本专题回答「**包怎么走、为什么不通**」——分层模型、DNS 解析、TCP/IP 状态机、TLS 握手，以及用 tcpdump/Wireshark 把证据抓下来；网格专题回答「**服务之间的调用该守什么策略**」——重试、超时、熔断、灰度、身份与授权。排障顺序天然是先本专题、后网格：抓包看到 RST、重传或 TLS 握手失败，回到[抓包分析](Capture/index.md)与[网络排查方法论](Troubleshoot/index.md)定位底层，而不是先去改网格策略；反过来，抓包显示每跳都 200 而业务仍超时，才轮到检查网格的重试与超时配置（见[韧性设计](../ContainerOrchestration/ServiceMesh/Resilience/index.md)）。一个具体的例子：网格里 mTLS 开启后容器内 `curl` 直连上游会失败，那不是网络故障，而是流量没走 Sidecar——判断依据在[安全：mTLS、身份与授权](../ContainerOrchestration/ServiceMesh/Security/index.md)。
