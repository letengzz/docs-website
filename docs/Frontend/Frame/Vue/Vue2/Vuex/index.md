# Vuex

Vuex 是 Vue.js 的状态管理模式。

- 官方文档：https://vuex.vuejs.org/zh/

## 安装

```bash
npm install vuex@3
```

## 基本使用

```javascript [store.js]
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    count: 0
  },
  mutations: {
    increment(state) {
      state.count++
    }
  }
})

export default store
```

```javascript [main.js]
import Vue from 'vue'
import App from './App.vue'
import store from './store'

new Vue({
  store,
  render: h => h(App)
}).$mount('#app')
```

## State

```html [state.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Vuex State</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vuex@3/dist/vuex.js"></script>
</head>
<body>
  <div id="app">
    <p>{{ $store.state.count }}</p>
  </div>
</body>
<script>
  const store = new Vuex.Store({
    state: {
      count: 0
    }
  })

  const vm = new Vue({
    store,
    el: '#app'
  })
</script>
</html>
```

## Getters

```html [getters.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Vuex Getters</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vuex@3/dist/vuex.js"></script>
</head>
<body>
  <div id="app">
    <p>偶数: {{ $store.getters.evenCount }}</p>
  </div>
</body>
<script>
  const store = new Vuex.Store({
    state: {
      count: 0
    },
    getters: {
      evenCount(state) {
        return state.count % 2 === 0
      }
    }
  })

  const vm = new Vue({
    store,
    el: '#app'
  })
</script>
</html>
```

## Mutations

```html [mutations.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Vuex Mutations</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vuex@3/dist/vuex.js"></script>
</head>
<body>
  <div id="app">
    <p>{{ $store.state.count }}</p>
    <button @click="increment">增加</button>
  </div>
</body>
<script>
  const store = new Vuex.Store({
    state: {
      count: 0
    },
    mutations: {
      increment(state, payload) {
        state.count += payload.amount
      }
    }
  })

  const vm = new Vue({
    store,
    methods: {
      increment() {
        this.$store.commit('increment', { amount: 10 })
      }
    },
    el: '#app'
  })
</script>
</html>
```

## Actions

```html [actions.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Vuex Actions</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vuex@3/dist/vuex.js"></script>
</head>
<body>
  <div id="app">
    <p>{{ $store.state.count }}</p>
    <button @click="incrementAsync">异步增加</button>
  </div>
</body>
<script>
  const store = new Vuex.Store({
    state: {
      count: 0
    },
    mutations: {
      increment(state) {
        state.count++
      }
    },
    actions: {
      incrementAsync(context) {
        setTimeout(() => {
          context.commit('increment')
        }, 1000)
      }
    }
  })

  const vm = new Vue({
    store,
    methods: {
      incrementAsync() {
        this.$store.dispatch('incrementAsync')
      }
    },
    el: '#app'
  })
</script>
</html>
```

## Modules

```javascript [modules.js]
const moduleA = {
  state: { count: 0 },
  mutations: {
    increment(state) {
      state.count++
    }
  }
}

const moduleB = {
  state: { message: 'Hello' }
}

const store = new Vuex.Store({
  modules: {
    a: moduleA,
    b: moduleB
  }
})

// 访问状态
store.state.a.count    // 0
store.state.b.message  // 'Hello'
```

::: tip 提示
- Vuex 3 对应 Vue 2
- Vuex 5 (Pinia) 对应 Vue 3
- state 存储状态
- mutations 同步修改状态
- actions 异步操作
- getters 计算属性
:::
