# Next 项目结构

Next.js 项目采用约定优于配置的设计，理解项目结构是高效开发的基础。

## App Router 目录结构

### 核心目录

```text
my-app/
├── app/                    # App Router 核心目录
│   ├── layout.tsx         # 根布局组件
│   ├── page.tsx           # 首页 (/)
│   ├── loading.tsx        # 全局加载状态
│   ├── error.tsx          # 全局错误边界
│   ├── not-found.tsx      # 404 页面
│   └── globals.css        # 全局样式
├── public/                 # 静态资源目录
│   ├── images/            # 图片资源
│   ├── fonts/             # 字体文件
│   └── favicon.ico        # 网站图标
├── components/             # React 组件
│   ├── ui/                # UI 基础组件
│   ├── layout/            # 布局组件
│   └── features/          # 功能组件
├── lib/                    # 工具函数和配置
│   ├── utils.ts           # 通用工具函数
│   ├── api.ts             # API 客户端
│   └── constants.ts       # 常量定义
├── hooks/                  # 自定义 Hooks
├── types/                  # TypeScript 类型定义
├── styles/                 # 样式文件
├── .env.local              # 本地环境变量
├── next.config.ts          # Next.js 配置
├── middleware.ts           # 中间件
├── tsconfig.json           # TypeScript 配置
└── package.json            # 项目依赖
```

## App 目录特殊文件

### 页面文件

| 文件 | 说明 | 路由 |
|------|------|------|
| `page.tsx` | 页面组件 | 对应路由路径 |
| `layout.tsx` | 布局组件 | 包裹子页面 |
| `loading.tsx` | 加载状态 | Suspense 边界 |
| `error.tsx` | 错误边界 | 捕获子组件错误 |
| `not-found.tsx` | 404 页面 | 未匹配路由 |

### 路由组

```text
app/
├── (marketing)/          # 路由组（不影响 URL）
│   ├── layout.tsx
│   ├── page.tsx          # /
│   └── about/
│       └── page.tsx      # /about
└── (dashboard)/
    ├── layout.tsx
    └── dashboard/
        └── page.tsx      # /dashboard
```

### 动态路由

```text
app/
├── blog/
│   ├── [slug]/           # 动态路由参数
│   │   └── page.tsx      # /blog/[slug]
│   └── page.tsx          # /blog
├── users/
│   ├── [id]/
│   │   └── page.tsx      # /users/[id]
│   └── page.tsx          # /users
└── [...catchAll]/        # 捕获所有路由
    └── page.tsx
```

## 组件组织

### 按功能分类

```text
components/
├── ui/                   # 基础 UI 组件
│   ├── Button.tsx
│   ├── Input.tsx
│   └── Modal.tsx
├── layout/               # 布局组件
│   ├── Header.tsx
│   ├── Footer.tsx
│   └── Sidebar.tsx
├── features/             # 业务功能组件
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   └── blog/
│       ├── PostCard.tsx
│       └── PostList.tsx
└── shared/               # 共享组件
    ├── EmptyState.tsx
    └── LoadingSpinner.tsx
```

### 按模块分类

```text
features/
├── auth/
│   ├── components/
│   ├── hooks/
│   ├── api.ts
│   └── types.ts
├── blog/
│   ├── components/
│   ├── hooks/
│   ├── api.ts
│   └── types.ts
└── user/
    ├── components/
    ├── hooks/
    ├── api.ts
    └── types.ts
```

## 样式组织

### CSS Modules

```text
components/
├── Button/
│   ├── Button.tsx
│   └── Button.module.css
└── Card/
    ├── Card.tsx
    └── Card.module.css
```

### Tailwind CSS

```text
styles/
├── globals.css           # 全局样式和 Tailwind 指令
└── components/           # 组件特定样式
    └── custom.css
```

```css [styles/globals.css]
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-white text-gray-900;
  }
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700;
  }
}
```

## 环境变量管理

### 环境文件

```text
.env                  # 所有环境共享
.env.local            # 本地开发（不提交到 Git）
.env.development      # 开发环境
.env.production       # 生产环境
```

### 变量分类

```env [.env.local]
# 服务端专用
DATABASE_URL=postgresql://localhost/mydb
API_SECRET=secret-key

# 客户端可访问
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

## 类型定义

### 全局类型

```typescript [types/index.ts]
export interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

export interface Post {
  id: string
  title: string
  content: string
  author: User
  createdAt: Date
}
```

### API 类型

```typescript [types/api.ts]
export interface ApiResponse<T> {
  data: T
  message: string
  success: boolean
}

export interface PaginationParams {
  page: number
  limit: number
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
}
```

## 路径别名配置

```json [tsconfig.json]
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"],
      "@/components/*": ["components/*"],
      "@/lib/*": ["lib/*"],
      "@/hooks/*": ["hooks/*"],
      "@/types/*": ["types/*"],
      "@/styles/*": ["styles/*"]
    }
  }
}
```

## 最佳实践

### 1. 保持 app 目录简洁

::: tip
`app/` 目录应只包含路由相关的文件（page、layout、loading、error），业务逻辑应放在其他目录。
:::

### 2. 组件拆分原则

- **UI 组件**：无状态、可复用、放在 `components/ui/`
- **业务组件**：包含业务逻辑、放在 `components/features/`
- **布局组件**：页面结构、放在 `components/layout/`

### 3. 文件命名规范

- 组件文件：`PascalCase.tsx`
- 工具函数：`camelCase.ts`
- 样式文件：`PascalCase.module.css`
- 类型文件：`camelCase.ts`
