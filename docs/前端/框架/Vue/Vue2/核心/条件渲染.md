# 条件渲染

## 判断指令

### v-if

`v-if` 指令用于条件性地渲染一块内容。这块内容只会在指令的表达式返回真值时才被渲染。

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue程序</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <!-- 指定挂载位置 -->
    <div id="app">
        <br>
          温度：<input type="number" v-model="temprature"></br>
          天气：
          <span v-if="temprature <= 10">寒冷</span>
          <span v-if="temprature > 10 && temprature <= 25">凉爽</span>
          <span v-if="temprature > 25">炎热</span>
        </div>
    </div>
</body>
<script>

    const vm = new Vue({
        data: {
            temprature: 10
        },
        el: '#app'
    })
</script>

</html>
```

![image-20240620222833318](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406202228738.png)

### v-else

使用 `v-else` 为 `v-if` 添加一个"else 区块"

**注意**：一个 `v-else` 元素必须跟在一个 `v-if` 或者 `v-else-if` 元素后面，否则它将不会被识别。

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue程序</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <!-- 指定挂载位置 -->
    <div id="app">
        <br>
          温度：<input type="number" v-model="temprature"></br>
          天气：
          <span v-if="temprature <= 10">寒冷</span>
          <span v-else="temprature > 10 && temprature <= 25">凉爽</span>
        </div>
    </div>
</body>
<script>

    const vm = new Vue({
        data: {
            temprature: 10
        },
        el: '#app'
    })
</script>

</html>
```

### v-else-if

`v-else-if` 提供的是相应于 `v-if` 的"else if 区块"。它可以连续多次重复使用：

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue程序</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <!-- 指定挂载位置 -->
    <div id="app">
        <br>
          温度：<input type="number" v-model="temprature"></br>
          天气：
          <span v-if="temprature <= 10">寒冷</span>
          <span v-else-if="temprature > 10 && temprature <= 25">凉爽</span>
          <span v-else-if="temprature > 25">炎热</span>
        </div>
    </div>
</body>
<script>

    const vm = new Vue({
        data: {
            temprature: 10
        },
        el: '#app'
    })
</script>

</html>
```

### v-if与template

因为 `v-if` 是一个指令，他必须依附于某个元素。但如果我们想要切换不止一个元素呢？在这种情况下我们可以在一个 `<template>` 元素上使用 `v-if`，这只是一个不可见的包装器元素，最后渲染的结果并不会包含这个 `<template>` 元素。

`v-else` 和 `v-else-if` 也可以在 `<template>` 上使用。

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue程序</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <!-- 指定挂载位置 -->
    <div id="app">
        <br>
        温度：<input type="number" v-model="temprature"></br>
        天气：
        <template v-if="temprature <= 10">
            <span>寒冷</span>
        </template>
        <template v-else-if="temprature > 10 && temprature <= 25">
            <span>凉爽</span>
        </template>
        <template v-else-if="temprature > 25">
            <span>炎热</span>
        </template>
    </div>
    </div>
</body>
<script>

    const vm = new Vue({
        data: {
            temprature: 10
        },
        el: '#app'
    })
</script>

</html>
```

### v-show

按条件显示一个元素的指令是 `v-show`。 `v-show` 会在 DOM 渲染中保留该元素；`v-show` 仅切换了该元素上名为 `display` 的 CSS 属性。

`v-show` 不支持在 `<template>` 元素上使用，也不能和 `v-else` 搭配使用。

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue程序</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <!-- 指定挂载位置 -->
    <div id="app">
        <br>
          温度：<input type="number" v-model="temprature"></br>
          天气：
          <span v-show="temprature <= 10">寒冷</span>
          <span v-show="temprature > 10 && temprature <= 25">凉爽</span>
          <span v-show="temprature > 25">炎热</span>
        </div>
    </div>
</body>
<script>

    const vm = new Vue({
        data: {
            temprature: 10
        },
        el: '#app'
    })
</script>

</html>
```

![image-20240620223708926](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406202237653.png)

### v-if与v-show

- `v-if` 是"真实的"按条件渲染，因为它确保了在切换时，条件区块内的事件监听器和子组件都会被销毁与重建。

  `v-if` 也是**惰性**的：如果在初次渲染时条件值为 false，则不会做任何事。条件区块只有当条件首次变为 true 时才被渲染。

- 相比`v-if`，`v-show` 简单许多，元素无论初始条件如何，始终会被渲染，只有 CSS `display` 属性会被切换。

总的来说，`v-if` 有更高的切换开销，而 `v-show` 有更高的初始渲染开销。因此，如果需要频繁切换，则使用 `v-show` 较好；如果在运行时绑定条件很少改变，则 `v-if` 会更合适。