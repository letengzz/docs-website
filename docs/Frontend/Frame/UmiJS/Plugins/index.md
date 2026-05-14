# UmiJS 插件系统

UmiJS 采用插件化架构，所有功能都通过插件实现。了解插件系统可以帮助你更好地扩展和定制 UmiJS。

::: tip UmiJS 4.x 插件变化
在 UmiJS 4.x 中，一些之前版本默认启用的插件规则需要显式配置，以减少"黑盒"行为。所有插件都需要在配置文件中明确启用和配置。
:::

## 什么是插件

UmiJS 的插件是一个 npm 包，可以扩展 UmiJS 的功能。插件可以：

- 修改构建配置
- 添加运行时功能
- 注册新的命令
- 扩展路由系统
- 添加页面模板

## 插件类型

### 构建时插件

在构建阶段执行，修改 Webpack/Vite 配置、添加 loader 等：

```typescript
import type { IApi } from 'umi'

export default (api: IApi) => {
  // 修改构建配置
  api.modifyWebpackConfig((memo) => {
    memo.resolve?.alias?.set('@custom', '/path/to/custom')
    return memo
  })
  
  // 添加 Babel 插件
  api.addBabelPlugins(() => require.resolve('babel-plugin-macros'))
  
  return {
    name: 'my-build-plugin',
  }
}
```

### 运行时插件

在浏览器端执行，添加全局组件、修改路由等：

```typescript
import type { IApi } from 'umi'

export default (api: IApi) => {
  // 添加运行时配置
  api.addRuntimePlugin(() => require.resolve('./runtime.ts'))
  
  return {
    name: 'my-runtime-plugin',
  }
}
```

## 官方插件

### @umijs/plugins

UmiJS 官方插件集合，包含常用功能：

```bash
npm install @umijs/plugins
```

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // UmiJS 4.x 需要显式配置插件
  model: {},
  antd: {},
  request: {},
  initialState: {},
  access: {},
  locale: {},
  layout: {},
  mock: {},
})
```

### 常用插件列表

| 插件名 | 功能 | 配置项 |
|--------|------|--------|
| `@umijs/plugins` | 插件集合 | - |
| `@umijs/plugin-access` | 权限管理 | `access` |
| `@umijs/plugin-antd` | Ant Design 集成 | `antd` |
| `@umijs/plugin-model` | 数据流 | `model` |
| `@umijs/plugin-request` | 请求封装 | `request` |
| `@umijs/plugin-initialState` | 初始状态 | `initialState` |
| `@umijs/plugin-locale` | 国际化 | `locale` |
| `@umijs/plugin-layout` | 布局系统 | `layout` |
| `@umijs/plugin-mock` | Mock 数据 | `mock` |

::: danger UmiJS 4.x 注意事项
在 UmiJS 4.x 中，不再默认启用插件。必须在配置文件中显式配置每个插件，即使使用空对象 `{}` 也要配置。这是为了减少"黑盒"行为，让开发者更清楚哪些插件被启用。
:::

## 权限管理插件

### 安装和配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  access: {},
})
```

### 定义权限

```tsx [src/app.tsx]
export function getInitialState() {
  return {
    name: '张三',
    isAdmin: true,
    permissions: ['read', 'write', 'delete'],
  }
}
```

```tsx [src/access.ts]
export default function access(initialState: any) {
  const { isAdmin, permissions } = initialState || {}
  
  return {
    isAdmin,
    canRead: permissions?.includes('read'),
    canWrite: permissions?.includes('write'),
    canDelete: permissions?.includes('delete'),
  }
}
```

### 使用权限

```tsx
import { useAccess, Access } from 'umi'

export default function Page() {
  const access = useAccess()
  
  return (
    <div>
      {access.isAdmin && <button>管理</button>}
      
      <Access accessible={access.canWrite}>
        <button>编辑</button>
      </Access>
      
      <Access accessible={access.canDelete} fallback={<div>无权限</div>}>
        <button>删除</button>
      </Access>
    </div>
  )
}
```

## Ant Design 插件

### 安装和配置

```bash
npm install antd @ant-design/icons
```

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  antd: {
    // 按需加载
    import: true,
    // 主题配置
    theme: {
      '@primary-color': '#1890ff',
    },
    // dark 主题
    dark: false,
    // compact 主题
    compact: false,
    // 配置 antd 的 configProvider
    configProvider: {},
    // 是否引入 antd 的样式
    style: true,
  },
})
```

### 使用组件

```tsx
import { Button, Input, Form } from 'antd'

export default function Page() {
  return (
    <Form>
      <Form.Item label="用户名">
        <Input placeholder="请输入用户名" />
      </Form.Item>
      <Form.Item>
        <Button type="primary">提交</Button>
      </Form.Item>
    </Form>
  )
}
```

## 数据流插件

### 安装和配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  model: {},
})
```

### 创建模型

```tsx [src/models/user.ts]
import { useState } from 'react'

export default function userModel() {
  const [user, setUser] = useState(null)
  
  const login = async (username: string, password: string) => {
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

### 使用模型

```tsx
import { useModel } from 'umi'

export default function Page() {
  const { user, login, logout } = useModel('user')
  
  if (!user) {
    return <button onClick={() => login('admin', '123456')}>登录</button>
  }
  
  return (
    <div>
      <p>欢迎, {user.name}</p>
      <button onClick={logout}>退出</button>
    </div>
  )
}
```

## 请求插件

### 安装和配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  request: {
    // 请求前缀
    dataField: 'data',
  },
})
```

### 使用请求

```tsx
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
```

### 请求拦截器

```tsx [src/app.tsx]
import type { RequestConfig } from 'umi'

export const request: RequestConfig = {
  timeout: 10000,
  errorConfig: {},
  middlewares: [],
  requestInterceptors: [
    (url, options) => {
      // 添加 token
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
      // 统一处理响应错误
      if (response.status === 401) {
        // 跳转到登录页
        history.push('/login')
      }
      return response
    },
  ],
}
```

## 国际化插件

### 安装和配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  locale: {
    // 默认语言
    default: 'zh-CN',
    // 支持的语言
    baseNavigator: true,
    // 是否开启
    enable: true,
    // 语言列表
    locales: [
      { name: '中文', locale: 'zh-CN' },
      { name: 'English', locale: 'en-US' },
    ],
  },
})
```

### 创建语言文件

```typescript [src/locales/zh-CN.ts]
export default {
  'nav.home': '首页',
  'nav.about': '关于',
  'nav.login': '登录',
  'user.welcome': '欢迎, {name}',
}
```

```typescript [src/locales/en-US.ts]
export default {
  'nav.home': 'Home',
  'nav.about': 'About',
  'nav.login': 'Login',
  'user.welcome': 'Welcome, {name}',
}
```

### 使用国际化

```tsx
import { useIntl } from 'umi'

export default function Navbar() {
  const intl = useIntl()
  
  return (
    <nav>
      <a>{intl.formatMessage({ id: 'nav.home' })}</a>
      <a>{intl.formatMessage({ id: 'nav.about' })}</a>
      <a>{intl.formatMessage({ id: 'nav.login' })}</a>
    </nav>
  )
}
```

## 布局插件

### 安装和配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  layout: {
    // 布局名称
    name: '我的应用',
    // 布局产品
    product: 'my-app',
    // 布局配置
    locale: true,
    layout: 'mix',
    navTheme: 'light',
    primaryColor: '#1890ff',
    fixedHeader: true,
    fixSiderbar: true,
  },
})
```

## 自定义插件

### 创建插件

```typescript
import type { IApi } from 'umi'

export default (api: IApi) => {
  // 插件名称
  api.describe({
    key: 'my-custom-plugin',
    config: {
      schema(joi) {
        return joi.object({
          enable: joi.boolean().default(true),
        })
      },
    },
    enableBy: api.EnableBy.config,
  })
  
  // 修改 Webpack 配置
  api.modifyWebpackConfig((memo) => {
    if (api.config.myCustomPlugin.enable) {
      // 自定义配置
      memo.plugins?.push(new MyPlugin())
    }
    return memo
  })
  
  // 添加运行时配置
  api.addRuntimePlugin(() => require.resolve('./runtime.ts'))
  
  // 注册命令
  api.registerCommand({
    name: 'my-command',
    fn() {
      console.log('执行自定义命令')
    },
  })
  
  return {
    name: 'my-custom-plugin',
  }
}
```

### 使用插件

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  myCustomPlugin: {
    enable: true,
  },
})
```

## 插件 API

### 构建时 API

| API | 说明 |
|-----|------|
| `api.describe()` | 描述插件 |
| `api.modifyWebpackConfig()` | 修改 Webpack 配置 |
| `api.addBabelPlugins()` | 添加 Babel 插件 |
| `api.addBabelPresets()` | 添加 Babel 预设 |
| `api.registerCommand()` | 注册命令 |
| `api.onBuildComplete()` | 构建完成回调 |
| `api.onDevCompileDone()` | 开发编译完成回调 |

### 运行时 API

| API | 说明 |
|-----|------|
| `api.addRuntimePlugin()` | 添加运行时插件 |
| `api.addRuntimePluginKey()` | 添加运行时插件 key |
| `api.modifyRoutes()` | 修改路由 |

## 插件开发最佳实践

1. **使用 `api.describe()`** 描述插件的名称和配置
2. **使用 `api.EnableBy.config`** 控制插件启用条件
3. **提供配置校验** 使用 `schema` 验证配置
4. **保持插件单一职责** 一个插件只做一件事
5. **提供类型定义** 方便 TypeScript 用户使用
6. **编写文档** 说明插件的使用方法和配置项

::: tip 提示
- UmiJS 的插件系统非常灵活，可以扩展任何功能
- 官方插件集合包含了大部分常用功能
- 自定义插件可以满足特定项目需求
- 插件配置在 `.umirc.ts` 中进行
:::

::: danger 注意事项
- 插件的 `key` 必须唯一，避免冲突
- 修改 Webpack 配置时注意性能影响
- 运行时插件会增加客户端代码体积
- 插件配置错误可能导致构建失败
- 自定义命令需要在开发环境使用
:::
