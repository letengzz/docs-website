# UmiJS 目录结构

UmiJS 遵循约定优于配置的原则，有标准的目录结构。了解这些约定可以帮助你更好地组织项目代码。

## 标准目录结构

一个完整的 UmiJS 项目通常包含以下目录结构：

```text
my-umi-app/
├── src/
│   ├── pages/              # 页面目录（约定式路由）
│   │   ├── index.tsx       # 首页 /
│   │   ├── about.tsx       # 关于页 /about
│   │   ├── users/          # 用户相关页面
│   │   │   ├── index.tsx   # 用户列表 /users
│   │   │   └── [id].tsx    # 用户详情 /users/:id
│   │   └── docs/           # 文档相关页面
│   │       ├── index.tsx   # 文档首页 /docs
│   │       └── guide.tsx   # 指南页 /docs/guide
│   ├── components/         # 公共组件
│   │   ├── Header/
│   │   │   ├── index.tsx
│   │   │   └── index.less
│   │   └── Footer/
│   │       ├── index.tsx
│   │       └── index.less
│   ├── layouts/            # 布局文件
│   │   └── index.tsx       # 全局布局
│   ├── models/             # 全局数据模型（数据流）
│   │   └── user.ts
│   ├── services/           # API 服务层
│   │   └── user.ts
│   ├── utils/              # 工具函数
│   │   └── request.ts
│   ├── assets/             # 静态资源
│   │   ├── images/
│   │   └── styles/
│   ├── app.tsx             # 运行时配置
│   ├── global.tsx          # 全局脚本
│   └── global.less         # 全局样式
├── config/                 # 配置目录
│   └── config.ts           # 配置文件（与 .umirc.ts 二选一）
├── public/                 # 公共目录（构建时直接复制）
│   └── favicon.ico
├── mock/                   # Mock 数据
│   └── user.ts
├── tests/                  # 测试文件
│   └── user.test.ts
├── .umirc.ts               # 配置文件（与 config/config.ts 二选一）
├── .env                    # 环境变量
├── package.json            # 项目依赖
├── tsconfig.json           # TypeScript 配置
└── typings.d.ts            # 类型声明文件
```

## 核心目录说明

### src/pages/ - 页面目录

`pages` 目录是 UmiJS 约定式路由的核心，目录结构会自动映射为路由结构。

```text
src/pages/
├── index.tsx           → /
├── about.tsx           → /about
├── users/
│   ├── index.tsx       → /users
│   └── [id].tsx        → /users/:id
└── docs/
    ├── index.tsx       → /docs
    └── guide.tsx       → /docs/guide
```

#### 动态路由

使用方括号 `[]` 创建动态路由参数：

```tsx [src/pages/users/[id].tsx]
import { useParams } from 'umi'

export default function UserDetail() {
  const { id } = useParams()
  return <div>用户 ID: {id}</div>
}
```

#### 嵌套路由

使用 `$` 前缀创建嵌套路由：

```text
src/pages/
├── users/
│   ├── index.tsx       → /users
│   └── $layout.tsx     → /users/* (布局)
│       └── [id].tsx    → /users/:id
```

#### 404 页面

创建 `404.tsx` 作为 404 页面：

```tsx [src/pages/404.tsx]
export default function NotFound() {
  return (
    <div>
      <h1>404 - 页面未找到</h1>
      <p>抱歉，您访问的页面不存在</p>
    </div>
  )
}
```

### src/components/ - 公共组件

存放项目中可复用的组件：

```text
src/components/
├── Header/
│   ├── index.tsx       # 组件代码
│   ├── index.less      # 组件样式
│   └── index.test.tsx  # 组件测试
├── Footer/
│   └── index.tsx
└── Button/
    └── index.tsx
```

#### 组件示例

```tsx [src/components/Header/index.tsx]
import { Link } from 'umi'
import styles from './index.less'

export default function Header() {
  return (
    <header className={styles.header}>
      <Link to="/">首页</Link>
      <Link to="/about">关于</Link>
    </header>
  )
}
```

### src/layouts/ - 布局文件

布局文件用于包裹页面组件，可以包含导航栏、侧边栏、页脚等公共部分。

```tsx [src/layouts/index.tsx]
import { Outlet } from 'umi'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function Layout() {
  return (
    <div>
      <Header />
      <main>
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
```

#### 多布局

可以创建多个布局文件：

```text
src/layouts/
├── index.tsx           # 默认布局
├── admin.tsx           # 管理后台布局
└── blank.tsx           # 空白布局（无导航栏）
```

在路由配置中指定使用的布局：

```typescript [.umirc.ts]
export default {
  routes: [
    {
      path: '/',
      component: '@/layouts/index',
      routes: [
        { path: '/', component: 'index' },
        { path: '/about', component: 'about' },
      ],
    },
    {
      path: '/admin',
      component: '@/layouts/admin',
      routes: [
        { path: '/admin', component: 'admin/index' },
      ],
    },
  ],
}
```

### src/models/ - 数据模型

使用 UmiJS 内置的数据流方案，存放全局状态：

```text
src/models/
├── user.ts             # 用户状态
├── product.ts          # 产品状态
└── order.ts            # 订单状态
```

#### 模型示例

```typescript [src/models/user.ts]
import { useState } from 'react'

export default function userModel() {
  const [user, setUser] = useState(null)

  const login = async (username: string, password: string) => {
    // 登录逻辑
    const userData = await fetchUser(username, password)
    setUser(userData)
  }

  const logout = () => {
    setUser(null)
  }

  return {
    user,
    login,
    logout,
  }
}
```

### src/services/ - API 服务层

封装 API 请求，保持代码的可维护性：

```text
src/services/
├── user.ts             # 用户相关 API
├── product.ts          # 产品相关 API
└── order.ts            # 订单相关 API
```

#### 服务示例

```typescript [src/services/user.ts]
import { request } from 'umi'

export async function getUserInfo() {
  return request('/api/user/info')
}

export async function updateUser(data: any) {
  return request('/api/user/update', {
    method: 'POST',
    data,
  })
}

export async function deleteUser(id: number) {
  return request(`/api/user/${id}`, {
    method: 'DELETE',
  })
}
```

### src/utils/ - 工具函数

存放项目中常用的工具函数：

```text
src/utils/
├── request.ts          # 请求封装
├── auth.ts             # 权限相关
├── format.ts           # 格式化工具
└── validate.ts         # 验证工具
```

### src/assets/ - 静态资源

存放项目中的静态资源文件：

```text
src/assets/
├── images/             # 图片
│   ├── logo.png
│   └── banner.jpg
├── icons/              # 图标
│   └── menu.svg
└── styles/             # 全局样式
    ├── variables.less
    └── mixins.less
```

## 配置文件

### .umirc.ts

项目配置文件，与 `config/config.ts` 二选一：

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  routes: [
    { path: '/', component: 'index' },
  ],
  npmClient: 'npm',
})
```

### config/config.ts

与 `.umirc.ts` 功能相同，适合配置较多的时使用：

```text
config/
├── config.ts           # 主配置
├── routes.ts           # 路由配置
└── proxy.ts            # 代理配置
```

## 公共目录

### public/

公共目录中的文件在构建时会直接复制到 `dist` 目录：

```text
public/
├── favicon.ico         # 网站图标
├── robots.txt          # 爬虫规则
└── manifest.json       # PWA 配置
```

### mock/

Mock 数据目录，用于开发环境模拟 API：

```typescript [mock/user.ts]
export default {
  'GET /api/users': [
    { id: 1, name: '张三' },
    { id: 2, name: '李四' },
  ],
  'POST /api/user/login': (req: any, res: any) => {
    const { username, password } = req.body
    if (username === 'admin' && password === '123456') {
      res.json({ success: true, token: 'xxx' })
    } else {
      res.json({ success: false, message: '用户名或密码错误' })
    }
  },
}
```

## 别名配置

UmiJS 默认配置了 `@` 别名指向 `src` 目录：

```tsx
// 使用 @ 别名导入
import Header from '@/components/Header'
import { getUserInfo } from '@/services/user'
import styles from './index.less'
```

## 最佳实践

1. **页面组件**放在 `src/pages/` 目录
2. **公共组件**放在 `src/components/` 目录
3. **布局文件**放在 `src/layouts/` 目录
4. **数据模型**放在 `src/models/` 目录
5. **API 服务**放在 `src/services/` 目录
6. **工具函数**放在 `src/utils/` 目录
7. **静态资源**放在 `src/assets/` 目录
8. **Mock 数据**放在 `mock/` 目录

::: tip 提示
- `@` 别名默认指向 `src` 目录
- `@@` 别名指向 UmiJS 生成的临时文件目录
- 组件目录建议包含 `index.tsx` 和样式文件
- 页面文件命名使用小写加中划线（如 `user-list.tsx`）
:::

::: danger 注意事项
- `pages` 目录下的文件会自动生成路由，注意文件命名规范
- `.umirc.ts` 和 `config/config.ts` 只能存在一个
- `public` 目录的文件会直接复制到构建目录，避免与构建产物冲突
- Mock 数据仅在开发环境生效，生产环境不会包含 Mock 代码
:::
