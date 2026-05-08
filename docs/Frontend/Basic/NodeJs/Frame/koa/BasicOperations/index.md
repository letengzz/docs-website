# Koa 基础操作

## 安装与启动

```shell [install.sh]
npm i koa
```

```js [app.js]
const Koa = require('koa')
const app = new Koa()

app.use(async (ctx) => {
  ctx.body = 'Hello Koa'
})

app.listen(3000, () => {
  console.log('服务启动在 3000 端口')
})
```

## 路由处理

### 基本路由

```js [routes.js]
const Koa = require('koa')
const app = new Koa()

app.use(async (ctx) => {
  if (ctx.path === '/') {
    ctx.body = '首页'
  } else if (ctx.path === '/about') {
    ctx.body = '关于页面'
  } else if (ctx.path === '/contact') {
    ctx.body = '联系我们'
  } else {
    ctx.status = 404
    ctx.body = '页面不存在'
  }
})

app.listen(3000)
```

### 使用 koa-router

```shell [install-router.sh]
npm i koa-router
```

```js [router.js]
const Koa = require('koa')
const Router = require('koa-router')

const app = new Koa()
const router = new Router()

// GET 请求
router.get('/', (ctx) => {
  ctx.body = '首页'
})

router.get('/users', (ctx) => {
  ctx.body = '用户列表'
})

router.get('/users/:id', (ctx) => {
  ctx.body = `用户 ${ctx.params.id}`
})

// POST 请求
router.post('/users', (ctx) => {
  ctx.body = '创建用户'
})

// PUT 请求
router.put('/users/:id', (ctx) => {
  ctx.body = `更新用户 ${ctx.params.id}`
})

// DELETE 请求
router.delete('/users/:id', (ctx) => {
  ctx.body = `删除用户 ${ctx.params.id}`
})

app.use(router.routes())
app.use(router.allowedMethods())

app.listen(3000)
```

## 获取请求参数

### 查询参数

```js [query.js]
const Koa = require('koa')
const app = new Koa()

app.use(async (ctx) => {
  // 获取查询参数
  const { page, limit, sort } = ctx.query
  
  ctx.body = {
    page: page || 1,
    limit: limit || 10,
    sort: sort || 'desc'
  }
})

app.listen(3000)

// 访问 /users?page=2&limit=20
// 返回 { page: '2', limit: '20', sort: 'desc' }
```

### 路径参数

```js [params.js]
const Koa = require('koa')
const Router = require('koa-router')

const app = new Koa()
const router = new Router()

router.get('/users/:id', (ctx) => {
  ctx.body = `用户ID: ${ctx.params.id}`
})

router.get('/users/:userId/posts/:postId', (ctx) => {
  ctx.body = {
    userId: ctx.params.userId,
    postId: ctx.params.postId
  }
})

app.use(router.routes())
app.listen(3000)
```

### 请求体数据

```shell [install-body.sh]
npm i koa-body
```

```js [body.js]
const Koa = require('koa')
const koaBody = require('koa-body')

const app = new Koa()

// 使用 body 解析中间件
app.use(koaBody({
  multipart: true,
  formidable: {
    maxFileSize: 10 * 1024 * 1024 // 10MB
  }
}))

app.use(async (ctx) => {
  if (ctx.method === 'POST') {
    ctx.body = {
      message: '接收成功',
      data: ctx.request.body
    }
  }
})

app.listen(3000)
```

## 响应设置

### 设置状态码

```js [status.js]
app.use(async (ctx) => {
  ctx.status = 200 // 成功
  ctx.status = 201 // 创建成功
  ctx.status = 400 // 请求错误
  ctx.status = 404 // 未找到
  ctx.status = 500 // 服务器错误
})
```

### 设置响应头

```js [headers.js]
app.use(async (ctx) => {
  ctx.set('Content-Type', 'application/json')
  ctx.set('X-Custom-Header', 'custom-value')
  ctx.body = { message: 'success' }
})
```

### 响应类型

```js [response-types.js]
app.use(async (ctx) => {
  // 字符串响应
  ctx.body = 'Hello World'
  
  // JSON 响应
  ctx.body = { name: '张三', age: 25 }
  
  // HTML 响应
  ctx.type = 'html'
  ctx.body = '<h1>Hello</h1>'
  
  // 文件响应
  ctx.body = fs.createReadStream('./file.txt')
})
```

## 完整示例

```js [full-example.js]
const Koa = require('koa')
const Router = require('koa-router')
const koaBody = require('koa-body')

const app = new Koa()
const router = new Router()

// 使用 body 解析
app.use(koaBody())

// 路由
router.get('/users', (ctx) => {
  ctx.body = {
    users: [
      { id: 1, name: '张三' },
      { id: 2, name: '李四' }
    ]
  }
})

router.get('/users/:id', (ctx) => {
  ctx.body = {
    id: ctx.params.id,
    name: '张三'
  }
})

router.post('/users', (ctx) => {
  const { name, age } = ctx.request.body
  ctx.status = 201
  ctx.body = {
    id: Date.now(),
    name,
    age
  }
})

// 使用路由
app.use(router.routes())
app.use(router.allowedMethods())

// 404 处理
app.use(async (ctx) => {
  ctx.status = 404
  ctx.body = { error: '路由不存在' }
})

app.listen(3000, () => {
  console.log('服务启动')
})
```

::: tip 提示
- Koa 本身不包含路由，需要使用 koa-router
- 使用 koa-body 解析请求体
- Context 对象封装了 request 和 response
:::
