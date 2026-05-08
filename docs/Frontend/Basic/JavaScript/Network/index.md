# JavaScript 网络请求

## XMLHttpRequest

```javascript [xhr.js]
// 基础 GET 请求
const xhr = new XMLHttpRequest()
xhr.open('GET', '/api/users', true)
xhr.onload = function() {
  if (xhr.status === 200) {
    console.log(JSON.parse(xhr.responseText))
  }
}
xhr.onerror = function() {
  console.error('请求失败')
}
xhr.send()

// POST 请求
const xhr2 = new XMLHttpRequest()
xhr2.open('POST', '/api/users', true)
xhr2.setRequestHeader('Content-Type', 'application/json')
xhr2.onload = function() {
  console.log(JSON.parse(xhr2.responseText))
}
xhr2.send(JSON.stringify({ name: '张三', age: 25 }))

// 进度监听
const xhr3 = new XMLHttpRequest()
xhr3.open('GET', '/api/large-file', true)
xhr3.onprogress = function(e) {
  if (e.lengthComputable) {
    const percent = (e.loaded / e.total) * 100
    console.log(`下载进度：${percent.toFixed(2)}%`)
  }
}
xhr3.send()
```

## Fetch API

```javascript [fetch.js]
// 基础 GET 请求
fetch('/api/users')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return response.json()
  })
  .then(data => console.log(data))
  .catch(error => console.error(error))

// async/await
async function fetchUsers() {
  try {
    const response = await fetch('/api/users')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('请求失败:', error)
  }
}

// POST 请求
async function createUser(user) {
  const response = await fetch('/api/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(user)
  })
  return response.json()
}

// 其他方法
fetch('/api/users/1', { method: 'PUT', body: JSON.stringify(user) })
fetch('/api/users/1', { method: 'DELETE' })

// 响应类型
fetch('/api/data')
  .then(response => response.json())    // JSON
  .then(response => response.text())    // 文本
  .then(response => response.blob())    // 二进制
  .then(response => response.formData())// 表单数据
  .then(response => response.arrayBuffer()) // ArrayBuffer
```

## 请求配置

```javascript [fetch-config.js]
// 完整配置
fetch('/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token123',
    'X-Custom-Header': 'value'
  },
  body: JSON.stringify({ name: '张三' }),
  mode: 'cors',           // cors, no-cors, same-origin
  credentials: 'include', // include, same-origin, omit
  cache: 'no-cache',      // default, no-cache, reload, force-cache
  redirect: 'follow',     // follow, error, manual
  referrerPolicy: 'no-referrer',
  signal: AbortSignal.timeout(5000)  // 超时控制
})

// 超时控制
const controller = new AbortController()
const timeoutId = setTimeout(() => controller.abort(), 5000)

fetch('/api/users', { signal: controller.signal })
  .then(response => response.json())
  .catch(error => {
    if (error.name === 'AbortError') {
      console.error('请求超时')
    }
  })
  .finally(() => clearTimeout(timeoutId))
```

## 封装请求

```javascript [request.js]
class HttpClient {
  constructor(baseURL) {
    this.baseURL = baseURL
    this.interceptors = {
      request: [],
      response: []
    }
  }

  use(type, fn) {
    this.interceptors[type].push(fn)
  }

  async request(url, options = {}) {
    const fullURL = `${this.baseURL}${url}`
    const config = {
      headers: { 'Content-Type': 'application/json' },
      ...options
    }

    // 请求拦截
    for (const interceptor of this.interceptors.request) {
      interceptor(config)
    }

    try {
      const response = await fetch(fullURL, config)
      
      // 响应拦截
      for (const interceptor of this.interceptors.response) {
        interceptor(response)
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('请求失败:', error)
      throw error
    }
  }

  get(url, params) {
    const query = new URLSearchParams(params).toString()
    return this.request(query ? `${url}?${query}` : url)
  }

  post(url, data) {
    return this.request(url, { method: 'POST', body: JSON.stringify(data) })
  }

  put(url, data) {
    return this.request(url, { method: 'PUT', body: JSON.stringify(data) })
  }

  delete(url) {
    return this.request(url, { method: 'DELETE' })
  }
}

// 使用
const api = new HttpClient('https://api.example.com')

api.use('request', (config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
})

api.use('response', (response) => {
  if (response.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }
})

const users = await api.get('/users', { page: 1 })
```

## 文件上传

```javascript [upload.js]
// 单文件上传
async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  })

  return response.json()
}

// 多文件上传
async function uploadFiles(files) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }

  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  })

  return response.json()
}

// 带进度
function uploadWithProgress(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/upload')

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        onProgress((e.loaded / e.total) * 100)
      }
    }

    xhr.onload = () => resolve(JSON.parse(xhr.responseText))
    xhr.onerror = () => reject(new Error('上传失败'))

    const formData = new FormData()
    formData.append('file', file)
    xhr.send(formData)
  })
}
```

## WebSocket

```javascript [websocket.js]
// 创建连接
const ws = new WebSocket('ws://localhost:8080')

// 连接成功
ws.onopen = () => {
  console.log('连接成功')
  ws.send(JSON.stringify({ type: 'login', user: '张三' }))
}

// 接收消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('收到消息:', data)
}

// 连接关闭
ws.onclose = () => {
  console.log('连接关闭')
}

// 连接错误
ws.onerror = (error) => {
  console.error('连接错误:', error)
}

// 封装
class WebSocketClient {
  constructor(url) {
    this.url = url
    this.handlers = {}
  }

  connect() {
    this.ws = new WebSocket(this.url)
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (this.handlers[data.type]) {
        this.handlers[data.type](data)
      }
    }
  }

  on(type, handler) {
    this.handlers[type] = handler
  }

  send(type, data) {
    this.ws.send(JSON.stringify({ type, ...data }))
  }

  close() {
    this.ws.close()
  }
}
```

## Server-Sent Events

```javascript [sse.js]
// 创建连接
const eventSource = new EventSource('/api/events')

// 接收消息
eventSource.onmessage = (event) => {
  console.log('收到消息:', event.data)
}

// 特定事件
eventSource.addEventListener('update', (event) => {
  console.log('更新:', event.data)
})

// 连接状态
eventSource.onopen = () => console.log('连接成功')
eventSource.onerror = () => console.error('连接错误')

// 关闭连接
eventSource.close()
```

## 网络状态

```javascript [network-status.js]
// 在线状态
window.addEventListener('online', () => {
  console.log('网络已连接')
})

window.addEventListener('offline', () => {
  console.log('网络已断开')
})

console.log(navigator.onLine)  // true/false

// 网络信息
if (navigator.connection) {
  console.log('网络类型:', navigator.connection.effectiveType)
  console.log('下行速度:', navigator.connection.downlink)
  console.log('延迟:', navigator.connection.rtt)
  
  navigator.connection.addEventListener('change', () => {
    console.log('网络变化:', navigator.connection.effectiveType)
  })
}
```

::: tip 提示
- 优先使用 Fetch API 替代 XMLHttpRequest
- 使用 async/await 简化异步代码
- 实现请求拦截器处理认证和错误
- 使用 AbortController 控制请求超时
- 大文件上传使用 FormData 和进度监听
:::
