# Koa 错误处理

Koa 提供了强大的错误处理机制，包括同步错误和异步错误的处理。

## 错误处理中间件

### 基本错误处理

```js [error-handler.js]
const Koa = require('koa')
const app = new Koa()

// 错误处理中间件（必须放在最前面）
app.use(async (ctx, next) => {
  try {
    await next()
  } catch (err) {
    ctx.status = err.status || 500
    ctx.body = {
      error: err.message,
      status: ctx.status
    }
    // 记录错误日志
    console.error(err.stack)
  }
})

app.use(async (ctx) => {
  throw new Error('自定义错误')
})

app.listen(3000)
```

## 同步错误处理

### 手动抛出错误

```js [sync-error.js]
app.use(async (ctx, next) => {
  try {
    await next()
  } catch (err) {
    ctx.status = err.status || 500
    ctx.body = { error: err.message }
  }
})

app.use(async (ctx) => {
  const error = new Error('参数错误')
  error.status = 400
  throw error
})
```

### 使用 http-errors

```shell [install.sh]
npm i http-errors
```

```js [http-errors.js]
const createError = require('http-errors')

app.use(async (ctx) => {
  throw createError(404, '页面不存在')
})
```

## 异步错误处理

### try-catch 方式

```js [async-try-catch.js]
app.use(async (ctx, next) => {
  try {
    await next()
  } catch (err) {
    ctx.status = err.status || 500
    ctx.body = { error: err.message }
  }
})

app.use(async (ctx) => {
  const data = await fetchData()
  ctx.body = data
})
```

### 包装函数方式

```js [async-wrapper.js]
// 创建包装函数
const asyncHandler = (fn) => async (ctx, next) => {
  try {
    await fn(ctx, next)
  } catch (err) {
    ctx.status = err.status || 500
    ctx.body = { error: err.message }
  }
}

// 使用
app.use(asyncHandler(async (ctx) => {
  const data = await fetchData()
  ctx.body = data
}))
```

## 404 错误处理

### 捕获未匹配的路由

```js [404.js]
// 所有路由之后添加
app.use(async (ctx) => {
  ctx.status = 404
  ctx.body = {
    error: '请求的资源不存在',
    path: ctx.url
  }
})
```

### 完整示例

```js [complete-404.js]
const Koa = require('koa')
const Router = require('koa-router')

const app = new Koa()
const router = new Router()

// 错误处理
app.use(async (ctx, next) => {
  try {
    await next()
  } catch (err) {
    ctx.status = err.status || 500
    ctx.body = { error: err.message }
  }
})

// 路由
router.get('/users', (ctx) => {
  ctx.body = { users: [] }
})

// 404 处理
app.use(async (ctx) => {
  ctx.status = 404
  ctx.body = { error: '路由不存在' }
})

app.use(router.routes())
app.use(router.allowedMethods())

app.listen(3000)
```

## 自定义错误类

### 创建错误类

```js [custom-error.js]
class AppError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
    this.name = 'AppError'
  }
}

module.exports = AppError
```

### 使用自定义错误

```js [use-custom-error.js]
const AppError = require('./AppError')

app.use(async (ctx) => {
  const user = await findUser(ctx.params.id)
  
  if (!user) {
    throw new AppError('用户不存在', 404)
  }
  
  ctx.body = user
})
```

## 开发环境与生产环境

### 环境配置

```js [env-error.js]
app.use(async (ctx, next) => {
  try {
    await next()
  } catch (err) {
    const status = err.status || 500
    
    // 开发环境 - 显示详细错误
    if (process.env.NODE_ENV === 'development') {
      ctx.status = status
      ctx.body = {
        error: err.message,
        stack: err.stack,
        status
      }
    }
    
    // 生产环境 - 隐藏错误详情
    if (process.env.NODE_ENV === 'production') {
      ctx.status = status
      ctx.body = {
        error: status === 500 ? '服务器内部错误' : err.message,
        status
      }
    }
  }
})
```

## 错误日志记录

### 使用 koa-logger

```shell [install-logger.sh]
npm i koa-logger
```

```js [logger.js]
const logger = require('koa-logger')

app.use(logger())
```

### 自定义日志

```js [custom-logger.js]
const fs = require('fs')

app.use(async (ctx, next) => {
  const start = Date.now()
  
  try {
    await next()
  } catch (err) {
    const log = `${new Date().toISOString()} - ${ctx.method} ${ctx.url} - ${err.message}\n`
    fs.appendFileSync('error.log', log)
    throw err
  }
  
  const ms = Date.now() - start
  console.log(`${ctx.method} ${ctx.url} - ${ms}ms`)
})
```

## 完整错误处理示例

```js [complete-error.js]
const Koa = require('koa')
const Router = require('koa-router')
const createError = require('http-errors')

const app = new Koa()
const router = new Router()

// 错误处理中间件
app.use(async (ctx, next) => {
  try {
    await next()
  } catch (err) {
    const status = err.status || 500
    
    // 记录日志
    console.error(`${new Date().toISOString()} - ${err.stack}`)
    
    // 返回错误响应
    ctx.status = status
    ctx.body = {
      error: {
        message: process.env.NODE_ENV === 'production' 
          ? (status === 500 ? '服务器错误' : err.message)
          : err.message,
        status
      }
    }
  }
})

// 路由
router.get('/users/:id', async (ctx) => {
  const user = await findUser(ctx.params.id)
  
  if (!user) {
    throw createError(404, '用户不存在')
  }
  
  ctx.body = user
})

// 404 处理
app.use(async (ctx) => {
  throw createError(404, '路由不存在')
})

app.use(router.routes())
app.use(router.allowedMethods())

app.listen(3000)
```

::: tip 提示
- 错误处理中间件必须放在最前面
- 使用 try-catch 捕获异步错误
- 生产环境不要暴露错误堆栈信息
:::
