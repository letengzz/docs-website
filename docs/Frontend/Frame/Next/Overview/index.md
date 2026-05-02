# Next 概述与安装

## Next.js 简介

Next.js 是由 Vercel 开发的基于 React 的全栈框架，提供了服务端渲染（SSR）、静态站点生成（SSG）、API 路由等开箱即用的功能。

### 核心特性

- **App Router**：基于 React Server Components 的新一代路由系统
- **服务端渲染（SSR）**：提升首屏加载速度和 SEO
- **静态站点生成（SSG）**：构建时预渲染页面
- **增量静态再生（ISR）**：无需重新构建即可更新静态页面
- **API 路由**：内置 API 端点支持
- **文件路由**：基于文件系统的路由，零配置
- **TypeScript 支持**：内置 TypeScript 支持
- **图片优化**：自动优化和懒加载图片
- **字体优化**：自动优化 Web 字体加载

### 渲染模式对比

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **CSR** | 客户端渲染，浏览器执行 | 动态交互多的应用 |
| **SSR** | 服务端渲染，每次请求生成 | 实时数据、SEO 要求高 |
| **SSG** | 静态生成，构建时生成 | 博客、文档、营销页 |
| **ISR** | 增量静态再生 | 内容频繁更新但可缓存 |

### 版本对比

| 特性 | Pages Router | App Router |
|------|-------------|------------|
| 路由方式 | `pages/` 目录 | `app/` 目录 |
| 数据获取 | `getServerSideProps` | Server Components |
| 布局系统 | 需手动实现 | `layout.tsx` 原生支持 |
| 错误处理 | `_error.js` | `error.tsx` |
| 加载状态 | 需手动实现 | `loading.tsx` |

::: tip 推荐
2026 年新建项目推荐使用 **App Router**，它是 Next.js 的未来方向，基于 React Server Components 构建。
:::

## 环境要求

### 硬件要求

- **CPU**：双核及以上处理器
- **内存**：至少 4GB RAM（推荐 8GB 以上）
- **硬盘**：至少 500MB 可用空间

### 软件要求

- **Node.js**：18.17 或更高版本
- **包管理器**：npm、yarn、pnpm 或 bun
- **操作系统**：Windows、macOS、Linux

## 安装方式

### 使用 create-next-app

```bash [终端]
# 使用 npx 创建项目
npx create-next-app@latest my-app

# 使用 pnpm 创建项目
pnpm create next-app my-app

# 使用 yarn 创建项目
yarn create next-app my-app
```

### 交互式配置选项

运行创建命令后，会提示以下配置选项：

```
√ Would you like to use TypeScript? ... No / Yes
√ Would you like to use ESLint? ... No / Yes
√ Would you like to use Tailwind CSS? ... No / Yes
√ Would you like to use `src/` directory? ... No / Yes
√ Would you like to use App Router? (recommended) ... No / Yes
√ Would you like to customize the default import alias (@/*)? ... No / Yes
```

### 手动安装

```bash [终端]
# 创建项目目录
mkdir my-app && cd my-app

# 初始化项目
npm init -y

# 安装依赖
npm install next react react-dom

# 安装开发依赖
npm install -D typescript @types/react @types/node

# 创建 package.json 脚本
```

```json [package.json]
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

## 项目结构

### App Router 结构

```
my-app/
├── app/
│   ├── layout.tsx      # 根布局
│   ├── page.tsx        # 首页
│   ├── loading.tsx     # 全局加载状态
│   ├── error.tsx       # 全局错误处理
│   └── globals.css     # 全局样式
├── public/             # 静态资源
├── components/         # 组件
├── lib/                # 工具函数
├── .env.local          # 环境变量
├── next.config.ts      # Next.js 配置
├── tsconfig.json       # TypeScript 配置
└── package.json        # 项目配置
```

### Pages Router 结构

```
my-app/
├── pages/
│   ├── _app.tsx        # 自定义 App
│   ├── _document.tsx   # 自定义 Document
│   ├── index.tsx       # 首页
│   └── api/            # API 路由
├── public/             # 静态资源
├── components/         # 组件
├── styles/             # 样式文件
├── next.config.ts      # Next.js 配置
└── package.json        # 项目配置
```

## 开发服务器

### 启动开发服务器

```bash [终端]
# 启动开发服务器
npm run dev

# 指定端口
npm run dev -- -p 3001

# 指定主机
npm run dev -- -H 0.0.0.0
```

### 访问应用

开发服务器启动后，访问 `http://localhost:3000` 查看应用。

## 构建与运行

### 生产构建

```bash [终端]
# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

### 输出分析

```bash [终端]
# 安装分析工具
npm install @next/bundle-analyzer

# 分析构建
ANALYZE=true npm run build
```

## 环境变量

### 创建环境变量文件

```env [.env.local]
# 服务端环境变量
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
API_SECRET=your-secret-key

# 客户端环境变量（需要 NEXT_PUBLIC_ 前缀）
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

### 使用环境变量

```tsx [app/config.ts]
// 服务端可用
const dbUrl = process.env.DATABASE_URL

// 客户端和服务端都可用
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```

## 常见问题

### 1. Node.js 版本过低

```bash [终端]
# 检查 Node.js 版本
node --version

# 使用 nvm 升级（Linux/macOS）
nvm install 18
nvm use 18
```

### 2. 端口被占用

```bash [终端]
# 检查端口占用
netstat -ano | findstr :3000

# 使用其他端口
npm run dev -- -p 3001
```

### 3. TypeScript 配置问题

```json [tsconfig.json]
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

