# Uniapp 状态管理

## Vuex

### 安装

```bash [终端]
npm install vuex@4
```

### 创建 Store

```javascript [store/index.js]
import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    token: '',
    cart: []
  },

  getters: {
    isLoggedIn: (state) => !!state.token,
    cartCount: (state) => state.cart.length,
    cartTotal: (state) => state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
  },

  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
    },
    ADD_TO_CART(state, item) {
      const existing = state.cart.find(i => i.id === item.id)
      if (existing) {
        existing.quantity++
      } else {
        state.cart.push({ ...item, quantity: 1 })
      }
    },
    REMOVE_FROM_CART(state, id) {
      state.cart = state.cart.filter(item => item.id !== id)
    },
    CLEAR_CART(state) {
      state.cart = []
    }
  },

  actions: {
    async login({ commit }, { username, password }) {
      const res = await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      })
      const data = await res.json()
      commit('SET_USER', data.user)
      commit('SET_TOKEN', data.token)
      uni.setStorageSync('token', data.token)
    },

    async logout({ commit }) {
      commit('SET_USER', null)
      commit('SET_TOKEN', '')
      commit('CLEAR_CART')
      uni.removeStorageSync('token')
    },

    async addToCart({ commit }, item) {
      commit('ADD_TO_CART', item)
    }
  }
})
```

### 使用 Store

```vue [pages/index/index.vue]
<script setup>
import { useStore } from 'vuex'
import { computed } from 'vue'

const store = useStore()

const isLoggedIn = computed(() => store.getters.isLoggedIn)
const cartCount = computed(() => store.getters.cartCount)
const user = computed(() => store.state.user)

const handleLogin = () => {
  store.dispatch('login', {
    username: 'admin',
    password: '123456'
  })
}

const handleLogout = () => {
  store.dispatch('logout')
}
</script>

<template>
  <view>
    <view v-if="isLoggedIn">
      <text>欢迎，{{ user.name }}</text>
      <text>购物车：{{ cartCount }} 件</text>
      <button @click="handleLogout">退出登录</button>
    </view>
    <view v-else>
      <button @click="handleLogin">登录</button>
    </view>
  </view>
</template>
```

## Pinia

### 安装

```bash [终端]
npm install pinia
```

### 创建 Store

```javascript [store/user.js]
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref('')

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const res = await fetch('/api/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    })
    const data = await res.json()
    user.value = data.user
    token.value = data.token
    uni.setStorageSync('token', data.token)
  }

  function logout() {
    user.value = null
    token.value = ''
    uni.removeStorageSync('token')
  }

  return { user, token, isLoggedIn, login, logout }
})
```

```javascript [store/cart.js]
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  const count = computed(() => items.value.length)
  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  function addItem(item) {
    const existing = items.value.find(i => i.id === item.id)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ ...item, quantity: 1 })
    }
  }

  function removeItem(id) {
    items.value = items.value.filter(item => item.id !== id)
  }

  function clear() {
    items.value = []
  }

  return { items, count, total, addItem, removeItem, clear }
})
```

### 使用 Store

```vue [pages/cart/index.vue]
<script setup>
import { useCartStore } from '@/store/cart.js'

const cartStore = useCartStore()

const removeItem = (id) => {
  cartStore.removeItem(id)
}
</script>

<template>
  <view>
    <view v-for="item in cartStore.items" :key="item.id" class="cart-item">
      <text>{{ item.name }}</text>
      <text>¥{{ item.price }}</text>
      <text>x{{ item.quantity }}</text>
      <button @click="removeItem(item.id)">删除</button>
    </view>
    <view class="cart-footer">
      <text>总计：¥{{ cartStore.total }}</text>
    </view>
  </view>
</template>
```

## 全局数据

### 简单全局状态

```javascript [utils/global.js]
const globalData = {
  user: null,
  token: '',
  config: {}
}

export function getGlobalData() {
  return globalData
}

export function setGlobalData(key, value) {
  globalData[key] = value
}
```

### 使用全局数据

```vue
<script setup>
import { getGlobalData, setGlobalData } from '@/utils/global.js'

const globalData = getGlobalData()

const login = (user) => {
  setGlobalData('user', user)
  setGlobalData('token', user.token)
}
</script>
```

## 状态持久化

### 使用 Storage

```javascript [store/user.js]
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(uni.getStorageSync('user') || null)
  const token = ref(uni.getStorageSync('token') || '')

  const isLoggedIn = computed(() => !!token.value)

  function login(userData) {
    user.value = userData
    token.value = userData.token
    uni.setStorageSync('user', userData)
    uni.setStorageSync('token', userData.token)
  }

  function logout() {
    user.value = null
    token.value = ''
    uni.removeStorageSync('user')
    uni.removeStorageSync('token')
  }

  return { user, token, isLoggedIn, login, logout }
})
```

## 状态管理选型

| 方案 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| 全局变量 | 简单数据共享 | 简单直接 | 无响应式 |
| Vuex | 大型项目 | 生态成熟、DevTools | 模板代码多 |
| Pinia | 中小型项目 | API 简洁、TypeScript | 生态相对年轻 |

::: tip 推荐
新项目推荐使用 **Pinia**，API 更简洁，TypeScript 支持更好，Vue 官方推荐。
:::
