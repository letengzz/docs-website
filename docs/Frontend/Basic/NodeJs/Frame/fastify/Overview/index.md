# Fastify 概述

Fastify 是一个专注于提供最佳开发者体验的高性能 Web 框架。

- 官网：https://fastify.dev/
- GitHub：https://github.com/fastify/fastify

## 什么是 Fastify

Fastify 以其高性能、插件化架构和 JSON Schema 验证而闻名。

**核心特性**：

- **高性能**：基于路由树优化，吞吐量极高
- **插件化**：强大的插件系统，支持封装
- **Schema 验证**：内置 JSON Schema 验证
- **TypeScript**：完整的 TypeScript 支持
- **日志系统**：内置结构化日志

## 性能对比

| 框架 | 请求/秒 | 延迟 (ms) |
|------|---------|-----------|
| Fastify | ~30,000 | ~2 |
| Express | ~15,000 | ~4 |
| Koa | ~16,000 | ~3 |

## Fastify 安装

```shell [install.sh]
npm i fastify
```

## 快速开始

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
})
```

## 路由定义

```js [routes.js]
// GET 请求
app.get('/users', async (request, reply) => {
  return [{ id: 1, name: '张三' }]
})

// POST 请求
app.post('/users', async (request, reply) => {
  const { name, age } = request.body
  return { id: Date.now(), name, age }
})

// PUT 请求
app.put('/users/:id', async (request, reply) => {
  const { id } = request.params
  return { id, message: '更新成功' }
})

// DELETE 请求
app.delete('/users/:id', async (request, reply) => {
  const { id } = request.params
  return { id, message: '删除成功' }
})
```

## Schema 验证

Fastify 内置 JSON Schema 验证：

```js [schema.js]
const userSchema = {
  body: {
    type: 'object',
    required: ['name', 'age'],
    properties: {
      name: { type: 'string', minLength: 2 },
      age: { type: 'integer', minimum: 0 }
    }
  },
  response: {
    200: {
      type: 'object',
      properties: {
        id: { type: 'integer' },
        name: { type: 'string' },
        age: { type: 'integer' }
      }
    }
  }
}

app.post('/users', { schema: userSchema }, async (request, reply) => {
  return request.body
})
```

## 插件系统

```js [plugin.js]
// 创建插件
const userPlugin = async (app, options) => {
  app.get('/users', async (request, reply) => {
    return [{ id: 1, name: '张三' }]
  })
}

// 注册插件
app.register(userPlugin, { prefix: '/api' })
```

## 中间件支持

Fastify 可以使用 Express/Koa 中间件：

```js [middleware.js]
const middie = require('@fastify/middie')
const cors = require('cors')

app.register(middie)

app.use(cors())
app.use(express.json())
```
