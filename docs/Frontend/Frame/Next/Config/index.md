# Next 配置详解

Next.js 提供了丰富的配置选项，允许你自定义构建、开发和生产行为。

## next.config.ts

### 基本配置

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // 基础配置
  reactStrictMode: true,
  swcMinify: true,
  
  // 输出配置
  output: 'standalone',
  
  // 基础路径
  basePath: '',
  
  // 资产前缀
  assetPrefix: '',
  
  // 图片配置
  images: {
    domains: ['example.com'],
    formats: ['image/webp', 'image/avif'],
  },
}

export default nextConfig
```

## 环境变量

### 环境文件

```text
.env                  # 所有环境共享
.env.local            # 本地开发（不提交到 Git）
.env.development      # 开发环境
.env.production       # 生产环境
.env.test             # 测试环境
```

### 使用环境变量

```env [.env.local]
# 服务端环境变量
DATABASE_URL=postgresql://localhost/mydb
API_SECRET=secret-key

# 客户端环境变量
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

```typescript [lib/api.ts]
// 服务端可用
const dbUrl = process.env.DATABASE_URL

// 客户端和服务端都可用
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```

## 图片优化

### 基本配置

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  images: {
    // 允许的外部域名
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'example.com',
        pathname: '/**',
      },
    ],
    
    // 图片尺寸
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    
    // 格式
    formats: ['image/webp', 'image/avif'],
    
    // 最小缓存 TTL
    minimumCacheTTL: 60,
    
    // 危险性允许所有 URL（不推荐）
    // dangerouslyAllowSVG: true,
  },
}

export default nextConfig
```

### 使用优化图片

```tsx [app/components/HeroImage.tsx]
import Image from 'next/image'

export default function HeroImage() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero"
      width={1200}
      height={600}
      priority
      sizes="(max-width: 768px) 100vw, 1200px"
    />
  )
}
```

## 重写和重定向

### 重写

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/blog/:slug',
        destination: '/posts/:slug',
      },
      {
        source: '/api/:path*',
        destination: 'https://api.example.com/:path*',
      },
    ]
  },
}

export default nextConfig
```

### 重定向

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async redirects() {
    return [
      {
        source: '/old-blog',
        destination: '/blog',
        permanent: true,
      },
      {
        source: '/users/:id',
        destination: '/profile/:id',
        permanent: true,
      },
    ]
  },
}

export default nextConfig
```

### 自定义头部

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}

export default nextConfig
```

## Webpack 配置

### 自定义 Webpack

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  webpack(config, { isServer }) {
    // 添加 loader
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    })
    
    // 添加别名
    config.resolve.alias['@'] = path.join(__dirname, 'src')
    
    return config
  },
}

export default nextConfig
```

### 环境变量注入

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
    CUSTOM_URL: process.env.CUSTOM_URL,
  },
}

export default nextConfig
```

## TypeScript 配置

### tsconfig.json

```json [tsconfig.json]
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

## ESLint 配置

### .eslintrc.json

```json [.eslintrc.json]
{
  "extends": "next/core-web-vitals",
  "rules": {
    "@typescript-eslint/no-explicit-any": "off",
    "react/no-unescaped-entities": "off"
  }
}
```

### 自定义规则

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
}

export default nextConfig
```

## 实验性功能

### 启用实验性功能

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
    typedRoutes: true,
    optimizePackageImports: ['lodash', 'date-fns'],
  },
}

export default nextConfig
```

## 输出配置

### 独立输出

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
}

export default nextConfig
```

### 导出静态站点

```typescript [next.config.ts]
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
}

export default nextConfig
```

## 最佳实践

### 1. 环境变量安全

::: danger
永远不要将敏感信息（如 API Key、数据库密码）暴露在客户端。只有以 `NEXT_PUBLIC_` 开头的变量才能在客户端访问。
:::

### 2. 图片优化

```typescript
// 好：配置允许的外部域名
images: {
  remotePatterns: [
    {
      protocol: 'https',
      hostname: 'cdn.example.com',
    },
  ],
}

// 不好：使用 dangerouslyAllowSVG
images: {
  dangerouslyAllowSVG: true,
}
```

### 3. 缓存策略

```typescript
// 好：设置合理的缓存时间
images: {
  minimumCacheTTL: 60,
}

// 好：使用 webp 格式
images: {
  formats: ['image/webp', 'image/avif'],
}
```

