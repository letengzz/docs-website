# Electron 系统托盘

## 创建托盘

```javascript [main.js]
const { app, BrowserWindow, Tray, Menu } = require('electron')
const path = require('path')

let tray

function createTray() {
  tray = new Tray(path.join(__dirname, 'assets', 'icon.png'))

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '打开应用',
      click: () => {
        const win = BrowserWindow.getAllWindows()[0]
        if (win) {
          win.show()
          win.focus()
        }
      }
    },
    {
      label: '隐藏应用',
      click: () => {
        const win = BrowserWindow.getAllWindows()[0]
        if (win) {
          win.hide()
        }
      }
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => app.quit()
    }
  ])

  tray.setToolTip('我的应用')
  tray.setContextMenu(contextMenu)
}

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    show: false
  })

  win.loadFile('index.html')

  win.once('ready-to-show', () => {
    win.show()
  })

  win.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault()
      win.hide()
    }
  })
}

app.whenReady().then(() => {
  createWindow()
  createTray()
})
```

## 托盘事件

```javascript [main.js]
const { Tray, Menu } = require('electron')

const tray = new Tray('./assets/icon.png')

tray.on('click', () => {
  console.log('托盘图标被点击')
  const win = BrowserWindow.getAllWindows()[0]
  if (win) {
    win.show()
    win.focus()
  }
})

tray.on('double-click', () => {
  console.log('托盘图标被双击')
})

tray.on('right-click', () => {
  console.log('托盘图标被右键点击')
  tray.popUpContextMenu()
})

tray.on('balloon-click', () => {
  console.log('气泡通知被点击')
})
```

## 托盘图标

### 动态图标

```javascript [main.js]
const { Tray, nativeImage } = require('electron')

const tray = new Tray('./assets/icon.png')

let isOnline = true

function updateTrayIcon() {
  const icon = isOnline
    ? nativeImage.createFromPath('./assets/icon-online.png')
    : nativeImage.createFromPath('./assets/icon-offline.png')
  tray.setImage(icon)
}

setInterval(() => {
  isOnline = !isOnline
  updateTrayIcon()
}, 5000)
```

### 模板图标（macOS）

```javascript [main.js]
const { Tray, nativeImage } = require('electron')

const image = nativeImage.createFromPath('./assets/iconTemplate.png')
image.setTemplateImage(true)

const tray = new Tray(image)
```

## 气泡通知

```javascript [main.js]
const { Tray } = require('electron')

const tray = new Tray('./assets/icon.png')

tray.displayBalloon({
  icon: './assets/icon.png',
  title: '通知标题',
  content: '这是通知内容',
  largeIcon: true,
  noSound: false,
  respectQuietTime: true
})
```

## 托盘标题

```javascript [main.js]
const { Tray } = require('electron')

const tray = new Tray('./assets/icon.png')

tray.setTitle('我的应用')
tray.setToolTip('鼠标悬停提示文本')
```

## 关闭窗口到托盘

```javascript [main.js]
const { app, BrowserWindow, Tray, Menu } = require('electron')

let tray
let mainWindow

function createTray() {
  tray = new Tray('./assets/icon.png')

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示窗口',
      click: () => {
        mainWindow.show()
        mainWindow.focus()
      }
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        app.isQuitting = true
        app.quit()
      }
    }
  ])

  tray.setContextMenu(contextMenu)
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600
  })

  mainWindow.loadFile('index.html')

  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault()
      mainWindow.hide()
    }
  })
}

app.whenReady().then(() => {
  createWindow()
  createTray()
})
```

## 平台差异

| 功能 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 托盘图标 | 支持 | 支持 | 支持 |
| 气泡通知 | 支持 | 不支持 | 支持 |
| 模板图标 | 不支持 | 支持 | 不支持 |
| 右键菜单 | 支持 | 支持 | 支持 |
| 双击事件 | 支持 | 支持 | 支持 |

## 下一步

- [Electron 对话框](Dialog/index.md) - 学习对话框
- [Electron 通知系统](Notification/index.md) - 学习通知系统
