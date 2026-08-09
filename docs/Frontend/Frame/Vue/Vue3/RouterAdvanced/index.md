# Vue Router 进阶

基础篇解决了「怎么配置路由、怎么跳转、怎么传参」，进阶篇解决真实项目里的懒加载、动态路由、权限控制和错误处理。

::: info 适用版本
Vue Router 4.x 是 Vue 3 的稳定路由方案（当前 4.6.x）。本文示例基于 Vue Router 4，命令与 API 以官方文档为准。
:::

## 路由懒加载

把路由组件改为动态导入，代码按路由拆分，首屏只加载需要的部分：

```ts [router/index.ts]
import { createRouter, createWebHistory } from "vue-router"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("@/views/Home.vue"),
    },
    {
      path: "/about",
      component: () => import("@/views/About.vue"),
    },
  ],
})
```

配合 Vite 的魔法注释可以自定义分包名：

```ts
component: () => import(/* @vite-ignore */ "@/views/Admin.vue")
```

Vite 会自动按目录生成 chunk 名；也可以使用 `rollupOptions.output.manualChunks` 做更细的分包。

## 动态路由

权限类系统通常需要登录后根据角色动态添加路由：

```ts [router/index.ts]
import { createRouter, createWebHistory } from "vue-router"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: () => import("@/views/Login.vue") },
    { path: "/", component: () => import("@/layouts/Default.vue") },
  ],
})

export function registerDynamicRoutes(routes: RouteRecordRaw[]) {
  routes.forEach((route) => {
    if (!router.hasRoute(route.name ?? route.path)) {
      router.addRoute(route)
    }
  })
}
```

动态路由相关的 API：

| API | 作用 |
| --- | --- |
| `router.addRoute(route)` | 添加路由，返回删除函数 |
| `router.removeRoute(name)` | 按名称删除路由 |
| `router.hasRoute(name)` | 判断路由是否存在 |
| `router.getRoutes()` | 获取全部路由记录 |

注意：`addRoute` 添加的是顶层路由，如果要在嵌套路由下动态添加，需要用父路由的 `children` 方式：

```ts
router.addRoute("parentName", childRoute)
```

## 权限控制实战

用路由元信息 `meta` 标记权限，在全局前置守卫里统一拦截：

```ts [router/index.ts]
router.beforeEach(async (to, from) => {
  const userStore = useUserStore()

  // 页面需要登录但未登录
  if (to.meta.requiresAuth && !userStore.isLogin) {
    return { path: "/login", query: { redirect: to.fullPath } }
  }

  // 已登录访问登录页，直接回首页
  if (to.path === "/login" && userStore.isLogin) {
    return "/"
  }

  // 动态注册权限路由（只做一次）
  if (to.meta.requiresAuth && !userStore.routesLoaded) {
    const routes = await fetchUserRoutes(userStore.user!.role)
    registerDynamicRoutes(routes)
    userStore.routesLoaded = true
    return { ...to, replace: true } // 重新进入目标路由
  }
})
```

导航守卫的三种写法（Vue Router 4 推荐返回式，不强制 `next`）：

```ts
// 返回 true/undefined：放行
// 返回 false：取消导航
// 返回路由地址：重定向
router.beforeEach((to) => {
  if (!to.meta.public) return "/login"
})
```

## 路由错误处理

异步组件加载失败、守卫抛异常时统一处理：

```ts
router.onError((error, to, from) => {
  console.error("路由错误：", error)
  // 上报错误、展示降级页面
})
```

配合动态导入，还可以做「加载失败重试」：

```ts
function lazyView(loader: () => Promise<Component>) {
  return () => loader().catch(() => import("@/views/Error.vue"))
}
```

## 滚动行为

切换路由后控制滚动位置：

```ts
const router = createRouter({
  history: createWebHistory(),
  routes: [],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: "smooth" }
    return { top: 0 }
  },
})
```

## 路由缓存与 keep-alive

配合 `<KeepAlive>` 缓存列表页，避免返回时重新请求：

```vue [App.vue]
<template>
  <RouterView v-slot="{ Component, route }">
    <KeepAlive :include="['ListPage']">
      <component :is="Component" :key="route.fullPath" />
    </KeepAlive>
  </RouterView>
</template>
```

`include` 匹配的是组件 `name`，需要在 `<script setup>` 中用 `defineOptions({ name: "ListPage" })` 声明。

## meta 类型扩展

默认 `route.meta` 是 `Record<string | number | symbol, unknown>`，想获得类型提示需要声明模块扩展：

```ts [env.d.ts]
import "vue-router"

declare module "vue-router" {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    roles?: string[]
    keepAlive?: boolean
  }
}
```

## 易错点

::: danger 常见错误
1. 动态 `addRoute` 后用户直接刷新页面，路由又丢了；需要持久化用户路由信息并在初始化时重建。
2. 在守卫里用 `next()` 与返回式混用，Vue Router 4 中一旦调用 `next` 就不要再用返回值，行为会冲突。
3. `addRoute` 同名路由重复添加，控制台警告；添加前先 `hasRoute` 判断。
4. `KeepAlive` 的 `include` 写的是组件名而不是路由名，组件没定义 `name` 时缓存不生效。
5. 懒加载组件路径写错，路由跳转白屏且 `onError` 没有注册，问题难定位。
6. 守卫里请求接口失败直接卡住导航；应 catch 并返回错误页或登录页。
:::

## 验证方式

1. 打开控制台 Network，访问 `/about` 时只加载对应的 chunk（`about.js`），而不是整个 bundle。
2. 未登录直接访问受保护路由，被重定向到 `/login?redirect=/admin`。
3. 登录后刷新页面，动态路由仍然存在，页面可访问。
4. 路由切换时滚动条回到顶部（或按 `scrollBehavior` 配置执行）。
5. 故意把懒加载路径改错，`router.onError` 能捕获错误。

## 参考资料

- Vue Router 官方文档：https://router.vuejs.org/zh/
- 动态路由：https://router.vuejs.org/zh/guide/advanced/dynamic-routing.html
- 导航守卫：https://router.vuejs.org/zh/guide/advanced/navigation-guards.html
- 滚动行为：https://router.vuejs.org/zh/guide/advanced/scroll-behavior.html
