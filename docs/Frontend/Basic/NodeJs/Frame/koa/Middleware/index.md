# Koa 中间件

Koa 的中间件采用洋葱模型，与 Express 的线性模型不同。

## 洋葱模型

请求从外到内穿过中间件，响应从内到外返回：

```js [onion.js]
const Koa = require('koa')
const app = new Koa()

app.use(async (ctx, next) => {
  console.log('1. 中间件1 - 请求进入')
  await next()
  console.log('4. 中间件1 - 响应返回')
})

app.use(async (ctx, next) => {
  console.log('2. 中间件2 - 请求进入')
  await next()
  console.log('3. 中间件2 - 响应返回')
})

app.use(async (ctx) => {
  console.log('核心处理')
  ctx.body = 'Hello Koa'
})

// 执行顺序：
// 1. 中间件1 - 请求进入
// 2. 中间件2 - 请求进入
// 核心处理
// 3. 中间件2 - 响应返回
// 4. 中间件1 - 响应返回
```

## 常用中间件

### koa-body

解析请求体数据：

```shell [install.sh]
npm i koa-body
```

```js [body.js]
const koaBody = require('koa-body')

app.use(koaBody({
  multipart: true,
  formidable: {
    maxFileSize: 10 * 1024 * 1024
  }
}))
```

### koa-static

静态文件服务：

```shell [install-static.sh]
npm i koa-static
```

```js [static.js]
const serve = require('koa-static')
const path = require('path')

// 托管 public 目录
app.use(serve(path.join(__dirname, 'public')))
```

### koa-logger

日志记录：

```shell [install-logger.sh]
npm i koa-logger
```

```js [logger.js]
const logger = require('koa-logger')

app.use(logger())
```

### koa-cors

跨域处理：

```shell [install-cors.sh]
npm i @koa/cors
```

```js [cors.js]
const cors = require('@koa/cors')

app.use(cors())
```

## 自定义中间件

### 日志中间件

```js [log-middleware.js]
async function logMiddleware(ctx, next) {
  const start = Date.now()
  
  await next()
  
  const ms = Date.now() - start
  console.log(`${ctx.method} ${ctx.url} - ${ms}ms`)
}

app.use(logMiddleware)
```

### 认证中间件

```js [auth-middleware.js]
async function authMiddleware(ctx, next) {
  const token = ctx.headers.authorization
  
  if (!token) {
    ctx.status = 401
    ctx.body = { error: '未授权' }
    return
  }
  
  // 验证 token
  if (token !== 'valid-token') {
    ctx.status = 403
    ctx.body = { error: '无效的 token' }
    return
  }
  
  await next()
}

// 使用
app.use(authMiddleware)
```

### 错误处理中间件

```js [error-middleware.js]
async function errorMiddleware(ctx, next) {
  try {
    await next()
  } catch (err) {
    ctx.status = err.status || 500
    ctx.body = {
      error: err.message
    }
    // 记录日志
    console.error(err.stack)
  }
}

// 必须放在最前面
app.use(errorMiddleware)
```

## 中间件执行顺序

```js [order.js]
const Koa = require('koa')
const app = new Koa()

// 1. 错误处理（最外层）
app.use(errorMiddleware)

// 2. 日志记录
app.use(logMiddleware)

// 3. 跨域处理
app.use(cors())

// 4. Body 解析
app.use(koaBody())

// 5. 静态文件
app.use(serve('./public'))

// 6. 路由
app.use(router.routes())

// 7. 404 处理
app.use(async (ctx) => {
  ctx.status = 404
  ctx.body = { error: 'Not Found' }
})
```

## 中间件组合

```js [compose.js]
const Koa = require('koa')
const compose = require('koa-compose')

// 组合多个中间件
const middleware = compose([
  logMiddleware,
  cors(),
  koaBody(),
  router.routes()
])

app.use(middleware)
```

::: tip 提示
- 错误处理中间件必须放在最前面
- 使用 await next() 才能继续执行
- 洋葱模型允许在 next() 前后执行代码
:::
