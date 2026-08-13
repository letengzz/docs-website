# Git 常见问题与最佳实践

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

## 参考资料

- Git 官方文档：https://git-scm.com/doc
- Git flight rules（飞行规则）：https://github.com/k88hudson/git-flight-rules
- GitHub Docs：https://docs.github.com/zh
