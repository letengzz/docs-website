# VueComponent

## VueComponent 构造函数

每次注册组件时，Vue 都会创建一个 VueComponent 构造函数。

```html [vuecomponent.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>VueComponent</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <school-component></school-component>
    <student-component></student-component>
  </div>
</body>
<script>
  Vue.component('school-component', {
    template: '<div>学校组件</div>'
  })

  Vue.component('student-component', {
    template: '<div>学生组件</div>'
  })

  const vm = new Vue({
    el: '#app'
  })

  // 查看组件构造函数
  console.log(typeof schoolComponent) // function
  console.log(typeof studentComponent) // function
</script>
</html>
```

## VueComponent 与 Vue 实例的关系

```javascript [relationship.js]
// VueComponent 原型对象
console.log(SchoolComponent.prototype.__proto__ === Vue.prototype) // true

// 说明：
// 1. 组件的 prototype 的 __proto__ 指向 Vue 的 prototype
// 2. 这样组件可以访问 Vue 原型上的所有方法
// 3. 组件实例最终继承自 Vue 实例
```

## this 指向

```html [this-context.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>this 指向</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <my-component></my-component>
  </div>
</body>
<script>
  Vue.component('my-component', {
    data() {
      return {
        name: '组件数据'
      }
    },
    mounted() {
      console.log('组件中的 this:', this)
      console.log('this.$el:', this.$el)
      console.log('this.$data:', this.$data)
      console.log('this.$parent:', this.$parent)
    },
    template: '<p>{{ name }}</p>'
  })

  const vm = new Vue({
    el: '#app'
  })

  console.log('Vue实例中的 this:', vm)
</script>
</html>
```

## 组件原型链

```javascript [prototype-chain.js]
// 组件实例的原型链
// VueComponent.prototype -> Vue.prototype -> Object.prototype

// 组件实例可以访问：
// 1. VueComponent 原型上的方法
// 2. Vue 原型上的方法（$mount, $watch 等）
// 3. Object 原型上的方法

// 验证
console.log(SchoolComponent.prototype.__proto__ === Vue.prototype) // true
console.log(Vue.prototype.__proto__ === Object.prototype) // true
```

## 重要结论

1. **VueComponent 的实例对象**（组件实例对象）
2. **VueComponent.prototype.__proto__ === Vue.prototype**（组件的原型对象指向 Vue 的原型对象）
3. **组件实例对象可以访问 Vue 原型上的所有方法**

```javascript [conclusion.js]
// 组件中可以使用的 Vue 方法
this.$mount()      // 挂载
this.$watch()      // 侦听
this.$set()        // 设置响应式数据
this.$delete()     // 删除响应式数据
this.$nextTick()   // 等待 DOM 更新
this.$emit()       // 触发自定义事件
this.$refs         // 访问子组件或 DOM 元素
```

::: tip 提示
- 每次注册组件都会创建一个新的 VueComponent 构造函数
- VueComponent.prototype.__proto__ 指向 Vue.prototype
- 组件实例可以访问 Vue 原型上的所有方法
- 组件中的 this 指向组件实例
:::
