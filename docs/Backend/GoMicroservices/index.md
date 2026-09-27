# Go 微服务

<p style="text-align:center;"><img src="./assets/go-microservices-logo.png" alt="Go" style="zoom:75%;" /></p>

Go 语言与微服务是「天然一对」：**编译成单个静态二进制**、**启动毫秒级**、**goroutine 让高并发网络服务写起来不别扭**、**没有虚拟机预热**。这几条加起来，正好对上微服务最看重的两个指标——**部署密度**与**冷启动开销**。本专题讲的是：用 Go 从零搭一套能被运维的服务群，协议怎么选、代码怎么分、治理能力怎么接、出问题怎么定位。

![Go 微服务技术栈分层与三种通信链路](./assets/rpc-choice.svg)

## 目录

### 入门与选型

- [Go 微服务概述与选型](Overview/index.md)

### 协议与治理

- [gRPC 与 Protobuf 工程化](GRPC/index.md)
- [服务治理：注册发现到可观测](Governance/index.md)

### 落地

- [实战：订单服务](Practice/index.md)

::: info 版本约定
本专题以 **Go 1.26** 为主线，gRPC-Go 以 **v1.7x** 分支为准（`google.golang.org/grpc`），Protobuf 使用 **proto3** 语法与 `protoc-gen-go` / `protoc-gen-go-grpc` 双插件生成（`protoc-gen-go` 自 v1.20 起为 `google.golang.org/protobuf` 的 `cmd/protoc-gen-go`，旧的 `github.com/golang/protobuf` 已归档，只保留兼容层）。

框架侧取 **go-zero v1.9.x** 与 **Kratos v2.9.x** 两条主流线做对照。两者 API 差异较大、但治理能力同构，本专题把「共同抽象」抽出来讲，不绑定任一家。
:::

::: tip 阅读前提
本专题假设你已经读过 [Go 语言专题](../Go/index.md)：goroutine 与 channel、接口、`context`、错误处理、`go mod`。如果不熟，先补 [Go 并发模型](../Go/Concurrency/index.md) 与 [Go 包与模块管理](../Go/Modules/index.md)——微服务代码 80% 的复杂度都在「并发 + 跨进程边界」这两件事上。
:::

## 各篇定位

| 页面 | 回答什么问题 |
| --- | --- |
| [Go 微服务概述与选型](Overview/index.md) | 什么场景该拆微服务、HTTP+JSON 与 gRPC 怎么选、go-zero 与 Kratos 怎么挑、单体到微服务的迁移路径 |
| [gRPC 与 Protobuf 工程化](GRPC/index.md) | proto3 怎么写、代码生成怎么接、四种流模式各自解决什么、拦截器怎么做横切、错误码怎么设计 |
| [服务治理：注册发现到可观测](Governance/index.md) | 服务怎么找到彼此、负载均衡策略怎么选、超时重试熔断限流的参数怎么定、Trace 怎么串起来 |
| [实战：订单服务](Practice/index.md) | 工程目录怎么分、配置怎么热更新、优雅退出怎么做、从零到可压测的完整步骤 |

## 与既有专题的分工

库内已经有 [微服务](../Microservices/index.md)（11 页）与 [Spring Cloud](../SpringCloud/index.md)，二者讲的是**通用的微服务方法论与 Java 侧实现**。本专题不重复那部分，只讲**Go 生态特有的三件事**：

- **协议层**：Java 侧习惯 Spring Cloud OpenFeign + JSON，Go 侧默认 gRPC + Protobuf，代码生成与类型安全的约束完全不同。
- **并发模型**：Java 侧一个请求一个线程（或虚拟线程），Go 侧一个请求一个 goroutine，超时、取消、连接池的写法都得跟着变。
- **工程形态**：Java 侧打 fat jar 起 JVM，Go 侧打静态二进制进 scratch 镜像（镜像可以做到 10 MB 以内），部署与发布策略的取舍点不同。

::: warning 说明
三者的关系是**分工**而不是替代：方法论看 [微服务](../Microservices/index.md)，Java 实现看 [Spring Cloud](../SpringCloud/index.md)，Go 实现看本专题。选型阶段读前者，动手阶段读本专题。
:::

## 相关专题

- [Go](../Go/index.md)：语言基础、并发模型、模块管理——本专题的地基
- [微服务](../Microservices/index.md)：服务拆分方法论、注册发现、配置中心的通用原理
- [Spring Cloud](../SpringCloud/index.md)：Java 侧同构实现的对照阅读（同为「服务治理」，实现差异很大）
- [网络编程](../NetworkProgramming/index.md)：TCP/HTTP2 底层、粘包拆包、编解码——理解 gRPC 为什么用 HTTP/2
- [消息队列](../MessageQueue/index.md)：异步解耦与最终一致性，微服务里绕不开的第二条通信链路
- [Docker](../../Ops/Docker/index.md) 与 [Kubernetes](../../Ops/Kubernetes/index.md)：Go 二进制的交付与编排形态
- [监控告警](../../Ops/Monitoring/index.md) 与 [日志体系](../../Ops/LogSystem/index.md)：治理篇里 Trace/Metrics 的落地出口
