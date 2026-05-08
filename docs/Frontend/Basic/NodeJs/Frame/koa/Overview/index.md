# Koa 概述

Koa 是一个新的 Web 框架，由 Express 团队原班人马打造。

- 官网：https://koajs.com/
- 中文文档：https://koa.bootcss.com/

## 什么是 Koa

Koa 致力于成为一个更小、更富有表现力、更健壮的 Web 框架。

**核心特性**：

- **更轻量**：核心代码仅约 2000 行
- **更现代**：使用 async/await 处理异步
- **更优雅**：洋葱模型中间件机制
- **更灵活**：不绑定任何中间件

## Koa vs Express

| 特性 | Koa | Express |
|------|-----|---------|
| 异步处理 | async/await | 回调函数 |
| 中间件模型 | 洋葱模型 | 线性模型 |
| 内置功能 | 极简 | 丰富 |
| 错误处理 | try/catch | 错误中间件 |

## Koa 安装

```shell [install.sh]
# 初始化项目
npm init -y

# 安装 Koa
npm i koa
```

## 快速开始

```js [app.js]
const Koa = require('koa')
const app = new Koa()

app.use(async (ctx) => {
  ctx.body = 'Hello Koa'
})

app.listen(3000, () => {
  console.log('服务启动在 3000 端口')
})
```

## 洋葱模型

Koa 的中间件采用洋葱模型，请求从外到内，响应从内到外：

```js [onion-model.js]
const Koa = require('koa')
const app = new Koa()

// 第一个中间件
app.use(async (ctx, next) => {
  console.log('1. 请求进入')
  await next()
  console.log('5. 响应返回')
})

// 第二个中间件
app.use(async (ctx, next) => {
  console.log('2. 进入第二层')
  await next()
  console.log('4. 返回第二层')
})

// 第三个中间件
app.use(async (ctx) => {
  console.log('3. 到达核心')
  ctx.body = 'Hello Koa'
})

app.listen(3000)

// 输出顺序：
// 1. 请求进入
// 2. 进入第二层
// 3. 到达核心
// 4. 返回第二层
// 5. 响应返回
```

## Context 对象

Koa 的 Context 对象封装了 request 和 response：

```js [context.js]
const Koa = require('koa')
const app = new Koa()

app.use(async (ctx) => {
  // ctx.request - 请求对象
  console.log(ctx.request.url)
  console.log(ctx.request.method)
  console.log(ctx.request.query)
  
  // ctx.response - 响应对象
  ctx.response.status = 200
  ctx.response.body = 'Hello'
  
  // 简写方式
  ctx.status = 200
  ctx.body = 'Hello'
})

app.listen(3000)
```
