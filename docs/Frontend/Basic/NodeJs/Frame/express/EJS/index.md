# EJS 模板引擎

**模板引擎**：分离 用户界面和业务数据 的一种技术

EJS 是一个高效的 Javascript 的模板引擎

- 官网: https://ejs.co/
- 中文站：https://ejs.bootcss.com/

## EJS 下载安装

命令行下运行：

```shell [install.sh]
npm i ejs --save
```

## EJS 配置

```js [app.js]
const express = require('express')
const app = express()

// 设置模板引擎为 ejs
app.set('view engine', 'ejs')

// 设置模板文件存放目录
app.set('views', './views')

app.listen(3000, () => {
  console.log('服务启动')
})
```

## EJS 常用语法

### 执行JS代码

```ejs
<% code %>
```

### 输出转义的数据到模板上

```ejs
<%= data %>
```

### 输出非转义的数据到模板

```ejs
<%- data %>
```

## 基本使用

### 渲染模板

```js [render.js]
//1.引入ejs
const ejs = require('ejs');

//2.定义数据
let person = ['张三','李四','王二麻子'];

//3.ejs解析模板返回结构
//<%= %> 是ejs解析内容的标记，作用是输出当前表达式的执行结构
let html = ejs.render('<%= person.join(",") %>', {person: person});

//4.输出结果
console.log(html);
// 输出: 张三,李四,王二麻子
```

### Express 中使用

```js [express-ejs.js]
const express = require('express')
const app = express()

// 设置模板引擎
app.set('view engine', 'ejs')
app.set('views', './views')

app.get('/', (req, res) => {
  // 渲染模板并传递数据
  res.render('index', {
    title: '首页',
    users: [
      { name: '张三', age: 25 },
      { name: '李四', age: 30 }
    ]
  })
})

app.listen(3000)
```

### 模板文件

```ejs [views/index.ejs]
<!DOCTYPE html>
<html>
<head>
  <title><%= title %></title>
</head>
<body>
  <h1><%= title %></h1>
  
  <ul>
    <% users.forEach(function(user) { %>
      <li><%= user.name %> - <%= user.age %>岁</li>
    <% }) %>
  </ul>
</body>
</html>
```

## 语法详解

### 变量输出

```ejs [variable.ejs]
<!-- 输出变量 -->
<p><%= name %></p>

<!-- 输出对象属性 -->
<p><%= user.name %></p>

<!-- 输出数组元素 -->
<p><%= arr[0] %></p>

<!-- 输出函数返回值 -->
<p><%= getName() %></p>
```

### 流程控制

```ejs [control.ejs]
<!-- if 判断 -->
<% if (user.age >= 18) { %>
  <p>成年人</p>
<% } else { %>
  <p>未成年人</p>
<% } %>

<!-- for 循环 -->
<% for(let i = 0; i < users.length; i++) { %>
  <p><%= users[i].name %></p>
<% } %>

<!-- forEach 循环 -->
<% users.forEach(function(user) { %>
  <p><%= user.name %></p>
<% }) %>
```

### 包含子模板

```ejs [include.ejs]
<!-- 引入头部 -->
<%- include('header') %>

<h1>页面内容</h1>

<!-- 引入底部 -->
<%- include('footer') %>
```

### 注释

```ejs [comment.ejs]
<!-- EJS 注释（不会输出到HTML） -->
<%# 这是注释 %>

<!-- HTML 注释（会输出到HTML） -->
<!-- 这是HTML注释 -->
```

## 完整示例

### 项目结构

```text
myapp/
├── views/
│   ├── layout.ejs
│   ├── header.ejs
│   ├── footer.ejs
│   └── users.ejs
├── app.js
└── package.json
```

### 布局模板

```ejs [views/layout.ejs]
<!DOCTYPE html>
<html>
<head>
  <title><%= title %></title>
</head>
<body>
  <%- include('header') %>
  
  <main>
    <%- body %>
  </main>
  
  <%- include('footer') %>
</body>
</html>
```

### 头部模板

```ejs [views/header.ejs]
<header>
  <nav>
    <a href="/">首页</a>
    <a href="/users">用户</a>
    <a href="/about">关于</a>
  </nav>
</header>
```

### 底部模板

```ejs [views/footer.ejs]
<footer>
  <p>&copy; 2024 我的网站</p>
</footer>
```

### 用户列表模板

```ejs [views/users.ejs]
<h1>用户列表</h1>

<table>
  <thead>
    <tr>
      <th>姓名</th>
      <th>年龄</th>
      <th>操作</th>
    </tr>
  </thead>
  <tbody>
    <% users.forEach(function(user) { %>
      <tr>
        <td><%= user.name %></td>
        <td><%= user.age %></td>
        <td>
          <a href="/users/<%= user.id %>">查看</a>
          <a href="/users/<%= user.id %>/edit">编辑</a>
        </td>
      </tr>
    <% }) %>
  </tbody>
</table>
```

### 路由处理

```js [routes.js]
const express = require('express')
const router = express.Router()

router.get('/users', (req, res) => {
  const users = [
    { id: 1, name: '张三', age: 25 },
    { id: 2, name: '李四', age: 30 },
    { id: 3, name: '王五', age: 28 }
  ]
  
  res.render('users', {
    title: '用户列表',
    users: users
  })
})

module.exports = router
```

## 高级用法

### 自定义分隔符

```js [delimiter.js]
const ejs = require('ejs')

// 使用自定义分隔符
ejs.delimiter = '?'

let html = ejs.render('<? = name ?>', { name: '张三' })
console.log(html)
```

### 过滤器

```ejs [filter.ejs]
<!-- 转义HTML -->
<%= '<script>' %>
<!-- 输出: &lt;script&gt; -->

<!-- 不转义HTML -->
<%- '<strong>粗体</strong>' %>
<!-- 输出: <strong>粗体</strong> -->
```

### 条件渲染

```ejs [conditional.ejs]
<% if (users && users.length > 0) { %>
  <p>共有 <%= users.length %> 个用户</p>
<% } else { %>
  <p>暂无用户</p>
<% } %>
```

::: tip 提示
- EJS 模板文件默认使用 .ejs 扩展名
- 使用 res.render() 渲染模板
- 模板文件默认放在 views 目录
- 使用 include 可以引入子模板
:::
