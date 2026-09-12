# 配置VueRequest

VueRequest 是面向 Vue 3 的请求库（基于 Hooks 思路），解决"请求状态管理"这件重复且易错的事：**加载中、错误、重试、取消、防抖**都由它统一处理，页面只关心数据。

::: tip 与网络请求封装的分工
[自定义配置网络请求](../Http/index.md) 负责"怎么发请求"（实例、拦截器、鉴权、错误码）；VueRequest 负责"请求在页面上的状态"。两者配合，而不是互相替代。
:::

## 一、安装

```shell
pnpm add vue-request
```

## 二、基础用法

```vue [src/views/user/UserList.vue]
<script setup lang="ts">
import { useRequest } from 'vue-request'
import { getUserList } from '@/api/user'

const {
  data,        // 请求成功的数据
  loading,     // 是否加载中
  error,       // 错误对象
  run,         // 手动触发（带参数）
  refresh,     // 用上次参数重新请求
} = useRequest(getUserList, {
  defaultParams: [{ page: 1, size: 20 }],   // 初始参数，自动发起请求
  manual: false,                            // false = 自动请求
})
</script>

<template>
  <div v-if="loading">加载中...</div>
  <div v-else-if="error">加载失败：{{ error.message }}</div>
  <ul v-else>
    <li v-for="item in data?.list ?? []" :key="item.id">{{ item.name }}</li>
  </ul>
  <button @click="refresh()">刷新</button>
  <button @click="run({ page: 2, size: 20 })">第二页</button>
</template>
```

## 三、常用配置

| 配置项 | 作用 | 建议 |
| --- | --- | --- |
| `manual` | 是否手动触发 | 查询表单场景用 `true` |
| `defaultParams` | 默认参数 | 显式写出分页初始值 |
| `refreshDeps` | 依赖变化时自动重新请求 | 查询条件变化时使用 |
| `debounceInterval` | 防抖间隔（ms） | 搜索框建议 300~500 |
| `throttleInterval` | 节流间隔（ms） | 滚动加载场景 |
| `cacheKey` | 缓存键 | 可缓存的下拉字典 |
| `onSuccess` / `onError` | 成功/失败回调 | 统一做提示与埋点 |

```ts [配合查询条件的写法]
import { ref } from 'vue'
import { useRequest } from 'vue-request'
import { getOrderList } from '@/api/order'

const keyword = ref('')
const { data, loading, run } = useRequest(getOrderList, {
  manual: true,
  debounceInterval: 400,
})

function handleSearch() {
  run({ keyword: keyword.value, page: 1, size: 20 })
}
```

## 四、与分页表格配合

在 [组件库集成](../ComponentLibrary/index.md) 里的 `ProTable` 接收的就是一个"请求函数"，可以直接把 `useRequest` 的 `run` 包一层传进去，形成「请求库 + 组件库」的组合：

```ts
const { run: fetchPage } = useRequest(getOrderList, { manual: true })

const request = ({ page, size }: { page: number; size: number }) =>
  fetchPage({ page, size }) as Promise<{ list: any[]; total: number }>
```

## 五、易错点

::: danger 使用 VueRequest 的四个坑
1. **`manual` 与 `defaultParams` 组合记反**：想自动请求却写了 `manual: true`，页面永远空白。
2. **在 `refreshDeps` 中放对象**：对象引用每次变化都会触发请求，应放基础类型或使用 `ref` 的 `.value`。
3. **忽略 `error` 分支**：请求失败时页面无提示，用户体验差且难以排查。
4. **把业务副作用写进组件**：成功后的统一提示、埋点建议放 `onSuccess`，避免每个页面重复。
:::

## 验证方式

1. 页面首次进入自动加载数据，`loading` 期间展示加载态。
2. 点击刷新与切换页码，确认参数正确且请求次数符合预期（用 Network 面板核对）。
3. 手动把接口改成 500，确认页面显示错误提示而不是白屏。
4. 在搜索框快速输入 5 个字符，确认只发出 1 次请求（防抖生效）。

## 参考资料

- VueRequest 官方文档：https://www.attojs.com/
- 本模块相关：[网络请求封装](../Http/index.md)、[组件库集成](../ComponentLibrary/index.md)
