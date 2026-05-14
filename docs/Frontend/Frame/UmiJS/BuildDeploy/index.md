# UmiJS 构建与部署

本指南将介绍如何构建和部署 UmiJS 项目，包括生产构建、部署到不同平台、性能优化等内容。

## 生产构建

### 基础构建

```bash
# 使用 npm
npm run build

# 使用 yarn
yarn build

# 使用 pnpm
pnpm build
```

构建完成后，产物会输出到 `dist` 目录。

### 构建分析

```bash
# 启用打包分析
ANALYZE=1 npm run build

# 或使用环境变量
cross-env ANALYZE=1 umi build
```

分析服务器会自动启动，可以查看打包结果的详细信息。

### 构建配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 启用文件名 hash
  hash: true,
  
  // 关闭 source map
  devtool: false,
  
  // 代码压缩配置
  terserOptions: {
    compress: {
      drop_console: true,
      drop_debugger: true,
    },
  },
  
  // 输出目录
  output: 'dist',
  
  // 静态资源路径
  publicPath: '/',
})
```

## 部署到静态服务器

### Nginx 部署

#### 1. 构建项目

```bash
npm run build
```

#### 2. 配置 Nginx

```nginx
server {
    listen 80;
    server_name example.com;
    
    root /var/www/umi-app/dist;
    index index.html;
    
    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;
}
```

#### 3. 部署文件

```bash
# 将 dist 目录复制到服务器
scp -r dist/* user@server:/var/www/umi-app/
```

### Apache 部署

#### 1. 创建 .htaccess

```apache
RewriteEngine On
RewriteBase /
RewriteRule ^index\.html$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]
```

#### 2. 部署文件

```bash
# 将 dist 目录复制到服务器
cp -r dist/* /var/www/html/
```

## 部署到云平台

### Vercel 部署

#### 1. 创建 vercel.json

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

#### 2. 部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel
```

### Netlify 部署

#### 1. 创建 netlify.toml

```toml
[build]
  publish = "dist"
  command = "npm run build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### 2. 部署

```bash
# 安装 Netlify CLI
npm i -g netlify-cli

# 部署
netlify deploy --prod
```

### GitHub Pages 部署

#### 1. 配置 publicPath

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 替换为你的仓库名
  publicPath: '/your-repo-name/',
  base: '/your-repo-name/',
})
```

#### 2. 创建部署脚本

```json
{
  "scripts": {
    "deploy": "npm run build && gh-pages -d dist"
  }
}
```

#### 3. 安装 gh-pages

```bash
npm install -D gh-pages
```

#### 4. 部署

```bash
npm run deploy
```

### Docker 部署

#### 1. 创建 Dockerfile

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 2. 创建 nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

#### 3. 构建和运行

```bash
# 构建镜像
docker build -t umi-app .

# 运行容器
docker run -p 80:80 umi-app
```

## 部署到子目录

### 配置 publicPath

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 子目录路径
  publicPath: '/my-app/',
  base: '/my-app/',
})
```

### Nginx 配置

```nginx
location /my-app/ {
    alias /var/www/my-app/dist/;
    try_files $uri $uri/ /my-app/index.html;
}
```

## 环境变量

### 创建环境文件

```bash
# .env.development
API_URL=http://localhost:3000

# .env.production
API_URL=https://api.example.com
```

### 使用环境变量

```typescript
const apiUrl = process.env.API_URL

export async function fetchData() {
  return fetch(`${apiUrl}/api/data`)
}
```

## 性能优化

### 代码分割

UmiJS 默认对路由组件进行代码分割：

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 启用动态导入
  dynamicImport: {
    loading: '@/components/Loading',
  },
})
```

### 图片优化

```tsx
// 使用 WebP 格式
<img src="/images/photo.webp" alt="photo" />

// 响应式图片
<picture>
  <source srcSet="/images/photo.webp" type="image/webp" />
  <source srcSet="/images/photo.jpg" type="image/jpeg" />
  <img src="/images/photo.jpg" alt="photo" />
</picture>
```

### 懒加载图片

```tsx
import { lazy } from 'react'

// 图片懒加载
<img loading="lazy" src="/images/photo.jpg" alt="photo" />
```

### CDN 加速

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 配置 CDN 路径
  publicPath: 'https://cdn.example.com/',
})
```

### Gzip 压缩

#### Nginx 配置

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

#### 构建时压缩

```bash
npm install -D compression-webpack-plugin
```

```typescript [.umirc.ts]
import { defineConfig } from 'umi'
import CompressionPlugin from 'compression-webpack-plugin'

export default defineConfig({
  chainWebpack(config) {
    config.plugin('compression').use(CompressionPlugin, [
      {
        algorithm: 'gzip',
        test: /\.(js|css|html|svg)$/,
        threshold: 10240,
        minRatio: 0.8,
      },
    ])
    return config
  },
})
```

## 缓存策略

### 文件名 Hash

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  hash: true,
})
```

### 缓存头配置

```nginx
# 静态资源长期缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# HTML 不缓存
location ~* \.html$ {
    expires -1;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

## HTTPS 部署

### 使用 Let's Encrypt

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d example.com

# 自动续期
sudo certbot renew --dry-run
```

### Nginx HTTPS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    root /var/www/umi-app/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

## CI/CD 部署

### GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Deploy to server
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_KEY }}
          source: "dist/*"
          target: "/var/www/umi-app"
```

## 部署检查清单

### 构建前检查

- [ ] 代码已通过 TypeScript 类型检查
- [ ] 代码已通过 ESLint 检查
- [ ] 所有测试用例通过
- [ ] 环境变量已配置
- [ ] 依赖版本已更新

### 构建后检查

- [ ] 构建产物大小合理
- [ ] 没有控制台错误和警告
- [ ] 静态资源路径正确
- [ ] 路由跳转正常
- [ ] 页面加载性能良好

### 部署后检查

- [ ] 网站可以正常访问
- [ ] HTTPS 配置正确
- [ ] 静态资源缓存策略生效
- [ ] 页面加载速度正常
- [ ] 移动端适配正常

## 最佳实践

1. **启用 Hash** 为文件名添加 hash，利用浏览器缓存
2. **配置 Gzip** 压缩静态资源，减少传输体积
3. **使用 CDN** 加速静态资源加载
4. **配置 HTTPS** 保证数据传输安全
5. **设置缓存策略** 合理配置缓存头
6. **监控性能** 使用工具监控页面性能
7. **自动化部署** 使用 CI/CD 自动构建和部署

::: tip 提示
- 生产环境不要开启 `devtool`，会暴露源码
- 使用 `hash: true` 可以利用浏览器长期缓存
- SPA 应用需要配置服务器支持 history 模式
- 使用 CDN 可以大幅提升静态资源加载速度
- 定期使用 Lighthouse 检查页面性能
:::

::: danger 注意事项
- 部署前确保代码没有 TypeScript 和 ESLint 错误
- 部署到子目录时必须配置 `publicPath`
- 生产环境不要包含敏感信息（API 密钥等）
- 确保服务器支持 SPA 路由的 fallback 配置
- HTTPS 证书需要定期续期
:::
