# Git 子模块

子模块（Submodule）让一个仓库引用另一个仓库的指定提交，常用于共享库、主题、协议定义等场景。它功能强大但坑很多，本节给出能落地的用法。

::: info 适用版本
以下命令在 Git 2.2x+ 均可用；`git submodule update --init --recursive` 是克隆后的标准操作。
:::

## 子模块是什么

子模块是「仓库中的仓库」：

- 父仓库只记录子仓库的提交哈希（`gitlink`）。
- 子仓库有自己独立的 `.git` 和历史。
- 拉取父仓库默认不会自动拉取子模块内容。

## 添加子模块

```shell
git submodule add https://github.com/example/shared-lib.git libs/shared
git commit -m "chore: 添加 shared-lib 子模块"
```

添加后仓库会多出：

```text
.gitmodules          # 记录子模块 URL 与路径
libs/shared          # 指向子模块提交的 gitlink
```

## 克隆带子模块的仓库

```shell
# 方式一：克隆后初始化
git clone https://github.com/example/project.git
cd project
git submodule update --init --recursive

# 方式二：克隆时直接拉取子模块
git clone --recurse-submodules https://github.com/example/project.git
```

## 更新子模块

```shell
# 进入子模块拉取最新
cd libs/shared
git fetch origin
git checkout <tag-or-branch>
cd ../..
git add libs/shared
git commit -m "chore: 升级 shared-lib"
```

父仓库不会自动跟踪子模块的分支，除非配置：

```ini [.gitmodules]
[submodule "libs/shared"]
	path = libs/shared
	url = https://github.com/example/shared-lib.git
	branch = main
```

```shell
git submodule update --remote libs/shared
```

## 删除子模块

```shell
git submodule deinit -f libs/shared
rm -rf .git/modules/libs/shared
git rm -f libs/shared
```

提交后确认 `.gitmodules` 中的条目也已移除。

## 子模块 vs 其他方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 子模块 | 版本精确、原生支持 | 操作繁琐、易忘初始化 |
| 包管理器（npm/Maven/Go mod） | 版本管理成熟、自动拉取 | 需要发布流程 |
| monorepo | 共享代码直接可见 | 仓库大、权限粒度粗 |
| Git subtree | 合并进父仓库 | 历史复杂、更新麻烦 |

大多数场景优先考虑包管理器或 monorepo；子模块适合「必须绑定特定提交」的场合（如固件、协议仓库）。

## 易错点

::: danger 常见错误
1. 克隆后忘记 `submodule update --init`，目录是空的，编译失败。
2. 子模块改完没提交，父仓库的 gitlink 一直是旧哈希。
3. 子模块 URL 用本机路径，别人克隆后无法拉取。
4. 在子模块里切到未提交的游离 HEAD，导致父仓库记录错误提交。
5. 删除子模块只删目录，`.gitmodules` 和 `.git/modules` 残留。
:::

## 验证方式

1. 新建测试仓库添加一个子模块并提交，`git submodule status` 显示对应哈希。
2. 重新克隆父仓库，用 `--recurse-submodules` 确认子模块内容就位。
3. 修改子模块后提交父仓库，确认 gitlink 更新。
4. 删除子模块后检查 `.gitmodules` 已无残留。

## 参考资料

- Git Submodule 文档：https://git-scm.com/docs/gitsubmodules
- Pro Git 子模块：https://git-scm.com/book/zh/v2/Git-工具-子模块
