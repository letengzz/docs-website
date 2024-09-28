# EJS 模板引擎

**模板引擎**：分离 用户界面和业务数据 的一种技术 

EJS 是一个高效的 Javascript 的模板引擎

- 官网: https://ejs.co/ 
- 中文站：https://ejs.bootcss.com/ 

## EJS 下载安装

代码示例 命令行下运行 

## EJS 常用语法

 执行JS代码 输出转义的数据到模板上 const express = require('express'); const app = express(); //5.引入子路由文件 const homeRouter = require('./routes/homeRouter'); //6.设置和使用中间件 app.use(homeRouter); app.listen(3000,()=>{ console.log('3000 端口启动....'); }) npm i ejs --save //1.引入ejs const ejs = require('ejs'); //2.定义数据 let person = ['张三','李四','王二麻子']; //3.ejs解析模板返回结构 //<%= %> 是ejs解析内容的标记，作用是输出当前表达式的执行结构 let html = ejs.render(‘<%= person.join(",") %>’, {person:person}); //4.输出结果 console.log(html); <% code %> 输出非转义的数据到模板