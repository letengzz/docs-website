# Vue3 响应式原理

响应式（Reactivity）是 Vue 的核心引擎：数据变化时，依赖它的界面和副作用函数会自动更新。本节从 `Proxy` 出发，讲清 `reactive`、`ref`、`computed`、`watch` 背后的依赖收集与触发机制。

::: info 适用版本
本节基于 Vue 3.5.x（当前稳定版，最新补丁 3.5.40）。Vue 3 的响应式系统基于 ES6 `Proxy`，不再依赖 Vue 2 的 `Object.defineProperty`。
:::

## 从 Vue2 到 Vue3：为什么换掉 defineProperty

Vue 2 使用 `Object.defineProperty` 拦截属性的读写，存在三个硬伤：

1. **只能拦截已有属性**：新增、删除属性不会触发更新，必须用 `Vue.set` / `Vue.delete` 补救。
2. **无法监听数组索引和长度变化**：`arr[0] = x`、`arr.length = 0` 失效。
3. **需要递归遍历对象**：初始化时一次性递归拦截，深层对象开销大。

Vue 3 改用 `Proxy` 代理整个对象，新增/删除属性、数组方法、动态下标都能被捕获，且支持惰性代理（访问到哪一层才代理哪一层）。

## 三个核心概念

| 概念 | 作用 | 对应代码 |
| --- | --- | --- |
| 响应式对象 | 被代理的数据，读写会被拦截 | `reactive(obj)` / `ref(value)` |
| 副作用函数 | 依赖数据、需要自动重跑的函数 | 渲染函数、`computed`、`watchEffect` |
| 依赖关系 | 数据 → 副作用函数的映射 | `track()` 收集、`trigger()` 触发 |

一句话流程：

```text
读取数据（get）→ 收集当前副作用 → 修改数据（set）→ 触发所有收集到的副作用
```

## track 与 trigger：依赖收集的核心

Vue 内部维护一个全局的「当前副作用」标记，配合 `WeakMap` 存储依赖：

```ts [reactive-core.ts]
type Dep = Set<ReactiveEffect>
// target -> key -> effects
const targetMap = new WeakMap<object, Map<PropertyKey, Dep>>()

let activeEffect: ReactiveEffect | undefined

function track(target: object, key: PropertyKey) {
  if (!activeEffect) return
  let depsMap = targetMap.get(target)
  if (!depsMap) {
    depsMap = new Map()
    targetMap.set(target, depsMap)
  }
  let dep = depsMap.get(key)
  if (!dep) {
    dep = new Set()
    depsMap.set(key, dep)
  }
  dep.add(activeEffect)
}

function trigger(target: object, key: PropertyKey) {
  const depsMap = targetMap.get(target)
  if (!depsMap) return
  const dep = depsMap.get(key)
  dep?.forEach((effect) => effect.run())
}
```

这是 Vue 响应式的最小骨架：`track` 在 get 时把「当前正在执行的副作用」记到数据名下，`trigger` 在 set 时把这些副作用重新执行。

## reactive 的实现

`reactive` 返回一个 `Proxy`，在 get 中收集依赖、在 set 中触发更新：

```ts [reactive.ts]
function reactive<T extends object>(target: T): T {
  return new Proxy(target, {
    get(target, key, receiver) {
      const value = Reflect.get(target, key, receiver)
      track(target, key)
      // 访问到对象时惰性代理
      if (value && typeof value === "object") {
        return reactive(value)
      }
      return value
    },
    set(target, key, value, receiver) {
      const oldValue = Reflect.get(target, key, receiver)
      const result = Reflect.set(target, key, value, receiver)
      if (oldValue !== value) {
        trigger(target, key)
      }
      return result
    },
    deleteProperty(target, key) {
      const hadKey = Reflect.has(target, key)
      const result = Reflect.deleteProperty(target, key)
      if (hadKey) trigger(target, key)
      return result
    },
  })
}
```

注意点：

- 用 `Reflect.get/set` 保持 `this` 指向代理对象，避免嵌套 getter 漏收集。
- 先比较新旧值再触发，避免无意义的重复渲染。
- 数组的 `push`、`splice` 等会触发多个 key 的 set，Vue 对 `length` 等做了特殊处理。

## ref 的实现

`ref` 把一个基本类型值包装成 `{ value }` 对象，getter 收集、setter 触发：

```ts [ref.ts]
class RefImpl<T> {
  private _value: T

  constructor(value: T) {
    this._value = toReactive(value)
  }

  get value() {
    track(this, "value")
    return this._value
  }

  set value(newValue) {
    if (newValue !== this._value) {
      this._value = toReactive(newValue)
      trigger(this, "value")
    }
  }
}

function ref<T>(value: T) {
  return new RefImpl(value)
}
```

`ref` 传对象时内部会调用 `reactive` 转换，所以 `ref({})` 的 `.value` 本身也是响应式对象。模板中 `ref` 会自动解包，脚本里必须写 `.value`。

## 依赖清理与调度器

真实实现比上面的骨架多了两件事：

1. **依赖清理**：副作用每次执行前清空旧依赖，避免 `if` 分支切换后残留过期依赖。
2. **调度器（scheduler）**：多次修改数据不会立刻同步执行所有副作用，而是把任务放入队列，通过微任务批量刷新，最后再走 `nextTick` 后的 DOM 更新。

这就是为什么连续修改同一个数据，页面只更新一次：

```ts
count.value++
count.value++
count.value++
// 只会触发一次重新渲染
```

## computed 与 watch 如何工作

- `computed`：内部创建 `ref`，getter 作为副作用执行；依赖变化时标记「脏」，下次读取时重算。
- `watch`：通过响应式系统读取源数据，变化时把回调放入调度队列，支持 `flush: "pre" | "post" | "sync"` 控制时机。
- `watchEffect`：立即执行一次副作用并自动收集依赖，类似 `watch` + 默认 `immediate`。

## 易错点

::: danger 常见错误
1. 从 `reactive` 对象解构出基本类型变量，会丢失响应式；要解构用 `toRefs` 或直接改用 `ref`。
2. 把 `reactive` 对象整体重新赋值（`state = newObj`），代理关系丢失；应修改对象内部属性或用 `Object.assign(state, newObj)`。
3. 用 `reactive(new Map())` 后直接 `map.set(...)`：Vue 3 支持 Map/Set 的响应式，但必须通过代理实例调用，重新赋值内部引用（如 `map = new Map()`）同样会失效。
4. 在 `watch` 回调里读取大量数据却没有显式收集依赖，导致更新不完整；监听来源应明确列出。
5. 以为 `ref` 是「非响应式」的普通对象，忘记 `.value`，模板显示正常但脚本里拿到的是包装对象。
:::

## 验证方式

1. 在组件里创建 `reactive` 对象并渲染，打开 Vue DevTools 的 Components 面板，修改数据后确认值同步变化。
2. 用 `watchEffect` 打印依赖：

```vue [App.vue]
<script setup>
import { reactive, watchEffect } from "vue"

const state = reactive({ count: 0 })

watchEffect(() => {
  console.log("count 变化为：", state.count)
})

setTimeout(() => {
  state.count++
}, 1000)
</script>
```

3. 运行后控制台先输出一次 `count 变化为：0`，1 秒后再输出 `count 变化为：1`，证明依赖收集与触发链路正常。
4. 尝试在模板中连续点击按钮三次，确认渲染只合并刷新（Performance 面板里没有三次完整渲染）。

## 参考资料

- Vue 官方响应式指南：https://cn.vuejs.org/guide/extras/reactivity-in-depth.html
- Vue 响应式 API：https://cn.vuejs.org/api/reactivity-core.html
- Vue 源码（vuejs/core）：https://github.com/vuejs/core/tree/main/packages/reactivity
- MDN Proxy：https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Proxy
