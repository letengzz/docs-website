# Electron 窗口管理

## 窗口创建

```javascript [main.js]
const { app, BrowserWindow } = require('electron')

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    maxWidth: 1920,
    maxHeight: 1080,
    title: '我的应用',
    icon: './assets/icon.png',
    show: false,
    webPreferences: {
      preload: './preload.js',
      contextIsolation: true
    }
  })

  win.loadFile('index.html')

  win.once('ready-to-show', () => {
    win.show()
  })
}

app.whenReady().then(createWindow)
```

## 窗口状态

```javascript [main.js]
const win = new BrowserWindow({ width: 800, height: 600 })

// 最小化
win.minimize()

// 最大化
win.maximize()

// 还原
win.unmaximize()

// 全屏
win.setFullScreen(true)

// 关闭
win.close()

// 聚焦
win.focus()

// 模糊
win.blur()

// 显示/隐藏
win.show()
win.hide()

// 检查状态
console.log(win.isMinimized())
console.log(win.isMaximized())
console.log(win.isFullScreen())
console.log(win.isVisible())
console.log(win.isFocused())
```

## 窗口位置与大小

```javascript [main.js]
const win = new BrowserWindow({ width: 800, height: 600 })

// 设置位置
win.setPosition(100, 100)

// 设置大小
win.setSize(1024, 768)

// 设置最小/最大尺寸
win.setMinimumSize(400, 300)
win.setMaximumSize(1920, 1080)

// 获取位置/大小
const [x, y] = win.getPosition()
const [width, height] = win.getSize()

// 居中显示
win.center()
```

## 窗口事件

```javascript [main.js]
const win = new BrowserWindow({ width: 800, height: 600 })

win.on('close', (event) => {
  console.log('窗口即将关闭')
})

win.on('closed', () => {
  console.log('窗口已关闭')
})

win.on('focus', () => {
  console.log('窗口获得焦点')
})

win.on('blur', () => {
  console.log('窗口失去焦点')
})

win.on('minimize', () => {
  console.log('窗口最小化')
})

win.on('maximize', () => {
  console.log('窗口最大化')
})

win.on('unmaximize', () => {
  console.log('窗口还原')
})

win.on('resize', () => {
  const [width, height] = win.getSize()
  console.log(`窗口大小: ${width}x${height}`)
})

win.on('move', () => {
  const [x, y] = win.getPosition()
  console.log(`窗口位置: ${x},${y}`)
})

win.on('ready-to-show', () => {
  win.show()
})
```

## 无边框窗口

```javascript [main.js]
const win = new BrowserWindow({
  frame: false,
  transparent: true,
  resizable: false
})
```

```html [index.html]
<div class="titlebar">
  <div class="title">我的应用</div>
  <div class="controls">
    <button id="minimize">─</button>
    <button id="maximize">□</button>
    <button id="close">✕</button>
  </div>
</div>
```

```css [styles.css]
.titlebar {
  -webkit-app-region: drag;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  background: #333;
  color: white;
}

.controls button {
  -webkit-app-region: no-drag;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 4px 8px;
}

.controls button:hover {
  background: rgba(255, 255, 255, 0.1);
}

#close:hover {
  background: #e81123;
}
```

```javascript [renderer.js]
document.getElementById('minimize').addEventListener('click', () => {
  window.electronAPI.minimize()
})

document.getElementById('maximize').addEventListener('click', () => {
  window.electronAPI.toggleMaximize()
})

document.getElementById('close').addEventListener('click', () => {
  window.electronAPI.close()
})
```

```javascript [preload.js]
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  minimize: () => ipcRenderer.send('window-minimize'),
  toggleMaximize: () => ipcRenderer.send('window-toggle-maximize'),
  close: () => ipcRenderer.send('window-close')
})
```

```javascript [main.js]
const { ipcMain } = require('electron')

ipcMain.on('window-minimize', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender)
  win?.minimize()
})

ipcMain.on('window-toggle-maximize', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender)
  if (win?.isMaximized()) {
    win.unmaximize()
  } else {
    win?.maximize()
  }
})

ipcMain.on('window-close', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender)
  win?.close()
})
```

## 子窗口

```javascript [main.js]
const parent = new BrowserWindow({ width: 800, height: 600 })

const child = new BrowserWindow({
  width: 400,
  height: 300,
  parent: parent,
  modal: true,
  show: false
})

child.loadFile('child.html')
child.once('ready-to-show', () => {
  child.show()
})
```

## 窗口截图

```javascript [main.js]
const win = new BrowserWindow({ width: 800, height: 600 })

async function captureWindow() {
  const image = await win.capturePage()
  const buffer = image.toPNG()
  require('fs').writeFileSync('screenshot.png', buffer)
}
```

