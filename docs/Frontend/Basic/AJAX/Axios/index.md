# Axios

Axios 是一个基于 Promise 的 HTTP 客户端，用于浏览器和 Node.js。

- 官网：https://axios-http.com/
- GitHub：https://github.com/axios/axios

## Axios 安装

### npm 安装

```shell [install.sh]
npm install axios
```

### CDN 引入

```html [cdn.html]
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
```

## Axios 基本使用

### GET 请求

```javascript [get.js]
import axios from 'axios'

// 基本 GET 请求
axios.get('/api/users')
  .then(response => console.log(response.data))
  .catch(error => console.error(error))

// 带参数
axios.get('/api/users', {
  params: {
    page: 1,
    limit: 10
  }
})
  .then(response => console.log(response.data))

// async/await
async function fetchUsers() {
  try {
    const response = await axios.get('/api/users', {
      params: { page: 1 }
    })
    console.log(response.data)
  } catch (error) {
    console.error(error)
  }
}
```

### POST 请求

```javascript [post.js]
import axios from 'axios'

// 基本 POST 请求
axios.post('/api/users', {
  name: '张三',
  age: 25
})
  .then(response => console.log(response.data))

// async/await
async function createUser() {
  try {
    const response = await axios.post('/api/users', {
      name: '张三',
      age: 25
    })
    console.log(response.data)
  } catch (error) {
    console.error(error)
  }
}
```

### 通用请求方式

```javascript [request.js]
import axios from 'axios'

axios({
  method: 'get',
  url: '/api/users',
  params: { page: 1 }
})

axios({
  method: 'post',
  url: '/api/users',
  data: { name: '张三' }
})
```

## 请求配置

### 完整配置选项

```javascript [config.js]
axios({
  url: '/api/users',              // 请求 URL
  method: 'get',                  // 请求方法
  baseURL: 'https://api.example.com', // 基础 URL
  headers: {                      // 请求头
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token'
  },
  params: {                       // URL 参数
    page: 1
  },
  data: {                         // 请求体
    name: '张三'
  },
  timeout: 5000,                  // 超时时间
  responseType: 'json',           // 响应类型
  withCredentials: true,          // 是否携带 cookie
  validateStatus: function(status) {
    return status >= 200 && status < 300 // 默认
  }
})
```

## 创建实例

### 基本实例

```javascript [instance.js]
import axios from 'axios'

const api = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 使用实例
api.get('/users')
  .then(response => console.log(response.data))

api.post('/users', { name: '张三' })
  .then(response => console.log(response.data))
```

### 多实例

```javascript [multi-instance.js]
import axios from 'axios'

// 公共 API 实例
const publicApi = axios.create({
  baseURL: 'https://public-api.example.com'
})

// 私有 API 实例
const privateApi = axios.create({
  baseURL: 'https://private-api.example.com',
  headers: {
    'Authorization': 'Bearer token123'
  }
})

// 使用
publicApi.get('/public/users')
privateApi.get('/private/profile')
```

## 拦截器

### 请求拦截器

```javascript [request-interceptor.js]
import axios from 'axios'

// 添加请求拦截器
axios.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    // 对请求错误做些什么
    return Promise.reject(error)
  }
)
```

### 响应拦截器

```javascript [response-interceptor.js]
import axios from 'axios'

// 添加响应拦截器
axios.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    return response.data
  },
  error => {
    // 对响应错误做点什么
    if (error.response) {
      switch (error.response.status) {
        case 401:
          console.error('未授权，请重新登录')
          // 跳转到登录页
          break
        case 403:
          console.error('拒绝访问')
          break
        case 404:
          console.error('请求地址不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
      }
    }
    return Promise.reject(error)
  }
)
```

### 移除拦截器

```javascript [remove-interceptor.js]
const interceptor = axios.interceptors.request.use(config => config)

// 移除拦截器
axios.interceptors.request.eject(interceptor)
```

## 取消请求

### AbortController

```javascript [cancel.js]
const controller = new AbortController()

axios.get('/api/users', {
  signal: controller.signal
})
  .then(response => console.log(response.data))
  .catch(error => {
    if (axios.isCancel(error)) {
      console.log('请求已取消')
    }
  })

// 取消请求
controller.abort()
```

### CancelToken（旧版）

```javascript [cancel-token.js]
const CancelToken = axios.CancelToken
const source = CancelToken.source()

axios.get('/api/users', {
  cancelToken: source.token
})
  .then(response => console.log(response.data))
  .catch(error => {
    if (axios.isCancel(error)) {
      console.log('请求已取消')
    }
  })

// 取消请求
source.cancel('请求已取消')
```

## 并发请求

### axios.all

```javascript [concurrent.js]
import axios from 'axios'

async function fetchMultiple() {
  const [users, posts] = await axios.all([
    axios.get('/api/users'),
    axios.get('/api/posts')
  ])
  
  console.log(users.data, posts.data)
}

// 或使用 Promise.all
async function fetchMultipleWithPromiseAll() {
  const [users, posts] = await Promise.all([
    axios.get('/api/users'),
    axios.get('/api/posts')
  ])
  
  console.log(users.data, posts.data)
}
```

## 文件上传

### 上传文件

```javascript [upload.js]
import axios from 'axios'

const fileInput = document.getElementById('file-input')

fileInput.addEventListener('change', async () => {
  const file = fileInput.files[0]
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    console.log('上传成功:', response.data)
  } catch (error) {
    console.error('上传失败:', error)
  }
})
```

### 上传进度

```javascript [upload-progress.js]
import axios from 'axios'

const fileInput = document.getElementById('file-input')

fileInput.addEventListener('change', async () => {
  const file = fileInput.files[0]
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const percent = (progressEvent.loaded / progressEvent.total) * 100
        console.log(`上传进度：${percent.toFixed(2)}%`)
      }
    })
    console.log('上传成功:', response.data)
  } catch (error) {
    console.error('上传失败:', error)
  }
})
```

## 完整封装示例

### 基础封装

```javascript [request.js]
import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

// 创建实例
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const { data } = response
    
    if (data.code !== 200) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    
    return data
  },
  error => {
    let message = error.message
    
    if (message === 'Network Error') {
      message = '网络异常'
    } else if (message.includes('timeout')) {
      message = '请求超时'
    } else if (error.response) {
      switch (error.response.status) {
        case 401:
          message = '未授权'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求不存在'
          break
        case 500:
          message = '服务器错误'
          break
      }
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service
```

### API 模块

```javascript [api.js]
import request from './request'

// 获取用户列表
export function getUsers(params) {
  return request({
    url: '/api/users',
    method: 'get',
    params
  })
}

// 创建用户
export function createUser(data) {
  return request({
    url: '/api/users',
    method: 'post',
    data
  })
}

// 更新用户
export function updateUser(id, data) {
  return request({
    url: `/api/users/${id}`,
    method: 'put',
    data
  })
}

// 删除用户
export function deleteUser(id) {
  return request({
    url: `/api/users/${id}`,
    method: 'delete'
  })
}
```

### 页面调用

```vue [page.vue]
<script setup>
import { ref, onMounted } from 'vue'
import { getUsers, createUser } from '@/api/user'

const users = ref([])

onMounted(async () => {
  try {
    const data = await getUsers({ page: 1 })
    users.value = data.list
  } catch (error) {
    console.error(error)
  }
})

const handleCreate = async () => {
  try {
    await createUser({ name: '张三' })
    // 刷新列表
    const data = await getUsers({ page: 1 })
    users.value = data.list
  } catch (error) {
    console.error(error)
  }
}
</script>
```

## Axios vs Fetch vs XMLHttpRequest

| 特性 | Axios | Fetch | XMLHttpRequest |
|------|-------|-------|----------------|
| 基于 Promise | ✅ | ✅ | ❌ |
| 拦截器 | ✅ | ❌ | ❌ |
| 自动转换 JSON | ✅ | 需手动 | ❌ |
| 请求取消 | ✅ | ✅ | ✅ |
| 进度监听 | ✅ | ❌ | ✅ |
| 超时处理 | ✅ | 需封装 | ✅ |
| 浏览器兼容 | 现代 | 现代 | 所有 |
| Node.js 支持 | ✅ | ❌ | ❌ |

::: tip 提示
- 现代项目推荐使用 Axios
- 需要兼容老浏览器时使用 XMLHttpRequest
- 简单场景可使用原生 Fetch API
:::
