# Koa 安全最佳实践

Koa 应用需要考虑多种安全问题。

## 常见安全威胁

### 1. XSS（跨站脚本攻击）

```js [xss.js]
const helmet = require('koa-helmet')

app.use(helmet())

// 转义用户输入
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
```

### 2. CSRF（跨站请求伪造）

```shell [install-csurf.sh]
npm i koa-csrf
```

```js [csrf.js]
const csrf = require('koa-csrf')

app.use(csrf({
  secret: 'your-secret-key',
  cookie: true
}))
```

### 3. SQL 注入

```js [sql-injection.js]
// 错误示例
const query = `SELECT * FROM users WHERE id = ${userId}`

// 正确示例 - 使用参数化查询
const query = 'SELECT * FROM users WHERE id = ?'
db.query(query, [userId])
```

## 使用 koa-helmet

```shell [install-helmet.sh]
npm i koa-helmet
```

```js [helmet.js]
const helmet = require('koa-helmet')

app.use(helmet())

// 或者配置
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"]
    }
  }
}))
```

## 速率限制

```shell [install-rate.sh]
npm i koa-ratelimit
```

```js [rate-limit.js]
const rateLimit = require('koa-ratelimit')

const limiter = rateLimit({
  db: new Map(),
  duration: 60000, // 1 分钟
  max: 100, // 最多 100 次请求
  errorMessage: '请求过于频繁'
})

app.use(limiter)
```

## CORS 配置

```shell [install-cors.sh]
npm i @koa/cors
```

```js [cors.js]
const cors = require('@koa/cors')

// 允许所有跨域
app.use(cors())

// 配置允许的域名
app.use(cors({
  origin: 'http://localhost:3000',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}))
```

## 输入验证

```shell [install-validator.sh]
npm i koa-joi-validate
```

```js [validator.js]
const validate = require('koa-joi-validate')
const Joi = require('joi')

app.use(validate({
  query: Joi.object({
    page: Joi.number().integer().min(1),
    limit: Joi.number().integer().min(1).max(100)
  }),
  body: Joi.object({
    name: Joi.string().min(2).max(50).required(),
    email: Joi.string().email().required()
  })
}))
```

## 密码安全

```shell [install-bcrypt.sh]
npm i bcrypt
```

```js [bcrypt.js]
const bcrypt = require('bcrypt')

// 加密密码
async function hashPassword(password) {
  const salt = await bcrypt.genSalt(10)
  return bcrypt.hash(password, salt)
}

// 验证密码
async function verifyPassword(password, hash) {
  return bcrypt.compare(password, hash)
}
```

## 安全清单

### 必须做的

- [ ] 使用 koa-helmet 设置安全头
- [ ] 启用 HTTPS
- [ ] 使用环境变量管理密钥
- [ ] 验证和清理用户输入
- [ ] 使用参数化查询
- [ ] 设置速率限制
- [ ] 配置 CORS
- [ ] 加密敏感数据

::: danger 注意
- 永远不要将敏感信息提交到版本控制
- 生产环境必须使用 HTTPS
- 定期更新依赖包修复安全漏洞
:::
