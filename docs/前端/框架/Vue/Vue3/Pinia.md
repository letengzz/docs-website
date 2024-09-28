# Vue3 Pinia

Pinia：集中式状态(数据)管理，把所有的要管理放到容器中集中管理起来。**适用于多个组件共享数据**。

官方网站：https://pinia.vuejs.org/zh

## 搭建 Pinia 环境

实现效果：

<img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402111711127.gif" alt="pinia_example" style="zoom:30%;border:3px solid" />

1. 创建Count.vue、LoveTalk.vue组件：

   > Count.vue

   ```vue
   <template>
     <div class="count">
       <h2>当前求和为：{{ sum }}</h2>
       <!-- 尽可能转换成数字 -->
       <select v-model.number="n">
         <option value="1">1</option>
         <option value="2">2</option>
         <option value="3">3</option>
       </select>
       <button @click="add">加</button>
       <button @click="minus">减</button>
     </div>
   </template>
   
   <script setup lang="ts" name="Count">
     import { ref } from "vue";
     // 数据
     let sum = ref(1) // 当前求和
     let n = ref(1) // 用户选择的数字
   
     // 方法
     function add(){
       sum.value += n.value
     }
     function minus(){
       sum.value -= n.value
     }
   </script>
   
   <style scoped>
     .count {
       background-color: skyblue;
       padding: 10px;
       border-radius: 10px;
       box-shadow: 0 0 10px;
     }
     select,button {
       margin: 0 5px;
       height: 25px;
     }
   </style>
   ```

   安装axios：

   ```bash
   npm i axios
   ```

   安装nanoid：

   ```
   npm i nanoid
   ```

   > LoveTalk.vue

   ```vue
   <template>
     <div class="talk">
       <button @click="getLoveTalk">获取一句土味情话</button>
       <ul>
         <li v-for="talk in talkList" :key="talk.id">{{talk.title}}</li>
       </ul>
     </div>
   </template>
   
   <script setup lang="ts" name="LoveTalk">
     import {reactive} from 'vue'
     import axios from "axios";
     import {nanoid} from 'nanoid'
     // 数据
     let talkList = reactive([
       {id:'ftrfasdf01',title:'今天你有点怪，哪里怪？怪好看的！'},
       {id:'ftrfasdf02',title:'草莓、蓝莓、蔓越莓，今天想我了没？'},
       {id:'ftrfasdf03',title:'心里给你留了一块地，我的死心塌地'}
     ])
     // 方法
     async function getLoveTalk(){
       // 发请求，下面这行的写法是：连续解构赋值+重命名
       let {data:{content:title}} = await axios.get('https://api.uomg.com/api/rand.qinghua?format=json')
       // 把请求回来的字符串，包装成一个对象
       let obj = {id:nanoid(),title}
       // 放到数组中
       talkList.unshift(obj)
     }
   </script>
   
   <style scoped>
     .talk {
       background-color: orange;
       padding: 10px;
       border-radius: 10px;
       box-shadow: 0 0 10px;
     }
   </style>
   ```

2. App.vue引入上述组件：

   > App.vue

   ```vue
   <template>
     <Count/>
     <br>
     <LoveTalk/>
   </template>
   <script setup lang="ts">
     import Count from "@/components/Count.vue";
     import LoveTalk from "@/components/LoveTalk.vue";
   </script>
   
   <style scoped>
   </style>
   ```

安装pinia：

```bash
npm install pinia
```

引入pinia：

> src/main.ts

```ts
import { createApp } from 'vue'
import App from './App.vue'

/* 引入createPinia，用于创建pinia */
import { createPinia } from 'pinia'

/* 创建pinia 最好在app创建之后 再创建 */
const pinia = createPinia()
const app = createApp(App)

/* 使用插件 */
app.use(pinia)
app.mount('#app')
```

此时开发者工具中已经有了`pinia`选项

<img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402111427410.png" style="zoom:80%;border:1px solid black;border-radius:10px" />

## 存储+读取数据

`Store`是一个保存：**状态**、**业务逻辑** 的实体，每个组件都可以**读取**、**写入**它。

它有三个概念：`state`、`getter`、`action`，相当于组件中的： `data`、 `computed` 和 `methods`。

1. 创建Store：

   **说明**：存放文件夹为store

   > src/store/count.ts

   ```typescript
   import {defineStore} from "pinia";
   
   // 命名useXxxStore
   export const useUserStore = defineStore('count', {
   
       //真正存放数据的地方
       state() {
           return {
               sum: 6
           }
       }
   })
   ```

   > src/store/talk.ts

   ```typescript
   // 引入defineStore用于创建store
   import {defineStore} from "pinia";
   
   // 定义并暴露一个store
   // 命名useXxxStore
   export const useTalkStore = defineStore('talk', {
       // 动作
       actions: {},
       // 状态
       //真正存放数据的地方
       state() {
           return {
               talkList: [
                   {id: 'ftrfasdf01', title: '今天你有点怪，哪里怪？怪好看的！'},
                   {id: 'ftrfasdf02', title: '草莓、蓝莓、蔓越莓，今天想我了没？'},
                   {id: 'ftrfasdf03', title: '心里给你留了一块地，我的死心塌地'}
               ]
           }
       },
       // 计算
       getters: {}
   })
   ```

2. 组件中使用`state`中的数据：

   > /src/components/Count.vue

   ```vue
   <template>
     <div class="count">
       <h2>当前求和为：{{ countStore.sum }}</h2>
     </div>
   </template>
   
   <script setup lang="ts" name="Count">
     // 引入对应的useCountStore
     import {useCountStore} from "@/store/count";
   
     // 调用useCountStore得到专门保存count对应的store
     const countStore = useCountStore()
     console.log('@@@',countStore.sum)
     console.log('@@@',countStore.$state.sum)
   </script>
   ```

   > /src/components/LoveTalk.vue

   ```vue
   <template>
     <div class="talk">
       <button @click="getLoveTalk">获取一句土味情话</button>
       <ul>
         <li v-for="talk in talkStore.talkList" :key="talk.id">{{talk.title}}</li>
   <!--      <li v-for="talk in talkStore.$state.talkList" :key="talk.id">{{talk.title}}</li>-->
       </ul>
     </div>
   </template>
   
   <script setup lang="ts" name="LoveTalk">
     // 引入对应的useTalkStore
     import {useTalkStore} from "@/store/talk";
     // 调用useXxxxxStore得到对应的store
     const talkStore = useTalkStore();
   </script>
   ```

## 修改数据 (三种方式)

**修改方式**：

1. 直接修改：

   ```typescript
   countStore.sum = 666
   ```

2. 批量修改：

   **说明**：通过多个直接修改也可以达到批量修改效果，但是不推荐

   ```typescript
   countStore.$patch({
     sum:999,
     address:'湖北'
   })
   ```

3. 借助`action`修改（`action`中可以编写一些业务逻辑 可以复用逻辑）

   ```typescript
   import { defineStore } from 'pinia'
   
   export const useCountStore = defineStore('count', {
     /*************/
     actions: {
       //加
       increment(value:number) {
         if (this.sum < 10) {
           //操作countStore中的sum（this是当前的store）
           this.sum += value
         }
       },
       //减
       decrement(value:number){
         if(this.sum > 1){
           this.sum -= value
         }
       }
     },
     /*************/
   })
   ```

   组件中调用`action`即可

   ```typescript
   // 使用countStore
   const countStore = useCountStore()
   
   // 调用对应action
   countStore.incrementOdd(n.value)
   ```

## storeToRefs

借助`storeToRefs`将`store`中的数据转为`ref`对象，方便在模板中使用。

注意：`pinia`提供的`storeToRefs`只会将数据做转换，而`Vue`的`toRefs`会转换`store`中所有数据。

```vue
<template>
	<div class="count">
		<h2>当前求和为：{{sum}}</h2>
	</div>
</template>

<script setup lang="ts" name="Count">
  import { useCountStore } from '@/store/count'
  /* 引入storeToRefs */
  import { storeToRefs } from 'pinia'

  /* 得到countStore */
  const countStore = useCountStore()
  /* 使用storeToRefs转换countStore，随后解构 */
  const {sum} = storeToRefs(countStore)
</script>
```

## getters

当`state`中的数据，需要经过处理后再使用时，可以使用`getters`配置。

追加```getters```配置：

```js
// 引入defineStore用于创建store
import {defineStore} from 'pinia'

// 定义并暴露一个store
export const useCountStore = defineStore('count',{
  // 动作
  actions:{
    /************/
  },
  // 状态
  state(){
    return {
      sum:1,
      school:'hello'
    }
  },
  // 计算
  getters:{
    bigSum:(state):number => state.sum *10,
    upperSchool():string{
      return this. school.toUpperCase()
    }
  }
})
```

组件中读取数据：

```js
const {increment,decrement} = countStore
let {sum,school,bigSum,upperSchool} = storeToRefs(countStore)
```

## $subscribe

在 Pinia 中，每个创建的 store 实例都可以使用 `$subscribe` 方法来订阅状态的变化。这个方法接受一个回调函数作为参数，当 store 的状态发生变化时，这个回调函数会被调用。

```ts
//mutate 本次修改的信息 state真正的数据
talkStore.$subscribe((mutate,state)=>{
  console.log('LoveTalk',mutate,state)
  //localStorage里面存的都是字符串 如果不是字符串 底层会将调用toString  
  localStorage.setItem('talk',JSON.stringify(talkList.value))
})
```

## store组合式写法

```ts
import {defineStore} from 'pinia'
import axios from 'axios'
import {nanoid} from 'nanoid'
import {reactive} from 'vue'

export const useTalkStore = defineStore('talk',()=>{
  // talkList就是state
  const talkList = reactive(
    JSON.parse(localStorage.getItem('talkList') as string) || []
  )

  // getATalk函数相当于action
  async function getATalk(){
    // 发请求，下面这行的写法是：连续解构赋值+重命名
    let {data:{content:title}} = await axios.get('https://api.uomg.com/api/rand.qinghua?format=json')
    // 把请求回来的字符串，包装成一个对象
    let obj = {id:nanoid(),title}
    // 放到数组中
    talkList.unshift(obj)
  }
  return {talkList,getATalk}
})
```







