# Vue概述

Vue (读音 /vjuː/，类似于 view) 是一套用于构建用户界面的渐进式框架。

Vue 的核心库只关注视图层，不仅易于上手，还便于与第三方库或既有项目整合。另一方面，当与现代化的工具链以及各种支持类库结合使用时，Vue 也完全能够为复杂的单页应用提供驱动。

官方网站：https://cn.vuejs.org

![Vue 示意图](./Overview/assets/img202401302208831.png)

- [Vue 概述](Overview/index.md)
- [Vue 2](Vue2/index.md)
- [Vue 3](Vue3/index.md)

## 从 Vue 到 Nuxt：什么时候需要全栈框架

本专题讲的是**视图层**：组件、响应式、路由、状态管理。这些知识在 Nuxt 里**完全适用**——Nuxt 不改变 Vue 的写法，它只是在外面包了一层服务端运行时。真正需要新学的只有四件事：

| 新问题 | Nuxt 的答案 | 详见 |
| --- | --- | --- |
| 页面在哪里被渲染 | SSR / SSG / ISR / SPA 四种模式 + `routeRules` 混合 | [渲染模式与架构](../Nuxt/Overview/index.md) |
| 数据怎么在服务端预取、客户端复用 | `useFetch` / `useAsyncData` 与 payload 复用 | [数据获取与状态](../Nuxt/DataFetching/index.md) |
| 怎么在同一个项目里写后端 | `server/api` 目录 + `runtimeConfig` | [服务端能力](../Nuxt/ServerRoute/index.md) |
| 产物怎么部署 | 静态托管 / Node 服务 / 平台 preset | [部署与实战](../Nuxt/Deployment/index.md) |

::: tip 什么时候该上 Nuxt，什么时候不该
| 场景 | 选择 | 理由 |
| --- | --- | --- |
| 面向外部用户、需要首屏与 SEO | **Nuxt** | SSR/SSG 是唯一能同时满足两者的方案 |
| 内容型站点（博客、文档、营销页） | **Nuxt（SSG）** | 产物是静态文件，成本为零 |
| 登录后的后台管理界面 | **Vite + Vue Router** | 无 SEO 需求，Nuxt 只会多一层服务端复杂度 |
| 纯组件库 / 内部工具 | **Vite + Vue** | 不需要服务端 |

**「用了 Vue 就该用 Nuxt」是不成立的**。Nuxt 的价值集中在「外部用户能看到的、需要被搜索引擎抓取且首屏要快的页面」。
:::

另一个相关但不同的问题：**一个页面里要放多个团队、多个技术栈的 Vue 应用**——那是微前端的领域，见 [微前端](../../MicroFrontend/index.md)（与 Nuxt 的分工是「单应用内的渲染策略 vs 多应用间的组合方式」）。

