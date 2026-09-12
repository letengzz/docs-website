# Vue3 生命周期

生命周期（Lifecycle）是组件从创建、挂载、更新到卸载的整个过程。理解每个阶段「能做什么、不能做什么」，是写出稳定组件的基础。

::: info 适用版本
本节基于 Vue 3.5.x。组合式 API 的生命周期钩子以 `on` 开头，只能在 `setup` 同步执行期间注册。
:::

## 生命周期全景

Vue 3 的生命周期按时间顺序：

```text
创建：beforeCreate → created
挂载：beforeMount → mounted
更新：beforeUpdate → updated
卸载：beforeUnmount → unmounted
（keep-alive 缓存：activated / deactivated）
（错误：errorCaptured）
```

在 `<script setup>` 中，`beforeCreate` 和 `created` 没有对应的组合式钩子，因为 `setup` 本身就发生在这两个阶段之间；直接在 `setup` 顶层写的代码相当于 `created` 的执行时机。

## 选项式与组合式对照

| 选项式 API | 组合式 API | 执行时机 |
| --- | --- | --- |
| `beforeCreate` | 无（在 setup 之前） | 实例初始化前 |
| `created` | 无（setup 顶层代码） | 实例创建完成 |
| `beforeMount` | `onBeforeMount` | 首次渲染前 |
| `mounted` | `onMounted` | 首次渲染后，DOM 可访问 |
| `beforeUpdate` | `onBeforeUpdate` | 数据变化、重新渲染前 |
| `updated` | `onUpdated` | 重新渲染后 |
| `beforeUnmount` | `onBeforeUnmount` | 卸载前 |
| `unmounted` | `onUnmounted` | 卸载后 |
| `activated` | `onActivated` | 被 keep-alive 缓存后重新激活 |
| `deactivated` | `onDeactivated` | 被 keep-alive 缓存 |
| `errorCaptured` | `onErrorCaptured` | 捕获子孙组件错误 |

## 各阶段能做什么

| 阶段 | 适合做的事 | 不适合做的事 |
| --- | --- | --- |
| `setup` / `created` | 初始化状态、注册 watch、读取 props | 操作 DOM（还没挂载） |
| `onMounted` | 请求接口、初始化图表/第三方库、绑定全局事件 | 同步执行耗时逻辑阻塞首屏 |
| `onBeforeUpdate` | 更新前读取旧 DOM 状态 | 修改会触发更新的数据 |
| `onUpdated` | 依赖最新 DOM 的统计、埋点 | 在回调里改数据造成循环更新 |
| `onBeforeUnmount` | 清理定时器、取消请求、移除监听 | 启动新的异步任务 |
| `onUnmounted` | 释放图表实例、销毁资源 | 访问已被卸载的 DOM |

## 组合式 API 用法

```vue [Example.vue]
<script setup>
import { onBeforeMount, onMounted, onBeforeUpdate, onUpdated, onBeforeUnmount, onUnmounted, ref } from "vue"

const timer = ref<number>()

onMounted(() => {
  console.log("组件挂载")
  timer.value = window.setInterval(() => {
    console.log("tick")
  }, 1000)
})

onBeforeUnmount(() => {
  console.log("组件卸载前")
  window.clearInterval(timer.value)
})

onUnmounted(() => {
  console.log("组件已卸载")
})
</script>

<template>
  <p>生命周期示例</p>
</template>
```

## 与 keep-alive 配合

被 `<KeepAlive>` 缓存的组件不会走 `onUnmounted`，而是走 `onDeactivated`：

```vue
<KeepAlive>
  <component :is="currentView" />
</KeepAlive>
```

```ts
onActivated(() => {
  // 重新进入缓存组件：刷新数据、恢复状态
  refreshList()
})

onDeactivated(() => {
  // 离开缓存组件：暂停动画、停止轮询
  stopPolling()
})
```

## 错误捕获

`onErrorCaptured` 可以捕获子孙组件抛出的错误，做统一上报或降级处理：

```ts
onErrorCaptured((err, instance, info) => {
  console.error("捕获到错误：", err, info)
  // 返回 false 阻止错误继续向上传播
  return false
})
```

## 执行顺序细节

1. 父组件 `setup` → 子组件 `setup` → 子组件 `onMounted` → 父组件 `onMounted`（子先挂载，父后完成）。
2. 卸载时相反：父组件先触发 `onBeforeUnmount`，子组件先完成卸载，最后父组件 `onUnmounted`。
3. `watch` 默认在组件更新前触发（`flush: "pre"`）；需要拿到更新后的 DOM 时用 `flush: "post"` 或 `nextTick`。

## 易错点

::: danger 常见错误
1. 在 `setup` 顶层做 DOM 操作（`document.querySelector`），此时组件还没挂载，取到 `null`。
2. 在 `onMounted` 里发起请求，组件已卸载才返回，回调更新已销毁的状态；应在 `onBeforeUnmount` 取消请求或加卸载标记。
3. 定时器/事件监听只创建不清理，路由切换后继续执行，内存泄漏。
4. 在 `onUpdated` 里修改响应式数据，触发下一次更新，形成死循环。
5. 在 `setup` 之外（如异步回调内）调用 `onMounted`，钩子不会被注册并报警告。
6. keep-alive 组件以为卸载了，其实只是 deactivated，继续执行了 `onUnmounted` 的清理逻辑导致状态丢失。

:::

## 验证方式

1. 在页面挂载一个带生命周期的子组件，观察控制台输出顺序为 setup → mounted → updated → unmounted。
2. 使用 `v-if` 销毁组件，确认 `onBeforeUnmount` 与 `onUnmounted` 依次执行。
3. 把组件放进 `<KeepAlive>` 切换，确认 `onDeactivated` / `onActivated` 触发而 `onUnmounted` 不触发。
4. 在组件卸载后确认定时器停止（控制台不再输出 tick）。

## 参考资料

- Vue 生命周期钩子：https://cn.vuejs.org/guide/essentials/lifecycle.html
- 组合式 API 生命周期：https://cn.vuejs.org/api/composition-api-lifecycle.html
- KeepAlive：https://cn.vuejs.org/guide/built-ins/keep-alive.html
