# UmiJS 快速开始

::: danger 注意事项

- 确保 Node.js 版本 >= 14.0.0
- 页面文件必须放在 `src/pages` 目录下才能自动生成路由
- 配置文件 `.umirc.ts` 和 `config/config.ts` 只能存在一个
- 生产环境构建前请确保代码没有 TypeScript 错误
- UmiJS 4.x 默认使用 React 18，注意依赖库的兼容性

:::

::: tip 提示

- UmiJS 支持热更新，修改代码后会自动刷新浏览器
- 使用 TypeScript 可以获得更好的开发体验和类型提示
- 建议配合 ESLint 和 Prettier 使用，保持代码质量
- UmiJS 4.x 默认开启 MFSU V3，编译速度更快

:::

## 环境要求

在开始之前，请确保你的开发环境满足以下要求：

- **Node.js**：>= 14.0.0（推荐 18+）
- **npm**：>= 6.0.0 或 **yarn**：>= 1.22.0 或 **pnpm**：>= 7.0.0
- **操作系统**：Windows / macOS / Linux

::: tip React 版本说明
UmiJS 4.x 默认使用 React 18。如果需要使用 React 17，可以运行以下命令并重启：

```bash
pnpm add react@^17 react-dom@^17
```
:::

## 安装 UmiJS

### 方式一：使用 create-umi 脚手架（推荐）

```bash
# 使用 npm
npm create umi@latest

# 使用 yarn
yarn create umi

# 使用 pnpm
pnpm create umi
```

运行命令后，脚手架会引导你完成项目配置：

1. 选择项目类型：
   - `app`：应用（适合大多数项目）
   - `lib`：库（适合开发组件库）

2. 选择模板：
   - `react`：基础 React 模板
   - `ant-design-pro`：Ant Design Pro 模板
   - `simple`：简单模板

3. 选择包管理器：npm / yarn / pnpm

### 方式二：手动安装

```bash
# 创建项目目录
mkdir my-umi-app
cd my-umi-app

# 初始化项目
npm init -y

# 安装 UmiJS
npm install umi

# 安装 React
npm install react react-dom

# 安装开发依赖
npm install -D @types/react @types/react-dom
```

## 创建第一个页面

### 创建页面文件

::: danger 注意事项

- 确保 Node.js 版本 >= 14.0.0
- 页面文件必须放在 `src/pages` 目录下才能自动生成路由
- 配置文件 `.umirc.ts` 和 `config/config.ts` 只能存在一个
- 生产环境构建前请确保代码没有 TypeScript 错误
- UmiJS 4.x 默认使用 React 18，注意依赖库的兼容性

:::

在 `src/pages` 目录下创建你的第一个页面：

```tsx [src/pages/index.tsx]
export default function HomePage() {
  return (
    <div>
      <h1>Hello UmiJS!</h1>
      <p>这是我的第一个 UmiJS 页面</p>
    </div>
  )
}
```

### 创建第二个页面

```tsx [src/pages/about.tsx]
export default function AboutPage() {
  return (
    <div>
      <h1>关于页面</h1>
      <p>这是关于页面的内容</p>
    </div>
  )
}
```

UmiJS 会自动根据文件结构生成路由：

- `/` → `src/pages/index.tsx`
- `/about` → `src/pages/about.tsx`

## 启动开发服务器

```bash
# 使用 npm
npm run dev

# 使用 yarn
yarn dev

# 使用 pnpm
pnpm dev
```

开发服务器启动后，访问 `http://localhost:8000` 即可看到你的应用。

::: tip 提示
- 默认端口为 8000，可以通过配置修改
- 开发服务器支持热更新，修改代码后会自动刷新
- 使用 `PORT=3000 npm run dev` 可以指定端口
- 如果代理静态资源后页面不断重启，可以配置 `SOCKET_SERVER=127.0.0.1`
:::

## 项目结构

目录结构：

```text
my-umi-app/
├── src/
│   ├── pages/          # 页面目录
│   │   ├── index.tsx   # 首页
│   │   └── about.tsx   # 关于页
│   ├── assets/         # 静态资源
│   ├── components/     # 公共组件
│   ├── layouts/        # 布局文件
│   └── app.tsx         # 运行时配置
├── .umirc.ts           # 配置文件
├── package.json        # 项目依赖
└── tsconfig.json       # TypeScript 配置
```

## 添加样式

### 方式一：CSS 模块

```tsx [src/pages/index.tsx]
import styles from './index.css'

export default function HomePage() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Hello UmiJS!</h1>
    </div>
  )
}
```

```css [src/pages/index.css]
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  color: #1890ff;
  font-size: 24px;
}
```

### 方式二：内联样式

```tsx
export default function HomePage() {
  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ color: '#1890ff', fontSize: '24px' }}>Hello UmiJS!</h1>
    </div>
  )
}
```

### 方式三：CSS 预处理器

UmiJS 内置对 Less、Sass 的支持，无需安装额外配置：

```less [src/pages/index.less]
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;

  .title {
    color: #1890ff;
    font-size: 24px;
  }
}
```

## 添加导航

### 使用 Link 组件

```tsx [src/components/Navbar.tsx]
import { Link } from 'umi'

export default function Navbar() {
  return (
    <nav style={{ padding: '10px', background: '#f0f0f0' }}>
      <Link to="/" style={{ marginRight: '10px' }}>首页</Link>
      <Link to="/about" style={{ marginRight: '10px' }}>关于</Link>
      <Link to="/users">用户列表</Link>
    </nav>
  )
}
```

### 使用编程式导航

```tsx
import { history } from 'umi'

export default function HomePage() {
  const goToAbout = () => {
    history.push('/about')
  }

  return (
    <div>
      <h1>首页</h1>
      <button onClick={goToAbout}>跳转到关于页面</button>
    </div>
  )
}
```

## 使用布局

### 全局布局

创建全局布局文件：

```tsx [src/layouts/index.tsx]
import { Outlet } from 'umi'

export default function Layout() {
  return (
    <div>
      <header style={{ padding: '20px', background: '#1890ff', color: '#fff' }}>
        <h1>我的 UmiJS 应用</h1>
      </header>
      <main style={{ padding: '20px' }}>
        <Outlet />
      </main>
      <footer style={{ padding: '20px', background: '#f0f0f0', textAlign: 'center' }}>
        © 2024 My UmiJS App
      </footer>
    </div>
  )
}
```

## 配置项目

### 基础配置

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 路由配置
  routes: [
    { path: '/', component: 'index' },
    { path: '/about', component: 'about' },
  ],
  // 主题配置
  theme: {
    '@primary-color': '#1890ff',
  },
  // 代理配置
  proxy: {
    '/api': {
      target: 'http://localhost:3000',
      changeOrigin: true,
    },
  },
  // npm 客户端配置
  npmClient: 'npm',
})
```

### UmiJS 4.x 插件配置

在 UmiJS 4.x 中，需要显式配置插件：

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 数据流插件
  model: {},
  // Ant Design 集成
  antd: {},
  // 请求封装
  request: {},
  // 初始状态
  initialState: {},
  // Mock 数据
  mock: {},
  // 权限管理
  access: {},
  // 国际化
  locale: {},
  // 布局系统
  layout: {},
})
```

## 构建项目

```bash
# 构建生产版本
npm run build

# 使用 yarn
yarn build

# 使用 pnpm
pnpm build
```

构建完成后，产物会输出到 `dist` 目录。

## 预览生产构建

```bash
# 使用 umi preview 预览构建结果
npx umi preview

# 或使用其他静态服务器
npx serve dist
```

## 常用命令

```bash
# 开发
npm run dev

# 构建
npm run build

# 预览构建结果
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run format

# 测试
npm run test
```



