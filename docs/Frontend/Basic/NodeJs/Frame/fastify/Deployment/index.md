# Fastify 部署

将 Fastify 应用部署到生产环境。

## 部署前准备

### 环境配置

```js [env-config.js]
const config = {
  port: process.env.PORT || 3000,
  host: process.env.HOST || '0.0.0.0',
  nodeEnv: process.env.NODE_ENV || 'development'
}

module.exports = config
```

### 生产环境优化

```js [production.js]
const Fastify = require('fastify')

const app = Fastify({
  logger: {
    level: process.env.NODE_ENV === 'production' ? 'warn' : 'debug'
  },
  // 启用 HTTP/2
  http2: false,
  // 信任代理
  trustProxy: true
})
```

## PM2 进程管理

### 安装

```shell [install-pm2.sh]
npm i -g pm2
```

### 启动应用

```shell [pm2.sh]
# 启动应用
pm2 start app.js --name "fastify-app"

# 集群模式
pm2 start app.js -i max --name "fastify-cluster"

# 查看状态
pm2 status

# 重启
pm2 restart fastify-app

# 停止
pm2 stop fastify-app

# 查看日志
pm2 logs fastify-app
```

### PM2 配置文件

```js [ecosystem.config.js]
module.exports = {
  apps: [{
    name: 'fastify-app',
    script: 'app.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    merge_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
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
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /public {
        alias /var/www/fastify-app/public;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### HTTPS 配置

```nginx [https.conf]
server {
    listen 443 ssl http2;
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

### .dockerignore

```dockerignore [.dockerignore]
node_modules
npm-debug.log
.git
.env
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
      - PORT=3000
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 启动

```shell [docker.sh]
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps

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

### Railway

```shell [railway.sh]
# 安装 CLI
npm i -g @railway/cli

# 登录
railway login

# 部署
railway up
```

## 监控与日志

### 健康检查

```js [health.js]
app.get('/health', async (request, reply) => {
  return {
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  }
})
```

### 性能监控

```js [metrics.js]
app.get('/metrics', async (request, reply) => {
  return {
    memory: process.memoryUsage(),
    cpu: process.cpuUsage(),
    uptime: process.uptime()
  }
})
```

## 部署检查清单

### 部署前

- [ ] 设置 NODE_ENV=production
- [ ] 配置环境变量
- [ ] 安装生产依赖 (npm ci --only=production)
- [ ] 配置日志级别
- [ ] 配置错误处理
- [ ] 启用 HTTPS

### 部署后

- [ ] 验证应用正常运行
- [ ] 检查日志输出
- [ ] 测试 API 端点
- [ ] 配置监控告警
- [ ] 设置自动备份
- [ ] 配置 SSL 证书

::: tip 提示
- 生产环境使用 PM2 集群模式
- 使用 Nginx 作为反向代理
- 配置 HTTPS 保证数据安全
- 定期更新依赖包
:::
