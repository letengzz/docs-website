# 常见问题与分诊

环境类的求助有一个共同特征：**描述的是症状，不是位置**。「跑不起来」「版本不对」「终端卡」这三句话对应十几个不同根因，而排查顺序错了会连改三处、把问题变成「三个问题」。本页给一张分诊表：从症状直接跳到**一条判定命令**，命令的输出决定去向。

![六个症状与对应的最短判定路径](../assets/de-faq.svg)

本页判据族 `ENQ-A` ~ `ENQ-H`，共 8 条。定义表在第五节。

## 一、症状分诊表（十行）

| 症状 | 一条判定命令 | 输出说明 | 去哪一页 |
| --- | --- | --- | --- |
| `command not found`，但文件存在 | `ls -l "$(command -v -p X 2>/dev/null)"`；再看 `echo $PATH` | 路径不在 `PATH` 里 → 补 PATH；在但无执行权限 → `chmod +x` | [PATH 与运行时](../PathAndRuntime/index.md) |
| `node -v` 与文档不一致 | `zsh -c 'command -v node'; zsh -i -c 'command -v node'` | 两行不同 → shell 分层问题，不是装错 | [PATH 与运行时](../PathAndRuntime/index.md) |
| 终端每开窗口卡一秒 | 15 次 `zsh -i -c exit` 取 p50 | > 300 ms → 先拆四段 | [启动预算](../StartupBudget/index.md) |
| 换机器报 `ModuleNotFoundError` | `env -i PATH=/usr/bin:/bin zsh -c 'X --version'` | `NOT_FOUND` → 依赖了环境变量 | [环境可复现](../Reproducibility/index.md) |
| 容器里报 `Module did not self-register` | `docker compose exec app ls -l node_modules/.bin` | 属主/架构不对 → 挂了宿主目录 | [环境可复现](../Reproducibility/index.md) |
| 改了 `.zshrc` 但 `which` 没变 | `hash -r && command -v X` | `hash` 缓存未失效 | [PATH 与运行时](../PathAndRuntime/index.md) |
| dotfiles 改完像没生效 | `ls -l ~/.zshrc` 看是不是 `->` | 是拷贝模式 → 未重装；是链接 → 改错文件 | [dotfiles](../Dotfiles/index.md) |
| 密钥被扫出来 | `git log --oneline -S '<key-prefix>' --all` | 有输出 → 已在历史里，必须轮换 | [密钥卫生](../Secrets/index.md) |
| 页面能开但不热更新 | 浏览器控制台看 `ws://` 地址 | 该端口未转发 | [远程开发](../RemoteDev/index.md) |
| JWT 一签发就过期 | `date -u; ssh host date -u` | 时间差 > 30 s → 校时 | [远程开发](../RemoteDev/index.md) |

## 二、十二问（按被问频率排序）

1. **为什么我 `node` 装了却 `command not found`？** 装的位置不在 `PATH`，或 `PATH` 被后加载的文件覆盖。用 `zsh -i -c 'echo $PATH'` 看真实值。
2. **`nvm` 装了但新窗口要手动 `nvm use`？** 因为加了 `--no-use`，这是有意为之（省 576 ms）。把 `nvm use` 写进项目 `cd` 钩子或 `.envrc`。
3. **`.zshrc` 里的别名在脚本里不生效？** 脚本是非交互 shell，不读 `.zshrc`。用函数放进 `PATH` 里的脚本，或显式 `source`。
4. **为什么 `PATH` 会重复？** 多处 `PATH=$PATH:...` 叠加，且每次 `source` 再加一遍（实测 1 次 10 项、5 次 22 项）。用 `typeset -U path`。
5. **终端启动 700 ms 算慢吗？** 与基线比：空配置 14 ms，说明 700 ms 里 95% 是你的配置。本机 660 ms 来自 nvm。
6. **容器里为什么读不到宿主的环境变量？** 容器只继承 `docker run -e` / compose `environment` / `env_file` 显式传入的变量，宿主的 `export` 不进容器。
7. **`--frozen-lockfile` 报错怎么办？** 说明 `package.json` 与锁文件不一致。本地跑一次不带该参数的安装并提交锁文件，**不要**在 CI 里去掉这个参数。
8. **`devcontainer` 里 `pnpm` 版本不对？** 容器内没跑 `corepack enable`，或镜像自带旧版 corepack。`postCreateCommand` 里显式启用。
9. **为什么 `ps eww` 能看到我的密钥？** 因为 `export` 的变量在进程环境里，`ps` 对同机用户可读。改进程级注入。
10. **dotfiles 用 symlink 还是 copy？** 单人多机用 symlink（改一次全生效，注意写穿）；多环境差异大用 copy（需对账脚本）。
11. **`env -i` 跑不通是不是脚本有问题？** 不一定。它是**故意**剥掉环境的实验，用来暴露隐式依赖。跑不通说明脚本该显式声明依赖。
12. **`make bootstrap` 第二遍改了文件怎么办？** 说明有步骤不幂等（常见是无条件 `mv`/`cp`/`curl`）。按「已正确则跳过」改造。

## 三、五条听起来对、实际会带偏的建议

::: danger 这五条都会被读数推翻
1. **「重装一遍试试」**——重装会同时改变 PATH、版本、全局包三个变量，问题消失了也说不清为什么，下次照样复发。先 `command -v`。
2. **「把 `export` 全挪进 `.zshenv` 就好了」**——那会让 CI 与非交互子进程都执行它，属于把问题扩大。
3. **「终端慢就删插件」**——本机 88% 的成本是 nvm，删插件省不到 30 ms。先量四段。
4. **「用 Docker 就一定可复现」**——容器锁不住宿主挂进去的 `node_modules`，也锁不住你自己的 `PATH`。
5. **「密钥删掉就安全了」**——删除只改变「以后」，`git log -S` 仍能搜到历史。唯一正确处置是轮换。
:::

## 四、上线前自查（14 项）

| # | 自查项 | 命令 |
| --- | --- | --- |
| 1 | 架构与系统版本已记录 | `uname -m` |
| 2 | 交互启动 p50 已记录 | 15 次计时取中位 |
| 3 | 非交互启动 p50 已记录 | `zsh -c exit` 计时 |
| 4 | `PATH` 无重复 | `... \| sort \| uniq -d` |
| 5 | 两种 shell 的 `command -v` 一致 | 对比两行 |
| 6 | 版本矩阵写进 README | 人工核对 |
| 7 | `.nvmrc` 与 `node -v` 一致 | 对比 |
| 8 | 锁文件进仓库 | `git ls-files \| grep lock` |
| 9 | bootstrap 幂等 | 连跑两遍 |
| 10 | 启动文件无密钥形态 | `grep -nE` |
| 11 | `.env` 已 ignore 且有 example | `git check-ignore .env` |
| 12 | 容器内版本一致 | `compose run node -v` |
| 13 | 时钟偏差 ≤ 5 s | `date -u` 对比 |
| 14 | 负向断言可造且确实失败 | 按[实战](../Practice/index.md)第四节 |

## 五、三类人的最短路径

分诊表是按症状排的，但不同处境的人该走的顺序不同。三条路径各自只有 4~5 步，跳步的代价写在同一行里。

### ① 新人第一天：先证明「机器能用」

| 序 | 动作 | 期望 | 跳过的代价 |
| --- | --- | --- | --- |
| 1 | `uname -m` 与文档比对 | 与镜像架构一致 | 后面所有装依赖的失败都可能是架构错 |
| 2 | `zsh -i -c 'command -v node'` | 有路径 | 没有就先装版本管理器，别急着 `pnpm install` |
| 3 | `node -v` 与 `.nvmrc` 比对 | 一致 | 不一致会让你在错误版本上调半天 API |
| 4 | `make bootstrap` | 打印四行版本矩阵 | 跳过自检，等于不知道装成功没有 |
| 5 | `curl 127.0.0.1:8080/health` | `ok` | 跳过会带着「服务没起来」的状态去调业务 |

### ② 换机器：先比差异，再装东西

不要从头装。先把旧机器的四行体检结果拿过来，在新机器上跑同样四条，**差异处就是你要处理的地方**：

```shell
uname -m
zsh -c 'command -v node'; zsh -i -c 'command -v node'
echo "$PATH" | tr ':' '\n' | sort | uniq -d | wc -l
command -v pnpm python3 docker
```

差异通常只有两三处，装完再跑一遍，直到四行一致。**「装完就能跑」是运气，「四行一致」才是判据。**

### ③ 接手老项目：先定位「谁在管版本」

老项目最麻烦的不是依赖多，而是**版本由谁决定说不清**：可能有 `.nvmrc`、可能有 `.tool-versions`、可能某个脚本里写死了路径。三步定位：

| 序 | 动作 | 解读 |
| --- | --- | --- |
| 1 | `ls -a` 中找 `nvmrc` / `tool-versions` / `node-version` | 有哪个文件就跟哪个，多个文件要确认优先级 |
| 2 | `grep -rn 'PATH=' Makefile scripts/ 2>/dev/null` | 脚本里写死的路径会覆盖 shell 的版本 |
| 3 | `git log -1 --format=%cd -- .nvmrc` | 这个版本是什么时候定的，之后依赖有没有升过 |

第 3 步经常被忽略，但它能解释一类怪现象：`.nvmrc` 三年前定的 node 18，而依赖半年前升到了要求 node 20 的版本——两边都对，只是没人同步。

## 六、判据表

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `ENQ-A` | 每个症状都有对应判定命令 | 靠猜即不通过 | 按分诊表补 |
| `ENQ-B` | 排查顺序是「先量后改」 | 先重装即不通过 | 改 `command -v` 起步 |
| `ENQ-C` | 区分交互与非交互两种 shell | 混用即不通过 | 分模式测量 |
| `ENQ-D` | 密钥问题按「轮换」处置 | 只删不换即不通过 | 轮换并记录 |
| `ENQ-E` | 容器问题先查挂载 | 先改代码即不通过 | 查 `volumes` |
| `ENQ-F` | 幂等失败定位到具体步骤 | 整体重跑即不通过 | 拆目标重试 |
| `ENQ-G` | 自查表 14 项全部有命令 | 有无命令项即不通过 | 补命令 |
| `ENQ-H` | 结论带读数（毫秒 / 项数 / 版本） | 只说「变快了」即不通过 | 补前后读数 |

## 一次完整演练：从报错到定位（五分钟）

把前面所有判据串成一次真实的排查。假设症状是「本地跑测试报 `Cannot find module`」，而同事机器上正常：

```shell
# ① 先确认是「哪个 node」在跑测试
zsh -c 'command -v node'; zsh -i -c 'command -v node'
#   两行不同 → 停在这里，先把版本统一（见 PATH 与运行时版本）

# ② 再确认依赖是「哪个 node_modules」
node -p "process.version"; node -p "require.resolve('vitest/package.json')"
#   路径落在别的目录 → 有嵌套安装或全局包，删掉重装

# ③ 再确认锁文件有没有被动过
git status --porcelain pnpm-lock.yaml
#   非空 → 别人改了锁文件或你本地装过新包，先还原再装

# ④ 最后用空环境复跑一次，排除 shell 配置的影响
env -i PATH=/usr/bin:/bin HOME="$HOME" pnpm test 2>&1 | head -5
```

四步里，①②③ 各自对应一类根因（版本 / 安装位置 / 依赖图），④ 是最后的「是不是我的 shell 在捣鬼」。**顺序不能换**：先改依赖再查版本，最常见的结局是重装了三次依赖而版本依旧是错的。

## 验证方式

```shell
# 把分诊表里能自动判的五条跑一遍
zsh -c 'command -v node'; zsh -i -c 'command -v node'          # 应相同
echo "$PATH" | tr ':' '\n' | sort | uniq -d                     # 应为空
grep -nE 'sk-[A-Za-z0-9]{16,}' ~/.zshrc 2>/dev/null             # 应无输出
env -i PATH=/usr/bin:/bin zsh -c 'command -v node || echo NOT_FOUND'
date -u +%s; ssh -o ConnectTimeout=3 host date -u +%s 2>/dev/null || echo skip
```

预期：第一条两行相同；第二条空；第三条无输出；第四条 `NOT_FOUND`（正常）；第五条两数差 ≤ 5。

## 参考资料

- POSIX.1-2017：*Command Search and Execution*
- zsh 官方文档：*Startup Files*、*Builtins*（`hash` / `rehash`）
- Docker 官方文档：*Environment variables*（`-e` / `env_file` / 容器不继承宿主 `export`）
- Corepack 官方文档：`packageManager` 与 `corepack enable`
- 本仓库相邻专题：[四层边界](../Overview/index.md)、[环境可复现](../Reproducibility/index.md)、[实战](../Practice/index.md)
