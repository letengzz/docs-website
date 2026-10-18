# JumpServer

::: info 本页的定位
本页按「**特权访问入口**」处理，只讲它与其他运维专题的边界（见下节三条），不讲安装与资产录入：这部分随部署形态（自建 / 云托管 / 内网离线）差异极大，写进来会立刻过期，而版本化的安装步骤在官方文档里始终是最新的。
:::

## 相关专题

- [Ansible 自动化运维](../Ansible/index.md)：JumpServer 负责"人"的登录审计，Ansible 负责"机器"的批量执行，两者互补
- [Linux · 安全加固](../Linux/Advanced/SecurityHardening/index.md)：SSH 加固与免密登录，是 Ansible 接管节点的前置条件
- [安全加固](../SecurityHardening/index.md)：从跨层治理视角看特权访问、凭据托管与操作审计
