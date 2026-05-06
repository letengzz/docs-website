# React 服务端组件

React Server Components（RSC）是 React 19 中正式稳定的特性，允许组件在服务端渲染，减少客户端 JavaScript 体积，提升首屏加载性能。

## 服务端组件 vs 客户端组件

| 特性 | 服务端组件 | 客户端组件 |
|------|------------|------------|
| 运行位置 | 服务端 | 浏览器 |
| 文件后缀 | `.server.jsx` 或默认 | `.client.jsx` |
| 可使用 Hooks | ❌ | ✅ |
| 可使用 State | ❌ | ✅ |
| 可访问浏览器 API | ❌ | ✅ |
| 可访问文件系统 | ✅ | ❌ |
| 可访问数据库 | ✅ | ❌ |
| 客户端 JS 体积 | 0KB | 包含组件代码 |

## 创建服务端组件

```tsx [app/components/UserProfile.server.tsx]
import { db } from '@/lib/db'

async function UserProfile({ userId }: { userId: string }) {
  const user = await db.users.findUnique({ where: { id: userId } })

  return (
    <div className="user-profile">
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <p>注册时间：{user.createdAt.toLocaleDateString()}</p>
    </div>
  )
}

export default UserProfile
```

## 创建客户端组件

```tsx [app/components/Counter.client.tsx]
'use client'

import { useState } from 'react'

function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <p>计数：{count}</p>
      <button onClick={() => setCount(c => c + 1)}>+1</button>
    </div>
  )
}

export default Counter
```

::: tip 提示
在文件顶部添加 `'use client'` 指令将组件标记为客户端组件。没有该指令的组件默认是服务端组件。
:::

## 服务端组件的优势

### 1. 零客户端 JavaScript

服务端组件不会打包到客户端 JS 中：

```tsx [app/components/HeavyChart.server.tsx]
import { getChartData } from '@/lib/data'

async function HeavyChart() {
  const data = await getChartData()

  return (
    <div className="chart">
      {data.map(item => (
        <div key={item.id} style={{ height: `${item.value}px` }} />
      ))}
    </div>
  )
}

export default HeavyChart
```

### 2. 直接访问后端资源

```tsx [app/components/ProductList.server.tsx]
import { db } from '@/lib/db'
import { cache } from '@/lib/cache'

async function ProductList({ category }: { category: string }) {
  const products = await cache.get(
    `products:${category}`,
    () => db.products.findMany({ where: { category } })
  )

  return (
    <ul>
      {products.map(product => (
        <li key={product.id}>
          <h3>{product.name}</h3>
          <p>¥{product.price}</p>
        </li>
      ))}
    </ul>
  )
}

export default ProductList
```

### 3. 流式渲染

```tsx [app/page.tsx]
import { Suspense } from 'react'
import ProductList from './components/ProductList.server'
import Reviews from './components/Reviews.server'

export default function ProductPage({ params }: { params: { id: string } }) {
  return (
    <div>
      <Suspense fallback={<div>加载产品信息...</div>}>
        <ProductList id={params.id} />
      </Suspense>

      <Suspense fallback={<div>加载评论...</div>}>
        <Reviews productId={params.id} />
      </Suspense>
    </div>
  )
}
```

## 服务端与客户端组件组合

```tsx [app/page.tsx]
import UserProfile from './components/UserProfile.server'
import Counter from './components/Counter.client'

export default function Page() {
  return (
    <div>
      <UserProfile userId="123" />
      <Counter />
    </div>
  )
}
```

### 将客户端组件作为 children 传递

```tsx [app/components/Layout.server.tsx]
import { db } from '@/lib/db'

async function Layout({ children }: { children: React.ReactNode }) {
  const siteConfig = await db.config.findFirst()

  return (
    <div className="layout">
      <header>{siteConfig.siteName}</header>
      <main>{children}</main>
    </div>
  )
}

export default Layout
```

```tsx [app/page.tsx]
import Layout from './components/Layout.server'
import Counter from './components/Counter.client'

export default function Page() {
  return (
    <Layout>
      <Counter />
    </Layout>
  )
}
```

## 数据获取模式

### 服务端数据获取

```tsx [app/components/RecentPosts.server.tsx]
import { db } from '@/lib/db'

async function RecentPosts({ limit = 5 }: { limit?: number }) {
  const posts = await db.posts.findMany({
    take: limit,
    orderBy: { createdAt: 'desc' }
  })

  return (
    <section>
      <h2>最新文章</h2>
      <ul>
        {posts.map(post => (
          <li key={post.id}>
            <a href={`/posts/${post.id}`}>{post.title}</a>
          </li>
        ))}
      </ul>
    </section>
  )
}

export default RecentPosts
```

### 并行数据获取

```tsx [app/page.tsx]
import { Suspense } from 'react'
import { getStats, getRecentUsers, getRecentPosts } from '@/lib/data'

async function Stats() {
  const stats = await getStats()
  return <div>用户数：{stats.userCount}，文章数：{stats.postCount}</div>
}

async function RecentUsers() {
  const users = await getRecentUsers()
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>
}

async function RecentPosts() {
  const posts = await getRecentPosts()
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>
}

export default function Dashboard() {
  return (
    <div>
      <Suspense fallback={<div>加载统计...</div>}>
        <Stats />
      </Suspense>

      <Suspense fallback={<div>加载用户...</div>}>
        <RecentUsers />
      </Suspense>

      <Suspense fallback={<div>加载文章...</div>}>
        <RecentPosts />
      </Suspense>
    </div>
  )
}
```

## 服务端 Actions

React 19 引入了 Server Actions，允许在服务端定义函数并在客户端调用：

```tsx [app/actions.ts]
'use server'

import { db } from '@/lib/db'
import { revalidatePath } from 'next/cache'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  await db.posts.create({ data: { title, content } })
  revalidatePath('/posts')
}

export async function deletePost(id: string) {
  await db.posts.delete({ where: { id } })
  revalidatePath('/posts')
}
```

```tsx [app/components/CreatePostForm.tsx]
'use client'

import { createPost } from '@/app/actions'
import { useFormStatus } from 'react-dom'

function SubmitButton() {
  const { pending } = useFormStatus()
  return <button disabled={pending}>{pending ? '发布中...' : '发布'}</button>
}

export default function CreatePostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="标题" required />
      <textarea name="content" placeholder="内容" required />
      <SubmitButton />
    </form>
  )
}
```

## 错误处理

```tsx [app/error.tsx]
'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div>
      <h2>出错了！</h2>
      <button onClick={() => reset()}>重试</button>
    </div>
  )
}
```

## 缓存策略

```tsx [app/components/CachedData.server.tsx]
import { cache } from '@/lib/cache'

async function CachedData() {
  const data = await cache.get(
    'my-data',
    async () => {
      const res = await fetch('https://api.example.com/data')
      return res.json()
    },
    { ttl: 60 * 5 }
  )

  return <div>{JSON.stringify(data)}</div>
}

export default CachedData
```

## 注意事项

::: danger 注意
- 服务端组件不能使用 Hooks（useState、useEffect 等）
- 服务端组件不能使用浏览器 API（window、document 等）
- 服务端组件不能添加事件监听器（onClick、onChange 等）
- 客户端组件不能直接导入服务端组件作为子组件
:::

## 适用场景

| 场景 | 推荐组件类型 |
|------|--------------|
| 数据获取 | 服务端组件 |
| 访问后端资源 | 服务端组件 |
| 隐藏敏感信息 | 服务端组件 |
| 减少客户端 JS | 服务端组件 |
| 交互性（点击、输入） | 客户端组件 |
| 使用 Hooks | 客户端组件 |
| 使用浏览器 API | 客户端组件 |
| 状态管理 | 客户端组件 |
