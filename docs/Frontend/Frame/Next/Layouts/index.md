# Next 布局系统

Next.js App Router 提供了强大的布局系统，支持嵌套布局、路由组布局等多种布局模式。

## 根布局

### 创建根布局

```tsx [app/layout.tsx]
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'My App',
  description: 'My Next.js Application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>
        <header>网站头部</header>
        <main>{children}</main>
        <footer>网站底部</footer>
      </body>
    </html>
  )
}
```

### 布局特性

- 布局在导航时保持状态
- 布局可以相互嵌套
- 布局默认是 Server Components

## 嵌套布局

### 目录结构

```text
app/
├── layout.tsx           # 根布局
├── page.tsx             # 首页
└── dashboard/
    ├── layout.tsx       # 仪表盘布局
    └── page.tsx         # 仪表盘页面
```

### 根布局

```tsx [app/layout.tsx]
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html>
      <body>
        <nav>全局导航</nav>
        {children}
      </body>
    </html>
  )
}
```

### 子布局

```tsx [app/dashboard/layout.tsx]
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="dashboard">
      <aside>侧边栏</aside>
      <main>{children}</main>
    </div>
  )
}
```

## 路由组布局

### 不同布局的路由组

```text
app/
├── (marketing)/
│   ├── layout.tsx       # 营销页面布局
│   ├── page.tsx
│   └── about/
│       └── page.tsx
└── (admin)/
    ├── layout.tsx       # 管理后台布局
    └── admin/
        └── page.tsx
```

### 营销布局

```tsx [app/(marketing)/layout.tsx]
export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div>
      <header>营销头部</header>
      {children}
      <footer>营销底部</footer>
    </div>
  )
}
```

### 管理后台布局

```tsx [app/(admin)/layout.tsx]
export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="admin">
      <nav>管理导航</nav>
      <main>{children}</main>
    </div>
  )
}
```

## 条件布局

### 基于认证的布局

```tsx [app/(auth)/layout.tsx]
import { getSession } from '@/lib/auth'

export default async function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await getSession()
  
  if (!session) {
    return (
      <div className="auth-layout">
        <nav>公开导航</nav>
        {children}
      </div>
    )
  }
  
  return (
    <div className="auth-layout">
      <nav>用户导航</nav>
      {children}
    </div>
  )
}
```

## 并行布局

### 多个插槽

```text
app/
├── layout.tsx
├── @sidebar/
│   └── page.tsx
└── @modal/
    └── page.tsx
```

```tsx [app/layout.tsx]
export default function RootLayout({
  children,
  sidebar,
  modal,
}: {
  children: React.ReactNode
  sidebar: React.ReactNode
  modal: React.ReactNode
}) {
  return (
    <div>
      <header>头部</header>
      <div className="content">
        <aside>{sidebar}</aside>
        <main>{children}</main>
      </div>
      {modal}
    </div>
  )
}
```

## 加载状态布局

### loading.tsx

```tsx [app/dashboard/loading.tsx]
export default function DashboardLoading() {
  return (
    <div className="loading">
      <div className="spinner"></div>
      <p>加载中...</p>
    </div>
  )
}
```

### 骨架屏

```tsx [app/dashboard/loading.tsx]
export default function DashboardLoading() {
  return (
    <div className="skeleton">
      <div className="skeleton-header"></div>
      <div className="skeleton-sidebar"></div>
      <div className="skeleton-content">
        <div className="skeleton-card"></div>
        <div className="skeleton-card"></div>
        <div className="skeleton-card"></div>
      </div>
    </div>
  )
}
```

## 错误布局

### error.tsx

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
    <div className="error">
      <h2>加载失败</h2>
      <p>{error.message}</p>
      <button onClick={reset}>重试</button>
    </div>
  )
}
```

## 模板布局

### template.tsx

与 layout 不同，template 在导航时会重新挂载：

```tsx [app/template.tsx]
'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'

export default function Template({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  
  useEffect(() => {
    // 每次路由变化执行
    window.scrollTo(0, 0)
    console.log('页面切换:', pathname)
  }, [pathname])
  
  return <>{children}</>
}
```

## 响应式布局

### CSS Grid 布局

```tsx [app/layout.tsx]
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="grid-layout">
      <header>头部</header>
      <aside>侧边栏</aside>
      <main>{children}</main>
      <footer>底部</footer>
    </div>
  )
}
```

```css [app/globals.css]
.grid-layout {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 250px 1fr;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .grid-layout {
    grid-template-areas:
      "header"
      "main"
      "footer";
    grid-template-columns: 1fr;
  }
  
  aside {
    display: none;
  }
}
```

### Tailwind CSS 响应式

```tsx [app/layout.tsx]
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-gray-800 text-white p-4">
        头部
      </header>
      
      <div className="flex-1 flex">
        <aside className="hidden md:block w-64 bg-gray-100 p-4">
          侧边栏
        </aside>
        <main className="flex-1 p-4">
          {children}
        </main>
      </div>
      
      <footer className="bg-gray-800 text-white p-4">
        底部
      </footer>
    </div>
  )
}
```

## 布局最佳实践

### 1. 布局组件分离

::: tip
将布局组件提取到 `components/layout/` 目录，保持 app 目录简洁。
:::

```text
components/
└── layout/
    ├── Header.tsx
    ├── Footer.tsx
    ├── Sidebar.tsx
    └── MainLayout.tsx
```

### 2. 布局状态管理

```tsx [app/(dashboard)/layout.tsx]
'use client'

import { useState } from 'react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  
  return (
    <div className={sidebarOpen ? 'with-sidebar' : 'without-sidebar'}>
      <button onClick={() => setSidebarOpen(!sidebarOpen)}>
        {sidebarOpen ? '收起' : '展开'}
      </button>
      {sidebarOpen && <aside>侧边栏</aside>}
      <main>{children}</main>
    </div>
  )
}
```

### 3. 布局组合

```tsx [app/layout.tsx]
import { Header } from '@/components/layout/Header'
import { Footer } from '@/components/layout/Footer'
import { Sidebar } from '@/components/layout/Sidebar'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html>
      <body>
        <Header />
        <div className="flex">
          <Sidebar />
          <main>{children}</main>
        </div>
        <Footer />
      </body>
    </html>
  )
}
```

