# Electron 通知系统

## 系统通知

```javascript [main.js]
const { Notification } = require('electron')

function showNotification() {
  const notification = new Notification({
    title: '通知标题',
    body: '这是通知内容',
    icon: './assets/icon.png',
    silent: false,
    urgency: 'normal'
  })

  notification.show()
}
```

## 通知选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `title` | string | 通知标题 |
| `body` | string | 通知内容 |
| `icon` | string | 通知图标 |
| `silent` | boolean | 是否静音 |
| `urgency` | string | 优先级：low/normal/critical |
| `timeoutType` | string | 超时类型：default/never |
| `replyPlaceholder` | string | 回复占位符 |
| `hasReply` | boolean | 是否显示回复框 |
| `sound` | string | 提示音文件 |

## 通知事件

```javascript [main.js]
const { Notification } = require('electron')

function showNotification() {
  const notification = new Notification({
    title: '新消息',
    body: '您有一条新消息',
    icon: './assets/icon.png',
    hasReply: true,
    replyPlaceholder: '回复消息...'
  })

  notification.on('show', () => {
    console.log('通知已显示')
  })

  notification.on('click', () => {
    console.log('通知被点击')
  })

  notification.on('close', () => {
    console.log('通知已关闭')
  })

  notification.on('reply', (event, reply) => {
    console.log('用户回复:', reply)
  })

  notification.on('action', (event, index) => {
    console.log('用户点击了操作按钮:', index)
  })

  notification.show()
}
```

## 从渲染进程发送通知

```javascript [preload.js]
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  showNotification: (options) => ipcRenderer.invoke('show-notification', options)
})
```

```javascript [main.js]
const { ipcMain, Notification } = require('electron')

ipcMain.handle('show-notification', async (event, options) => {
  const notification = new Notification(options)
  notification.show()
  return true
})
```

```javascript [renderer.js]
window.electronAPI.showNotification({
  title: '下载完成',
  body: '文件已成功下载',
  icon: './assets/icon.png'
})
```

## HTML5 通知

```javascript [renderer.js]
if (Notification.permission === 'granted') {
  new Notification('标题', {
    body: '内容',
    icon: './assets/icon.png'
  })
} else if (Notification.permission !== 'denied') {
  Notification.requestPermission().then(permission => {
    if (permission === 'granted') {
      new Notification('标题', {
        body: '内容'
      })
    }
  })
}
```

## 通知权限

```javascript [main.js]
const { Notification } = require('electron')

console.log('通知权限:', Notification.isSupported())
```

## 批量通知

```javascript [main.js]
const { Notification } = require('electron')

function showNotifications(messages) {
  messages.forEach((msg, index) => {
    setTimeout(() => {
      const notification = new Notification({
        title: msg.title,
        body: msg.body
      })
      notification.show()
    }, index * 1000)
  })
}

showNotifications([
  { title: '消息 1', body: '这是第一条消息' },
  { title: '消息 2', body: '这是第二条消息' },
  { title: '消息 3', body: '这是第三条消息' }
])
```

