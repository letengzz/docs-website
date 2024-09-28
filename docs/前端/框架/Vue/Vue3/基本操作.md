# Vue3 基本操作

## 目录结构

### 基于 vue-cli 创建目录结构

### 基于 vite 创建

- public：公共静态文件
  - favicon.ico：页签图标
- src：源代码文件
  - main.ts：通过入口文件(index.html)来引入main.ts 来支撑整个src目录
  - App.vue：根组件 (在main.ts设置引入)
  - components：存放组件目录
  - assets：存放公共目录
- .gitignore：忽略文件
- node_modules：使用 `npm i`安装所有依赖会出现，存放项目中的依赖
- env.d.ts：引入所有文件声明：让TypeScript认识 图片、文本txt、图标等
- index.html：项目的首页，访问入口文件
- package.json：包管理文件。整个项目对依赖库的配置，包括了启动命令、构建项目命令
- package-lock.json：包管理文件
- vite.config.ts：整个工程的配置文件，比如安装插件、配置代理等。
- tsconfig.json、tsconfig.node.json、tsconfig.app.json：TypeScript 配置文件

## 运行原理

![运行原理.png](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406202049756.png)

## 编写APP组件

`Vue3`向下兼容`Vue2`语法，且`Vue3`中的模板中可以没有根标签。

index.html为项目的入口文件，在项目的最外层，主要将main.ts引入：

![image-20240131000503248](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401310005377.png)

加载`index.html`后，`Vite` 解析 `<script type="module" src="xxx">` 指向的`TypeScript`。通过main.ts引入样式，通过createApp创建应用实例设置App为根组件，并挂载App组件到#app元素上：

![image-20240131000943148](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402052208664.png)

将src目录全部删除。

创建main.ts：

```typescript
// 引入createApp用于创建应用
import { createApp } from 'vue'
// 引入App根组件
import App from './App.vue'
// 创建应用实例设置App为根组件，并挂载App组件到#app元素上
createApp(App).mount('#app')
```

`.vue` 结尾的文件就是vue页面，也可以称为vue组件。

Vue页面(组件)一般由三部分组成：

- `<template>`：HTML页面，要展示的内容
- `<script>`：JavaScript代码
- `<style>`：CSS

创建App.vue：

```vue
<!-- 编写模板结构 -->
<template>
  <!-- Html -->
  <div class="app">
    <h1>你好 世界</h1>
  </div>
</template>
<!-- 编写脚本代码 -->
<script lang="ts">
// JS或TS
//默认暴露
export default {
  name: "App" //组件名
}

</script>
<!-- 样式 scoped:表示局部样式-->
<style scoped>
/* css */
.app {
  background-color: #ddd;
  box-shadow: 0 0 10px;
  border-radius: 10px;
  padding: 20px;
}
</style>
```

编写自己的组件：`src/components/person.vue`

```vue
<template>
  <div class="person">
    <h2>姓名：{{ name }}</h2>
    <h2>年龄：{{ age }}</h2>
    <button @click="changeName">修改名字</button>
    <button @click="changeAge">修改年龄</button>
    <button @click="showTel">查看联系方式</button>
  </div>
</template>

<script lang="ts">
export default {
  //Vue2: 配置式风格(选项式)
  name: 'Person',
  data() {
    return {
      name: '张三',
      age: 18,
      tel: '1388888888'
    }
  },
  methods: {
    changeName() {
      this.name = '李四'
    },
    changeAge() {
      this.age += 1;
    },
    showTel() {
      alert(this.tel)
    }
  }
}
</script>

<style scoped>
.person {
  background-color: skyblue;
  box-shadow: 0 0 10px;
  border-radius: 10px;
  padding: 20px;
}

button {
  margin: 0 5px;
}
</style>
```

App.vue：

```vue
<!-- 编写模板结构 -->
<template>
  <!-- Html -->
  <div class="app">
    <h1>你好 世界</h1>
    <!--Vue3可以写多个标签且不用包裹-->
    <Person/>
  </div>
</template>
<!-- 编写脚本代码 -->
<script lang="ts">
// JS或TS
  import Person from "./components/person.vue"
//默认暴露
export default {
  name: "App", //组件名
  components: { Person } //引入的组件
}

</script>
<!-- 样式 -->
<style scoped>
/* css */
.app {
  background-color: #ddd;
  box-shadow: 0 0 10px;
  border-radius: 10px;
  padding: 20px;
}
</style>
```

env.d.ts：

```typescript
/// <reference types="vite/client" />
declare module '*.vue' {
    import { DefineComponent } from "vue"
    const component: DefineComponent<{}, {}, any>
    export default component
}
```

运行 `npm run dev` 并访问：http://localhost:5174/

![image-20240131005349510](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401310053711.png)

## 修改端口号

在 vite.config.ts中修改端口号：

```
export default defineConfig({
  plugins: [
    vue(),
  ],
  server: {
    port: 3000
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

