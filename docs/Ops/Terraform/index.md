# Terraform

<p style="text-align:center;"><img src="./assets/terraform-logo.png" style="zoom:75%;" /></p>

Terraform 是 HashiCorp 推出的**基础设施即代码（IaC）**工具：用声明式的 HCL 配置描述"云上最终要有哪些资源"，由 Terraform 自己算出"当前缺什么、要改什么、按什么顺序改"，再把真实资源建出来、把状态记进 state 文件。

本专题从 IaC 理念与 Core/Provider 架构讲到 HCL、资源、状态后端与模块，最后用一套真实代码交付"VPC + 子网 + 安全组 + EC2 + 对象存储"，走完"写配置 → init → plan → apply → 验收 → destroy"的完整链路。

## 目录

- [概述与选型](Overview/index.md) - IaC 理念、声明式 vs 命令式、Core/Provider 架构、与 Ansible/Pulumi/CloudFormation 对比
- [安装与初始化](Install/index.md) - 三平台安装、terraform init 做了什么、lock 文件、私有镜像与 provider 缓存
- [HCL 语法与表达式](HCL/index.md) - 块与参数、变量类型、运算符、for 表达式、内置函数、动态块
- [资源、数据源与变量](Resource/index.md) - resource/data/variable/output/locals、count 与 for_each、lifecycle、import 与 moved
- [State 与远程后端](State/index.md) - state 的作用、S3+DynamoDB 后端、状态锁、导入既有资源、工作区与 state 拆分
- [模块与注册表](Module/index.md) - 模块目录规范、输入输出契约、source 五种来源、版本约束与组合
- [实战：交付一套云上环境](Practice/index.md) - 从零写一套 VPC/子网/安全组/EC2/S3 的完整代码，含验收与销毁
- [常见问题与最佳实践](FAQ/index.md) - 高频疑问、十八个踩坑、最佳实践，以及与 OpenTofu 的选型对比

## 一句话理解

::: tip 一句话理解
Ansible 回答"**怎么把机器配好**"（配置管理），Terraform 回答"**云上该有哪些东西**"（资源编排）——前者面向已存在的机器，后者面向"让资源存在"本身。
:::

## 版本状态速览（2026-09 核对）

| 产品 | 主线 | 维护中 | 仅存量 |
| --- | --- | --- | --- |
| Terraform | 1.16.x（1.16.2 / 2026-09-09） | 1.15.x | 1.14 及更早；1.17 已进 beta |
| OpenTofu | 1.12.x（1.12.6 / 2026-08-19） | 1.11.x | 1.10.x 及更早；1.13 已进 beta |

::: warning 先搞清楚你用的是哪一个 Terraform
2023-08-10 起，HashiCorp 把 Terraform 从 **MPL 2.0** 改为 **BUSL 1.1**（自 1.6.0 生效，1.5.7 是最后一个 MPL 版本），社区随即从 1.5.6 分叉出 **OpenTofu**，保持 MPL 2.0 并交由 Linux Foundation（2025-04 进入 CNCF）治理。

- 自己公司内部用 Terraform 管理自己的云账号 → BUSL 不影响你，可继续用官方二进制。
- 要把 IaC 能力嵌入对外销售的产品、或对许可证有硬性要求 → 选 OpenTofu（命令从 `terraform` 换成 `tofu`，语法与 state 格式兼容）。
- 两者 state 格式互通，可以 `terraform apply` 与 `tofu apply` 交替操作同一份 state。

判据、迁移步骤与两条线的功能差异见 [常见问题与最佳实践](FAQ/index.md) 与[版本时间线](FAQ/index.md)。
:::

详细支持状态与 1.6 之后的破坏性变更见 [常见问题与最佳实践](FAQ/index.md)。
