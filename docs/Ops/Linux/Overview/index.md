# Linux 概述

Linux 是一个开源的类 Unix 操作系统，由 **内核（Kernel）** 和围绕内核的**发行版（Distribution）**组成，是服务器、云计算、容器和嵌入式领域的事实标准。

## 内核与发行版

- **内核**：Linux 最核心的部分，负责进程调度、内存管理、文件系统、网络等。由 Linus Torvalds 于 1991 年发起。
- **发行版**：内核 + 系统工具 + 包管理器 + 应用集合，打包成可安装使用的系统，如 Ubuntu、Debian、RHEL。

::: tip
日常说的“装一个 Linux”，实际上都是装某个发行版；不同发行版的命令差异主要来自包管理器和默认配置。
:::

## 常见发行版（2026 年）

| 发行版 | 当前主线 | 特点 | 适用 |
| --- | --- | --- | --- |
| Ubuntu | 26.04 LTS（2026 年 4 月发布） | 生态完善、资料多、云厂商默认支持 | 新手、Web 服务器、云主机 |
| Debian | 13（Trixie） | 稳定、纯净、社区驱动 | 服务器、追求稳定 |
| RHEL | 10 | 企业级商业支持、生命周期长 | 企业关键业务 |
| CentOS Stream | 10 | RHEL 上游滚动版 | 兼容 RHEL 的开发环境 |
| Rocky / AlmaLinux | 10 | RHEL 二进制兼容的免费替代 | 迁移自 CentOS 的存量环境 |
| openSUSE | Leap / Tumbleweed | 德国老牌发行版 | 桌面与服务器 |
| Arch | 滚动更新 | 精简、可定制 | 折腾型用户、开发环境 |

::: danger 注意
CentOS 8 已于 2021 年底停止维护，CentOS 7 于 2024 年 6 月 EOL；存量 CentOS 环境建议迁移到 Rocky / AlmaLinux 或云厂商兼容镜像。
:::

## 两大派系

| 派系 | 代表 | 包管理 | 服务管理 |
| --- | --- | --- | --- |
| Debian 系 | Debian、Ubuntu | `apt` / `dpkg` | `systemctl` |
| Red Hat 系 | RHEL、CentOS、Rocky | `dnf` / `yum` / `rpm` | `systemctl` |

命令差异主要在安装软件时：Debian 系用 `apt install`，Red Hat 系用 `dnf install`。

## 适用场景

- 服务器：Web、数据库、中间件、文件服务。
- 云计算与容器：绝大多数云主机、Docker、Kubernetes 都跑在 Linux 上。
- 开发环境：终端工具链、Git、编程语言环境。
- 嵌入式与物联网：路由器、Android 底层、车载系统。

## 基本理念

1. **一切皆文件**：设备、进程、配置都以文件或目录形式暴露。
2. **多用户多任务**：同一系统支持多个用户同时使用。
3. **命令行优先**：终端是最高效的操作方式。
4. **权限模型**：文件有属主、属组和其他用户的读/写/执行权限。

## 学习路径

1. 目录结构与文件命令
2. 文本处理（grep / sed / awk）
3. 权限与用户
4. 进程与服务（systemd）
5. 网络命令
6. Shell 脚本
7. 安全加固与排障

## 相关链接

- Linux 内核官网：https://www.kernel.org/
- Ubuntu 官网：https://ubuntu.com/
- Debian 官网：https://www.debian.org/
- RHEL 文档：https://docs.redhat.com/
