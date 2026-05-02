# Next 部署与优化

Next.js 支持多种部署方式，并提供了丰富的优化选项来提升应用性能。

## 部署方式

### Vercel 部署（推荐）

Vercel 是 Next.js 的官方部署平台，提供零配置部署：

```bash [终端]
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel

# 生产部署
vercel --prod
```

### Docker 部署

```dockerfile [Dockerfile]
FROM node:18-alpine AS base

# 依赖
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN npm ci

# 构建
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# 运行
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

```bash [终端]
# 构建镜像
docker build -t nextjs-app .

# 运行容器
docker run -p 3000:3000 nextjs-app
```

### 自建服务器部署

```bash [终端]
# 构建
npm run build

# 启动
npm start
```

### PM2 部署

```bash [终端]
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start npm --name "nextjs-app" -- start

# 查看状态
pm2 status

# 设置开机自启
pm2 startup
pm2 save
```

## 性能优化

### 代码分割

Next.js 自动进行代码分割，你也可以手动优化：

```tsx [app/components/HeavyComponent.tsx]
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>加载中...</p>,
  ssr: false,
})

export default function Page() {
  return <HeavyComponent />
}
```

### 字体优化

```tsx [app/layout.tsx]
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html className={inter.variable}>
      <body>{children}</body>
    </html>
  )
}
```

### 脚本优化

```tsx [app/components/Analytics.tsx]
import Script from 'next/script'

export default function Analytics() {
  return (
    <>
      <Script
        src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'GA_MEASUREMENT_ID');
        `}
      </Script>
    </>
  )
}
```

## 构建优化

### 分析打包体积

```bash [终端]
# 安装分析工具
npm install @next/bundle-analyzer

# 使用
ANALYZE=true npm run build
```

```typescript [next.config.ts]
import withBundleAnalyzer from '@next/bundle-analyzer'

const nextConfig = {
  // 你的配置
}

export default withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
})(nextConfig)
```

### 优化包导入

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ['lodash', 'date-fns', 'react-icons'],
  },
}

export default nextConfig
```

## SEO 优化

### 元数据

```tsx [app/layout.tsx]
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    default: 'My App',
    template: '%s | My App',
  },
  description: 'My awesome application',
  keywords: ['nextjs', 'react', 'typescript'],
  authors: [{ name: 'Author', url: 'https://example.com' }],
  openGraph: {
    title: 'My App',
    description: 'My awesome application',
    url: 'https://example.com',
    siteName: 'My App',
    images: [
      {
        url: 'https://example.com/og.jpg',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'zh_CN',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My App',
    description: 'My awesome application',
    images: ['https://example.com/og.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}
```

### Sitemap

```typescript [app/sitemap.ts]
import { MetadataRoute } from 'next'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await fetchPosts()
  
  return [
    {
      url: 'https://example.com',
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    ...posts.map(post => ({
      url: `https://example.com/blog/${post.slug}`,
      lastModified: new Date(post.updatedAt),
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    })),
  ]
}
```

### Robots

```typescript [app/robots.ts]
import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/private/', '/admin/'],
    },
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

## 缓存策略

### 静态资源缓存

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
}

export default nextConfig
```

### API 缓存

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function GET() {
  const users = await fetchUsers()
  
  const response = NextResponse.json(users)
  response.headers.set('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=300')
  
  return response
}
```

## 监控与分析

### 性能监控

```tsx [app/layout.tsx]
import { SpeedInsights } from '@vercel/speed-insights/next'
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
        <Analytics />
      </body>
    </html>
  )
}
```

### 错误追踪

```bash [终端]
npm install @sentry/nextjs
```

```typescript [sentry.client.config.ts]
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
})
```

## 安全检查清单

### 1. 环境变量

::: danger
确保敏感环境变量不以 `NEXT_PUBLIC_` 开头，避免暴露在客户端。
:::

### 2. HTTPS

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ]
  },
}

export default nextConfig
```

### 3. 依赖审计

```bash [终端]
# 检查漏洞
npm audit

# 自动修复
npm audit fix

# 强制修复
npm audit fix --force
```

## 部署最佳实践

### 1. CI/CD 流程

```yaml [.github/workflows/deploy.yml]
name: Deploy
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - run: npm test
```

### 2. 环境变量管理

```bash [终端]
# 使用 .env 文件
echo ".env*.local" >> .gitignore

# 在部署平台设置环境变量
vercel env add DATABASE_URL
```

### 3. 监控告警

- 设置性能监控
- 配置错误告警
- 定期检查日志
