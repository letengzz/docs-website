# 自定义指令

Vue 允许你注册自定义指令，用于对普通 DOM 元素进行底层操作。

## 全局自定义指令

```html [global-directive.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>全局自定义指令</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <input v-focus>
  </div>
</body>
<script>
  // 注册全局指令
  Vue.directive('focus', {
    inserted(el) {
      el.focus()
    }
  })

  const vm = new Vue({
    el: '#app'
  })
</script>
</html>
```

## 局部自定义指令

```html [local-directive.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>局部自定义指令</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p v-highlight="'yellow'">高亮文本</p>
  </div>
</body>
<script>
  const vm = new Vue({
    el: '#app',
    directives: {
      highlight: {
        bind(el, binding) {
          el.style.backgroundColor = binding.value
        }
      }
    }
  })
</script>
</html>
```

## 指令钩子函数

指令定义可以提供几个钩子函数：

- `bind`: 只调用一次，指令第一次绑定到元素时调用
- `inserted`: 被绑定元素插入父节点时调用
- `update`: 所在组件的 VNode 更新时调用
- `componentUpdated`: 所在组件的 VNode 及其子 VNode 全部更新后调用
- `unbind`: 只调用一次，指令与元素解绑时调用

```html [hooks.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>指令钩子函数</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <div v-demo="{ color: 'red', text: 'Hello' }"></div>
  </div>
</body>
<script>
  Vue.directive('demo', {
    bind(el, binding, vnode) {
      console.log('bind 调用')
      el.style.color = binding.value.color
      el.textContent = binding.value.text
    },
    inserted(el) {
      console.log('inserted 调用')
    },
    update(el, binding) {
      console.log('update 调用')
      el.style.color = binding.value.color
    },
    componentUpdated(el) {
      console.log('componentUpdated 调用')
    },
    unbind(el) {
      console.log('unbind 调用')
    }
  })

  const vm = new Vue({
    el: '#app'
  })
</script>
</html>
```

## 指令简写

如果只需要 bind 和 update 钩子，可以使用函数简写：

```javascript [shorthand.js]
Vue.directive('color-swatch', function(el, binding) {
  el.style.backgroundColor = binding.value
})
```

## 指令参数

```html [directive-args.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>指令参数</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <div v-pin:[direction]="200">固定定位元素</div>
  </div>
</body>
<script>
  Vue.directive('pin', {
    bind(el, binding) {
      el.style.position = 'fixed'
      el.style[binding.arg] = binding.value + 'px'
    }
  })

  const vm = new Vue({
    data: {
      direction: 'top'
    },
    el: '#app'
  })
</script>
</html>
```

::: tip 提示
- 自定义指令用于底层 DOM 操作
- 全局指令使用 Vue.directive()
- 局部指令在 directives 选项中定义
- 钩子函数提供不同生命周期的操作点
:::
