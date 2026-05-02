# Next 中间件

Next.js 中间件允许你在请求完成之前运行代码，常用于身份验证、重定向、日志记录等场景。

## 中间件基础

### 创建中间件

在项目根目录创建 `middleware.ts` 文件：

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 中间件逻辑
  return NextResponse.next()
}

// 配置匹配路径
export const config = {
  matcher: '/about/:path*',
}
```

### 匹配器配置

```typescript [middleware.ts]
export const config = {
  matcher: [
    '/about/:path*',           // 匹配 /about 及其子路径
    '/dashboard/:path*',       // 匹配 /dashboard 及其子路径
    '/((?!api|_next/static|_next/image|favicon.ico).*)', // 排除特定路径
  ],
}
```

### 常用匹配模式

| 模式 | 说明 |
|------|------|
| `/about` | 精确匹配 |
| `/about/:path*` | 匹配 /about 及其所有子路径 |
| `/about/:id` | 匹配 /about/xxx |
| `/about/(.*)` | 匹配 /about/xxx（正则） |

## 身份验证

### 基本认证

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')
  
  // 未登录用户重定向到登录页
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'],
}
```

### JWT 验证

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtVerify } from 'jose'

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value
  
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  try {
    await jwtVerify(token, new TextEncoder().encode(process.env.JWT_SECRET))
    return NextResponse.next()
  } catch {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}

export const config = {
  matcher: ['/api/:path*', '/dashboard/:path*'],
}
```

## 重定向

### 条件重定向

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // 旧路由重定向
  if (pathname.startsWith('/old-blog')) {
    return NextResponse.redirect(new URL('/blog', request.url))
  }
  
  // 根据语言重定向
  if (pathname.startsWith('/cn')) {
    return NextResponse.rewrite(new URL(pathname.replace('/cn', ''), request.url))
  }
  
  return NextResponse.next()
}
```

### 区域重定向

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const country = request.geo?.country
  
  if (country === 'CN') {
    return NextResponse.redirect(new URL('/cn' + request.nextUrl.pathname, request.url))
  }
  
  return NextResponse.next()
}
```

## 请求头修改

### 添加请求头

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-custom-header', 'custom-value')
  
  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  })
}
```

### 添加响应头

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const response = NextResponse.next()
  
  response.headers.set('x-custom-response-header', 'response-value')
  response.headers.set('X-Frame-Options', 'DENY')
  
  return response
}
```

## 路径重写

### 基本重写

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // 将 /blog/:slug 重写为 /api/blog/:slug
  if (pathname.startsWith('/blog')) {
    return NextResponse.rewrite(new URL(`/api${pathname}`, request.url))
  }
  
  return NextResponse.next()
}
```

### 多语言支持

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // 检查是否已有语言前缀
  const hasLocale = /^\/(en|zh|ja)/.test(pathname)
  
  if (!hasLocale) {
    const locale = request.headers.get('accept-language')?.startsWith('zh') ? 'zh' : 'en'
    return NextResponse.redirect(new URL(`/${locale}${pathname}`, request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

## 日志记录

### 请求日志

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const start = Date.now()
  
  const response = NextResponse.next()
  
  const duration = Date.now() - start
  
  console.log(`${request.method} ${request.nextUrl.pathname} - ${duration}ms`)
  
  response.headers.set('x-response-time', `${duration}ms`)
  
  return response
}
```

### 错误日志

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  try {
    // 中间件逻辑
    return NextResponse.next()
  } catch (error) {
    console.error('中间件错误:', error)
    return NextResponse.json(
      { error: '服务器内部错误' },
      { status: 500 }
    )
  }
}
```

## 限流

### 基本限流

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const rateLimit = new Map<string, { count: number; resetTime: number }>()

export function middleware(request: NextRequest) {
  const ip = request.ip || 'unknown'
  const now = Date.now()
  const limit = rateLimit.get(ip)
  
  if (limit) {
    if (now > limit.resetTime) {
      rateLimit.set(ip, { count: 1, resetTime: now + 60000 })
    } else if (limit.count >= 100) {
      return NextResponse.json(
        { error: '请求过于频繁' },
        { status: 429 }
      )
    } else {
      limit.count++
    }
  } else {
    rateLimit.set(ip, { count: 1, resetTime: now + 60000 })
  }
  
  return NextResponse.next()
}
```

## CORS 处理

### 跨域配置

```typescript [middleware.ts]
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  if (request.method === 'OPTIONS') {
    const response = new NextResponse(null, { status: 200 })
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response
  }
  
  const response = NextResponse.next()
  response.headers.set('Access-Control-Allow-Origin', '*')
  
  return response
}

export const config = {
  matcher: '/api/:path*',
}
```

## 最佳实践

### 1. 精简中间件逻辑

::: tip
中间件应该在最短时间内完成，避免复杂计算和长时间操作。
:::

### 2. 合理配置 matcher

```typescript
// 好：精确匹配
export const config = {
  matcher: ['/api/:path*', '/dashboard/:path*'],
}

// 不好：匹配所有路径
export const config = {
  matcher: '/:path*',
}
```

### 3. 错误处理

```typescript
export async function middleware(request: NextRequest) {
  try {
    return NextResponse.next()
  } catch (error) {
    console.error('Middleware error:', error)
    return NextResponse.json({ error: 'Internal error' }, { status: 500 })
  }
}
```

