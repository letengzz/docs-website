# 配置自动路由

## 路由插件

`unplugin-vue-router`是一个基于文件系统的自动路由解决方案，支持 TypeScript 类型。

- GitHub 地址：https://github.com/posva/unplugin-vue-router

- 文档地址：https://uvr.esm.is/


### 安装依赖

安装 unplugin-vue-router 开发依赖：

```shell
pnpm add unplugin-vue-router -D
```

### 配置 vite 插件

在配置文件 `vite.config.ts`中引入该插件：

:::danger

在 plugins 中，`VueRouter({})`必须放在 `vue()`前面。

:::

```typescript [vite.config.ts]
// ...
import VueRouter from 'unplugin-vue-router/vite'

export default defineConfig({
  plugins: [
    VueRouter({
      routesFolder: [
        { 
          // 指定页面目录
          src: 'src/views',
        },
      ],
      // 创建types文件夹用于存放类型声明文件
      dts: './types/typed-router.d.ts',
    }),
    // ⚠️ Vue must be placed after VueRouter()
    vue(),
    // ...
  ],
  // ...
})
```

### 修改路由文件

修改路由配置 `router/index.ts`：

1. 从 `vue-router/auto-routes`中导入 `routes` (这个 routes 是插件根据文件系统自动生成的)。
2. 删除创建路由实例 `createRouter`中前面手动配置的 `routes`数组，使用上面导入的 `routes`。

```typescript [src/router/index.ts]
// ...
import { routes, handleHotUpdate } from 'vue-router/auto-routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})
// 运行时更新路由，而无需重新加载页面
if (import.meta.hot) {
  handleHotUpdate(router)
}

// ...
```

## 忽略文件

启动服务，默认会在项目types下自动生成`typed-router.d.ts`文件。

在.gitignore中添加：

```tex [.gitignore]
/types/typed-router.d.ts
```

### 添加类型引用

在 `env.d.ts`末行添加如下类型引用代码：

```typescript [types/env.d.ts]
/// <reference types="unplugin-vue-router/client" />
```

### 添加页面进行测试

`unplugin-vue-router`默认会解析 `src/pages`目录，将该目录中的 Vue 文件解析到路由中。

:::tip

页面目录可以在 vite.config.ts 配置插件时指定。

:::

在 `src/views/`目录中创建 `index.vue`和 `demo.vue`。

目录结构：

```
src/
 |- views/
      |- index.vue
      |- demo.vue
```

```vue [src/views/index.vue]
<template>
  <h1>index page</h1>
</template>
```

```vue [src/views/demo.vue]
<template>
  <h1>demo</h1>
</template>
```

启动服务，在浏览器中分别访问：`http://localhost:5173`、`http://localhost:5173/demo`

## 全局布局

vite-plugin-vue-layouts非常适用于多个页面具有相同的布局的场景。

Github 地址：https://github.com/JohnCampionJr/vite-plugin-vue-layouts

### 安装依赖

安装开发依赖：

```shell
pnpm add vite-plugin-vue-layouts -D
```

### 配置 vite 插件

在 `vite.config.ts`中配置该插件：

```typescript [vite.config.ts]
// ...
import Layouts from 'vite-plugin-vue-layouts'

export default defineConfig({
  plugins: [
    // ...
    Layouts({
      layoutsDirs: 'src/layouts',
      defaultLayout: 'default',
    }),
    // ...
  ],
  // ...
})
```

- `layoutDirs`：存放布局 vue 文件的目录。
- `defaultLayout`：默认使用的布局文件名。上面配置 `default`，则默认使用。
- `src/layouts/default.vue`：作为默认布局文件。在该文件中提要提供 router-view。

### 添加类型声明

在 `env.d.ts`的末行追加类型声明语句：

```typescript [types/env.d.ts]
/// <reference types="vite-plugin-vue-layouts/client" />
```

### 创建默认布局文件

按照上面的配置创建默认布局文件：默认布局非常简单，仅包含首页 & demo页面的导航链接、路由插座 router-view。

```vue [src/layouts/default.vue]
<template>
  <div>
    <header>
      <router-link to="/" class="item">home</router-link>&nbsp;
      <router-link to="/demo" class="item">demo</router-link>
    </header>
    <router-view></router-view>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped></style>
```

### 修改路由配置

修改 `router/index.ts`，由于使用了全局布局插件，本质上是在访问的路径外面又包裹了一层组件，需要修改 `unplugin-vue-router`自动生成的路由数组 routes：

```typescript [src/router/index.ts]
// ...
import { setupLayouts } from 'virtual:generated-layouts'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // routes
  routes: setupLayouts([...routes]),
})

// ...
```

启动服务，无论访问首页（/）还是demo（/demo），都会看到默认布局中的导航链接。

### 多个布局

如果某个页面要使用其他布局，只需要按照以下两步进行：

1. 在 layouts 目录中定义布局文件，如：blank.vue，该文件中一定要有路由插座 
2. 在需要使用该布局的 Vue 文件中，通过 `definePage`来指定 `layout`：

```typescript
definePage({
  meta: {
    layout: 'blank',
  },
})
```

如果不生效，重启服务后刷新页面即可。
