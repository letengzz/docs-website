# Koa 模板引擎

Koa 可以使用多种模板引擎来渲染页面。

## 常用模板引擎

### 1. EJS

```shell [install.sh]
npm i koa-views ejs
```

```js [ejs.js]
const views = require('koa-views')
const path = require('path')

app.use(views(path.join(__dirname, 'views'), {
  extension: 'ejs'
}))

app.use(async (ctx) => {
  await ctx.render('index', {
    title: '首页',
    users: [
      { name: '张三', age: 25 },
      { name: '李四', age: 30 }
    ]
  })
})
```

```ejs [views/index.ejs]
<!DOCTYPE html>
<html>
<head>
  <title><%= title %></title>
</head>
<body>
  <h1><%= title %></h1>
  <ul>
    <% users.forEach(user => { %>
      <li><%= user.name %> - <%= user.age %>岁</li>
    <% }) %>
  </ul>
</body>
</html>
```

### 2. Pug

```shell [install-pug.sh]
npm i koa-views pug
```

```js [pug.js]
app.use(views(path.join(__dirname, 'views'), {
  extension: 'pug'
}))

app.use(async (ctx) => {
  await ctx.render('index', {
    title: '首页',
    users: [
      { name: '张三', age: 25 }
    ]
  })
})
```

```pug [views/index.pug]
html
  head
    title= title
  body
    h1= title
    ul
      each user in users
        li #{user.name} - #{user.age}岁
```

### 3. Handlebars

```shell [install-hbs.sh]
npm i koa-views koa-hbs
```

```js [hbs.js]
const render = require('koa-hbs')

app.use(render.middleware({
  viewPath: path.join(__dirname, 'views'),
  defaultLayout: 'main',
  helpers: {
    json: (context) => JSON.stringify(context)
  }
}))

app.use(async (ctx) => {
  await ctx.render('index', {
    title: '首页'
  })
})
```

## 模板继承

### EJS 布局

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

## 完整示例

```js [full-example.js]
const Koa = require('koa')
const views = require('koa-views')
const path = require('path')

const app = new Koa()

// 配置模板
app.use(views(path.join(__dirname, 'views'), {
  extension: 'ejs',
  options: {
    helpers: {
      formatDate: (date) => new Date(date).toLocaleDateString()
    }
  }
}))

// 路由
app.use(async (ctx) => {
  await ctx.render('users', {
    title: '用户列表',
    users: [
      { id: 1, name: '张三', age: 25, created: '2024-01-01' },
      { id: 2, name: '李四', age: 30, created: '2024-01-02' }
    ]
  })
})

app.listen(3000)
```

::: tip 提示
- 使用 koa-views 统一管理模板
- 可以选择 EJS、Pug、Handlebars 等
- 支持模板继承和组件化
:::
