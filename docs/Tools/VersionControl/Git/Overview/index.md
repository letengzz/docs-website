# Git 进阶概述

Git 是当前最主流的分布式版本控制系统。基础篇解决「怎么提交、怎么回退」，进阶篇解决「分支怎么管理、历史怎么整理、多人怎么协作」。本节先建立进阶所需的底层认知。

::: info 版本现状（2026-08 核对）
Git 当前稳定版为 **2.55.x**（2.55.0 于 2026-06 发布）。以下命令均基于 Git 2.2x+，`git switch` / `git restore` 等命令从 2.23 起可用。
:::

## Git 的三个区域

进阶操作前必须清楚三个区域的关系：

```text
工作区（Working Tree） → 暂存区（Index/Staging） → 本地仓库（Repository） → 远程仓库（Remote）
     git add                 git commit                git push
```

| 区域 | 说明 | 相关命令 |
| --- | --- | --- |
| 工作区 | 你看到的文件 | `git status`、`git diff` |
| 暂存区 | 已 `git add` 待提交的内容 | `git add`、`git restore --staged` |
| 本地仓库 | 已提交的历史（对象库） | `git commit`、`git log` |
| 远程仓库 | GitHub/GitLab/Gitee 等托管端 | `git push`、`git fetch`、`git pull` |

## 提交（Commit）与 HEAD

- `HEAD` 指向当前分支的最新提交。
- 提交是不可变的快照，修改历史本质是「创建新提交并移动引用」。
- `HEAD~1` 表示上一个提交，`HEAD~2` 表示上两个提交。

```shell
git log --oneline -3
git show HEAD
git diff HEAD~1 HEAD
```

## 分支（Branch）的本质

分支只是一个指向提交的「可移动指针」：

```shell
git branch feature/xxx        # 创建分支（指针）
git switch feature/xxx        # 切换分支（移动 HEAD）
git branch -d feature/xxx     # 删除分支（删除指针，不影响提交）
```

理解「分支是指针」后，rebase、merge、reset 的行为就很容易推理。

## 进阶必备命令

| 命令 | 用途 |
| --- | --- |
| `git switch` / `git switch -c` | 切换/创建分支（推荐替代 `checkout`） |
| `git restore` | 恢复工作区或暂存区文件 |
| `git stash` | 临时保存未提交的改动 |
| `git rebase` | 变基整理历史 |
| `git cherry-pick` | 挑选提交 |
| `git worktree` | 一个仓库同时检出多个分支 |
| `git maintenance` | 自动维护仓库（gc、commit-graph 等） |
| `git sparse-checkout` | 稀疏检出大仓库 |

## 常见误区

::: danger 常见错误
1. 以为 `git checkout` 是「切换分支」专属命令，其实它同时负责恢复文件，语义混杂；新项目用 `switch` / `restore` 更清晰。
2. 以为分支是「复制一份代码」，实际只是指针，所以创建分支几乎零成本。
3. 在 `main` 上直接开发并频繁提交，历史难以整理，协作冲突多。
4. 用 `git reset --hard` 当「撤销工具」，导致未提交的工作丢失。
5. 把大文件提交进仓库，历史永远无法真正删除（除非重写历史）。
:::

## 验证方式

1. `git --version` 确认版本为 2.55.x 或更高。
2. 在测试仓库执行 `git switch -c test`、`git branch`、`git switch main`，确认分支切换正常。
3. `git log --oneline --graph --all` 查看提交与分支拓扑。
4. 执行 `git help switch` 确认 switch 命令可用。

## 参考资料

- Git 官方文档：https://git-scm.com/doc
- Pro Git 中文版：https://git-scm.com/book/zh/v2
- Git 2.55 发布说明：https://github.com/git/git/blob/master/Documentation/RelNotes/2.55.0.txt
