# XMLHttpRequest

XMLHttpRequest（XHR）是浏览器提供的用于与服务器交换数据的 API。

- MDN 文档：https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest

## 创建 XMLHttpRequest

### 基本语法

```javascript [create.js]
const xhr = new XMLHttpRequest()
```

### 兼容性处理

```javascript [compatibility.js]
let xhr

if (window.XMLHttpRequest) {
  // 现代浏览器
  xhr = new XMLHttpRequest()
} else {
  // IE6 及以下
  xhr = new ActiveXObject('Microsoft.XMLHTTP')
}
```

## 发送请求

### GET 请求

```javascript [get.js]
const xhr = new XMLHttpRequest()

// 初始化请求
xhr.open('GET', '/api/users?id=1', true)

// 发送请求
xhr.send()

// 监听响应
xhr.onload = function() {
  if (xhr.status === 200) {
    console.log(xhr.responseText)
  }
}
```

### POST 请求

```javascript [post.js]
const xhr = new XMLHttpRequest()

xhr.open('POST', '/api/users', true)

// 设置请求头
xhr.setRequestHeader('Content-Type', 'application/json')

// 发送数据
const data = JSON.stringify({
  name: '张三',
  age: 25
})

xhr.send(data)

xhr.onload = function() {
  if (xhr.status === 200) {
    console.log(xhr.responseText)
  }
}
```

## 请求参数

### open() 方法

```javascript [open.js]
xhr.open(method, url, async, user, password)
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| method | String | ✅ | HTTP 方法（GET、POST、PUT、DELETE） |
| url | String | ✅ | 请求地址 |
| async | Boolean | ❌ | 是否异步，默认 true |
| user | String | ❌ | 用户名 |
| password | String | ❌ | 密码 |

### setRequestHeader() 方法

```javascript [headers.js]
// 设置单个请求头
xhr.setRequestHeader('Content-Type', 'application/json')

// 设置多个请求头
xhr.setRequestHeader('Authorization', 'Bearer token123')
xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
```

### send() 方法

```javascript [send.js]
// 发送无数据请求
xhr.send()

// 发送字符串数据
xhr.send('name=张三&age=25')

// 发送 JSON 数据
xhr.send(JSON.stringify({ name: '张三', age: 25 }))

// 发送 FormData
const formData = new FormData()
formData.append('name', '张三')
formData.append('avatar', fileInput.files[0])
xhr.send(formData)
```

## 响应处理

### 响应属性

```javascript [response.js]
xhr.onload = function() {
  // 响应状态码
  console.log(xhr.status)        // 200
  console.log(xhr.statusText)    // "OK"
  
  // 响应数据
  console.log(xhr.responseText)  // 字符串
  console.log(xhr.responseXML)   // XML 文档
  console.log(xhr.response)      // 根据 responseType
  
  // 响应头
  console.log(xhr.getAllResponseHeaders())
  console.log(xhr.getResponseHeader('Content-Type'))
}
```

### responseType 设置

```javascript [responseType.js]
const xhr = new XMLHttpRequest()

// 设置响应类型
xhr.responseType = 'json'  // 自动解析 JSON
xhr.responseType = 'blob'  // 二进制数据
xhr.responseType = 'arraybuffer'  // ArrayBuffer
xhr.responseType = 'document'     // XML 文档

xhr.open('GET', '/api/users')
xhr.send()

xhr.onload = function() {
  // 根据 responseType 自动解析
  console.log(xhr.response)
}
```

## 事件监听

### 常用事件

```javascript [events.js]
const xhr = new XMLHttpRequest()

// 请求开始
xhr.onloadstart = function() {
  console.log('请求开始')
}

// 请求进度
xhr.onprogress = function(e) {
  if (e.lengthComputable) {
    const percent = (e.loaded / e.total) * 100
    console.log(`下载进度：${percent.toFixed(2)}%`)
  }
}

// 请求完成
xhr.onload = function() {
  console.log('请求成功')
  console.log(xhr.responseText)
}

// 请求失败
xhr.onerror = function() {
  console.log('请求失败')
}

// 请求超时
xhr.ontimeout = function() {
  console.log('请求超时')
}

// 请求中止
xhr.onabort = function() {
  console.log('请求中止')
}

// 请求结束（无论成功失败）
xhr.onloadend = function() {
  console.log('请求结束')
}
```

### readyState 状态

```javascript [readystate.js]
const xhr = new XMLHttpRequest()

xhr.onreadystatechange = function() {
  switch (xhr.readyState) {
    case 0: // UNSENT - 未初始化
      console.log('请求未初始化')
      break
    case 1: // OPENED - 已打开
      console.log('已调用 open()')
      break
    case 2: // HEADERS_RECEIVED - 已获取头
      console.log('已获取响应头')
      break
    case 3: // LOADING - 加载中
      console.log('正在下载响应体')
      break
    case 4: // DONE - 完成
      console.log('请求完成')
      if (xhr.status === 200) {
        console.log(xhr.responseText)
      }
      break
  }
}

xhr.open('GET', '/api/users')
xhr.send()
```

## 超时设置

```javascript [timeout.js]
const xhr = new XMLHttpRequest()

// 设置超时时间（毫秒）
xhr.timeout = 5000

xhr.ontimeout = function() {
  console.log('请求超时')
}

xhr.open('GET', '/api/users')
xhr.send()
```

## 中止请求

```javascript [abort.js]
const xhr = new XMLHttpRequest()

xhr.open('GET', '/api/users')
xhr.send()

// 中止请求
xhr.abort()

xhr.onabort = function() {
  console.log('请求已中止')
}
```

## 文件上传

### 上传进度

```javascript [upload.js]
const xhr = new XMLHttpRequest()

// 监听上传进度
xhr.upload.onprogress = function(e) {
  if (e.lengthComputable) {
    const percent = (e.loaded / e.total) * 100
    console.log(`上传进度：${percent.toFixed(2)}%`)
  }
}

xhr.onload = function() {
  if (xhr.status === 200) {
    console.log('上传成功')
  }
}

const formData = new FormData()
formData.append('file', fileInput.files[0])

xhr.open('POST', '/api/upload')
xhr.send(formData)
```

### 拖拽上传

```javascript [drag-drop.js]
const dropZone = document.getElementById('drop-zone')

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault()
  dropZone.classList.add('drag-over')
})

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over')
})

dropZone.addEventListener('drop', (e) => {
  e.preventDefault()
  dropZone.classList.remove('drag-over')
  
  const files = e.dataTransfer.files
  const formData = new FormData()
  
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i])
  }
  
  const xhr = new XMLHttpRequest()
  xhr.open('POST', '/api/upload')
  xhr.send(formData)
})
```

## 完整示例

```javascript [full-example.js]
function ajax(options) {
  const {
    url,
    method = 'GET',
    data = null,
    headers = {},
    timeout = 0,
    onSuccess,
    onError,
    onProgress
  } = options
  
  const xhr = new XMLHttpRequest()
  
  // 处理 GET 请求参数
  let requestUrl = url
  if (method.toUpperCase() === 'GET' && data) {
    const params = new URLSearchParams(data).toString()
    requestUrl += (url.includes('?') ? '&' : '?') + params
  }
  
  xhr.open(method, requestUrl, true)
  
  // 设置请求头
  for (const key in headers) {
    xhr.setRequestHeader(key, headers[key])
  }
  
  // 设置超时
  if (timeout > 0) {
    xhr.timeout = timeout
  }
  
  // 监听响应
  xhr.onload = function() {
    if (xhr.status >= 200 && xhr.status < 300) {
      onSuccess && onSuccess(xhr.response)
    } else {
      onError && onError(xhr)
    }
  }
  
  xhr.onerror = function() {
    onError && onError(xhr)
  }
  
  xhr.ontimeout = function() {
    onError && onError(xhr, 'timeout')
  }
  
  // 监听进度
  if (onProgress) {
    xhr.onprogress = onProgress
  }
  
  // 发送请求
  xhr.send(method.toUpperCase() === 'GET' ? null : data)
  
  return xhr
}

// 使用示例
ajax({
  url: '/api/users',
  method: 'POST',
  data: JSON.stringify({ name: '张三' }),
  headers: { 'Content-Type': 'application/json' },
  timeout: 5000,
  onSuccess: (res) => console.log('成功:', res),
  onError: (err) => console.error('失败:', err)
})
```

::: tip 提示
- XMLHttpRequest 兼容性最好，支持所有浏览器
- 现代项目推荐使用 Fetch API 或 Axios
- 文件上传时可使用 upload.onprogress 监听进度
:::
