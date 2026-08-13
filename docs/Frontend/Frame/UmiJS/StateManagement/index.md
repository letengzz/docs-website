# UmiJS 状态管理

UmiJS 提供了内置的数据流方案，同时也支持其他流行的状态管理库。本指南将介绍在 UmiJS 中管理状态的各种方式。

## UmiJS 内置数据流

UmiJS 内置了基于 Hooks 的简易数据流方案，无需额外安装。

### 启用数据流

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  model: {},
})
```

### 创建 Model

在 `src/models` 目录下创建 model 文件：

```tsx [src/models/user.ts]
import { useState } from 'react'

export default function userModel() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)

  const login = async (username: string, password: string) => {
    setLoading(true)
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = await response.json()
      setUser(data.user)
      return data
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
  }

  const updateProfile = async (profile: any) => {
    const response = await fetch('/api/user/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    })
    const data = await response.json()
    setUser(data.user)
  }

  return {
    user,
    loading,
    login,
    logout,
    updateProfile,
  }
}
```

### 使用 Model

```tsx
import { useModel } from 'umi'

export default function LoginPage() {
  const { user, login, loading } = useModel('user')

  const handleLogin = async () => {
    await login('admin', '123456')
  }

  if (user) {
    return <div>欢迎, {user.name}</div>
  }

  return (
    <div>
      <button onClick={handleLogin} disabled={loading}>
        {loading ? '登录中...' : '登录'}
      </button>
    </div>
  )
}
```

### 多 Model 管理

```text
src/models/
├── user.ts           # 用户状态
├── product.ts        # 产品状态
└── order.ts          # 订单状态
```

```tsx
import { useModel } from 'umi'

export default function Dashboard() {
  const { user } = useModel('user')
  const { products } = useModel('product')
  const { orders } = useModel('order')

  return (
    <div>
      <h2>欢迎, {user?.name}</h2>
      <p>产品数: {products.length}</p>
      <p>订单数: {orders.length}</p>
    </div>
  )
}
```

## 初始状态管理

使用 `@umijs/plugin-initialState` 管理全局初始状态。

### 配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  initialState: {},
})
```

### 定义初始状态

```tsx [src/app.tsx]
import type { InitialState } from 'umi'

export async function getInitialState(): Promise<InitialState> {
  // 获取用户信息
  const user = await fetchUserInfo()
  
  // 获取权限信息
  const permissions = await fetchPermissions()
  
  return {
    user,
    permissions,
    settings: {
      theme: 'light',
      language: 'zh-CN',
    },
  }
}
```

### 使用初始状态

```tsx
import { useModel } from 'umi'

export default function Header() {
  const { initialState, setInitialState } = useModel('@@initialState')

  const { user, settings } = initialState || {}

  const handleLogout = () => {
    setInitialState({
      user: null,
      permissions: [],
      settings,
    })
  }

  return (
    <header>
      {user ? (
        <>
          <span>欢迎, {user.name}</span>
          <button onClick={handleLogout}>退出</button>
        </>
      ) : (
        <a href="/login">登录</a>
      )}
    </header>
  )
}
```

## Redux

### 安装

```bash
npm install redux react-redux @reduxjs/toolkit
```

### 创建 Store

```tsx [src/store/index.ts]
import { configureStore } from '@reduxjs/toolkit'
import userReducer from './userSlice'
import productReducer from './productSlice'

export const store = configureStore({
  reducer: {
    user: userReducer,
    product: productReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

### 创建 Slice

```tsx [src/store/userSlice.ts]
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

interface UserState {
  user: any
  loading: boolean
  error: string | null
}

const initialState: UserState = {
  user: null,
  loading: false,
  error: null,
}

export const login = createAsyncThunk(
  'user/login',
  async ({ username, password }: { username: string; password: string }) => {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    return response.json()
  }
)

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.user = action.payload.user
        state.loading = false
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '登录失败'
      })
  },
})

export const { logout } = userSlice.actions
export default userSlice.reducer
```

### 提供 Store

```tsx [src/app.tsx]
import { Provider } from 'react-redux'
import { store } from './store'

export function rootContainer(container: React.ReactNode) {
  return <Provider store={store}>{container}</Provider>
}
```

### 使用 Redux

```tsx
import { useSelector, useDispatch } from 'react-redux'
import { login, logout } from '@/store/userSlice'
import type { RootState, AppDispatch } from '@/store'

export default function LoginPage() {
  const { user, loading, error } = useSelector((state: RootState) => state.user)
  const dispatch = useDispatch<AppDispatch>()

  const handleLogin = async () => {
    await dispatch(login({ username: 'admin', password: '123456' }))
  }

  const handleLogout = () => {
    dispatch(logout())
  }

  if (user) {
    return (
      <div>
        <p>欢迎, {user.name}</p>
        <button onClick={handleLogout}>退出</button>
      </div>
    )
  }

  return (
    <div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button onClick={handleLogin} disabled={loading}>
        {loading ? '登录中...' : '登录'}
      </button>
    </div>
  )
}
```

## Zustand

### 安装

```bash
npm install zustand
```

### 创建 Store

```tsx [src/store/userStore.ts]
import { create } from 'zustand'

interface UserState {
  user: any
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  loading: false,
  login: async (username: string, password: string) => {
    set({ loading: true })
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = await response.json()
      set({ user: data.user, loading: false })
    } catch (error) {
      set({ loading: false })
      throw error
    }
  },
  logout: () => set({ user: null }),
}))
```

### 使用 Zustand

```tsx
import { useUserStore } from '@/store/userStore'

export default function LoginPage() {
  const { user, loading, login, logout } = useUserStore()

  const handleLogin = async () => {
    await login('admin', '123456')
  }

  if (user) {
    return (
      <div>
        <p>欢迎, {user.name}</p>
        <button onClick={logout}>退出</button>
      </div>
    )
  }

  return (
    <button onClick={handleLogin} disabled={loading}>
      {loading ? '登录中...' : '登录'}
    </button>
  )
}
```

## MobX

### 安装

```bash
npm install mobx mobx-react-lite
```

### 创建 Store

```tsx [src/stores/userStore.ts]
import { makeAutoObservable } from 'mobx'

class UserStore {
  user: any = null
  loading = false

  constructor() {
    makeAutoObservable(this)
  }

  async login(username: string, password: string) {
    this.loading = true
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = await response.json()
      this.user = data.user
    } finally {
      this.loading = false
    }
  }

  logout() {
    this.user = null
  }
}

export const userStore = new UserStore()
```

### 使用 MobX

```tsx
import { observer } from 'mobx-react-lite'
import { userStore } from '@/stores/userStore'

const LoginPage = observer(function LoginPage() {
  const { user, loading, login, logout } = userStore

  const handleLogin = async () => {
    await login('admin', '123456')
  }

  if (user) {
    return (
      <div>
        <p>欢迎, {user.name}</p>
        <button onClick={logout}>退出</button>
      </div>
    )
  }

  return (
    <button onClick={handleLogin} disabled={loading}>
      {loading ? '登录中...' : '登录'}
    </button>
  )
})

export default LoginPage
```

## 状态管理对比

| 方案 | 复杂度 | 性能 | 学习曲线 | 适用场景 |
|------|--------|------|----------|----------|
| UmiJS 数据流 | 低 | 中 | 低 | 简单项目 |
| Redux + Toolkit | 中 | 高 | 中 | 中大型项目 |
| Zustand | 低 | 高 | 低 | 中小型项目 |
| MobX | 中 | 高 | 中 | 复杂状态管理 |

## 选择建议

### 使用 UmiJS 数据流

- 项目规模较小
- 状态管理需求简单
- 不想引入额外依赖

### 使用 Redux

- 项目规模较大
- 需要时间旅行调试
- 团队熟悉 Redux
- 需要完善的生态

### 使用 Zustand

- 追求简洁的 API
- 不想写 boilerplate 代码
- 中小型项目

### 使用 MobX

- 需要响应式编程
- 状态关系复杂
- 喜欢 OOP 风格

## 最佳实践

1. **简单状态**使用组件内部 `useState`
2. **跨组件状态**使用 UmiJS 数据流或 Context
3. **复杂状态**使用 Redux 或 Zustand
4. **避免全局状态** 尽量将状态保持在组件内部
5. **状态规范化** 避免冗余和重复的状态
6. **异步处理** 使用 thunk 或 async/await
7. **类型安全** 使用 TypeScript 定义状态类型

::: tip 提示
- UmiJS 内置数据流适合简单项目
- Redux 是最流行的状态管理方案
- Zustand API 简洁，适合中小型项目
- MobX 提供响应式编程体验
- 根据项目规模选择合适的方案
:::

::: danger 注意事项
- 避免将所有状态都放在全局
- 状态更新应该是不可变的
- 异步操作需要正确处理 loading 和 error 状态
- 使用 Redux 时不要忘记配置 Provider
- MobX 需要使用 observer 包装组件才能响应状态变化
:::
