# 组件与布局

## 内置组件

Nuxt 提供了几个内置组件：

### NuxtPage

用于显示当前路由的页面：

```vue [app.vue]
<template>
  <div>
    <NuxtPage />
  </div>
</template>
```

### NuxtLink

用于导航的链接组件：

```vue
<template>
  <NuxtLink to="/about">关于</NuxtLink>
</template>
```

### NuxtLayout

用于切换布局：

```vue
<template>
  <NuxtLayout name="custom">
    <h1>自定义布局</h1>
  </NuxtLayout>
</template>
```

### ClientOnly

只在客户端渲染的组件：

```vue
<template>
  <ClientOnly>
    <SomeClientOnlyComponent />
    <template #fallback>
      <div>加载中...</div>
    </template>
  </ClientOnly>
</template>
```

## 布局

### 默认布局

创建 `layouts/default.vue`：

```vue [layouts/default.vue]
<template>
  <div>
    <header>
      <nav>
        <NuxtLink to="/">首页</NuxtLink>
        <NuxtLink to="/about">关于</NuxtLink>
      </nav>
    </header>
    <main>
      <slot />
    </main>
    <footer>© 2024</footer>
  </div>
</template>
```

### 自定义布局

创建 `layouts/auth.vue`：

```vue [layouts/auth.vue]
<template>
  <div class="auth-layout">
    <slot />
  </div>
</template>
```

在页面中使用：

```vue [pages/login.vue]
<script setup>
definePageMeta({
  layout: 'auth'
})
</script>
```

## 组件目录

### 基础组件

```
components/
├── MyButton.vue
└── MyInput.vue
```

### 嵌套组件

```
components/
└── base/
    ├── Button.vue
    └── Input.vue
```

使用时：

```vue
<template>
  <BaseButton />
  <BaseInput />
</template>
```

### 组件前缀

在 `nuxt.config.ts` 中配置组件前缀：

```ts [nuxt.config.ts]
export default defineNuxtConfig({
  components: [
    {
      path: '~/components',
      pathPrefix: false
    }
  ]
})
```

## 插槽

在布局中使用插槽：

```vue [layouts/default.vue]
<template>
  <div>
    <header>
      <slot name="header">默认头部</slot>
    </header>
    <main>
      <slot />
    </main>
  </div>
</template>
```

在页面中使用：

```vue [pages/index.vue]
<template>
  <div>
    <template #header>
      <h1>自定义头部</h1>
    </template>
    <p>页面内容</p>
  </div>
</template>
```
