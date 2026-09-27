# Next

- [Next 概述与安装](Overview/index.md)
- [Next 项目结构](Structure/index.md)
- [Next 路由系统](Routing/index.md)
- [Next 页面管理](Pages/index.md)
- [Next 布局系统](Layouts/index.md)
- [Next 组件开发](Components/index.md)
- [Next 数据获取](DataFetching/index.md)
- [Next 状态管理](StateManagement/index.md)
- [Next 中间件](Middleware/index.md)
- [Next API 路由](ApiRoutes/index.md)
- [Next 配置详解](Config/index.md)
- [Next 部署与优化](Deployment/index.md)

## 与 Nuxt 的逐项对照

两者是同层方案（Vue 生态与 React 生态的全栈框架），架构决策可以互相对照。差异最大的不是功能多少，而是**「服务端边界画在哪里」**。

| 维度 | Nuxt 4 | Next.js（App Router） |
| --- | --- | --- |
| 底层视图 | Vue 3 组合式 API | React（Server Components） |
| **服务端边界** | **目录粒度**：`server/` 是服务端，`app/` 是前端 | **组件粒度**：每个组件自己声明在哪跑 |
| 服务端引擎 | Nitro（跨运行时 preset） | 自带 Node / Edge runtime |
| 数据获取 | `useFetch` / `useAsyncData`（显式 key 与缓存） | `fetch` 扩展 + `cache` 选项（隐式） |
| 状态传递 | payload 自动内联，客户端复用 | RSC 序列化流 |
| 混合渲染 | `routeRules` 按路由 | `export const dynamic` / `revalidate` 按路由 |
| 学习曲线 | 相对平缓（延续 Vue 心智） | 陡（RSC 与客户端边界是新概念） |
| 构建产物 | `.output/`（服务端依赖已内联） | `.next/`（仍需部分依赖） |

::: tip 「目录粒度 vs 组件粒度」的取舍
- **目录粒度（Nuxt）** 更好理解：看目录就知道代码在哪跑，不需要逐个组件判断。
- **组件粒度（Next 的 RSC）** 更细：可以把「一个页面的静态框架放服务端、一小块交互放客户端」，从而减少客户端 JS 体积。

两者的**实际差别出现在大型页面**：RSC 能把客户端 bundle 压得更小；Nuxt 需要靠 `<ClientOnly>`、`defineAsyncComponent`、`<Lazy*>` 等手动手段控制。

**选型结论不变：团队是 Vue 栈 → Nuxt；React 栈 → Next。** 架构差异不足以让人跨栈迁移。Nuxt 侧的完整展开见 [Nuxt 专题](../Nuxt/index.md)。
:::

