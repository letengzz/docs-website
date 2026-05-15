# 计算属性

计算属性用于基于响应式依赖进行缓存计算。

## 基本用法

```html [basic.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>计算属性</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p>原始消息: {{ message }}</p>
    <p>反转消息: {{ reversedMessage }}</p>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      message: 'Hello'
    },
    computed: {
      reversedMessage() {
        return this.message.split('').reverse().join('')
      }
    },
    el: '#app'
  })
</script>
</html>
```

## 计算属性 vs 方法

```html [computed-vs-methods.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>计算属性 vs 方法</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p>计算属性: {{ reversedMessage }}</p>
    <p>计算属性: {{ reversedMessage }}</p>
    <p>方法: {{ reversedMessageMethod() }}</p>
    <p>方法: {{ reversedMessageMethod() }}</p>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      message: 'Hello'
    },
    computed: {
      reversedMessage() {
        console.log('计算属性被调用')
        return this.message.split('').reverse().join('')
      }
    },
    methods: {
      reversedMessageMethod() {
        console.log('方法被调用')
        return this.message.split('').reverse().join('')
      }
    },
    el: '#app'
  })
</script>
</html>
```

计算属性会基于依赖进行缓存，只有依赖变化时才会重新计算。

## 计算属性的 getter 和 setter

```html [getter-setter.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>计算属性的 getter 和 setter</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p>{{ fullName }}</p>
    <button @click="fullName = 'John Doe'">修改全名</button>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      firstName: 'John',
      lastName: 'Doe'
    },
    computed: {
      fullName: {
        get() {
          return this.firstName + ' ' + this.lastName
        },
        set(newValue) {
          const names = newValue.split(' ')
          this.firstName = names[0]
          this.lastName = names[names.length - 1]
        }
      }
    },
    el: '#app'
  })
</script>
</html>
```

## 计算属性缓存

```html [cache.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>计算属性缓存</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p>计算属性: {{ now }}</p>
    <p>方法: {{ getNow() }}</p>
    <button @click="counter++">触发更新 ({{ counter }})</button>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      counter: 0
    },
    computed: {
      now() {
        return Date.now()
      }
    },
    methods: {
      getNow() {
        return Date.now()
      }
    },
    el: '#app'
  })
</script>
</html>
```

::: tip 提示
- 计算属性基于依赖进行缓存
- 只有依赖变化时才会重新计算
- 适合复杂计算或需要缓存的场景
- 方法每次调用都会执行

:::
