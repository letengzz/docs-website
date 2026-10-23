# 密钥卫生：别让它进环境变量

`export API_KEY=...` 是最顺手的一行，也是最难收回的一行。它的作用域不是「这个终端」，而是**这个 shell 之后产生的每一个子进程**——而子进程的环境变量在进程存活期内对同机任意用户可读。本页用一条本机实测把这件事从「理论上不安全」变成「一条命令就能看到」。

![导出到环境变量的密钥进入每个子进程，并能被 ps 读取](../assets/de-secrets.svg)

本页判据族 `SCT-A` ~ `SCT-H`，共 8 条。定义表在第五节。

## 一、实测：19,793 字节里能搜到明文

```shell
# 起一个带密钥的子进程
DB_PASSWORD='S3cr3t-Token-9f2a' python3 -c 'import time; time.sleep(5)' &
sleep 0.5
ps eww -p $! | grep -c 'S3cr3t-Token-9f2a'     # 1
```

本机结果：`ps eww` 的输出共 **19,793 字节**，其中包含**完整环境变量块**，密钥明文可检索。

两种写法的差别是决定性的：

| 写法 | 子进程里 `'DB_PASSWORD' in os.environ` | 谁能看到 |
| --- | --- | --- |
| `export DB_PASSWORD=...; python3 app.py` | **True** | 该 shell 的所有后代进程 |
| `DB_PASSWORD=... python3 app.py` | **False** | 只有 `python3` 自己，且仅在它的进程环境里 |

实测的第二种：`DB_PASSWORD=... python -c "..."` 启动的子进程输出 **False**——因为它是**命令级变量**，只对那一条命令生效，且不进入 `export` 表；但注意它**仍然**在该进程的环境里可读，只是不再传给它的子进程。

::: danger 「只有我自己用这台机器」
三条反驳都是可验证的：

1. `ps` 对同机所有用户可读（macOS 与 Linux 默认如此），CI 的共享 runner 上尤其如此。
2. 进程崩溃时的转储、APM 的错误上报、`set -x` 的调试日志都会带上环境变量。
3. 只要 dotfiles 进过 Git，`.zshrc` 里的那行就永久留在历史里——`git log -S 'sk-'` 能搜出来，即使后来删掉了。
:::

## 二、四层注入方式，按暴露面排序

| 方式 | 暴露面 | 适用 | 代价 |
| --- | --- | --- | --- |
| 写进 `.zshrc`（`export`） | 所有后代进程 + dotfiles 仓库 | **不推荐** | 泄漏面最大，轮换最麻烦 |
| 项目内 `.env` + 加载库 | 加载它的那个进程树 | 本地开发 | `.env` 必须进 `.gitignore`，且要有 `.env.example` |
| `direnv`（`.envrc`） | 进入目录的那个 shell 及其后代 | 按项目隔离 | 需要 `direnv allow` 的信任步骤 |
| 进程级注入（`op run` / `keychain` / secret manager） | 只有被启动的那一个进程 | 生产与高风险环境 | 多一次网络/解锁调用 |

「按项目隔离」的价值常被低估：同一个 `DATABASE_URL` 在三个项目里指向三个库，写进 `.zshrc` 就只有一个值，于是你会在错误的库上跑迁移。`direnv` 把变量绑定到目录，退出目录即失效。

## 三、`op run` 的形态：模板 + 进程注入

```shell
# .env.tpl（可以进仓库，里面只有引用，没有值）
DATABASE_URL=op://dev-db/teamboard/url
STRIPE_KEY=op://dev-pay/stripe/secret_key

# 启动：值在进程内存里，不落盘、不进 shell 环境
op run --env-file=.env.tpl -- pnpm dev
```

判定的关键差别是**磁盘上有没有明文**。`op run` 的 `.env.tpl` 里只有 `op://` 引用，可以安全进仓库；真正的值在 `op` 的加密库里，解锁后直接注入被启动的那个进程。

同类方案：`aws-vault exec`、`gcloud secrets versions access` + 管道、HashiCorp Vault 的 `vault run`。选型只看一条：**能否做到「进程级注入 + 磁盘无明文」**。

## 四、扫描：把「不许出现」变成一条命令

```shell
# 扫启动文件与仓库（排除 node_modules / .git）
grep -nE 'sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' \
  ~/.zshrc ~/.zprofile ~/.zshenv 2>/dev/null
grep -rnE 'sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}' --include='*' \
  --exclude-dir={node_modules,.git,dist} . 2>/dev/null
```

三条纪律让扫描有用：

1. **扫的是「形态」而不是「已知值」**：形态规则能抓到新泄漏，值比对只能抓到已知的。
2. **扫描要进 pre-commit**：等 push 之后再扫，密钥已经在远端历史里了。
3. **命中后的处置是轮换，不是删除**：删除只改变「以后」，不改变「已经泄漏」。

::: warning 高熵扫描的两个真实误报源
① **测试夹具**：文档与测试里常有 `sk-test-...` 这类假值，加白名单文件而不是关掉规则；② **base64 的随机串**：`package-lock.json` 的 `integrity` 字段熵很高，必须排除锁文件与 `dist`。
:::

## 五、轮换：泄漏之后做什么

「删掉那一行」是最常见也最没用的处置。密钥的生命周期里，**暴露的那一刻就已经结束**——之后的动作不是「清理」，而是「作废 + 换新 + 证明旧的不能用」。

四步，顺序不能换：

| 步 | 动作 | 判据 | 不能省的后果 |
| --- | --- | --- | --- |
| 1 | 先签发新密钥并完成部署 | 新密钥能通过一次真实调用 | 先吊销会导致服务直接不可用 |
| 2 | 吊销旧密钥 | 用旧密钥调用返回 401 | 只删文件不吊销等于没换 |
| 3 | 清理所有存放位置 | 见下面的九位置清单 | 某个 CI 变量里还留着旧的 |
| 4 | 记录与复盘动作 | 变更记录里有时间、位置、影响面 | 下次同样位置再泄漏一次 |

**九位置清单**（按「最容易漏」排序）：启动文件 → 项目 `.env` → CI 的 secret 变量 → 容器编排的 `secrets` / `env_file` → 云厂商控制台的环境变量 → 部署机器的 systemd unit → 应用配置中心 → 笔记与聊天记录 → 团队共享文档。

第 3 步的判定不能靠「我记得都改了」，要靠一条命令：把旧密钥的前 8 个字符当搜索词，扫一遍所有可能位置：

```shell
# 只打印「哪个文件命中」，不打印密钥本身
grep -rl --exclude-dir={node_modules,.git,dist} 'OLD_KEY_PREFIX' . ~ 2>/dev/null | head -20
```

::: danger 「我把它从 Git 历史里删了」
历史可以被重写（`git filter-repo`），但**已经被 clone 的副本收不回来**，CI 缓存、构建产物、别人的本地仓库、平台的 fork 都算。凡密钥进过远端仓库，正确假设是「已公开」。

处置顺序因此固定：**先吊销，再考虑要不要重写历史**。反过来做（先重写历史再吊销）会给你一种「已经处理完」的错觉，而旧密钥仍然有效。
:::

## 六、判据表

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `SCT-A` | 启动文件中无密钥形态字面量 | 有即不通过 | 移出到 `.envrc` 或密钥管理器 |
| `SCT-B` | `.env` 在 `.gitignore` 中，且存在 `.env.example` | 缺失即不通过 | 补两个文件 |
| `SCT-C` | 生产启动用进程级注入 | 用 `export` 即不通过 | 改 `op run` / secret manager |
| `SCT-D` | `ps eww -p <pid>` 中搜不到密钥 | 能搜到即不通过 | 改命令级变量或注入方式 |
| `SCT-E` | pre-commit 有扫描钩子 | 无钩子即不通过 | 加 `gitleaks` / 自写 grep 钩子 |
| `SCT-F` | 泄漏过的密钥已轮换并有记录 | 只删未换即不通过 | 轮换并写进变更记录 |
| `SCT-G` | `.envrc` 需 `direnv allow` 才生效 | 自动加载即不通过 | 不提交 `allow` 授权 |
| `SCT-H` | 密钥不出现在任何日志输出中 | 出现即不通过 | 脱敏中间件 + 关闭 `set -x` |

## 验证方式

```shell
# 1) 进程可见性（应当搜不到）
( DB_PASSWORD='probe-9f2a' sleep 3 & ); sleep 0.5
ps eww -Ao pid,command | grep -c 'probe-9f2a'      # 期望 0（用命令级变量）

# 2) 启动文件扫描（应当无输出）
grep -nE 'sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE' ~/.zshrc ~/.zprofile ~/.zshenv 2>/dev/null

# 3) 仓库扫描
grep -rnE 'sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}' --exclude-dir={node_modules,.git,dist} . 2>/dev/null | head

# 4) 历史检查：曾经提交过就一定会被搜到
git log --oneline -S 'sk-' --all | head
```

预期：第 1 步为 `0`；第 2、3 步无输出；第 4 步为空。**第 4 步不为空时，唯一的正确处置是轮换密钥**——历史可以被重写，但已被读取的密钥不能被收回。

## 参考资料

- 1Password 官方文档：*CLI `op run`* 与 `op://` 引用语法
- direnv 官方文档：*Standard Library*（`.envrc` 的 `allow` 信任模型、`layout` 函数）
- git 官方文档：`git log -S`（pickaxe 检索）、`git filter-repo`（历史重写）
- gitleaks 官方文档：规则集与 `--baseline-path`
- OWASP：*Secrets Management Cheat Sheet*
- 本仓库相邻专题：[密钥治理](../../../Ops/SecurityHardening/SecretGovernance/index.md)、[dotfiles](../Dotfiles/index.md)、[环境可复现](../Reproducibility/index.md)
