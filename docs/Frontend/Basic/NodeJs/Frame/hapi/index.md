# Hapi 框架

Hapi 是一个用于构建应用程序和服务的配置优先的 Web 框架。

- 官网：https://hapi.dev/
- GitHub：https://github.com/hapijs/hapi

Hapi 以配置优先的设计理念著称，强调安全性和可维护性。

## Hapi 特点

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

## 安装

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
