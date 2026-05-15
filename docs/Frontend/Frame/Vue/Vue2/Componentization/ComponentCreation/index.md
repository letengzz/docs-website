# 组件创建、注册、使用

## 全局注册

```html [global-registration.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>全局注册</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <my-component></my-component>
    <my-component></my-component>
  </div>
</body>
<script>
  // 全局注册组件
  Vue.component('my-component', {
    data() {
      return {
        count: 0
      }
    },
    template: '<button @click="count++">点击了 {{ count }} 次</button>'
  })

  const vm = new Vue({
    el: '#app'
  })
</script>
</html>
```

## 局部注册

```html [local-registration.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>局部注册</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <my-component></my-component>
  </div>
</body>
<script>
  const MyComponent = {
    data() {
      return {
        message: 'Hello from component'
      }
    },
    template: '<p>{{ message }}</p>'
  }

  const vm = new Vue({
    el: '#app',
    components: {
      'my-component': MyComponent
    }
  })
</script>
</html>
```

## 组件 data 必须是函数

```javascript [data-function.js]
// 正确写法
Vue.component('my-component', {
  data() {
    return {
      count: 0
    }
  }
})

// 错误写法 - 数据会共享
Vue.component('my-component', {
  data: {
    count: 0
  }
})
```

## 组件通信 - Props

```html [props.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Props</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <child-component message="Hello" :count="5"></child-component>
  </div>
</body>
<script>
  Vue.component('child-component', {
    props: ['message', 'count'],
    template: '<p>{{ message }} - {{ count }}</p>'
  })

  const vm = new Vue({
    el: '#app'
  })
</script>
</html>
```

## Props 验证

```javascript [props-validation.js]
Vue.component('my-component', {
  props: {
    // 基础类型检查
    name: String,
    // 多种类型
    value: [String, Number],
    // 必填字符串
    title: {
      type: String,
      required: true
    },
    // 带默认值
    count: {
      type: Number,
      default: 0
    },
    // 对象默认值
    config: {
      type: Object,
      default() {
        return { theme: 'default' }
      }
    }
  }
})
```

## 组件通信 - 自定义事件

```html [custom-events.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>自定义事件</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <p>父组件收到: {{ message }}</p>
    <child-component @send-message="handleMessage"></child-component>
  </div>
</body>
<script>
  Vue.component('child-component', {
    template: '<button @click="sendMessage">发送消息</button>',
    methods: {
      sendMessage() {
        this.$emit('send-message', 'Hello from child')
      }
    }
  })

  const vm = new Vue({
    data: {
      message: ''
    },
    methods: {
      handleMessage(msg) {
        this.message = msg
      }
    },
    el: '#app'
  })
</script>
</html>
```

::: tip 提示
- 全局注册使用 Vue.component()
- 局部注册使用 components 选项
- 组件 data 必须是函数
- props 用于父传子
- 自定义事件用于子传父
:::
