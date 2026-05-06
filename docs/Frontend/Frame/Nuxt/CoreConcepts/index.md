# 核心概念

## 自动导入

Nuxt 3 提供了强大的自动导入功能，你可以直接使用 Vue 和 Nuxt 的组合式 API 而无需显式导入。

```vue [app.vue]
<script setup>
// 无需导入 ref
const count = ref(0)
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

## 组件自动导入

在 `components/` 目录下的组件会被自动导入，无需手动导入：

```
components/
└── MyButton.vue
```

```vue [pages/index.vue]
<template>
  <!-- 直接使用，无需导入 -->
  <MyButton />
</template>
```

## Composables

在 `composables/` 目录下定义的组合式函数会被自动导入：

```ts [composables/useCounter.ts]
export function useCounter() {
  const count = ref(0)
  const increment = () => count.value++
  return { count, increment }
}
```

```vue [pages/index.vue]
<script setup>
const { count, increment } = useCounter()
</script>
```

## 目录结构约定

Nuxt 使用约定优于配置的原则，特定目录下的文件会有特殊的处理：

- `pages/` - 自动路由
- `components/` - 自动导入的组件
- `composables/` - 自动导入的组合式函数
- `layouts/` - 布局组件
- `assets/` - 资源文件
- `public/` - 静态资源
- `server/` - 服务端 API

## 渲染模式

### 服务端渲染（SSR）
默认模式，在服务端渲染页面，发送完整的 HTML 给客户端。

### 客户端渲染（CSR）
只在客户端渲染页面。

### 静态站点生成（SSG）
预渲染所有页面为静态 HTML。

### 混合渲染（ISR/SSG+SSR）
部分页面静态化，部分页面动态渲染。

## 状态管理

Nuxt 内置了 `useState` 来管理跨组件和服务端客户端共享的状态：

```ts
const count = useState('count', () => 0)
```
