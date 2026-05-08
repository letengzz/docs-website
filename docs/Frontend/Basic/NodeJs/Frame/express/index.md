# Express 框架

Express 是一个基于 Node.js 平台的极简、灵活的 Web 应用开发框架。

- 官方网址：https://www.expressjs.com.cn/

简单来说，Express 是一个封装好的工具包，封装了很多功能，便于开发 Web 应用（HTTP 服务）。

![Express 框架](assets/img202310262146166.png)

## 基础

- [Express 概述](Overview/index.md)
- [Express 基础操作](BasicOperations/index.md)

> 基础操作：安装、路由、请求参数、响应设置

## 核心功能

- [Express 中间件](Middleware/index.md)

> 中间件：全局中间件、路由中间件、静态资源、body-parser

- [Express Router](Router/index.md)

> Router：路由模块化、路由参数、RESTful 设计

## 模板引擎

- [EJS 模板引擎](EJS/index.md)

> EJS：安装配置、常用语法、模板继承

- [模板引擎对比](TemplateEngine/index.md)

> 模板引擎：EJS、Pug、Handlebars 对比

## 高级特性

- [静态文件服务](StaticFiles/index.md)

> 静态文件：express.static、缓存配置、安全注意事项

- [错误处理](ErrorHandling/index.md)

> 错误处理：同步错误、异步错误、自定义错误类

- [安全最佳实践](Security/index.md)

> 安全：XSS、CSRF、速率限制、输入验证

## 部署

- [Express 部署](Deployment/index.md)

> 部署：PM2、Nginx、Docker、云平台
