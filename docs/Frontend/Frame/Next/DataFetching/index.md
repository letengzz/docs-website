# Next 数据获取

Next.js 提供了多种数据获取方式，支持服务端和客户端两种场景。

## Server Components 数据获取

### 基本用法

在 Server Components 中直接使用 async/await：

```tsx [app/users/page.tsx]
async function fetchUsers() {
  const res = await fetch('https://api.example.com/users')
  return res.json()
}

export default async function UsersPage() {
  const users = await fetchUsers()
  
  return (
    <div>
      <h1>用户列表</h1>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  )
}
```

### 并行数据获取

```tsx [app/dashboard/page.tsx]
export default async function DashboardPage() {
  const [users, posts, stats] = await Promise.all([
    fetch('https://api.example.com/users').then(res => res.json()),
    fetch('https://api.example.com/posts').then(res => res.json()),
    fetch('https://api.example.com/stats').then(res => res.json()),
  ])
  
  return (
    <div>
      <h1>仪表盘</h1>
      <p>用户: {users.length}</p>
      <p>文章: {posts.length}</p>
      <p>统计: {stats.total}</p>
    </div>
  )
}
```

### 串行数据获取

```tsx [app/blog/[slug]/page.tsx]
export default async function PostPage({
  params,
}: {
  params: { slug: string }
}) {
  const post = await fetch(`https://api.example.com/posts/${params.slug}`).then(res => res.json())
  const author = await fetch(`https://api.example.com/users/${post.authorId}`).then(res => res.json())
  const comments = await fetch(`https://api.example.com/posts/${post.id}/comments`).then(res => res.json())
  
  return (
    <article>
      <h1>{post.title}</h1>
      <p>作者: {author.name}</p>
      <div>{post.content}</div>
      <section>
        <h2>评论</h2>
        {comments.map(comment => (
          <div key={comment.id}>{comment.content}</div>
        ))}
      </section>
    </article>
  )
}
```

## Fetch 缓存

### 缓存策略

```tsx
// 默认缓存（静态生成）
fetch('https://api.example.com/data')

// 不缓存（每次请求）
fetch('https://api.example.com/data', { cache: 'no-store' })

// 强制缓存（即使有 no-store）
fetch('https://api.example.com/data', { cache: 'force-cache' })

// 重新验证（ISR）
fetch('https://api.example.com/data', { next: { revalidate: 60 } })
```

### 标签重新验证

```tsx [app/products/page.tsx]
export default async function ProductsPage() {
  const products = await fetch('https://api.example.com/products', {
    next: { tags: ['products'] },
  })
  
  return (
    <div>
      {products.map(product => (
        <div key={product.id}>{product.name}</div>
      ))}
    </div>
  )
}
```

重新验证：

```tsx [app/revalidate/route.ts]
import { revalidateTag } from 'next/cache'

export async function POST() {
  revalidateTag('products')
  return Response.json({ revalidated: true })
}
```

## 路由段缓存配置

### 页面级配置

```tsx [app/products/page.tsx]
// 强制动态渲染
export const dynamic = 'force-dynamic'

// 强制静态生成
export const dynamic = 'force-static'

// 设置重新验证时间
export const revalidate = 60
```

### 配置选项

| 选项 | 值 | 说明 |
|------|-----|------|
| `dynamic` | `'auto'` / `'force-dynamic'` / `'force-static'` | 渲染模式 |
| `revalidate` | `number` / `false` | 重新验证时间（秒） |
| `fetchCache` | 多种选项 | 缓存策略 |

## 客户端数据获取

### 使用 useEffect

```tsx [app/components/UserList.tsx]
'use client'

import { useState, useEffect } from 'react'

export default function UserList() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetch('https://api.example.com/users')
      .then(res => res.json())
      .then(data => {
        setUsers(data)
        setLoading(false)
      })
  }, [])
  
  if (loading) return <p>加载中...</p>
  
  return (
    <div>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  )
}
```

### 使用 SWR

```bash [终端]
npm install swr
```

```tsx [app/components/UserList.tsx]
'use client'

import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function UserList() {
  const { data, error, isLoading } = useSWR('/api/users', fetcher)
  
  if (isLoading) return <p>加载中...</p>
  if (error) return <p>加载失败</p>
  
  return (
    <div>
      {data.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  )
}
```

### 使用 TanStack Query

```bash [终端]
npm install @tanstack/react-query
```

```tsx [app/providers.tsx]
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

```tsx [app/components/UserList.tsx]
'use client'

import { useQuery } from '@tanstack/react-query'

export default function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(res => res.json()),
  })
  
  if (isLoading) return <p>加载中...</p>
  if (error) return <p>加载失败</p>
  
  return (
    <div>
      {data.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  )
}
```

## 服务端 Actions

### 基本用法

```tsx [app/actions.ts]
'use server'

export async function createUser(formData: FormData) {
  const name = formData.get('name')
  const email = formData.get('email')
  
  await fetch('https://api.example.com/users', {
    method: 'POST',
    body: JSON.stringify({ name, email }),
  })
  
  return { success: true }
}
```

```tsx [app/components/CreateUserForm.tsx]
'use client'

import { createUser } from '@/app/actions'

export default function CreateUserForm() {
  const handleSubmit = async (formData: FormData) => {
    const result = await createUser(formData)
    if (result.success) {
      alert('创建成功')
    }
  }
  
  return (
    <form action={handleSubmit}>
      <input name="name" placeholder="姓名" />
      <input name="email" placeholder="邮箱" />
      <button type="submit">创建</button>
    </form>
  )
}
```

### 表单处理

```tsx [app/components/UserForm.tsx]
'use client'

import { useFormStatus } from 'react-dom'
import { updateUser } from '@/app/actions'

function SubmitButton() {
  const { pending } = useFormStatus()
  
  return (
    <button type="submit" disabled={pending}>
      {pending ? '提交中...' : '提交'}
    </button>
  )
}

export default function UserForm({ user }: { user: User }) {
  const updateUserWithId = updateUser.bind(null, user.id)
  
  return (
    <form action={updateUserWithId}>
      <input name="name" defaultValue={user.name} />
      <input name="email" defaultValue={user.email} />
      <SubmitButton />
    </form>
  )
}
```

## 数据获取模式对比

| 模式 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| Server Components | 初始数据加载 | 性能好、SEO 友好 | 无法交互 |
| useEffect | 简单客户端数据 | 简单易用 | 需要手动处理缓存 |
| SWR | 需要缓存和重新验证 | 自动缓存、焦点重新验证 | 额外依赖 |
| TanStack Query | 复杂状态管理 | 功能强大、开发者工具 | 学习曲线陡峭 |

## 最佳实践

### 1. 优先使用 Server Components

::: tip
在服务端获取数据可以获得更好的性能和 SEO 效果。
:::

### 2. 并行获取数据

```tsx
// 好：并行获取
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
])

// 不好：串行获取
const users = await fetchUsers()
const posts = await fetchPosts()
```

### 3. 错误处理

```tsx [app/error.tsx]
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>数据加载失败</h2>
      <button onClick={reset}>重试</button>
    </div>
  )
}
```

