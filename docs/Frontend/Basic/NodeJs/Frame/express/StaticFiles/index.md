# 静态文件服务

Express 提供了内置的中间件来托管静态文件，如图片、CSS、JavaScript 等。

## express.static 中间件

### 基本使用

```js [static.js]
const express = require('express')
const app = express()

// 托管 public 目录下的静态文件
app.use(express.static('public'))

app.listen(3000)
```

访问方式：
- `http://localhost:3000/images/logo.png`
- `http://localhost:3000/css/style.css`
- `http://localhost:3000/js/app.js`

### 多个静态目录

```js [multiple-static.js]
// 设置多个静态文件目录
app.use(express.static('public'))
app.use(express.static('files'))
```

Express 会按照设置顺序查找文件。

### 虚拟路径前缀

```js [prefix.js]
// 使用虚拟路径前缀
app.use('/static', express.static('public'))
```

访问方式：
- `http://localhost:3000/static/images/logo.png`
- `http://localhost:3000/static/css/style.css`

## 配置选项

### 设置缓存

```js [cache.js]
app.use(express.static('public', {
  maxAge: '1d', // 缓存 1 天
  etag: true,
  lastModified: true
}))
```

### 隐藏文件

```js [dotfiles.js]
app.use(express.static('public', {
  dotfiles: 'ignore' // 忽略隐藏文件
}))
```

选项：
- `allow` - 允许访问隐藏文件
- `deny` - 拒绝访问隐藏文件
- `ignore` - 忽略隐藏文件（默认）

### 设置索引文件

```js [index.js]
app.use(express.static('public', {
  index: 'default.html' // 默认索引文件
}))
```

## 安全注意事项

### 不要暴露敏感文件

```js [security.js]
// 错误示例 - 暴露整个项目
app.use(express.static('.'))

// 正确示例 - 只暴露 public 目录
app.use(express.static('public'))
```

### 文件上传目录

```js [upload.js]
// 不要直接托管上传目录
// app.use(express.static('uploads'))

// 应该通过路由控制访问
app.get('/uploads/:filename', (req, res) => {
  const filename = req.params.filename
  // 验证文件名，防止路径遍历攻击
  res.sendFile(__dirname + '/uploads/' + filename)
})
```

## 完整示例

```js [full-example.js]
const express = require('express')
const path = require('path')
const app = express()

// 静态文件配置
app.use('/static', express.static(path.join(__dirname, 'public'), {
  maxAge: '1d',
  etag: true
}))

// 路由
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'index.html'))
})

app.listen(3000, () => {
  console.log('服务启动')
})
```

::: danger 注意
- 永远不要暴露敏感文件（如 .env、package.json）
- 使用路径前缀组织静态资源
- 注意文件上传安全，防止路径遍历攻击
:::
