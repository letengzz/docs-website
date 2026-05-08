# pnpm 包管理工具

pnpm 是一个快速、节省磁盘空间的包管理工具。

- 官网：https://pnpm.io/
- GitHub：https://github.com/pnpm/pnpm

## pnpm 特点

- **快速**：比 npm 快 2 倍，比 yarn 快 3 倍
- **节省磁盘空间**：使用硬链接和符号链接
- **严格**：默认非扁平的 node_modules 结构
- **兼容**：完全兼容 npm 和 yarn 的 package.json

## 安装 pnpm

### 使用 npm 安装

```shell [install-npm.sh]
npm install -g pnpm
```

### 使用 Homebrew 安装 (macOS)

```shell [install-brew.sh]
brew install pnpm
```

### 使用 Corepack 安装

```shell [install-corepack.sh]
corepack enable
corepack prepare pnpm@latest --activate
```

## pnpm 常用命令

### 初始化项目

```shell [init.sh]
pnpm init
```

### 安装依赖

```shell [install.sh]
# 安装所有依赖
pnpm install

# 安装单个依赖
pnpm add express

# 安装开发依赖
pnpm add -D typescript

# 安装全局依赖
pnpm add -g nodemon
```

### 移除依赖

```shell [remove.sh]
# 移除依赖
pnpm remove express

# 移除全局依赖
pnpm remove -g nodemon
```

### 运行脚本

```shell [run.sh]
# 运行脚本
pnpm run dev

# 简写
pnpm dev
```

## pnpm 工作空间

### 配置工作空间

```yaml [pnpm-workspace.yaml]
packages:
  - 'packages/*'
  - 'apps/*'
```

### 工作空间命令

```shell [workspace.sh]
# 在所有工作空间中安装依赖
pnpm install -r

# 在特定工作空间中运行命令
pnpm --filter my-package run build

# 添加依赖到工作空间根目录
pnpm add -w express
```

## pnpm vs npm vs yarn

| 特性 | pnpm | npm | yarn |
|------|------|-----|------|
| 速度 | 最快 | 较慢 | 中等 |
| 磁盘空间 | 最省 | 占用多 | 中等 |
| 严格性 | 严格 | 宽松 | 中等 |
| 工作空间 | 支持 | 支持 | 支持 |
| 缓存 | 内容寻址 | 缓存 | 缓存 |

## pnpm 配置

### .npmrc 配置

```ini [.npmrc]
# 使用淘宝镜像
registry=https://registry.npmmirror.com

# 严格 peer dependencies
strict-peer-dependencies=true

# 自动安装 peer dependencies
auto-install-peers=true
```

### 查看配置

```shell [config.sh]
# 查看所有配置
pnpm config list

# 设置配置
pnpm config set registry https://registry.npmmirror.com
```

## pnpm 优势

### 1. 节省磁盘空间

pnpm 使用内容寻址存储，相同版本的包只存储一次。

### 2. 快速安装

使用硬链接和符号链接，避免重复复制文件。

### 3. 严格依赖管理

默认非扁平的 node_modules 结构，避免幽灵依赖。

### 4. 原生支持 Monorepo

内置工作空间支持，无需额外配置。

::: tip 提示
- pnpm 完全兼容 npm 和 yarn
- 推荐使用 pnpm 替代 npm

Monorepo 项目首选 pnpm
:::
