# 事件处理

**官方文档**：https://cn.vuejs.org/guide/essentials/event-handling.html

## 事件绑定

**官方文档**：https://cn.vuejs.org/api/built-in-directives.html#v-on

**事件绑定的语法格式**：`v-on:事件名`。**例如**：鼠标单击事件的绑定使用 `v-on:click`。

**注意**： 

1. 绑定的回调函数需要在 Vue 实例中使用 methods 进行注册。methods 可以配置多个回调函数，采用逗号隔开。
2. 绑定回调函数时，如果回调函数没有参数，`()`可以省略。
3. 每一个回调函数都可以接收一个事件对象event
4. 如果回调函数有参数，并且还需要获取事件对象，可以使用`$event` 进行占位。
5. `v-on:click` 可以简写为`@click`。简写的语法格式：`@事件名`
6. 回调函数中的this 是 vm。如果回调函数是箭头函数的话，this 是window 对象，因为箭头函数没有自己的 this，它的 this 是继承过来的，默认这个this 是箭头函数所在的宿主对象。这个宿主对象其实就是它的父级作用域。而对象又不能构成单独的作用城，所以这个父级作用域是全局作用域，也就是 window。
7. 可以在函数中改变 data 中的数据，例如：`this.counter++`，这样会联动页面上产生动态效果。

![image.png](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406202136183.png)

```js
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
            <button v-on:click="buy">购买</button>
            <button @click="buy">购买</button>
        </div>
    </div>
</body>
<script>

    const vm = new Vue({
        methods: {
            buy: function () {
                alert("购买成功");
            }
        },
        el: '#app'
    })
</script>

</html>
```

## 事件修饰符

**官方文档**：https://cn.vuejs.org/guide/essentials/event-handling.html#event-modifiers

1. `.stop`：调用 `event.stopPropagation()`

2. `.prevent`：调用 `event.preventDefault()`

3. `.capture`：添加事件侦听器时使用capture模式

   **注意**：只有添加了capture修饰符的元素才会采用捕获模式(带有capture修饰符的优先触发)

4. `.self`：只当事件是从侦听器绑定的元素本身触发时才触发回调

5. `.once`：只触发一次回调

6. `.passive` (2.3.0)：以`{passive:true}`模式添加侦听器

   1. 无需等待，直接继续(立即)执行事件默认行为(对wheel事件有效果)。
   2. `.passive` 和 `.prevent` 修饰符不能共存

## 按键修饰符

**官方文档**：https://cn.vuejs.org/guide/essentials/event-handling.html#key-modifiers

**常用按键修饰符**：

1. `.enter`
2. `.tab`：只能配合keydown使用
3. `.delete`：捕获"删除"和"退格"键
4. `.esc`
5. `.space`
6. `.up`
7. `.down`
8. `.left`
9. `.right`

可以直接将 `KeyboardEvent.key`暴露的任意有效按键名转换为 `kebab-case`来作为修饰符：

```html
<input type="text" @keyup.page-down="getInfo"></input>
```

可以通过全局config.keyCodes对象自定义按键修饰符别名：

```
Vue.config.keyCodes.huiche=13
```

## 系统修饰符

**系统修饰键**：

1. `.ctrl`
2. `.alt`
3. `.shift`
4. `.meta`

**注意**：

1. 只有当系统修饰键和其他键组合使用，并且组合键释放时，才会触发keyup事件
2. 只要按下系统修饰键，就会触发keydown事件

```html
<input type="text" @keyup.ctrl.c="getInfo"></input>
```

