# 配置与部署

## nuxt.config.ts

主要配置文件：

```ts [nuxt.config.ts]
export default defineNuxtConfig({
  // 应用配置
  app: {
    head: {
      title: 'My Nuxt App',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ]
    }
  },
  
  // 模块
  modules: [],
  
  // CSS
  css: ['~/assets/css/main.css'],
  
  // 构建配置
  build: {},
  
  // 开发工具
  devtools: { enabled: true }
})
```

## 环境变量

在项目根目录创建 `.env` 文件：

```env [.env]
NUXT_PUBLIC_API_BASE=https://api.example.com
NUXT_SECRET_KEY=your-secret-key
```

使用环境变量：

```ts
const config = useRuntimeConfig()
console.log(config.public.apiBase)
console.log(config.secretKey)
```

## 构建配置

### 构建模式

在 `nuxt.config.ts` 中配置：

```ts [nuxt.config.ts]
export default defineNuxtConfig({
  ssr: true // 启用 SSR
})
```

### 构建命令

```bash [终端]
# 开发模式
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview

# 静态站点生成
npm run generate
```

## 部署

### Node.js 服务器

```bash [终端]
npm run build
node .output/server/index.mjs
```

### 静态托管

```bash [终端]
npm run generate
```

将 `.output/public/` 目录部署到任何静态托管服务。

### Docker

创建 `Dockerfile`：

```dockerfile [Dockerfile]
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

### Vercel

安装 Vercel CLI 并部署：

```bash [终端]
npm i -g vercel
vercel
```

### Netlify

在 `nuxt.config.ts` 中配置：

```ts [nuxt.config.ts]
export default defineNuxtConfig({
  nitro: {
    preset: 'netlify'
  }
})
```

## 性能优化

### 代码分割

Nuxt 自动进行代码分割，每个页面单独打包。

### 图片优化

使用 Nuxt Image 模块：

```ts [nuxt.config.ts]
export default defineNuxtConfig({
  modules: ['@nuxt/image']
})
```

### 缓存配置

```ts [nuxt.config.ts]
export default defineNuxtConfig({
  nitro: {
    compressPublicAssets: true,
    routeRules: {
      '/api/**': { cache: { maxAge: 60 } }
    }
  }
})
```
