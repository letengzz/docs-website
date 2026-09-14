# Ansible

<p style="text-align:center;"><img src="./assets/ansible-logo.png" style="zoom:75%;" /></p>

Ansible 是**无代理（agentless）的自动化配置管理与批量部署工具**：用 SSH 连上目标机，把模块推过去执行再删掉，被管节点不需要装任何常驻程序。它把"登录 N 台机器逐条敲命令"变成"写一份可重复执行的 Playbook"。

本专题从架构与选型讲到角色与 Galaxy，最后用一套真实角色批量交付生产 Web 服务器，走完"写清单 → 编角色 → 加密变量 → 灰度执行 → 幂等验收"的完整链路。

## 目录

- [概述与选型](Overview/index.md) - 无代理架构、与 Shell/同类工具对比、适用边界
- [安装与环境准备](Install/index.md) - ansible-core 与社区包的区别、控制/被管节点要求、SSH 免密、ansible.cfg
- [清单与变量作用域](Inventory/index.md) - INI/YAML 清单、组与子组、host_vars/group_vars、动态清单
- [常用模块与 Ad-hoc](Module/index.md) - 文件/包/服务/系统类模块、幂等性、临时命令
- [Playbook 编写](Playbook/index.md) - play 结构、handler、loop、when、block/rescue、tags、check mode
- [变量、Facts 与模板](Variable/index.md) - 变量优先级、facts 与 register、Jinja2 模板与过滤器
- [角色、Galaxy 与 Collections](Role/index.md) - 角色目录规范、依赖、requirements.yml、集合
- [实战：批量交付生产 Web 服务器](Practice/index.md) - 清单 + 角色 + Vault 加密变量 + 灰度执行与验收
- [常见问题与最佳实践](FAQ/index.md) - 高频疑问、踩坑清单与版本演进迁移

## 一句话理解

::: tip 一句话理解
Shell 脚本是"**做什么**"（命令式，跑第二遍可能出错），Ansible 是"**要什么**"（声明式，跑第二遍什么都不做）——**幂等**是它和脚本最大的区别。
:::

## 版本状态速览（2026-09 核对）

| 组件 | 主线 | 维护中 | 仅存量 |
| --- | --- | --- | --- |
| ansible-core | 2.21.x（2.21.2 / 2026-07-13） | 2.20.x（2.20.7） | 2.19.x（2026-11-30 结束支持）、2.18 及更早（已 EOL） |
| ansible（社区聚合包） | 13.x（依赖 ansible-core 2.20） | 12.x（依赖 2.19，2026-12 EOL） | 11.x 及更早 |

::: warning 两个"Ansible"别搞混
- **ansible-core**：只有引擎 + 内置模块（约 100 个），版本号形如 2.21.x，**生产环境推荐**。
- **ansible**（PyPI 上的社区包）：ansible-core + 数百个社区集合（collections），版本号形如 13.x。

两者版本号不同步，升级前先确认自己装的是哪个。详见 [安装与环境准备](Install/index.md)。
:::

详细支持状态与 2.19 起的破坏性变更（Data Tagging）见 [常见问题与最佳实践](FAQ/index.md)。

## 相关专题

- [Terraform](../Terraform/index.md)：两者互补——**Terraform 建机器（VPC / 子网 / 安全组 / 云主机 / 对象存储），Ansible 配机器（装包、下发配置、重启服务）**。标准组合姿势是 Terraform 用 `output` 输出主机 IP，Ansible 用这份清单做配置收敛，分工与判据见 [Terraform 概述与选型](../Terraform/Overview/index.md)。
- [Linux 进阶](../Linux/Advanced/index.md)：被 Ansible 接管前，机器本身要先按基线加固好。
- [CI/CD 自动部署与回滚](../../Tools/CICD/DeployRollback/index.md)：把 Playbook 接进流水线做批量发布与灰度。
