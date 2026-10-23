# 启动预算与优化顺序

「终端有点慢」不是可执行的描述。可执行的描述是：**交互 shell 启动 p50 ≤ 200 ms，其中框架 ≤ 20 ms、补全 ≤ 30 ms、版本管理器 ≤ 100 ms、其余 ≤ 50 ms**。有了这四个数，变慢的那天你能立刻指出是哪一段，而不是重装一遍碰运气。

本页把上一章的 746 ms 拆成预算，并给出「按收益/代价排序」的四步优化——顺序错了会白干。

![启动预算的四段构成与优化顺序](../assets/de-budget.svg)

本页判据族 `SBD-A` ~ `SBD-H`，共 8 条。定义表在第五节。

## 一、预算从哪来：先有基线，再有上限

预算不能拍脑袋。正确做法是先测出自己的当前值，再把「占比最大的那一段」定成优化目标：

| 段 | 本机当前 p50 | 建议预算 | 依据 |
| --- | --- | --- | --- |
| 框架自身（空 `.zshrc`） | **14.2 ms** | ≤ 20 ms | 这是不可压缩的底座，超过就是框架选型或版本问题 |
| 补全 `compinit` | **43.7 ms**（58.3 − 14.2） | ≤ 30 ms | `-C` 能到 35.2 ms，留 5 ms 余量给缓存失效那一次 |
| 版本管理器 | **659.6 ms**（673.8 − 14.2） | ≤ 100 ms | `--no-use` 实测 97.9 ms |
| 其余（别名 / 提示符 / 插件） | **28.5 ms** | ≤ 50 ms | 本机现状，说明这一块已经不是瓶颈 |
| **合计** | **746.0 ms** | **≤ 200 ms** | 优化后约 145 ms，留 55 ms 余量 |

::: tip 为什么把「框架自身」也算进预算
它是最容易被忽略的一段：空 `.zshrc` 也要 14.2 ms，其中包含 zsh 自身初始化、`/etc/zshrc` 的少量系统级配置。如果哪天这一段从 14 ms 变成 60 ms，原因通常在**系统升级**或**`/etc` 被改动**，而不是你的配置。
:::

## 二、测量方法：三个必须遵守的口径

```shell
# 口径 1：15 次取中位数（本机单次波动 12~22 ms）
for i in {1..15}; do /usr/bin/time -p zsh -i -c exit; done 2>&1 \
  | grep real | awk '{print $2}' | sort -n | sed -n '8p'

# 口径 2：隔离测量（ZDOTDIR 指向临时目录，不动自己的配置）
mkdir -p /tmp/zdot-base && : > /tmp/zdot-base/.zshrc
ZDOTDIR=/tmp/zdot-base /usr/bin/time -p zsh -i -c exit

# 口径 3：分模式测量（CI 关心的是非交互那条）
/usr/bin/time -p zsh -c exit          # 本机 9.1 ms
/usr/bin/time -p zsh -i -c exit       # 本机 907.6 ms
```

| 口径 | 违反后的后果 |
| --- | --- |
| 取中位数 | 单次读数可能落在缓存冷态，得出「慢了 3 倍」的假结论 |
| 隔离测量 | 边改边测，改坏了也说不清是哪一行 |
| 分模式测量 | 拿交互 shell 的数去解释 CI 的耗时，方向就错了 |

## 三、优化顺序：为什么 nvm 必须排第一

按「收益 ÷ 风险」排序，四步的性价比差一个数量级：

| 顺序 | 动作 | 收益 | 风险 | 代价 |
| --- | --- | --- | --- | --- |
| ① | nvm 初始化加 `--no-use` | **−576 ms** | 极低（只影响新窗口里 `node` 的默认版本） | 需要显式 `nvm use` |
| ② | `compinit` 改 `-C` + 24 小时刷新 | **−23 ms** | 低（放弃每次启动的安全检查） | 一天一次全量检查 |
| ③ | 重型插件改惰性加载 | −0~100 ms（取决于插件） | 中（首次调用慢、补全缺失） | 需要写包装函数 |
| ④ | 收敛别名与函数体量 | **−20 ms 量级** | 极低 | 手工整理 |

::: danger 两个「优化」反而让事情变坏
1. **把 `export` 挪进 `.zshenv`**：交互 shell 确实快了几毫秒，但每个非交互子进程（`make`、CI、编辑器调起的 shell）都开始执行它。省的是你的 3 ms，付的是整条流水线。
2. **为了少加载一个插件而删掉补全**：省 20 ms，代价是每天多敲几百个字符。预算的意义是**有据可依地停手**，不是把所有数字压到最小。
:::

## 四、优化前后对照（本机）

| 项 | 优化前 | 优化后 | 变化 |
| --- | --- | --- | --- |
| 框架自身 | 14.2 ms | 14.2 ms | — |
| 补全 | 43.7 ms | **21.0 ms**（`compinit -C` 命中缓存时） | −22.7 ms |
| 版本管理器 | 659.6 ms | **83.7 ms**（`--no-use` 增量） | −575.9 ms |
| 其余 | 28.5 ms | 28.5 ms | — |
| **合计** | **746.0 ms** | **约 147 ms** | **5.1×** |

优化后的 `~/.zshrc` 关键片段（其余保持不动）：

```zsh
# 版本管理器：只定义函数，不动 PATH
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" --no-use

# 补全：一天一次全量检查，其余跳过
autoload -Uz compinit
if [[ -n ${ZDOTDIR:-$HOME}/.zcompdump(#qN.mh+24) ]]; then
  compinit
else
  compinit -C
fi
```

::: warning `--no-use` 之后「新窗口没有 node」怎么办
两种收口方式，选一种并写进 README：

- **项目内显式**：`cd` 进项目后 `nvm use`（或配合 `direnv` 的 `use node`），版本由 `.nvmrc` 决定。推荐。
- **全局保底**：在 `PATH` 里保留一个系统级 node（`/usr/local/bin/node`）作为「没有项目时」的默认，避免 `node: command not found`。

两种都要避免同一个反模式：**在 `.zshrc` 里写死某个版本目录到 `PATH`**——那等于把 nvm 换成了硬编码，`nvm use` 会失效。
:::

## 五、判据表

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `SBD-A` | 四段预算都有数值并写进 README | 只有总数即不通过 | 按第一节补表 |
| `SBD-B` | 计时取 15 次中位数 | 单次即不通过 | 改测量脚本 |
| `SBD-C` | 测量用 `ZDOTDIR` 隔离 | 边改边测即不通过 | 建临时目录 |
| `SBD-D` | 交互与非交互分别有读数 | 混用即不通过 | 补 `zsh -c` 基线 |
| `SBD-E` | 版本管理器段 ≤ 100 ms | 超过即不通过 | 加 `--no-use` 或惰性 |
| `SBD-F` | 补全段 ≤ 30 ms | 超过即不通过 | 改 `-C` + 24 小时刷新 |
| `SBD-G` | 优化顺序按收益排序执行 | 先删插件后看 nvm 即不通过 | 按第三节顺序重排 |
| `SBD-H` | `--no-use` 后 `node` 的获取方式已写明 | 未写明即不通过 | 补 README「首次需 nvm use」 |

## 预算被打破时：二分定位而不是逐个删

某天启动从 147 ms 变成 420 ms。不要开始删插件，用**二分**：先把 `.zshrc` 折半注释，测；再折半，测。四次之后定位到一段。

```shell
# 用 ZDOTDIR 做「折半」实验，不动本体
mkdir -p /tmp/zdot-half
head -n $(( $(wc -l < ~/.zshrc) / 2 )) ~/.zshrc > /tmp/zdot-half/.zshrc
for i in {1..15}; do ZDOTDIR=/tmp/zdot-half /usr/bin/time -p zsh -i -c exit; done 2>&1 \
  | grep real | awk '{print $2}' | sort -n | sed -n '8p'
```

| 折半结果 | 结论 |
| --- | --- |
| 前半已超预算 | 问题在前半，继续对前半折半 |
| 前半正常、全量超 | 问题在后半 |
| 两半都正常、全量超 | 交互效应：两段各自有条件的加载（如 `if` 判断后才 source） |

第三种情况最费时，但它有个特征：**只在特定目录或特定机器上慢**。这时先怀疑「某个命令在启动时做了网络或磁盘探测」，而不是插件本身。

## 验证方式

```shell
# 优化前/后各跑一次，把两行记进 README
for tag in before after; do
  v=$(for i in {1..15}; do /usr/bin/time -p zsh -i -c exit; done 2>&1 \
      | grep real | awk '{print $2}' | sort -n | sed -n '8p')
  printf '%-7s %s s\n' "$tag" "$v"
done
```

预期：`after` 约为 `before` 的 **1/5**（本机 746 ms → 约 147 ms）。若 `after` 没有明显下降，先确认 `--no-use` 是否真的生效：

```shell
zsh -c 'source "$NVM_DIR/nvm.sh" --no-use; command -v node'   # 应为空或系统 node
```

返回空说明 `PATH` 未被 nvm 改写，`--no-use` 生效；若仍返回 nvm 目录，说明还有另一处（`.zprofile` 或 `.zshenv`）在改 `PATH`。

## 参考资料

- zsh 官方文档：*Completion System*（`compinit -C` 与 `zcompdump` 的刷新条件）
- nvm 官方 README：`--no-use` 的语义与 `nvm use` 的行为
- Apple 文档：`path_helper(8)`（登录 shell 里重排 `PATH` 的来源）
- Brendan Gregg：*Systems Performance*（中位数与 p95/p99 的选择，为什么不用均值）
- 本仓库相邻专题：[shell 启动链路](../ShellStartup/index.md)、[PATH 与运行时版本](../PathAndRuntime/index.md)、[终端工具](../../Efficiency/Terminal/index.md)
