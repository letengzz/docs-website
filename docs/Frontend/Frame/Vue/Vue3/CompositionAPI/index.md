# Vue3 Composition API 深入

Composition API 把「同一功能的代码」组织在一起，而不是按 `data`、`methods` 等选项分散。本节在基础语法之上，讲透 `<script setup>` 的编译特性、可组合函数（composable）的设计规范和类型化用法。

::: info 适用版本
本节基于 Vue 3.5.x。`<script setup>` 从 Vue 3.2 起稳定，`defineModel` 从 3.4 起稳定，响应式 props 解构在 3.5 中成为稳定特性。
:::

## script setup 的编译期魔法

`<script setup>` 中的顶层变量和方法会**自动暴露给模板**，不需要 `return`：

```vue [Counter.vue]
<script setup>
import { ref } from "vue"
const count = ref(0)
function add() {
  count.value++
}
</script>

<template>
  <button @click="add">{{ count }}</button>
</template>
```

编译后它等价于一个 `setup()` 函数体，因此：

- 顶层 `await` 可用（组件变成异步组件，需要配合 `Suspense`）。
- 不能出现重复的顶层声明，否则编译报错。
- 与普通 `<script>` 共存时，普通 `<script>` 用于模块级副作用（如注册全局组件）。

## defineProps 与 defineEmits

`defineProps` 和 `defineEmits` 是编译器宏，不需要 import：

```vue [UserCard.vue]
<script setup lang="ts">
interface User {
  id: number
  name: string
}

const props = defineProps<{
  user: User
  showAvatar?: boolean
}>()

const emit = defineEmits<{
  (e: "update", user: User): void
  (e: "delete", id: number): void
}>()

function remove() {
  emit("delete", props.user.id)
}
</script>

<template>
  <div @click="remove">{{ user.name }}</div>
</template>
```

类型化声明还支持默认值（Vue 3.5+ 可直接解构）：

```vue
<script setup lang="ts">
const { title = "默认标题", showAvatar = true } = defineProps<{
  title?: string
  showAvatar?: boolean
}>()
</script>
```

## defineExpose 与 defineOptions

`<script setup>` 的组件默认是「关闭的」，父组件通过模板 ref 只能访问到 `defineExpose` 暴露的内容：

```vue [Child.vue]
<script setup>
function reset() {
  console.log("reset")
}
defineExpose({ reset })
</script>
```

```vue [Parent.vue]
<script setup>
import { ref } from "vue"
import Child from "./Child.vue"
const childRef = ref<InstanceType<typeof Child> | null>(null)
</script>

<template>
  <Child ref="childRef" />
  <button @click="childRef?.reset()">重置</button>
</template>
```

`defineOptions` 用于声明组件选项（Vue 3.3+）：

```vue
<script setup>
defineOptions({
  name: "MyCard",
  inheritAttrs: false,
})
</script>
```

## watch 的进阶选项

```ts
watch(
  () => props.user.id,
  async (newId, oldId) => {
    const data = await fetchUser(newId)
    userData.value = data
  },
  {
    deep: false,        // 监听对象内部变化
    immediate: true,    // 立即执行一次
    flush: "post",      // DOM 更新后执行
  },
)
```

同时监听多个来源：

```ts
watch([firstName, lastName], ([newFirst, newLast], [oldFirst, oldLast]) => {
  console.log(newFirst, newLast)
})
```

## composable：把逻辑抽成函数

约定：以 `use` 开头、返回响应式状态和操作函数：

```ts [useCounter.ts]
import { ref } from "vue"

export function useCounter(initial = 0) {
  const count = ref(initial)
  const double = computed(() => count.value * 2)

  function increment() {
    count.value++
  }

  return { count, double, increment }
}
```

```vue [App.vue]
<script setup>
import { useCounter } from "./useCounter"
const { count, double, increment } = useCounter(10)
</script>

<template>
  <p>{{ count }} / {{ double }}</p>
  <button @click="increment">+1</button>
</template>
```

设计原则：

1. **单一职责**：一个 composable 只解决一个问题。
2. **返回 ref 而不是 reactive**：解构后仍保持响应式，调用方更灵活。
3. **参数化**：允许传入初始值、依赖项。
4. **清理副作用**：事件监听、定时器、请求取消在 `onScopeDispose` 中清理。

```ts [useMouse.ts]
import { onScopeDispose, ref } from "vue"

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  function update(e: MouseEvent) {
    x.value = e.clientX
    y.value = e.clientY
  }

  window.addEventListener("mousemove", update)
  onScopeDispose(() => window.removeEventListener("mousemove", update))

  return { x, y }
}
```

## provide / inject 类型化

```ts [symbols.ts]
import type { InjectionKey, Ref } from "vue"

export const themeKey: InjectionKey<Ref<string>> = Symbol("theme")
```

```ts [Provider.vue]
import { provide, ref } from "vue"
import { themeKey } from "./symbols"
provide(themeKey, ref("dark"))
```

```ts [Consumer.vue]
import { inject } from "vue"
import { themeKey } from "./symbols"
const theme = inject(themeKey)
```

用 `InjectionKey` 后，取到的值自动获得类型推导；建议注入默认值并用 `readonly` 保护，避免子组件随意修改。

## 易错点

::: danger 常见错误
1. 在 `setup` 顶层之外（如 `setTimeout` 回调里）调用 `watchEffect` 等 API，会失去组件作用域，生命周期清理失效。
2. `defineProps` 解构后直接修改解构变量，修改不会同步回 props；只有响应式解构（3.5+）才允许按 ref 方式使用。
3. 父组件想调用子组件方法却忘了 `defineExpose`，`ref` 拿到的是空对象。
4. composable 里返回 `reactive` 对象再解构，解构出的字段丢失响应式。
5. 在 `watch` 回调里做异步请求但不在 `onScopeDispose` 里取消，组件卸载后仍可能更新状态。
6. 同时使用 `<script setup>` 和 `setup()` 选项重复声明逻辑，行为混乱。
:::

## 验证方式

1. `npm run dev` 后修改 `useCounter` 的初始值，页面显示正确。
2. 在 `useMouse` 示例中移动鼠标，页面坐标实时变化；切换路由卸载组件后，控制台确认监听器已被移除（可用 `window` 事件计数验证）。
3. 用 TypeScript 写错 `defineProps` 类型，`vue-tsc` 或编辑器立即报错。
4. 父组件通过模板 ref 调用子组件 `defineExpose` 的方法，能正常执行。

## 参考资料

- `<script setup>`：https://cn.vuejs.org/api/sfc-script-setup.html
- 组合式函数：https://cn.vuejs.org/guide/reusability/composables.html
- 依赖注入：https://cn.vuejs.org/guide/components/provide-inject.html
- 响应式 API：https://cn.vuejs.org/api/reactivity-core.html
