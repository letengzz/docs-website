# Vue2 部署

## 构建生产版本

```bash
# 使用 Vue CLI 构建
npm run build

# 构建完成后会生成 dist 目录
```

## 静态服务器部署

### 使用 Nginx

```nginx [nginx.conf]
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 使用 Apache

```apache [.htaccess]
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

## 云平台部署

### Vercel

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel
```

### Netlify

```bash
# 安装 Netlify CLI
npm install -g netlify-cli

# 部署
netlify deploy --prod --dir=dist
```

### GitHub Pages

```bash
# 安装 gh-pages
npm install gh-pages --save-dev

# 在 package.json 中添加脚本
{
  "scripts": {
    "deploy": "gh-pages -d dist"
  }
}

# 部署
npm run build
npm run deploy
```

## Docker 部署

```dockerfile [Dockerfile]
# 构建阶段
FROM node:14 as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
# 构建镜像
docker build -t vue-app .

# 运行容器
docker run -d -p 80:80 vue-app
```

## 注意事项

### 路由模式

- **hash 模式**：使用 URL 的 hash 来模拟完整的 URL，不需要服务器配置
- **history 模式**：需要服务器配置，将所有请求指向 index.html

```javascript [router-mode.js]
const router = new VueRouter({
  mode: 'history', // 或 'hash'
  routes: [...]
})
```

### 环境变量

```bash
# .env.production
VUE_APP_API_URL=https://api.example.com
```

### 性能优化

- 启用 gzip 压缩
- 使用 CDN 加载第三方库
- 代码分割和懒加载
- 图片优化

::: tip 提示
- 生产环境使用 npm run build 构建
- history 模式需要服务器配置
- 推荐使用 HTTPS
- 启用静态资源缓存
:::
