# 内置指令

**官方文档**：https://cn.vuejs.org/api/built-in-directives.html

## 核心语法

**指令的语法格式**： `<标签 v-指令名:参数="表达式"></标签>`

## 更新文本内容

可以使用差值语法：

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>第一个Vue程序</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <!-- 指定挂载位置 -->
    <div id="app">
        <div>
            <h1>{{name}}</h1>
            <h1>{{age}}</h1>
        </div>
    </div>
</body>
<script>
    const vm = new Vue({
        data: {
            name: '张三',
            age: 18
        },
        el: '#app'
    })
</script>

</html>
```

也可以使用`v-text`更新文本内容：

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
        <div>
            <h1 v-text="name"></h1>
            <h1 v-text="age"></h1>
        </div>
    </div>
</body>
<script>
    const vm = new Vue({
        data: {
            name: '张三',
            age: 18
        },
        el: '#app'
    })
</script>

</html>
```

## 更新元素

使用`v-html`更新元素：

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
        <div>
            <h1 v-text="html"></h1>
            <h1 v-html="html"></h1>
        </div>
    </div>
</body>
<script>
    const vm = new Vue({
        data: {
            html: "<p style='color:red'>你好</p>",
        },
        el: '#app'
    })
</script>

</html>
```

