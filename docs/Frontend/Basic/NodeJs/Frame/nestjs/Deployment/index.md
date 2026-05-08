# NestJS 部署

将 NestJS 应用部署到生产环境。

## 构建应用

### 生产构建

```shell [build.sh]
# 构建应用
npm run build

# 构建产物在 dist 目录
ls dist/
```

### package.json 配置

```json [package.json]
{
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:prod": "node dist/main"
  }
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
pm2 start dist/main.js --name "nestjs-app"

# 集群模式
pm2 start dist/main.js -i max --name "nestjs-cluster"

# 查看状态
pm2 status

# 重启
pm2 restart nestjs-app

# 停止
pm2 stop nestjs-app

# 查看日志
pm2 logs nestjs-app
```

### PM2 配置文件

```js [ecosystem.config.js]
module.exports = {
  apps: [{
    name: 'nestjs-app',
    script: 'dist/main.js',
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
        alias /var/www/nestjs-app/public;
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
# 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

# 生产阶段
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["node", "dist/main.js"]
```

### .dockerignore

```dockerignore [.dockerignore]
node_modules
dist
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

### 健康检查

```typescript [health.controller.ts]
import { Controller, Get } from '@nestjs/common'

@Controller('health')
export class HealthController {
  @Get()
  check() {
    return {
      status: 'ok',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    }
  }
}
```

### 性能监控

```typescript [metrics.controller.ts]
import { Controller, Get } from '@nestjs/common'

@Controller('metrics')
export class MetricsController {
  @Get()
  getMetrics() {
    return {
      memory: process.memoryUsage(),
      cpu: process.cpuUsage(),
      uptime: process.uptime()
    }
  }
}
```

## 部署检查清单

### 部署前

- [ ] 运行生产构建 (npm run build)
- [ ] 设置 NODE_ENV=production
- [ ] 配置环境变量
- [ ] 安装生产依赖
- [ ] 配置日志级别
- [ ] 配置错误处理

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
- 使用多阶段 Docker 构建减小镜像体积
:::
