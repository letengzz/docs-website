# React 性能优化

React 默认已经非常高效，但在大型应用中仍需要手动优化。本章介绍从基础到高级的性能优化技术。

## 性能分析工具

### React DevTools Profiler

React DevTools 内置 Profiler 可以测量组件渲染时间：

1. 打开浏览器开发者工具
2. 切换到 Profiler 标签
3. 点击录制按钮开始记录
4. 与应用交互
5. 停止录制查看火焰图

### why-did-you-render

自动检测不必要的重渲染：

```bash [终端]
npm install @welldone-software/why-did-you-render --save-dev
```

```javascript [src/wdyr.js]
import React from 'react'

if (process.env.NODE_ENV === 'development') {
  const whyDidYouRender = require('@welldone-software/why-did-you-render')
  whyDidYouRender(React, {
    trackAllComponents: false,
    trackHooks: true,
    logOnDifferentValues: true
  })
}
```

```typescript [src/main.tsx]
import './wdyr'
import { createRoot } from 'react-dom/client'
import App from './App'

createRoot(document.getElementById('root')!).render(<App />)
```

## 避免不必要的重渲染

### React.memo

包裹组件，在 props 不变时跳过渲染：

```tsx [components/UserCard.tsx]
import { memo } from 'react'

interface UserCardProps {
  name: string
  email: string
  avatar: string
}

const UserCard = memo(function UserCard({ name, email, avatar }: UserCardProps) {
  console.log('UserCard 渲染')
  return (
    <div className="user-card">
      <img src={avatar} alt={name} />
      <h3>{name}</h3>
      <p>{email}</p>
    </div>
  )
})

export default UserCard
```

::: tip 提示
React.memo 只对类组件或函数组件有效，且仅在 props 浅比较相等时跳过渲染。如果 props 包含复杂对象或函数，需要配合 useMemo 和 useCallback 使用。
:::

### 自定义比较函数

```tsx [components/ExpensiveList.tsx]
import { memo } from 'react'

interface ExpensiveListProps {
  items: Item[]
  onItemClick: (id: string) => void
}

const ExpensiveList = memo(
  function ExpensiveList({ items, onItemClick }: ExpensiveListProps) {
    return (
      <ul>
        {items.map(item => (
          <li key={item.id} onClick={() => onItemClick(item.id)}>
            {item.name}
          </li>
        ))}
      </ul>
    )
  },
  (prevProps, nextProps) => {
    return prevProps.items.length === nextProps.items.length &&
      prevProps.items.every((item, i) => item.id === nextProps.items[i].id)
  }
)

export default ExpensiveList
```

### useCallback 缓存函数

```tsx [components/SearchPage.tsx]
import { useState, useCallback } from 'react'
import SearchResults from './SearchResults'

function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  const handleSearch = useCallback(async (searchQuery: string) => {
    const res = await fetch(`/api/search?q=${searchQuery}`)
    const data = await res.json()
    setResults(data)
  }, [])

  return (
    <div>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && handleSearch(query)}
      />
      <SearchResults results={results} onItemSelect={handleSearch} />
    </div>
  )
}

export default SearchPage
```

### useMemo 缓存计算结果

```tsx [components/Dashboard.tsx]
import { useMemo, useState } from 'react'

function Dashboard({ data }: { data: DataItem[] }) {
  const [filter, setFilter] = useState('')

  const filteredData = useMemo(() => {
    console.log('重新计算过滤...')
    return data.filter(item =>
      item.name.toLowerCase().includes(filter.toLowerCase())
    )
  }, [data, filter])

  const total = useMemo(() => {
    console.log('重新计算总和...')
    return filteredData.reduce((sum, item) => sum + item.value, 0)
  }, [filteredData])

  return (
    <div>
      <input value={filter} onChange={e => setFilter(e.target.value)} />
      <p>总计：{total}</p>
      <ul>
        {filteredData.map(item => (
          <li key={item.id}>{item.name}: {item.value}</li>
        ))}
      </ul>
    </div>
  )
}

export default Dashboard
```

## 代码分割

### 路由级分割

```tsx [router/index.tsx]
import { lazy, Suspense } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

const HomePage = lazy(() => import('@/pages/HomePage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      {
        path: 'dashboard',
        element: (
          <Suspense fallback={<DashboardSkeleton />}>
            <DashboardPage />
          </Suspense>
        ),
      },
      {
        path: 'settings',
        element: (
          <Suspense fallback={<SettingsSkeleton />}>
            <SettingsPage />
          </Suspense>
        ),
      },
    ],
  },
])

function App() {
  return <RouterProvider router={router} />
}

export default App
```

### 组件级分割

```tsx [components/HeavyChart.tsx]
import { lazy, Suspense } from 'react'

const ChartLib = lazy(() => import('heavy-chart-lib'))

function HeavyChart({ data }: { data: number[] }) {
  return (
    <Suspense fallback={<div>加载图表...</div>}>
      <ChartLib data={data} />
    </Suspense>
  )
}

export default HeavyChart
```

## 虚拟列表

处理大量数据时，只渲染可视区域内的元素：

```bash [终端]
npm install @tanstack/react-virtual
```

```tsx [components/VirtualList.tsx]
import { useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'

interface VirtualListProps {
  items: string[]
  itemHeight: number
}

function VirtualList({ items, itemHeight }: VirtualListProps) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => itemHeight,
    overscan: 5
  })

  return (
    <div
      ref={parentRef}
      style={{ height: '400px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative'
        }}
      >
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  )
}

export default VirtualList
```

## 并发特性

### useTransition

标记非紧急更新，保持 UI 响应：

```tsx [components/SearchInput.tsx]
import { useState, useTransition } from 'react'

function SearchInput() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [isPending, startTransition] = useTransition()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)

    startTransition(() => {
      const filtered = searchDatabase(value)
      setResults(filtered)
    })
  }

  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending && <div>搜索中...</div>}
      <ul>
        {results.map(result => (
          <li key={result.id}>{result.name}</li>
        ))}
      </ul>
    </div>
  )
}

export default SearchInput
```

### useDeferredValue

延迟更新某个值：

```tsx [components/DeferredList.tsx]
import { useState, useDeferredValue, useMemo } from 'react'

function DeferredList({ items }: { items: string[] }) {
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)

  const filteredItems = useMemo(() => {
    if (!deferredQuery) return items
    return items.filter(item =>
      item.toLowerCase().includes(deferredQuery.toLowerCase())
    )
  }, [items, deferredQuery])

  return (
    <div>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="搜索..."
      />
      <ul>
        {filteredItems.map(item => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  )
}

export default DeferredList
```

## 图片优化

### 懒加载

```tsx [components/LazyImage.tsx]
import { useState, useRef, useEffect } from 'react'

function LazyImage({ src, alt }: { src: string; alt: string }) {
  const [isLoaded, setIsLoaded] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && imgRef.current) {
          imgRef.current.src = src
          observer.disconnect()
        }
      },
      { rootMargin: '200px' }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => observer.disconnect()
  }, [src])

  return (
    <div className="image-wrapper">
      {!isLoaded && <div className="placeholder">加载中...</div>}
      <img
        ref={imgRef}
        alt={alt}
        onLoad={() => setIsLoaded(true)}
        style={{ display: isLoaded ? 'block' : 'none' }}
      />
    </div>
  )
}

export default LazyImage
```

## 状态管理优化

### 选择器优化

```tsx [components/CartCount.tsx]
import { useCartStore } from '@/stores/useCartStore'
import { shallow } from 'zustand/shallow'

function CartCount() {
  const count = useCartStore(state => state.items.length)
  return <span>购物车 ({count})</span>
}

export default CartCount
```

### 状态拆分

```typescript [stores/useUserStore.ts]
import { create } from 'zustand'

interface UserState {
  name: string
  email: string
  setName: (name: string) => void
  setEmail: (email: string) => void
}

export const useUserStore = create<UserState>(set => ({
  name: '',
  email: '',
  setName: name => set({ name }),
  setEmail: email => set({ email })
}))

// 组件只订阅需要的字段
function UserName() {
  const name = useUserStore(state => state.name)
  return <span>{name}</span>
}

function UserEmail() {
  const email = useUserStore(state => state.email)
  return <span>{email}</span>
}
```

## 性能优化清单

| 优化项 | 方法 | 适用场景 |
|--------|------|----------|
| 减少重渲染 | React.memo | 纯展示组件 |
| 缓存函数 | useCallback | 传递给子组件的回调 |
| 缓存计算 | useMemo | 昂贵的计算 |
| 代码分割 | lazy + Suspense | 大型组件、路由 |
| 虚拟列表 | @tanstack/react-virtual | 长列表 |
| 图片懒加载 | IntersectionObserver | 图片列表 |
| 状态选择器 | zustand/shallow | 状态管理 |
| 并发更新 | useTransition | 搜索、过滤 |
| 延迟值 | useDeferredValue | 输入联动 |
