# Vue3 性能优化

Vue 3 的编译器和响应式系统已经做了大量优化，但真正卡顿往往来自「不该更新的更新、不该加载的加载」。本节给出从渲染、包体积到网络加载的优化清单。

::: info 适用版本
本节基于 Vue 3.5.x 与 Vite 构建。Vue 3 编译器默认启用静态提升、patchFlag 和事件缓存，模板本身已经足够高效。
:::

## 先定位再优化

优化前先量化：

1. 打开 Vue DevTools 的 Performance 面板，录制交互，查看组件渲染耗时。
2. 用 Vite 构建分析：`npx vite-bundle-visualizer` 或安装 `rollup-plugin-visualizer` 查看包体积。
3. 用浏览器 Performance 面板确认瓶颈是渲染、网络还是主线程脚本。

不要凭感觉优化，先找到真正的热点。

## 渲染性能优化

### 减少不必要的响应式

不需要响应式的数据用普通变量；大对象只在部分字段变化时用 `shallowRef` / `shallowReactive`：

```ts
import { shallowRef } from "vue"

// 大数据集整体替换时，浅层 ref 避免深层代理开销
const list = shallowRef<Item[]>([])
list.value = await fetchList()
```

永远不变的对象用 `markRaw` 标记，跳过代理：

```ts
import { markRaw } from "vue"

const echartsInstance = markRaw(echarts.init(el))
```

### v-memo 与 v-once

`v-once` 只渲染一次，适合静态内容：

```vue
<p v-once>{{ staticText }}</p>
```

`v-memo` 在条件不变时跳过子树的更新（Vue 3.2+）：

```vue
<div v-memo="[item.id, item.updatedAt]">
  <ExpensiveItem :item="item" />
</div>
```

### 列表性能

- 保证 `:key` 稳定唯一。
- 大列表用虚拟滚动（`vue-virtual-scroller` 或自实现）。
- 过滤/排序逻辑放计算属性，避免模板里写方法每次渲染都执行。

### keep-alive 缓存

```vue
<KeepAlive :include="['ListPage', 'DetailPage']">
  <RouterView />
</KeepAlive>
```

适合重复进入的列表页、详情页。

## 异步组件与分包

`defineAsyncComponent` 让非首屏组件按需加载：

```vue [App.vue]
<script setup>
import { defineAsyncComponent } from "vue"

const HeavyChart = defineAsyncComponent(() => import("./HeavyChart.vue"))
</script>

<template>
  <HeavyChart />
</template>
```

配合 `Suspense` 提供加载占位：

```vue
<Suspense>
  <template #default>
    <AsyncPage />
  </template>
  <template #fallback>
    <Loading />
  </template>
</Suspense>
```

## 包体积优化

1. **按需引入组件库**：Element Plus 用 `unplugin-vue-components` + `unplugin-auto-import`。
2. **只 import 用到的 API**：`import { ref } from "vue"` 而不是 `import Vue from "vue"`。
3. **避免全量引入 lodash**：改用 `lodash-es` 并按需 import，或直接手写。
4. **压缩与拆包**：Vite 默认产物压缩，`manualChunks` 把 vendor 单独拆出，利用浏览器缓存。
5. **gzip/brotli**：部署层（Nginx）开启压缩，参考本站 Nginx 相关文档。

## 网络与数据优化

- 路由懒加载（见「Vue Router 进阶」）。
- 图片懒加载：`loading="lazy"` 或组件库的 Lazy 组件。
- 请求合并与缓存：列表页缓存数据，返回时直接展示。
- 大接口分页或虚拟列表，不要一次渲染上万行。

## watch 与计算属性

- 计算属性有缓存，模板中多处使用同一逻辑时优先计算属性。
- `watch` 监听对象默认 `deep: false`；确定需要深监听时评估性能影响。
- `flush: "post"` 让回调在 DOM 更新后执行，减少布局抖动。

## 易错点

::: danger 常见错误
1. 大列表每次渲染都重新执行过滤方法（模板里 `v-for="item in filterList()"`），改为计算属性。
2. 对不可能变化的数据也用 `reactive`，白白增加代理开销。
3. 组件库全量引入，bundle 直接多几百 KB。
4. 每个列表项都是重量级组件且没有 `v-memo`，滚动卡顿。
5. 在 `watch` 回调里频繁请求接口且没有防抖/取消，接口风暴。
6. 优化后不测量，改了半天不知道是否有效。
:::

## 验证方式

1. 构建后运行 `npx vite-bundle-visualizer`，确认首屏相关 chunk 大小合理。
2. Vue DevTools Performance 录制：交互前后组件更新数量明显下降。
3. 浏览器 Network 面板确认路由懒加载只加载当前页 chunk。
4. 用 Lighthouse 跑一次性能分，记录优化前后对比。
5. 大列表滚动测试帧率，虚拟滚动实现后滚动流畅。

## 相关专题

- [前端工程化](../../../../Others/FrontendEngineering/index.md)：工程级构建优化与性能基线
- [构建优化](../../../../Others/FrontendEngineering/BuildOptimization/index.md)：分包、压缩、CDN 与体积监控

## 参考资料

- Vue 渲染机制与性能：https://cn.vuejs.org/guide/extras/rendering-mechanism.html
- Vue 性能优化：https://cn.vuejs.org/guide/best-practices/performance.html
- 虚拟滚动（vue-virtual-scroller）：https://github.com/Akryum/vue-virtual-scroller
- rollup-plugin-visualizer：https://github.com/btd/rollup-plugin-visualizer
