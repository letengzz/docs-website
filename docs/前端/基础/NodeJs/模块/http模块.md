# http 模块

- [HTTP 协议](../../../其他/HTTP协议.md)

## 创建HTTP服务

通过使用http模块中的`createServer()`创建服务

**http.createServer 里的回调函数的执行时机**： 当接收到 HTTP 请求的时候，就会执行

```js
//1. 导入http模块
const http = require('http');

//2. 创建服务对象 create 创建 server 服务
// request 意为请求. 是对请求报文的封装对象, 通过 request 对象可以获得请求报文的数据
// response 意为响应. 是对响应报文的封装对象, 通过 response 对象可以设置响应报文
const server = http.createServer((request,response) =>{
    response.end('Hello HTTP server');
});

//3. 监听端口, 启动服务
server.listen(9000,() =>{
    console.log('服务已经启动, 端口 9000 监听中...');
});
```

当访问 http://localhost:9000/ 时，网页会显示 `Hello HTTP server`：

![image-20231004185109939](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041853418.png)

**停止服务**：命令行 `ctrl + c`停止服务

**注意**：

- 当服务启动后，更新代码必须要重启服务才能生效(可以安装nodemon就可以对代码进行实时更新)

- 响应内容中文内容乱码解决办法(`setHeader()`必须要在`end()`方法之前)：

  ```js
  response.setHeader('content-type','text/html;charset=utf-8');
  ```

- 当端口号被占用时：

  > Error: listen EADDRINUSE: address already in use :::9000

  - 关闭当前正在运行监听端口的服务 (如果端口被其他程序占用，可以使用**资源监视器**找到占用端口的程序，然后使用任务管理器关闭对应的程序)
  - 修改成其他端口号

  **拓展**：HTTP 协议默认端口是 80 。HTTPS 协议的默认端口是 443, HTTP 服务开发常用端口有 3000，
  8080，8090，9000 等

## 获取请求报文

通过 `request`对象来获取请求的数据。

![image-20231004202327065](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310042023982.png)

**获取请求方法**：

```js
console.log('获取请求方法:'+request.method);
```

**获取请求路径** (只能获取路径以及查询字符串，无法获取 URL 中的域名以及协议的内容)：

```js
console.log('获取请求路径:'+request.url); //只包含url中的路径与查询字符串
```

**获取HTTP协议的版本号**：

```js
console.log('获取HTTP协议的版本号:'+request.httpVersion);
```

**获取HTTP的请求头** (将请求信息转化成一个对象，并将属性名都转化成了**小写**)：

```js
//获取HTTP请求头
console.log(request.headers);
//获取HTTP某个请求头
console.log(request.headers.host);
```

**获取请求体**：

```js
//1.声明变量
let body = '';
//2.绑定data事件
request.on('data',chunk => {
    body += chunk;
})
//3.绑定end事件
request.on('end',()=>{
    console.log(body);
    //响应
    response.end('End');
});
```

**获取URL路径**：

```js
let pathname = require('url').parse(request.url).pathname;
console.log(pathname);
```

```js
let pathname2 = new URL(request.url,'http://127.0.0.1').pathname;
console.log(pathname2);
```

**获取URL查询字符串**：

```js
//true 将查询字符串转换为对象
let username = require('url').parse(request.url,true).query.username;
console.log(username);
```

```js
let username2 = new URL(request.url,'http://127.0.0.1').searchParams.get('username');
console.log(username2);
```

**注意**：

1. 如果访问网站的时候，只填写了 IP 地址或者是域名信息，此时请求的路径为 `/` 
2. favicon.ico 请求是属于浏览器自动发送的请求

**例**：搭建HTTP服务

![image-20231004204411634](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310042044212.png)

```js
//1.导入http模块
const http = require('http');

//2.创建服务对象
const server = http.createServer((request, response) =>{
    //解构赋值 简写 获取请求方法、路径
    let {url,method} = request;
    //解决乱码
    response.setHeader("Content-Type","text/html;charset=utf-8");
    //获取请求的url路径
    let pathname = new URL(url,'http://127.0.0.1').pathname;
    //判断
    if(pathname == '/register' && method == 'GET'){
        //注册
        response.end('注册界面');  //设置响应体
    }else if(pathname == '/login' && method == 'GET'){
        //登录
        response.end('登录界面');  //设置响应体
    }else {
        response.end('<h1>404 Not Found</h1>');
    }
});
//3.监听端口，启动服务
server.listen(9000,()=>{
    console.log('服务正在运行中');
});
```

## 设置响应报文

通过 `response`对象来获取响应的数据。

![image-20231011173021015](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310111732839.png)

**设置响应状态码**：

```js
response.statusCode = 250;
```

**设置响应状态描述**：

```js
response.statusMessage = 'Okk';
```

**设置响应头信息**：

```js
response.setHeader("Content-Type","text/html;charset=utf-8");
//设置多个相同名的响应头
response.setHeader("test",['a','b','c']);
```

**设置响应体**：

```js
//1.write和end结合使用，响应体相对分散
response.write('xx');
response.write('xx');
response.write('xx');
response.end();
```

```js
//2.单独使用end方法 响应体相对集中
response.end('xxx');
```

**例**：

```js
const http = require('http')
http.createServer(function (request, response) {
    // 发送 HTTP 头部 
    // HTTP 状态值: 200 : OK
    // 内容类型: text/plain
    response.writeHead(200, {'Content-Type': 'text/plain'})
    // 发送响应数据 "Hello World"
    response.end('Hello Server')
}).listen(8888)
// 终端打印如下信息
console.log('Server running at http://127.0.0.1:8888/')
```

搭建 HTTP 服务，响应一个 4 行 3 列的表格，并且要求表格有隔行换色效果，且点击单元格能高亮显示

```js
//导入 http 模块
const http = require('http');

//创建服务对象
const server = http.createServer((request, response) => {
  response.end(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Document</title>
      <style>
        td{
          padding: 20px 40px;
        }
        table tr:nth-child(odd){
          background: #aef;
        }
        table tr:nth-child(even){
          background: #fcb;
        }
        table, td{
          border-collapse: collapse;
        }
      </style>
    </head>
    <body>
      <table border="1">
        <tr><td></td><td></td><td></td></tr>
        <tr><td></td><td></td><td></td></tr>
        <tr><td></td><td></td><td></td></tr>
        <tr><td></td><td></td><td></td></tr>
      </table>
      <script>
        //获取所有的 td
        let tds = document.querySelectorAll('td');
        //遍历
        tds.forEach(item => {
          item.onclick = function(){
            this.style.background = '#222';
          }
        })
      </script>
    </body>
    </html>
  `); //设置响应体
});

//监听端口, 启动服务
server.listen(9000, () => {
  console.log('服务已经启动....')
});
```

改造：

> index.html

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
  <style>
    td {
      padding: 20px 40px;
    }

    table tr:nth-child(odd) {
      background: rgb(179, 165, 201);
    }

    table tr:nth-child(even) {
      background: #fcb;
    }

    table,
    td {
      border-collapse: collapse;
    }
  </style>
</head>

<body>
  <table border="1">
    <tr>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </table>
  <script>
    //获取所有的 td
    let tds = document.querySelectorAll('td');
    //遍历
    tds.forEach(item => {
      item.onclick = function () {
        this.style.background = '#222';
      }
    })
  </script>
</body>

</html>
```

```js
//导入 http 模块
const http = require('http');
const fs = require('fs');

//创建服务对象
const server = http.createServer((request, response) => {
  //读取文件内容
  let html = fs.readFileSync(__dirname + '/index.html');
  
  response.end(html); //设置响应体
});

//监听端口, 启动服务
server.listen(9000, () => {
  console.log('服务已经启动....')
});
```

## 网页资源的基本加载过程

网页资源的加载都是循序渐进的，首先获取 HTML 的内容， 然后解析 HTML 在发送其他资源的请求，如
CSS，Javascript，图片等。

## 静态资源服务

**静态资源**：指内容长时间不发生改变的资源，例如图片，视频，CSS 文件，JS文件，HTML文件，字体文
件等
**动态资源**：指内容经常更新的资源，例如百度首页，网易首页，京东搜索列表页面等

### 引入外部资源

当将HTML中的css、JavaScript拆分为文件，发现访问的样式和效果并没有生效，但是CSS、JavaScript都正常请求。因为CSS、JavaScript请求报文的回调函数请求响应结果同样都是HTML结果。

> index.html

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
  <link rel="stylesheet" href="./style.css">
</head>

<body>
<table border="1">
  <tr>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</table>
<script src="./script.js"></script>
</body>

</html>
```

> style.css

```css
td {
    padding: 20px 40px;
}

table tr:nth-child(odd) {
    background: rgb(179, 165, 201);
}

table tr:nth-child(even) {
    background: #fcb;
}

table,
td {
    border-collapse: collapse;
}
```

> script.js

```js
//获取所有的 td
let tds = document.querySelectorAll('td');
//遍历
tds.forEach(item => {
    item.onclick = function () {
        this.style.background = '#222';
    }
})
```

> server.js

```js
//导入 http 模块
const http = require('http');
const fs = require('fs');

//创建服务对象
const server = http.createServer((request, response) => {
    //读取文件内容
    let html = fs.readFileSync(__dirname + '/index.html');

    response.end(html); //设置响应体
});

//监听端口, 启动服务
server.listen(9000, () => {
    console.log('服务已经启动....')
});
```

解决办法：根据请求的路径响应对应的结果

> server.js

```js
//导入 http 模块
const http = require('http');
const fs = require('fs');

//创建服务对象
const server = http.createServer((request, response) => {
    //获取请求url的路径
    let {pathname} = new URL(request.url,'http://127.0.0.1');
    if (pathname === '/index.html'){
        //读取文件内容
        let html = fs.readFileSync(__dirname + '/index.html');
        response.end(html); //设置响应体
    }else if (pathname === '/style.css'){
        //读取文件内容
        let css = fs.readFileSync(__dirname + '/style.css');
        response.end(css); //设置响应体
    }else if (pathname === '/script.js'){
        //读取文件内容
        let js = fs.readFileSync(__dirname + '/script.js');
        response.end(js); //设置响应体
    }else {
        response.statusCode = 404;
        response.end('<h1>404 Not Found</h1>');
    }
});

//监听端口, 启动服务
server.listen(9000, () => {
    console.log('服务已经启动....')
});
```

但是设置过于麻烦，根据规律可知，url的请求路径 跟 请求路径有关联：请求路径 = `__dirname` + url路径

```js
//导入 http 模块
const http = require('http');
const fs = require('fs');

//创建服务对象
const server = http.createServer((request, response) => {
    //获取请求url的路径
    let {pathname} = new URL(request.url,'http://127.0.0.1');
    //声明根目录
    let root = __dirname;
    //拼接文件路径
    let filePath = root + pathname;
    //读取文件 fs 异步API
    fs.readFile(filePath,(err,data) =>{
       if (err){
           response.statusCode = 500;
           response.end('500 Server Error');
           return;
       }
       //响应文件内容
        response.end(data);
    });
});

//监听端口, 启动服务
server.listen(9000, () => {
    console.log('服务已经启动....')
});
```

### 网站根目录或静态资源目录

HTTP 服务在哪个文件夹中寻找静态资源，那个文件夹就是**静态资源目录**，也称之为**网站根目录**

## 网页中的 URL

网页中的 URL 主要分为两大类：相对路径与绝对路径。

网页中使用 URL 的场景包括但不限于如下场景：

- a 标签 href
- link 标签 href
- script 标签 src
- img 标签 src
- video audio 标签 src
- form 中的 action
- AJAX 请求中的 URL

### 绝对路径

绝对路径可靠性强，而且相对容易理解，在项目中运用较多。

![image-20231013133130643](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310131331314.png)

### 相对路径

相对路径在发送请求时，需要与当前页面 URL 路径进行计算，得到完整 URL 后，再发送请求。
例如当前网页 url 为 http://www.hjc-demo.com/course/h5.html

![image-20231013133656668](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310131336815.png)

## 设置资源类型(mime类型)

媒体类型（通常称为 `Multipurpose Internet Mail Extensions` 或 MIME 类型 ）是一种标准，用来表示文档、文件或字节流的性质和格式。

**mime 类型结构**： 

```
[type]/[subType]
```

例：`text/html`、`text/css`、`image/jpeg`、`image/png`、`application/json`

HTTP 服务可以设置响应头 `Content-Type` 来表明响应体的 MIME 类型，浏览器会根据该类型决定如何处理
资源。

常见文件对应的 mime 类型：

```js
html: 'text/html',
css: 'text/css',
js: 'text/javascript',
png: 'image/png',
jpg: 'image/jpeg',
gif: 'image/gif',
mp4: 'video/mp4',
mp3: 'audio/mpeg',
json: 'application/json'
```

**说明**：对于未知的资源类型，可以选择 `application/octet-stream` 类型，浏览器在遇到该类型的响应
时，会对响应体内容进行独立存储，也就是常见的下载效果

```js
//导入 http 模块
const http = require('http');
const fs = require('fs');
const path = require('path');

//声明变量
let mimes = {
    html: 'text/html',
    css: 'text/css',
    js: 'text/javascript',
    png: 'image/png',
    jpg: 'image/jpeg',
    gif: 'image/gif',
    mp4: 'video/mp4',
    mp3: 'audio/mpeg',
    json: 'application/json'
}

//创建服务对象
const server = http.createServer((request, response) => {
    //获取请求url的路径
    let pathname = new URL(request.url, 'http://127.0.0.1').pathname;
    //声明根目录
    let root = __dirname;
    //拼接文件路径
    let filePath = root + pathname;
    //读取文件 fs 异步API
    fs.readFile(filePath, (err, data) => {
        if (err) {
            response.statusCode = 500;
            response.end('500 Server Error');
            return;
        }
        //获取文件的后缀名
        let ext = path.extname(filePath).slice(1);
        //获取对应的类型
        let type = mimes[ext];
        //判断是否匹配到
        if (type){
            //匹配到了
            response.setHeader("Content-Type",type);
        }else {
            //没有匹配到
            response.setHeader("Content-Type","application/octet-stream");
        }
        //响应文件内容
        response.end(data);
    });
});

//监听端口, 启动服务
server.listen(9000, () => {
    console.log('服务已经启动....');
});
```

**乱码问题**：

- 当文件为HTML时，设置Meta标签和设置响应头两种方式。**设置响应头 的编码方式优先**

  ```js
  response.setHeader("Content-Type","text/html;charset=utf-8");
  ```

- 对于网页的外部资源，如：CSS、JavaScript、图片。设置响应时没有必要设置字符集，这些资源进入网页中都会根据网页的字符集来对响应进行处理。

```js
//导入 http 模块
const http = require('http');
const fs = require('fs');
const path = require('path');

//声明变量
let mimes = {
    html: 'text/html',
    css: 'text/css',
    js: 'text/javascript',
    png: 'image/png',
    jpg: 'image/jpeg',
    gif: 'image/gif',
    mp4: 'video/mp4',
    mp3: 'audio/mpeg',
    json: 'application/json'
}

//创建服务对象
const server = http.createServer((request, response) => {
    //获取请求url的路径
    let pathname = new URL(request.url, 'http://127.0.0.1').pathname;
    //声明根目录
    let root = __dirname;
    //拼接文件路径
    let filePath = root + pathname;
    //读取文件 fs 异步API
    fs.readFile(filePath, (err, data) => {
        if (err) {
            response.statusCode = 500;
            response.end('500 Server Error');
            return;
        }
        //获取文件的后缀名
        let ext = path.extname(filePath).slice(1);
        //获取对应的类型
        let type = mimes[ext];
        //判断是否匹配到
        if (type) {
            //匹配到了
            if (type === 'html') {
                response.setHeader("Content-Type", type + ';charset=utf-8');
            } else {
                response.setHeader("Content-Type", type);
            }
        } else {
            //没有匹配到
            response.setHeader("Content-Type", "application/octet-stream");
        }
        //响应文件内容
        response.end(data);
    });
});

//监听端口, 启动服务
server.listen(9000, () => {
    console.log('服务已经启动....');
});
```

## 错误处理

当错误处理时，需要根据不同的错误来返回不同的错误编号和错误提示。

API 文档：https://nodejs.cn/api/errors.html

```js
//导入 http 模块
const http = require('http');
const fs = require('fs');
const path = require('path');

//声明变量
let mimes = {
    html: 'text/html',
    css: 'text/css',
    js: 'text/javascript',
    png: 'image/png',
    jpg: 'image/jpeg',
    gif: 'image/gif',
    mp4: 'video/mp4',
    mp3: 'audio/mpeg',
    json: 'application/json'
}

//创建服务对象
const server = http.createServer((request, response) => {
    // 处理请求方式错误
    if (request.method !== 'GET') {
        response.statusCode = 405;
        response.end('<h1>405 Method Not Allowed</h1>');
        return;
    }
    //获取请求url的路径
    let pathname = new URL(request.url, 'http://127.0.0.1').pathname;
    //声明根目录
    let root = __dirname;
    //拼接文件路径
    let filePath = root + pathname;
    //读取文件 fs 异步API
    fs.readFile(filePath, (err, data) => {
        if (err) {
            switch (err.code) {
                case 'ENOENT':
                    response.statusCode = 404;
                    response.end('<h1>404 Not Found</h1>');
                case 'EPERM':
                    response.statusCode = 403;
                    response.end('<h1>403 Forbidden</h1>');
                default:
                    response.statusCode = 500;
                    response.end('<h1>Internal Server Error</h1>');
            }
            return;
        }
        //获取文件的后缀名
        let ext = path.extname(filePath).slice(1);
        //获取对应的类型
        let type = mimes[ext];
        //判断是否匹配到
        if (type) {
            //匹配到了
            if (type === 'html') {
                response.setHeader("Content-Type", type + ';charset=utf-8');
            } else {
                response.setHeader("Content-Type", type);
            }
        } else {
            //没有匹配到
            response.setHeader("Content-Type", "application/octet-stream");
        }
        //响应文件内容
        response.end(data);
    });
});

//监听端口, 启动服务
server.listen(9000, () => {
    console.log('服务已经启动....');
});
```

## GET 和 POST 请求

GET 请求的情况：

- 在地址栏直接输入 url 访问
- 点击 a 链接
- link 标签引入 css
- script 标签引入 js
- img 标签引入图片
- form 标签中的 method 为 get (不区分大小写)
- AJAX 中的 get 请求

POST 请求的情况：

- form 标签中的 method 为 post (不区分大小写)
- AJAX 的 post 请求

**GET和POST请求的区别**：

GET 和 POST 是 HTTP 协议请求的两种方式。

- **作用**：GET 主要用来获取数据，POST 主要用来提交数据

- **参数位置**：GET 带参数请求是将参数缀到 URL 之后，在地址栏中输入 url 访问网站就是 GET 请求，POST 带参数请求是将参数放到请求体中

- **安全性**：POST 请求相对 GET 安全一些，因为在浏览器中参数会暴露在地址栏
- **请求大小**：GET 请求大小有限制，一般为 2K，而 POST 请求则没有大小限制
