# Go

<p style="text-align:center;"><img src="./assets/go-logo.png" alt="Go" style="zoom:75%;" /></p>

Go（又称 Golang）是 Google 于 2009 年开源的**静态类型、编译型**编程语言。它的设计目标很明确：用接近脚本语言的开发效率，写出接近 C 的运行性能，并且**把并发与工程化能力直接做进语言和工具链**。本专题面向零基础到能用 Go 写服务的人，覆盖语言核心、并发模型、工程化、Web 开发与实战交付。

## 目录

### 入门与基础

- [Go 概述](Overview/index.md)
- [Go 环境搭建](Environment/index.md)
- [Go 基础语法](BasicSyntax/index.md)
- [Go 函数、方法与接口](Functions/index.md)
- [Go 集合：数组、切片与映射](Collections/index.md)

### 语言进阶

- [Go 泛型](Generics/index.md)
- [Go 并发模型](Concurrency/index.md)
- [Go 错误处理与 panic](ErrorHandling/index.md)
- [Go 包与模块管理](Modules/index.md)

### 应用与交付

- [Go Web 开发](WebDev/index.md)
- [实战：短链服务](Practice/index.md)
- [Go 常见问题与最佳实践](FAQ/index.md)

::: info 版本约定
本专题以 **Go 1.26**（当前稳定线，最新补丁 go1.26.6）为主线编写。Go 团队同时维护两条版本线（1.26 与 1.25），约每月发布一个小版本并持续提供安全修复。涉及旧版本差异的地方会明确标注，例如**循环变量捕获语义**在 Go 1.22 发生变化、**泛型**自 Go 1.18 才可用。
:::

::: tip 学习路径建议
先按「概述 → 环境 → 基础语法 → 函数与接口 → 集合」写出第一个能跑的 Go 程序；再补「泛型 → 并发 → 错误处理 → 模块管理」；最后做「Web 开发 → 实战」。每学完一节都用 `go test ./...` 和 `go vet ./...` 跑一遍，比只读代码效果好得多。
:::

## 各篇定位

| 页面 | 回答什么问题 |
| --- | --- |
| [Go 概述](Overview/index.md) | Go 适合做什么、与 Java/Python 的差异、生态与版本策略 |
| [Go 环境搭建](Environment/index.md) | 安装、GOPATH 与 Module、代理、IDE 与调试配置 |
| [Go 基础语法](BasicSyntax/index.md) | 变量、常量、类型、流程控制、指针与结构体 |
| [Go 函数、方法与接口](Functions/index.md) | 多返回值、闭包、方法集、接口与隐式实现 |
| [Go 集合：数组、切片与映射](Collections/index.md) | slice 扩容、map 底层、拷贝与引用语义 |
| [Go 泛型](Generics/index.md) | 类型参数、约束、与接口方案的取舍 |
| [Go 并发模型](Concurrency/index.md) | goroutine、channel、GMP 调度、sync 与并发模式 |
| [Go 错误处理与 panic](ErrorHandling/index.md) | error 惯例、错误包装、defer/recover 边界 |
| [Go 包与模块管理](Modules/index.md) | go.mod、版本选择、私有仓库与依赖治理 |
| [Go Web 开发](WebDev/index.md) | net/http、路由、中间件、JSON 与优雅关闭 |
| [实战：短链服务](Practice/index.md) | 从零到可部署服务的完整工程实践 |
| [Go 常见问题与最佳实践](FAQ/index.md) | 高频坑、性能与工程规范速查 |

::: warning 说明
Go 的**工具链本身就是语言的一部分**（`go fmt` / `go test` / `go vet` / `go mod`）。因此本专题会把命令与代码放在同等重要的位置——只读代码不跑命令，很难真正掌握 Go 的工程习惯。
:::

## 相关专题

- [Java 入门](../Java/JavaSE/Overview/index.md)：另一门静态类型语言的对照学习
- [认证与授权](../Auth/index.md)：Go 服务同样需要的 JWT / OAuth2 基础
- [微服务](../Microservices/index.md)：Go 常作为微服务与网关的实现语言
- [Docker](../../Ops/Docker/index.md)：Go 二进制的容器化交付方式
- [Kubernetes](../../Ops/Kubernetes/index.md)：Go 生态最主流的运行平台
