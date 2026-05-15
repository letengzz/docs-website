# Vue2 概述

Vue.js 是一套用于构建用户界面的渐进式框架。

- 官方网站：https://v2.cn.vuejs.org
- GitHub：https://github.com/vuejs/vue

## Vue 的特点

### 渐进式框架

Vue 被设计为可以自底向上逐层应用。

- 核心库只关注视图层
- 易于上手
- 便于与第三方库或既有项目整合

### 响应式数据

Vue 使用数据劫持结合发布者-订阅者模式实现数据的双向绑定。

```javascript [reactive.js]
const vm = new Vue({
  data: {
    message: 'Hello Vue'
  }
})

// 修改数据，视图自动更新
vm.message = 'Hello World'
```

### 组件化开发

Vue 允许将界面拆分为多个独立的组件。

```javascript [component.js]
Vue.component('my-button', {
  template: '<button>点击我</button>'
})
```

### 虚拟 DOM

Vue 使用虚拟 DOM 来提高渲染性能。

- 减少真实 DOM 操作
- 高效的 diff 算法
- 批量更新视图

## Vue 与其他框架对比

| 特性 | Vue | React | Angular |
|------|-----|-------|---------|
| 类型 | 渐进式框架 | UI 库 | 完整框架 |
| 数据绑定 | 双向绑定 | 单向数据流 | 双向绑定 |
| 模板 | HTML 模板 | JSX | HTML 模板 |
| 学习曲线 | 低 | 中 | 高 |
| 性能 | 高 | 高 | 中 |

## Vue 的版本

### Vue 2.x

- 使用 Object.defineProperty 实现响应式
- 支持 IE9+
- 选项式 API

### Vue 3.x

- 使用 Proxy 实现响应式
- 组合式 API
- 更好的 TypeScript 支持
- 更小的体积

## 安装方式

### CDN 引入

```html [cdn.html]
<!-- 开发环境版本 -->
<script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>

<!-- 生产环境版本 -->
<script src="https://fastly.jsdelivr.net/npm/vue@2"></script>
```

### npm 安装

```bash
npm install vue@2
```

### Vue CLI

```bash
npm install -g @vue/cli

vue create my-project
```

## 第一个 Vue 程序

```html [first-vue.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>第一个 Vue 程序</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    {{ message }}
  </div>

  <script>
    const vm = new Vue({
      el: '#app',
      data: {
        message: 'Hello Vue!'
      }
    })
  </script>
</body>
</html>
```

## Vue 实例

### 创建实例

```javascript [instance.js]
const vm = new Vue({
  // 选项
})
```

### 常用选项

```javascript [options.js]
const vm = new Vue({
  el: '#app',           // 挂载元素
  data: {},             // 数据
  methods: {},          // 方法
  computed: {},         // 计算属性
  watch: {},            // 侦听器
  components: {},       // 组件
  filters: {},          // 过滤器
  directives: {},       // 指令
  beforeCreate() {},    // 生命周期钩子
  created() {},
  beforeMount() {},
  mounted() {},
  beforeUpdate() {},
  updated() {},
  beforeDestroy() {},
  destroyed() {}
})
```

::: tip 提示
- Vue 2 是成熟的稳定版本
- 适合中小型项目快速开发
- 生态系统完善，社区活跃
- 学习成本低，易于上手
:::
