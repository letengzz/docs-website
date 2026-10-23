# dotfiles：符号链接与写穿

把 dotfiles 纳入 Git 之后，问题从「怎么备份」变成了「谁是真源」。符号链接和拷贝两种装法各有一次「我以为改了、其实没改」或「我以为没改、其实改了」的时刻，而这两种时刻都发生在**你已经忘了这个文件是链过去的**之后。

本页的实测结论只有一句：**符号链接模式检出 0 处漂移，不是因为干净，而是因为改动直接写穿了仓库**。

![dotfiles 仓库与 HOME 的两种绑定方式，以及各自的漂移行为](../assets/de-dotfiles.svg)

本页判据族 `DOT-A` ~ `DOT-H`，共 8 条。定义表在第六节。

## 一、两种装法，两种失效模式

| 维度 | 符号链接（symlink） | 拷贝（copy） |
| --- | --- | --- |
| 真源 | 仓库 | HOME（仓库只是模板） |
| 仓库改文件 | HOME 立刻看到 | HOME 保持旧值，直到重装 |
| HOME 改文件 | **直接改到仓库**（写穿） | 仓库不知道，漂移 |
| 本页实测（20 文件、改 2 处） | 检出 **0 处**漂移 / **3.56 ms** | 检出 **2 处**漂移 / **1.88 ms** |
| 主要风险 | 临时手改被 `git add -A` 提交 | 双向漂移、下次安装被覆盖 |
| 适合 | 单人、多机、配置稳定 | 多环境差异大、需要本机特化 |

### 为什么 symlink 的「0 处漂移」是陷阱

测试做法：仓库 20 个文件、HOME 下 20 个同名符号链接；然后①改仓库里 `.rc3`，②改 HOME 里 `.rc7`。检测脚本遍历 20 个文件，比对链接目标与内容。

结果是 **0 处漂移**——因为 `.rc7` 的「改动」实际写进了仓库文件本体（同一个 inode），两侧永远一致。检测脚本什么都没发现，而**仓库的 `git status` 已经脏了**。

::: danger 写完 `~/.zshrc` 顺手 `git add -A` 会把什么带进去
symlink 模式下，你在 HOME 里做的任何临时试验（一个 `alias tmp=...`、一段调试用的 `export DEBUG=1`）都直接落在仓库工作区。`git add -A && git commit -m "update"` 会把它一起提交。

**这条纪律必须写进 README**：symlink 模式下，`git commit` 前先 `git diff` 看一遍，且禁止 `-A` 盲提交。
:::

### 拷贝模式的漂移长什么样

同一测试里拷贝模式检出 2 处：`.rc3`（仓库改了、HOME 没跟上）与 `.rc11`（HOME 改了、仓库不知道）。这两种漂移的处置方向**相反**：

- 仓库新、HOME 旧 → 重跑安装（或 `diff` 后手工合并）。
- HOME 新、仓库旧 → 决定是否把本机特化回写成仓库的「主机叠加层」。

不写清方向，`diff` 一多就会变成「全都覆盖一遍」，而覆盖会静默丢掉本机特化。

## 二、一个能判断方向的对账脚本

判据要能回答「哪边新、改哪边」，所以脚本输出的不是「不一致」而是三类：

```python
#!/usr/bin/env python3
# 用法: python3 dotcheck.py ~/.dotfiles ~
import os, sys, hashlib

repo, home = os.path.realpath(sys.argv[1]), os.path.realpath(sys.argv[2])

def digest(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]

for name in sorted(os.listdir(os.path.join(repo, "zsh"))):
    src = os.path.join(repo, "zsh", name)
    dst = os.path.join(home, name)
    if not os.path.exists(dst):
        print(f"MISSING   {name}   HOME 没有这个文件，重跑安装")
        continue
    if os.path.islink(dst):
        # 关键：两侧都要 realpath 归一化
        if os.path.realpath(dst) != src:
            print(f"RELINK    {name}   链接指向了别处：{os.path.realpath(dst)}")
        continue
    if digest(dst) != digest(src):
        newer = "HOME" if os.path.getmtime(dst) > os.path.getmtime(src) else "REPO"
        print(f"DRIFT     {name}   较新的一侧是 {newer}，先 diff 再决定方向")
```

::: warning macOS 上一个把 20 个链接全判成漂移的坑
第一次跑这个脚本时，20 个符号链接**全部**被判成「指向别处」。原因不在链接，在路径：`tempfile.mkdtemp()` 返回 `/var/folders/...`，而 `os.path.realpath()` 把它解析成 `/private/var/folders/...`——**同一目录的两个名字**。脚本只归一化了 HOME 一侧，另一侧留着 `/var` 前缀，于是永久不相等。

修法只有一句：**比较前两边都 `realpath`**。这个坑在任何「比较两个路径是否相同」的脚本里都会复现，包括备份校验与容器挂载检查。
:::

## 三、分层：每个文件只放一类东西

dotfiles 仓库的价值不在「把所有配置塞进来」，而在**每个文件的职责边界清楚**，这样换 shell、换机器、上 CI 时才知道该带走什么。

| 文件 | 什么时候执行 | 只放这些 | 绝不放这些 |
| --- | --- | --- | --- |
| `~/.zshenv` | 所有模式（含非交互） | `PATH` 兜底、`EDITOR` | 密钥、版本管理器初始化、提示符 |
| `~/.zprofile` | 登录 shell | `brew shellenv`、登录期一次性环境 | 别名、补全 |
| `~/.zshrc` | 交互 shell | 别名、补全、提示符、版本管理器 | 密钥、构建期需要的变量 |
| `~/.zlogin` | 登录后 | 欢迎信息、`tmux` 自动挂载 | 任何会被脚本依赖的东西 |
| `~/.config/<tool>/` | 由工具自己读 | 工具配置（`git`、`gh`、`starship`） | 机器相关的绝对路径 |
| 项目内 `.envrc` | 进入目录（direnv） | 项目专属变量 | 全局别名 |

**判断一个 `export` 该放哪，只问一句**：非交互子进程（`make`、`CI`、编辑器调起的 shell）需不需要它？需要 → `.zshenv`；不需要 → `.zshrc` 或项目内 `.envrc`。

## 四、安装：一次、幂等、可回滚

```shell
#!/bin/sh
# install.sh —— 跑两遍结果一样，失败可重入
set -eu
REPO="${DOTFILES:-$HOME/.dotfiles}"

link() {                       # link <仓库内相对路径> <HOME 内相对路径>
  src="$REPO/$1"; dst="$HOME/$2"
  [ -e "$src" ] || { echo "skip: $1 不存在"; return 0; }
  mkdir -p "$(dirname "$dst")"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    echo "ok:   $2 已链接"; return 0          # 幂等的关键：已正确就跳过
  fi
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    mv "$dst" "$dst.bak.$(date +%Y%m%d%H%M%S)"  # 不覆盖，先备份
    echo "bak:  $2 已备份"
  fi
  ln -sfn "$src" "$dst"; echo "link: $2"
}

link zsh/.zshenv    .zshenv
link zsh/.zshrc     .zshrc
link git/.gitconfig .gitconfig
```

三个要点，缺一个就会在第二次运行时出问题：

1. **已正确则跳过**：没有这一步，第二遍会重复 `mv` 出 `.bak` 文件。
2. **非链接文件先备份再替换**：否则第一次安装就永久丢掉原配置。
3. **`ln -sfn` 而不是 `ln -s`**：`-n` 让「目标是已存在的符号链接目录」时替换链接本身而不是在里面建链接（这个坑在 `~/.config/nvim` 这类目录上必现）。

::: danger `stow` 的默认行为会「接管」整个目录
`stow zsh` 会把 `zsh/` 下**所有**文件链到父目录。仓库里多一个 `zsh/.zshrc.local`，它就会链到 `~/.zshrc.local`——即使你并不想让它生效。先 `stow -n -v zsh`（dry-run）看清单，再执行。
:::

## 五、回滚：三种粒度

| 粒度 | 命令 | 适用 |
| --- | --- | --- |
| 单个文件 | `git checkout HEAD~1 -- zsh/.zshrc && ./install.sh` | 改坏了一个别名 |
| 整个快照 | `git tag dot-2026-10 && git checkout dot-2026-10 -- .` | 升级框架后大面积异常 |
| 环境回退 | `git worktree add ~/.dotfiles-old dot-2026-10` | 需要新旧并存对比 |

第三种最少用但最有用：`worktree` 让旧版本完整存在于另一个目录，`HOME` 里的链接改指过去就完成回退，不用 `checkout` 打断当前工作区。

## 六、判据表

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `DOT-A` | 安装模式（symlink / copy）在 README 中写明 | 未写明即不通过 | 补 README 一节 |
| `DOT-B` | `install.sh` 连跑两遍，第二遍无 `bak` 产生 | 产生即不通过 | 加「已正确则跳过」分支 |
| `DOT-C` | 安装前对已存在的非链接文件做备份 | 直接覆盖即不通过 | 补 `mv` 到 `.bak.<时间戳>` |
| `DOT-D` | 对账脚本两侧都做 `realpath` 归一化 | 只归一化一侧即不通过 | 按第二节修 |
| `DOT-E` | `.zshenv` 中无密钥、无版本管理器 | 有即不通过 | 移到 `.zshrc` / `.envrc` |
| `DOT-F` | symlink 模式下 `git commit` 前必看 `git diff` | 盲用 `-A` 即不通过 | 写进 README 纪律 |
| `DOT-G` | 目录型配置用 `stow -n` / `ln -sfn` 预演 | 直接 `stow` 即不通过 | 先 dry-run |
| `DOT-H` | 存在可执行的回滚粒度（单文件 / 快照 / worktree） | 只能「重装」即不通过 | 补 tag 与回滚命令 |

## 验证方式

```shell
# 1) 幂等：连跑两遍，第二遍不应出现 bak 行
./install.sh; ./install.sh | grep -c '^bak:' || true    # 期望 0

# 2) 链接指向（应全部指向仓库内路径）
ls -l ~/.zshrc ~/.gitconfig | awk '{print $9, $10, $11}'

# 3) 漂移（用本页第二节的脚本，两侧 realpath 归一化）
python3 dotcheck.py ~/.dotfiles "$HOME"    # 期望无 DRIFT / RELINK 行

# 4) 写穿检查：在 HOME 改一个字符，仓库应当立刻 dirty
echo '# probe' >> ~/.zshrc && git -C ~/.dotfiles status --porcelain
git -C ~/.dotfiles checkout -- . && echo restored
```

预期：第 1 步输出 0；第 2 步每行都是 `link -> /Users/.../.dotfiles/...`；第 3 步为空；第 4 步 `git status` 显示 `.zshrc` 被修改——**这一步是故意让仓库变脏的**，用来确认你理解了写穿，测完立刻还原。

## 参考资料

- GNU Stow 官方手册：*Invoking Stow*（`-n` dry-run、`--adopt`、目录折叠）
- git 官方文档：`git worktree`、`git checkout <tree-ish> -- <path>`
- zsh 官方文档：*Files*（`.zshenv` / `.zprofile` / `.zshrc` / `.zlogin` 的执行时机）
- direnv 官方文档：`.envrc` 与 `direnv allow` 的信任模型
- 本仓库相邻专题：[shell 启动链路](../ShellStartup/index.md)、[配置同步](../../IDE/ConfigSync/index.md)、[密钥卫生](../Secrets/index.md)
