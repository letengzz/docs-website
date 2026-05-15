# 类和样式绑定

## class 绑定

### 对象语法

```html [class-object.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>class 绑定</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <div :class="{ active: isActive, 'text-danger': hasError }">
      内容
    </div>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      isActive: true,
      hasError: false
    },
    el: '#app'
  })
</script>
</html>
```

### 数组语法

```html [class-array.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>class 绑定</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <div :class="[activeClass, errorClass]">
      内容
    </div>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      activeClass: 'active',
      errorClass: 'text-danger'
    },
    el: '#app'
  })
</script>
</html>
```

## style 绑定

### 对象语法

```html [style-object.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>style 绑定</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <div :style="{ color: activeColor, fontSize: fontSize + 'px' }">
      内容
    </div>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      activeColor: 'red',
      fontSize: 30
    },
    el: '#app'
  })
</script>
</html>
```

### 数组语法

```html [style-array.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>style 绑定</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <div :style="[baseStyles, overridingStyles]">
      内容
    </div>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      baseStyles: {
        color: 'red',
        fontSize: '20px'
      },
      overridingStyles: {
        fontWeight: 'bold'
      }
    },
    el: '#app'
  })
</script>
</html>
```

::: tip 提示
- :class 和 :style 是 v-bind 的缩写
- 支持对象语法和数组语法
- 可以自动添加浏览器前缀

:::
