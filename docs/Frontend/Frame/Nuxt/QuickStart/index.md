# 快速入门

## 环境要求

- Node.js 18.0.0 或更高版本
- npm、yarn、pnpm 或 bun

## 创建项目

使用以下命令创建一个新的 Nuxt 项目：

```bash [终端]
npx nuxi@latest init my-nuxt-app
```

进入项目目录：

```bash [终端]
cd my-nuxt-app
```

## 安装依赖

```bash [终端]
npm install
```

## 开发服务器

启动开发服务器：

```bash [终端]
npm run dev
```

默认情况下，开发服务器将在 `http://localhost:3000` 启动。

## 项目结构

```
my-nuxt-app/
├── .nuxt/          # 自动生成的构建目录
├── assets/         # 未编译的资源文件
├── components/     # Vue 组件
├── composables/    # 可组合函数
├── layouts/        # 布局组件
├── pages/          # 页面（自动生成路由）
├── public/         # 静态资源
├── server/         # 服务端代码
├── app.vue         # 根组件
├── nuxt.config.ts  # Nuxt 配置
└── package.json
```

## 创建第一个页面

在 `pages/` 目录下创建 `index.vue`：

```vue [pages/index.vue]
<template>
  <div>
    <h1>Hello Nuxt!</h1>
    <p>欢迎来到 Nuxt 世界</p>
  </div>
</template>
```

::: tip
如果 `pages/` 目录不存在，你需要手动创建它。
:::

## 构建生产版本

```bash [终端]
npm run build
```

## 预览生产构建

```bash [终端]
npm run preview
```
