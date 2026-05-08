# Koa 部署

将 Koa 应用部署到生产环境需要考虑多个方面。

## 部署前准备

### 环境配置

```js [env-config.js]
const config = {
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development'
}

module.exports = config
```

### 生产环境优化

```js [production.js]
const Koa = require('koa')
const compress = require('koa-compress')

const app = new Koa()

// 启用压缩
if (process.env.NODE_ENV === 'production') {
  app.use(compress())
}
```

## PM2 进程管理

### 安装

```shell [install-pm2.sh]
npm i -g pm2
```

### 启动应用

```shell [pm2.sh]
# 启动应用
pm2 start app.js --name "koa-app"

# 查看状态
pm2 status

# 重启应用
pm2 restart koa-app

# 停止应用
pm2 stop koa-app

# 查看日志
pm2 logs koa-app
```

### PM2 配置文件

```js [ecosystem.config.js]
module.exports = {
  apps: [{
    name: 'koa-app',
    script: 'app.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log'
  }]
}
```

## Nginx 反向代理

### 配置

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
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态文件
    location /static {
        alias /var/www/koa-app/public;
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

### Dockerfile

```dockerfile [Dockerfile]
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "app.js"]
```

### docker-compose.yml

```yaml [docker-compose.yml]
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    restart: always
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

### Heroku

```shell [heroku.sh]
# 登录
heroku login

# 创建应用
heroku create myapp

# 部署
git push heroku main

# 设置环境变量
heroku config:set NODE_ENV=production
```

### Vercel

```shell [vercel.sh]
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel

# 生产部署
vercel --prod
```

## 监控与日志

### 使用 koa-logger

```js [logger.js]
const logger = require('koa-logger')

app.use(logger())
```

### 健康检查

```js [health.js]
app.use(async (ctx) => {
  if (ctx.path === '/health') {
    ctx.body = {
      status: 'ok',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    }
  }
})
```

## 部署检查清单

### 部署前

- [ ] 设置 NODE_ENV=production
- [ ] 配置环境变量
- [ ] 安装生产依赖
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
:::
