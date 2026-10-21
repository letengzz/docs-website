# Git 常见问题与最佳实践

本节涉及的版本与时效性结论按 2026-09 口径整理；使用前请以官方发布页为准。


汇总 Git 使用中最高频的问题与解法，并给出一份生产自查清单。

::: info 适用版本
以下命令适用于 Git 2.2x+（当前稳定版 2.55.x）。
:::

## 生产自查清单

- [ ] main 分支已开启保护（禁直推、要求 Review 与 CI）
- [ ] 提交遵循 Conventional Commits
- [ ] 不在共享分支上 rebase/force push
- [ ] 不使用 `reset --hard` 处理已推送的历史
- [ ] 大文件不进入仓库（用 Git LFS 或对象存储）
- [ ] `.gitignore` 覆盖本地工具与密钥文件
- [ ] 敏感信息一旦提交，立即轮换并重写历史
- [ ] 定期 `git maintenance run` 保持仓库健康

## 常见问题

### 1. 提交后发现密码/密钥

立即处理：

1. 轮换该密钥（Git 历史无法保证真正删除）。
2. `git commit --amend` 或 rebase 移除文件。
3. 已推送则重写历史并强推（确认只有你自己在用）。
4. 用 `git filter-repo` 清理历史。

### 2. pull 提示 refusing to merge unrelated histories

两个仓库没有共同祖先（如重新初始化过）：

```shell
git pull origin main --allow-unrelated-histories
```

确认这是预期行为再执行，否则会产生混乱合并。

### 3. 想撤销最后一次提交但保留改动

```shell
git reset --soft HEAD~1
```

### 4. 提交已推送，想撤销

```shell
git revert HEAD
```

### 5. 误删分支

```shell
# 从 reflog 找回提交
git reflog
git checkout -b recover <hash>
```

### 6. 提交信息写错

```shell
# 最近一次
git commit --amend

# 更早的提交（未推送）
git rebase -i HEAD~3
```

### 7. 分支名/仓库名大小写问题

Windows/macOS 文件系统不敏感，重命名后 Git 可能不识别：

```shell
git mv oldname newname
git config core.ignorecase false
```

### 8. 中文乱码

```shell
git config --global core.quotepath false
```

### 9. 大仓库操作慢

```shell
git maintenance start
git maintenance run
```

### 10. 只想克隆部分目录

```shell
git clone --filter=blob:none --sparse https://github.com/example/big-repo.git
cd big-repo
git sparse-checkout set docs
```

## 最佳实践

1. **小步提交**：一个提交一个逻辑，便于 review 与回滚。
2. **提交信息即文档**：写清「为什么」，而不是只写「改了什么」。
3. **共享分支用 merge/revert，私有分支用 rebase/reset**。
4. **reflog 是后悔药**：误操作先查 `git reflog`。
5. **PR 合并前跑 CI**：宁可慢一点，不要坏 main。
6. **定期清理**：删除已合并分支、`git maintenance` 保持仓库健康。

## 验证方式

1. 在测试仓库演练 reset/revert/stash/cherry-pick 全套操作。
2. 用 `git reflog` 找回一次「误删」的提交。
3. 配置 commitlint 后提交一条非法信息，确认被拦截。
4. 用 `git maintenance run` 后观察仓库命令响应速度。

## 相关文档

- [IDE 配置 · 快捷键与高效操作](../../../IDE/Shortcuts/index.md)：IDE 内 Git 面板与命令行的分工，以及提交/推送的键位对照。
- [IDE 配置 · 配置同步与团队统一](../../../IDE/ConfigSync/index.md)：`.gitattributes` 与 `.editorconfig` 的换行策略为何必须一致（否则每次打开文件都显示整文件被改）。
- [IDE 配置 · 实战：搭一套统一的 IDE 环境](../../../IDE/Practice/index.md)：批量格式化提交应单独成一次提交，出问题可直接 revert。

## 与「代码搜索与索引工程」的分工：`git grep` 的边界在哪

| 问题 | 归谁 | 关键差别 |
| --- | --- | --- |
| 「这个符号在这个分支的哪一行」 | 本页（`git grep`） | 线性扫描、无索引、单工作树 |
| 「跨 20 个仓 / 20 个分支 / 要按相关性排序」 | [代码搜索与索引工程](../../../CodeSearch/index.md) | 需要索引、需要排序、需要权限 |
| 「这段代码是哪次提交引入的」 | 本页 + [`git log -S`](../Overview/index.md) | 历史检索与工作树检索是两套语义 |

**这一页特有的一个坑**：`git grep` **默认只搜「已跟踪且在本次检出中」的文件**——未跟踪的新文件（还没 `git add`）不在结果里，`--untracked` 才会包含；想看历史版本要显式给一个 revision（`git grep x HEAD~3`），否则它永远只看当前工作树。这与「索引漏入库」（判据 `CSG-A`）是同一类失效：**范围没说清，结果就不可信**。

## 参考资料

- Git 官方文档：https://git-scm.com/doc
- Git flight rules（飞行规则）：https://github.com/k88hudson/git-flight-rules
- GitHub Docs：https://docs.github.com/zh
