# Express 部署

将 Express 应用部署到生产环境需要考虑多个方面。

## 部署前准备

### 1. 环境配置

```js [env-config.js]
// 使用环境变量
const config = {
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  dbUrl: process.env.DB_URL
}

// 根据环境加载不同配置
const envConfig = require(`./config/${config.nodeEnv}.js`)
```

### 2. 生产环境优化

```js [production.js]
// 禁用视图缓存（开发环境）
if (process.env.NODE_ENV === 'production') {
  app.set('view cache', true)
}

// 启用压缩
const compression = require('compression')
app.use(compression())
```

### 3. 进程管理

使用 PM2 管理 Node.js 进程：

```shell [pm2.sh]
# 安装 PM2
npm i -g pm2

# 启动应用
pm2 start app.js --name "myapp"

# 查看状态
pm2 status

# 重启应用
pm2 restart myapp

# 停止应用
pm2 stop myapp

# 查看日志
pm2 logs myapp
```

### PM2 配置文件

```js [ecosystem.config.js]
module.exports = {
  apps: [{
    name: 'myapp',
    script: 'app.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
}
```

## Nginx 反向代理

### 安装 Nginx

```shell [nginx-install.sh]
# Ubuntu/Debian
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 配置反向代理

```nginx [nginx.conf]
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static {
        alias /var/www/myapp/public;
        expires 30d;
    }
}
```

### HTTPS 配置

```nginx [https.conf]
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

## Docker 部署

### 创建 Dockerfile

```dockerfile [Dockerfile]
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "app.js"]
```

### 创建 docker-compose.yml

```yaml [docker-compose.yml]
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_URL=mongodb://db:27017/myapp
    depends_on:
      - db
    restart: always

  db:
    image: mongo:latest
    volumes:
      - mongo-data:/data/db
    restart: always

volumes:
  mongo-data:
```

### 启动

```shell [docker.sh]
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 云平台部署

### 1. Heroku

```shell [heroku.sh]
# 安装 Heroku CLI
# 登录
heroku login

# 创建应用
heroku create myapp

# 部署
git push heroku main

# 设置环境变量
heroku config:set NODE_ENV=production
```

### 2. Vercel

```shell [vercel.sh]
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel

# 生产部署
vercel --prod
```

### 3. Railway

```shell [railway.sh]
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 部署
railway up
```

## 监控与日志

### 1. 使用 morgan 记录日志

```js [morgan.js]
const morgan = require('morgan')
const fs = require('fs')

const accessLogStream = fs.createWriteStream('access.log', { flags: 'a' })
app.use(morgan('combined', { stream: accessLogStream }))
```

### 2. 健康检查

```js [health.js]
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  })
})
```

### 3. 错误监控

```js [error-monitor.js]
// 使用 Sentry
const Sentry = require('@sentry/node')

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV
})

app.use(Sentry.Handlers.requestHandler())
app.use(Sentry.Handlers.errorHandler())
```

## 部署检查清单

### 部署前

- [ ] 设置 NODE_ENV=production
- [ ] 配置环境变量
- [ ] 安装生产依赖 (npm ci --only=production)
- [ ] 启用压缩
- [ ] 配置错误处理
- [ ] 设置日志记录

### 部署后

- [ ] 验证应用正常运行
- [ ] 检查日志输出
- [ ] 测试 API 端点
- [ ] 配置监控告警
- [ ] 设置自动备份
- [ ] 配置 SSL 证书

::: tip 提示
- 生产环境使用 PM2 管理进程
- 使用 Nginx 作为反向代理
- 配置 HTTPS 保证数据安全
- 定期备份数据库和文件
:::
