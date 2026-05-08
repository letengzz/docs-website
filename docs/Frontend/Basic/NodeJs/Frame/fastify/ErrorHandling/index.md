# Fastify 错误处理

Fastify 提供了完善的错误处理机制。

## 错误处理基础

### 基本错误处理

```js [error-handler.js]
const Fastify = require('fastify')

const app = Fastify({ logger: true })

app.get('/error', async (request, reply) => {
  const error = new Error('自定义错误')
  error.statusCode = 400
  throw error
})

app.listen({ port: 3000 })
```

## 自定义错误处理器

### 全局错误处理

```js [global-error.js]
app.setErrorHandler(function (error, request, reply) {
  const statusCode = error.statusCode || 500
  
  this.log.error(error)
  
  reply.code(statusCode).send({
    error: {
      message: error.message,
      statusCode
    }
  })
})
```

### 路由级错误处理

```js [route-error.js]
app.get('/users/:id', {
  errorHandler: (error, request, reply) => {
    reply.code(400).send({
      error: '处理用户请求时出错',
      message: error.message
    })
  }
}, async (request, reply) => {
  // 路由处理
})
```

## Schema 验证错误

### 自定义验证错误

```js [validation-error.js]
app.setSchemaErrorFormatter((errors, dataVar) => {
  const message = errors.map(err => {
    return `${err.instancePath} ${err.message}`
  }).join(', ')
  
  return new Error(`验证失败: ${message}`)
})
```

### 验证错误响应

```js [validation-response.js]
app.setErrorHandler(function (error, request, reply) {
  if (error.validation) {
    reply.code(400).send({
      error: '验证失败',
      details: error.validation
    })
    return
  }
  
  reply.code(error.statusCode || 500).send({
    error: error.message
  })
})
```

## 404 错误处理

### 自定义 404

```js [404.js]
app.setNotFoundHandler(function (request, reply) {
  reply.code(404).send({
    error: '路由不存在',
    path: request.url
  })
})
```

### 带前缀的 404

```js [prefix-404.js]
// 在插件中设置
async function usersPlugin(app) {
  app.setNotFoundHandler(function (request, reply) {
    reply.code(404).send({
      error: '用户路由不存在'
    })
  })
  
  app.get('/users', async (request, reply) => {
    return { users: [] }
  })
}
```

## HTTP 错误

### 使用 http-errors

```shell [install.sh]
npm i @fastify/sensible
```

```js [sensible.js]
const sensible = require('@fastify/sensible')

app.register(sensible)

app.get('/error', async (request, reply) => {
  throw app.httpErrors.badRequest('参数错误')
})

app.get('/not-found', async (request, reply) => {
  throw app.httpErrors.notFound('资源不存在')
})
```

## 异步错误处理

### try-catch 方式

```js [async-try-catch.js]
app.get('/users/:id', async (request, reply) => {
  try {
    const user = await findUser(request.params.id)
    if (!user) {
      throw app.httpErrors.notFound('用户不存在')
    }
    return user
  } catch (err) {
    request.log.error(err)
    throw err
  }
})
```

## 错误日志

### 配置日志

```js [logging.js]
const app = Fastify({
  logger: {
    level: 'error',
    file: '/var/log/app/error.log'
  }
})

app.setErrorHandler(function (error, request, reply) {
  this.log.error({
    err: error,
    req: request,
    timestamp: new Date().toISOString()
  })
  
  reply.code(500).send({ error: '服务器错误' })
})
```

## 完整错误处理示例

```js [complete-error.js]
const Fastify = require('fastify')

const app = Fastify({
  logger: {
    level: process.env.NODE_ENV === 'production' ? 'error' : 'debug'
  }
})

// 注册 sensible
app.register(require('@fastify/sensible'))

// 错误处理
app.setErrorHandler(function (error, request, reply) {
  // 记录日志
  this.log.error({
    err: error,
    url: request.url,
    method: request.method
  })
  
  // 验证错误
  if (error.validation) {
    return reply.code(400).send({
      error: '验证失败',
      details: error.validation
    })
  }
  
  // HTTP 错误
  const statusCode = error.statusCode || 500
  const message = process.env.NODE_ENV === 'production'
    ? (statusCode === 500 ? '服务器错误' : error.message)
    : error.message
  
  return reply.code(statusCode).send({
    error: message,
    statusCode
  })
})

// 404 处理
app.setNotFoundHandler(function (request, reply) {
  reply.code(404).send({
    error: '路由不存在',
    path: request.url
  })
})

// 路由
app.get('/users/:id', async (request, reply) => {
  const user = await findUser(request.params.id)
  
  if (!user) {
    throw app.httpErrors.notFound('用户不存在')
  }
  
  return user
})

app.listen({ port: 3000 })
```

::: tip 提示
- 使用 @fastify/sensible 简化错误处理
- 自定义错误处理器统一响应格式
- 生产环境不要暴露错误详情
:::
