# Vue3 实战案例

用一个可运行的「商品搜索 + 购物车」小项目，把前面学到的响应式、模板语法、组合式 API、路由、Pinia、组件通信串起来。整个项目约 6 个文件，可直接复制到 `create-vue` 项目中运行。

::: info 运行环境
Node.js 22+（LTS），`npm create vue@latest` 创建的 Vue 3.5 + Vite + TypeScript + Router + Pinia 项目。
:::

## 功能设计

| 页面 | 功能 |
| --- | --- |
| 首页 `/` | 展示商品列表，支持关键词搜索，加入购物车 |
| 购物车 `/cart` | 展示购物车明细、数量加减、清空、总价 |
| 详情 `/product/:id` | 展示单个商品详情（简单版） |

数据用本地模拟，方便验证；真实项目替换成接口请求即可。

## 1. 类型定义

```ts [src/types.ts]
export interface Product {
  id: number
  name: string
  price: number
  category: string
}

export interface CartItem extends Product {
  count: number
}
```

## 2. 模拟数据

```ts [src/mock.ts]
import type { Product } from "./types"

export const products: Product[] = [
  { id: 1, name: "机械键盘", price: 299, category: "外设" },
  { id: 2, name: "无线鼠标", price: 129, category: "外设" },
  { id: 3, name: "27 寸显示器", price: 1299, category: "显示" },
  { id: 4, name: "人体工学椅", price: 899, category: "家具" },
]
```

## 3. 购物车 Store

```ts [src/stores/cart.ts]
import { computed, ref } from "vue"
import { defineStore } from "pinia"
import type { CartItem, Product } from "../types"

export const useCartStore = defineStore("cart", () => {
  const items = ref<CartItem[]>([])

  const totalCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.count, 0),
  )

  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.count, 0),
  )

  function add(product: Product) {
    const exist = items.value.find((item) => item.id === product.id)
    if (exist) {
      exist.count++
    } else {
      items.value.push({ ...product, count: 1 })
    }
  }

  function changeCount(id: number, delta: number) {
    const item = items.value.find((i) => i.id === id)
    if (!item) return
    item.count += delta
    if (item.count <= 0) {
      items.value = items.value.filter((i) => i.id !== id)
    }
  }

  function clear() {
    items.value = []
  }

  return { items, totalCount, totalPrice, add, changeCount, clear }
})
```

## 4. 商品列表 composable

```ts [src/composables/useProductList.ts]
import { computed, ref } from "vue"
import { products } from "../mock"

export function useProductList() {
  const keyword = ref("")
  const filtered = computed(() =>
    products.filter((p) => p.name.includes(keyword.value.trim())),
  )
  return { keyword, filtered }
}
```

## 5. 首页组件

```vue [src/views/Home.vue]
<script setup lang="ts">
import { useProductList } from "../composables/useProductList"
import { useCartStore } from "../stores/cart"

const { keyword, filtered } = useProductList()
const cartStore = useCartStore()
</script>

<template>
  <div>
    <h2>商品列表</h2>
    <input v-model.trim="keyword" placeholder="搜索商品名称" />
    <ul>
      <li v-for="product in filtered" :key="product.id">
        <RouterLink :to="`/product/${product.id}`">{{ product.name }}</RouterLink>
        <span>¥{{ product.price }}</span>
        <button @click="cartStore.add(product)">加入购物车</button>
      </li>
    </ul>
    <p>共 {{ filtered.length }} 件商品</p>
  </div>
</template>
```

## 6. 购物车组件

```vue [src/views/Cart.vue]
<script setup lang="ts">
import { storeToRefs } from "pinia"
import { useCartStore } from "../stores/cart"

const cartStore = useCartStore()
const { items, totalCount, totalPrice } = storeToRefs(cartStore)
</script>

<template>
  <h2>购物车（{{ totalCount }} 件）</h2>
  <table>
    <thead>
      <tr>
        <th>名称</th>
        <th>单价</th>
        <th>数量</th>
        <th>小计</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in items" :key="item.id">
        <td>{{ item.name }}</td>
        <td>¥{{ item.price }}</td>
        <td>
          <button @click="cartStore.changeCount(item.id, -1)">-</button>
          {{ item.count }}
          <button @click="cartStore.changeCount(item.id, 1)">+</button>
        </td>
        <td>¥{{ item.price * item.count }}</td>
      </tr>
    </tbody>
  </table>
  <p>合计：¥{{ totalPrice }}</p>
  <button @click="cartStore.clear()">清空</button>
</template>
```

## 7. 详情页与路由

```vue [src/views/ProductDetail.vue]
<script setup lang="ts">
import { computed } from "vue"
import { useRoute } from "vue-router"
import { products } from "../mock"

const route = useRoute()
const product = computed(() =>
  products.find((p) => p.id === Number(route.params.id)),
)
</script>

<template>
  <div v-if="product">
    <h2>{{ product.name }}</h2>
    <p>分类：{{ product.category }}，价格：¥{{ product.price }}</p>
  </div>
  <p v-else>商品不存在</p>
</template>
```

```ts [src/router/index.ts]
import { createRouter, createWebHistory } from "vue-router"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: () => import("../views/Home.vue") },
    { path: "/cart", name: "cart", component: () => import("../views/Cart.vue") },
    {
      path: "/product/:id",
      name: "product",
      component: () => import("../views/ProductDetail.vue"),
    },
  ],
})

export default router
```

## 8. 页面导航

```vue [src/App.vue]
<script setup lang="ts">
import { storeToRefs } from "pinia"
import { useCartStore } from "./stores/cart"

const cartStore = useCartStore()
const { totalCount } = storeToRefs(cartStore)
</script>

<template>
  <nav>
    <RouterLink to="/">首页</RouterLink>
    <RouterLink to="/cart">购物车（{{ totalCount }}）</RouterLink>
  </nav>
  <RouterView />
</template>
```

## 验证方式

1. `npm run dev` 启动，打开 http://localhost:5173/。
2. 搜索「键盘」，列表只剩机械键盘；清空搜索后恢复全部商品。
3. 点击「加入购物车」后，导航栏购物车数量 +1；重复加入同一商品只增加数量。
4. 进入购物车页，加减数量、小计和合计实时更新；减到 0 自动移除。
5. 点击商品名进入详情页，地址栏为 `/product/1`，刷新后页面正常。
6. `npm run type-check` 通过，`npm run build` 构建成功。

## 扩展思路

- 把 mock 换成真实接口（axios/fetch + loading 状态）。
- 给购物车加 `pinia-plugin-persistedstate`，刷新不丢数据。
- 用 `defineAsyncComponent` 懒加载详情页组件。
- 用组件库（Element Plus）替换原生表格和按钮，按需引入。

## 参考资料

- create-vue：https://github.com/vuejs/create-vue
- Vue Router 4：https://router.vuejs.org/zh/
- Pinia：https://pinia.vuejs.org/zh/
- Vite：https://cn.vitejs.dev/
