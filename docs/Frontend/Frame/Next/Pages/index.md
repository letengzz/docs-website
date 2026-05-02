# Next 页面管理

Next.js 的页面系统基于文件路由，每个 `page.tsx` 文件对应一个路由。

## 页面基础

### 创建页面

```tsx [app/page.tsx]
export default function HomePage() {
  return (
    <main>
      <h1>首页</h1>
      <p>欢迎来到 Next.js 应用</p>
    </main>
  )
}
```

### 页面元数据

```tsx [app/about/page.tsx]
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '关于我们',
  description: '了解我们的团队和使命',
  keywords: ['团队', '公司', '介绍'],
  openGraph: {
    title: '关于我们',
    description: '了解我们的团队和使命',
    images: ['/og-image.jpg'],
  },
}

export default function AboutPage() {
  return <h1>关于我们</h1>
}
```

### 动态元数据

```tsx [app/blog/[slug]/page.tsx]
import type { Metadata, ResolvingMetadata } from 'next'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateMetadata(
  { params }: Props,
  parent: ResolvingMetadata
): Promise<Metadata> {
  const { slug } = await params
  const post = await fetchPost(slug)
  
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      images: [post.coverImage],
    },
  }
}

export default async function PostPage({ params }: Props) {
  const { slug } = await params
  const post = await fetchPost(slug)
  
  return <article>{post.content}</article>
}
```

## 页面渲染模式

### 静态生成（默认）

```tsx [app/blog/page.tsx]
// 构建时静态生成
export default async function BlogPage() {
  const posts = await fetchPosts()
  
  return (
    <div>
      {posts.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </div>
  )
}
```

### 服务端渲染

```tsx [app/dashboard/page.tsx]
// 每次请求时渲染
export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  const data = await fetchDashboardData()
  
  return (
    <div>
      <h1>仪表盘</h1>
      <p>实时数据: {data.value}</p>
    </div>
  )
}
```

### 增量静态再生

```tsx [app/products/[id]/page.tsx]
// 每 60 秒重新生成
export const revalidate = 60

export default async function ProductPage({
  params,
}: {
  params: { id: string }
}) {
  const product = await fetchProduct(params.id)
  
  return (
    <div>
      <h1>{product.name}</h1>
      <p>价格: {product.price}</p>
    </div>
  )
}
```

## 页面配置

### 动态配置

```tsx [app/products/[id]/page.tsx]
export const dynamic = 'force-dynamic'
export const dynamicParams = true
export const revalidate = 60
export const fetchCache = 'default-no-store'

export default function ProductPage() {
  return <div>产品详情</div>
}
```

### 配置选项

| 选项 | 值 | 说明 |
|------|-----|------|
| `dynamic` | `'auto'` / `'force-dynamic'` / `'force-static'` / `'error'` | 渲染模式 |
| `dynamicParams` | `true` / `false` | 是否允许未知参数 |
| `revalidate` | `number` / `false` | 重新验证时间（秒） |
| `fetchCache` | 多种选项 | 缓存策略 |

## 页面导航

### 客户端导航

```tsx [app/products/page.tsx]
'use client'

import { useSearchParams } from 'next/navigation'

export default function ProductsPage() {
  const searchParams = useSearchParams()
  const category = searchParams.get('category')
  
  return (
    <div>
      <h1>产品列表</h1>
      <p>分类: {category || '全部'}</p>
    </div>
  )
}
```

### 服务端获取参数

```tsx [app/products/page.tsx]
interface Props {
  searchParams: Promise<{ category?: string }>
}

export default async function ProductsPage({ searchParams }: Props) {
  const { category } = await searchParams
  
  return (
    <div>
      <h1>产品列表</h1>
      <p>分类: {category || '全部'}</p>
    </div>
  )
}
```

## 页面模板

### template.tsx

与 `layout.tsx` 不同，`template.tsx` 在导航时会重新挂载：

```tsx [app/template.tsx]
'use client'

import { useEffect } from 'react'

export default function Template({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    // 每次导航都执行
    console.log('页面切换')
  }, [])
  
  return <>{children}</>
}
```

## 404 页面

### 自定义 404

```tsx [app/not-found.tsx]
import Link from 'next/link'

export default function NotFound() {
  return (
    <div>
      <h1>404 - 页面未找到</h1>
      <p>抱歉，您访问的页面不存在</p>
      <Link href="/">返回首页</Link>
    </div>
  )
}
```

### 触发 404

```tsx [app/users/[id]/page.tsx]
import { notFound } from 'next/navigation'

export default async function UserPage({
  params,
}: {
  params: { id: string }
}) {
  const user = await fetchUser(params.id)
  
  if (!user) {
    notFound()
  }
  
  return <div>{user.name}</div>
}
```

## 错误页面

### 全局错误处理

```tsx [app/error.tsx]
'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('页面错误:', error)
  }, [error])
  
  return (
    <div>
      <h2>出错了!</h2>
      <p>{error.message}</p>
      <button onClick={() => reset()}>重试</button>
    </div>
  )
}
```

### 路由级错误处理

```tsx [app/dashboard/error.tsx]
'use client'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>仪表盘加载失败</h2>
      <button onClick={reset}>重新加载</button>
    </div>
  )
}
```

## 页面重定向

### 服务端重定向

```tsx [app/old-page/page.tsx]
import { redirect } from 'next/navigation'

export default function OldPage() {
  redirect('/new-page')
}
```

### 条件重定向

```tsx [app/admin/page.tsx]
import { redirect } from 'next/navigation'

export default async function AdminPage() {
  const user = await getCurrentUser()
  
  if (!user) {
    redirect('/login')
  }
  
  if (user.role !== 'admin') {
    redirect('/unauthorized')
  }
  
  return <div>管理后台</div>
}
```

## 页面预取

### 自动预取

Next.js 会自动预取视口内的链接：

```tsx
// 自动预取
<Link href="/about">关于</Link>

// 禁用预取
<Link href="/about" prefetch={false}>关于</Link>

// 条件预取
<Link href="/about" prefetch={isVisible}>关于</Link>
```

### 编程式预取

```tsx
'use client'

import { useRouter } from 'next/navigation'

export default function Page() {
  const router = useRouter()
  
  const prefetchPage = () => {
    router.prefetch('/about')
  }
  
  return (
    <button onMouseEnter={prefetchPage}>
      悬停预取
    </button>
  )
}
```

## 最佳实践

### 1. 元数据优化

::: tip
每个页面都应该设置完整的元数据，包括 title、description 和 Open Graph 信息。
:::

### 2. 错误边界

```tsx
// 在关键路由设置错误边界
app/
├── dashboard/
│   ├── page.tsx
│   └── error.tsx
└── settings/
    ├── page.tsx
    └── error.tsx
```

### 3. 加载状态

```tsx
// 为慢路由添加加载状态
app/
├── dashboard/
│   ├── page.tsx
│   └── loading.tsx
```

