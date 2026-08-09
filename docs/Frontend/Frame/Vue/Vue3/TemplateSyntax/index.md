# Vue3 模板语法

模板（Template）是 Vue 组件的「视图层描述」，把状态与 DOM 绑定起来。本节系统梳理插值、指令、动态参数、修饰符和 `v-model` 原理，帮助你把模板写得更准确。

::: info 适用版本
本节基于 Vue 3.5.x。Vue 3 模板支持 JavaScript 表达式，但模板表达式只能访问组件实例暴露的成员，不能访问全局变量（`window`、`Math` 等需要显式挂到实例上）。
:::

## 插值：双花括号

```vue [App.vue]
<script setup>
import { ref } from "vue"
const name = ref("Codex")
const count = ref(2)
</script>

<template>
  <p>你好，{{ name }}</p>
  <p>{{ count + 1 }} 件商品</p>
  <p>{{ count > 1 ? "有货" : "缺货" }}</p>
</template>
```

插值里只能写**单行表达式**，不能写语句（`if`、`for`）或声明变量。需要复杂逻辑时用计算属性或方法。

`v-text` 与 `v-html`：

```vue
<p v-text="rawText"></p>
<p v-html="richHtml"></p>
```

`v-html` 会渲染真实 HTML，**只允许渲染可信内容**，用户输入直接传入会引发 XSS。

## v-bind：属性绑定

```vue
<img v-bind:src="imgSrc" />
<img :src="imgSrc" />
<button :disabled="isDisabled">提交</button>
```

绑定对象可以一次给多个属性：

```vue
<div v-bind="attrs"></div>
```

动态参数（Vue 3.3+ 支持更宽松的动态参数表达式）：

```vue
<button :[eventName]="handler">点击</button>
```

## v-on：事件绑定

```vue
<button v-on:click="handler">点击</button>
<button @click="handler">点击</button>
<button @click="handler(1, $event)">传参</button>
```

常用修饰符：

| 修饰符 | 作用 |
| --- | --- |
| `.stop` | 调用 `event.stopPropagation()` |
| `.prevent` | 调用 `event.preventDefault()` |
| `.once` | 事件只触发一次 |
| `.self` | 只有 `event.target` 是自身时才触发 |
| `.enter` / `.esc` | 按键修饰符，监听指定键 |
| `.capture` | 捕获阶段触发 |

```vue
<form @submit.prevent="onSubmit">...</form>
<a @click.stop="onClick">链接</a>
```

## v-model：双向绑定

`v-model` 是「值绑定 + 事件监听」的语法糖。对组件而言：

```vue
<MyInput v-model="value" />
```

等价于：

```vue
<MyInput :modelValue="value" @update:modelValue="value = $event" />
```

在子组件里接收和修改：

```vue [MyInput.vue]
<script setup>
const props = defineProps({
  modelValue: String,
})
const emit = defineEmits(["update:modelValue"])
</script>

<template>
  <input
    :value="props.modelValue"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
```

Vue 3.4+ 推荐用 `defineModel` 简化：

```vue [MyInput.vue]
<script setup>
const model = defineModel({ type: String })
</script>

<template>
  <input v-model="model" />
</template>
```

`v-model` 修饰符：

| 修饰符 | 作用 |
| --- | --- |
| `.lazy` | 改为 `change` 事件后同步 |
| `.number` | 自动转数字 |
| `.trim` | 自动去首尾空格 |

## 条件与列表渲染

```vue
<p v-if="status === 'loading'">加载中...</p>
<p v-else-if="status === 'error'">出错了</p>
<p v-else>加载完成</p>

<p v-show="visible">v-show 只是切换 display</p>
```

`v-if` 与 `v-show` 的选择：`v-if` 真正创建/销毁元素，切换开销大；`v-show` 只改 `display`，适合频繁切换。

列表渲染必须带 `key`：

```vue
<ul>
  <li v-for="(item, index) in list" :key="item.id">
    {{ index }} - {{ item.name }}
  </li>
</ul>
```

`key` 帮助 Vue 复用和移动元素，使用稳定且唯一的 ID，不要用数组下标（列表会增删/排序时容易出问题）。

## class 与 style 绑定

```vue
<!-- 对象语法 -->
<div :class="{ active: isActive, disabled: isDisabled }"></div>

<!-- 数组语法 -->
<div :class="[baseClass, isActive ? 'active' : '']"></div>

<!-- style 对象 -->
<div :style="{ color: textColor, fontSize: size + 'px' }"></div>
```

## 内置组件与插槽

动态组件：

```vue
<component :is="currentComponent" />
```

插槽：

```vue
<!-- 父组件 -->
<Card>
  <p>插槽内容</p>
</Card>

<!-- 子组件 Card.vue -->
<template>
  <div class="card">
    <slot></slot>
  </div>
</template>
```

## 易错点

::: danger 常见错误
1. 在模板里写 `if (x) { return 1 }` 这类语句，模板只支持表达式。
2. 用 `v-html` 渲染用户输入，导致 XSS。
3. `v-for` 与 `v-if` 同时用在同一个元素上：`v-if` 优先级更高但会导致每次渲染都判断，可读性也差，建议用计算属性先过滤。
4. 列表项用 `index` 当 `key`，插入/删除后元素复用错乱，输入框内容串位。
5. `v-model` 直接绑定 `props.modelValue`，子组件里修改 prop 报警告；应通过事件或 `defineModel` 修改。
6. 忘了动态参数名是运行时计算，`:[eventName]` 中 `eventName` 必须是合法属性名，否则报错。
:::

## 验证方式

1. `npm run dev` 启动后修改 `ref` 值，确认插值和绑定同步更新。
2. 在浏览器控制台执行 `document.querySelector('input').value`，再触发 `input` 事件，确认 `v-model` 双向同步。
3. 用 Vue DevTools 打开组件，修改 `props`/`state`，观察模板变化。
4. 给列表动态增删一条数据，确认 DOM 中的输入框内容没有串位（`key` 正确）。

## 参考资料

- Vue 模板语法：https://cn.vuejs.org/guide/essentials/template-syntax.html
- 事件处理：https://cn.vuejs.org/guide/essentials/events.html
- 表单输入绑定：https://cn.vuejs.org/guide/essentials/forms.html
- 列表渲染：https://cn.vuejs.org/guide/essentials/list.html
