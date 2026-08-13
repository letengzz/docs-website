# Git Cherry-Pick

`git cherry-pick` 把某个（或某几个）提交「复制」到当前分支，常用于补丁移植、紧急修复跨分支同步。

::: info 适用版本
以下命令在 Git 2.2x+ 均可用；批量 cherry-pick 使用提交范围语法。
:::

## 基本用法

```shell
# 把指定提交复制到当前分支
git cherry-pick a1b2c3d

# 一次复制多个提交
git cherry-pick a1b2c3d e4f5g6h

# 复制一个连续范围（不包含左端点）
git cherry-pick main..feature/xxx

# 复制但只写入工作区，不自动提交
git cherry-pick -n a1b2c3d
```

## 典型场景

1. `hotfix` 修复提交需要同时合入 `main` 和 `release/1.3`。
2. 某个功能提交被误删，从 reflog 找回后移植。
3. 只想把一个 PR 里的某个提交带到当前分支（而不合并整个 PR）。

## 冲突处理

cherry-pick 冲突时：

```shell
# 查看状态
git status

# 解决冲突后继续
git add <file>
git cherry-pick --continue

# 放弃本次 cherry-pick
git cherry-pick --abort

# 冲突较多时跳过当前提交，处理下一个
git cherry-pick --skip
```

## Cherry-Pick 与 Merge 的区别

| 对比 | Cherry-Pick | Merge |
| --- | --- | --- |
| 是否保留原始提交 | 生成新提交（哈希不同） | 保留原提交 |
| 用途 | 挑选部分提交 | 合并整个分支 |
| 可追溯性 | 新提交没有「来自哪个分支」的直接关系 | 合并提交保留双亲信息 |
| 重复合并 | 再次 merge 可能重复冲突 | 已合并内容不会重复 |

## 配合 Rebase 批量移植

把一个分支的所有提交移到另一个基线（推荐用 rebase）：

```shell
git switch feature/backport
git rebase --onto release/1.3 main feature/backport
```

## 易错点

::: danger 常见错误
1. 用 cherry-pick 代替 merge 把整个分支复制一遍，历史重复且难追溯。
2. cherry-pick 已存在于目标分支的提交，冲突或空提交。
3. 忘记 `--continue` / `--abort`，仓库停留在 cherry-pick 中间状态。
4. 复制提交后没有测试，以为「代码一样就安全」。
5. 依赖了被移植提交之外的其他提交，编译失败。
:::

## 验证方式

1. 在测试仓库创建两个分支，提交修复后 `git cherry-pick <hash>` 到另一分支。
2. 确认新提交哈希与原提交不同，`git show` 内容一致。
3. 故意制造冲突，走一遍 `--continue` 和 `--abort` 两条路径。
4. 用 `git log --oneline --graph` 观察 cherry-pick 后的线性历史。

## 参考资料

- Git Cherry-Pick 文档：https://git-scm.com/docs/git-cherry-pick
- Pro Git 拣选提交：https://git-scm.com/book/zh/v2/Git-工具-拣选提交
