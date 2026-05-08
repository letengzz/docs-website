# Fastify 基础操作

## 安装与启动

```shell [install.sh]
npm i fastify
```

```js [app.js]
const Fastify = require('fastify')

const app = Fastify({
  logger: true
})

app.get('/', async (request, reply) => {
  return { hello: 'world' }
})

app.listen({ port: 3000 }, (err) => {
  if (err) {
    app.log.error(err)
    process.exit(1)
  }
  console.log('服务启动在 3000 端口')
})
```

## 路由处理

### 基本路由

```js [basic-routes.js]
// GET 请求
app.get('/', async (request, reply) => {
  return '首页'
})

app.get('/about', async (request, reply) => {
  return '关于页面'
})

app.get('/contact', async (request, reply) => {
  return '联系我们'
})
```

### 路由参数

```js [route-params.js]
// 路径参数
app.get('/users/:id', async (request, reply) => {
  const { id } = request.params
  return { id, name: '张三' }
})

// 多个路径参数
app.get('/users/:userId/posts/:postId', async (request, reply) => {
  return {
    userId: request.params.userId,
    postId: request.params.postId
  }
})

// 查询参数
app.get('/users', async (request, reply) => {
  const { page, limit, sort } = request.query
  return {
    page: page || 1,
    limit: limit || 10,
    sort: sort || 'desc'
  }
})
```

### 路由前缀

```js [prefix.js]
// 创建路由器
const userRouter = async (app, options) => {
  app.get('/', async (request, reply) => {
    return '用户列表'
  })
  
  app.get('/:id', async (request, reply) => {
    return { id: request.params.id }
  })
}

// 注册并设置前缀
app.register(userRouter, { prefix: '/api/users' })

// 访问 /api/users
// 访问 /api/users/1
```

## 请求处理

### 获取请求体

```js [request-body.js]
app.post('/users', async (request, reply) => {
  const { name, age, email } = request.body
  return {
    id: Date.now(),
    name,
    age,
    email
  }
})
```

### 获取请求头

```js [headers.js]
app.get('/info', async (request, reply) => {
  return {
    contentType: request.headers['content-type'],
    userAgent: request.headers['user-agent'],
    authorization: request.headers['authorization']
  }
})
```

### 获取 Cookie

```js [cookies.js]
const cookie = require('@fastify/cookie')

app.register(cookie)

app.get('/cookie', async (request, reply) => {
  return {
    sessionId: request.cookies.sessionId
  }
})
```

## 响应处理

### 设置状态码

```js [status.js]
app.post('/users', async (request, reply) => {
  reply.code(201)
  return { message: '创建成功' }
})

app.delete('/users/:id', async (request, reply) => {
  reply.code(204)
  return null
})
```

### 设置响应头

```js [response-headers.js]
app.get('/download', async (request, reply) => {
  reply.header('Content-Disposition', 'attachment; filename=file.txt')
  reply.header('Content-Type', 'application/octet-stream')
  return fileContent
})
```

### 重定向

```js [redirect.js]
app.get('/old-route', async (request, reply) => {
  reply.redirect('/new-route')
})

app.get('/external', async (request, reply) => {
  reply.redirect(302, 'https://example.com')
})
```

### 发送文件

```js [send-file.js]
const path = require('path')

app.get('/file', async (request, reply) => {
  return reply.sendFile('file.txt', path.join(__dirname, 'files'))
})
```

## Schema 验证

### 请求体验证

```js [validation.js]
const createUserSchema = {
  body: {
    type: 'object',
    required: ['name', 'email'],
    properties: {
      name: {
        type: 'string',
        minLength: 2,
        maxLength: 50
      },
      email: {
        type: 'string',
        format: 'email'
      },
      age: {
        type: 'integer',
        minimum: 0,
        maximum: 150
      }
    }
  }
}

app.post('/users', { schema: createUserSchema }, async (request, reply) => {
  return request.body
})
```

### 响应验证

```js [response-schema.js]
const getUserSchema = {
  response: {
    200: {
      type: 'object',
      properties: {
        id: { type: 'integer' },
        name: { type: 'string' },
        email: { type: 'string' }
      }
    }
  }
}

app.get('/users/:id', { schema: getUserSchema }, async (request, reply) => {
  return {
    id: parseInt(request.params.id),
    name: '张三',
    email: 'zhangsan@example.com'
  }
})
```

## 完整示例

```js [full-example.js]
const Fastify = require('fastify')

const app = Fastify({
  logger: true
})

// 用户 Schema
const userSchema = {
  body: {
    type: 'object',
    required: ['name', 'email'],
    properties: {
      name: { type: 'string', minLength: 2 },
      email: { type: 'string', format: 'email' }
    }
  },
  response: {
    200: {
      type: 'object',
      properties: {
        id: { type: 'integer' },
        name: { type: 'string' },
        email: { type: 'string' }
      }
    }
  }
}

// 路由
app.get('/users', async (request, reply) => {
  return [
    { id: 1, name: '张三', email: 'zhangsan@example.com' },
    { id: 2, name: '李四', email: 'lisi@example.com' }
  ]
})

app.get('/users/:id', async (request, reply) => {
  return {
    id: parseInt(request.params.id),
    name: '张三',
    email: 'zhangsan@example.com'
  }
})

app.post('/users', { schema: userSchema }, async (request, reply) => {
  reply.code(201)
  return {
    id: Date.now(),
    ...request.body
  }
})

app.put('/users/:id', async (request, reply) => {
  return {
    id: parseInt(request.params.id),
    message: '更新成功'
  }
})

app.delete('/users/:id', async (request, reply) => {
  reply.code(204)
  return null
})

// 启动服务
app.listen({ port: 3000 }, (err) => {
  if (err) {
    app.log.error(err)
    process.exit(1)
  }
  console.log('服务启动在 3000 端口')
})
```

::: tip 提示
- 使用 async/await 处理异步
- Schema 验证可以提高性能和安全性
- 使用 reply.code() 设置状态码
:::
