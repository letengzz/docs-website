# Next 状态管理

Next.js 支持多种状态管理方案，从简单的 Context API 到专业的状态管理库。

## React Context

### 基本用法

```tsx [context/ThemeContext.tsx]
'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

interface ThemeContextType {
  theme: string
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light')
  
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
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

### 使用 Context

```tsx [app/layout.tsx]
import { ThemeProvider } from '@/context/ThemeContext'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
```

```tsx [app/components/Header.tsx]
'use client'

import { useTheme } from '@/context/ThemeContext'

export default function Header() {
  const { theme, toggleTheme } = useTheme()
  
  return (
    <header className={theme}>
      <h1>当前主题: {theme}</h1>
      <button onClick={toggleTheme}>切换主题</button>
    </header>
  )
}
```

## Zustand

### 安装

```bash [终端]
npm install zustand
```

### 基本用法

```tsx [store/useStore.ts]
import { create } from 'zustand'

interface User {
  id: string
  name: string
  email: string
}

interface Store {
  user: User | null
  setUser: (user: User) => void
  logout: () => void
}

export const useStore = create<Store>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}))
```

### 使用 Store

```tsx [app/components/UserProfile.tsx]
'use client'

import { useStore } from '@/store/useStore'

export default function UserProfile() {
  const { user, setUser, logout } = useStore()
  
  if (!user) {
    return <button onClick={() => setUser({ id: '1', name: '张三', email: 'test@test.com' })}>登录</button>
  }
  
  return (
    <div>
      <p>姓名: {user.name}</p>
      <p>邮箱: {user.email}</p>
      <button onClick={logout}>退出</button>
    </div>
  )
}
```

### 异步 Actions

```tsx [store/useCartStore.ts]
import { create } from 'zustand'

interface Product {
  id: string
  name: string
  price: number
}

interface CartStore {
  items: Product[]
  loading: boolean
  fetchCart: () => Promise<void>
  addToCart: (product: Product) => Promise<void>
}

export const useCartStore = create<CartStore>((set) => ({
  items: [],
  loading: false,
  
  fetchCart: async () => {
    set({ loading: true })
    const res = await fetch('/api/cart')
    const items = await res.json()
    set({ items, loading: false })
  },
  
  addToCart: async (product) => {
    const res = await fetch('/api/cart', {
      method: 'POST',
      body: JSON.stringify({ product }),
    })
    const items = await res.json()
    set({ items })
  },
}))
```

## Redux Toolkit

### 安装

```bash [终端]
npm install @reduxjs/toolkit react-redux
```

### 创建 Store

```tsx [store/index.ts]
import { configureStore, createSlice, PayloadAction } from '@reduxjs/toolkit'

interface User {
  id: string
  name: string
  email: string
}

interface UserState {
  user: User | null
  loading: boolean
}

const initialState: UserState = {
  user: null,
  loading: false,
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
    },
    logout: (state) => {
      state.user = null
    },
  },
})

export const { setUser, logout } = userSlice.actions

export const store = configureStore({
  reducer: {
    user: userSlice.reducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

### Provider 设置

```tsx [app/providers.tsx]
'use client'

import { Provider } from 'react-redux'
import { store } from '@/store'

export function Providers({ children }: { children: React.ReactNode }) {
  return <Provider store={store}>{children}</Provider>
}
```

### 使用 Redux

```tsx [app/components/UserProfile.tsx]
'use client'

import { useSelector, useDispatch } from 'react-redux'
import { RootState, AppDispatch, setUser, logout } from '@/store'

export default function UserProfile() {
  const user = useSelector((state: RootState) => state.user.user)
  const dispatch = useDispatch<AppDispatch>()
  
  if (!user) {
    return (
      <button onClick={() => dispatch(setUser({ id: '1', name: '张三', email: 'test@test.com' }))}>
        登录
      </button>
    )
  }
  
  return (
    <div>
      <p>姓名: {user.name}</p>
      <p>邮箱: {user.email}</p>
      <button onClick={() => dispatch(logout())}>退出</button>
    </div>
  )
}
```

## Jotai

### 安装

```bash [终端]
npm install jotai
```

### 基本用法

```tsx [store/atoms.ts]
import { atom } from 'jotai'

export const userAtom = atom<{ id: string; name: string } | null>(null)
export const themeAtom = atom<'light' | 'dark'>('light')
export const countAtom = atom(0)
```

```tsx [app/components/Counter.tsx]
'use client'

import { useAtom } from 'jotai'
import { countAtom } from '@/store/atoms'

export default function Counter() {
  const [count, setCount] = useAtom(countAtom)
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(c => c + 1)}>+1</button>
      <button onClick={() => setCount(c => c - 1)}>-1</button>
    </div>
  )
}
```

## 方案对比

| 方案 | 复杂度 | 性能 | 生态 | 适用场景 |
|------|--------|------|------|----------|
| Context | 简单 | 中 | 内置 | 简单全局状态 |
| Zustand | 简单 | 高 | 中 | 中小型项目 |
| Redux Toolkit | 复杂 | 高 | 丰富 | 大型复杂项目 |
| Jotai | 简单 | 高 | 中 | 原子化状态 |

## 最佳实践

### 1. 选择合适的方案

::: tip
简单应用使用 Context 或 Zustand，复杂应用使用 Redux Toolkit。
:::

### 2. 服务端状态与客户端状态分离

```tsx
// 服务端状态（使用 Server Components）
export default async function Page() {
  const data = await fetchData()
  return <ClientComponent initialData={data} />
}

// 客户端状态（使用 Zustand）
'use client'
import { useStore } from '@/store'

export default function ClientComponent({ initialData }: { initialData: Data }) {
  const { setData } = useStore()
  
  useEffect(() => {
    setData(initialData)
  }, [initialData])
  
  return <div>...</div>
}
```

### 3. 持久化状态

```tsx [store/useStore.ts]
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Settings {
  theme: string
  language: string
}

interface SettingsStore {
  settings: Settings
  updateSettings: (settings: Partial<Settings>) => void
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      settings: { theme: 'light', language: 'zh-CN' },
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),
    }),
    { name: 'settings-storage' }
  )
)
```

