# 其他指令

## v-once 指令

v-once 指令使元素只渲染一次，之后不再更新。

```html [v-once.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>v-once 指令</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p v-once>{{ message }}</p>
    <p>{{ message }}</p>
    <button @click="message = '更新后的消息'">更新</button>
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

点击按钮后，第一个 `<p>` 不会更新，但第二个会更新。

## v-pre 指令

v-pre 指令跳过该元素及其子元素的编译，直接显示原始 Mustache 语法。

```html [v-pre.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>v-pre 指令</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p v-pre>{{ 这里不会被编译 }}</p>
    <p>{{ 这里会被编译 }}</p>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      '这里会被编译': '已编译内容'
    },
    el: '#app'
  })
</script>
</html>
```

## v-cloak 指令

v-cloak 指令用于隐藏未编译的 Mustache 标签，直到实例准备完毕。

```html [v-cloak.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>v-cloak 指令</title>
  <style>
    [v-cloak] {
      display: none;
    }
  </style>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app" v-cloak>
    <p>{{ message }}</p>
  </div>
</body>
<script>
  // 模拟延迟
  setTimeout(() => {
    const vm = new Vue({
      data: {
        message: 'Hello Vue!'
      },
      el: '#app'
    })
  }, 1000)
</script>
</html>
```

## v-bind 缩写

```html [v-bind-shortcut.html]
<div v-bind:id="dynamicId"></div>
<!-- 缩写为 -->
<div :id="dynamicId"></div>
```

## v-on 缩写

```html [v-on-shortcut.html]
<button v-on:click="doSomething"></button>
<!-- 缩写为 -->
<button @click="doSomething"></button>
```

::: tip 提示
- v-once 用于静态内容，提升性能
- v-pre 用于显示原始语法
- v-cloak 防止闪烁问题
- : 是 v-bind 的缩写
- @ 是 v-on 的缩写
:::
