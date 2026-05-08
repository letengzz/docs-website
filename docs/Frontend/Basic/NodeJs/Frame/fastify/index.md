# Fastify 框架

Fastify 是一个专注于提供最佳开发者体验的高性能 Web 框架。

- 官网：https://fastify.dev/
- GitHub：https://github.com/fastify/fastify

Fastify 以其高性能、插件化架构和 JSON Schema 验证而闻名。

## Fastify 特点

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

## 安装

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
