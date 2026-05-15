# Vue Router

Vue Router 是 Vue.js 官方的路由管理器。

- 官方文档：https://router.vuejs.org/zh/

## 安装

```bash
npm install vue-router@3
```

## 基本使用

```html [basic.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Vue Router</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vue-router@3/dist/vue-router.js"></script>
</head>
<body>
  <div id="app">
    <h1>Hello App!</h1>
    <p>
      <router-link to="/">首页</router-link>
      <router-link to="/about">关于</router-link>
    </p>
    <router-view></router-view>
  </div>
</body>
<script>
  const Home = { template: '<div>首页</div>' }
  const About = { template: '<div>关于</div>' }

  const routes = [
    { path: '/', component: Home },
    { path: '/about', component: About }
  ]

  const router = new VueRouter({
    routes
  })

  const vm = new Vue({
    router,
    el: '#app'
  })
</script>
</html>
```

## 动态路由匹配

```html [dynamic-routes.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>动态路由</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vue-router@3/dist/vue-router.js"></script>
</head>
<body>
  <div id="app">
    <router-link to="/user/1">用户 1</router-link>
    <router-link to="/user/2">用户 2</router-link>
    <router-view></router-view>
  </div>
</body>
<script>
  const User = {
    template: '<div>用户 ID: {{ $route.params.id }}</div>'
  }

  const routes = [
    { path: '/user/:id', component: User }
  ]

  const router = new VueRouter({
    routes
  })

  const vm = new Vue({
    router,
    el: '#app'
  })
</script>
</html>
```

## 嵌套路由

```html [nested-routes.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>嵌套路由</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vue-router@3/dist/vue-router.js"></script>
</head>
<body>
  <div id="app">
    <router-link to="/user/1">用户</router-link>
    <router-view></router-view>
  </div>
</body>
<script>
  const UserHome = { template: '<div>用户主页</div>' }
  const UserProfile = { template: '<div>用户资料</div>' }

  const User = {
    template: `
      <div>
        <h2>用户组件</h2>
        <router-link to="/user/1/home">主页</router-link>
        <router-link to="/user/1/profile">资料</router-link>
        <router-view></router-view>
      </div>
    `
  }

  const routes = [
    {
      path: '/user/:id',
      component: User,
      children: [
        { path: 'home', component: UserHome },
        { path: 'profile', component: UserProfile }
      ]
    }
  ]

  const router = new VueRouter({
    routes
  })

  const vm = new Vue({
    router,
    el: '#app'
  })
</script>
</html>
```

## 编程式导航

```javascript [programmatic-navigation.js]
// 字符串路径
router.push('/home')

// 对象路径
router.push({ path: '/home' })

// 带参数
router.push({ path: '/user', query: { id: 1 } })

// 命名路由
router.push({ name: 'user', params: { id: 1 } })

// 前进/后退
router.go(1)    // 前进 1 步
router.go(-1)   // 后退 1 步
router.forward()
router.back()
```

## 路由守卫

```javascript [navigation-guards.js]
const router = new VueRouter({
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要登录
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

// 全局后置守卫
router.afterEach((to, from) => {
  // 页面加载完成后执行
  console.log('导航完成')
})

export default router
```

## 路由元信息

```javascript [meta.js]
const routes = [
  {
    path: '/dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, title: '仪表盘' }
  },
  {
    path: '/login',
    component: Login,
    meta: { requiresAuth: false, title: '登录' }
  }
]
```

::: tip 提示
- Vue Router 3 对应 Vue 2
- Vue Router 4 对应 Vue 3
- 使用 router-link 进行导航
- 使用 router-view 渲染匹配的组件
- 编程式导航使用 router.push()
:::
