# UmiJS 路由系统

UmiJS 提供了强大的路由系统，支持约定式路由和配置式路由两种方式，可以满足不同项目的需求。

## 路由方式

### 约定式路由

约定式路由是 UmiJS 的默认路由方式，根据 `src/pages` 目录下的文件结构自动生成路由配置。

#### 基础路由

```text
src/pages/
├── index.tsx       → /
├── about.tsx       → /about
└── users.tsx       → /users
```

#### 目录路由

```text
src/pages/
├── index.tsx           → /
└── users/
    ├── index.tsx       → /users
    └── profile.tsx     → /users/profile
```

#### 动态路由

使用方括号 `[]` 创建动态路由参数：

```text
src/pages/
├── users/
│   └── [id].tsx        → /users/:id
└── posts/
    └── [slug].tsx      → /posts/:slug
```

```tsx [src/pages/users/[id].tsx]
import { useParams } from 'umi'

export default function UserDetail() {
  const { id } = useParams()
  return <div>用户 ID: {id}</div>
}
```

#### 可选参数

使用 `[]` 包裹的参数为必填参数，使用 `$` 前缀创建可选参数：

```text
src/pages/
└── users/
    └── [[id]].tsx      → /users 或 /users/:id
```

#### 嵌套路由

使用 `_layout.tsx` 创建嵌套路由的布局：

```text
src/pages/
└── users/
    ├── _layout.tsx     → /users 的布局
    ├── index.tsx       → /users
    └── [id].tsx        → /users/:id
```

```tsx [src/pages/users/_layout.tsx]
import { Outlet } from 'umi'

export default function UsersLayout() {
  return (
    <div>
      <h2>用户管理</h2>
      <Outlet />
    </div>
  )
}
```

#### 404 页面

创建 `404.tsx` 作为 404 页面：

```tsx [src/pages/404.tsx]
export default function NotFound() {
  return (
    <div>
      <h1>404</h1>
      <p>页面未找到</p>
    </div>
  )
}
```

### 配置式路由

通过配置文件手动定义路由，适合需要精确控制路由的场景。

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  routes: [
    { path: '/', component: 'index' },
    { path: '/about', component: 'about' },
    {
      path: '/users',
      component: 'users/_layout',
      routes: [
        { path: '/users', component: 'users/index' },
        { path: '/users/:id', component: 'users/[id]' },
      ],
    },
    { path: '/*', component: '404' },
  ],
})
```

#### 路由配置项

| 配置项 | 类型 | 说明 |
|--------|------|------|
| path | string | 路由路径 |
| component | string | 组件路径（相对于 pages 目录） |
| routes | array | 子路由配置 |
| redirect | string | 重定向路径 |
| wrappers | array | 路由包装器（权限控制等） |
| title | string | 页面标题 |
| exact | boolean | 是否精确匹配 |

#### 路由重定向

```typescript
export default {
  routes: [
    { path: '/', redirect: '/home' },
    { path: '/home', component: 'home' },
    { path: '/old-path', redirect: '/new-path' },
  ],
}
```

#### 路由权限

使用 `wrappers` 实现路由权限控制：

```typescript
export default {
  routes: [
    {
      path: '/admin',
      component: 'admin',
      wrappers: ['@/wrappers/auth'],
    },
  ],
}
```

```tsx [src/wrappers/auth.tsx]
import { Navigate, Outlet } from 'umi'

export default function AuthWrapper() {
  const isLogin = checkAuth()
  
  if (isLogin) {
    return <Outlet />
  }
  
  return <Navigate to="/login" />
}
```

## 路由跳转

### Link 组件

使用 `Link` 组件进行声明式导航：

```tsx
import { Link } from 'umi'

export default function Navbar() {
  return (
    <nav>
      <Link to="/">首页</Link>
      <Link to="/about">关于</Link>
      <Link to="/users/123">用户详情</Link>
    </nav>
  )
}
```

#### Link 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| to | string | 目标路径 |
| replace | boolean | 是否替换当前历史记录 |
| state | object | 传递的状态数据 |

```tsx
<Link to="/about" replace>关于</Link>

<Link 
  to="/users/123" 
  state={{ from: 'home' }}
>用户详情</Link>
```

### 编程式导航

使用 `history` 对象进行编程式导航：

```tsx
import { history } from 'umi'

export default function HomePage() {
  const goToAbout = () => {
    history.push('/about')
  }

  const goBack = () => {
    history.goBack()
  }

  const replacePage = () => {
    history.replace('/new-path')
  }

  return (
    <div>
      <button onClick={goToAbout}>跳转到关于</button>
      <button onClick={goBack}>返回</button>
      <button onClick={replacePage}>替换页面</button>
    </div>
  )
}
```

#### history 方法

| 方法 | 说明 |
|------|------|
| push(path, state) | 跳转到新页面 |
| replace(path, state) | 替换当前页面 |
| goBack() | 返回上一页 |
| goForward() | 前进到下一页 |
| go(n) | 前进/后退 n 页 |
| location | 当前路由信息 |

```tsx
// 获取当前路由信息
console.log(history.location)
// { pathname: '/users', search: '?id=123', hash: '#section', state: null }

// 带参数跳转
history.push('/search?q=umijs')

// 带状态跳转
history.push('/users', { from: 'home' })
```

## 路由参数

### 路径参数

使用 `useParams` 获取路径参数：

```tsx [src/pages/users/[id].tsx]
import { useParams } from 'umi'

export default function UserDetail() {
  const { id } = useParams()
  return <div>用户 ID: {id}</div>
}
```

### 查询参数

使用 `useSearchParams` 获取查询参数：

```tsx
import { useSearchParams } from 'umi'

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q')
  const page = searchParams.get('page')
  
  return (
    <div>
      <p>搜索关键词: {query}</p>
      <p>页码: {page}</p>
    </div>
  )
}
```

### 路由状态

使用 `useLocation` 获取路由状态：

```tsx
import { useLocation } from 'umi'

export default function UserDetail() {
  const location = useLocation()
  const from = location.state?.from
  
  return (
    <div>
      <p>来自: {from}</p>
    </div>
  )
}
```

## 路由钩子

### useParams

获取动态路由参数：

```tsx
import { useParams } from 'umi'

export default function PostDetail() {
  const { slug } = useParams()
  return <div>文章: {slug}</div>
}
```

### useSearchParams

获取和设置查询参数：

```tsx
import { useSearchParams } from 'umi'

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  
  const updateSearch = (query: string) => {
    setSearchParams({ q: query })
  }
  
  return (
    <div>
      <input 
        value={searchParams.get('q') || ''}
        onChange={(e) => updateSearch(e.target.value)}
      />
    </div>
  )
}
```

### useNavigate

编程式导航钩子：

```tsx
import { useNavigate } from 'umi'

export default function LoginPage() {
  const navigate = useNavigate()
  
  const handleLogin = async () => {
    const success = await login()
    if (success) {
      navigate('/dashboard')
    }
  }
  
  return <button onClick={handleLogin}>登录</button>
}
```

### useLocation

获取当前路由信息：

```tsx
import { useLocation } from 'umi'

export default function PageTracker() {
  const location = useLocation()
  
  useEffect(() => {
    // 页面访问统计
    trackPageView(location.pathname)
  }, [location.pathname])
  
  return null
}
```

## 路由守卫

### 全局路由守卫

在 `src/app.tsx` 中配置全局路由守卫：

```typescript [src/app.tsx]
export function onRouteChange({ location }) {
  // 路由变化时执行
  console.log('路由变化:', location.pathname)
  
  // 设置页面标题
  document.title = getPageTitle(location.pathname)
  
  // 页面访问统计
  trackPageView(location.pathname)
}
```

### 路由级守卫

使用 `wrappers` 实现路由级守卫：

```tsx [src/wrappers/auth.tsx]
import { Navigate, Outlet } from 'umi'

export default function AuthWrapper() {
  const isLogin = checkAuth()
  
  if (isLogin) {
    return <Outlet />
  }
  
  return <Navigate to="/login" replace />
}
```

```typescript [.umirc.ts]
export default {
  routes: [
    {
      path: '/admin',
      component: 'admin',
      wrappers: ['@/wrappers/auth'],
    },
  ],
}
```

## 路由懒加载

UmiJS 默认对路由组件进行代码分割和懒加载：

```tsx
// 路由组件会自动分割为单独的 chunk
// 访问时才会加载对应的代码
```

### 自定义分割

使用 `React.lazy` 手动控制代码分割：

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

## 路由配置示例

### 完整路由配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  routes: [
    {
      path: '/',
      component: '@/layouts/index',
      routes: [
        { path: '/', component: 'index', title: '首页' },
        { path: '/about', component: 'about', title: '关于' },
        {
          path: '/users',
          component: 'users/_layout',
          routes: [
            { path: '/users', component: 'users/index', title: '用户列表' },
            { path: '/users/:id', component: 'users/[id]', title: '用户详情' },
          ],
        },
        {
          path: '/admin',
          component: 'admin/_layout',
          wrappers: ['@/wrappers/auth'],
          routes: [
            { path: '/admin', component: 'admin/index', title: '管理后台' },
            { path: '/admin/users', component: 'admin/users', title: '用户管理' },
          ],
        },
        { path: '/*', component: '404', title: '页面未找到' },
      ],
    },
    { path: '/login', component: 'login', title: '登录' },
  ],
})
```

## 最佳实践

1. **简单项目**使用约定式路由，减少配置
2. **复杂项目**使用配置式路由，精确控制路由
3. **权限控制**使用 `wrappers` 实现路由守卫
4. **页面标题**在路由配置中设置 `title`
5. **404 页面**创建 `404.tsx` 处理未匹配路由
6. **动态参数**使用 `useParams` 获取路径参数
7. **查询参数**使用 `useSearchParams` 获取查询参数
8. **代码分割**利用 UmiJS 默认的懒加载机制

::: tip 提示
- 约定式路由适合快速开发，配置式路由适合精确控制
- 使用 `wrappers` 可以实现权限控制、登录验证等功能
- 路由组件会自动进行代码分割，无需手动配置
- 使用 `history` 对象可以进行编程式导航
:::

::: danger 注意事项
- 约定式路由的文件命名会影响路由路径，注意命名规范
- 动态路由参数使用 `[]` 包裹，如 `[id].tsx`
- 路由守卫的 `wrappers` 组件必须返回 `<Outlet />` 或 `<Navigate />`
- 配置式路由和约定式路由不能同时使用
- 生产环境确保所有路由都有对应的页面组件
:::
