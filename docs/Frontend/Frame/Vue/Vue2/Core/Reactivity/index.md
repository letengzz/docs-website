# 响应式与数据劫持

Vue 2 使用 Object.defineProperty 实现响应式系统。

## 响应式原理

Vue 2 通过 Object.defineProperty 劫持数据的 getter 和 setter，实现数据变化时自动更新视图。

```javascript [reactive-principle.js]
// Vue 2 响应式原理简化版
function defineReactive(obj, key, val) {
  Object.defineProperty(obj, key, {
    get() {
      console.log('读取数据:', key)
      return val
    },
    set(newVal) {
      if (newVal !== val) {
        console.log('设置数据:', key, newVal)
        val = newVal
        // 触发视图更新
        updateView()
      }
    }
  })
}

function observe(obj) {
  if (typeof obj !== 'object' || obj === null) return
  
  Object.keys(obj).forEach(key => {
    defineReactive(obj, key, obj[key])
  })
}
```

## 数据劫持示例

```html [data-hijack.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>数据劫持</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p>{{ message }}</p>
    <button @click="message = '新消息'">更新</button>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      message: '初始消息'
    },
    el: '#app'
  })
</script>
</html>
```

## 响应式的限制

### 对象属性添加/删除

Vue 2 无法检测到对象属性的添加或删除。

```html [object-limitation.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>响应式限制</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p>{{ user.name }}</p>
    <p>{{ user.age || '未定义' }}</p>
    <button @click="addAge">添加 age 属性</button>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      user: {
        name: '张三'
      }
    },
    methods: {
      addAge() {
        // 这种方式不会触发响应式更新
        // this.user.age = 18
        
        // 正确方式：使用 Vue.set
        this.$set(this.user, 'age', 18)
      }
    },
    el: '#app'
  })
</script>
</html>
```

### 数组索引修改

Vue 2 无法检测到通过索引直接设置数组项。

```html [array-limitation.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>数组响应式</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <ul>
      <li v-for="(item, index) in list" :key="index">
        {{ item }}
      </li>
    </ul>
    <button @click="updateItem">更新第一项</button>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      list: ['苹果', '香蕉', '橙子']
    },
    methods: {
      updateItem() {
        // 这种方式不会触发响应式更新
        // this.list[0] = '葡萄'
        
        // 正确方式 1：使用 Vue.set
        this.$set(this.list, 0, '葡萄')
        
        // 正确方式 2：使用 splice
        // this.list.splice(0, 1, '葡萄')
      }
    },
    el: '#app'
  })
</script>
</html>
```

## Vue.set / this.$set

用于向响应式对象添加属性或修改数组项。

```javascript [vue-set.js]
// 语法
Vue.set(target, key, value)
// 或
this.$set(target, key, value)

// 示例
this.$set(this.user, 'age', 18)
this.$set(this.list, 0, '新值')
```

## Vue.delete / this.$delete

用于删除响应式对象的属性。

```javascript [vue-delete.js]
// 语法
Vue.delete(target, key)
// 或
this.$delete(target, key)

// 示例
this.$delete(this.user, 'age')
```

## 异步更新队列

Vue 异步执行 DOM 更新。使用 `this.$nextTick` 等待 DOM 更新完成。

```html [next-tick.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>异步更新</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p ref="message">{{ message }}</p>
    <button @click="updateMessage">更新并获取 DOM</button>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      message: '初始消息'
    },
    methods: {
      updateMessage() {
        this.message = '新消息'
        // DOM 还未更新
        console.log(this.$refs.message.textContent) // 初始消息
        
        // 等待 DOM 更新后执行
        this.$nextTick(() => {
          console.log(this.$refs.message.textContent) // 新消息
        })
      }
    },
    el: '#app'
  })
</script>
</html>
```

::: danger 注意事项
- Vue 2 无法检测对象属性的添加/删除
- Vue 2 无法检测通过索引直接修改数组
- 必须使用 Vue.set 或 this.$set 来添加新属性
- 必须使用 splice 或 Vue.set 来修改数组项
:::

::: tip 提示
- Vue 3 使用 Proxy 解决了这些限制
- 对于复杂数据结构，考虑使用 Vue 3
- $nextTick 用于等待 DOM 更新完成
:::
