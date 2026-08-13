# Git Rebase 与 Merge

`merge` 保留真实历史，`rebase` 重写历史让提交线更整洁。本节讲清两者的区别、适用场景和交互式 rebase 的用法。

::: info 适用版本
示例基于 Git 2.2x+，`git switch`、`--autostash`、`--ff-only` 等均为常见稳定特性。
:::

## Merge 与 Rebase 的区别

```text
Merge：保留分叉历史，产生合并提交
main: A ─ B ──────── M
                  ╱
feature:         C ─ D

Rebase：把 feature 的提交“移植”到 main 之后，历史线性
main: A ─ B ─ C' ─ D'
```

| 对比 | Merge | Rebase |
| --- | --- | --- |
| 历史形状 | 有分叉和合并提交 | 线性 |
| 是否重写提交 | 否 | 是（提交哈希变化） |
| 冲突处理 | 一次解决 | 每个提交都可能冲突 |
| 安全共享 | 安全 | 已推送的分支不要 rebase |
| 适合 | 合并已完成的功能 | 本地整理提交、更新分支基线 |

## Merge 的三种方式

```shell
# 普通合并，生成合并提交
git merge feature/xxx

# 只允许快进，不能快进就报错（推荐 CI/受保护分支用）
git merge --ff-only feature/xxx

# 禁用快进，总是生成合并提交（保留“何时合并”信息）
git merge --no-ff feature/xxx
```

## Rebase 基本用法

把当前分支的提交变基到 `main` 最新：

```shell
git switch feature/xxx
git rebase main
```

也可以把提交「移植」到指定基线：

```shell
# 把当前分支的前 3 个提交重新放到 main 上
git rebase --onto main HEAD~3
```

rebase 时临时保存未提交改动：

```shell
git rebase --autostash main
```

## 交互式 Rebase

整理最近 3 个提交：

```shell
git rebase -i HEAD~3
```

编辑器里出现操作列表：

```text
pick a1b2c3d 提交一
squash e4f5g6h 提交二
fixup i7j8k9l 提交三
```

| 命令 | 作用 |
| --- | --- |
| `pick` | 保留提交 |
| `reword` | 保留提交并修改说明 |
| `edit` | 保留提交并暂停修改 |
| `squash` | 合并到上一个提交 |
| `fixup` | 合并到上一个提交并丢弃说明 |
| `drop` | 删除提交 |

## 何时该用 Rebase

- 拉取远程更新：`git pull --rebase`（避免多余的 merge 提交）。
- 功能分支本地整理：多个「wip」提交合并成一个清晰提交。
- 提交信息不清晰：`reword` 修改。

## 何时不该用 Rebase

- 分支已经推送并被他人使用：重写历史会让协作者困惑。
- 需要保留「功能何时合并」的时间线：用 `--no-ff` merge。

## 易错点

::: danger 常见错误
1. 对已推送的共享分支执行 `git rebase` 后强推，覆盖他人提交。
2. `git rebase -i HEAD~3` 分不清方向，把提交顺序改乱。
3. 冲突时直接 `git rebase --abort` 放弃，而不是逐个解决。
4. 把 `git pull --rebase` 当成万能，本地有未提交改动时仍应配合 `--autostash`。
5. 团队约定用 merge，却在共享分支上随意 rebase，历史混乱。
:::

## 验证方式

1. 创建测试分支提交 2 次，`git rebase main` 后 `git log --graph --oneline` 呈线性。
2. `git rebase -i HEAD~2` 把两个提交 squash 成一个，确认 `git log` 只剩一个。
3. 用 `git merge --ff-only` 验证不能快进时会报错。
4. `git pull --rebase` 模拟远程更新，确认无多余合并提交。

## 参考资料

- Pro Git 分支的变基：https://git-scm.com/book/zh/v2/Git-分支-变基
- Git 合并：https://git-scm.com/docs/git-merge
- Git 变基：https://git-scm.com/docs/git-rebase
