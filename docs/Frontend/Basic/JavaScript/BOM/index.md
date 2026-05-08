# JavaScript BOM 操作

## window 对象

```javascript [window.js]
// 全局对象
console.log(window === this)  // true

// 窗口尺寸
console.log(window.innerWidth)   // 视口宽度
console.log(window.innerHeight)  // 视口高度
console.log(window.outerWidth)   // 浏览器宽度
console.log(window.outerHeight)  // 浏览器高度

// 位置
console.log(window.screenX)  // 相对于屏幕 X
console.log(window.screenY)  // 相对于屏幕 Y

// 历史记录
console.log(window.history.length)

// 导航
console.log(window.navigator.userAgent)
```

## location 对象

```javascript [location.js]
// 当前 URL: https://example.com:8080/path?query=value#hash

console.log(location.href)      // 完整 URL
console.log(location.protocol)  // https:
console.log(location.host)      // example.com:8080
console.log(location.hostname)  // example.com
console.log(location.port)      // 8080
console.log(location.pathname)  // /path
console.log(location.search)    // ?query=value
console.log(location.hash)      // #hash

// 页面跳转
location.href = 'https://example.com'
location.assign('https://example.com')
location.replace('https://example.com')  // 不保留历史

// 刷新
location.reload()
location.reload(true)  // 强制从服务器刷新

// 解析 URL
const url = new URL('https://example.com:8080/path?query=value#hash')
console.log(url.searchParams.get('query'))  // value
```

## history 对象

```javascript [history.js]
// 前进/后退
history.back()
history.forward()
history.go(-1)   // 后退一步
history.go(1)    // 前进一步
history.go(2)    // 前进两步

// 历史记录数量
console.log(history.length)

// pushState
history.pushState({ page: 1 }, 'title', '/page1')

// replaceState
history.replaceState({ page: 2 }, 'title', '/page2')

// 监听历史变化
window.addEventListener('popstate', (e) => {
  console.log('历史变化:', e.state)
})

// SPA 路由示例
class Router {
  constructor() {
    window.addEventListener('popstate', (e) => {
      this.handleRoute(e.state?.path)
    })
  }

  navigate(path) {
    history.pushState({ path }, '', path)
    this.handleRoute(path)
  }

  handleRoute(path) {
    console.log('当前路由:', path)
  }
}
```

## navigator 对象

```javascript [navigator.js]
// 浏览器信息
console.log(navigator.userAgent)
console.log(navigator.appName)
console.log(navigator.appVersion)
console.log(navigator.platform)
console.log(navigator.language)

// 网络信息
navigator.connection?.addEventListener('change', () => {
  console.log('网络类型:', navigator.connection.effectiveType)
  console.log('下行速度:', navigator.connection.downlink)
})

// 电池信息
navigator.getBattery?.().then(battery => {
  console.log('电量:', battery.level * 100 + '%')
  console.log('充电中:', battery.charging)
})

// 剪贴板
navigator.clipboard.writeText('复制内容')
navigator.clipboard.readText().then(text => console.log(text))

// 地理位置
navigator.geolocation.getCurrentPosition(
  (pos) => console.log(pos.coords.latitude, pos.coords.longitude),
  (err) => console.error(err)
)

// 通知
Notification.requestPermission().then(permission => {
  if (permission === 'granted') {
    new Notification('通知标题', { body: '通知内容' })
  }
})
```

## screen 对象

```javascript [screen.js]
// 屏幕信息
console.log(screen.width)        // 屏幕宽度
console.log(screen.height)       // 屏幕高度
console.log(screen.availWidth)   // 可用宽度
console.log(screen.availHeight)  // 可用高度
console.log(screen.colorDepth)   // 颜色深度
console.log(screen.pixelDepth)   // 像素深度

// 全屏 API
document.documentElement.requestFullscreen()
document.exitFullscreen()
console.log(document.fullscreenElement)

// 屏幕方向
screen.orientation?.addEventListener('change', () => {
  console.log('屏幕方向:', screen.orientation.type)
})
```

## 窗口操作

```javascript [window-ops.js]
// 打开窗口
const newWindow = window.open('https://example.com', '_blank', 'width=800,height=600')

// 关闭窗口
newWindow.close()

// 窗口大小
window.resizeTo(800, 600)
window.resizeBy(100, 100)

// 窗口位置
window.moveTo(100, 100)
window.moveBy(50, 50)

// 滚动
window.scrollTo(0, 100)
window.scrollBy(0, 50)
window.scroll({ top: 0, left: 0, behavior: 'smooth' })

// 焦点
newWindow.focus()
window.blur()
```

## 定时器

```javascript [timer.js]
// setTimeout
const timeoutId = setTimeout(() => {
  console.log('1 秒后执行')
}, 1000)

// 清除
clearTimeout(timeoutId)

// setInterval
const intervalId = setInterval(() => {
  console.log('每 2 秒执行')
}, 2000)

// 清除
clearInterval(intervalId)

// Promise 封装
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function example() {
  await delay(1000)
  console.log('1 秒后')
}

// requestAnimationFrame
function animate() {
  element.style.transform = `translateX(${x}px)`
  requestAnimationFrame(animate)
}
requestAnimationFrame(animate)

// requestIdleCallback
requestIdleCallback((deadline) => {
  while (deadline.timeRemaining() > 0) {
    // 执行低优先级任务
  }
})
```

## 对话框

```javascript [dialog.js]
// alert
alert('提示信息')

// confirm
const result = confirm('确定要删除吗？')
if (result) {
  console.log('用户点击确定')
}

// prompt
const name = prompt('请输入姓名：')
if (name !== null) {
  console.log('用户输入:', name)
}

// 自定义对话框
function showDialog(title, message) {
  const dialog = document.createElement('dialog')
  dialog.innerHTML = `
    <h2>${title}</h2>
    <p>${message}</p>
    <button onclick="this.closest('dialog').close()">关闭</button>
  `
  document.body.appendChild(dialog)
  dialog.showModal()
}
```

## Storage API

```javascript [storage.js]
// localStorage（持久化）
localStorage.setItem('key', 'value')
localStorage.getItem('key')
localStorage.removeItem('key')
localStorage.clear()

// sessionStorage（会话）
sessionStorage.setItem('key', 'value')
sessionStorage.getItem('key')
sessionStorage.removeItem('key')
sessionStorage.clear()

// 监听变化
window.addEventListener('storage', (e) => {
  console.log('存储变化:', e.key, e.newValue)
})

// 封装
const storage = {
  get(key) {
    const value = localStorage.getItem(key)
    try {
      return JSON.parse(value)
    } catch {
      return value
    }
  },
  set(key, value) {
    localStorage.setItem(key, JSON.stringify(value))
  },
  remove(key) {
    localStorage.removeItem(key)
  }
}
```

## IndexedDB

```javascript [indexeddb.js]
// 打开数据库
const request = indexedDB.open('myDB', 1)

request.onupgradeneeded = (e) => {
  const db = e.target.result
  const store = db.createObjectStore('users', { keyPath: 'id' })
  store.createIndex('name', 'name', { unique: false })
}

request.onsuccess = (e) => {
  const db = e.target.result
  
  // 添加数据
  const tx = db.transaction('users', 'readwrite')
  const store = tx.objectStore('users')
  store.add({ id: 1, name: '张三', age: 25 })
  
  // 查询数据
  const getRequest = store.get(1)
  getRequest.onsuccess = () => {
    console.log(getRequest.result)
  }
}

// Promise 封装
function openDB(name, version, upgrade) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(name, version)
    request.onupgradeneeded = upgrade
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}
```

::: tip 提示
- 使用 location 对象处理 URL
- 使用 history API 实现 SPA 路由
- 使用 requestAnimationFrame 进行动画
- 使用 localStorage 存储简单数据
- 使用 IndexedDB 存储大量数据
:::
