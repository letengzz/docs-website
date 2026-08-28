# Ajax 概述

Ajax（Asynchronous JavaScript and XML）是一种在无需重新加载整个网页的情况下，能够更新部分网页的技术。

## 什么是 Ajax

Ajax 不是一种新的编程语言，而是一种用于创建更好更快以及交互性更强的 Web 应用程序的技术。

使用 Ajax，JavaScript 可以直接与服务器进行数据交换，实现：

- 在不重新加载页面的情况下更新网页
- 在页面已加载后从服务器请求数据
- 在页面已加载后从服务器接收数据
- 在后台向服务器发送数据

## Ajax 工作原理

```text
用户操作 → JavaScript → XMLHttpRequest/Fetch → 服务器
                                    ↓
用户界面 ← JavaScript ← 响应数据 ← 服务器
```

## Ajax 的优势

| 优势 | 说明 |
|------|------|
| 局部刷新 | 无需重新加载整个页面 |
| 异步通信 | 不阻塞用户操作 |
| 减少带宽 | 只传输必要的数据 |
| 提升体验 | 响应更快，交互更流畅 |

## Ajax 的应用场景

- 表单验证（用户名是否可用）
- 搜索建议（自动补全）
- 无限滚动（加载更多数据）
- 实时通知（消息推送）
- 文件上传（进度显示）

## Ajax 技术栈

### 1. XMLHttpRequest

传统的 Ajax 实现方式，兼容性最好。

```javascript [xhr.js]
const xhr = new XMLHttpRequest()
xhr.open('GET', '/api/users')
xhr.send()

xhr.onload = function() {
  if (xhr.status === 200) {
    console.log(xhr.responseText)
  }
}
```

### 2. Fetch API

现代浏览器提供的原生 API，基于 Promise。

```javascript [fetch.js]
fetch('/api/users')
  .then(res => res.json())
  .then(data => console.log(data))
```

### 3. Axios

第三方库，功能最完善，支持浏览器和 Node.js。

```javascript [axios.js]
import axios from 'axios'

axios.get('/api/users')
  .then(res => console.log(res.data))
```

## 同源策略

Ajax 请求受到同源策略的限制：

| URL | 是否同源 | 说明 |
|-----|---------|------|
| http://example.com/a | ✅ | 相同 |
| http://example.com/b | ✅ | 路径不同但同源 |
| https://example.com/a | ❌ | 协议不同 |
| http://example.com:8080/a | ❌ | 端口不同 |
| http://api.example.com/a | ❌ | 域名不同 |

## 跨域解决方案

### 1. CORS（跨域资源共享）

服务器设置响应头允许跨域。

```javascript [cors.js]
// 服务器端设置
res.setHeader('Access-Control-Allow-Origin', '*')
res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
```

### 2. JSONP

利用 script 标签不受同源策略限制的特性。

```javascript [jsonp.js]
function handleResponse(data) {
  console.log(data)
}

const script = document.createElement('script')
script.src = 'http://api.example.com/data?callback=handleResponse'
document.body.appendChild(script)
```

### 3. 代理服务器

通过同源服务器转发请求。

```javascript [proxy.js]
// Nginx 配置
server {
    location /api {
        proxy_pass http://api.example.com;
    }
}
```

::: tip 提示
- 现代项目推荐使用 Axios 或 Fetch API
- 需要兼容老浏览器时使用 XMLHttpRequest
- 跨域问题优先使用 CORS 解决
:::

## 相关专题

- [浏览器原理](../../Browser/index.md)
