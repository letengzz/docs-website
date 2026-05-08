# JavaScript 存储机制

## 存储方式对比

| 特性 | Cookie | localStorage | sessionStorage | IndexedDB |
|------|--------|--------------|----------------|-----------|
| 容量 | 4KB | 5-10MB | 5-10MB | 无限制 |
| 有效期 | 可设置 | 永久 | 会话结束 | 永久 |
| 服务端访问 | 是 | 否 | 否 | 否 |
| 数据类型 | 字符串 | 字符串 | 字符串 | 任意类型 |
| API | 原始 | 简单 | 简单 | 复杂 |

## Cookie

```javascript [cookie.js]
// 设置 Cookie
document.cookie = 'name=张三; path=/; max-age=3600'
document.cookie = 'age=25; path=/; expires=Fri, 31 Dec 2024 23:59:59 GMT'

// 读取 Cookie
console.log(document.cookie)  // "name=张三; age=25"

// 删除 Cookie
document.cookie = 'name=; path=/; max-age=0'

// 封装
const Cookie = {
  set(name, value, options = {}) {
    const { path = '/', maxAge, expires, domain, secure, httpOnly } = options
    let cookie = `${name}=${encodeURIComponent(value)}; path=${path}`
    if (maxAge) cookie += `; max-age=${maxAge}`
    if (expires) cookie += `; expires=${expires.toUTCString()}`
    if (domain) cookie += `; domain=${domain}`
    if (secure) cookie += `; secure`
    if (httpOnly) cookie += `; httponly`  // 只能服务端设置
    document.cookie = cookie
  },

  get(name) {
    const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]*)(;|$)`))
    return match ? decodeURIComponent(match[2]) : null
  },

  remove(name, path = '/') {
    this.set(name, '', { path, maxAge: 0 })
  }
}

// 使用
Cookie.set('token', 'abc123', { maxAge: 7 * 24 * 3600 })
console.log(Cookie.get('token'))
Cookie.remove('token')
```

## localStorage

```javascript [localstorage.js]
// 基础操作
localStorage.setItem('name', '张三')
localStorage.setItem('age', '25')

console.log(localStorage.getItem('name'))  // 张三
console.log(localStorage.getItem('age'))   // 25

localStorage.removeItem('name')
localStorage.clear()

// 存储对象
const user = { name: '张三', age: 25 }
localStorage.setItem('user', JSON.stringify(user))

const storedUser = JSON.parse(localStorage.getItem('user'))
console.log(storedUser.name)  // 张三

// 遍历
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i)
  console.log(key, localStorage.getItem(key))
}

// 监听变化
window.addEventListener('storage', (e) => {
  console.log('存储变化:', e.key, e.newValue, e.oldValue)
})

// 封装
const Storage = {
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
  },

  clear() {
    localStorage.clear()
  }
}
```

## sessionStorage

```javascript [sessionstorage.js]
// 基础操作
sessionStorage.setItem('temp', '临时数据')
console.log(sessionStorage.getItem('temp'))

sessionStorage.removeItem('temp')
sessionStorage.clear()

// 页面间通信（同标签页）
window.addEventListener('storage', (e) => {
  if (e.storageArea === sessionStorage) {
    console.log('sessionStorage 变化:', e.key)
  }
})

// 表单数据暂存
const form = document.querySelector('#myForm')
form.addEventListener('input', (e) => {
  sessionStorage.setItem(`form_${e.target.name}`, e.target.value)
})

// 恢复表单
window.addEventListener('load', () => {
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i)
    if (key.startsWith('form_')) {
      const name = key.replace('form_', '')
      const input = form.querySelector(`[name="${name}"]`)
      if (input) input.value = sessionStorage.getItem(key)
    }
  }
})
```

## IndexedDB

```javascript [indexeddb.js]
// 打开数据库
const request = indexedDB.open('myApp', 1)

request.onupgradeneeded = (e) => {
  const db = e.target.result
  
  // 创建对象仓库
  const userStore = db.createObjectStore('users', { keyPath: 'id' })
  userStore.createIndex('name', 'name', { unique: false })
  userStore.createIndex('email', 'email', { unique: true })
  
  const postStore = db.createObjectStore('posts', { keyPath: 'id' })
  postStore.createIndex('userId', 'userId', { unique: false })
  postStore.createIndex('createdAt', 'createdAt', { unique: false })
}

request.onsuccess = (e) => {
  const db = e.target.result
  console.log('数据库打开成功')
}

request.onerror = (e) => {
  console.error('数据库打开失败:', e.target.error)
}

// 添加数据
function addUser(user) {
  return new Promise((resolve, reject) => {
    const db = request.result
    const tx = db.transaction('users', 'readwrite')
    const store = tx.objectStore('users')
    
    const addRequest = store.add(user)
    addRequest.onsuccess = () => resolve(addRequest.result)
    addRequest.onerror = () => reject(addRequest.error)
  })
}

// 查询数据
function getUser(id) {
  return new Promise((resolve, reject) => {
    const db = request.result
    const tx = db.transaction('users', 'readonly')
    const store = tx.objectStore('users')
    
    const getRequest = store.get(id)
    getRequest.onsuccess = () => resolve(getRequest.result)
    getRequest.onerror = () => reject(getRequest.error)
  })
}

// 使用索引查询
function getUsersByName(name) {
  return new Promise((resolve, reject) => {
    const db = request.result
    const tx = db.transaction('users', 'readonly')
    const store = tx.objectStore('users')
    const index = store.index('name')
    
    const getRequest = index.getAll(name)
    getRequest.onsuccess = () => resolve(getRequest.result)
    getRequest.onerror = () => reject(getRequest.error)
  })
}

// 更新数据
function updateUser(user) {
  return new Promise((resolve, reject) => {
    const db = request.result
    const tx = db.transaction('users', 'readwrite')
    const store = tx.objectStore('users')
    
    const putRequest = store.put(user)
    putRequest.onsuccess = () => resolve(putRequest.result)
    putRequest.onerror = () => reject(putRequest.error)
  })
}

// 删除数据
function deleteUser(id) {
  return new Promise((resolve, reject) => {
    const db = request.result
    const tx = db.transaction('users', 'readwrite')
    const store = tx.objectStore('users')
    
    const deleteRequest = store.delete(id)
    deleteRequest.onsuccess = () => resolve()
    deleteRequest.onerror = () => reject(deleteRequest.error)
  })
}

// 游标遍历
function getAllUsers() {
  return new Promise((resolve, reject) => {
    const db = request.result
    const tx = db.transaction('users', 'readonly')
    const store = tx.objectStore('users')
    
    const users = []
    const cursorRequest = store.openCursor()
    
    cursorRequest.onsuccess = (e) => {
      const cursor = e.target.result
      if (cursor) {
        users.push(cursor.value)
        cursor.continue()
      } else {
        resolve(users)
      }
    }
    
    cursorRequest.onerror = () => reject(cursorRequest.error)
  })
}
```

## Cache API

```javascript [cache.js]
// 打开缓存
caches.open('my-cache-v1').then(cache => {
  // 添加资源
  cache.add('/index.html')
  cache.addAll(['/style.css', '/script.js', '/image.png'])
  
  // 缓存请求
  cache.put('/api/data', new Response(JSON.stringify({ data: 'test' })))
  
  // 匹配缓存
  cache.match('/index.html').then(response => {
    if (response) {
      response.text().then(text => console.log(text))
    }
  })
  
  // 删除缓存
  cache.delete('/index.html')
})

// 管理缓存
caches.keys().then(names => {
  console.log('所有缓存:', names)
})

caches.delete('my-cache-v1').then(success => {
  console.log('缓存删除:', success)
})

// Service Worker 中使用
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).then(fetchResponse => {
        return caches.open('v1').then(cache => {
          cache.put(event.request, fetchResponse.clone())
          return fetchResponse
        })
      })
    })
  )
})
```

## 存储策略

```javascript [storage-strategy.js]
// 缓存策略
class StorageStrategy {
  // 先缓存后网络
  async cacheFirst(request) {
    const cache = await caches.open('v1')
    const cached = await cache.match(request)
    if (cached) return cached
    
    const response = await fetch(request)
    cache.put(request, response.clone())
    return response
  }

  // 先网络后缓存
  async networkFirst(request) {
    try {
      const response = await fetch(request)
      const cache = await caches.open('v1')
      cache.put(request, response.clone())
      return response
    } catch {
      const cache = await caches.open('v1')
      return cache.match(request)
    }
  }

  // 缓存和网络并行
  async cacheAndNetwork(request) {
    const cachePromise = caches.match(request)
    const fetchPromise = fetch(request).then(response => {
      caches.open('v1').then(cache => cache.put(request, response.clone()))
      return response
    })
    
    return Promise.race([cachePromise, fetchPromise])
  }
}

// 数据同步
class SyncManager {
  constructor() {
    this.pending = []
  }

  async add(task) {
    this.pending.push(task)
    await this.save()
  }

  async save() {
    localStorage.setItem('pending_tasks', JSON.stringify(this.pending))
  }

  async sync() {
    while (this.pending.length > 0) {
      const task = this.pending.shift()
      try {
        await task.execute()
      } catch (error) {
        this.pending.unshift(task)
        break
      }
    }
    await this.save()
  }
}
```

::: tip 提示
- 小数据使用 localStorage/sessionStorage
- 大数据使用 IndexedDB
- 需要服务端交互使用 Cookie
- 使用 Cache API 缓存静态资源
- 注意存储容量限制
:::
