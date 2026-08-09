# Vue3 TypeScript 集成

Vue 3 从设计上就拥抱 TypeScript：组合式 API 的类型推导非常友好。本节覆盖从项目创建、组件类型化到常用工具类型的完整写法。

::: info 适用版本
本节基于 Vue 3.5.x 与 TypeScript 5.x。推荐使用 `create-vue` 创建项目，官方模板已内置 `vue-tsc` 类型检查。
:::

## 创建 TypeScript 项目

```shell
npm create vue@latest my-app
```

交互式选择时勾选 TypeScript、Router、Pinia 即可。项目会包含：

```text
├─ tsconfig.app.json      # 应用代码类型检查
├─ tsconfig.node.json     # vite.config 等 Node 环境代码
├─ env.d.ts               # *.vue 模块声明、vite/client 类型
└─ src/
   ├─ main.ts
   └─ App.vue
```

检查类型与构建：

```json [package.json]
{
  "scripts": {
    "type-check": "vue-tsc --build",
    "build": "run-p type-check \"build-only {@}\""
  }
}
```

## 组件 Props 类型化

```vue [UserCard.vue]
<script setup lang="ts">
interface User {
  id: number
  name: string
  email?: string
}

const props = defineProps<{
  user: User
  showAvatar?: boolean
}>()
</script>

<template>
  <div>
    <span>{{ props.user.name }}</span>
  </div>
</template>
```

带默认值（3.5+ 可直接解构）：

```vue
<script setup lang="ts">
const { showAvatar = true, size = "md" as "sm" | "md" | "lg" } = defineProps<{
  showAvatar?: boolean
  size?: "sm" | "md" | "lg"
}>()
</script>
```

## Emits 类型化

```vue
<script setup lang="ts">
const emit = defineEmits<{
  (e: "submit", payload: { name: string }): void
  (e: "cancel"): void
}>()
</script>
```

也可以用对象写法获得更好的可读性（Vue 3.3+）：

```ts
const emit = defineEmits<{
  submit: [payload: { name: string }]
  cancel: []
}>()
```

## ref / reactive / computed 泛型

```ts
import { computed, reactive, ref } from "vue"

const count = ref<number>(0)
const user = ref<User | null>(null)

const state = reactive<{ list: User[]; loading: boolean }>({
  list: [],
  loading: false,
})

const total = computed<number>(() => state.list.length)
```

`ref<User | null>(null)` 在模板里使用时需要判空：

```vue
<p v-if="user">{{ user.name }}</p>
```

## 模板 ref 类型化

给 DOM 或组件实例绑定类型：

```vue [App.vue]
<script setup lang="ts">
import { ref } from "vue"
import UserCard from "./UserCard.vue"

const inputEl = ref<HTMLInputElement | null>(null)
const cardRef = ref<InstanceType<typeof UserCard> | null>(null)

function focusInput() {
  inputEl.value?.focus()
}
</script>

<template>
  <input ref="inputEl" />
  <UserCard ref="cardRef" :user="{ id: 1, name: 'Codex' }" />
</template>
```

Vue 3.5+ 也可以用 `useTemplateRef`：

```ts
import { useTemplateRef } from "vue"
const inputEl = useTemplateRef<HTMLInputElement>("inputEl")
```

## provide / inject 类型化

```ts [keys.ts]
import type { InjectionKey, Ref } from "vue"

export const themeKey: InjectionKey<Ref<string>> = Symbol("theme")
```

```ts
import { inject, provide, ref } from "vue"
import { themeKey } from "./keys"

provide(themeKey, ref("dark"))

const theme = inject(themeKey, ref("light"))
```

## 环境声明

`env.d.ts` 声明 `*.vue` 模块（新项目模板已内置）：

```ts [env.d.ts]
/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue"
  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, unknown>
  export default component
}
```

## 常用类型工具

| 类型 | 用途 |
| --- | --- |
| `InstanceType<typeof Comp>` | 组件实例类型，用于模板 ref |
| `ComponentPublicInstance` | 通用组件实例 |
| `DefineComponent` | SFC 模块的默认导出类型 |
| `PropType<T>` | 选项式 API 中声明复杂 prop 类型 |
| `ExtractPropTypes` | 从 props 选项提取类型 |

## 易错点

::: danger 常见错误
1. 只装了 `typescript` 没装 `vue-tsc`，`npm run type-check` 找不到命令。
2. `defineProps` 用接口时，默认值必须用 `withDefaults`（3.5 之前）或响应式解构（3.5+），直接写默认值会报错。
3. `ref<HTMLInputElement | null>(null)` 忘记初始值 `null`，类型报错或运行时 undefined。
4. 在模板里直接 `user.name` 而 `user` 可能是 `null`，类型检查报错；应先用 `v-if` 或可选链（模板支持 `user?.name`）。
5. `tsconfig` 没启用 `"moduleResolution": "bundler"`，导入 `.vue` 和别名报错。
6. 把 `defineProps` 的返回值赋值给变量后直接修改，类型不报错但运行时修改无效。
:::

## 验证方式

1. `npm run type-check` 通过，无类型错误。
2. 故意把 prop 类型写错（如 `user.name` 传数字），编辑器与 `vue-tsc` 立即标红。
3. 模板 ref 使用 `instanceof` 或断点确认类型正确。
4. `npm run dev` 启动后页面渲染正常，控制台无 TS 相关警告。

## 参考资料

- Vue TypeScript 指南：https://cn.vuejs.org/guide/typescript/overview.html
- vue-tsc：https://github.com/vuejs/language-tools
- create-vue：https://github.com/vuejs/create-vue
- 组合式 API 类型推导：https://cn.vuejs.org/guide/typescript/composition-api.html
