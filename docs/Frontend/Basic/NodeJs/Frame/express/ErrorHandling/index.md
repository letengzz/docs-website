# 错误处理

Express 提供了完善的错误处理机制，包括同步错误和异步错误的处理。

## 错误处理中间件

### 基本格式

错误处理中间件有 4 个参数：

```js [error-middleware.js]
app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(500).send('服务器内部错误')
})
```

**注意**：必须包含 4 个参数，即使某些参数未使用。

## 同步错误处理

### 手动抛出错误

```js [sync-error.js]
app.get('/error', (req, res, next) => {
  const err = new Error('自定义错误')
  err.status = 400
  next(err)
})

// 错误处理中间件
app.use((err, req, res, next) => {
  const status = err.status || 500
  res.status(status).json({
    error: {
      message: err.message,
      status: status
    }
  })
})
```

### 使用 throw

```js [throw-error.js]
app.get('/throw', (req, res) => {
  throw new Error('出错了！')
})

// Express 会自动捕获 throw 的错误
app.use((err, req, res, next) => {
  res.status(500).send(err.message)
})
```

## 异步错误处理

### 方式1：手动捕获

```js [async-error-manual.js]
app.get('/async', async (req, res, next) => {
  try {
    const data = await someAsyncOperation()
    res.json(data)
  } catch (err) {
    next(err)
  }
})
```

### 方式2：使用 catch 方法

```js [async-error-catch.js]
app.get('/async', async (req, res, next) => {
  someAsyncOperation()
    .then(data => res.json(data))
    .catch(next)
})
```

### 方式3：使用包装函数

```js [async-wrapper.js]
// 创建包装函数
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next)
}

// 使用
app.get('/async', asyncHandler(async (req, res) => {
  const data = await someAsyncOperation()
  res.json(data)
}))
```

## 404 错误处理

### 捕获未匹配的路由

```js [404.js]
// 所有路由之后添加
app.use((req, res, next) => {
  res.status(404).json({
    error: '请求的资源不存在',
    path: req.originalUrl
  })
})

// 错误处理中间件
app.use((err, req, res, next) => {
  res.status(err.status || 500).json({
    error: err.message
  })
})
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

app.get('/users/:id', async (req, res, next) => {
  const user = await User.findById(req.params.id)
  
  if (!user) {
    return next(new AppError('用户不存在', 404))
  }
  
  res.json(user)
})
```

## 开发环境与生产环境

### 环境配置

```js [env-error.js]
// 开发环境 - 显示详细错误信息
if (process.env.NODE_ENV === 'development') {
  app.use((err, req, res, next) => {
    res.status(err.status || 500).json({
      error: {
        message: err.message,
        stack: err.stack,
        status: err.status
      }
    })
  })
}

// 生产环境 - 隐藏错误详情
if (process.env.NODE_ENV === 'production') {
  app.use((err, req, res, next) => {
    res.status(err.status || 500).json({
      error: {
        message: '服务器内部错误',
        status: err.status || 500
      }
    })
  })
}
```

## 错误日志记录

### 使用 morgan

```js [error-log.js]
const morgan = require('morgan')
const fs = require('fs')

// 创建日志流
const accessLogStream = fs.createWriteStream('access.log', { flags: 'a' })

// 使用 morgan 记录日志
app.use(morgan('combined', { stream: accessLogStream }))

// 错误日志
app.use((err, req, res, next) => {
  console.error(`${new Date().toISOString()} - ${err.message}`)
  next(err)
})
```

## 完整错误处理示例

```js [complete-error.js]
const express = require('express')
const app = express()

// 路由
app.get('/users/:id', async (req, res, next) => {
  try {
    const user = await User.findById(req.params.id)
    if (!user) {
      return next(new AppError('用户不存在', 404))
    }
    res.json(user)
  } catch (err) {
    next(err)
  }
})

// 404 处理
app.use((req, res) => {
  res.status(404).json({ error: '路由不存在' })
})

// 错误处理
app.use((err, req, res, next) => {
  const status = err.status || 500
  
  // 记录日志
  console.error(`${new Date().toISOString()} - ${err.stack}`)
  
  // 返回错误响应
  res.status(status).json({
    error: {
      message: process.env.NODE_ENV === 'production' 
        ? '服务器错误' 
        : err.message,
      status: status
    }
  })
})

app.listen(3000)
```

::: tip 提示
- 错误处理中间件必须放在所有路由之后
- 异步错误需要使用 next(err) 传递
- 生产环境不要暴露错误堆栈信息
:::
