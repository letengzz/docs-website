# 效率工具

<p style="text-align:center;"><img src="./assets/efficiency-logo.png" alt="效率工具" style="zoom:75%;" /></p>

本专题讲的是**日常开发与办公中的效率工具**：终端、命令行、剪贴板、截图、笔记、自动化。它们不是"锦上添花的小玩意"，而是决定你**每天有多少时间花在搬运信息而不是解决问题**的那一层。

和 [IDE 配置](../IDE/index.md) 的分工很清楚：IDE 管"写代码时的效率"，本专题管"写代码之外的所有操作"——跑命令、找文件、贴图、记笔记、把重复动作变成脚本。

## 版本状态速览（2026-09 核对）

| 工具 | 当前版本 / 状态 | 说明 |
| --- | --- | --- |
| Windows Terminal | **1.24.x**（winget 最新 1.24.11911.0 / 2026-08-31） | 需 Windows 10 2004（build 19041）及以上；Shell Integration 的 command marks 自 1.21 起稳定 |
| PowerShell | **7.6（LTS）**，最新补丁 7.6.5 / 2026-08-14 | 支持到 2028-11-14；非 LTS 线 7.5.10（2026-11-10 结束支持）；7.6.0 起 winget 默认装 MSIX |
| Windows PowerShell | **5.1**，随 Windows 分发 | 与 PowerShell 7 并存，可执行文件是 `powershell.exe`（7 是 `pwsh.exe`），互不替换 |
| Microsoft PowerToys | **0.101.2362.0** / 2026-08-25 | 含 Command Palette 紧凑模式、Window Hopper、Advanced Paste 端侧 AI 转换 |
| AutoHotkey | **v2.0.28** / 2026-09-12 | 新脚本一律用 v2 语法；**v1 已不再维护** |
| Obsidian | 公开稳定版 **1.13.8** / 2026-08-20 | 1.14.x 处于早期访问（2026-09）；1.13 起设置界面重构为独立窗口 + 全局搜索 |
| fzf | **0.74.3** / 2026-08-10 | 按 `--query` 的非 ASCII 匹配在 0.74.3 做过性能优化 |
| ripgrep | **15.2.0**（发行版打包）/ 2026-07-16 | 15.x 起 respect `jj` 仓库的 gitignore；`rg` 是命令名 |
| zoxide | **0.9.9** / 2026-01-31 | "频率 + 新近度"记目录；建议保留 `cd` 原义，只用 `z` 加速 |
| starship | **1.26.0** / 2026-06-28 | 跨 Shell 同一份配置；Bash / zsh / fish / PowerShell / Nushell 等 |

::: info 关于版本
上表按各项目官方发布页核对（核对时间 2026-09）。这类工具迭代快，**安装时以包管理器或官方 release 页为准**；页内正文会标明哪些是版本敏感的行为。
:::

## 本专题页面

- [概述与选型](./Overview/index.md)：五类工具地图、选型三原则、2026 年的三个结构变化
- [终端与 Shell 环境](./Terminal/index.md)：Windows Terminal / PowerShell 7 / zsh / starship，配置分层与排障
- [命令行提效](./ShellProductivity/index.md)：别名与函数、fzf、ripgrep、bat、zoxide、jq 的最小可用组合
- [剪贴板与输入效率](./Clipboard/index.md)：三种剪贴板形态、历史剪贴板、文本扩展与安全边界
- [截图与标注](./Screenshot/index.md)：捕获、标注、命名、归档的完整工作流，以及与文档库的衔接
- [笔记与知识管理](./Notes/index.md)：本地优先的笔记库、双向链接、Git 版本化，与发布型文档库的分工
- [桌面与任务自动化](./Automation/index.md)：系统级 / 应用级 / 脚本级三层自动化，AutoHotkey v2 与任务计划
- [实战：搭一套个人效率工具链](./Practice/index.md)：六步落地、30 分钟上手清单、验收与回滚
- [常见问题与最佳实践](./FAQ/index.md)：高频问答、15 条踩坑、12 条最佳实践、术语表

## 推荐阅读路径

| 你的情况 | 建议顺序 |
| --- | --- |
| 刚开始折腾效率工具 | [概述与选型](./Overview/index.md) → [终端与 Shell 环境](./Terminal/index.md) → [实战](./Practice/index.md) |
| 终端天天用但总觉得慢 | [终端与 Shell 环境](./Terminal/index.md) → [命令行提效](./ShellProductivity/index.md) |
| 找文件/找截图花的时间最多 | [截图与标注](./Screenshot/index.md) → [笔记与知识管理](./Notes/index.md) |
| 想减少重复劳动 | [概述与选型](./Overview/index.md) → [桌面与任务自动化](./Automation/index.md) |
| 装了工具但老出问题 | [常见问题与最佳实践](./FAQ/index.md) |

## 三条底线

1. **键盘优先**：鼠标往返一次平均 2 秒，一天 200 次就是十几分钟。能在键盘上完成的，不碰鼠标。
2. **版本化**：工具配置（dotfiles、`settings.json`、`.ahk` 脚本）必须进 Git。否则换台机器你要从零再配一遍——这是最贵的隐性成本。
3. **只留天天用的**：装完一周没打开过的工具，删掉。工具越多，快捷键冲突与启动开销越大。

::: tip 一句话理解
**效率工具的价值不在"工具本身"，而在"少做一次搬运"。** 判断标准很朴素：用了一周之后，你手工复制粘贴的次数有没有变少？
:::

## 相关专题

- [IDE 配置](../IDE/index.md)：编辑器侧的效率（快捷键、插件、配置同步）
- [版本控制工具](../VersionControl/index.md)：dotfiles 与笔记库的版本化都靠它
- [协作与项目管理](../Collaboration/index.md)：效率工具在团队场景下的统一与规范
- [运维 · Linux](../../Ops/Linux/index.md)：服务器侧的终端与 Shell 环境
- [项目管理 · 后端通用模板](../../../project/Base/BackendTemplate/index.md)：把脚本、Git 钩子、容器化落到真实项目里

## 参考资料

- Windows Terminal 官方文档：[learn.microsoft.com/windows/terminal](https://learn.microsoft.com/zh-cn/windows/terminal/)
- PowerShell 官方文档：[learn.microsoft.com/powershell](https://learn.microsoft.com/zh-cn/powershell/)
- Microsoft PowerToys：[github.com/microsoft/PowerToys](https://github.com/microsoft/PowerToys)
- AutoHotkey 官方文档（v2）：[autohotkey.com/docs/v2](https://www.autohotkey.com/docs/v2/)
- Obsidian 官方帮助：[help.obsidian.md](https://help.obsidian.md/)
- fzf / ripgrep / zoxide / starship 官方仓库与文档见各页「参考资料」
