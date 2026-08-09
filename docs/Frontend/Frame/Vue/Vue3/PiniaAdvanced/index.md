# Pinia 进阶

Pinia 是 Vue 官方推荐的集中式状态管理方案。基础篇解决了「怎么存、怎么取、怎么改」，进阶篇解决类型安全、组合式 store、插件、跨 store 协作与持久化。

::: info 适用版本
Pinia 当前稳定版为 3.x（2025 年 2 月发布 3.0，需 Vue 3）。Vuex 已进入维护模式，新项目默认使用 Pinia。
:::

## 组合式 Store（Setup Store）

基础篇用的是选项式写法（`state` / `getters` / `actions`），组合式写法更像 composable：

```ts [stores/cart.ts]
import { computed, ref } from "vue"
import { defineStore } from "pinia"

interface CartItem {
  id: number
  name: string
  price: number
  count: number
}

export const useCartStore = defineStore("cart", () => {
  const items = ref<CartItem[]>([])

  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.count, 0),
  )
  const totalCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.count, 0),
  )

  function addItem(item: Omit<CartItem, "count">) {
    const exist = items.value.find((i) => i.id === item.id)
    if (exist) {
      exist.count++
    } else {
      items.value.push({ ...item, count: 1 })
    }
  }

  function clear() {
    items.value = []
  }

  return { items, totalPrice, totalCount, addItem, clear }
})
```

组合式 store 中：

- `ref()` 相当于 `state`；
- `computed()` 相当于 `getters`；
- 普通函数相当于 `actions`；
- 返回的对象里 `ref` 会被自动解包（模板中直接用 `items`，脚本中仍要 `.value`）。

## TypeScript 类型推导

Pinia 的 store 类型完全由定义推导，无需额外写类型：

```ts [stores/user.ts]
export interface UserInfo {
  id: number
  name: string
  token: string
}

export const useUserStore = defineStore("user", {
  state: () => ({ user: null as UserInfo | null }),
  getters: {
    isLogin: (state) => state.user !== null,
  },
  actions: {
    setUser(user: UserInfo) {
      this.user = user
    },
    logout() {
      this.user = null
    },
  },
})
```

组件中使用：

```ts
import { storeToRefs } from "pinia"
import { useUserStore } from "@/stores/user"

const userStore = useUserStore()
const { user, isLogin } = storeToRefs(userStore)
```

`storeToRefs` 让解构出的 state/getters 保持响应式；`actions` 直接解构即可。

## 跨 Store 协作

一个 store 的 action 里调用另一个 store：

```ts [stores/order.ts]
import { useCartStore } from "./cart"
import { useUserStore } from "./user"

export const useOrderStore = defineStore("order", {
  actions: {
    async checkout() {
      const cartStore = useCartStore()
      const userStore = useUserStore()

      if (!userStore.isLogin) {
        throw new Error("请先登录")
      }

      const order = await api.createOrder({
        userId: userStore.user!.id,
        items: cartStore.items,
      })
      cartStore.clear()
      return order
    },
  },
})
```

## 订阅与监听

```ts
// 监听状态变化
cartStore.$subscribe(
  (mutation, state) => {
    console.log("变化类型：", mutation.type, "新状态：", state)
  },
  { detached: true }, // 组件卸载后仍继续订阅
)

// 监听 action 调用
cartStore.$onAction(({ name, args, after, onError }) => {
  console.log("调用 action：", name, args)
  after(() => console.log("完成"))
  onError((err) => console.error("失败", err))
})
```

## 插件与持久化

Pinia 插件在 store 创建时注入能力，最常见的用途是持久化：

```ts [plugins/persist.ts]
import { watch } from "vue"
import type { PiniaPluginContext } from "pinia"

export function persistPlugin({ store }: PiniaPluginContext) {
  const saved = localStorage.getItem(store.$id)
  if (saved) {
    store.$patch(JSON.parse(saved))
  }
  watch(
    () => JSON.stringify(store.$state),
    (value) => localStorage.setItem(store.$id, value),
  )
}
```

注册插件：

```ts [main.ts]
import { createPinia } from "pinia"
import { persistPlugin } from "./plugins/persist"

const pinia = createPinia()
pinia.use(persistPlugin)
app.use(pinia)
```

更省事的方式是使用社区维护的 `pinia-plugin-persistedstate`，支持按 store 配置需要持久化的字段。

## 与选项式 API 集成

选项式组件可以用映射辅助函数：

```vue
<script>
import { mapStores, mapState, mapActions } from "pinia"
import { useCartStore } from "@/stores/cart"

export default {
  computed: {
    ...mapStores(useCartStore),
    ...mapState(useCartStore, ["totalPrice", "totalCount"]),
  },
  methods: {
    ...mapActions(useCartStore, ["addItem", "clear"]),
  },
}
</script>
```

## 性能与最佳实践

1. 一个业务域一个 store，不要把所有状态塞进一个巨型 store。
2. 模板里尽量通过 `storeToRefs` 解构，避免整个 store 被依赖。
3. `$subscribe` 是深度监听，频率很高的状态建议只订阅需要的字段。
4. SSR 场景避免在模块顶层 `useStore()`，应在 `setup` 内调用。
5. 敏感信息（token）不要直接持久化到 localStorage，或至少加密并设置过期。

## 易错点

::: danger 常见错误
1. 直接解构 `store`：`const { items } = useCartStore()`，解构出的 `items` 丢失响应式；必须用 `storeToRefs`。
2. 在 store 外模块顶层调用 `useStore()` 导致 SSR/测试环境报错。
3. 组合式 store 返回了没有 `ref` 包裹的普通对象，状态变化不触发更新。
4. `$subscribe` 忘记 `{ detached: true }`，组件卸载后订阅被自动清理，与预期不符。
5. 持久化插件保存了整个 state，包含大对象和临时数据，性能差且容易踩到旧数据兼容问题。
6. 把 `pinia-plugin-persistedstate` 装到 Pinia 2 项目后不按 3.x 文档迁移，配置不生效。
:::

## 验证方式

1. 在组件里 `storeToRefs` 解构后修改 state，界面实时更新。
2. 打开 Vue DevTools 的 Pinia 面板，能看到 store、state、getters 和 action 调用记录。
3. 刷新页面后，持久化的购物车数据还在。
4. 未登录调用 `checkout()`，控制台抛出「请先登录」。

## 参考资料

- Pinia 官方文档：https://pinia.vuejs.org/zh/
- 组合式 Store：https://pinia.vuejs.org/zh/core-concepts/#setup-stores
- 插件：https://pinia.vuejs.org/zh/core-concepts/plugins.html
- pinia-plugin-persistedstate：https://github.com/prazdevs/pinia-plugin-persistedstate
