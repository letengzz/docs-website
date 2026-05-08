# Express 概述

Express 是一个基于 Node.js 平台的极简、灵活的 Web 应用开发框架。

- 官方网址：https://www.expressjs.com.cn/

简单来说，Express 是一个封装好的工具包，封装了很多功能，便于开发 Web 应用（HTTP 服务）。

![Express 框架](../assets/img202310262146166.png)

## 什么是 Express

Express 是 Node.js 最流行的 Web 框架之一，它提供了一系列强大的特性：

- **快速构建 Web 应用**：简洁的 API，快速开发
- **路由系统**：支持 RESTful 路由
- **中间件**：强大的中间件机制
- **模板引擎**：支持多种模板引擎
- **错误处理**：完善的错误处理机制

## Express 的特点

### 1. 极简灵活

Express 设计哲学是"极简"，核心功能精简，通过中间件扩展功能。

```js [app.js]
const express = require('express')
const app = express()

app.get('/', (req, res) => {
  res.send('Hello World!')
})

app.listen(3000, () => {
  console.log('Server is running on port 3000')
})
```

### 2. 路由系统

支持多种 HTTP 方法的路由定义：

```js [routes.js]
// GET 请求
app.get('/users', (req, res) => {
  res.send('获取用户列表')
})

// POST 请求
app.post('/users', (req, res) => {
  res.send('创建用户')
})

// PUT 请求
app.put('/users/:id', (req, res) => {
  res.send('更新用户')
})

// DELETE 请求
app.delete('/users/:id', (req, res) => {
  res.send('删除用户')
})
```

### 3. 中间件机制

中间件是 Express 的核心概念：

```js [middleware.js]
// 应用级中间件
app.use((req, res, next) => {
  console.log('请求时间:', Date.now())
  next()
})

// 路由级中间件
app.get('/users', (req, res, next) => {
  // 处理逻辑
  next()
}, (req, res) => {
  res.send('用户列表')
})

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(500).send('服务器错误')
})
```

## Express 的应用场景

### 1. Web 应用

- 企业官网
- 博客系统
- 电商平台
- 内容管理系统（CMS）

### 2. API 服务

- RESTful API
- GraphQL API
- 微服务架构
- 移动端后端

### 3. 实时应用

- 聊天应用
- 实时通知
- 在线游戏
- 协作工具

## Express 与其他框架对比

| 特性 | Express | Koa | Hapi | Fastify |
|------|---------|-----|------|---------|
| 学习曲线 | 简单 | 中等 | 中等 | 中等 |
| 性能 | 良好 | 良好 | 良好 | 优秀 |
| 中间件 | 丰富 | 较少 | 内置 | 插件 |
| 社区 | 最大 | 较大 | 中等 | 增长中 |
| 异步支持 | 回调 | async/await | async/await | async/await |

## Express 的历史

- **2010 年**：TJ Holowaychuk 创建 Express
- **2014 年**：Express 4.0 发布，引入路由中间件
- **2015 年**：Express 成为 OpenJS 基金会项目
- **2020 年**：Express 5.0 开始开发
- **2023 年**：Express 4.x 仍然是主流版本

## 为什么选择 Express

### 优势

- **学习成本低**：API 简洁，文档完善
- **生态丰富**：大量中间件和插件
- **社区活跃**：问题容易找到解决方案
- **性能稳定**：经过多年生产环境验证
- **灵活扩展**：可以根据需求选择中间件

### 适用场景

- 快速原型开发
- RESTful API 开发
- 传统 Web 应用
- 微服务架构
- 全栈 JavaScript 项目

::: tip 提示
Express 是最流行的 Node.js Web 框架，适合快速开发各种 Web 应用和 API 服务。
:::
