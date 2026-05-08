# Koa Router

Koa 本身不包含路由功能，需要使用 koa-router 中间件来实现路由。

- GitHub：https://github.com/koajs/router

## 安装

```shell [install.sh]
npm i koa-router
```

## 基本使用

```js [basic.js]
const Koa = require('koa')
const Router = require('koa-router')

const app = new Koa()
const router = new Router()

router.get('/', (ctx) => {
  ctx.body = '首页'
})

router.get('/users', (ctx) => {
  ctx.body = '用户列表'
})

app.use(router.routes())
app.use(router.allowedMethods())

app.listen(3000)
```

## 路由方法

### GET 请求

```js [get.js]
// 获取所有用户
router.get('/users', (ctx) => {
  ctx.body = { users: [] }
})

// 获取单个用户
router.get('/users/:id', (ctx) => {
  ctx.body = { id: ctx.params.id }
})

// 带查询参数
router.get('/users/search', (ctx) => {
  const { name, age } = ctx.query
  ctx.body = { name, age }
})
```

### POST 请求

```js [post.js]
router.post('/users', (ctx) => {
  const { name, email } = ctx.request.body
  ctx.status = 201
  ctx.body = {
    id: Date.now(),
    name,
    email
  }
})
```

### PUT 请求

```js [put.js]
router.put('/users/:id', (ctx) => {
  const { id } = ctx.params
  const { name, email } = ctx.request.body
  ctx.body = {
    id,
    name,
    email,
    message: '更新成功'
  }
})
```

### DELETE 请求

```js [delete.js]
router.delete('/users/:id', (ctx) => {
  const { id } = ctx.params
  ctx.status = 204
  ctx.body = null
})
```

## 路由参数

### 路径参数

```js [params.js]
// 单个参数
router.get('/users/:id', (ctx) => {
  ctx.body = { userId: ctx.params.id }
})

// 多个参数
router.get('/users/:userId/posts/:postId', (ctx) => {
  ctx.body = {
    userId: ctx.params.userId,
    postId: ctx.params.postId
  }
})

// 可选参数
router.get('/users/:id?', (ctx) => {
  ctx.body = { id: ctx.params.id || '全部' }
})

// 通配符参数
router.get('/files/*', (ctx) => {
  ctx.body = { path: ctx.params[0] }
})
```

### 查询参数

```js [query.js]
router.get('/users', (ctx) => {
  const { page = 1, limit = 10, sort = 'desc' } = ctx.query
  ctx.body = { page, limit, sort }
})
```

## 路由前缀

```js [prefix.js]
const Koa = require('koa')
const Router = require('koa-router')

const app = new Koa()

// 创建用户路由
const userRouter = new Router({ prefix: '/api/users' })

userRouter.get('/', (ctx) => {
  ctx.body = '用户列表'
})

userRouter.get('/:id', (ctx) => {
  ctx.body = { id: ctx.params.id }
})

// 创建商品路由
const productRouter = new Router({ prefix: '/api/products' })

productRouter.get('/', (ctx) => {
  ctx.body = '商品列表'
})

// 注册路由
app.use(userRouter.routes())
app.use(userRouter.allowedMethods())
app.use(productRouter.routes())
app.use(productRouter.allowedMethods())

app.listen(3000)
```

## 路由模块化

### 用户路由

```js [userRoutes.js]
const Router = require('koa-router')
const router = new Router()

router.get('/', async (ctx) => {
  ctx.body = { users: [] }
})

router.get('/:id', async (ctx) => {
  ctx.body = { id: ctx.params.id }
})

router.post('/', async (ctx) => {
  ctx.status = 201
  ctx.body = { message: '创建成功' }
})

module.exports = router
```

### 商品路由

```js [productRoutes.js]
const Router = require('koa-router')
const router = new Router()

router.get('/', async (ctx) => {
  ctx.body = { products: [] }
})

router.get('/:id', async (ctx) => {
  ctx.body = { id: ctx.params.id }
})

module.exports = router
```

### 主应用

```js [app.js]
const Koa = require('koa')
const userRoutes = require('./routes/userRoutes')
const productRoutes = require('./routes/productRoutes')

const app = new Koa()

app.use(userRoutes.routes())
app.use(userRoutes.allowedMethods())

app.use(productRoutes.routes())
app.use(productRoutes.allowedMethods())

app.listen(3000)
```

## 路由中间件

### 路由级中间件

```js [route-middleware.js]
// 单个路由中间件
router.get('/admin', authMiddleware, (ctx) => {
  ctx.body = '管理员页面'
})

// 多个中间件
router.get('/admin', authMiddleware, permissionMiddleware, (ctx) => {
  ctx.body = '管理员页面'
})
```

### 路由组中间件

```js [group-middleware.js]
const Router = require('koa-router')
const router = new Router({ prefix: '/admin' })

// 为所有路由添加中间件
router.use(authMiddleware)

router.get('/dashboard', (ctx) => {
  ctx.body = '仪表盘'
})

router.get('/users', (ctx) => {
  ctx.body = '用户管理'
})
```

## RESTful 路由

```js [restful.js]
const Router = require('koa-router')
const router = new Router({ prefix: '/articles' })

// GET /articles - 获取文章列表
router.get('/', async (ctx) => {
  ctx.body = { articles: [] }
})

// GET /articles/new - 显示创建表单
router.get('/new', async (ctx) => {
  ctx.body = '创建文章表单'
})

// GET /articles/:id - 获取单篇文章
router.get('/:id', async (ctx) => {
  ctx.body = { id: ctx.params.id }
})

// GET /articles/:id/edit - 显示编辑表单
router.get('/:id/edit', async (ctx) => {
  ctx.body = '编辑文章表单'
})

// POST /articles - 创建文章
router.post('/', async (ctx) => {
  ctx.status = 201
  ctx.body = { message: '创建成功' }
})

// PUT /articles/:id - 更新文章
router.put('/:id', async (ctx) => {
  ctx.body = { message: '更新成功' }
})

// DELETE /articles/:id - 删除文章
router.delete('/:id', async (ctx) => {
  ctx.status = 204
  ctx.body = null
})

module.exports = router
```

## 嵌套路由

```js [nested.js]
const Koa = require('koa')
const Router = require('koa-router')

const app = new Koa()

// 主路由
const router = new Router()

// 子路由
const userRouter = new Router()
userRouter.get('/', (ctx) => ctx.body = '用户列表')
userRouter.get('/:id', (ctx) => ctx.body = { id: ctx.params.id })

// 嵌套路由
router.use('/users', userRouter.routes(), userRouter.allowedMethods())

app.use(router.routes())
app.use(router.allowedMethods())

app.listen(3000)
```

## 路由命名

```js [named.js]
router.get('users', '/users/:id', (ctx) => {
  ctx.body = { id: ctx.params.id }
})

// 生成 URL
const url = router.url('users', { id: 1 })
console.log(url) // /users/1
```

## allowedMethods

```js [allowed.js]
// 自动处理 OPTIONS 请求和方法不允许的情况
app.use(router.routes())
app.use(router.allowedMethods())

// 自定义 405 处理
app.use(router.allowedMethods({
  throw: true
}))
```

::: tip 提示
- 必须调用 router.routes() 和 router.allowedMethods()
- 使用 prefix 选项设置路由前缀
- 支持路由模块化和嵌套
:::
