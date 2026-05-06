# 路由与数据获取

## 页面路由

Nuxt 基于 `pages/` 目录自动生成路由。

### 基本路由

```
pages/
├── index.vue        # /
├── about.vue        # /about
└── posts/
    ├── index.vue    # /posts
    └── [id].vue     # /posts/:id
```

### 动态路由

使用 `[param]` 语法创建动态路由：

```vue [pages/posts/[id].vue]
<script setup>
const route = useRoute()
console.log(route.params.id)
</script>
```

### 嵌套路由

```
pages/
├── users/
│   ├── index.vue    # /users
│   └── [id].vue     # /users/:id
└── users.vue        # 父路由
```

```vue [pages/users.vue]
<template>
  <div>
    <h1>Users</h1>
    <NuxtPage /> <!-- 子路由插槽 -->
  </div>
</template>
```

## 路由导航

使用 `useRouter` 和 `useRoute` 进行导航：

```vue
<script setup>
const router = useRouter()
const route = useRoute()

const goHome = () => {
  router.push('/')
}
</script>
```

或者使用 `<NuxtLink>` 组件：

```vue
<template>
  <NuxtLink to="/">首页</NuxtLink>
  <NuxtLink :to="{ name: 'posts-id', params: { id: 1 } }">文章 1</NuxtLink>
</template>
```

## 数据获取

### useFetch

在组件中获取数据：

```vue [pages/posts/[id].vue]
<script setup>
const route = useRoute()
const { data: post } = await useFetch(`/api/posts/${route.params.id}`)
</script>
```

### useAsyncData

更灵活的数据获取：

```vue
<script setup>
const { data, pending, error, refresh } = await useAsyncData(
  'posts',
  () => $fetch('/api/posts')
)
</script>
```

### $fetch

Nuxt 提供了增强的 fetch 函数：

```ts
const data = await $fetch('/api/users')
```

## API 路由

在 `server/api/` 目录下创建 API 路由：

```ts [server/api/hello.ts]
export default defineEventHandler(() => {
  return {
    message: 'Hello World'
  }
})
```

访问 `http://localhost:3000/api/hello` 即可调用此 API。
