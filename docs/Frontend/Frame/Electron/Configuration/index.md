# Electron 配置

## 窗口配置

**官方文档**：https://www.electronjs.org/zh/docs/latest/api/base-window#%E5%AE%9E%E4%BE%8B%E5%B1%9E%E6%80%A7

创建窗口配置：

```javascript [main.js]
const { app, BrowserWindow } = require('electron')

app.whenReady().then(() => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    autoHideMenuBar: true,
    x: 0,
    y: 0,
    alwaysOnTop: true,
    frame: false,
    transparent: true,
    resizable: false,
    minimizable: false,
    maximizable: false,
    closable: true,
    focusable: true,
    show: false,
    backgroundColor: '#ffffff',
    icon: './assets/icon.png',
    title: '我的应用',
    webPreferences: {
      preload: './preload.js',
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  })

  win.once('ready-to-show', () => {
    win.show()
  })

  win.loadURL('https://www.baidu.com')
})
```

## 常用窗口选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `width` | number | 800 | 窗口宽度 |
| `height` | number | 600 | 窗口高度 |
| `x` | number | 居中 | 窗口 X 坐标 |
| `y` | number | 居中 | 窗口 Y 坐标 |
| `frame` | boolean | true | 是否显示窗口边框 |
| `transparent` | boolean | false | 是否透明窗口 |
| `resizable` | boolean | true | 是否可调整大小 |
| `minimizable` | boolean | true | 是否可最小化 |
| `maximizable` | boolean | true | 是否可最大化 |
| `closable` | boolean | true | 是否可关闭 |
| `focusable` | boolean | true | 是否可聚焦 |
| `show` | boolean | true | 创建后是否立即显示 |
| `alwaysOnTop` | boolean | false | 是否始终置顶 |
| `fullscreen` | boolean | false | 是否全屏 |
| `fullscreenable` | boolean | true | 是否可全屏 |
| `kiosk` | boolean | false | 是否 Kiosk 模式 |
| `title` | string | - | 窗口标题 |
| `icon` | string | - | 窗口图标 |
| `backgroundColor` | string | - | 背景颜色 |

## 退出应用配置

### Windows 和 Linux

关闭所有窗口时退出应用：

```javascript [main.js]
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
```

### macOS

即使在没有打开任何窗口的情况下也继续运行：

```javascript [main.js]
function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    autoHideMenuBar: true
  })

  win.loadFile('./page/index.html')
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})
```

## 加载本地页面

在 `page` 文件夹中创建 `index.html`：

```html [page/index.html]
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;" />
    <title>Electron 应用</title>
    <link rel="stylesheet" href="./index.css" />
  </head>
  <body>
    <h1>欢迎学习 Electron</h1>
  </body>
</html>
```

```css [page/index.css]
h1 {
  background-color: gray;
  color: orange;
}
```

```javascript [main.js]
const { app, BrowserWindow } = require('electron')
const path = require('path')

app.whenReady().then(() => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    autoHideMenuBar: true
  })

  win.loadFile(path.join(__dirname, 'page', 'index.html'))
})
```

## CSP 配置

打开开发者模式时出现 `Electron Security Warning (Insecure Content-Security-Policy)` 警告：

![安全警告](assets/img202406272039200.png)

解决办法：配置 CSP (Content-Security-Policy)

```html [index.html]
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
/>
```

说明：

1. `default-src 'self'`：配置加载策略，适用于所有未在其它指令中明确指定的资源类型。`self` 表示仅允许从同源的资源加载。
2. `style-src 'self' 'unsafe-inline'`：指定样式表（CSS）的加载策略，允许内联样式。
3. `img-src 'self' data:`：指定图像资源的加载策略，允许使用 data: URI 嵌入图像。

参考文档：

- https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Content-Security-Policy
- https://www.electronjs.org/docs/latest/tutorial/security

## 配置自动重启

1. 安装 Nodemon

   ```bash [终端]
   npm i nodemon -D
   ```

2. 修改 `package.json` 命令

   ```json [package.json]
   {
     "scripts": {
       "start": "nodemon --exec electron ."
     }
   }
   ```

3. 配置 `nodemon.json` 规则

   ```json [nodemon.json]
   {
     "ignore": ["node_modules", "dist"],
     "restartable": "r",
     "watch": ["*.*"],
     "ext": "html,js,css"
   }
   ```

配置好以后，当代码修改后，应用就会自动重启，或者在控制台输入 `r` 重启。

## 环境变量配置

```javascript [main.js]
const isDev = process.env.NODE_ENV === 'development'

app.whenReady().then(() => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      devTools: isDev
    }
  })

  if (isDev) {
    win.loadURL('http://localhost:5173')
  } else {
    win.loadFile(path.join(__dirname, 'dist', 'index.html'))
  }
})
```

## 多窗口管理

```javascript [main.js]
const windows = new Set()

function createWindow(url) {
  const win = new BrowserWindow({
    width: 800,
    height: 600
  })

  windows.add(win)
  win.loadURL(url)

  win.on('closed', () => {
    windows.delete(win)
  })

  return win
}

app.whenReady().then(() => {
  createWindow('https://example.com')
  createWindow('https://example.org')
})
```

