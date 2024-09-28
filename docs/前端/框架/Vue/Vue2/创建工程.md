# Vue2 创建工程

官方文档：https://v2.cn.vuejs.org/v2/guide/#%E8%B5%B7%E6%AD%A5

创建一个`.html` 文件：

引入Vue：

- 开发环境版本：包含了有帮助的命令行警告

  ```html
  <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  ```

- 生产环境版本：优化了尺寸和速度

  ```
  <script src="https://cdn.jsdelivr.net/npm/vue@2"></script>
  ```

当使用script引入vue.js时，Vue会被注册为一个全局变量。

使用Vue必须new一个Vue实例：Vue的构造方法参数是一个options配置对象。配置对象中有大量Vue预定义的配置。每一个配置项都是`key:value`结构。一个`key:value`就是一个Vue的配置项。

![image-20240509211828203](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405092118522.png)

template 配置项：value是一个**模板字符串**，用来编写符合Vue语法规则的代码 (Vue有一套自己规定的语法规则)，该配置的字符串会被Vue解析器进行编译，将其转换成浏览器能够识别的HTML代码。

Vue实例的`$mount`：完成挂载动作，将Vue实例挂载到指定位置。也就是说将Vue编译后的HTML代码**渲染**到页面的指定位置。**注意**：指定位置的元素被**替换**

`#app`：类似于CSS中的id选择器语法。表示将Vue实例挂载到`id = 'app'`的元素位置。使用原生JS也可以：

`vm.$mount(document.getElementById('app'))`，也可以使用其他选择器，如类选择器`.app`，但是类选择器可以匹配多个元素(位置)，Vue只会选择第一个位置进行挂载(从上到下第一个)

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
    <div id="app"></div>
</body>
<script>
    //创建Vue实例
    const vm = new Vue({
        template: '<h1>Hello Vue</h1>'
    })
    //将Vue实例挂载到指定位置
    vm.$mount('#app');
</script>

</html>
```

![image-20240509214331102](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405092143739.png)

## data 配置项

在Vue中的data配置项进行动态的渲染页面。data是Vue实例的数据对象。此对象必须是纯粹的对象(含有零个或多个key/value对)

使用`{{}}`插值语法(也称为胡子语法)从data中根据key来获取value，并将value插入到对应的位置。

**原理**：Vue编译器对template进行编译，遇到`{{}}`时从data中取数据，然后将取到的数据插到对应的位置。生成一段HTML代码，最终将HTML渲染到挂载位置呈现。当data发生变化时，template模板会被重新编译，重新渲染。

- 当data为：

  ```json
  data: {
      name: '张三',
      age: 18
  }
  ```

  插值语法：

  ```
  {{name}}
  {{age}}
  ```

- 当data为：

  ```json
  data:{
      user: {
          name: '张三',
          age: 18
      }
  }
  ```

  插值语法：

  ```
  {{user.name}}
  {{user.age}}
  ```

- 当data为：

  ```json
  data{
      colors: ['红色','黄色','蓝色']
  }
  ```

  插值语法：

  ```
  {{colors[0]}}
  {{colors[1]}}
  {{colors[2]}}
  ```

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue选项 data</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <!-- 指定挂载位置 -->
    <div id="app"></div>
</body>
<script>
    //创建Vue实例
    const vm = new Vue({
        data: {
            message: 'Hello Vue'
        },
        template: '<h1>{{message}}</h1>'
    })
    //将Vue实例挂载到指定位置
    vm.$mount('#app');
</script>

</html>
```

![image-20240509214331102](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405092143739.png)

## template 配置项

template编译后进行渲染时会将挂载位置的元素进行**替换**，**template只能有一个根元素**。

当template有多个元素时，只会显示第一个元素：

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue选项 template</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <div id="app"></div>
</body>
<script>
    const vm = new Vue({
        data: {
            name: '张三',
            age: 18
        },
        template: '<h1>{{name}}</h1><h1>{{age}}</h1>'
    }).$mount('#app');
</script>

</html>
```

![image-20240510125955135](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405101259602.png)

可以使用`<div>`来包裹：

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue选项 template</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <div id="app"></div>
</body>
<script>
    const vm = new Vue({
        data: {
            name: '张三',
            age: 18
        },
        template: '<div><h1>{{name}}</h1><h1>{{age}}</h1></div>'
    }).$mount('#app');
</script>

</html>
```

![image-20240510130043761](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405101300128.png)

如果代码需要换行时，可以将代码放入 <span>``</span>：

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue选项 template</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>

<body>
    <div id="app"></div>
</body>
<script>
    const vm = new Vue({
        data: {
            name: '张三',
            age: 18
        },
        template: `
            <div>
                <h1>{{name}}</h1>
                <h1>{{age}}</h1>
            </div>`
    }).$mount('#app');
</script>

</html>
```

![image-20240510130043761](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405101300128.png)

template配置项可以省略，将其直接编写到HTML代码中：这种方式不会产生像template的元素替换。同时， `<div id="app">`下具有Vue语法特色的模板语句。

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue选项 template</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
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
            age: 18
        }
    }).$mount('#app');
</script>

</html>
```

![image-20240510130043761](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405101300128.png)

将Vue实例挂载时，可以不用 `$mount`方法，可以使用Vue的el配置项：el(`element`，元素)配置项主要是用来指定Vue实例关联的容器。

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue选项 template</title>
    <!-- 开发环境版本，包含了有帮助的命令行警告 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
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
            age: 18
        },
        el: '#app'
    })
</script>

</html>
```

![image-20240510130043761](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405101300128.png)
