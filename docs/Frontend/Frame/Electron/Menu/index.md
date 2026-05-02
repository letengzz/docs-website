# Electron 菜单与快捷键

## 应用菜单

### 创建菜单

```javascript [main.js]
const { app, BrowserWindow, Menu } = require('electron')

function createWindow() {
  const win = new BrowserWindow({ width: 800, height: 600 })
  win.loadFile('index.html')

  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '新建',
          accelerator: 'CmdOrCtrl+N',
          click: () => console.log('新建文件')
        },
        {
          label: '打开',
          accelerator: 'CmdOrCtrl+O',
          click: () => console.log('打开文件')
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { role: 'resetZoom' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '关于',
          click: () => console.log('关于')
        }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

app.whenReady().then(createWindow)
```

## 常用角色（Role）

| 角色 | 说明 | 快捷键 |
|------|------|--------|
| `undo` | 撤销 | Ctrl+Z |
| `redo` | 重做 | Ctrl+Y |
| `cut` | 剪切 | Ctrl+X |
| `copy` | 复制 | Ctrl+C |
| `paste` | 粘贴 | Ctrl+V |
| `selectAll` | 全选 | Ctrl+A |
| `reload` | 刷新 | Ctrl+R |
| `forceReload` | 强制刷新 | Ctrl+Shift+R |
| `toggleDevTools` | 开发者工具 | Ctrl+Shift+I |
| `zoomIn` | 放大 | Ctrl+= |
| `zoomOut` | 缩小 | Ctrl+- |
| `resetZoom` | 重置缩放 | Ctrl+0 |
| `togglefullscreen` | 全屏 | F11 |
| `minimize` | 最小化 | Ctrl+M |
| `close` | 关闭 | Ctrl+W |
| `quit` | 退出 | Ctrl+Q |

## 右键菜单

```javascript [main.js]
const { app, BrowserWindow, Menu } = require('electron')

function createWindow() {
  const win = new BrowserWindow({ width: 800, height: 600 })

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '复制',
      role: 'copy'
    },
    {
      label: '粘贴',
      role: 'paste'
    },
    { type: 'separator' },
    {
      label: '刷新',
      role: 'reload'
    },
    {
      label: '开发者工具',
      role: 'toggleDevTools'
    }
  ])

  win.webContents.on('context-menu', (event, params) => {
    contextMenu.popup({
      window: win,
      x: params.x,
      y: params.y
    })
  })

  win.loadFile('index.html')
}

app.whenReady().then(createWindow)
```

## 快捷键

### 全局快捷键

```javascript [main.js]
const { app, BrowserWindow, globalShortcut } = require('electron')

app.whenReady().then(() => {
  const win = new BrowserWindow({ width: 800, height: 600 })
  win.loadFile('index.html')

  globalShortcut.register('CommandOrControl+Shift+K', () => {
    console.log('全局快捷键触发')
    win.webContents.send('shortcut-triggered')
  })

  globalShortcut.register('CommandOrControl+Alt+M', () => {
    win.minimize()
  })
})

app.on('will-quit', () => {
  globalShortcut.unregisterAll()
})
```

### 检查快捷键

```javascript [main.js]
const isRegistered = globalShortcut.isRegistered('CommandOrControl+Shift+K')
console.log('快捷键是否已注册:', isRegistered)
```

### 注销快捷键

```javascript [main.js]
globalShortcut.unregister('CommandOrControl+Shift+K')
globalShortcut.unregisterAll()
```

## 菜单项选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `label` | string | 菜单项文本 |
| `type` | string | 类型：normal/separator/submenu/checkbox/radio |
| `click` | function | 点击回调 |
| `accelerator` | string | 快捷键 |
| `role` | string | 预定义角色 |
| `visible` | boolean | 是否可见 |
| `enabled` | boolean | 是否可用 |
| `checked` | boolean | 是否选中（checkbox/radio） |
| `submenu` | array | 子菜单 |

## 动态菜单

```javascript [main.js]
const { app, BrowserWindow, Menu } = require('electron')

let menu

function createWindow() {
  const win = new BrowserWindow({ width: 800, height: 600 })

  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '新建',
          accelerator: 'CmdOrCtrl+N',
          click: () => console.log('新建')
        },
        {
          label: '保存',
          accelerator: 'CmdOrCtrl+S',
          enabled: false,
          id: 'save-item'
        }
      ]
    }
  ]

  menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)

  win.loadFile('index.html')
}

function enableSaveItem() {
  const saveItem = menu.getMenuItemById('save-item')
  if (saveItem) {
    saveItem.enabled = true
  }
}

app.whenReady().then(createWindow)
```

