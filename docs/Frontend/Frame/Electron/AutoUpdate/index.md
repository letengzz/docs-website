# Electron 自动更新

## electron-updater

### 安装

```bash [终端]
npm install electron-updater
```

### 配置

```json [package.json]
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "username",
      "repo": "my-electron-app",
      "releaseType": "release"
    }
  }
}
```

### 主进程实现

```javascript [main.js]
const { app, BrowserWindow, ipcMain } = require('electron')
const { autoUpdater } = require('electron-updater')

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600
  })

  mainWindow.loadFile('index.html')

  autoUpdater.autoDownload = false
  autoUpdater.autoInstallOnAppQuit = true

  autoUpdater.on('checking-for-update', () => {
    mainWindow.webContents.send('update-status', '正在检查更新...')
  })

  autoUpdater.on('update-available', (info) => {
    mainWindow.webContents.send('update-available', info)
  })

  autoUpdater.on('update-not-available', () => {
    mainWindow.webContents.send('update-status', '当前已是最新版本')
  })

  autoUpdater.on('error', (err) => {
    mainWindow.webContents.send('update-error', err.message)
  })

  autoUpdater.on('download-progress', (progressObj) => {
    mainWindow.webContents.send('download-progress', progressObj)
  })

  autoUpdater.on('update-downloaded', () => {
    mainWindow.webContents.send('update-downloaded')
  })
}

ipcMain.on('check-for-update', () => {
  autoUpdater.checkForUpdates()
})

ipcMain.on('download-update', () => {
  autoUpdater.downloadUpdate()
})

ipcMain.on('quit-and-install', () => {
  autoUpdater.quitAndInstall()
})

app.whenReady().then(createWindow)
```

### 渲染进程实现

```javascript [preload.js]
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  checkForUpdate: () => ipcRenderer.send('check-for-update'),
  downloadUpdate: () => ipcRenderer.send('download-update'),
  quitAndInstall: () => ipcRenderer.send('quit-and-install'),
  onUpdateStatus: (callback) => ipcRenderer.on('update-status', (_event, status) => callback(status)),
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', (_event, info) => callback(info)),
  onUpdateNotAvailable: (callback) => ipcRenderer.on('update-not-available', (_event) => callback()),
  onUpdateError: (callback) => ipcRenderer.on('update-error', (_event, error) => callback(error)),
  onDownloadProgress: (callback) => ipcRenderer.on('download-progress', (_event, progress) => callback(progress)),
  onUpdateDownloaded: (callback) => ipcRenderer.on('update-downloaded', (_event) => callback())
})
```

```javascript [renderer.js]
window.electronAPI.onUpdateStatus((status) => {
  console.log('更新状态:', status)
})

window.electronAPI.onUpdateAvailable((info) => {
  console.log('发现新版本:', info.version)
  if (confirm('发现新版本，是否下载？')) {
    window.electronAPI.downloadUpdate()
  }
})

window.electronAPI.onDownloadProgress((progress) => {
  console.log('下载进度:', progress.percent.toFixed(2) + '%')
})

window.electronAPI.onUpdateDownloaded(() => {
  if (confirm('更新已下载，是否立即安装？')) {
    window.electronAPI.quitAndInstall()
  }
})

// 检查更新
window.electronAPI.checkForUpdate()
```

## 更新服务器配置

### GitHub Releases

```json [package.json]
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "username",
      "repo": "my-electron-app",
      "releaseType": "release",
      "token": "your-github-token"
    }
  }
}
```

### 自定义服务器

```json [package.json]
{
  "build": {
    "publish": {
      "provider": "generic",
      "url": "https://example.com/updates/",
      "channel": "latest"
    }
  }
}
```

### S3

```json [package.json]
{
  "build": {
    "publish": {
      "provider": "s3",
      "bucket": "my-electron-updates",
      "region": "us-east-1"
    }
  }
}
```

## 手动更新检查

```javascript [main.js]
const { autoUpdater } = require('electron-updater')

// 应用启动时检查
app.whenReady().then(() => {
  createWindow()

  setTimeout(() => {
    autoUpdater.checkForUpdatesAndNotify()
  }, 5000)
})
```

## 更新流程

```mermaid
graph TD
    A[应用启动] --> B[检查更新]
    B --> C{有更新?}
    C -->|是| D[通知用户]
    C -->|否| E[继续运行]
    D --> F[用户确认下载]
    F --> G[下载更新]
    G --> H[下载完成]
    H --> I[用户确认安装]
    I --> J[重启并安装]
```

## 错误处理

```javascript [main.js]
autoUpdater.on('error', (err) => {
  console.error('更新错误:', err)

  if (err.message.includes('net::ERR_INTERNET_DISCONNECTED')) {
    mainWindow.webContents.send('update-error', '网络连接失败')
  } else if (err.message.includes('404')) {
    mainWindow.webContents.send('update-error', '未找到更新文件')
  } else {
    mainWindow.webContents.send('update-error', '更新失败，请稍后重试')
  }
})
```

## 强制更新

```javascript [main.js]
autoUpdater.on('update-downloaded', () => {
  mainWindow.webContents.send('update-downloaded')

  setTimeout(() => {
    autoUpdater.quitAndInstall()
  }, 60000)
})
```

::: danger 注意
**强制自动安装是高风险操作**。若新版本存在严重缺陷，用户会被动升级到有问题的版本且无法回退。建议：

1. 优先采用「提示用户、由用户选择何时重启」，而不是静默强制安装；
2. 若必须强制，先灰度放量，观察关键指标后再全量；
3. 保留「跳过此版本」能力，避免用户被反复打扰。
:::

## 更新失败的处理原则

| 情况 | 处理 |
| --- | --- |
| 网络不通 / 超时 | 静默重试，不打断用户使用（**更新失败绝不能阻塞主流程**） |
| 清单 404 | 检查产物命名与 `latest.yml` 是否匹配，以及上传是否完整 |
| 签名不符 | 更新会被系统拒绝，需核对签名配置与证书 |
| 下载中断 | 支持断点重试，或下次启动再试 |
| 安装失败 | 记录日志并保留旧版本可运行 |

## 相关专题

- [Electron 构建工具](../BuildingTools/index.md)：`artifactName` 与更新清单的对应
- [Electron 打包应用](../PackageApplications/index.md)：产物生成流程
- [Electron 安全最佳实践](../Security/index.md)：签名与完整性校验
- [Electron 性能优化](../Performance/index.md)：更新对启动耗时的影响
- [Electron 自动化测试](../Testing/index.md)：把更新检查纳入观测

::: tip 一句话原则
**自动更新是「可用性」而非「关键路径」**。它挂掉时应用必须照常可用；只有当用户主动选择升级时才让它影响使用。
:::

