# 配置同步与团队统一

「我这边能跑」这句话背后，往往是**配置差异**而不是代码差异。本页把 IDE 配置拆成三个层次，说清每一层该由谁负责、放在哪里、怎么验证——这是团队把「各配各的」变成「仓库说了算」的核心方法论。

![配置同步的三个层次：个人 / 团队 / 环境](../assets/config-sync.svg)

## 一句话定位

配置分三层：**个人偏好归个人同步，团队规则归仓库，运行环境归容器与版本清单。** 层次搞混就会出现两类问题——用个人同步分发团队规则（新人收不到），或者用仓库管理个人偏好（天天冲突）。

## 第 1 层：个人同步

目标：换机器不丢自己的习惯（主题、字体、键位、片段）。

### 各平台配置路径

| 工具 | Windows | macOS | Linux |
| --- | --- | --- | --- |
| IntelliJ IDEA | `%APPDATA%\JetBrains\IntelliJIdea2026.2\` | `~/Library/Application Support/JetBrains/IntelliJIdea2026.2/` | `~/.config/JetBrains/IntelliJIdea2026.2/` |
| VS Code | `%APPDATA%\Code\User\` | `~/Library/Application Support/Code/User/` | `~/.config/Code/User/` |

::: warning 路径里的版本号是关键
IDEA 配置目录名带大版本号，**升级大版本等于换了目录**，旧配置不会被自动继承（首次启动会提示导入）。VS Code 的 `Code` 目录不带版本号，升级无此问题。
:::

### 内建同步能力对比

| 维度 | JetBrains Settings Sync | VS Code Settings Sync |
| --- | --- | --- |
| 开启位置 | `Settings` → `Settings Sync` | 左下角账户图标 → `Turn on Settings Sync` |
| 账号 | JetBrains Account | GitHub 或 Microsoft 账号 |
| 可同步内容 | IDE 设置、键位、代码样式、颜色主题、插件列表、Live Templates 等 | 设置、快捷键、代码片段、扩展、UI 状态（可按项勾选） |
| 粒度控制 | 按类别开关 | 按类别勾选 |
| 企业环境 | 受 License Server 场景限制，部分档位不可用 | 部分组织策略下会被禁用（也有私有同步服务的替代方案） |
| 适合谁 | 个人多机、个人偏好 | 个人多机、个人偏好 |

::: danger 三条边界，越界会出事
1. **不要用来分发团队规则**：团队规则必须进仓库，否则「装了没装同步」的人表现不同。
2. **不要同步含密钥的内容**：数据库连接、`launch.json` 环境变量、私有仓库凭据都可能被带上去。
3. **不要把它当备份**：它同步的是「类别」，不是「文件快照」，误删一项可能同步到所有机器。
:::

### dotfiles 方案：把配置交给 Git

对不想依赖账号同步的团队，最稳的做法是**把配置目录做成 dotfiles 仓库 + 软链接**。

```shell
# 目录结构示例
dotfiles/
├─ idea/
│  ├─ options/
│  ├─ keymaps/
│  └─ codeStyles/
└─ vscode/
   ├─ settings.json
   ├─ keybindings.json
   └─ snippets/

# 用软链接挂回真实位置（Linux/macOS）
ln -sfn ~/dotfiles/vscode/settings.json  ~/.config/Code/User/settings.json
ln -sfn ~/dotfiles/vscode/keybindings.json ~/.config/Code/User/keybindings.json

# Windows（PowerShell，需管理员或开启开发者模式）
# New-Item -ItemType SymbolicLink -Path "$env:APPDATA\Code\User\settings.json" -Target "D:\dotfiles\vscode\settings.json"
```

| 方案 | 优点 | 代价 |
| --- | --- | --- |
| 内建 Settings Sync | 零配置、跨平台 | 依赖账号；粒度粗；不透明 |
| dotfiles + 软链接 | 完全可控、可 review、可回滚 | 需要一次性搭建；Windows 需权限 |
| 手动导出/导入 | 简单 | 容易忘记，形同不存在 |

::: tip 推荐组合
**内建同步负责「日常无感」，dotfiles 负责「关键项可控」。** 例如把键位与代码样式放进 dotfiles，把主题与 UI 状态交给内建同步。
:::

## 第 2 层：团队统一（最重要的一层）

目标：**代码风格、检查规则、必备插件在仓库里说清楚**，不靠口头约定。

### 用什么文件承载

| 关注点 | 载体 | 作用范围 |
| --- | --- | --- |
| 缩进/换行/字符集/尾空格 | `.editorconfig` | **所有编辑器通用**（事实标准） |
| 格式化细节（空行、导入顺序、换行策略） | IDA：`.idea/codeStyles/`<br/>VS Code：`.vscode/settings.json` | 各自工具 |
| 语言级规则 | ESLint / Prettier / Checkstyle / spotless 配置 | 工具链，可与 CI 共用 |
| 静态检查规则 | `.idea/inspectionProfiles/`、`.eslintrc`、`sonar-project.properties` | 各自工具 + CI |
| 推荐/必备插件 | `.vscode/extensions.json`、`.idea/externalDependencies.xml` | 各自工具 |
| 构建与调试 | `.vscode/tasks.json`、`.vscode/launch.json`、`.idea/runConfigurations/` | 各自工具 |

### `.editorconfig`：跨工具一致性的地基

```ini [.editorconfig]
# 顶层标记：告诉工具不要再往上层目录找
root = true

# 所有文件
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

# 按语言覆盖
[*.{java,xml}]
indent_size = 4

[*.md]
# Markdown 里行尾两个空格代表硬换行，不能裁
trim_trailing_whitespace = false

[Makefile]
indent_style = tab

[*.{yml,yaml}]
indent_size = 2
```

| 属性 | 取值 | 说明 |
| --- | --- | --- |
| `root` | `true` | 只应出现在仓库根的 `.editorconfig`，表示不再向上查找 |
| `charset` | `utf-8` / `utf-8-bom` / `latin1` | 中文项目统一 `utf-8`；**不要用 BOM**（容易在脚本里读出多余字符） |
| `end_of_line` | `lf` / `crlf` / `cr` | Windows 开发也建议 `lf`，由 Git 的 `core.autocrlf` 处理工作区差异 |
| `indent_style` / `indent_size` | `space` + 数字 / `tab` | 与团队格式化工具保持一致 |
| `insert_final_newline` | `true` / `false` | 绝大多数语言应为 `true` |
| `trim_trailing_whitespace` | `true` / `false` | Markdown 例外 |
| `max_line_length` | 数字 / `off` | 与格式化器的 `printWidth` 对齐 |

::: danger 四个常见错误
1. **忘了 `root = true`**：工具会继续向上层目录找 `.editorconfig`，可能命中用户主目录里的配置，导致「同一份代码在不同机器缩进不同」。
2. **`[*.md]` 没关掉 `trim_trailing_whitespace`**：会破坏 Markdown 的硬换行，也会在 diff 里产生大量噪音。
3. **`end_of_line` 与 Git 配置打架**：仓库写 `lf`、而 `.gitattributes` 又强制 `crlf`，会出现「每次打开文件都显示全文件改动」。
4. **`.editorconfig` 与 IDE 代码样式不一致**：IDE 风格覆盖了它，结果「配置文件写了但没人遵守」。
:::

### 让 IDEA 真正服从 `.editorconfig`

IDEA 内建支持 EditorConfig，但要注意两点：

```text
① 确认已启用：Settings → Editor → Code Style → "Enable EditorConfig support"
   启用后，.editorconfig 中出现的属性会「接管」IDE 里同名设置（界面会置灰）

② 反向导出：Settings → Editor → Code Style → ⚙ → Export → EditorConfig
   可以把当前 IDEA 风格导出成带 ij_ 前缀的 .editorconfig 属性
```

::: tip `ij_` 前缀属性
JetBrains 支持在 `.editorconfig` 中使用 `ij_` 前缀的属性来承载 IDEA 专有的风格设置（如导入顺序、空行策略）。**好处是「一份文件同时服务 IDE 与跨工具基础规则」**；代价是其他编辑器不认识这些属性（会安静忽略，不影响使用）。
:::

### VS Code 侧的工作区配置模板

```json [.vscode/settings.json]
{
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "files.eol": "\n",
  "files.encoding": "utf8",
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true,

  "[markdown]": {
    "files.trimTrailingWhitespace": false
  },

  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/target": true
  }
}
```

### 代码风格对齐矩阵

同一项规则在不同载体里的名字不同，**对齐时按这张表逐项核对**，比凭印象靠谱。

| 规则 | `.editorconfig` | IDEA（`codeStyles/*.xml`） | VS Code `settings.json` | Prettier |
| --- | --- | --- | --- | --- |
| 缩进方式 | `indent_style` | `INDENT_STYLE` | `editor.insertSpaces` | `useTabs` |
| 缩进宽度 | `indent_size` | `INDENT_SIZE` | `editor.tabSize` | `tabWidth` |
| 换行符 | `end_of_line` | `LINE_SEPARATOR` | `files.eol` | `endOfLine` |
| 字符集 | `charset` | 项目编码设置 | `files.encoding` | — |
| 行尾空格 | `trim_trailing_whitespace` | `KEEP_TRAILING_SPACES`（反向） | `files.trimTrailingWhitespace` | 自动处理 |
| 文件末尾空行 | `insert_final_newline` | 由格式化器处理 | `files.insertFinalNewline` | 自动处理 |
| 最大行宽 | `max_line_length` | `RIGHT_MARGIN` | `editor.rulers` | `printWidth` |

::: warning `KEEP_TRAILING_SPACES` 是反向的
IDEA 的字段表示「保留行尾空格」，而 `.editorconfig` 的 `trim_trailing_whitespace = true` 表示「裁掉」。**对齐时不要写成同一个值**，这是「配置明明一样但行为相反」的典型来源。
:::

### 哪些该提交，哪些不该

| 类别 | 例子 | 建议 |
| --- | --- | --- |
| 团队规则 | `.editorconfig`、`.idea/codeStyles/`、`.idea/inspectionProfiles/`、`.vscode/settings.json`（不含个人偏好） | **提交** |
| 构建与调试 | `.vscode/tasks.json`、`.vscode/launch.json`（用 `${env:}` 读密钥）、`.idea/runConfigurations/` | **提交** |
| 插件声明 | `.vscode/extensions.json`、`.idea/externalDependencies.xml` | **提交** |
| 个人状态 | `.idea/workspace.xml`、`.vscode/.history`、`.idea/shelf/`、`.idea/usage.statistics.xml` | 忽略 |
| 敏感信息 | `.idea/dataSources*.xml`、含口令的 `launch.json` | 忽略或改用环境变量 |

## 第 3 层：环境可复现

目标：**换台机器或新人入职，一条命令得到同样的开发环境。**

| 手段 | 做什么 | 关联文档 |
| --- | --- | --- |
| 版本锁定 | 用 Toolbox / 安装清单把 IDE 大版本线固定；写明升级流程 | [IntelliJ IDEA 深入](../IntelliJIDEA/index.md) |
| 容器化环境 | `devcontainer.json` 定义基础镜像、工具链、端口、VSCode 扩展 | [远程开发与容器化环境](../RemoteDev/index.md) |
| 依赖锁定 | Maven 版本由 `pom.xml` + toolchain 决定；Node 侧由 lockfile 决定 | [包管理器深入](../../PackageManager/index.md) |
| 自检脚本 | 一个脚本检查 jdk/mvn/node 版本与必需文件是否存在 | 本页「CI 校验」一节 |

## CI 校验：把「配置存在」变成门禁

配置文件最容易「写着写着就没人维护」。把它纳入流水线，成本极低但效果显著。

```shell
#!/usr/bin/env bash
# scripts/check-ide-config.sh
# 用途：在 CI 中校验 IDE 配置文件存在且关键项未被改坏
set -euo pipefail

fail=0

# 1. 跨编辑器风格声明必须存在
if [ ! -f .editorconfig ]; then
  echo "✗ 缺少 .editorconfig（跨工具风格一致性无法保证）"; fail=1
fi

# 2. 根 .editorconfig 必须声明 root = true
if [ -f .editorconfig ] && ! grep -qE '^\s*root\s*=\s*true' .editorconfig; then
  echo "✗ .editorconfig 缺少 root = true（会向上层目录继承）"; fail=1
fi

# 3. Markdown 不应被裁掉行尾空格
if [ -f .editorconfig ] && ! grep -qA2 '\[\*\.md\]' .editorconfig; then
  echo "⚠ 建议为 [*.md] 显式关闭 trim_trailing_whitespace"; fail=1
fi

# 4. VS Code 工作区配置不允许出现绝对路径
if grep -rnE '"[^"]*":\s*"[A-Za-z]:\\\\|/Users/|/home/' .vscode/settings.json 2>/dev/null; then
  echo "✗ .vscode/settings.json 含绝对路径（他人机器无效）"; fail=1
fi

# 5. 工作区配置不应包含个人偏好白名单之外的键
if grep -qE '"(workbench\.colorTheme|editor\.fontSize)"' .vscode/settings.json 2>/dev/null; then
  echo "⚠ .vscode/settings.json 出现个人偏好项（主题/字号），建议移回用户设置"; fail=1
fi

[ "$fail" -eq 0 ] && echo "✓ IDE 配置校验通过"
exit "$fail"
```

::: tip 为什么值得做
这段脚本 40 行，能拦住三类高频问题：新人 clone 后风格不一致、`settings.json` 里混进绝对路径、个人偏好污染团队配置。**回报远高于维护成本。**
:::

## 安全注意

| 风险 | 场景 | 对策 |
| --- | --- | --- |
| 凭据入库 | `dataSources*.xml`、`launch.json`、`.env` 被 `datasource` 插件写入 | 加入 `.gitignore`；改用环境变量；已提交的需清理历史 |
| 同步外泄 | Settings Sync 把含密钥的类别同步到云端 | 同步前审查类别；密钥类配置不放进被同步的文件 |
| 插件读取代码 | 第三方插件可读全部代码与终端输出 | 只用官方市场；企业环境做插件清单与扫描 |
| 远程开发泄露 | 远程侧配置文件可能含主机信息 | 远程设置单独管理，不把内网地址写进仓库 |

## 验证方式

```shell
# 1. 确认 .editorconfig 被 IDE 读取
#    VS Code：装了 EditorConfig 扩展后，改动缩进设置应无效果（被 .editorconfig 接管）
#    IDEA：改动缩进设置应无法编辑（被 .editorconfig 接管）

# 2. 确认两人格式化结果一致（最有效的验证）
git checkout -b test-format
# 在 A 机器打开一个文件、保存（触发格式化）
git diff --stat          # 期望：无改动，或只有预期的改动
# 在 B 机器（不同系统）重复上述步骤，再次 git diff --stat
# 期望：两次结果一致，没有「只有换行符变了」的整文件 diff

# 3. 确认工作区配置无绝对路径
grep -nE '([A-Za-z]:\\\\|/Users/|/home/)' .vscode/settings.json || echo "OK: 无绝对路径"

# 4. 确认 CI 校验可运行
bash scripts/check-ide-config.sh
# 期望：✓ IDE 配置校验通过
```

## 常见问题与坑

::: danger 十个高频坑
1. **`.editorconfig` 忘了 `root = true`**：命中用户主目录配置，表现随机。
2. **`[*.md]` 没关 `trim_trailing_whitespace`**：破坏 Markdown 硬换行。
3. **`.editorconfig` 与 IDE 代码样式打架**：写了不生效，因为 IDE 风格覆盖了它。
4. **`KEEP_TRAILING_SPACES` 与 `trim_trailing_whitespace` 写成同值**：语义相反。
5. **`.idea/` 整个忽略**：代码风格与必需插件无法共享，新人体验断层。
6. **提交 `.idea/workspace.xml`**：打开的文件、窗口布局全在里面，必然冲突。
7. **`.vscode/settings.json` 写绝对路径**：他人机器无效，还可能泄露用户名。
8. **把个人偏好（主题/字号）写进工作区设置**：团队被迫接受某个人的审美。
9. **用 Settings Sync 分发团队规则**：没开同步的人收不到，问题更隐蔽。
10. **凭据类文件入库**：`dataSources*.xml` 这类文件经常被忽略，需专项检查。
:::

::: tip 最佳实践五条
1. **三层分明**：个人同步只管偏好，仓库管规则，容器管环境。
2. **`.editorconfig` 是地基**：先用它把「跨工具能一致」的部分锁住。
3. **IDE 专有风格单独管**：`.idea/codeStyles/` 与 `ij_` 前缀二选一，不要两套并行。
4. **把校验放进 CI**：40 行脚本就能防止配置腐化。
5. **格式化以工具链为准**：Prettier / Spotless 的输出是唯一标准，IDE 只是触发器。
:::

## 相关文档

- [IDE 配置总览](../index.md)
- [IntelliJ IDEA 深入](../IntelliJIDEA/index.md)：`.idea/` 目录的提交策略与 `options/` 备份。
- [VS Code 深入](../VSCode/index.md)：配置层级与工作区文件全表。
- [插件与扩展](../Plugins/index.md)：插件清单怎么随仓库分发。
- [远程开发与容器化环境](../RemoteDev/index.md)：第 3 层「环境可复现」的容器方案。
- [实战：搭一套统一的 IDE 环境](../Practice/index.md)：把本页的方法论走完一遍。

## 参考资料

- EditorConfig 规范与属性列表：[editorconfig.org](https://editorconfig.org/)
- JetBrains 对 EditorConfig 的支持（含 `ij_` 属性）：[jetbrains.com/help/idea/editorconfig.html](https://www.jetbrains.com/help/idea/editorconfig.html)
- JetBrains Settings Sync 说明：[jetbrains.com/help/idea/settings-sync.html](https://www.jetbrains.com/help/idea/settings-sync.html)
- VS Code Settings Sync：[code.visualstudio.com/docs/configure/settings-sync](https://code.visualstudio.com/docs/configure/settings-sync)
- Prettier 配置项参考：[prettier.io/docs/options](https://prettier.io/docs/options)
