# Electron 剪贴板

## 读取剪贴板

```javascript [main.js]
const { clipboard } = require('electron')

// 读取文本
const text = clipboard.readText()
console.log('剪贴板文本:', text)

// 读取 HTML
const html = clipboard.readHTML()
console.log('剪贴板 HTML:', html)

// 读取 RTF
const rtf = clipboard.readRTF()
console.log('剪贴板 RTF:', rtf)

// 读取图片
const image = clipboard.readImage()
console.log('剪贴板图片:', image)

// 读取书签
const bookmark = clipboard.readBookmark()
console.log('剪贴板书签:', bookmark)
```

## 写入剪贴板

```javascript [main.js]
const { clipboard, nativeImage } = require('electron')

// 写入文本
clipboard.writeText('Hello, Electron!')

// 写入 HTML
clipboard.writeHTML('<b>Hello</b> <i>Electron!</i>')

// 写入 RTF
clipboard.writeRTF('{\\rtf1\\ansi {\\b Hello} Electron!}')

// 写入图片
const image = nativeImage.createFromPath('./assets/icon.png')
clipboard.writeImage(image)

// 写入书签
clipboard.writeBookmark({
  title: 'Electron 官网',
  url: 'https://www.electronjs.org'
})
```

## 从渲染进程操作剪贴板

```javascript [preload.js]
const { contextBridge, clipboard } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  readText: () => clipboard.readText(),
  writeText: (text) => clipboard.writeText(text),
  readHTML: () => clipboard.readHTML(),
  writeHTML: (html) => clipboard.writeHTML(html),
  clear: () => clipboard.clear()
})
```

```javascript [renderer.js]
// 读取剪贴板
const text = window.electronAPI.readText()
console.log('剪贴板内容:', text)

// 写入剪贴板
window.electronAPI.writeText('这是要复制的内容')

// 清空剪贴板
window.electronAPI.clear()
```

## 剪贴板事件

```javascript [main.js]
const { clipboard } = require('electron')

// 监听剪贴板变化
let lastText = clipboard.readText()

setInterval(() => {
  const currentText = clipboard.readText()
  if (currentText !== lastText) {
    console.log('剪贴板内容已变化:', currentText)
    lastText = currentText
  }
}, 500)
```

## 清空剪贴板

```javascript [main.js]
const { clipboard } = require('electron')

clipboard.clear()
```

## 检查剪贴板格式

```javascript [main.js]
const { clipboard } = require('electron')

// 检查是否有文本
const hasText = clipboard.has('text/plain')
console.log('是否有文本:', hasText)

// 检查是否有 HTML
const hasHTML = clipboard.has('text/html')
console.log('是否有 HTML:', hasHTML)

// 检查是否有图片
const hasImage = clipboard.has('image/png')
console.log('是否有图片:', hasImage)
```

## 复制文件路径

```javascript [main.js]
const { clipboard } = require('electron')

clipboard.writeBuffer(
  'FileNameW',
  Buffer.from('C:\\path\\to\\file.txt\0', 'ucs2')
)
```

