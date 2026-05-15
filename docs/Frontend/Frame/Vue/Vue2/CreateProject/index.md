# Vue2 创建工程

官方文档：https://v2.cn.vuejs.org/v2/guide/#%E8%B5%B7%E6%AD%A5

## CDN 方式

创建一个 `.html` 文件，引入 Vue：

- 开发环境版本：包含了有帮助的命令行警告

  ```html [dev.html]
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  ```

- 生产环境版本：优化了尺寸和速度

  ```html [prod.html]
  <script src="https://fastly.jsdelivr.net/npm/vue@2"></script>
  ```

当使用 script 引入 vue.js 时，Vue 会被注册为一个全局变量。

### 第一个 Vue 程序

```html [first-vue.html]
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>第一个Vue程序</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  </head>

  <body>
    <!-- 指定挂载位置 -->
    <div id="app"></div>
  </body>
  <script>
    //创建Vue实例
    const vm = new Vue({
      template: '<h1>Hello Vue</h1>',
    })
    //将Vue实例挂载到指定位置
    vm.$mount('#app')
  </script>
</html>
```

## Vue 实例

使用 Vue 必须 new 一个 Vue 实例：Vue 的构造方法参数是一个 options 配置对象。配置对象中有大量 Vue 预定义的配置。每一个配置项都是 `key:value` 结构。

### template 配置项

value 是一个**模板字符串**，用来编写符合 Vue 语法规则的代码，该配置的字符串会被 Vue 解析器进行编译，将其转换成浏览器能够识别的 HTML 代码。

### $mount 方法

Vue 实例的 `$mount`：完成挂载动作，将 Vue 实例挂载到指定位置。也就是说将 Vue 编译后的 HTML 代码**渲染**到页面的指定位置。

**注意**：指定位置的元素被**替换**

`#app`：类似于 CSS 中的 id 选择器语法。表示将 Vue 实例挂载到 `id = 'app'` 的元素位置。

```javascript [mount.js]
// 使用选择器
vm.$mount('#app')

// 使用原生JS
vm.$mount(document.getElementById('app'))
```

也可以使用其他选择器，如类选择器 `.app`，但是类选择器可以匹配多个元素，Vue 只会选择第一个位置进行挂载。

## data 配置项

在 Vue 中的 data 配置项进行动态的渲染页面。data 是 Vue 实例的数据对象。此对象必须是纯粹的对象。

使用 `{{}}` 插值语法（也称为胡子语法）从 data 中根据 key 来获取 value，并将 value 插入到对应的位置。

### 基本数据类型

```javascript [basic-data.js]
const vm = new Vue({
  data: {
    name: '张三',
    age: 18
  },
  template: `
    <div>
      <p>{{name}}</p>
      <p>{{age}}</p>
    </div>
  `
})
```

### 对象类型

```javascript [object-data.js]
const vm = new Vue({
  data: {
    user: {
      name: '张三',
      age: 18
    }
  },
  template: `
    <div>
      <p>{{user.name}}</p>
      <p>{{user.age}}</p>
    </div>
  `
})
```

### 数组类型

```javascript [array-data.js]
const vm = new Vue({
  data: {
    colors: ['红色', '黄色', '蓝色']
  },
  template: `
    <div>
      <p>{{colors[0]}}</p>
      <p>{{colors[1]}}</p>
      <p>{{colors[2]}}</p>
    </div>
  `
})
```

## template 配置项详解

template 编译后进行渲染时会将挂载位置的元素进行**替换**，**template 只能有一个根元素**。

### 多个元素（错误示例）

当 template 有多个元素时，只会显示第一个元素：

```html [multi-element.html]
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vue选项 template</title>
    <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  </head>
  <body>
    <div id="app"></div>
  </body>
  <script>
    const vm = new Vue({
      data: {
        name: '张三',
        age: 18,
      },
      template: '<h1>{{name}}</h1><h1>{{age}}</h1>',
    }).$mount('#app')
  </script>
</html>
```

### 使用 div 包裹

```html [wrapped.html]
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vue选项 template</title>
    <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  </head>
  <body>
    <div id="app"></div>
  </body>
  <script>
    const vm = new Vue({
      data: {
        name: '张三',
        age: 18,
      },
      template: '<div><h1>{{name}}</h1><h1>{{age}}</h1></div>',
    }).$mount('#app')
  </script>
</html>
```

### 使用模板字符串

```html [template-string.html]
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vue选项 template</title>
    <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  </head>
  <body>
    <div id="app"></div>
  </body>
  <script>
    const vm = new Vue({
      data: {
        name: '张三',
        age: 18,
      },
      template: `
        <div>
          <h1>{{name}}</h1>
          <h1>{{age}}</h1>
        </div>`,
    }).$mount('#app')
  </script>
</html>
```

## 省略 template

template 配置项可以省略，将其直接编写到 HTML 代码中：这种方式不会产生像 template 的元素替换。

```html [no-template.html]
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vue选项 template</title>
    <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  </head>
  <body>
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
        age: 18,
      },
    }).$mount('#app')
  </script>
</html>
```

## el 配置项

将 Vue 实例挂载时，可以不用 `$mount` 方法，可以使用 Vue 的 el 配置项：el（element，元素）配置项主要是用来指定 Vue 实例关联的容器。

```html [el-config.html]
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vue选项 template</title>
    <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  </head>
  <body>
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
        age: 18,
      },
      el: '#app',
    })
  </script>
</html>
```

::: tip 提示
- CDN 方式适合快速原型开发
- template 只能有一个根元素
- el 和 $mount 二选一使用
- data 必须是函数（组件中）或对象（实例中）
:::
