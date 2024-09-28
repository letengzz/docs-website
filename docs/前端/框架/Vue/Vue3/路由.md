# Vue3 路由

路由(Route)是一组key-value的对应关系。多个路由，需要经过路由器(Router)的管理

在单页面(SPA，`single page web application`)应用中，点击导航区不同的导航项就会在展示区展示不同的内容

整个过程中，页面是不抖动的，没有进行页面的跳转。

当点击一个导航项时，地址的路径发生变化，路由器监测到路径变化就会进行规则的匹配，若匹配上 则会出现在展示区。只要路径发生变化会在第一时间捕获到去寻找规则 把之前装载的组件进行卸载 把匹配上的组件进行挂载。

`Vue3`中要使用`vue-router`的最新版本，目前是`4`版本。

官方网站：https://router.vuejs.org/zh/ 

## 基本切换效果

安装vue 路由：

```bash
npm i vue-router
```

编写组件：

**说明**：路由组件(靠路由的规则渲染出来的)通常存放在`pages` 或 `views`文件夹，一般组件通常存放在`components`文件夹。

- 一般组件：

  > /src/components/Header.vue

  ```vue
  <script setup lang="ts">
  
  </script>
  
  <template>
    <h2 class="title">Vue 路由测试</h2>
  </template>
  
  <style scoped>
  .title {
    text-align: center;
    word-spacing: 5px;
    margin: 30px 0;
    height: 70px;
    line-height: 70px;
    background-image: linear-gradient(45deg, rgb(128, 128, 128), white);
    border-radius: 10px;
    box-shadow: 0 0 2px;
    font-size: 30px;
  }
  </style>
  ```

- 路由组件：

  > /src/views/About.vue

  ```vue
  <template>
    <div class="about">
      <h2>Vue 路由Router</h2>
    </div>
  </template>
  <script setup lang="ts" name="About">
  
  </script>
  
  <style scoped>
  .about {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: rgb(85, 84, 84);
    font-size: 18px;
  }
  </style>
  ```

  > /src/views/Home.vue

  ```vue
  <template>
    <div class="home">
      <img src="https://vuejs.org/images/logo.png" alt="Vue logo">
    </div>
  </template>
  <script setup lang="ts" name="Home">
  
  import {onMounted, onUnmounted} from "vue";
  
  onMounted(()=>{
    console.log('Home组件被挂载了')
  })
  onUnmounted(()=>{
    console.log('Home组件被卸载了')
  })
  </script>
  
  
  <style scoped>
  .home {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
  }
  </style>
  ```

  > /src/views/News.vue

  ```vue
  <template>
    <div class="news">
      <ul>
        <li><a href="#">新闻001</a></li>
        <li><a href="#">新闻002</a></li>
        <li><a href="#">新闻003</a></li>
        <li><a href="#">新闻004</a></li>
      </ul>
    </div>
  </template>
  <script setup lang="ts" name="News">
  
  </script>
  
  <style scoped>
  /* 新闻 */
  .news {
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    height: 100%;
  }
  .news ul {
    margin-top: 30px;
    list-style: none;
    padding-left: 10px;
  }
  .news li>a {
    font-size: 18px;
    line-height: 40px;
    text-decoration: none;
    color: #64967E;
    text-shadow: 0 0 1px rgb(0, 84, 0);
  }
  .news-content {
    width: 70%;
    height: 90%;
    border: 1px solid;
    margin-top: 20px;
    border-radius: 10px;
  }
  </style>
  ```

路由配置文件：

> /src/router/index.ts

```typescript
// 创建一个路由器，并暴露出去

//第一步：引入createRouter
import {createRouter, createWebHistory} from 'vue-router';
//引入可能要呈现的组件
import Home from '@/views/Home.vue';
import About from '@/views/About.vue';
import News from "@/views/News.vue";

//第二步：创建路由器
const router = createRouter({
    // 路由器工作模式
    //在制定路由的之后 一定要想好路由器的工作模式
    history: createWebHistory(),
    //配置路由规则
    routes: [
        // 配置路由
        {
            // 路由路径
            path: '/home',
            //组件
            component: Home
        },
        {
            path: '/about',
            component: About
        },
        {
            path: '/news',
            component: News
        }
    ]
});

//暴露router
export default router;
```

使用router路由器：

> main.ts

```typescript
// 引入createApp用于创建应用
import { createApp } from 'vue'
// 引入App根组件
import App from './App.vue'
// 引入Router路由器
import router from './router'

//创建一个应用
const app = createApp(App);
//使用router路由器
app.use(router);
//挂载整个应用到app容器中
app.mount('#app')
```

> App.vue

```vue
<template>
  <div class="app">
    <!-- 标题 -->
    <Header />
    <!-- 导航栏 -->
    <div class="navigate">
      <!--      <a href="#" class="active">首页</a>-->
      <!--      <a href="#">新闻</a>-->
      <!--      <a href="#">关于</a>-->
      <!-- 跳转路径 to：跳转的路径 active-class 点击呈现的class样式-->
      <RouterLink to="/home" active-class="active">首页</RouterLink>
      <RouterLink to="/news" active-class="active">新闻</RouterLink>
      <RouterLink to="/about" active-class="active">关于</RouterLink>
    </div>
    <!-- 展示区 -->
    <div class="main-content">
      <!-- 此处根据路径展示各种组件 -->
      <!-- 路由器视图 把路由的内容展示到这-->
      <RouterView></RouterView>
    </div>
  </div>
</template>
<script setup lang="ts">
import {RouterLink, RouterView} from 'vue-router'
import Header from "@/components/Header.vue";
</script>

<style scoped>
/* App */

.navigate {
  display: flex;
  justify-content: space-around;
  margin: 0 100px;
}

.navigate a {
  display: block;
  text-align: center;
  width: 90px;
  height: 40px;
  line-height: 40px;
  border-radius: 10px;
  background-color: rgb(128, 128, 128);
  text-decoration: none;
  color: white;
  font-size: 18px;
  letter-spacing: 5px;
}

.navigate a.active {
  background-color: #259039;
  color: #bcaf14;
  font-weight: 900;
  text-shadow: 0 0 1px black;
  font-family: 微软雅黑, serif;
}

.main-content {
  margin: 0 auto;
  margin-top: 30px;
  border-radius: 10px;
  width: 90%;
  height: 400px;
  border: 1px solid;
}
</style>
```

![image-20240210140017360](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402111349186.png)

通过点击导航，视觉效果上“消失” 了的路由组件，默认是被**卸载**掉的，需要的时候再去**挂载**：

![image-20240210141040400](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402111349876.png)

## 路由器工作模式

`history`模式

- 优点：`URL`更加美观，不带有`#`，更接近传统的网站`URL`。

- 缺点：后期项目上线，需要服务端配合处理路径问题，否则刷新会有`404`错误。

  ```js
  const router = createRouter({
  	history:createWebHistory(), //history模式
  	/******/
  })
  ```

`hash`模式

- 优点：兼容性更好，因为不需要服务器端处理路径。


- 缺点：`URL`带有`#`不太美观，且在`SEO`优化方面相对较差。

  ```js
  const router = createRouter({
  	history:createWebHashHistory(), //hash模式
  	/******/
  })
  ```

![image-20240210141410326](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202402111350315.png)

## to的两种写法

```vue
<!-- 第一种：to的字符串写法 -->
<RouterLink to="/home" active-class="active">首页</RouterLink>
<RouterLink to="/news" active-class="active">新闻</RouterLink>
<RouterLink to="/about" active-class="active">关于</RouterLink>

<!-- 第二种：to的对象写法 -->
<RouterLink :to="{path:'/home'}" active-class="active">首页</RouterLink>
<RouterLink :to="{path:'/news'}" active-class="active">新闻</RouterLink>
<RouterLink :to="{path:'/about'}" active-class="active">关于</RouterLink>
```

## 命名路由

作用：可以简化路由跳转及传参。

给路由规则命名：

```js
const router = createRouter({
    // 路由器工作模式
    history: createWebHistory(),
    //配置路由规则
    routes: [
        // 配置路由
        {
            // 路由名称
            name:'zy',
            // 路由路径
            path: '/home',
            //组件
            component: Home
        },
        {
            // 路由名称
            name:'gy',
            path: '/about',
            component: About
        },
        {
            // 路由名称
            name:'xw',
            path: '/news',
            component: News
        }
    ]
});
```

跳转路由：

```vue
<!--简化前：需要写完整的路径（to的字符串写法） -->
<RouterLink to="/home" active-class="active">首页</RouterLink>
<RouterLink to="/news" active-class="active">新闻</RouterLink>
<RouterLink to="/about" active-class="active">关于</RouterLink>

<!--简化后：直接通过名字跳转（to的对象写法配合name属性） -->
<RouterLink :to="{name:'zy'}" active-class="active">首页</RouterLink>
<RouterLink :to="{name:'xw'}" active-class="active">新闻</RouterLink>
<RouterLink :to="{name:'gy'}" active-class="active">关于</RouterLink>
```

## 嵌套路由

1. 编写`News`的子路由

   > Detail.vue

   ```vue
   <template>
     <ul class="news-list">
       <li>编号：xxx</li>
       <li>标题：xxx</li>
       <li>内容：xxx</li>
     </ul>
   </template>
   
   <script setup lang="ts" name="About">
   
   </script>
   
   <style scoped>
     .news-list {
       list-style: none;
       padding-left: 20px;
     }
   
     .news-list>li {
       line-height: 30px;
     }
   </style>
   ```

2. 配置路由规则，使用`children`配置项：

   > /src/router/index.ts

   ```ts
   // 创建一个路由器，并暴露出去
   
   //第一步：引入createRouter
   import {createRouter, createWebHashHistory, createWebHistory} from 'vue-router';
   //引入可能要呈现的组件
   import Home from '@/views/Home.vue';
   import About from '@/views/About.vue';
   import News from "@/views/News.vue";
   import Detail from "@/views/Detail.vue";
   
   //第二步：创建路由器
   const router = createRouter({
       // 路由器工作模式
       //在制定路由的之后 一定要想好路由器的工作模式
       history: createWebHistory(),
       //配置路由规则
       routes: [
           // 配置路由
           {
               // 路由名称
               name: 'sy',
               // 路由路径
               path: '/home',
               //组件
               component: Home
           },
           {
               // 路由名称
               name: 'gy',
               path: '/about',
               component: About
           },
           {
               // 路由名称
               name: 'xw',
               path: '/news',
               component: News,
               children: [
                   {
                       name: 'detail',
                       //注意 不用写 '/'
                       path: 'detail',
                       // component: () => import('@/views/Detail.vue')
                       component: Detail
                   }
               ]
           }
       ]
   });
   
   //暴露router
   export default router;
   ```

3. 跳转路由（记得要加完整路径）：

   > /src/views/News.vue

   ```vue
   <template>
     <div class="news">
       <!-- 导航区 -->
       <ul>
         <li v-for="news in newList" :key="news.id">
           <RouterLink to="/news/detail">{{news.title}}</RouterLink>
           <!-- 或 -->
           <RouterLink :to="{path:'/news/detail'}">{{news.title}}</RouterLink>
         </li>
       </ul>
       <!-- 展示区 -->
       <div class="news-content">
         <RouterView></RouterView>
       </div>
     </div>
   </template>
   <script setup lang="ts" name="News">
   import {reactive} from "vue";
   
   const newList = reactive([
     {id: 'new001', title: '新闻01', content: '新闻001内容'},
     {id: 'new002', title: '新闻02', content: '新闻002内容'},
     {id: 'new003', title: '新闻03', content: '新闻003内容'},
     {id: 'new004', title: '新闻04', content: '新闻004内容'}
   ])
   </script>
   
   <style scoped>
   /* 新闻 */
   .news {
     padding: 0 20px;
     display: flex;
     justify-content: space-between;
     height: 100%;
   }
   
   .news ul {
     margin-top: 30px;
     list-style: none;
     padding-left: 10px;
   }
   
   .news li > a {
     font-size: 18px;
     line-height: 40px;
     text-decoration: none;
     color: #64967E;
     text-shadow: 0 0 1px rgb(0, 84, 0);
   }
   
   .news-content {
     width: 70%;
     height: 90%;
     border: 1px solid;
     margin-top: 20px;
     border-radius: 10px;
   }
   </style>
   ```

## 路由传参

### query参数

   1. 传递参数

      ```vue
      <template>
        <div class="news">
          <!-- 导航区 -->
          <ul>
            <li v-for="news in newList" :key="news.id">
              <!-- 跳转并携带query参数（to的字符串写法） -->
              <RouterLink
                  :to="`/news/detail?id=${news.id}&title=${news.title}&content=${news.content}`"
              >
                {{ news.title }}
              </RouterLink>
      
              <!-- 跳转并携带query参数（to的对象写法） -->
              <RouterLink
                  :to="{
                    path:'/news/detail',
                    query:{
                      id:news.id,
                      title:news.title,
                      content:news.content
                    }}">
                {{news.title}}
              </RouterLink>
      
            </li>
          </ul>
          <!-- 展示区 -->
          <div class="news-content">
            <RouterView></RouterView>
          </div>
        </div>
      </template>
      <script setup lang="ts" name="News">
      import {reactive} from "vue";
      
      const newList = reactive([
        {id: 'new001', title: '新闻01', content: '新闻001内容'},
        {id: 'new002', title: '新闻02', content: '新闻002内容'},
        {id: 'new003', title: '新闻03', content: '新闻003内容'},
        {id: 'new004', title: '新闻04', content: '新闻004内容'}
      ])
      </script>
      ```

   2. 接收参数：

      ```vue
      <template>
        <ul class="news-list">
      <!--    <li>编号：{{ route.query.id }}</li>-->
      <!--    <li>标题：{{ route.query.title }}</li>-->
      <!--    <li>内容：{{ route.query.content }}</li>-->
          <li>编号：{{ query.id }}</li>
          <li>标题：{{ query.title }}</li>
          <li>内容：{{ query.content }}</li>
        </ul>
      </template>
      
      <script setup lang="ts" name="Detail">
        import {useRoute} from "vue-router";
        import {toRefs} from "vue";
      
        let route = useRoute();
        console.log(route)
        // 打印query参数
        console.log(route.query)
        let {query} = toRefs(route);
      </script>
      ```

### params参数

**说明**：

- 传递`params`参数时，若使用`to`的对象写法，必须使用`name`配置项，不能用`path`。

- 传递`params`参数时，需要提前在规则中占位。

****

   1. 设置匹配规则：

      ```typescript
      const router = createRouter({
          // 路由器工作模式
          //在制定路由的之后 一定要想好路由器的工作模式
          history: createWebHistory(),
          //配置路由规则
          routes: [
              // 配置路由
              {
                  // 路由名称
                  name: 'xw',
                  path: '/news',
                  component: News,
                  children: [
                      {
                          name: 'detail',
                          //注意 不用写/
                          //加? 可传可不传 配置传入的必要性
                          path: 'detail/:id/:title/:content?',
                          // component: () => import('@/views/Detail.vue')
                          component: Detail
                      }
                  ]
              }
          ]
      });
      ```

   2. 传递参数：

      ```vue
      <template>
        <div class="news">
          <!-- 导航区 -->
          <ul>
            <li v-for="news in newList" :key="news.id">
              <!-- 跳转并携带params参数（to的字符串写法） -->
              <RouterLink :to="`/news/detail/${news.id}/${news.title}/${news.content}`">
                {{ news.title }}
              </RouterLink>
              <!-- 或 -->
              <!-- 跳转并携带params参数（to的对象写法） -->
              <RouterLink
                  :to="{
                    //必须使用名字进行匹配
                    name:'detail',
                    //传入的不能是对象和数组
                    params:{
                      id:news.id,
                      title:news.title,
                      content:news.content
                    }
                  }"
              >
                {{ news.title }}
              </RouterLink>
            </li>
          </ul>
          <!-- 展示区 -->
          <div class="news-content">
            <RouterView></RouterView>
          </div>
        </div>
      </template>
      ```

   3. 接收参数：

      ```vue
      <template>
        <ul class="news-list">
          <!--    <li>编号：{{route.params.id }}</li>-->
          <!--    <li>标题：{{route.params.title }}</li>-->
          <!--    <li>内容：{{route.params.content }}</li>-->
          <li>编号：{{ params.id }}</li>
          <li>标题：{{ params.title }}</li>
          <li>内容：{{ params.content }}</li>
        </ul>
      </template>
      
      <script setup lang="ts" name="About">
        import {useRoute} from 'vue-router'
        import {toRefs} from "vue";
      
        const route = useRoute()
        let {params} = toRefs(route);
        // 打印params参数
        console.log(route.params)
      </script>
      ```

## 路由的props配置

作用：让路由组件更方便的收到参数（可以将路由参数作为`props`传给组件）

```js
const router = createRouter({
    // 路由器工作模式
    //在制定路由的之后 一定要想好路由器的工作模式
    history: createWebHistory(),
    //配置路由规则
    routes: [
        // 配置路由
        {
            // 路由名称
            name: 'xw',
            path: '/news',
            component: News,
            children: [
                {
                    name: 'detail',
                    //params path
                    // path: 'detail/:id/:title/:content?',
                    //query path
                    path: 'detail',
                    component: Detail,
                    // props的对象写法，作用：把对象中的每一组key-value作为props传给Detail组件(只限于params)
                    // props:{id:1,title:2,content:3}
                    // props的布尔值写法，作用：把收到了每一组params参数，作为props传给Detail组件(只限于params)
                    // props:true
                    // props的函数写法，作用：把返回的对象中每一组key-value作为props传给Detail组件(可以用作params和query)
                    props(route){
                        // return route.params
                        return route.query
                    }
                }
            ]
        }
    ]
});
```

接收参数：

```vue
<template>
  <ul class="news-list">
    <li>编号：{{ id }}</li>
    <li>标题：{{ title }}</li>
    <li>内容：{{ content }}</li>
  </ul>
</template>

<script setup lang="ts" name="About">
  defineProps(['id', 'title', 'content'])
</script>
```

## replace属性

作用：控制路由跳转时操作浏览器历史记录的模式。

浏览器的历史记录有两种写入方式：分别为```push```和```replace```：

- ```push```是追加历史记录（默认值）。
- `replace`是替换当前记录。

开启`replace`模式：

```vue
<RouterLink replace .......>News</RouterLink>
```

## 编程式路由导航

编程式路由导航：脱离`<RouterLink>`实现路由跳转

路由组件的两个重要的属性：`$route`和`$router`变成了两个`hooks`

```js
import {useRoute,useRouter} from 'vue-router'

const route = useRoute()
const router = useRouter()

console.log(route.query)
console.log(route.parmas)
console.log(router.push)
console.log(router.replace)
```

点击按钮跳转路由：

```vue
<template>
  <div class="news">
    <!-- 导航区 -->
    <ul>
      <li v-for="news in newList" :key="news.id">
        <button @click="showNewsDetail(news)">点击跳转</button>
        <!-- 跳转并携带query参数（to的对象写法） -->
        <RouterLink
            :to="{
              path:'/news/detail',
              query:{
                id:news.id,
                title:news.title,
                content:news.content
              }}">
          {{news.title}}
        </RouterLink>

      </li>
    </ul>
    <!-- 展示区 -->
    <div class="news-content">
      <RouterView></RouterView>
    </div>
  </div>
</template>
<script setup lang="ts" name="News">
import {onMounted, reactive} from "vue";
import {useRoute, useRouter} from "vue-router";

const newList = reactive([
  {id: 'new001', title: '新闻01', content: '新闻001内容'},
  {id: 'new002', title: '新闻02', content: '新闻002内容'},
  {id: 'new003', title: '新闻03', content: '新闻003内容'},
  {id: 'new004', title: '新闻04', content: '新闻004内容'}
])

const router = useRouter();
interface  NewsInter {
  id:string,
  title:string,
  content:string
}
function showNewsDetail(news:NewsInter){
  router.push({
    path:'/news/detail',
    query:{
      id:news.id,
      title:news.title,
      content:news.content
    }})
}
</script>
```

## 重定向

作用：将特定的路径，重新定向到已有路由。

```js
{
    path:'/',
    redirect:'/about'
}
```

