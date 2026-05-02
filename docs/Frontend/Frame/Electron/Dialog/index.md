# Electron 对话框

## 文件对话框

### 打开文件

```javascript [main.js]
const { dialog, BrowserWindow } = require('electron')

async function openFile() {
  const result = await dialog.showOpenDialog({
    title: '选择文件',
    buttonLabel: '打开',
    filters: [
      { name: '文本文件', extensions: ['txt', 'md'] },
      { name: '所有文件', extensions: ['*'] }
    ],
    properties: ['openFile', 'multiSelections']
  })

  if (!result.canceled) {
    console.log('选择的文件:', result.filePaths)
  }
}
```

### 保存文件

```javascript [main.js]
const { dialog, BrowserWindow } = require('electron')

async function saveFile() {
  const result = await dialog.showSaveDialog({
    title: '保存文件',
    buttonLabel: '保存',
    defaultPath: 'untitled.txt',
    filters: [
      { name: '文本文件', extensions: ['txt'] },
      { name: '所有文件', extensions: ['*'] }
    ]
  })

  if (!result.canceled) {
    console.log('保存路径:', result.filePath)
  }
}
```

### 选择文件夹

```javascript [main.js]
const { dialog } = require('electron')

async function selectFolder() {
  const result = await dialog.showOpenDialog({
    title: '选择文件夹',
    properties: ['openDirectory']
  })

  if (!result.canceled) {
    console.log('选择的文件夹:', result.filePaths)
  }
}
```

### 对话框选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `title` | string | 对话框标题 |
| `buttonLabel` | string | 按钮文本 |
| `defaultPath` | string | 默认路径 |
| `filters` | array | 文件过滤器 |
| `properties` | array | 对话框属性 |

### 常用属性

| 属性 | 说明 |
|------|------|
| `openFile` | 允许选择文件 |
| `openDirectory` | 允许选择文件夹 |
| `multiSelections` | 允许多选 |
| `showHiddenFiles` | 显示隐藏文件 |
| `createDirectory` | 允许创建文件夹 |
| `promptToCreate` | 提示创建文件 |
| `noResolveAliases` | 不解析别名 |
| `treatPackageAsDirectory` | 将包视为目录 |

## 消息对话框

```javascript [main.js]
const { dialog, BrowserWindow } = require('electron')

async function showMessage() {
  const result = await dialog.showMessageBox({
    type: 'info',
    title: '提示',
    message: '操作成功！',
    detail: '您的文件已成功保存。',
    buttons: ['确定', '取消'],
    defaultId: 0,
    cancelId: 1,
    checkboxLabel: '不再提示',
    checkboxChecked: false
  })

  console.log('用户点击了:', result.response)
  console.log('复选框状态:', result.checkboxChecked)
}
```

### 消息类型

| 类型 | 说明 | 图标 |
|------|------|------|
| `none` | 无类型 | 无 |
| `info` | 信息 | ℹ️ |
| `error` | 错误 | ❌ |
| `question` | 问题 | ❓ |
| `warning` | 警告 | ⚠️ |

### 确认对话框

```javascript [main.js]
const { dialog } = require('electron')

async function confirmAction() {
  const result = await dialog.showMessageBox({
    type: 'warning',
    title: '确认删除',
    message: '确定要删除此文件吗？',
    detail: '此操作不可撤销。',
    buttons: ['删除', '取消'],
    defaultId: 1,
    cancelId: 1
  })

  if (result.response === 0) {
    console.log('用户确认删除')
  }
}
```

## 错误对话框

```javascript [main.js]
const { dialog } = require('electron')

function showError(error) {
  dialog.showErrorBox(
    '错误',
    `发生错误：${error.message}\n\n请检查日志文件获取更多信息。`
  )
}
```

## 从渲染进程调用对话框

```javascript [preload.js]
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  saveFile: (content) => ipcRenderer.invoke('dialog:saveFile', content),
  showMessage: (options) => ipcRenderer.invoke('dialog:showMessage', options)
})
```

```javascript [main.js]
const { ipcMain, dialog } = require('electron')
const fs = require('fs')

ipcMain.handle('dialog:openFile', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [{ name: '文本文件', extensions: ['txt'] }]
  })
  return result.canceled ? null : result.filePaths[0]
})

ipcMain.handle('dialog:saveFile', async (event, content) => {
  const result = await dialog.showSaveDialog({
    filters: [{ name: '文本文件', extensions: ['txt'] }]
  })

  if (!result.canceled && result.filePath) {
    fs.writeFileSync(result.filePath, content)
    return true
  }
  return false
})

ipcMain.handle('dialog:showMessage', async (event, options) => {
  const result = await dialog.showMessageBox(options)
  return result.response
})
```

```javascript [renderer.js]
async function handleOpenFile() {
  const filePath = await window.electronAPI.openFile()
  if (filePath) {
    console.log('选择的文件:', filePath)
  }
}

async function handleSaveFile(content) {
  const saved = await window.electronAPI.saveFile(content)
  if (saved) {
    console.log('文件已保存')
  }
}
```

