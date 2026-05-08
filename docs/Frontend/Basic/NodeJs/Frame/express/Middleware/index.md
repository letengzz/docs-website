# Express 中间件

中间件 (Middleware) 本质是一个回调函数

中间件函数可以像路由回调一样访问 请求对象 (request)， 响应对象(response)

**中间件的作用**：使用函数封装公共操作，简化代码

**中间件的类型**：

- 全局中间件
- 路由中间件

## 定义全局中间件

每一个请求 到达服务端之后 都会执行全局中间件函数

```js [global-middleware.js]
// 声明中间件函数
let recordMiddleware = function(request, response, next){
  // 实现功能代码
  console.log('请求时间:', Date.now())
  console.log('请求方法:', request.method)
  console.log('请求路径:', request.url)
  
  // 执行next函数(当如果希望执行完中间件函数之后，仍然继续执行路由中的回调函数，必须调用next)
  next();
}

// 应用中间件
app.use(recordMiddleware)
```

声明时可以直接将匿名函数传递给 use：

```js [anonymous-middleware.js]
app.use(function (request, response, next) {
  console.log('定义第一个中间件');
  next();
})
```

## 多个全局中间件

express 允许使用 app.use() 定义多个全局中间件

```js [multiple-middleware.js]
app.use(function (request, response, next) {
  console.log('定义第一个中间件');
  next();
})

app.use(function (request, response, next) {
  console.log('定义第二个中间件');
  next();
})
```

## 定义路由中间件

如果 只需要对某一些路由进行功能封装 ，则就需要路由中间件

调用格式如下：

```js [route-middleware.js]
app.get('/路径', 中间件函数, (request, response) => {
  // 路由处理
});

app.get('/路径', 中间件函数1, 中间件函数2, (request, response) => {
  // 路由处理
});
```

**示例**：

```js [route-middleware-example.js]
// 定义路由中间件
function authMiddleware(req, res, next) {
  const token = req.headers.authorization
  
  if (!token) {
    return res.status(401).send('未授权')
  }
  
  // 验证 token
  if (token === 'valid-token') {
    next()
  } else {
    res.status(403).send('无效的 token')
  }
}

// 应用路由中间件
app.get('/admin', authMiddleware, (req, res) => {
  res.send('管理员页面')
})

app.get('/user', authMiddleware, (req, res) => {
  res.send('用户页面')
})
```

## 静态资源中间件

express 内置处理静态资源的中间件

```js [static-middleware.js]
// 静态资源中间件的设置，将当前文件夹下的public目录作为网站的根目录
app.use(express.static('./public'));
```

**注意事项**:

1. index.html 文件为默认打开的资源
2. 如果静态资源与路由规则同时匹配，谁先匹配谁就响应
3. 路由响应动态资源，静态资源中间件响应静态资源

```js [static-example.js]
//引入express框架
const express = require('express');
//创建服务对象
const app = express();

// 静态资源中间件的设置，将当前文件夹下的public目录作为网站的根目录
app.use(express.static('./public'));
//当然这个目录中都是一些静态资源

//如果访问的内容经常变化，还是需要设置路由
//但是，在这里有一个问题，如果public目录下有index.html文件，单独也有index.html的路由，
//则谁书写在前，优先执行谁
app.get('/index.html',(request,response)=>{
  response.send('首页');
});

//监听端口
app.listen(3000,()=>{
  console.log('3000 端口启动....');
});
```

## 获取请求体数据 body-parser

Express 可以使用 body-parser 包处理请求体

**第一步**：安装

```shell [install.sh]
npm i body-parser
```

**第二步**：导入 body-parser 包

**第三步**：获取中间件函数

**第四步**：设置路由中间件，然后使用 request.body 来获取请求体数据

```js [body-parser.js]
//引入express框架
const express = require('express');
//导入 body-parser
const bodyParser = require('body-parser');
//创建服务对象
const app = express();

//处理 querystring 格式的请求体
let urlParser = bodyParser.urlencoded({extended: false});

//处理 JSON 格式的请求体
let jsonParser = bodyParser.json();

// 使用中间件
app.post('/login', urlParser, (req, res) => {
  console.log(req.body)
  res.send('登录成功')
})

app.post('/api/data', jsonParser, (req, res) => {
  console.log(req.body)
  res.json({ message: '数据接收成功' })
})

//监听端口
app.listen(3000,()=>{
  console.log('3000 端口启动....');
});
```

获取到的请求体数据：

```js [request-body.js]
// POST /login
// Content-Type: application/x-www-form-urlencoded
// username=admin&password=123456

// req.body 输出:
// { username: 'admin', password: '123456' }

// POST /api/data
// Content-Type: application/json
// { "name": "张三", "age": 25 }

// req.body 输出:
// { name: '张三', age: 25 }
```

## Express 内置中间件

Express 4.16+ 版本内置了常用的中间件：

```js [builtin-middleware.js]
const express = require('express')
const app = express()

// 解析 application/json
app.use(express.json())

// 解析 application/x-www-form-urlencoded
app.use(express.urlencoded({ extended: true }))

// 解析 text/plain
app.use(express.text())

// 解析 application/octet-stream
app.use(express.raw())
```

## 第三方中间件

### morgan - 日志记录

```js [morgan.js]
const morgan = require('morgan')

// 使用 morgan 中间件记录日志
app.use(morgan('dev'))
```

### cors - 跨域处理

```js [cors.js]
const cors = require('cors')

// 允许所有跨域请求
app.use(cors())

// 或者配置允许的域名
app.use(cors({
  origin: 'http://localhost:3000'
}))
```

### helmet - 安全头设置

```js [helmet.js]
const helmet = require('helmet')

// 设置安全相关的 HTTP 头
app.use(helmet())
```

## 中间件执行顺序

```js [order.js]
// 1. 全局中间件（按定义顺序执行）
app.use(middleware1)
app.use(middleware2)

// 2. 路由中间件（按匹配顺序执行）
app.get('/path', middleware3, (req, res) => {})
app.get('/path', middleware4, (req, res) => {})

// 3. 错误处理中间件（最后执行）
app.use(errorHandler)
```

::: tip 提示
- 中间件中必须调用 next() 才能继续执行后续处理
- 错误处理中间件有 4 个参数 (err, req, res, next)
- 静态资源中间件应该放在路由之前
:::
