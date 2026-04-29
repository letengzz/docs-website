# OpenClaw 安装

## 环境要求

### 软件要求

| 要求 | 最低版本 | 推荐版本 |
|------|----------|----------|
| **Node.js** | 22.x | 最新 LTS |
| **npm** | 10.x（随 Node.js 附带） | 最新版 |
| **Git**（WSL2 / 源码安装） | 2.x | 最新版 |
| **Docker**（容器部署） | 20.10+ | 最新版 |

### 硬件建议

| 场景 | 内存 | 硬盘 |
|------|------|------|
| 轻量使用（个人助理） | 4GB+ | 2GB 可用 |
| 日常使用（办公自动化） | 8GB+ | 5GB 可用 |
| 重度使用（多任务并发） | 16GB+ | 10GB 可用 |

---

## Windows 安装

### 方式一：一键安装（推荐）

这是最快捷的方式，适合大多数 Windows 用户。

#### 1. 安装 Node.js

OpenClaw 基于 **Node.js** 开发，对版本要求严格（**必须 22+**）。强烈推荐使用 `nvm-windows` 管理 Node.js 版本。

- **下载安装 nvm-windows**：[nvm-windows Releases](https://github.com/coreybutler/nvm-windows/releases)，下载 `nvm-setup.exe` 并安装。

- **以管理员身份打开 PowerShell**（`Win+X` →「Windows PowerShell (管理员)」或「终端 (管理员)」）。

- **安装并切换 Node.js 版本**：

```powershell
# 安装 Node.js 22.x
nvm install 22

# 使用该版本
nvm use 22.22.0
```

- **验证安装**：

```powershell
node --version   # 应显示 v22.x.x
npm --version    # 应显示 10.x.x 或更高
```

#### 2. 安装 OpenClaw

```powershell
# 设置执行策略（如脚本执行报错）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 一键安装（官方脚本）
iwr -useb https://openclaw.ai/install.ps1 | iex
```

::: tip 💡 国内网络加速
如果下载超时或失败，可使用国内镜像脚本：
```powershell
iwr -useb https://clawd.org.cn/install.ps1 | iex
```

或先配置 npm 国内镜像：
```powershell
npm config set registry https://registry.npmmirror.com
npm install -g openclaw
```
:::

#### 3. 启动服务

```powershell
# 启动 Gateway
openclaw gateway start

# 查看状态
openclaw gateway status
```

打开浏览器访问 **[http://127.0.0.1:18789](http://127.0.0.1:18789)**，首次使用需运行 `openclaw onboard` 完成初始化配置。

---

### 方式二：WSL2 安装（推荐高级用户）

WSL2 提供更好的 Linux 生态兼容性，特别适合需要 Docker 容器化或使用 Linux 工具链的用户。这也是官方推荐的 Windows 运行方式。

#### 1. 安装 WSL2

以**管理员**身份打开 PowerShell：

```powershell
# 安装 WSL2 及 Ubuntu 发行版
wsl --install -d Ubuntu-22.04

# 设置默认 WSL 版本为 2
wsl --set-default-version 2
```

安装完成后按提示设置 Linux 用户名和密码。

#### 2. WSL2 性能优化（可选但推荐）

在 Windows 用户目录（`C:\Users\你的用户名`）下创建 `.wslconfig` 文件：

```ini
[wsl2]
memory=6GB          # 根据物理内存调整，建议不超过总内存的 50%
processors=4        # 根据 CPU 核心数调整
localhostForwarding=true
```

保存后，在 PowerShell 中执行 `wsl --shutdown` 重启 WSL 使配置生效。

#### 3. 在 WSL2 中安装 OpenClaw

进入 WSL 环境：

```bash
wsl ~
```

安装 Node.js 和依赖：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Node.js 22.x（使用 NodeSource 官方源）
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 Git
sudo apt install -y git

# 验证版本
node --version   # 应显示 v22.x.x
npm --version
```

安装 OpenClaw：

```bash
# 方式 A：npm 全局安装（推荐）
npm install -g openclaw

# 方式 B：从源码安装（如需定制开发）
git clone https://github.com/openclaw/openclaw.git
cd openclaw
npm install
npm run build
npm link
```

启动服务：

```bash
openclaw gateway start
```

WSL2 会自动将端口转发到 Windows，因此在 Windows 浏览器中访问 `http://127.0.0.1:18789` 即可。

#### 4. 让 OpenClaw 在后台持续运行

WSL2 关闭后所有进程会停止。如需后台运行：

```bash
# 使用 tmux（推荐）
sudo apt install -y tmux
tmux new -s openclaw
openclaw gateway start
# 按 Ctrl+B 然后按 D 分离会话

# 重新连接: tmux attach -t openclaw
```

---

## macOS 安装

### 方式一：npm 全局安装（推荐）

```bash
# 先安装 Node.js 22+（使用 nvm 管理版本）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install 22
nvm use 22

# 安装 OpenClaw
npm install -g openclaw

# 初始化配置
openclaw onboard

# 启动
openclaw gateway start
```

### 方式二：Homebrew

```bash
# 注意：Homebrew 方式可能不是最新版，推荐使用 npm
brew install node@22
npm install -g openclaw
```

---

## Linux 安装

### Ubuntu / Debian

```bash
# 1. 安装 Node.js 22.x
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 2. 安装 OpenClaw
npm install -g openclaw

# 3. 初始化配置
openclaw onboard

# 4. 启动
openclaw gateway start
```

### CentOS / RHEL / Fedora

```bash
# 1. 安装 Node.js 22.x
curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo bash -
sudo yum install -y nodejs   # CentOS/RHEL
# 或
sudo dnf install -y nodejs   # Fedora

# 2. 安装 OpenClaw
npm install -g openclaw

# 3. 初始化配置
openclaw onboard

# 4. 启动
openclaw gateway start
```

### 设为系统服务（开机自启）

创建 systemd 服务文件：

```bash
sudo tee /etc/systemd/system/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway Service
After=network.target

[Service]
Type=simple
User=你的用户名
ExecStart=/usr/bin/openclaw gateway start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable openclaw-gateway
sudo systemctl start openclaw-gateway
```

---

## Docker 安装

适合服务器部署或需要环境隔离的场景。

### 使用 Docker 运行

```bash
# 拉取镜像
docker pull openclaw/openclaw:latest

# 运行容器
docker run -d \
  --name openclaw \
  --restart unless-stopped \
  -p 18789:18789 \
  -v openclaw-config:/app/config \
  -v openclaw-data:/app/data \
  -e OPENCLAW_API_KEY=your_api_key_here \
  openclaw/openclaw:latest

# 查看日志
docker logs -f openclaw
```

### 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  openclaw:
    image: openclaw/openclaw:latest
    container_name: openclaw
    restart: unless-stopped
    ports:
      - "18789:18789"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    environment:
      - NODE_ENV=production
      # 模型 API Key 通过 onboard 或环境变量配置
```

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

::: warning ⚠️ Docker 模式注意事项
- Docker 容器内默认无法访问宿主机的文件系统。如果需要操控宿主机文件，需要挂载对应目录。
- 容器内运行 Shell 命令的作用域仅限于容器内部。
- 访问宿主机服务时使用 `host.docker.internal`（Windows/Mac）或 `172.17.0.1`（Linux）。

:::

## 验证安装

### 检查版本

```bash
openclaw --version
# 输出示例: openclaw v1.5.0
```

### 检查 Gateway 状态

```bash
openclaw gateway status
# 应输出: Gateway is running at http://127.0.0.1:18789
```

### 访问 Web 控制台

浏览器打开：**[http://127.0.0.1:18789](http://127.0.0.1:18789)**

看到登录界面或对话界面即表示安装成功。

---

## 卸载

### Windows

```powershell
# 停止 Gateway
openclaw gateway stop

# 卸载 npm 全局包
npm uninstall -g openclaw

# 清理配置和数据（可选）
# 配置目录通常在: C:\Users\你的用户名\.openclaw
Remove-Item -Recurse -Force $env:USERPROFILE\.openclaw
```

### macOS / Linux

```bash
# 停止服务
openclaw gateway stop

# 卸载
npm uninstall -g openclaw

# 清理配置和数据（可选）
rm -rf ~/.openclaw
```

### Docker

```bash
# 停止并删除容器
docker stop openclaw
docker rm openclaw

# 删除镜像
docker rmi openclaw/openclaw

# 清理数据卷（可选）
docker volume rm openclaw-config openclaw-data
```

---

## 常见问题

### 'openclaw' 不是内部或外部命令

**原因**：npm 全局安装路径未添加到系统 PATH。

**解决**：
- **Windows**：关闭当前 PowerShell，重新以管理员身份打开。若仍不行，手动将 `%APPDATA%\npm` 添加到系统环境变量 PATH。
- **Mac/Linux**：检查 npm 全局路径 `npm config get prefix`，确认该路径在 `$PATH` 中。

### 安装脚本卡死或下载失败

**原因**：网络无法访问 GitHub 或境外 npm 源。

**解决**：
```bash
# 方案 A：使用国内镜像脚本（Windows PowerShell）
iwr -useb https://clawd.org.cn/install.ps1 | iex

# 方案 B：配置 npm 国内镜像后安装
npm config set registry https://registry.npmmirror.com
npm install -g openclaw

# 方案 C：使用代理
set HTTP_PROXY=http://127.0.0.1:7890   # Windows
export HTTP_PROXY=http://127.0.0.1:7890  # Mac/Linux
```

### Gateway 启动失败，端口 18789 被占用

**解决**：
```powershell
# Windows：查找占用进程
netstat -ano | findstr :18789
# 记下 PID，在任务管理器中结束对应进程

# Mac/Linux
lsof -i :18789
kill -9 <PID>
```

或修改 OpenClaw 端口（不推荐新手操作）：
```bash
openclaw config set gateway.port 18790
openclaw gateway restart
```

### Node.js 版本不兼容

**症状**：安装或运行时报语法错误（如 `??=`、`||=` 等运算符不支持）。

**原因**：Node.js 版本低于 22.x。

**解决**：
```bash
# 使用 nvm 切换到 Node.js 22+
nvm install 22
nvm use 22

# 确认版本
node --version   # 必须是 v22.x.x 或更高
```

### WSL2 中无法访问 Windows 代理

**原因**：WSL2 使用虚拟化网络，IP 地址与宿主机不同。

**解决**：在 WSL2 中使用 `host.docker.internal` 指向宿主机：
```bash
export HTTP_PROXY=http://host.docker.internal:7890
export HTTPS_PROXY=http://host.docker.internal:7890
```

### WSL2 文件系统性能差

**原因**：在 WSL2 中访问 `/mnt/c/` 下的 Windows 文件系统性能较差。

**解决**：将 OpenClaw 项目和数据存放在 WSL2 内部文件系统中（如 `/home/用户名/`），而非 `/mnt/c/` 下。
