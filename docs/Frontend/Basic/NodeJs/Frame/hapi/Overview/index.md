# Hapi 概述

Hapi 是一个用于构建应用程序和服务的配置优先的 Web 框架。

- 官网：https://hapi.dev/
- GitHub：https://github.com/hapijs/hapi

Hapi 以配置优先的设计理念著称，强调安全性和可维护性。

## 什么是 Hapi

Hapi 由 Walmart 实验室开发，最初用于处理黑色星期五的流量高峰。

**核心特性**：

- **配置优先**：通过配置而非代码定义路由和行为
- **内置验证**：强大的输入验证系统
- **插件系统**：模块化插件架构
- **安全性**：内置安全特性
- **企业级**：适合大型项目

## 框架对比

| 框架 | 设计理念 | 验证 | 插件 |
|------|---------|------|------|
| Hapi | 配置优先 | 内置 | 强大 |
| Express | 极简 | 需中间件 | 生态丰富 |
| Koa | 现代简洁 | 需中间件 | 洋葱模型 |
| Fastify | 高性能 | Schema | 封装系统 |

## Hapi 安装

```shell [install.sh]
npm i @hapi/hapi
```

## 快速开始

```js [app.js]
const Hapi = require('@hapi/hapi')

const init = async () => {
  const server = Hapi.server({
    port: 3000,
    host: 'localhost'
  })

  server.route({
    method: 'GET',
    path: '/',
    handler: (request, h) => {
      return 'Hello World!'
    }
  })

  await server.start()
  console.log('服务启动在', server.info.uri)
}

process.on('unhandledRejection', (err) => {
  console.log(err)
  process.exit(1)
})

init()
```

## 路由配置

Hapi 使用配置对象定义路由：

```js [routes.js]
server.route({
  method: 'GET',
  path: '/users/{id}',
  handler: (request, h) => {
    return {
      id: request.params.id,
      name: '张三'
    }
  }
})
```

## 输入验证

Hapi 内置 Joi 验证库：

```js [validation.js]
const Joi = require('joi')

server.route({
  method: 'POST',
  path: '/users',
  options: {
    validate: {
      payload: Joi.object({
        name: Joi.string().min(2).max(50).required(),
        email: Joi.string().email().required(),
        age: Joi.number().integer().min(0).max(150)
      })
    }
  },
  handler: (request, h) => {
    return request.payload
  }
})
```

## 插件系统

```js [plugin.js]
const myPlugin = {
  name: 'myPlugin',
  register: async (server, options) => {
    server.route({
      method: 'GET',
      path: '/plugin',
      handler: (request, h) => {
        return '来自插件的响应'
      }
    })
  }
}

await server.register(myPlugin)
```
