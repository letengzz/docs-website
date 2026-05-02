# Electron 进程

在 Electron 中主要控制两类进程：主进程、渲染器进程。

## 主进程

每个 Electron 应用都有一个单一的主进程，作为应用程序的入口点。

主进程在 Node.js 环境中运行，它具有 require 模块和使用所有 Node.js API 的能力。

主进程的核心就是：**使用 BrowserWindow 来创造和管理窗口**

```javascript [main.js]
const { app, BrowserWindow } = require('electron')

app.whenReady().then(() => {
  const win = new BrowserWindow({
    width: 800,
    height: 600
  })

  win.loadFile('index.html')
})
```

## 渲染进程

每个 BrowserWindow 实例都对应一个单独的渲染器进程，运行在渲染器进程中的代码，必须遵守网页标准，这也就意味着：渲染器进程无权直接访问 require 或使用任何 Node.js 的 API。

```html [index.html]
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>渲染进程</title>
  </head>
  <body>
    <h1>这是渲染进程</h1>
    <script src="./renderer.js"></script>
  </body>
</html>
```

```javascript [renderer.js]
console.log('运行在渲染进程中')
document.body.innerHTML += '<p>Hello from Renderer!</p>'
```

## 进程对比

| 特性 | 主进程 | 渲染进程 |
|------|--------|----------|
| 数量 | 每个应用一个 | 每个窗口一个 |
| 运行环境 | Node.js | Chromium |
| Node.js API | 完全访问 | 默认不可访问 |
| DOM API | 不可访问 | 完全访问 |
| 职责 | 创建窗口、生命周期管理 | 渲染页面、用户交互 |

## 进程生命周期

### 主进程事件

```javascript [main.js]
const { app, BrowserWindow } = require('electron')

app.on('ready', () => {
  console.log('应用准备就绪')
})

app.on('window-all-closed', () => {
  console.log('所有窗口已关闭')
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', (event) => {
  console.log('应用即将退出')
})

app.on('will-quit', (event) => {
  console.log('应用即将退出（可阻止）')
})

app.on('quit', () => {
  console.log('应用已退出')
})
```

### 渲染进程事件

```javascript [renderer.js]
window.addEventListener('DOMContentLoaded', () => {
  console.log('DOM 加载完成')
})

window.addEventListener('load', () => {
  console.log('页面加载完成')
})

window.addEventListener('beforeunload', (event) => {
  console.log('页面即将卸载')
})
```

## 进程间通信

主进程和渲染进程之间通过 IPC（Inter-Process Communication）进行通信。

```javascript [preload.js]
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  sendMessage: (message) => ipcRenderer.send('message', message),
  onReply: (callback) => ipcRenderer.on('reply', (_event, value) => callback(value))
})
```

```javascript [main.js]
const { ipcMain } = require('electron')

ipcMain.on('message', (event, message) => {
  console.log('收到消息:', message)
  event.sender.send('reply', '主进程已收到')
})
```

```javascript [renderer.js]
window.electronAPI.sendMessage('Hello from Renderer!')
window.electronAPI.onReply((reply) => {
  console.log(reply)
})
```

