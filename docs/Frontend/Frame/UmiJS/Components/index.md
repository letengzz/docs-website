# UmiJS 组件开发

UmiJS 基于 React，组件开发与 React 组件开发基本一致。本指南将介绍在 UmiJS 中开发组件的最佳实践。

## 组件基础

### 函数组件

推荐使用函数组件和 Hooks：

```tsx [src/components/Button/index.tsx]
import React from 'react'

interface ButtonProps {
  type?: 'primary' | 'default' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  onClick?: () => void
  children: React.ReactNode
}

export default function Button({
  type = 'default',
  size = 'medium',
  disabled = false,
  onClick,
  children,
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${type} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
```

### 类组件

```tsx
import React, { Component } from 'react'

interface Props {
  title: string
}

interface State {
  count: number
}

export default class Counter extends Component<Props, State> {
  state: State = {
    count: 0,
  }

  increment = () => {
    this.setState({ count: this.state.count + 1 })
  }

  render() {
    return (
      <div>
        <h2>{this.props.title}</h2>
        <p>Count: {this.state.count}</p>
        <button onClick={this.increment}>+1</button>
      </div>
    )
  }
}
```

## 组件样式

### CSS 模块

UmiJS 默认支持 CSS 模块：

```tsx [src/components/Card/index.tsx]
import styles from './index.less'

interface CardProps {
  title: string
  children: React.ReactNode
}

export default function Card({ title, children }: CardProps) {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>{title}</h3>
      <div className={styles.content}>{children}</div>
    </div>
  )
}
```

```less [src/components/Card/index.less]
.card {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 16px;

  .title {
    margin: 0 0 12px;
    font-size: 16px;
    font-weight: 500;
  }

  .content {
    color: #666;
  }
}
```

### 内联样式

```tsx
interface AvatarProps {
  src: string
  size?: number
}

export default function Avatar({ src, size = 40 }: AvatarProps) {
  return (
    <img
      src={src}
      alt="avatar"
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        objectFit: 'cover',
      }}
    />
  )
}
```

### Tailwind CSS / UnoCSS

如果项目配置了原子化 CSS 框架：

```tsx
export default function Card({ title, children }: CardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4 mb-4">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <div className="text-gray-600">{children}</div>
    </div>
  )
}
```

## 组件通信

### Props 传递

父组件向子组件传递数据：

```tsx [src/components/UserList.tsx]
import UserCard from './UserCard'

interface User {
  id: number
  name: string
  email: string
}

interface UserListProps {
  users: User[]
  onUserClick: (user: User) => void
}

export default function UserList({ users, onUserClick }: UserListProps) {
  return (
    <div>
      {users.map((user) => (
        <UserCard key={user.id} user={user} onClick={onUserClick} />
      ))}
    </div>
  )
}
```

### 回调函数

子组件向父组件传递数据：

```tsx [src/components/UserCard.tsx]
interface UserCardProps {
  user: { id: number; name: string; email: string }
  onClick: (user: { id: number; name: string; email: string }) => void
}

export default function UserCard({ user, onClick }: UserCardProps) {
  return (
    <div className="user-card" onClick={() => onClick(user)}>
      <h4>{user.name}</h4>
      <p>{user.email}</p>
    </div>
  )
}
```

### Context

跨组件传递数据：

```tsx [src/contexts/ThemeContext.tsx]
import { createContext, useContext, useState } from 'react'

interface ThemeContextType {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'))
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

```tsx
// 使用 Context
import { useTheme } from '@/contexts/ThemeContext'

export default function Header() {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className={theme === 'dark' ? 'dark' : 'light'}>
      <button onClick={toggleTheme}>切换主题</button>
    </header>
  )
}
```

## 常用 Hooks

### useState

管理组件状态：

```tsx
import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
      <button onClick={() => setCount(count - 1)}>-1</button>
    </div>
  )
}
```

### useEffect

处理副作用：

```tsx
import { useState, useEffect } from 'react'

export default function UserProfile({ userId }: { userId: number }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchUser() {
      setLoading(true)
      try {
        const response = await fetch(`/api/users/${userId}`)
        const data = await response.json()
        setUser(data)
      } catch (error) {
        console.error('Failed to fetch user:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [userId])

  if (loading) return <div>加载中...</div>
  if (!user) return <div>用户不存在</div>

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  )
}
```

### useCallback

缓存回调函数：

```tsx
import { useState, useCallback } from 'react'

export default function SearchBox({ onSearch }: { onSearch: (query: string) => void }) {
  const [query, setQuery] = useState('')

  const handleSearch = useCallback(() => {
    onSearch(query)
  }, [query, onSearch])

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="搜索..."
      />
      <button onClick={handleSearch}>搜索</button>
    </div>
  )
}
```

### useMemo

缓存计算结果：

```tsx
import { useState, useMemo } from 'react'

export default function ProductList({ products }: { products: any[] }) {
  const [filter, setFilter] = useState('')

  const filteredProducts = useMemo(() => {
    return products.filter((p) =>
      p.name.toLowerCase().includes(filter.toLowerCase())
    )
  }, [products, filter])

  return (
    <div>
      <input
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="筛选产品..."
      />
      <ul>
        {filteredProducts.map((p) => (
          <li key={p.id}>{p.name}</li>
        ))}
      </ul>
    </div>
  )
}
```

### useRef

引用 DOM 元素或保存可变值：

```tsx
import { useRef, useEffect } from 'react'

export default function AutoFocusInput() {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  return <input ref={inputRef} placeholder="自动聚焦" />
}
```

## 自定义 Hooks

封装可复用的逻辑：

```tsx [src/hooks/useLocalStorage.ts]
import { useState, useEffect } from 'react'

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch {
      return initialValue
    }
  })

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error('Error saving to localStorage:', error)
    }
  }

  return [storedValue, setValue] as const
}
```

```tsx
// 使用自定义 Hook
import { useLocalStorage } from '@/hooks/useLocalStorage'

export default function Settings() {
  const [theme, setTheme] = useLocalStorage('theme', 'light')

  return (
    <div>
      <p>当前主题: {theme}</p>
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        切换主题
      </button>
    </div>
  )
}
```

## 组件最佳实践

### 组件拆分原则

1. **单一职责**：每个组件只做一件事
2. **可复用性**：提取通用逻辑为独立组件
3. **合理粒度**：不要过度拆分，保持组件内聚

### 命名规范

- 组件文件名使用 PascalCase：`UserProfile.tsx`
- 组件函数名使用 PascalCase：`function UserProfile()`
- 组件目录名使用 PascalCase：`UserProfile/`

### 组件结构

```tsx
import React, { useState, useEffect } from 'react'
import styles from './index.less'

// 类型定义
interface Props {
  title: string
  data: any[]
  onRefresh: () => void
}

// 组件定义
export default function DataList({ title, data, onRefresh }: Props) {
  // Hooks
  const [loading, setLoading] = useState(false)

  // 副作用
  useEffect(() => {
    // 初始化逻辑
  }, [])

  // 事件处理
  const handleRefresh = async () => {
    setLoading(true)
    try {
      await onRefresh()
    } finally {
      setLoading(false)
    }
  }

  // 渲染
  return (
    <div className={styles.container}>
      <h2>{title}</h2>
      <button onClick={handleRefresh} disabled={loading}>
        {loading ? '刷新中...' : '刷新'}
      </button>
      <ul>
        {data.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  )
}
```

### 性能优化

#### React.memo

避免不必要的重渲染：

```tsx
import React from 'react'

const UserCard = React.memo(function UserCard({ user }: { user: any }) {
  return (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  )
})

export default UserCard
```

#### 列表渲染优化

```tsx
export default function UserList({ users }: { users: any[] }) {
  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          {user.name}
        </li>
      ))}
    </ul>
  )
}
```

#### 懒加载组件

```tsx
import { lazy, Suspense } from 'react'

const HeavyComponent = lazy(() => import('@/components/HeavyComponent'))

export default function Page() {
  return (
    <Suspense fallback={<div>加载中...</div>}>
      <HeavyComponent />
    </Suspense>
  )
}
```

## 组件测试

### 单元测试

```tsx [src/components/Button/index.test.tsx]
import { render, screen, fireEvent } from '@testing-library/react'
import Button from './index'

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>)
    expect(screen.getByText('Click me')).toBeDisabled()
  })
})
```

## 组件文档

### 使用 Storybook

```tsx [src/components/Button/Button.stories.tsx]
import type { Meta, StoryObj } from '@storybook/react'
import Button from './index'

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: {
    type: 'primary',
    children: 'Primary Button',
  },
}

export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled Button',
  },
}
```

::: tip 提示
- 优先使用函数组件和 Hooks
- 使用 TypeScript 定义组件类型
- 使用 CSS 模块或原子化 CSS 管理样式
- 合理使用 React.memo 优化性能
- 为组件编写单元测试
:::

::: danger 注意事项
- 避免在渲染函数中创建对象或函数，会导致不必要的重渲染
- 列表渲染时必须提供唯一的 key
- useEffect 的依赖数组要包含所有使用的变量
- 不要在 useEffect 中直接调用 setState，可能导致无限循环
- 组件 props 尽量使用 TypeScript 定义类型
:::
