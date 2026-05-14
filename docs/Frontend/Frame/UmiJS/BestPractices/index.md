# UmiJS 最佳实践

本指南总结了 UmiJS 项目开发中的最佳实践，帮助你构建高质量的企业级应用。

## 项目结构

### 推荐的目录结构

```
src/
├── assets/             # 静态资源
│   ├── images/
│   ├── icons/
│   └── styles/
├── components/         # 公共组件
│   ├── Button/
│   ├── Card/
│   └── Layout/
├── hooks/              # 自定义 Hooks
│   ├── useAuth.ts
│   └── useRequest.ts
├── layouts/            # 布局文件
│   └── index.tsx
├── models/             # 数据模型
│   ├── user.ts
│   └── product.ts
├── pages/              # 页面组件
│   ├── index.tsx
│   ├── about.tsx
│   └── users/
│       ├── index.tsx
│       └── [id].tsx
├── services/           # API 服务
│   ├── user.ts
│   └── product.ts
├── utils/              # 工具函数
│   ├── request.ts
│   ├── auth.ts
│   └── format.ts
├── wrappers/           # 路由包装器
│   └── auth.tsx
├── app.tsx             # 运行时配置
├── global.less         # 全局样式
└── global.tsx          # 全局脚本
```

### 命名规范

- **组件文件**：PascalCase（如 `UserProfile.tsx`）
- **工具文件**：camelCase（如 `request.ts`）
- **样式文件**：与组件同名（如 `index.less`）
- **页面文件**：小写 + 中划线（如 `user-list.tsx`）

## 路由设计

### 路由规划

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  routes: [
    {
      path: '/',
      component: '@/layouts/index',
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
      ],
    },
    { path: '/login', component: 'login' },
    { path: '/*', component: '404' },
  ],
})
```

### 路由权限控制

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

```typescript
// 在路由配置中使用
{
  path: '/admin',
  component: 'admin',
  wrappers: ['@/wrappers/auth'],
}
```

## 组件开发

### 组件设计原则

1. **单一职责**：每个组件只负责一个功能
2. **可复用性**：提取通用逻辑为独立组件
3. **合理粒度**：不要过度拆分，保持组件内聚

### 组件模板

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

## 状态管理

### 选择策略

| 场景 | 推荐方案 |
|------|----------|
| 组件内部状态 | `useState` |
| 简单跨组件状态 | Context 或 UmiJS 数据流 |
| 中等复杂度状态 | Zustand |
| 复杂企业级状态 | Redux + Toolkit |

### UmiJS 数据流示例

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

  const logout = () => setUser(null)

  return { user, loading, login, logout }
}
```

## API 请求

### 请求封装

```tsx [src/utils/request.ts]
import { request } from 'umi'

const customRequest = (url: string, options: any = {}) => {
  const token = localStorage.getItem('token')
  
  return request(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: token ? `Bearer ${token}` : '',
    },
    timeout: 10000,
  })
}

export default customRequest
```

### 服务层封装

```tsx [src/services/user.ts]
import request from '@/utils/request'

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

### 错误处理

```tsx [src/app.tsx]
import type { RequestConfig } from 'umi'

export const request: RequestConfig = {
  timeout: 10000,
  errorConfig: {
    adaptor: (res) => {
      return {
        success: res.success,
        errorMessage: res.message,
      }
    },
  },
  middlewares: [],
  requestInterceptors: [
    (url, options) => {
      const token = localStorage.getItem('token')
      if (token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token}`,
        }
      }
      return { url, options }
    },
  ],
  responseInterceptors: [
    (response) => {
      if (response.status === 401) {
        history.push('/login')
      }
      return response
    },
  ],
}
```

## 样式管理

### CSS 模块

```tsx
import styles from './index.less'

export default function Card({ title, children }: CardProps) {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>{title}</h3>
      <div className={styles.content}>{children}</div>
    </div>
  )
}
```

### 全局样式

```less [src/global.less]
// 全局变量
@primary-color: #1890ff;
@text-color: #333;
@border-color: #e8e8e8;

// 全局重置
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: @text-color;
}
```

## 性能优化

### 组件优化

```tsx
import React, { memo, useCallback, useMemo } from 'react'

// 使用 memo 避免不必要的重渲染
const UserCard = memo(function UserCard({ user }: { user: any }) {
  return (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  )
})

// 使用 useCallback 缓存回调
const UserList = function UserList({ users, onSelect }: UserListProps) {
  const handleSelect = useCallback(
    (user) => onSelect(user),
    [onSelect]
  )

  // 使用 useMemo 缓存计算结果
  const sortedUsers = useMemo(() => {
    return [...users].sort((a, b) => a.name.localeCompare(b.name))
  }, [users])

  return (
    <ul>
      {sortedUsers.map((user) => (
        <UserCard key={user.id} user={user} />
      ))}
    </ul>
  )
}
```

### 路由懒加载

UmiJS 默认对路由组件进行代码分割，无需额外配置。

### 图片优化

```tsx
// 使用 WebP 格式
<img src="/images/photo.webp" alt="photo" />

// 懒加载
<img loading="lazy" src="/images/photo.jpg" alt="photo" />

// 响应式图片
<picture>
  <source srcSet="/images/photo.webp" type="image/webp" />
  <img src="/images/photo.jpg" alt="photo" />
</picture>
```

## 代码质量

### ESLint 配置

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "no-console": "warn"
  }
}
```

### TypeScript 配置

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "jsx": "react-jsx",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

## 测试

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
})
```

### 集成测试

```tsx [src/pages/Login.test.tsx]
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import LoginPage from './login'

describe('LoginPage', () => {
  it('login successfully', async () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )

    fireEvent.change(screen.getByPlaceholderText('用户名'), {
      target: { value: 'admin' },
    })
    fireEvent.change(screen.getByPlaceholderText('密码'), {
      target: { value: '123456' },
    })
    fireEvent.click(screen.getByText('登录'))

    await waitFor(() => {
      expect(screen.getByText('欢迎')).toBeInTheDocument()
    })
  })
})
```

## 部署优化

### 构建配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  hash: true,
  devtool: false,
  terserOptions: {
    compress: {
      drop_console: true,
      drop_debugger: true,
    },
  },
  publicPath: '/',
})
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name example.com;
    
    root /var/www/umi-app/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;
}
```

## 安全最佳实践

### XSS 防护

```tsx
// 避免使用 dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// 使用 DOMPurify 清理 HTML
import DOMPurify from 'dompurify'

<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
```

### CSRF 防护

```tsx
// 在请求头中添加 CSRF Token
export const request: RequestConfig = {
  headers: {
    'X-CSRF-Token': getCsrfToken(),
  },
}
```

### 敏感信息处理

```tsx
// 不要在代码中硬编码敏感信息
const API_KEY = process.env.REACT_APP_API_KEY

// 使用环境变量
const apiUrl = process.env.REACT_APP_API_URL
```

## 开发工作流

### Git 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

### 分支策略

- `main`：生产环境分支
- `develop`：开发环境分支
- `feature/*`：功能分支
- `bugfix/*`：修复分支
- `release/*`：发布分支

## 监控和日志

### 错误监控

```tsx [src/app.tsx]
export function onRouteChange({ location }) {
  // 页面访问统计
  trackPageView(location.pathname)
}

// 全局错误捕获
window.addEventListener('error', (event) => {
  reportError(event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  reportError(event.reason)
})
```

### 性能监控

```tsx
// 使用 Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

function reportMetric(metric) {
  // 上报性能指标
  sendToAnalytics(metric)
}

getCLS(reportMetric)
getFID(reportMetric)
getFCP(reportMetric)
getLCP(reportMetric)
getTTFB(reportMetric)
```

## 最佳实践总结

1. **项目结构**：遵循 UmiJS 约定的目录结构
2. **组件设计**：单一职责，合理拆分，使用 TypeScript
3. **状态管理**：根据项目规模选择合适的方案
4. **API 请求**：封装请求层，统一错误处理
5. **样式管理**：使用 CSS 模块或原子化 CSS
6. **性能优化**：代码分割，图片优化，缓存策略
7. **代码质量**：ESLint + TypeScript + 单元测试
8. **部署优化**：Hash 文件名，Gzip 压缩，CDN 加速
9. **安全防护**：XSS 防护，CSRF 防护，敏感信息处理
10. **监控日志**：错误监控，性能监控，访问统计

::: tip 提示
- 遵循 UmiJS 约定优于配置的原则
- 使用 TypeScript 提高代码质量
- 合理使用插件扩展功能
- 定期更新依赖版本
- 编写单元测试保证代码质量
- 使用 CI/CD 自动化部署
:::

::: danger 注意事项
- 不要在代码中硬编码敏感信息
- 生产环境不要开启 devtool
- 确保所有路由都有对应的页面组件
- 部署前确保代码没有 TypeScript 和 ESLint 错误
- 定期检查和更新依赖版本，修复安全漏洞
:::
