# Fetch API

Fetch API 是现代浏览器提供的基于 Promise 的网络请求 API。

- MDN 文档：https://developer.mozilla.org/zh-CN/docs/Web/API/Fetch_API

## Fetch 基础

### 基本语法

```javascript [basic.js]
fetch(url)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error))
```

### async/await 写法

```javascript [async.js]
async function fetchData() {
  try {
    const response = await fetch('/api/users')
    const data = await response.json()
    console.log(data)
  } catch (error) {
    console.error(error)
  }
}

fetchData()
```

## 请求配置

### GET 请求

```javascript [get.js]
// 基本 GET 请求
fetch('/api/users')
  .then(res => res.json())
  .then(data => console.log(data))

// 带查询参数
const params = new URLSearchParams({
  page: 1,
  limit: 10
})

fetch(`/api/users?${params}`)
  .then(res => res.json())
  .then(data => console.log(data))
```

### POST 请求

```javascript [post.js]
fetch('/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: '张三',
    age: 25
  })
})
  .then(res => res.json())
  .then(data => console.log(data))
```

### 请求选项

```javascript [options.js]
fetch('/api/users', {
  method: 'GET',           // 请求方法
  headers: {               // 请求头
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token123'
  },
  body: JSON.stringify({}), // 请求体
  mode: 'cors',            // 请求模式
  credentials: 'include',  // 是否携带 cookie
  cache: 'no-cache',       // 缓存模式
  redirect: 'follow',      // 重定向模式
  referrer: 'no-referrer', // referrer 信息
  integrity: '',           // 资源完整性校验
  timeout: 5000            // 超时时间（非标准）
})
```

## 响应处理

### Response 对象

```javascript [response.js]
fetch('/api/users')
  .then(response => {
    console.log(response.ok)          // 是否成功（200-299）
    console.log(response.status)      // 状态码
    console.log(response.statusText)  // 状态文本
    console.log(response.headers)     // 响应头
    console.log(response.type)        // 响应类型
    console.log(response.url)         // 请求 URL
    
    // 解析响应体
    return response.json()
  })
  .then(data => console.log(data))
```

### 解析响应体

```javascript [parse.js]
// JSON 数据
fetch('/api/users')
  .then(res => res.json())
  .then(data => console.log(data))

// 文本数据
fetch('/api/text')
  .then(res => res.text())
  .then(text => console.log(text))

// Blob 数据（图片、文件等）
fetch('/api/image')
  .then(res => res.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob)
    img.src = url
  })

// ArrayBuffer 数据
fetch('/api/binary')
  .then(res => res.arrayBuffer())
  .then(buffer => console.log(buffer))

// FormData 数据
fetch('/api/form')
  .then(res => res.formData())
  .then(formData => console.log(formData))
```

## 请求头操作

### 设置请求头

```javascript [headers.js]
const headers = new Headers({
  'Content-Type': 'application/json',
  'Authorization': 'Bearer token123'
})

// 添加请求头
headers.append('X-Custom-Header', 'value')

// 检查请求头
headers.has('Content-Type')  // true

// 获取请求头
headers.get('Content-Type')  // 'application/json'

// 删除请求头
headers.delete('X-Custom-Header')

fetch('/api/users', { headers })
```

### 读取响应头

```javascript [response-headers.js]
fetch('/api/users')
  .then(response => {
    // 获取单个响应头
    console.log(response.headers.get('Content-Type'))
    
    // 遍历所有响应头
    for (const [key, value] of response.headers) {
      console.log(`${key}: ${value}`)
    }
  })
```

## 错误处理

### 基本错误处理

```javascript [error.js]
fetch('/api/users')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  })
  .then(data => console.log(data))
  .catch(error => console.error('Fetch error:', error))
```

### async/await 错误处理

```javascript [async-error.js]
async function fetchData() {
  try {
    const response = await fetch('/api/users')
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    console.log(data)
  } catch (error) {
    console.error('Fetch error:', error)
  }
}
```

## 超时处理

```javascript [timeout.js]
// 使用 AbortController 实现超时
function fetchWithTimeout(url, options = {}, timeout = 5000) {
  const controller = new AbortController()
  const { signal } = controller
  
  const timer = setTimeout(() => controller.abort(), timeout)
  
  return fetch(url, { ...options, signal })
    .finally(() => clearTimeout(timer))
}

// 使用
fetchWithTimeout('/api/users', {}, 5000)
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => {
    if (err.name === 'AbortError') {
      console.error('请求超时')
    } else {
      console.error('请求失败', err)
    }
  })
```

## 取消请求

```javascript [cancel.js]
const controller = new AbortController()
const { signal } = controller

fetch('/api/users', { signal })
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => {
    if (err.name === 'AbortError') {
      console.log('请求已取消')
    }
  })

// 取消请求
controller.abort()
```

## 并发请求

### Promise.all

```javascript [promise-all.js]
async function fetchMultiple() {
  const [users, posts, comments] = await Promise.all([
    fetch('/api/users').then(res => res.json()),
    fetch('/api/posts').then(res => res.json()),
    fetch('/api/comments').then(res => res.json())
  ])
  
  console.log(users, posts, comments)
}
```

### Promise.allSettled

```javascript [promise-allsettled.js]
async function fetchAllSettled() {
  const results = await Promise.allSettled([
    fetch('/api/users').then(res => res.json()),
    fetch('/api/posts').then(res => res.json()),
    fetch('/api/comments').then(res => res.json())
  ])
  
  results.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      console.log(`请求 ${index} 成功:`, result.value)
    } else {
      console.log(`请求 ${index} 失败:`, result.reason)
    }
  })
}
```

## 文件上传

### 上传文件

```javascript [upload.js]
const fileInput = document.getElementById('file-input')

fileInput.addEventListener('change', async () => {
  const file = fileInput.files[0]
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    })
    
    const data = await response.json()
    console.log('上传成功:', data)
  } catch (error) {
    console.error('上传失败:', error)
  }
})
```

### 上传进度

```javascript [upload-progress.js]
const fileInput = document.getElementById('file-input')

fileInput.addEventListener('change', async () => {
  const file = fileInput.files[0]
  const formData = new FormData()
  formData.append('file', file)
  
  // 使用 XMLHttpRequest 监听进度
  const xhr = new XMLHttpRequest()
  
  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
      const percent = (e.loaded / e.total) * 100
      console.log(`上传进度：${percent.toFixed(2)}%`)
    }
  }
  
  xhr.onload = () => {
    if (xhr.status === 200) {
      console.log('上传成功')
    }
  }
  
  xhr.open('POST', '/api/upload')
  xhr.send(formData)
})
```

## 完整封装

```javascript [fetch-wrapper.js]
class HttpClient {
  constructor(baseURL = '') {
    this.baseURL = baseURL
  }

  async request(url, options = {}) {
    const fullUrl = this.baseURL + url
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    }
    
    const config = { ...defaultOptions, ...options }
    
    // 处理 body
    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }
    
    try {
      const response = await fetch(fullUrl, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      return data
    } catch (error) {
      console.error('Request failed:', error)
      throw error
    }
  }

  get(url, options = {}) {
    return this.request(url, { ...options, method: 'GET' })
  }

  post(url, data, options = {}) {
    return this.request(url, { ...options, method: 'POST', body: data })
  }

  put(url, data, options = {}) {
    return this.request(url, { ...options, method: 'PUT', body: data })
  }

  delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' })
  }
}

// 使用
const http = new HttpClient('https://api.example.com')

// GET 请求
http.get('/users')
  .then(data => console.log(data))

// POST 请求
http.post('/users', { name: '张三' })
  .then(data => console.log(data))

// async/await
async function fetchUsers() {
  const users = await http.get('/users')
  console.log(users)
}
```

## Fetch vs XMLHttpRequest

| 特性 | Fetch | XMLHttpRequest |
|------|-------|----------------|
| API 风格 | Promise | 回调 |
| 代码简洁 | ✅ | ❌ |
| 错误处理 | 需手动判断 | 自动 |
| 超时控制 | 需 AbortController | 内置 timeout |
| 进度监听 | 不支持 | 支持 |
| 取消请求 | AbortController | abort() |
| 兼容性 | 现代浏览器 | 所有浏览器 |

::: tip 提示
- Fetch 是现代浏览器推荐使用的 API
- 需要兼容老浏览器时使用 XMLHttpRequest
- 复杂项目推荐使用 Axios 等第三方库
:::
