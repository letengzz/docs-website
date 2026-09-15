# 版本控制工具

版本控制用于记录代码变更、多人协作与发布管理。

## 常见工具

- Git（主流）
- GitHub / GitLab / Gitee 托管平台
- SVN（存量项目）

- [Git 进阶](Git/index.md)

## 版本控制还能管什么

版本控制不只用于业务代码，它同样是**个人工作资产的保险**：

| 对象 | 为什么要版本化 | 参考 |
| --- | --- | --- |
| dotfiles（`$PROFILE`、`.zshrc`、`starship.toml`） | 换机器 `git clone` 即可恢复整套终端环境 | [效率工具 · 终端与 Shell 环境](../Efficiency/Terminal/index.md) |
| AutoHotkey / PowerShell 脚本 | 改坏了可回滚，不会一次失误毁掉半年的自动化 | [效率工具 · 桌面与任务自动化](../Efficiency/Automation/index.md) |
| 个人笔记库（纯 Markdown） | 笔记寿命比工具长，Git 保证换工具后内容还在 | [效率工具 · 笔记与知识管理](../Efficiency/Notes/index.md) |
| 文档库本身 | 结构化的公开知识，改动需要可追溯 | [效率工具 · 实战](../Efficiency/Practice/index.md) |

::: warning 注意
**笔记库与 dotfiles 建议用私有仓库**：里面常有内网地址、客户名、临时凭据。推送前先用 `git grep` 搜一遍敏感词。
:::

## 相关专题

- [效率工具](../Efficiency/index.md)：dotfiles、脚本与笔记库的版本化，是效率工具「配置进 Git」这条底线的实现方式。
- [协作与项目管理](../Collaboration/index.md)：面向团队的提交规范与分支策略。
- [CI/CD](../CICD/index.md)：把本地的 Git 钩子升级为服务端流水线。
