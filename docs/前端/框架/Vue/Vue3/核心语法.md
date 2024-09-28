# Vue3 核心语法

## OptionsAPI 与 CompositionAPI

- `Vue2`的`API`设计是`Options`（配置式、选项式）风格的。
- `Vue3`的`API`设计是`Composition`（组合）风格的。

**Options API 的弊端**：`Options`类型的 `API`：数据、方法、计算属性等，是分散在：`data`、`methods`、`computed`中的，若想新增或者修改一个需求，就需要分别修改：`data`、`methods`、`computed`，不便于维护和复用。

<img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402061623795.gif" alt="1.gif" style="zoom:70%;border-radius:20px" /><img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401310106948.gif" alt="2.gif" style="zoom:70%;border-radius:20px" />

**Composition API 的优势**：可以用函数的方式，更加优雅的组织代码，让相关功能的代码更加有序的集中组织在一起。

<img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401310106357.gif" alt="3.gif" style="height:300px;border-radius:10px"  /><img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401310122342.gif" alt="4.gif" style="height:300px;border-radius:10px"  />

## setup

`setup`是`Vue3`中一个新的配置项，值是一个函数，它是 `Composition API` **“表演的舞台**_**”**_，组件中所用到的：数据、方法、计算属性、监视......等等，均配置在`setup`中。

**特点**：

- `setup`函数返回的对象中的内容，可直接在模板中使用。
- `setup`中访问`this`是`undefined`。
- `setup`函数会在`beforeCreate`之前调用，它是"领先"所有钩子执行的。

```vue
<template>
  <div class="person">
    <h2>姓名：{{name}}</h2>
    <h2>年龄：{{age}}</h2>
    <button @click="changeName">修改名字</button>
    <button @click="changeAge">年龄+1</button>
    <button @click="showTel">点我查看联系方式</button>
  </div>
</template>

<script lang="ts">
  export default {
    name:'Person',
    //setup 先于 beforeCreate执行
    beforeCreate(){
    	console.log("beforeCreate")
    },
    setup(){
      // console.log(this) //setup函数中的this是undefined，Vue3中已经弱化this了
      // 数据，原来写在data中（注意：此时的name、age、tel数据都不是响应式数据）
      let name = '张三'
      let age = 18
      let tel = '13888888888'

      // 方法，原来写在methods中
      function changeName(){
        name = 'zhang-san' //注意：此时这么修改name页面是不变化的
        console.log(name) //name确实改了，但name不是响应式的
      }
      function changeAge(){
        age += 1 //注意：此时这么修改age页面是不变化的
        console.log(age) //age确实改了，但age不是响应式的
      }
      function showTel(){
        alert(tel)
      }

      // 返回一个对象，对象中的内容，模板中可以直接使用 name:name 可简写成name
      return {name:name,age:age,tel,changeName,changeAge,showTel}
      // return 后不要写任何内容 否则不会执行
    }
  }
</script>
```

**setup 的返回值**：

- 若返回一个**对象**：则对象中的：属性、方法等，在模板中均可以直接使用

- 若返回一个**函数**：则可以自定义渲染内容：

  ```vue
  setup(){
    return ()=> '你好啊！'
  }
  ```

**setup 与 Options API 的关系**：

- `Vue2` 的配置（`data`、`methods`......）中**可以访问到** `setup`中的属性、方法。
- 但在`setup`中**不能访问到**`Vue2`的配置（`data`、`methods`......）。
- 如果与`Vue2`冲突，则`setup`优先。

## setup 语法糖

`setup`函数有一个语法糖，这个语法糖，可以把`setup`独立出去，并直接`return`。

> person.vue

```vue
<template>
  <div class="person">
    <h2>姓名：{{name}}</h2>
    <h2>年龄：{{age}}</h2>
    <button @click="changName">修改名字</button>
    <button @click="changAge">年龄+1</button>
    <button @click="showTel">点我查看联系方式</button>
  </div>
</template>

<script lang="ts">
  export default {
    name:'Person',
  }
</script>

<!-- 下面的写法是setup语法糖 -->
<script setup lang="ts">
  console.log(this) //undefined
  
  // 数据（注意：此时的name、age、tel都不是响应式数据）
  let name = '张三'
  let age = 18
  let tel = '13888888888'

  // 方法
  function changName(){
    name = '李四'//注意：此时这么修改name页面是不变化的
  }
  function changAge(){
    console.log(age)
    age += 1 //注意：此时这么修改age页面是不变化的
  }
  function showTel(){
    alert(tel)
  }
</script>
```

> App.vue

```vue
<!-- 编写模板结构 -->
<template>
  <!-- Html -->
  <div class="app">
    <h1>你好 世界</h1>
    <!-- Vue3 可以写多个根标签-->
    <Person/>
  </div>
</template>
<!-- 编写脚本代码 -->
<script lang="ts">
export default {
  name: 'App',
}
</script>
<script setup lang="ts">
// JS或TS
import Person from "./components/person.vue"
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

扩展：上述代码，还需要编写一个不写`setup`的`script`标签，去指定组件名字，比较麻烦，可以借助`vite`中的插件简化

1. 安装插件依赖：

   ```powershell
   npm i vite-plugin-vue-setup-extend -D
   ```

2. 第二步：`vite.config.ts`

   ```typescript
   import { defineConfig } from 'vite'
   import VueSetupExtend from 'vite-plugin-vue-setup-extend'
   
   export default defineConfig({
     plugins: [ VueSetupExtend() ]
   })
   ```

3. 第三步：

   > person.vue

   ```vue
   <template>
     <div class="person">
       <h2>姓名：{{name}}</h2>
       <h2>年龄：{{age}}</h2>
       <button @click="changName">修改名字</button>
       <button @click="changAge">年龄+1</button>
       <button @click="showTel">点我查看联系方式</button>
     </div>
   </template>
   
   <!-- 下面的写法是setup语法糖 -->
   <script setup lang="ts" name="Person">
     console.log(this) //undefined
     
     // 数据（注意：此时的name、age、tel都不是响应式数据）
     // 在Vue2中，data()中的数据是响应式的，在Vue3中需要借助ref、reactive来创建响应式数据
     let name = '张三'
     let age = 18
     let tel = '13888888888'
   
     // 方法
     function changName(){
       name = '李四'//注意：此时这么修改name页面是不变化的
     }
     function changAge(){
       console.log(age)
       age += 1 //注意：此时这么修改age页面是不变化的
     }
     function showTel(){
       alert(tel)
     }
   </script>
   ```

   > App.vue

   ```vue
   <!-- 编写模板结构 -->
   <template>
     <!-- Html -->
     <div class="app">
       <h1>你好 世界</h1>
       <!-- Vue3 可以写多个根标签-->
       <Person/>
     </div>
   </template>
   <!-- 编写脚本代码 -->
   <script setup lang="ts" name="App">
   // JS或TS
   import Person from "./components/person.vue"
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

## 响应式数据

### ref 创建

`ref`接收的数据可以是：**基本类型**、**对象类型**。

#### 基本类型的响应式数据

**作用：**定义响应式变量。

**语法：**`let xxx = ref(初始值)`。

**返回值：**一个`RefImpl`的实例对象，简称`ref对象`或`ref`，`ref`对象的`value`**属性是响应式的**。

**注意点：**

- `JS`中操作数据需要：`xxx.value`，但模板中不需要`.value`，直接使用即可。
- 对于`let name = ref('张三')`来说，`name`不是响应式的，`name.value`是响应式的。

```vue
<template>
  <div class="person">
    <!-- 不需要加.value -->
    <h2>姓名：{{ name }}</h2>
    <h2>年龄：{{ age }}</h2>
    <button @click="changeName">修改名字</button>
    <button @click="changeAge">修改年龄</button>
    <button @click="showTel">查看联系方式</button>
  </div>
</template>

<!-- 下面的写法是setup语法糖 -->
<script setup lang="ts" name="Person">
//引入ref
import {ref} from "vue";

// name和age是一个RefImpl的实例对象，简称ref对象，它们的value属性是响应式的。
let name = ref('张三')
let age = ref(18)
// tel就是一个普通的字符串，不是响应式的
let tel = '1388888888'

function changeName() {
  // 注意：name不是响应式的，name.value是响应式的，会引起页面的更新。
  // JS中操作ref对象时候需要.value
  name.value = 'zhang-san' 
  console.log(name.value)
}

function changeAge() {
  // 注意：name不是响应式的，name.value是响应式的，会引起页面的更新。
  // JS中操作ref对象时候需要.value
  age.value += 1 
  console.log(age.value) 
}

function showTel() {
  alert(tel)
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

#### 对象类型的响应式数据

若`ref`接收的是对象类型，内部其实也是调用了`reactive`函数。

```vue
<template>
  <div class="person">
    <h2>汽车信息：一台{{ car.brand }}汽车，价值{{ car.price }}万</h2>
    <h2>游戏列表：</h2>
    <ul>
      <li v-for="g in games" :key="g.id">{{ g.name }}</li>
    </ul>
    <h2>测试：{{obj.a.b.c.d}}</h2>
    <button @click="changeCarPrice">修改汽车价格</button>
    <button @click="changeFirstGame">修改第一游戏</button>
    <button @click="test">测试</button>
  </div>
</template>

<script lang="ts" setup name="Person">
import { ref } from 'vue'

// 数据
let car = ref({ brand: '奔驰', price: 100 })
let games = ref([
  { id: 'test01', name: '英雄联盟' },
  { id: 'test02', name: '王者荣耀' },
  { id: 'test03', name: '原神' }
])
let obj = ref({
  a:{
    b:{
      c:{
        d:666
      }
    }
  }
})

console.log(car)

function changeCarPrice() {
  car.value.price += 10
}
function changeFirstGame() {
  games.value[0].name = '流星蝴蝶剑'
}
function test(){
  obj.value.a.b.c.d = 999
}
</script>
```

### reactive 创建

**说明**：reactive 只能创建对象类型的响应式数据

#### 对象类型的响应式数据

**作用：**定义一个**响应式对象**（基本类型不要用它，要用`ref`，否则报错）

**语法：**`let 响应式对象= reactive(源对象)`。

**返回值：**一个`Proxy`的实例对象，简称：响应式对象。

**注意点：**`reactive`定义的响应式数据是“深层次”的，不管数据藏得多深，都会变成响应式的。

```vue
<template>
  <div class="person">
    <h2>汽车信息：一台{{ car.brand }}汽车，价值{{ car.price }}万</h2>
    <h2>游戏列表：</h2>
    <ul>
      <li v-for="g in games" :key="g.id">{{ g.name }}</li>
    </ul>
    <h2>测试：{{obj.a.b.c.d}}</h2>
    <button @click="changeCarPrice">修改汽车价格</button>
    <button @click="changeFirstGame">修改第一游戏</button>
    <button @click="test">测试</button>
  </div>
</template>

<script lang="ts" setup name="Person">
import { reactive } from 'vue'

// 数据
//源对象：{ brand: '奔驰', price: 100 } 响应式对象：car
let car = reactive({ brand: '奔驰', price: 100 })
let games = reactive([
  { id: 'test01', name: '英雄联盟' },
  { id: 'test02', name: '王者荣耀' },
  { id: 'test03', name: '原神' }
])
let obj = reactive({
  a:{
    b:{
      c:{
        d:666
      }
    }
  }
})

//方法
function changeCarPrice() {
  car.price += 10
}
function changeFirstGame() {
  games[0].name = '流星蝴蝶剑'
}
function test(){
  obj.a.b.c.d = 999
}
</script>
```

### ref 对比 reactive

**宏观角度看**：

1. `ref`用来定义：**基本类型数据**、**对象类型数据**
2. `reactive`用来定义：**对象类型数据**

**区别**：

1. `ref`创建的变量必须使用`.value`（可以使用vscode的`volar`插件自动添加`.value`：设置中勾选Auto Insert Dot Value）。

   <img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401312120000.png" alt="自动补充value" style="zoom:50%;border-radius:20px" />

   ```js
   let car = ref({brand:'奔驰',price:100})
   function changeCar(){
   	car.value = {brand:'奥拓',price:1}
   }
   ```

2. `reactive`重新分配一个新对象，会**失去**响应式（可以使用`Object.assign`去整体替换）

   ```js
   let car = reactive({brand:'奔驰',price:100})
   function changeCar(){
   	//car = {brand:'奥拓',price:1} //此写法页面不会更新
   	//car = reactive({brand:'奥拓',price:1}) //此写法页面不会更新
   	Object.assign(car,{brand:'奥拓',price:1}) //页面可以更新
   }
   ```

**使用原则**：

1. 若需要一个基本类型的响应式数据，必须使用`ref`。
2. 若需要一个响应式对象，层级不深，`ref`、`reactive`都可以。
3. 若需要一个响应式对象，且层级较深，推荐使用`reactive`。

### toRefs 与 toRef

作用：将一个响应式对象中的每一个属性，转换为`ref`对象。

备注：`toRefs`与`toRef`功能一致，但`toRefs`可以批量转换。

```vue
<template>
  <div class="person">
    <h2>姓名：{{person.name}}</h2>
    <h2>年龄：{{person.age}}</h2>
    <h2>性别：{{person.gender}}</h2>
    <button @click="changeName">修改名字</button>
    <button @click="changeAge">修改年龄</button>
    <button @click="changeGender">修改性别</button>
  </div>
</template>

<script lang="ts" setup name="Person">
  import {ref,reactive,toRefs,toRef} from 'vue'

  // 数据
  let person = reactive({name:'张三', age:18, gender:'男'})

  //解构赋值 相当于 let name = person.name let gender = person.gender
  // let {name, gender} = person
  
  // 通过toRefs将person对象中的n个属性批量取出，且依然保持响应式的能力
  //相当于 name = ref(person.name) gender = ref(person.gender)
  let {name,gender} =  toRefs(person)
	
  // 通过toRef将person对象中的gender属性取出，且依然保持响应式的能力
  let age = toRef(person,'age')

  // 方法
  function changeName(){
    name.value += '~'
  }
  function changeAge(){
    age.value += 1
  }
  function changeGender(){
    gender.value = '女'
  }
</script>
```

## computed 计算属性 

作用：根据已有数据计算出新数据（和`Vue2`中的`computed`作用一致）。

<img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402091439573.gif" style="zoom:20%;" />  

```vue
<template>
  <div class="person">
    姓：<input type="text" v-model="firstName"> <br>
    名：<input type="text" v-model="lastName"> <br>
    全名：<span>{{fullName}}</span> <br>
    <button @click="changeFullName">全名改为：li-si</button>
  </div>
</template>

<script setup lang="ts" name="App">
  import {ref,computed} from 'vue'

  let firstName = ref('zhang')
  let lastName = ref('san')

  // 计算属性——只读取，不修改
  /* let fullName = computed(()=>{
    return firstName.value + '-' + lastName.value
  }) */


  // 计算属性——既读取又修改
  let fullName = computed({
    // 读取
    get() {
      return firstName.value.slice(0,1).toUpperCase() + firstName.value.split('-')[0].slice(1) + '-' + lastName.value
    },
    // 修改
    set(val) {
      console.log('有人修改了fullName', val)
      firstName.value = val.split('-')[0].slice(0,1).toUpperCase() + val.split('-')[0].slice(1)
      lastName.value = val.split('-')[1]
    }
  })

  function changeFullName(){
    fullName.value = 'li-si'
  } 
</script>
```

## watch 监视

作用：监视数据的变化（和`Vue2`中的`watch`作用一致）

特点：`Vue3`中的`watch`只能监视以下**四种数据**：
1. `ref`定义的数据。
1. `reactive`定义的数据。
1. 函数返回一个值（`getter`函数）。
1. 一个包含上述内容的数组。


在`Vue3`中使用`watch`的时候，通常会遇到以下几种情况：

1. 监视`ref`定义的【基本类型】数据：直接写数据名即可，监视的是其`value`值的改变。

   ```vue
   <template>
     <div class="person">
       <h1>情况一：监视【ref】定义的【基本类型】数据</h1>
       <h2>当前求和为：{{sum}}</h2>
       <button @click="changeSum">点我sum+1</button>
     </div>
   </template>
   
   <script lang="ts" setup name="Person">
     import {ref,watch} from 'vue'
     // 数据
     let sum = ref(0)
     // 方法
     function changeSum(){
       sum.value += 1
     }
     // 监视，情况一：监视【ref】定义的【基本类型】数据
     const stopWatch = watch(sum,(newValue,oldValue)=>{
       console.log('sum变化了',newValue,oldValue)
       if(newValue >= 10){
         stopWatch()
       }
     })
   </script>
   ```

2. 监视`ref`定义的【对象类型】数据：直接写数据名，监视的是对象的【地址值】，若想监视对象内部的数据，要手动开启深度监视。

   **注意**：

   * 若修改的是`ref`定义的对象中的属性，`newValue` 和 `oldValue` 都是新值，因为它们是同一个对象。

   * 若修改整个`ref`定义的对象，`newValue` 是新值， `oldValue` 是旧值，因为不是同一个对象了。

   ```vue
   <template>
     <div class="person">
       <h1>情况二：监视【ref】定义的【对象类型】数据</h1>
       <h2>姓名：{{ person.name }}</h2>
       <h2>年龄：{{ person.age }}</h2>
       <button @click="changeName">修改名字</button>
       <button @click="changeAge">修改年龄</button>
       <button @click="changePerson">修改整个人</button>
     </div>
   </template>
   
   <script lang="ts" setup name="Person">
     import {ref,watch} from 'vue'
     // 数据
     let person = ref({
       name:'张三',
       age:18
     })
     // 方法
     function changeName(){
       person.value.name += '~'
     }
     function changeAge(){
       person.value.age += 1
     }
     function changePerson(){
       person.value = {name:'李四',age:90}
     }
   /*
     监视，情况一：监视【ref】定义的【对象类型】数据，监视的是对象的地址值，若想监视对象内部属性的变化，需要手动开启深度监视
     watch的第一个参数是：被监视的数据
     watch的第二个参数是：监视的回调
     watch的第三个参数是：配置对象（深度监视：deep、立即监视 不管是否变化初次都会监视：immediate等等.....）
   */
     watch(person,(newValue,oldValue)=>{
       console.log('person变化了',newValue,oldValue)
     },{deep:true})
     
   </script>
   ```

3. 监视`reactive`定义的【对象类型】数据，且默认开启了深度监视。

   ```vue
   <template>
     <div class="person">
       <h1>情况三：监视【reactive】定义的【对象类型】数据</h1>
       <h2>姓名：{{ person.name }}</h2>
       <h2>年龄：{{ person.age }}</h2>
       <button @click="changeName">修改名字</button>
       <button @click="changeAge">修改年龄</button>
       <button @click="changePerson">修改整个人</button>
       <hr>
       <h2>测试：{{obj.a.b.c}}</h2>
       <button @click="test">修改obj.a.b.c</button>
     </div>
   </template>
   
   <script lang="ts" setup name="Person">
     import {reactive,watch} from 'vue'
     // 数据
     let person = reactive({
       name:'张三',
       age:18
     })
     let obj = reactive({
       a:{
         b:{
           c:666
         }
       }
     })
     // 方法
     function changeName(){
       person.name += '~'
     }
     function changeAge(){
       person.age += 1
     }
     function changePerson(){
       //对象还是之前的对象，所以直接赋值不会触发监视
       Object.assign(person,{name:'李四',age:80})
     }
     function test(){
       obj.a.b.c = 888
     }
   
     // 监视，情况三：监视【reactive】定义的【对象类型】数据，且默认是开启深度监视的且取消不掉
     watch(person,(newValue,oldValue)=>{
       console.log('person变化了',newValue,oldValue)
     })
     watch(obj,(newValue,oldValue)=>{
       console.log('Obj变化了',newValue,oldValue)
     })
   </script>
   ```

4. 监视`ref`或`reactive`定义的【对象类型】数据中的**某个属性**，注意点如下：

   1. 若该属性值**不是**【对象类型】，需要写成函数形式。
   2. 若该属性值是**依然**是【对象类型】，可直接编，也可写成函数，建议写成函数。

   结论：监视的要是对象里的属性，那么最好写函数式，注意点：若是对象监视的是地址值，需要关注对象内部，需要手动开启深度监视。

   ```vue
   <template>
     <div class="person">
       <h1>情况四：监视【ref】或【reactive】定义的【对象类型】数据中的某个属性</h1>
       <h2>姓名：{{ person.name }}</h2>
       <h2>年龄：{{ person.age }}</h2>
       <h2>汽车：{{ person.car.c1 }}、{{ person.car.c2 }}</h2>
       <button @click="changeName">修改名字</button>
       <button @click="changeAge">修改年龄</button>
       <button @click="changeC1">修改第一台车</button>
       <button @click="changeC2">修改第二台车</button>
       <button @click="changeCar">修改整个车</button>
     </div>
   </template>
   
   <script lang="ts" setup name="Person">
     import {reactive,watch} from 'vue'
   
     // 数据
     let person = reactive({
       name:'张三',
       age:18,
       car:{
         c1:'奔驰',
         c2:'宝马'
       }
     })
     // 方法
     function changeName(){
       person.name += '~'
     }
     function changeAge(){
       person.age += 1
     }
     function changeC1(){
       person.car.c1 = '奥迪'
     }
     function changeC2(){
       person.car.c2 = '大众'
     }
     function changeCar(){
       person.car = {c1:'雅迪',c2:'爱玛'}
     }
   
     // 监视，情况四：监视响应式对象中的某个属性，且该属性是基本类型的，要写成函数式
     /* watch(()=> person.name,(newValue,oldValue)=>{
       console.log('person.name变化了',newValue,oldValue)
     }) */
   
     // 监视，情况四：监视响应式对象中的某个属性，且该属性是对象类型的，可以直接写，也能写函数，更推荐写函数
     watch(()=>person.car,(newValue,oldValue)=>{
       console.log('person.car变化了',newValue,oldValue)
     },{deep:true})
   </script>
   ```

5. 监视上述的多个数据

   ```vue
   <template>
     <div class="person">
       <h1>情况五：监视上述的多个数据</h1>
       <h2>姓名：{{ person.name }}</h2>
       <h2>年龄：{{ person.age }}</h2>
       <h2>汽车：{{ person.car.c1 }}、{{ person.car.c2 }}</h2>
       <button @click="changeName">修改名字</button>
       <button @click="changeAge">修改年龄</button>
       <button @click="changeC1">修改第一台车</button>
       <button @click="changeC2">修改第二台车</button>
       <button @click="changeCar">修改整个车</button>
     </div>
   </template>
   
   <script lang="ts" setup name="Person">
     import {reactive,watch} from 'vue'
   
     // 数据
     let person = reactive({
       name:'张三',
       age:18,
       car:{
         c1:'奔驰',
         c2:'宝马'
       }
     })
     // 方法
     function changeName(){
       person.name += '~'
     }
     function changeAge(){
       person.age += 1
     }
     function changeC1(){
       person.car.c1 = '奥迪'
     }
     function changeC2(){
       person.car.c2 = '大众'
     }
     function changeCar(){
       person.car = {c1:'雅迪',c2:'爱玛'}
     }
   
     // 监视，情况五：监视上述的多个数据
     watch([()=>person.name,()=>person.car],(newValue,oldValue)=>{
       console.log('person.car变化了',newValue,oldValue)
     },{deep:true})
   
   </script>
   ```

## watchEffect

watchEffect会**立即运行一个函数**，同时**响应式地追踪其依赖**，并在依赖更改时重新执行该函数。

`watch`对比`watchEffect`：

- **相同点**：都能监听响应式数据的变化
- **不同点**：是监听数据变化的方式不同
  1. `watch`：要明确指出监视的数据
  1. `watchEffect`：不用明确指出监视的数据（函数中用到哪些属性，那就监视哪些属性）。

```vue
<template>
  <div class="person">
    <h1>需求：水温达到50℃，或水位达到20cm，则联系服务器</h1>
    <h2 id="demo">水温：{{temp}}</h2>
    <h2>水位：{{height}}</h2>
    <button @click="changePrice">水温+1</button>
    <button @click="changeSum">水位+10</button>
  </div>
</template>

<script lang="ts" setup name="Person">
  import {ref,watch,watchEffect} from 'vue'
  // 数据
  let temp = ref(0)
  let height = ref(0)

  // 方法
  function changePrice(){
    temp.value += 10
  }
  function changeSum(){
    height.value += 1
  }

  // 用watch实现，需要明确的指出要监视：temp、height
  watch([temp,height],(value)=>{
    // 从value中获取最新的temp值、height值
    const [newTemp,newHeight] = value
    // 室温达到50℃，或水位达到20cm，立刻联系服务器
    if(newTemp >= 50 || newHeight >= 20){
      console.log('联系服务器')
    }
  })

  // 用watchEffect实现，不用
  const stopWatch = watchEffect(()=>{
    // 室温达到50℃，或水位达到20cm，立刻联系服务器
    if(temp.value >= 50 || height.value >= 20){
      console.log(document.getElementById('demo')?.innerText)
      console.log('联系服务器')
    }
    // 水温达到100，或水位达到50，取消监视
    if(temp.value === 100 || height.value === 50){
      console.log('清理了')
      stopWatch()
    }
  })
</script>
```

## 标签的 ref 属性

作用：用于注册模板引用。

用在普通`DOM`标签上，获取的是`DOM`节点：

当使用id 来获取DOM节点时，自定义组件和App组件id相同时，则会输出App组件的DOM节点：

> Person.vue

```vue
<template>
  <div class="person">
    <h1>你好</h1>
    <h2 id="title2">前端</h2>
    <h3>Vue</h3>
    <button @click="showLog">点我打印内容</button>
  </div>
</template>

<script lang="ts" setup name="Person">
function showLog(){
  // 通过id获取元素
  console.log(document.getElementById('title2'));
}
</script>
```

> App.vue

```vue
<!-- 编写模板结构 -->
<template>
  <div class="app">
    <h1 id="title2">你好 世界</h1>
    <Person/>
  </div>
</template>

<script setup lang="ts" name="App">
  import Person from "./components/person.vue"
</script>
```

App.vue 和 自定义组件中的template中的内容都会扭在一起，形成整个页面，id只能唯一，所以只打印了App.vue的id为title2的DOM元素

![image-20240207205914975](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402091442507.png)

使用标签中的ref属性可以解决该问题，将数据隔离：

> person.vue

```vue
<template>
  <div class="person">
    <h1>你好</h1>
<!--    <h2 id="title2">前端</h2>-->
    <h2 ref="title2">前端</h2>
    <h3>Vue</h3>
    <button @click="showLog">点我打印内容</button>
  </div>
</template>

<script lang="ts" setup name="Person">
import {ref} from "vue";

//变量名必须和ref中的名称一致
//创建一个title2,用于存储ref标记的内容
let title2 = ref()
function showLog(){
  // 通过id获取元素
  // console.log(document.getElementById('title2'));
  console.log(title2.value);
}
</script>
```

> App.vue

```vue
<!-- 编写模板结构 -->
<template>
  <div class="app">
    <h1 ref="title2">hello</h1>
    <button @click="showLog">点我打印内容</button>
    <Person/>
  </div>
</template>

<script setup lang="ts" name="App">
  import Person from "./components/person.vue"
  import {ref} from "vue";
  let title2 = ref();
  function  showLog() {
    console.log(title2.value)
  }
</script>
```

![image-20240207210941131](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402091447197.png)

用在组件标签上，获取的是组件实例对象：

> App.vue

```vue
<!-- 父组件App.vue -->
<template>
  <div class="app">
    <button @click="showLog">点我打印内容</button>
    <Person ref="ren"/>
  </div>
</template>

<script setup lang="ts" name="App">
  import Person from "./components/person.vue"
  import {ref} from "vue";
  let ren = ref();
  function showLog() {
    console.log(ren.value)
  }
</script>
```

打印取到组件的实例：

![image-20240207212000020](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402091443449.png)

在组件中设置三个值：

> person.vue

```vue
<template>
  <div class="person">
    <h1>{{a}}</h1>
    <h2>{{b}}</h2>
    <h3>{{c}}</h3>
  </div>
</template>

<script lang="ts" setup name="Person">
  let a = ref(0)
  let b = ref(1)
  let c = ref(2)
</script>
```

发现控制台并没有看到这三个值，这是因为存在保护措施，使用defineExpose暴露内容：

```vue
<template>
  <div class="person">
    <h1>{{a}}</h1>
    <h2>{{b}}</h2>
    <h3>{{c}}</h3>
  </div>
</template>

<script lang="ts" setup name="Person">
  let a = ref(0)
  let b = ref(1)
  let c = ref(2)
  // vue中要使用defineExpose暴露内容
  // 使用defineExpose将组件中的数据交给外部
  //defineExpose是宏函数，可以直接用，无需引入
  defineExpose({a,b})
</script>
```

![image-20240207212544477](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402091443856.png)

## props

> src/types/index.ts

```js
//定义接口 用于限制每个Person对象的具体属性格式
//使用分别暴露
export interface  PersonInter {
    id: string;
    name: string;
    age: number;
    gender?: string; // 可选属性
}
//定义常量 用于暴露给其他模块
export const a = 9;

//自定义类型：定义一个自定义类型Persons
//两种方式都可以
// export type Persons = Array<PersonInter>;
export type Persons = PersonInter[];
```

> App.vue
>

```vue
<!-- 编写模板结构 -->
<template>
<!--  :list : 表达式-->
    <Person a="哈哈" b="嘿嘿" :list="personList"/>
<!-- 输入错误时，并没有展示想要的数据 如果v-for写的指定的数字 则循环多少次-->
<!--    <Person a="哈哈" b="嘿嘿" :list="5"/>-->
</template>
<!-- 编写脚本代码 -->
<script setup lang="ts" name="App">
import Person from "./components/person.vue"

//@代表src目录
//PersonInter不是一个具体的值,而是一个接口(类型) 前缀需要添加type
import {type PersonInter,a,type Persons} from '@/types'
import {reactive} from "vue";
console.log(a)
//对person进行限制：定义一个person变量，必须符合PersonInter接口的规范
// let person:PersonInter = {id: "zs1", name:'张三', age: 18, gender: '男'}

//定义一个数组，必须符合PersonInter接口的规范
//方式一：使用Array泛型为PersonInter 每一项都是PersonInter类型
// let personList:Array<PersonInter> = [
//     {id: "zs1", name:'张三', age: 18, gender: '男'},
//     {id: "ls1", name:'李四', age: 20, gender: '女'},
// ]
//方式二：使用自定义类型
// let personList2:Persons = [
//   {id: "zs1", name:'张三', age: 18, gender: '男'},
//   {id: "ls1", name:'李四', age: 20, gender: '女'},
// ]
//响应式 调用函数时传入泛型
let personList = reactive<Persons>( [
  {id: "zs1", name:'张三', age: 18, gender: '男'},
  {id: "ls1", name:'李四', age: 20, gender: '女'},
])
</script>
<!-- 样式 -->
<style scoped>
/* css */
</style>
```

> Person.vue

```Vue
<template>
  <div class="person">
<!--    <h2>{{a}}</h2>-->
<!--    <h2>{{x.a}}</h2>-->
<!--    <h2 >{{list}}</h2>-->
    <ul>
      <li v-for="person in list" :key="person.id">
        {{person.name}}- {{person.age}}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts" name="Person">
//defineProps是宏函数，可以直接用，无需引入
// import { defineProps } from 'vue';
import {type Persons} from '@/types'

// todo 只接收a
// defineProps(["a","list"])
// todo 接收所有的接收的数据 并将props保存
// let x = defineProps(['a','list']);
// 由于没有传入c 所以c为undefined
// let x = defineProps(["a", "b", "c"]);
// console.log(x)
// console.log(x.a)
// todo 接收list并限制类型
// defineProps<{list: Persons}>()

// todo 接收+限制类型+指定默认值+限制必要性
let props = withDefaults(defineProps<{list?:Persons}>(),{
  //需要是一个函数 返回值
  list:()=>[{id:'pq',name:'小猪佩奇',age:18}]
})
console.log(props)
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

## 生命周期

概念：`Vue`组件实例在创建时要经历一系列的初始化步骤，在此过程中`Vue`会在合适的时机，调用特定的函数，从而让开发者有机会在特定阶段运行自己的代码，这些特定的函数统称为：**生命周期钩子**(声明周期函数)

规律：生命周期整体分为四个阶段，分别是：**创建、挂载、更新、销毁**，每个阶段都有两个钩子，一前一后。

`Vue2`的生命周期：

- 创建阶段：`beforeCreate`(创建前)、`created`(创建完毕)


- 挂载阶段：`beforeMount`(挂载前)、`mounted`(挂载完毕)


- 更新阶段：`beforeUpdate`(更新前)、`updated`(更新完毕)


- 销毁阶段：`beforeDestroy`(销毁前)、`destroyed`(销毁完毕)

`Vue3`的生命周期：

- 创建阶段：`setup`


- 挂载阶段：`onBeforeMount`(挂载前)、`onMounted`(挂载完毕)


- 更新阶段：`onBeforeUpdate`(更新前)、`onUpdated`(更新完毕)


- 卸载阶段：`onBeforeUnmount`(卸载前)、`onUnmounted`(卸载完毕)

常用的钩子：`onMounted`(挂载完毕)、`onUpdated`(更新完毕)、`onBeforeUnmount`(卸载之前)


```vue
<template>
  <div class="person">
    <h2>当前求和为：{{ sum }}</h2>
    <button @click="changeSum">点我sum+1</button>
  </div>
</template>

<!-- vue3写法 -->
<script lang="ts" setup name="Person">
  import { 
    ref, 
    onBeforeMount, 
    onMounted, 
    onBeforeUpdate, 
    onUpdated, 
    onBeforeUnmount, 
    onUnmounted 
  } from 'vue'

  // 数据
  let sum = ref(0)
  // 方法
  function changeSum() {
    sum.value += 1
  }
  console.log('setup')
  // 生命周期钩子
  onBeforeMount(()=>{
    console.log('挂载之前')
  })
  onMounted(()=>{
    console.log('挂载完毕')
  })
  onBeforeUpdate(()=>{
    console.log('更新之前')
  })
  onUpdated(()=>{
    console.log('更新完毕')
  })
  onBeforeUnmount(()=>{
    console.log('卸载之前')
  })
  onUnmounted(()=>{
    console.log('卸载完毕')
  })
</script>
```

## 自定义hook

`hook`：本质是一个函数，把`setup`函数中使用的`Composition API`进行了封装，类似于`vue2.x`中的`mixin`。

**自定义`hook`的优势**：复用代码, 让`setup`中的逻辑更清楚易懂。

**说明**：命名最好以`useXxx`命名，Xxx为具体的功能。

> useSum.ts

```js
import {ref,onMounted} from 'vue'

export default function(){
  let sum = ref(0)

  const increment = ()=>{
    sum.value += 1
  }
  const decrement = ()=>{
    sum.value -= 1
  }
  onMounted(()=>{
    increment()
  })

  //向外部暴露数据
  return {sum,increment,decrement}
}		
```

安装axios：

```bash
npm i axios
```

> useDog.ts

```js
import {reactive,onMounted} from 'vue'
import axios,{AxiosError} from 'axios'

export default function(){
  let dogList = reactive<string[]>([])

  // 方法
  async function getDog(){
    try {
      // 发请求
      let {data} = await axios.get('https://dog.ceo/api/breed/pembroke/images/random')
      // 维护数据
      dogList.push(data.message)
    } catch (error) {
      // 处理错误
      const err = <AxiosError>error
      console.log(err.message)
    }
  }

  // 挂载钩子
  onMounted(()=>{
    getDog()
  })
	
  //向外部暴露数据
  return {dogList,getDog}
}
```

组件中具体使用：

```vue
<template>
  <div class="person">
    <h2>当前求和为：{{sum}}，放大10倍后{{bigSum}}</h2>
    <button @click="increment">点我+1</button>
    <button @click="decrement">点我-1</button>
    <hr>
    <img v-for="(u,index) in dogList" :key="index" :src="(u as string)">
    <br>
    <button @click="getDog">再来一只狗</button>
  </div>
</template>

<script setup lang="ts" name="Person">
  import useSum from '@/hooks/useSum'
  import useDog from '@/hooks/useDog'

  let {sum,bigSum,increment,decrement} = useSum()
  let {dogList,getDog} = useDog()
</script>
```