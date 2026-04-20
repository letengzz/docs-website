# 封装 Pinia

作为 Vue3 的官方状态管理库，与 Vuex 相比，Pinia 具有：

- 更简洁的 API。
- 更好的 TypeScript 支持。
- 更灵活的组合式 API 风格。

封装 Pinia 只需两步：

1. 创建 Pinia 实例，并配置持久化插件。
2. 将 Pinia 实例注册到 Vue 应用中。

## 安装依赖

项目创建时已默认安装了 Pinia 核心依赖，只需添加状态持久化插件，使用该插件会自动将 Pinia 中的状态持久化到本地存储，避免页面刷新后状态丢失的问题。

添加状态持久化插件：

```shell
pnpm add pinia-plugin-persistedstate
```

## 封装 Pinia

在 `src/stores`目录下创建 `index.ts`文件，实现 Pinia 的封装和模块化注册：

```typescript [src/stores/index.ts]
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import type { App } from 'vue'

// 创建 Pinia 实例
const pinia = createPinia()

// 添加持久化插件
// 该插件会自动将状态保存到 localStorage，默认 key 为 store 名称
pinia.use(piniaPluginPersistedstate)

/**
 * 安装 Pinia
 * @paramapp Vue 应用实例
 * 采用模块化方法注册 Pinia
 */
export const useStore = (app: App) => {
  app.use(pinia)
}

export default pinia
```

在 `main.ts`中调用 `useStore`方法注册 Pinia：

```typescript [src/main.ts]
import { createApp } from 'vue'

import App from './App.vue'
import { useRouter } from '@/router'
import { useStore } from './stores' // [!code focus] [!code highlight]

const app = createApp(App)
useRouter(app)
useStore(app) // [!code focus] [!code highlight]
app.mount('#app')
```

## 测试 Pinia

为了验证 Pinia 及持久化插件的配置效果，创建一个测试 store：

1. 在 `stores`目录下创建 `modules`子目录，用于组织不同业务模块的 store。

2. 在 `modules`中创建 `demo.ts`文件：

   ```typescript [src/stores/modules/demo.ts]
   import { defineStore } from 'pinia'
   import { ref } from 'vue'
   
   /**
    * 测试用的 Pinia Store
    * 使用组合式 API 风格编写，与 Vue3 的组合式 API 保持一致
    */
   export const useDemoStore = defineStore(
   'demoStore',// Store 唯一标识
   ()=>{
     // 状态定义
     const counter = ref<number>(0)
   
     // Action 定义（修改状态的方法）
     const increment = () => {
       counter.value++
     }
   
     // 返回需要暴露的状态和方法
     return{
       counter,
       increment,
     }
   },
   {
     persist:true,// 开启状态持久化
   },
   )
   ```

**代码说明**：

- 使用组合式 API 风格编写 Store，与 Vue3 的组合式 API  setup 保持一致的风格。
- 通过 `persist: true`开启状态持久化，默认会将状态保存到 localStorage 中，可自定义状态保存的方式。
- 模块化组织 Store 文件 main.ts 的代码显得条理清晰。

在 `demo.vue`中添加测试代码，验证 Pinia 功能：

```vue [src/views/demo.vue]
<template>
  <div class="demo">
  <h2>Pinia 测试</h2>
  <h3>计数器: {{ counter }}</h3>
  <button @click="demoStore.increment()"> 点击+1 </button>
  </div>
</template>

<script setup lang="ts">
import { useDemoStore } from '@/stores/modules/demo'
import { storeToRefs } from 'pinia'

// 初始化 Store 实例
const demoStore = useDemoStore()

// 使用 storeToRefs 解构状态，保持响应性
const { counter } = storeToRefs(demoStore)
</script>
```

**测试步骤**：

1. 启动项目并在浏览题访问 demo 页面
2. 界面显示的计数默认为 0
3. 点击按钮，计数器值会+1
4. 刷新页面，计数器值保持不变，刷新前是多少，刷新后依旧是多少（测试持久化功能）
5. 将 `persist`设置为 `false`，再次刷新页面，计数器会重置为 0

Pinia 及持久化插件已正确配置，可以正常管理和持久化应用状态。
