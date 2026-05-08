# Express Router

Express 中的 Router 是一个完整的中间件和路由系统，可以看做是一个小型的 app 对象。

**Router 作用**：对路由进行模块化，更好的管理路由

## Router 使用

### 创建路由器

创建独立的 JS 文件（homeRouter.js）：

```js [homeRouter.js]
//1. 导入 express
const express = require('express');
//2. 创建路由器对象
const router = express.Router();

//3. 在 router 对象身上添加路由
router.get('/', (req, res) => {
  res.send('首页');
})

router.get('/cart', (req, res) => {
  res.send('购物车');
});

//4. 暴露
module.exports = router;
```

### 使用路由器

主文件中引入并使用：

```js [app.js]
const express = require('express')
const homeRouter = require('./routes/homeRouter')

const app = express()

// 使用路由器
app.use('/', homeRouter)

app.listen(3000, () => {
  console.log('服务启动')
})
```

## 路由模块化

### 用户路由

```js [userRouter.js]
const express = require('express')
const router = express.Router()

// 获取用户列表
router.get('/', (req, res) => {
  res.json([
    { id: 1, name: '张三' },
    { id: 2, name: '李四' }
  ])
})

// 获取单个用户
router.get('/:id', (req, res) => {
  const user = { id: req.params.id, name: '张三' }
  res.json(user)
})

// 创建用户
router.post('/', (req, res) => {
  const { name } = req.body
  res.json({ id: Date.now(), name })
})

// 更新用户
router.put('/:id', (req, res) => {
  res.json({ message: '更新成功' })
})

// 删除用户
router.delete('/:id', (req, res) => {
  res.json({ message: '删除成功' })
})

module.exports = router
```

### 商品路由

```js [productRouter.js]
const express = require('express')
const router = express.Router()

// 获取商品列表
router.get('/', (req, res) => {
  res.json([
    { id: 1, name: '商品1', price: 99 },
    { id: 2, name: '商品2', price: 199 }
  ])
})

// 获取商品详情
router.get('/:id', (req, res) => {
  res.json({ id: req.params.id, name: '商品详情', price: 99 })
})

module.exports = router
```

### 主应用

```js [app.js]
const express = require('express')
const userRouter = require('./routes/userRouter')
const productRouter = require('./routes/productRouter')

const app = express()

// 解析 JSON 请求体
app.use(express.json())

// 使用路由
app.use('/users', userRouter)
app.use('/products', productRouter)

// 404 处理
app.use((req, res) => {
  res.status(404).send('Not Found')
})

app.listen(3000, () => {
  console.log('服务启动在 3000 端口')
})
```

## 路由参数

### 路径参数

```js [path-params.js]
// 获取单个资源
router.get('/:id', (req, res) => {
  res.send(`资源ID: ${req.params.id}`)
})

// 多个路径参数
router.get('/users/:userId/posts/:postId', (req, res) => {
  res.send(`用户 ${req.params.userId} 的文章 ${req.params.postId}`)
})
```

### 查询参数

```js [query-params.js]
// 分页查询
router.get('/users', (req, res) => {
  const { page = 1, limit = 10, sort } = req.query
  res.json({ page, limit, sort })
})

// 搜索
router.get('/search', (req, res) => {
  const { keyword, category } = req.query
  res.json({ keyword, category })
})
```

## 路由中间件

可以在路由中使用中间件：

```js [route-middleware.js]
const express = require('express')
const router = express.Router()

// 验证中间件
function validateId(req, res, next) {
  const id = parseInt(req.params.id)
  if (isNaN(id)) {
    return res.status(400).json({ error: '无效的ID' })
  }
  req.userId = id
  next()
}

// 应用中间件
router.get('/users/:id', validateId, (req, res) => {
  res.json({ id: req.userId })
})

module.exports = router
```

## 路由前缀

可以为整个路由器设置前缀：

```js [prefix.js]
const express = require('express')
const router = express.Router()

router.get('/users', (req, res) => {
  res.send('用户列表')
})

router.get('/users/:id', (req, res) => {
  res.send('用户详情')
})

// 在主应用中使用前缀
// app.use('/api/v1', router)
// 访问 /api/v1/users
// 访问 /api/v1/users/1

module.exports = router
```

## RESTful 路由设计

遵循 RESTful 风格的路由设计：

```js [restful.js]
const express = require('express')
const router = express.Router()

// GET /articles - 获取文章列表
router.get('/', (req, res) => {
  res.send('文章列表')
})

// GET /articles/new - 显示创建表单
router.get('/new', (req, res) => {
  res.send('创建文章表单')
})

// GET /articles/:id - 获取单篇文章
router.get('/:id', (req, res) => {
  res.send('文章详情')
})

// GET /articles/:id/edit - 显示编辑表单
router.get('/:id/edit', (req, res) => {
  res.send('编辑文章表单')
})

// POST /articles - 创建文章
router.post('/', (req, res) => {
  res.send('创建文章')
})

// PUT /articles/:id - 更新文章
router.put('/:id', (req, res) => {
  res.send('更新文章')
})

// DELETE /articles/:id - 删除文章
router.delete('/:id', (req, res) => {
  res.send('删除文章')
})

module.exports = router
```

::: tip 提示
- Router 可以帮助我们将路由按模块拆分
- 每个资源应该有独立的路由文件
- 遵循 RESTful 风格设计路由
:::
