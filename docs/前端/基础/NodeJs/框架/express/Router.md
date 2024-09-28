# Router

Express 中的 Router 是一个完整的中间件和路由系统，可以看做是一个小型的 app 对象。

**Router 作用**：对路由进行模块化，更好的管理路由 

## Router 使用

 创建独立的 JS 文件（homeRouter.js） 主文件 app.post('/login', urlParser, (request,response)=>{ //获取请求体数据 //console.log(request.body); //用户名 console.log(request.body.username); //密码 console.log(request.body.userpass); response.send('获取请求体数据'); }); [Object: null prototype] { username: 'admin', userpass: '123456' } //1. 导入 express const express = require('express'); //2. 创建路由器对象 const router = express.Router(); //3. 在 router 对象身上添加路由 router.get('/', (req, res) => { res.send('首页'); }) router.get('/cart', (req, res) => { res.send('购物车'); }); //4. 暴露 module.exports = router; 