# Next 路由系统

Next.js 采用基于文件系统的路由机制，App Router 基于 React Server Components 提供了更强大的路由能力。

## 路由基础

### 文件路由约定

在 App Router 中，`app/` 目录下的文件结构直接映射为路由：

```text
app/
├── page.tsx              → /
├── about/
│   └── page.tsx          → /about
├── blog/
│   ├── page.tsx          → /blog
│   └── first-post/
│       └── page.tsx      → /blog/first-post
```

### 路由类型

| 类型 | 目录结构 | 路由路径 |
|------|----------|----------|
| 静态路由 | `app/about/page.tsx` | `/about` |
| 动态路由 | `app/blog/[slug]/page.tsx` | `/blog/:slug` |
| 捕获所有 | `app/docs/[...slug]/page.tsx` | `/docs/*` |
| 可选捕获 | `app/docs/[[...slug]]/page.tsx` | `/docs` 或 `/docs/*` |

## 动态路由

### 单个参数

```text
app/
└── users/
    └── [id]/
        └── page.tsx
```

```tsx [app/users/[id]/page.tsx]
interface Props {
  params: Promise<{ id: string }>
}

export default async function UserPage({ params }: Props) {
  const { id } = await params
  
  return (
    <div>
      <h1>用户 ID: {id}</h1>
    </div>
  )
}
```

### 多个参数

```text
app/
└── users/
    └── [userId]/
        └── posts/
            └── [postId]/
                └── page.tsx
```

```tsx [app/users/[userId]/posts/[postId]/page.tsx]
interface Props {
  params: Promise<{ userId: string; postId: string }>
}

export default async function UserPostPage({ params }: Props) {
  const { userId, postId } = await params
  
  return (
    <div>
      <h1>用户 {userId} 的文章 {postId}</h1>
    </div>
  )
}
```

### 生成静态参数

```tsx [app/users/[id]/page.tsx]
export async function generateStaticParams() {
  const users = await fetch('https://api.example.com/users').then(res => res.json())
  
  return users.map((user: { id: string }) => ({
    id: user.id,
  }))
}

export default function UserPage({ params }: { params: { id: string } }) {
  return <div>用户: {params.id}</div>
}
```

## 捕获所有路由

### 基本用法

```text
app/
└── docs/
    └── [...slug]/
        └── page.tsx
```

```tsx [app/docs/[...slug]/page.tsx]
interface Props {
  params: Promise<{ slug: string[] }>
}

export default async function DocsPage({ params }: Props) {
  const { slug } = await params
  
  return (
    <div>
      <h1>文档路径: {slug.join('/')}</h1>
    </div>
  )
}
```

### 可选捕获所有

```text
app/
└── docs/
    └── [[...slug]]/
        └── page.tsx
```

```tsx [app/docs/[[...slug]]/page.tsx]
interface Props {
  params: Promise<{ slug?: string[] }>
}

export default async function DocsPage({ params }: Props) {
  const { slug } = await params
  
  if (!slug || slug.length === 0) {
    return <h1>文档首页</h1>
  }
  
  return <h1>文档: {slug.join('/')}</h1>
}
```

## 路由组

### 组织路由

路由组使用括号命名，不会影响 URL 路径：

```text
app/
├── (marketing)/
│   ├── layout.tsx
│   ├── page.tsx              → /
│   └── about/
│       └── page.tsx          → /about
└── (shop)/
    ├── layout.tsx
    └── products/
        └── page.tsx          → /products
```

### 条件布局

```text
app/
├── (auth)/
│   ├── layout.tsx           # 无导航布局
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
└── (dashboard)/
    ├── layout.tsx           # 带侧边栏布局
    └── dashboard/
        └── page.tsx
```

## 并行路由

### 基本用法

```text
app/
├── page.tsx
├── @analytics/
│   └── page.tsx
└── @team/
    └── page.tsx
```

```tsx [app/layout.tsx]
export default function RootLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <html>
      <body>
        {children}
        {analytics}
        {team}
      </body>
    </html>
  )
}
```

### 条件渲染

```tsx [app/layout.tsx]
export default function RootLayout({
  children,
  sidebar,
}: {
  children: React.ReactNode
  sidebar: React.ReactNode
}) {
  const isLoggedIn = checkAuth()
  
  return (
    <div>
      {isLoggedIn ? sidebar : null}
      {children}
    </div>
  )
}
```

## 拦截路由

### 基本用法

拦截路由使用 `(..) `语法，用于模态框等场景：

```text
app/
├── @modal/
│   └── (.)photo/
│       └── [id]/
│           └── page.tsx
├── photo/
│   └── [id]/
│       └── page.tsx
└── layout.tsx
```

```tsx [app/@modal/(.)photo/[id]/page.tsx]
export default function PhotoModal({
  params,
}: {
  params: { id: string }
}) {
  return (
    <div className="modal">
      <h2>照片详情 (模态框)</h2>
      <p>ID: {params.id}</p>
    </div>
  )
}
```

### 拦截级别

| 语法 | 说明 |
|------|------|
| `(.)` | 同级拦截 |
| `(..)` | 上一级拦截 |
| `(..)(..)` | 上两级拦截 |
| (...) | 根目录拦截 |

## 路由导航

### Link 组件

```tsx [components/Navigation.tsx]
import Link from 'next/link'

export default function Navigation() {
  return (
    <nav>
      <Link href="/">首页</Link>
      <Link href="/about">关于</Link>
      <Link href="/blog">博客</Link>
      
      {/* 动态路由 */}
      <Link href={`/users/${userId}`}>用户</Link>
      
      {/* 带查询参数 */}
      <Link href="/search?q=nextjs">搜索</Link>
      
      {/* 替换当前历史 */}
      <Link href="/login" replace>登录</Link>
      
      {/* 预取禁用 */}
      <Link href="/heavy" prefetch={false}>重页面</Link>
    </nav>
  )
}
```

### useRouter Hook

```tsx [app/dashboard/page.tsx]
'use client'

import { useRouter } from 'next/navigation'

export default function Dashboard() {
  const router = useRouter()
  
  const handleNavigate = () => {
    router.push('/settings')
  }
  
  const handleReplace = () => {
    router.replace('/home')
  }
  
  const handleBack = () => {
    router.back()
  }
  
  const handleForward = () => {
    router.forward()
  }
  
  const handleRefresh = () => {
    router.refresh()
  }
  
  return (
    <div>
      <button onClick={handleNavigate}>跳转</button>
      <button onClick={handleReplace}>替换</button>
      <button onClick={handleBack}>返回</button>
      <button onClick={handleForward}>前进</button>
      <button onClick={handleRefresh}>刷新</button>
    </div>
  )
}
```

### redirect 函数

```tsx [app/admin/page.tsx]
import { redirect } from 'next/navigation'

export default function AdminPage() {
  const isAdmin = checkAdmin()
  
  if (!isAdmin) {
    redirect('/login')
  }
  
  return <div>管理后台</div>
}
```

## 路由匹配优先级

```text
app/
├── about/
│   └── page.tsx           # 1. 静态路由（最高优先级）
├── [slug]/
│   └── page.tsx           # 2. 动态路由
└── [...catchAll]/
    └── page.tsx           # 3. 捕获所有路由（最低优先级）
```

## 最佳实践

### 1. 路由分组

::: tip
使用路由组 `(group)` 来组织不同功能模块的路由，保持目录结构清晰。
:::

### 2. 动态路由参数

```tsx
// 好的做法：明确参数类型
interface Props {
  params: Promise<{ id: string }>
}

// 避免：不明确的参数
const { id } = await params
```

### 3. 预取优化

```tsx
// 视口内的链接自动预取
<Link href="/about">关于</Link>

// 禁用不必要的预取
<Link href="/heavy" prefetch={false}>重页面</Link>
```
