# 侦听属性

watch 选项允许我们监听 Vue 实例上的数据变化，并在变化时执行相应的操作。

## 基本用法

```html [basic.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>侦听属性</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <input v-model="message">
    <p>{{ answer }}</p>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      message: '',
      answer: ''
    },
    watch: {
      message(newVal, oldVal) {
        this.answer = '你输入了: ' + newVal
      }
    },
    el: '#app'
  })
</script>
</html>
```

## 深度监听

```html [deep.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>深度监听</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <input v-model="user.name">
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      user: {
        name: '张三'
      }
    },
    watch: {
      user: {
        handler(newVal) {
          console.log('user 变化了:', newVal)
        },
        deep: true
      }
    },
    el: '#app'
  })
</script>
</html>
```

## 立即执行

```html [immediate.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>立即执行</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p>{{ result }}</p>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      message: 'Hello',
      result: ''
    },
    watch: {
      message: {
        handler(newVal) {
          this.result = newVal.toUpperCase()
        },
        immediate: true
      }
    },
    el: '#app'
  })
</script>
</html>
```

::: tip 提示
- watch 用于监听数据变化
- deep: true 用于深度监听对象
- immediate: true 用于立即执行一次
:::
