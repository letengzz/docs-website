# Vue3 新组件

::: info 版本现状
`Fragment`、`Teleport` 在 Vue 3 中已稳定；`Suspense` 目前仍属于实验性特性（API 可能调整），生产使用前请评估。
:::

## Fragment

在Vue2中每个组件必须有一个根标签。这样性能方面稍微有点问题，如果每一个组件必须有根标签，组件嵌套组件的时候，有很多无用的根标签。

在Vue3中每个组件不需要有根标签。实际上内部实现的时候，最终将所有组件嵌套好之后，最外层会添加一个Fragment，用这个Fragment当做根标签。这是一种性能优化策略。

## Teleport

Teleport 是一种能够将**组件html结构**移动到指定位置的技术(设置组件的显示位置)。

```vue
<teleport to='body' >
    <div class="modal" v-show="isShow">
      <h2>我是一个弹窗</h2>
      <p>我是弹窗中的一些内容</p>
      <button @click="isShow = false">关闭弹窗</button>
    </div>
</teleport>
```

Teleport 的典型场景：

- 弹窗/模态框：从组件 DOM 树中移出，挂到 `body`，避免被父级 `overflow: hidden`、`z-index` 影响。
- 全局通知、Tooltip：需要脱离文档流层级，避免被中间容器裁剪。
- 条件性传送：`disabled` 属性为 `true` 时元素停留在原位置，需要时再传送出去。

效果验证：运行后打开浏览器控制台的元素树，弹窗内容挂在 `<body>` 下而不是组件内部。

```html
<teleport to='body' >
    <div class="modal" v-show="isShow">
      <h2>我是一个弹窗</h2>
      <p>我是弹窗中的一些内容</p>
      <button @click="isShow = false">关闭弹窗</button>
    </div>
</teleport>
```

## Suspense

等待异步组件时渲染一些额外内容，让应用有更好的用户体验。

使用步骤： 

-  异步引入组件
-  使用`Suspense`包裹组件，并配置好`default` 与 `fallback`

```tsx
import { defineAsyncComponent,Suspense } from "vue";
const Child = defineAsyncComponent(()=>import('./Child.vue'))
```

```vue
<template>
    <div class="app">
        <h3>我是App组件</h3>
        <Suspense>
          <template v-slot:default>
            <Child/>
          </template>
          <template v-slot:fallback>
            <h3>加载中.......</h3>
          </template>
        </Suspense>
    </div>
</template>
```

## 全局API转移到应用对象

- 注册全局组件：`app.component`
- 配置对象：`app.config`
- 注册全局指令：`app.directive`
- `app.mount`
- `app.unmount`
- `app.use`

## 其他

**官方文档**：https://v3-migration.vuejs.org/zh/breaking-changes/

- 过渡类名 `v-enter` 修改为 `v-enter-from`、过渡类名 `v-leave` 修改为 `v-leave-from`。


- `keyCode` 作为 `v-on` 修饰符的支持。

- `v-model` 指令在组件上的使用已经被重新设计，替换掉了 `v-bind.sync。`

- `v-if` 和 `v-for` 在同一个元素身上使用时的优先级发生了变化。`v-if`优先级更高

- 移除了`$on`、`$off` 和 `$once` 实例方法。

- 移除了过滤器 `filter`。

- 移除了`$children` 实例 `propert`。

  ......
