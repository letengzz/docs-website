# 组件嵌套

## 父子组件关系

```html [parent-child.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>组件嵌套</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <parent-component></parent-component>
  </div>
</body>
<script>
  // 子组件
  const ChildComponent = {
    template: '<p>我是子组件</p>'
  }

  // 父组件
  Vue.component('parent-component', {
    template: `
      <div>
        <h2>我是父组件</h2>
        <child-component></child-component>
      </div>
    `,
    components: {
      'child-component': ChildComponent
    }
  })

  const vm = new Vue({
    el: '#app'
  })
</script>
</html>
```

## 多层嵌套

```html [multi-level.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>多层嵌套</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <grandparent-component></grandparent-component>
  </div>
</body>
<script>
  // 孙子组件
  const GrandchildComponent = {
    template: '<p>我是孙子组件</p>'
  }

  // 子组件
  const ChildComponent = {
    template: `
      <div>
        <p>我是子组件</p>
        <grandchild-component></grandchild-component>
      </div>
    `,
    components: {
      'grandchild-component': GrandchildComponent
    }
  }

  // 父组件
  Vue.component('grandparent-component', {
    template: `
      <div>
        <h2>我是父组件</h2>
        <child-component></child-component>
      </div>
    `,
    components: {
      'child-component': ChildComponent
    }
  })

  const vm = new Vue({
    el: '#app'
  })
</script>
</html>
```

## 插槽（Slot）

```html [slot.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>插槽</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <my-component>
      <p>这是插入的内容</p>
    </my-component>
  </div>
</body>
<script>
  Vue.component('my-component', {
    template: `
      <div>
        <h2>组件标题</h2>
        <slot></slot>
      </div>
    `
  })

  const vm = new Vue({
    el: '#app'
  })
</script>
</html>
```

## 具名插槽

```html [named-slot.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>具名插槽</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <layout-component>
      <template v-slot:header>
        <h1>头部内容</h1>
      </template>
      <template v-slot:footer>
        <p>底部内容</p>
      </template>
    </layout-component>
  </div>
</body>
<script>
  Vue.component('layout-component', {
    template: `
      <div>
        <header>
          <slot name="header"></slot>
        </header>
        <main>
          <slot></slot>
        </main>
        <footer>
          <slot name="footer"></slot>
        </footer>
      </div>
    `
  })

  const vm = new Vue({
    el: '#app'
  })
</script>
</html>
```

## 作用域插槽

```html [scoped-slot.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>作用域插槽</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <list-component :items="users">
      <template v-slot:default="slotProps">
        <p>{{ slotProps.item.name }} - {{ slotProps.item.age }}</p>
      </template>
    </list-component>
  </div>
</body>
<script>
  Vue.component('list-component', {
    props: ['items'],
    template: `
      <div>
        <div v-for="item in items" :key="item.id">
          <slot :item="item"></slot>
        </div>
      </div>
    `
  })

  const vm = new Vue({
    data: {
      users: [
        { id: 1, name: '张三', age: 18 },
        { id: 2, name: '李四', age: 20 }
      ]
    },
    el: '#app'
  })
</script>
</html>
```

::: tip 提示
- 组件可以无限嵌套
- 使用 props 向下传递数据
- 使用事件向上传递数据
- 插槽用于内容分发
- 作用域插槽可以访问子组件数据
:::
