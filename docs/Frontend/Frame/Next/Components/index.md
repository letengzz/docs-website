# Next 组件开发

Next.js 基于 React 构建，支持 Server Components 和 Client Components 两种组件模式。

## Server Components

### 基本概念

Server Components 是 Next.js App Router 的默认组件类型，在服务端运行：

```tsx [app/components/PostList.tsx]
// 默认就是 Server Component
export default async function PostList() {
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

### 特性

- 可以直接访问数据库和文件系统
- 减少客户端 JavaScript 体积
- 支持 async/await
- 不能使用 Hooks 和事件处理

### 数据获取

```tsx [app/components/UserProfile.tsx]
interface Props {
  userId: string
}

export default async function UserProfile({ userId }: Props) {
  const user = await fetch(`https://api.example.com/users/${userId}`).then(res => res.json())
  
  return (
    <div>
      <img src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.bio}</p>
    </div>
  )
}
```

## Client Components

### 使用场景

需要使用以下功能时，必须使用 Client Components：

- 状态管理（useState、useReducer）
- 生命周期（useEffect）
- 事件处理（onClick、onChange）
- 浏览器 API（window、document）
- 自定义 Hooks

### 声明方式

```tsx [app/components/Counter.tsx]
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
    </div>
  )
}
```

### 事件处理

```tsx [app/components/SearchBox.tsx]
'use client'

import { useState } from 'react'

export default function SearchBox() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    const res = await fetch(`/api/search?q=${query}`)
    const data = await res.json()
    setResults(data)
  }
  
  return (
    <form onSubmit={handleSearch}>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="搜索..."
      />
      <button type="submit">搜索</button>
    </form>
  )
}
```

## 组件组合模式

### Server + Client 组合

```tsx [app/page.tsx]
// Server Component
import ClientCounter from '@/components/Counter'

export default async function HomePage() {
  const data = await fetchData()
  
  return (
    <div>
      <h1>{data.title}</h1>
      <ClientCounter />
    </div>
  )
}
```

### Props 传递

```tsx [app/components/ProductCard.tsx]
// Server Component
import AddToCartButton from '@/components/AddToCartButton'

interface Product {
  id: string
  name: string
  price: number
}

export default function ProductCard({ product }: { product: Product }) {
  return (
    <div>
      <h3>{product.name}</h3>
      <p>¥{product.price}</p>
      <AddToCartButton productId={product.id} />
    </div>
  )
}
```

```tsx [app/components/AddToCartButton.tsx]
'use client'

import { useState } from 'react'

export default function AddToCartButton({ productId }: { productId: string }) {
  const [added, setAdded] = useState(false)
  
  const handleAdd = () => {
    addToCart(productId)
    setAdded(true)
  }
  
  return (
    <button onClick={handleAdd} disabled={added}>
      {added ? '已添加' : '加入购物车'}
    </button>
  )
}
```

## 组件最佳实践

### 1. 优先使用 Server Components

::: tip
默认使用 Server Components，只在需要交互性时才使用 Client Components。
:::

### 2. 组件拆分

```text
components/
├── ui/                 # 基础 UI 组件（Client）
│   ├── Button.tsx
│   └── Input.tsx
├── features/           # 功能组件（混合）
│   ├── SearchBox.tsx
│   └── FilterPanel.tsx
└── layout/             # 布局组件（Server）
    ├── Header.tsx
    └── Footer.tsx
```

### 3. 类型安全

```tsx [app/components/UserCard.tsx]
interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

interface Props {
  user: User
  onEdit?: (user: User) => void
}

export default function UserCard({ user, onEdit }: Props) {
  return (
    <div>
      <img src={user.avatar || '/default-avatar.png'} alt={user.name} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      {onEdit && <button onClick={() => onEdit(user)}>编辑</button>}
    </div>
  )
}
```

## 组件优化

### 1. 避免不必要的 Client Components

```tsx
// 不好：整个组件都是 Client
'use client'
import { useState } from 'react'

export default function BadExample() {
  const [data] = useState(fetchData()) // 服务端数据在客户端获取
  return <div>{data.title}</div>
}

// 好：分离 Server 和 Client
export default async function GoodExample() {
  const data = await fetchData() // 服务端获取
  return <ClientComponent data={data} />
}
```

### 2. 使用 Suspense

```tsx [app/components/SlowComponent.tsx]
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>页面标题</h1>
      <Suspense fallback={<p>加载中...</p>}>
        <SlowComponent />
      </Suspense>
    </div>
  )
}
```

### 3. 错误边界

```tsx [app/components/ErrorBoundary.tsx]
'use client'

import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }
  
  static getDerivedStateFromError(): State {
    return { hasError: true }
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('组件错误:', error, errorInfo)
  }
  
  render() {
    if (this.state.hasError) {
      return this.props.fallback || <h2>出错了</h2>
    }
    
    return this.props.children
  }
}
```

## 组件复用

### 自定义 Hooks

```tsx [hooks/useFetch.ts]
'use client'

import { useState, useEffect } from 'react'

export function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(url)
        const json = await res.json()
        setData(json)
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
  }, [url])
  
  return { data, loading, error }
}
```

### 高阶组件

```tsx [components/withAuth.tsx]
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return function WithAuthComponent(props: P) {
    const router = useRouter()
    
    useEffect(() => {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/login')
      }
    }, [router])
    
    return <WrappedComponent {...props} />
  }
}
```

