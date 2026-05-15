# vue-resource

vue-resource 是 Vue.js 的 HTTP 客户端插件，用于发送 AJAX 请求。

- GitHub：https://github.com/pagekit/vue-resource

::: danger 注意事项
- vue-resource 已停止维护
- 官方推荐使用 axios 替代
- 本文档仅供学习参考
:::

## 安装

```bash
npm install vue-resource
```

## 基本使用

```html [basic.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>vue-resource</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vue-resource/dist/vue-resource.min.js"></script>
</head>
<body>
  <div id="app">
    <button @click="getData">获取数据</button>
    <p>{{ message }}</p>
  </div>
</body>
<script>
  Vue.use(VueResource)

  const vm = new Vue({
    data: {
      message: ''
    },
    methods: {
      getData() {
        this.$http.get('https://jsonplaceholder.typicode.com/posts/1')
          .then(response => {
            this.message = response.body.title
          })
          .catch(error => {
            console.error('请求失败:', error)
          })
      }
    },
    el: '#app'
  })
</script>
</html>
```

## GET 请求

```javascript [get.js]
// 基本 GET 请求
this.$http.get('/api/users').then(response => {
  console.log(response.body)
})

// 带参数的 GET 请求
this.$http.get('/api/users', {
  params: {
    page: 1,
    limit: 10
  }
}).then(response => {
  console.log(response.body)
})
```

## POST 请求

```javascript [post.js]
// 基本 POST 请求
this.$http.post('/api/users', {
  name: '张三',
  age: 18
}).then(response => {
  console.log('创建成功:', response.body)
})

// 设置请求头
this.$http.post('/api/users', {
  name: '张三'
}, {
  headers: {
    'Content-Type': 'application/json'
  }
}).then(response => {
  console.log('创建成功:', response.body)
})
```

## PUT 请求

```javascript [put.js]
// 更新资源
this.$http.put('/api/users/1', {
  name: '李四',
  age: 20
}).then(response => {
  console.log('更新成功:', response.body)
})
```

## DELETE 请求

```javascript [delete.js]
// 删除资源
this.$http.delete('/api/users/1').then(response => {
  console.log('删除成功:', response.body)
})
```

## JSONP 请求

```html [jsonp.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JSONP 请求</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/vue-resource/dist/vue-resource.min.js"></script>
</head>
<body>
  <div id="app">
    <button @click="getJsonp">JSONP 请求</button>
    <p>{{ message }}</p>
  </div>
</body>
<script>
  Vue.use(VueResource)

  const vm = new Vue({
    data: {
      message: ''
    },
    methods: {
      getJsonp() {
        this.$http.jsonp('https://api.example.com/data', {
          params: {},
          jsonp: 'callback'
        }).then(response => {
          this.message = JSON.stringify(response.body)
        })
      }
    },
    el: '#app'
  })
</script>
</html>
```

## 全局配置

```javascript [global-config.js]
// 设置根 URL
Vue.http.options.root = '/api'

// 设置请求头
Vue.http.headers.common['Authorization'] = 'Bearer token'

// 设置超时时间
Vue.http.options.timeout = 5000
```

## 拦截器

```javascript [interceptor.js]
Vue.http.interceptors.push((request, next) => {
  // 请求前处理
  console.log('请求 URL:', request.url)
  
  // 继续请求
  next((response) => {
    // 响应后处理
    console.log('响应状态:', response.status)
    return response
  })
})
```

::: tip 提示
- vue-resource 已停止维护
- 推荐使用 axios 作为替代
- axios 功能更强大，社区更活跃
- 新项目建议使用 axios 或 fetch API
:::
