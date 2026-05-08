# 安全最佳实践

Express 应用需要考虑多种安全问题，包括 XSS、CSRF、SQL 注入等。

## 常见安全威胁

### 1. XSS（跨站脚本攻击）

攻击者通过注入恶意脚本到网页中执行。

**防御方法**：

```js [xss-defense.js]
const helmet = require('helmet')
app.use(helmet())

// 转义用户输入
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}
```

### 2. CSRF（跨站请求伪造）

攻击者伪造用户请求执行操作。

**防御方法**：

```js [csrf-defense.js]
const csrf = require('csurf')

// 启用 CSRF 保护
app.use(csrf({ cookie: true }))

// 在表单中添加 CSRF token
app.get('/form', (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() })
})

// 验证 CSRF token
app.post('/submit', (req, res) => {
  res.send('提交成功')
})
```

### 3. SQL 注入

通过恶意 SQL 语句操作数据库。

**防御方法**：

```js [sql-injection.js]
// 错误示例 - 字符串拼接
const query = `SELECT * FROM users WHERE id = ${userId}`

// 正确示例 - 使用参数化查询
const query = 'SELECT * FROM users WHERE id = ?'
db.query(query, [userId])
```

## 使用 helmet 增强安全

### 安装

```shell [install.sh]
npm i helmet
```

### 基本使用

```js [helmet.js]
const helmet = require('helmet')
app.use(helmet())
```

### 配置选项

```js [helmet-config.js]
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"]
    }
  },
  crossOriginEmbedderPolicy: false
}))
```

## 速率限制

防止暴力攻击和 API 滥用。

### 安装

```shell [install-rate.sh]
npm i express-rate-limit
```

### 使用

```js [rate-limit.js]
const rateLimit = require('express-rate-limit')

// 全局限制
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 最多 100 次请求
  message: '请求过于频繁，请稍后再试'
})

app.use(limiter)

// API 路由限制
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 50,
  message: 'API 请求过于频繁'
})

app.use('/api/', apiLimiter)
```

## 输入验证

### 使用 express-validator

```shell [install-validator.sh]
npm i express-validator
```

```js [validator.js]
const { body, validationResult } = require('express-validator')

app.post('/users', [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 6 }),
  body('name').trim().isLength({ min: 1, max: 50 })
], (req, res) => {
  const errors = validationResult(req)
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() })
  }
  
  // 处理有效数据
  res.send('用户创建成功')
})
```

## CORS 配置

### 安装

```shell [install-cors.sh]
npm i cors
```

### 基本使用

```js [cors.js]
const cors = require('cors')

// 允许所有跨域
app.use(cors())

// 配置允许的域名
app.use(cors({
  origin: ['http://localhost:3000', 'https://example.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}))
```

## 密码安全

### 使用 bcrypt 加密

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

// 使用
const hashedPassword = await hashPassword('123456')
const isValid = await verifyPassword('123456', hashedPassword)
```

## 环境变量安全

### 使用 dotenv

```shell [install-dotenv.sh]
npm i dotenv
```

```js [dotenv.js]
require('dotenv').config()

const config = {
  port: process.env.PORT || 3000,
  dbUrl: process.env.DB_URL,
  jwtSecret: process.env.JWT_SECRET
}

// 不要将 .env 文件提交到版本控制
```

### .env 文件

```env [.env]
PORT=3000
DB_URL=mongodb://localhost:27017/myapp
JWT_SECRET=your-secret-key-here
NODE_ENV=production
```

## 安全清单

### 必须做的

- [ ] 使用 helmet 设置安全头
- [ ] 启用 HTTPS
- [ ] 使用环境变量管理密钥
- [ ] 验证和清理用户输入
- [ ] 使用参数化查询
- [ ] 设置速率限制
- [ ] 配置 CORS
- [ ] 加密敏感数据

### 不要做的

- [ ] 不要在代码中硬编码密钥
- [ ] 不要暴露错误堆栈信息
- [ ] 不要信任用户输入
- [ ] 不要使用已知的漏洞依赖
- [ ] 不要将 .env 文件提交到 Git

::: danger 注意
- 永远不要将敏感信息提交到版本控制
- 生产环境必须使用 HTTPS
- 定期更新依赖包修复安全漏洞
:::
