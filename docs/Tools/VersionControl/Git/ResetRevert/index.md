# Git Reset 与 Revert

撤销操作分两种：`reset` 移动分支指针（改变历史），`revert` 生成反向提交（保留历史）。选错工具会带来灾难，本节给出完整决策表。

::: info 适用版本
以下命令在 Git 2.2x+ 均可用；`git restore` 用于工作区/暂存区恢复。
:::

## Reset 的三种模式

```shell
# soft：只移动 HEAD，暂存区和工作区都不动
git reset --soft HEAD~1

# mixed（默认）：移动 HEAD 并清空暂存区，工作区不动
git reset HEAD~1

# hard：移动 HEAD，暂存区和工作区全部回到目标状态
git reset --hard HEAD~1
```

| 模式 | HEAD | 暂存区 | 工作区 | 典型用途 |
| --- | --- | --- | --- | --- |
| `--soft` | 移动 | 保留 | 保留 | 撤销 commit，重新组织暂存 |
| `--mixed` | 移动 | 清空 | 保留 | 撤销 commit 和 add |
| `--hard` | 移动 | 清空 | 清空 | 彻底丢弃改动（危险） |

## 什么时候用 Reset

- 提交还没有推送到远程：`git reset --soft HEAD~1` 重新提交。
- 不小心 `git add` 多了文件：`git restore --staged <file>`。
- 本地实验想彻底回退：`git reset --hard <commit>`。

```shell
# 撤销上一次提交但保留改动，重新整理
git reset --soft HEAD~1

# 撤销最近 3 个提交（保留改动）
git reset --mixed HEAD~3

# 回到指定提交（彻底）
git reset --hard a1b2c3d
```

## 什么时候用 Revert

提交已经推送到远程、可能被他人使用：**不要 reset，用 revert**。

```shell
# 生成一个“反向提交”，撤销指定提交的内容
git revert a1b2c3d

# 撤销最近一次提交
git revert HEAD

# 连续撤销多个提交（按顺序生成多个反向提交）
git revert --no-edit HEAD~2..HEAD

# 只生成反向改动到工作区，不自动提交
git revert --no-commit a1b2c3d
```

Revert 的优点是历史完整：所有人都能看到「这个改动被撤销了」，适合共享分支。

## 撤销已合并的提交

用 revert 而不是 reset：

```shell
git revert -m 1 <merge-commit>
```

`-m 1` 表示保留合并的第一父分支（通常是 main）。如果不加 `-m`，Git 会拒绝 revert 合并提交。

## 恢复误删的工作区文件

```shell
# 把工作区文件恢复到 HEAD 状态
git restore <file>

# 把暂存区文件恢复到 HEAD 状态（相当于 unstage）
git restore --staged <file>
```

## 决策表

| 场景 | 推荐操作 |
| --- | --- |
| 提交未推送，想改提交信息 | `git commit --amend` |
| 提交未推送，想重新组织 | `git reset --soft HEAD~n` |
| 误 add 文件 | `git restore --staged <file>` |
| 提交已推送，要撤销 | `git revert <commit>` |
| 撤销合并提交 | `git revert -m 1 <merge>` |
| 丢弃未提交改动 | `git restore <file>` 或 `git reset --hard`（谨慎） |
| 找回误删的提交 | `git reflog` + `git reset --hard <hash>`（未 gc 前） |

## 易错点

::: danger 常见错误
1. 已推送的提交用 `reset --hard` 然后强推，覆盖他人工作。
2. `reset --hard` 当成普通撤销，未提交的工作区改动全部丢失。
3. 把 `revert` 理解成「回到某个版本」，它只是生成反向提交，后续提交仍然保留。
4. revert 合并提交不加 `-m`，命令直接报错。
5. 忘记 `git reflog` 这个「后悔药」，误删后不知所措。
:::

## 验证方式

1. 在测试仓库提交 3 次，`git reset --soft HEAD~2` 后 `git log` 只剩 1 个提交、`git status` 显示 2 个提交的改动。
2. 对已推送提交执行 `git revert`，`git log` 多出一个反向提交。
3. 测试 `git revert -m 1` 撤销合并提交。
4. 误删文件后用 `git restore` 恢复。
5. `git reflog` 查看操作记录，用 `git reset --hard <hash>` 找回误删提交。

## 参考资料

- Git Reset 文档：https://git-scm.com/docs/git-reset
- Git Revert 文档：https://git-scm.com/docs/git-revert
- Pro Git 重置揭秘：https://git-scm.com/book/zh/v2/Git-工具-重置揭密
