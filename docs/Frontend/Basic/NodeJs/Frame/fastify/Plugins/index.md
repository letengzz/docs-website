# Fastify 插件系统

Fastify 拥有强大的插件系统，支持封装和代码组织。

- 官方文档：https://fastify.dev/docs/latest/Reference/Plugins/

## 插件基础

### 创建插件

```js [plugin.js]
const fp = require('fastify-plugin')

async function myPlugin(app, options) {
  app.get('/plugin-route', async (request, reply) => {
    return { message: '来自插件' }
  })
}

module.exports = fp(myPlugin)
```

### 注册插件

```js [register.js]
const myPlugin = require('./myPlugin')

app.register(myPlugin, {
  prefix: '/api'
})
```

## 封装作用域

### 基本封装

```js [encapsulation.js]
// users.js
async function usersPlugin(app) {
  // 这个装饰器只在 usersPlugin 作用域内可用
  app.decorate('usersService', {
    findAll: () => []
  })
  
  app.get('/users', async (request, reply) => {
    return app.usersService.findAll()
  })
}

app.register(usersPlugin, { prefix: '/users' })

// 在外部无法访问 app.usersService
```

### 打破封装

```js [break-encapsulation.js]
const fp = require('fastify-plugin')

async function globalPlugin(app) {
  // 使用 fastify-plugin 包装后，装饰器将在全局可用
  app.decorate('globalService', {
    getData: () => 'data'
  })
}

module.exports = fp(globalPlugin)
```

## 常用插件

### @fastify/cors

```shell [install-cors.sh]
npm i @fastify/cors
```

```js [cors.js]
const cors = require('@fastify/cors')

app.register(cors, {
  origin: ['http://localhost:3000'],
  methods: ['GET', 'POST', 'PUT', 'DELETE']
})
```

### @fastify/helmet

```shell [install-helmet.sh]
npm i @fastify/helmet
```

```js [helmet.js]
const helmet = require('@fastify/helmet')

app.register(helmet, {
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"]
    }
  }
})
```

### @fastify/static

```shell [install-static.sh]
npm i @fastify/static
```

```js [static.js]
const fastifyStatic = require('@fastify/static')
const path = require('path')

app.register(fastifyStatic, {
  root: path.join(__dirname, 'public'),
  prefix: '/public/'
})
```

### @fastify/cookie

```shell [install-cookie.sh]
npm i @fastify/cookie
```

```js [cookie.js]
const cookie = require('@fastify/cookie')

app.register(cookie, {
  secret: 'my-secret'
})

app.get('/cookie', async (request, reply) => {
  reply.setCookie('sessionId', '123', {
    path: '/',
    httpOnly: true,
    secure: true
  })
  
  return { cookie: request.cookies.sessionId }
})
```

### @fastify/jwt

```shell [install-jwt.sh]
npm i @fastify/jwt
```

```js [jwt.js]
const jwt = require('@fastify/jwt')

app.register(jwt, {
  secret: 'my-secret-key'
})

app.post('/login', async (request, reply) => {
  const { username, password } = request.body
  
  // 验证用户
  const token = app.jwt.sign({
    username,
    role: 'user'
  })
  
  return { token }
})

app.get('/profile', async (request, reply) => {
  await request.jwtVerify()
  return { user: request.user }
})
```

## 插件依赖

```js [dependencies.js]
async function pluginA(app) {
  app.decorate('serviceA', { getData: () => 'A' })
}

async function pluginB(app) {
  // 依赖 pluginA
  app.decorate('serviceB', {
    getData: () => app.serviceA.getData() + 'B'
  })
}

// 注册顺序很重要
app.register(pluginA)
app.register(pluginB)
```

## 插件选项

```js [options.js]
async function configurablePlugin(app, options) {
  const { prefix, limit } = options
  
  app.get(`${prefix}/items`, async (request, reply) => {
    return { items: [], limit }
  })
}

app.register(configurablePlugin, {
  prefix: '/api',
  limit: 10
})
```

## 完整示例

```js [full-example.js]
const Fastify = require('fastify')

const app = Fastify({ logger: true })

// 数据库插件
async function dbPlugin(app) {
  const db = {
    users: [
      { id: 1, name: '张三' },
      { id: 2, name: '李四' }
    ]
  }
  
  app.decorate('db', db)
}

// 用户插件
async function usersPlugin(app) {
  app.get('/', async (request, reply) => {
    return app.db.users
  })
  
  app.get('/:id', async (request, reply) => {
    const user = app.db.users.find(u => u.id === parseInt(request.params.id))
    if (!user) {
      reply.code(404)
      return { error: '用户不存在' }
    }
    return user
  })
  
  app.post('/', async (request, reply) => {
    const user = {
      id: app.db.users.length + 1,
      ...request.body
    }
    app.db.users.push(user)
    reply.code(201)
    return user
  })
}

// 注册插件
app.register(dbPlugin)
app.register(usersPlugin, { prefix: '/users' })

app.listen({ port: 3000 })
```

::: tip 提示
- 使用 fastify-plugin 打破封装
- 插件可以接收配置选项
- 注意插件注册顺序
:::
