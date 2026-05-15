# 使用脚手架操作

Vue CLI 是 Vue 官方的脚手架工具。

- 官方文档：https://cli.vuejs.org/zh/

## 安装 Vue CLI

```bash
npm install -g @vue/cli
```

## 创建项目

```bash
vue create my-project
```

### 选择预设

```
Vue CLI v4.5.0
? Please pick a preset:
  Default ([Vue 2] babel, eslint)
  Default (Vue 3) ([Vue 3] babel, eslint)
> Manually select features
```

### 手动选择功能

```
? Check the features needed for your project:
 (*) Babel
 ( ) TypeScript
 ( ) Progressive Web App (PWA) Support
 (*) Router
 (*) Vuex
 (*) CSS Pre-processors
 (*) Linter / Formatter
 ( ) Unit Testing
 ( ) E2E Testing
```

### 选择 Vue 版本

```
? Choose a version of Vue.js that you want to start the project with
  3.x
> 2.x
```

## 项目结构

```
my-project/
├── node_modules/
├── public/
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── assets/
│   ├── components/
│   ├── router/
│   │   └── index.js
│   ├── store/
│   │   └── index.js
│   ├── views/
│   ├── App.vue
│   └── main.js
├── .gitignore
├── babel.config.js
├── package.json
└── vue.config.js
```

## 运行项目

```bash
# 进入项目目录
cd my-project

# 启动开发服务器
npm run serve

# 构建生产版本
npm run build

# 运行 lint
npm run lint
```

## vue.config.js 配置

```javascript [vue.config.js]
module.exports = {
  // 基本路径
  publicPath: '/',
  
  // 输出文件目录
  outputDir: 'dist',
  
  // 静态资源目录
  assetsDir: 'static',
  
  // 关闭 source map
  productionSourceMap: false,
  
  // 开发服务器配置
  devServer: {
    port: 8080,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      }
    }
  },
  
  // CSS 相关配置
  css: {
    loaderOptions: {
      less: {
        javascriptEnabled: true
      }
    }
  }
}
```

## 环境变量

```bash
# .env.development
VUE_APP_API_URL=http://localhost:3000/api

# .env.production
VUE_APP_API_URL=https://api.example.com
```

```javascript [use-env.js]
// 在代码中使用
const apiUrl = process.env.VUE_APP_API_URL
```

## 路由配置

```javascript [router/index.js]
import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
```

## Vuex 配置

```javascript [store/index.js]
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    count: 0
  },
  mutations: {
    increment(state) {
      state.count++
    }
  },
  actions: {
    incrementAsync({ commit }) {
      setTimeout(() => {
        commit('increment')
      }, 1000)
    }
  },
  modules: {}
})
```

## 常用命令

```bash
# 查看 Vue CLI 版本
vue --version

# 升级 Vue CLI
npm update -g @vue/cli

# 创建项目
vue create my-project

# 添加插件
vue add eslint

# 检查项目问题
vue ui
```

::: tip 提示
- Vue CLI 4.x 支持 Vue 2 和 Vue 3
- 推荐使用手动选择功能创建项目
- vue.config.js 用于自定义配置
- 使用环境变量管理不同环境的配置
:::
