# Git Stash 暂存

`git stash` 用于「手头工作没做完，但需要切换分支/拉取更新」的场景：把未提交的改动暂时收起来，之后随时恢复。

::: info 适用版本
以下命令在 Git 2.2x+ 均可用；`git stash push -m` 是推荐的显式写法。
:::

## Stash 解决什么问题

典型场景：

1. 正在开发 `feature/login`，线上出了 bug 需要切到 `hotfix`。
2. 想 `git pull` 拉取更新，但本地有未提交改动。
3. 想试验一个方案，不想污染当前工作区。

## 基本用法

```shell
# 保存当前未提交改动（工作区 + 暂存区）
git stash push -m "登录功能进行中"

# 查看 stash 列表
git stash list

# 恢复最近一次 stash 并删除记录
git stash pop

# 恢复但不删除记录
git stash apply

# 删除指定 stash
git stash drop stash@{1}

# 清空所有 stash
git stash clear
```

## 只暂存部分内容

```shell
# 只暂存指定文件
git stash push -m "只存配置" -- src/config.ts

# 只暂存已 add 的内容
git stash push --staged -m "只存暂存区"
```

## 从 Stash 创建分支

恢复 stash 时所在分支已经变化，直接 `pop` 可能冲突：

```shell
git stash branch fix/restore-config
```

该命令会以 stash 保存时的基线创建新分支并恢复改动，推荐用于「忘了 stash 来自哪个分支」的情况。

## 查看 Stash 内容

```shell
git stash show -p stash@{0}
git stash show --stat stash@{0}
```

## Stash 与 Rebase/Merge 配合

```shell
# 拉取远程更新时自动暂存未提交改动
git pull --rebase --autostash

# 变基时自动暂存
git rebase --autostash main
```

## 易错点

::: danger 常见错误
1. `git stash` 默认不包含未跟踪文件（untracked），新文件会被留在工作区；需要时用 `git stash -u`。
2. `git stash pop` 冲突后，stash 记录不会自动删除，需要手动解决后 `git stash drop`。
3. 把 stash 当长期存储，堆积几十条，恢复时根本分不清。
4. `git stash clear` 会永久删除所有 stash，不可恢复。
5. 忽略 `-m` 写说明，列表里全是 `WIP on ...`。
:::

## 验证方式

1. 修改一个文件后 `git stash push -m "测试"`，`git status` 变干净。
2. `git stash list` 能看到 `stash@{0}`。
3. `git stash pop` 后改动恢复，`git stash list` 为空。
4. 新建未跟踪文件，测试 `git stash -u` 与不带 `-u` 的区别。
5. 用 `git stash branch` 在错误分支上恢复，确认不冲突。

## 参考资料

- Git Stash 文档：https://git-scm.com/docs/git-stash
- Pro Git 贮藏与清理：https://git-scm.com/book/zh/v2/Git-工具-贮藏与清理
