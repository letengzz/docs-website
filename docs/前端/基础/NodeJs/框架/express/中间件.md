# Express 中间件

中间件 (Middleware) 本质是一个回调函数 

中间件函数可以像路由回调一样访问 请求对象 (request)， 响应对象(response) 

**中间件的作用**：使用函数封装公共操作，简化代码

**中间件的类型**：

- 全局中间件
- 路由中间件

## 定义全局中间件

 每一个请求 到达服务端之后 都会执行全局中间件函数 声明中间件函数 //获取请求的路由规则 app.get("/response", (req, res) => { //1. express 中设置响应的方式兼容 HTTP 模块的方式 res.statusCode = 404; res.statusMessage = 'xxx'; res.setHeader('abc','xyz'); res.write('响应体'); res.end('xxx'); //2. express 的响应方法 res.status(500); //设置响应状态码 res.set('xxx','yyy');//设置响应头 res.send('中文响应不乱码');//设置响应体 //连贯操作 res.status(404).set('xxx','yyy').send('你好朋友') //3. 其他响应 res.redirect('http://atguigu.com')//重定向 res.download('./package.json');//下载响应 res.json();//响应 JSON res.sendFile(__dirname + '/home.html') //响应文件内容 }); let recordMiddleware = function(request,response,next){ //实现功能代码 //..... //执行next函数(当如果希望执行完中间件函数之后，仍然继续执行路由中的回调函数，必须调用next) next(); } 应用中间件 声明时可以直接将匿名函数传递给 use 5.3.2 

## 多个全局中间件

 express 允许使用 app.use() 定义多个全局中间件 

## 定义路由中间件

如果 只需要对某一些路由进行功能封装 ，则就需要路由中间件 调用格式如下： app.use(recordMiddleware); app.use(function (request, response, next) { console.log('定义第一个中间件'); next(); }) app.use(function (request, response, next) { console.log('定义第一个中间件'); next(); }) app.use(function (request, response, next) { console.log('定义第二个中间件'); next(); }) app.get('/路径',`中间件函数`,(request,response)=>{ }); app.get('/路径',`中间件函数1`,`中间件函数2`,(request,response)=>{ }); 5.4 

## 静态资源中间件

 express 内置处理静态资源的中间件 注意事项: 1. index.html 文件为默认打开的资源 2. 如果静态资源与路由规则同时匹配，谁先匹配谁就响应 3. 路由响应动态资源，静态资源中间件响应静态资源 5.5 

## 获取请求体数据 body-parser

Express 可以使用 body-parser 包处理请求体 第一步：安装 第二步：导入 body-parser 包 第三步：获取中间件函数 第四步：设置路由中间件，然后使用 request.body 来获取请求体数据 //引入express框架 const express = require('express'); //创建服务对象 const app = express(); //静态资源中间件的设置，将当前文件夹下的public目录作为网站的根目录 app.use(express.static('./public')); //当然这个目录中都是一些静态资源 //如果访问的内容经常变化，还是需要设置路由 //但是，在这里有一个问题，如果public目录下有index.html文件，单独也有index.html的路由， //则谁书写在前，优先执行谁 app.get('/index.html',(request,response)=>{ respsonse.send('首页'); }); //监听端口 app.listen(3000,()=>{ console.log('3000 端口启动....'); }); npm i body-parser const bodyParser = require('body-parser'); //处理 querystring 格式的请求体 let urlParser = bodyParser.urlencoded({extended:false})); //处理 JSON 格式的请求体 let jsonParser = bodyParser.json(); 获取到的请求体数据： 