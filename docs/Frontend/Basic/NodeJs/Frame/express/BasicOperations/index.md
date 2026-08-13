# Express 基础操作

## Express 安装

Express 本身是一个 npm 包，所以可以通过 npm 安装

```shell [install.sh]
npm init
npm i express
```

## Express 使用操作

**使用操作**：

1. 创建 JS 文件：

   ```js [app.js]
   //1. 导入express
   const express = require('express');
   //2. 创建应用对象
   const app = express();
   //3. 创建路由规则
   app.get('/home',(req,res) =>{
       res.end('hello express server');
   });
   //4. 监听端口 启动服务
   app.listen(3000,()=>{
       console.log('服务已经启动, 端口监听为 3000...');
   });
   ```

2. 命令行下执行脚本

   ```shell [run.sh]
   node <文件名>
   # 或者
   nodemon <文件名>
   ```

3. 然后在浏览器就可以访问 http://127.0.0.1:3000/home

## Express 路由

路由确定了应用程序如何响应客户端对特定端点的请求

一个路由的组成有 请求方法 ， **路径**和**回调函数**组成 express 中提供了一系列方法，可以很方便的使用路由。

**使用格式**：

```js [route-format.js]
app.<method>(path，callback)
```

**例**：

```js [routes.js]
//导入 express
const express = require('express');

//创建应用对象
const app = express();

//创建 get 路由
app.get('/home', (req, res) => {
    res.send('网站首页');
});

//首页路由
app.get('/', (req,res) => {
    res.send('我才是真正的首页');
});

//创建 post 路由
app.post('/login', (req, res) => {
    res.send('登录成功');
});

//匹配所有的请求方法
app.all('/search', (req, res) => {
    res.send('1 秒钟为您找到相关结果约 100,000,000 个');
});

//自定义 404 路由
app.all("*", (req, res) => {
    res.send('<h1>404 Not Found</h1>')
});


//监听端口 启动服务
app.listen(3000,() =>{
    console.log('服务已经启动, 端口监听为 3000');
});
```

## Express 获取请求参数

Express 框架封装了一些 API 来方便获取请求报文中的数据，并且兼容原生 HTTP 模块的获取方式

```js [request.js]
//导入 express
const express = require('express');
//创建应用对象
const app = express();
//获取请求的路由规则
app.get('/request', (req, res) => {
    //1. 获取报文的方式与原生 HTTP 获取方式是兼容的
    console.log(req.method);
    console.log(req.url);
    console.log(req.httpVersion);
    console.log(req.headers);
    
    //2. express 独有的获取报文的方式
    //获取查询字符串
    console.log(req.query);
    // 获取指定的请求头
    console.log(req.get('host'));
    res.send('请求报文的获取');
});

//启动服务
app.listen(3000, () => {
    console.log('启动成功....')
});
```

## Express 获取路由参数

路由参数指的是 URL 路径中的参数 (数据)

```js [route-params.js]
//导入 express
const express = require('express');
//创建应用对象
const app = express();
//获取请求的路由规则
app.get('/:id', (req, res) => {
    res.send('商品详情, 商品 id 为' + req.params.id);
});

//启动服务
app.listen(3000, () => {
    console.log('启动成功....')
});
```

## Express 响应设置

express 框架封装了一些 API 来方便给客户端响应数据，并且兼容原生 HTTP 模块的获取方式

```js [response.js]
//导入 express
const express = require('express');
//创建应用对象
const app = express();
//获取请求的路由规则
app.get("/response", (req, res) => {
    //1. express 中设置响应的方式兼容 HTTP 模块的方式
    res.statusCode = 404;
    res.statusMessage = 'xxx';
    res.setHeader('abc','xyz');
    res.write('响应体');
    res.end('xxx');

    //2. express 的响应方法
    res.status(500); //设置响应状态码
    res.set('xxx','yyy');//设置响应头
    res.send('中文响应不乱码');//设置响应体
    //连贯操作
    res.status(404).set('xxx','yyy').send('你好朋友');

    //3. 其他响应
    res.redirect('http://hjc.com')//重定向
    res.download('./package.json');//下载响应
    res.json();//响应 JSON
    res.sendFile(__dirname + '/home.html') //响应文件内容
});


//启动服务
app.listen(3000, () => {
    console.log('启动成功....')
});
```

## 项目结构

一个标准的 Express 项目结构：

```text
myapp/
├── node_modules/
├── public/
│   ├── css/
│   ├── js/
│   └── images/
├── routes/
│   ├── index.js
│   └── users.js
├── views/
│   ├── index.ejs
│   └── error.ejs
├── app.js
└── package.json
```

## 常用配置

### 环境变量

```js [env.js]
const express = require('express')
const app = express()

// 从环境变量获取端口
const PORT = process.env.PORT || 3000

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`)
})
```

### 解析请求体

```js [body-parser.js]
const express = require('express')
const app = express()

// 解析 application/json
app.use(express.json())

// 解析 application/x-www-form-urlencoded
app.use(express.urlencoded({ extended: true }))

app.post('/users', (req, res) => {
  console.log(req.body)
  res.send('用户创建成功')
})
```

::: tip 提示
- Express 4.x 是目前最稳定的版本
- 使用 nodemon 可以自动重启服务
- 推荐使用环境变量管理配置
:::
