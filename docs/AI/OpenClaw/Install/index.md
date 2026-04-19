# OpenClaw 安装

## 环境要求

### 硬件要求

- **CPU**：双核及以上处理器
- **内存**：至少 8GB RAM（推荐 16GB 以上）
- **硬盘**：至少 10GB 可用空间
- **网络**：稳定的网络连接

### 软件要求

- **操作系统**：Windows 10/11 64位、Ubuntu 18.04+、macOS 10.15+
- **容器**：Docker（可选，用于容器化部署）

## 安装方式

### Windows 安装

#### 原生环境快速部署

这是最直接的部署方式，适合个人开发者快速体验和轻量级使用。

##### 安装Node.js

OpenClaw基于Node.js开发，对版本要求严格。为避免版本冲突，推荐使用 `nvm-windows` 进行版本管理。

- **安装nvm-windows**：从GitHub Releases下载最新版 `nvm-setup.exe` 并安装。

- **以管理员身份打开PowerShell**：按 `Win+X`，选择 “Windows PowerShell (管理员)”。

- **安装并使用Node.js 22.x版本**：

  ```perl
  # 安装Node.js 22.x
  nvm install 22
  
  # 使用指定版本
  nvm use 22.22.0
  ```

- **验证安装**：

  ```bash
  node --version  # 应显示 v22.x.x
  npm --version   # 应显示 10.x.x 或更高
  ```

##### 核心部署：一键安装与Gateway配置

- **解锁PowerShell执行策略**（若后续脚本执行报错）：

  ```sql
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **一键安装OpenClaw**： 使用官方脚本进行安装。若网络受限，可使用国内镜像源。

  ```bash
  # 官方脚本（推荐）
  iwr -useb https://openclaw.ai/install.ps1 | iex
  
  # 若下载超时，使用国内镜像脚本
  # iwr -useb https://clawd.org.cn/install.ps1 | iex
  ```

- **配置Gateway模式**： 安装完成后，需配置并启动Gateway服务，这是提供Web控制台访问和任务执行能力的关键。

  ```bash
  # 设置Gateway为本地模式
  openclaw config set gateway.mode local
  
  # 安装Gateway服务（创建计划任务，实现开机自启）
  openclaw gateway install
  
  # 启动Gateway服务
  openclaw gateway start
  ```

- **验证服务状态并访问**：

  ```bash
  openclaw gateway status  # 应显示 “Running”
  ```

  打开浏览器，访问 `http://127.0.0.1:18789`。看到登录界面即表示核心部署成功。

##### 避坑指南：原生环境常见问题

- 坑1：命令找不到（‘openclow’ 不是内部或外部命令）
  - **原因**：npm全局安装路径未添加到系统PATH。
  - **解决**：关闭当前PowerShell，重新以管理员身份打开。若仍不行，手动添加 `C:\Users\你的用户名\AppData\Roaming\npm` 到环境变量。
- 坑2：安装脚本卡死或下载失败
  - **原因**：网络无法访问GitHub或境外资源。
  - **解决**：使用国内镜像脚本；或配置npm镜像 `npm config set registry https://registry.npmmirror.com` 后，尝试通过 `npm install -g openclaw` 安装。
- 坑3：Gateway启动失败，端口18789被占用
  - **解决**：查找占用进程 `netstat -ano | findstr :18789`，在任务管理器中结束相应进程，或修改OpenClaw配置文件中的端口（不推荐新手操作）。

#### WSL2专业级部署

对于追求稳定性、需要使用Docker容器化或更好地利用Linux生态的用户，WSL2是最佳选择。这也是官方推荐的Windows运行方式。

##### WSL2环境搭建

- **启用WSL功能并安装发行版**： 以管理员身份打开PowerShell，运行：

  ```csharp
  # 安装WSL2及默认的Ubuntu发行版
  wsl --install -d Ubuntu-22.04
  
  # 设置WSL默认版本为2
  wsl --set-default-version 2
  ```

  安装完成后，按提示设置用户名和密码。

- **WSL2性能优化**： 在Windows用户目录（`C:\Users\你的用户名`）下创建 `.wslconfig` 文件，用于限制WSL2的内存和CPU使用，避免占满主机资源。

  ```ini
  memory=6GB      # 根据你的物理内存调整
  processors=4
  localhostForwarding=true
  ```

  保存后，在PowerShell中执行 `wsl --shutdown` 重启WSL使配置生效。

##### 在WSL2中部署OpenClaw

- **进入WSL环境**：

  ```
  wsl ~
  ```
  
- **安装基础依赖**：

  ```bash
  # 更新软件源并安装Node.js、Git、Docker等
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y git nodejs npm docker.io
  ```

- **配置npm国内镜像（加速依赖下载）**：

  ```shell
  npm config set registry https://registry.npmmirror.com
  ```
  
- **克隆仓库并安装**：

  ```bash
  git clone https://github.com/OpenClaw/Clawdbot.git
  cd Clawdbot
  npm install
  npm run init
  ```

- **启动服务**：

  ```shell
  npm run start
  ```
  
  此时，OpenClaw服务将在WSL2内部运行，但由于WSL2的网络特性，需要通过 `localhost` 在Windows浏览器中访问它。

##### 避坑指南：WSL2特有网络与权限问题

- 坑1：WSL2中访问Windows本地的代理服务
  - **原因**：WSL2使用虚拟化网络，IP地址与宿主机不同。
  - **解决**：在WSL2中使用 `host.docker.internal` 这个特殊域名来指向宿主机。配置代理时使用 `export http_proxy=http://host.docker.internal:1080`。
- 坑2：WSL2文件系统性能
  - **原因**：在WSL2中访问 `/mnt/c/` 下的Windows文件系统性能较差。
  - **解决**：将OpenClaw项目及其数据存放在WSL2的内部文件系统（如 `/home/用户名/`）中，而非 `/mnt/c/` 下，以获得最佳I/O性能。
- 坑3：服务在WSL2关闭后停止
  - **解决**：若需要OpenClaw在后台持续运行，应学习使用 `screen`、`tmux` 或将其注册为WSL2内部的systemd服务。或者，考虑将WSL2一直保持在后台运行（不执行 `wsl --shutdown`）。

## 验证安装

### 检查版本

```bash [终端]
openclaw --version
# 输出: OpenClaw v1.0.0
```

### 检查服务状态

```bash [终端]
openclaw status
# 输出: OpenClaw is running on http://localhost:8080
```

### 访问 Web 界面

安装完成后，打开浏览器访问：

```
http://localhost:8080
```

## 常见安装问题

### 1. 端口被占用

```bash [终端]
# 检查端口占用
netstat -ano | findstr :8080

# 修改端口
openclaw start --port 8081
```

### 2. 权限不足

```bash [终端]
# Linux/macOS
sudo openclaw start

# Windows（以管理员身份运行）
# 右键点击 PowerShell -> 以管理员身份运行
```

### 3. 依赖缺失

```bash [终端]
# 安装 .NET 运行时
# Windows
winget install Microsoft.DotNet.Runtime.6

# Linux
sudo apt install dotnet-runtime-6.0

# macOS
brew install dotnet
```

## 卸载

### Windows

```powershell [终端]
# 通过控制面板卸载
# 或使用命令行
openclaw uninstall
```

### Linux

```bash [终端]
# Ubuntu/Debian
sudo apt remove openclaw

# CentOS/RHEL
sudo yum remove openclaw
```

### macOS

```bash [终端]
# Homebrew 安装的
brew uninstall openclaw

# 手动安装的
sudo rm /usr/local/bin/openclaw
```

### Docker

```bash [终端]
# 停止并删除容器
docker stop openclaw
docker rm openclaw

# 删除镜像
docker rmi openclaw/openclaw
```

