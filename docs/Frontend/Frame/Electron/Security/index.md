# Electron 安全最佳实践

## 安全配置

### 推荐的 webPreferences 配置

```javascript [main.js]
const win = new BrowserWindow({
  webPreferences: {
    contextIsolation: true,
    nodeIntegration: false,
    sandbox: true,
    preload: './preload.js',
    webSecurity: true,
    allowRunningInsecureContent: false,
    experimentalFeatures: false,
    enableRemoteModule: false
  }
})
```

| 选项 | 推荐值 | 说明 |
|------|--------|------|
| `contextIsolation` | `true` | 隔离预加载脚本和页面脚本 |
| `nodeIntegration` | `false` | 禁止渲染进程直接访问 Node.js |
| `sandbox` | `true` | 沙盒模式，限制渲染进程权限 |
| `webSecurity` | `true` | 启用同源策略 |
| `allowRunningInsecureContent` | `false` | 禁止混合内容 |
| `enableRemoteModule` | `false` | 禁用 remote 模块 |

## 内容安全策略

```html [index.html]
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.example.com;"
/>
```

## 使用 contextBridge

```javascript [preload.js]
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  getVersion: () => process.versions.electron,
  readFile: (path) => ipcRenderer.invoke('read-file', path),
  writeFile: (path, content) => ipcRenderer.invoke('write-file', path, content)
})
```

## IPC 通信安全

### 验证通道名称

```javascript [main.js]
const { ipcMain } = require('electron')

const ALLOWED_CHANNELS = new Set(['read-file', 'write-file', 'get-version'])

ipcMain.handle('*', (event, channel, ...args) => {
  if (!ALLOWED_CHANNELS.has(channel)) {
    throw new Error(`不允许的通道: ${channel}`)
  }
})
```

### 验证参数

```javascript [main.js]
const path = require('path')
const fs = require('fs')

ipcMain.handle('read-file', async (event, filePath) => {
  const resolvedPath = path.resolve(filePath)
  const allowedDir = path.resolve(__dirname, 'data')

  if (!resolvedPath.startsWith(allowedDir)) {
    throw new Error('不允许访问该文件')
  }

  return fs.readFileSync(resolvedPath, 'utf-8')
})
```

## 避免使用 remote 模块

```javascript
// 错误：使用 remote 模块
const { remote } = require('@electron/remote')
const win = remote.getCurrentWindow()

// 正确：使用 IPC
const { ipcRenderer } = require('electron')
ipcRenderer.invoke('get-window-info')
```

## 加载远程内容

```javascript [main.js]
// 错误：加载不可信的远程内容
win.loadURL('https://untrusted-site.com')

// 正确：加载本地内容
win.loadFile('index.html')

// 如果必须加载远程内容，使用沙盒
const win = new BrowserWindow({
  webPreferences: {
    sandbox: true,
    contextIsolation: true,
    nodeIntegration: false
  }
})
```

## 协议处理

```javascript [main.js]
const { app, protocol } = require('electron')

app.whenReady().then(() => {
  protocol.registerFileProtocol('myapp', (request, callback) => {
    const url = request.url.replace('myapp://', '')
    const filePath = path.resolve(__dirname, url)

    if (!filePath.startsWith(path.resolve(__dirname, 'public'))) {
      callback({ error: -10 })
      return
    }

    callback({ path: filePath })
  })
})
```

## 安全检查清单

- [ ] 启用 `contextIsolation`
- [ ] 禁用 `nodeIntegration`
- [ ] 启用 `sandbox`
- [ ] 配置 CSP
- [ ] 使用 `contextBridge` 暴露 API
- [ ] 验证 IPC 通道和参数
- [ ] 禁用 `remote` 模块
- [ ] 使用 HTTPS 加载远程内容
- [ ] 定期更新 Electron 版本
- [ ] 审查第三方依赖
- [ ] 使用代码签名
- [ ] 启用 ASAR 打包

