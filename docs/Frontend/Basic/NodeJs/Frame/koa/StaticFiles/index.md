# Koa 静态文件服务

Koa 使用 koa-static 中间件来提供静态文件服务。

## 安装

```shell [install.sh]
npm i koa-static
```

## 基本使用

```js [static.js]
const Koa = require('koa')
const serve = require('koa-static')
const path = require('path')

const app = new Koa()

// 托管 public 目录
app.use(serve(path.join(__dirname, 'public')))

app.listen(3000)
```

访问方式：
- `http://localhost:3000/images/logo.png`
- `http://localhost:3000/css/style.css`
- `http://localhost:3000/js/app.js`

## 配置选项

### 设置缓存

```js [cache.js]
app.use(serve(path.join(__dirname, 'public'), {
  maxAge: 86400000, // 缓存 1 天（毫秒）
  immutable: true
}))
```

### 隐藏文件

```js [dotfiles.js]
app.use(serve(path.join(__dirname, 'public'), {
  hidden: false // 不显示隐藏文件
}))
```

### 设置索引文件

```js [index.js]
app.use(serve(path.join(__dirname, 'public'), {
  index: 'default.html' // 默认索引文件
}))
```

## 多个静态目录

```js [multiple.js]
app.use(serve(path.join(__dirname, 'public')))
app.use(serve(path.join(__dirname, 'uploads')))
```

## 虚拟路径前缀

```js [prefix.js]
const mount = require('koa-mount')

// 使用 /static 前缀
app.use(mount('/static', serve(path.join(__dirname, 'public'))))

// 访问 /static/images/logo.png
```

## 完整示例

```js [full-example.js]
const Koa = require('koa')
const serve = require('koa-static')
const path = require('path')

const app = new Koa()

// 静态文件配置
app.use(serve(path.join(__dirname, 'public'), {
  maxAge: 86400000,
  hidden: false,
  index: 'index.html'
}))

// 上传目录
app.use(serve(path.join(__dirname, 'uploads'), {
  maxAge: 3600000
}))

app.listen(3000, () => {
  console.log('服务启动')
})
```

::: danger 注意
- 不要暴露敏感文件
- 使用路径前缀组织静态资源
- 注意文件上传安全
:::
