# Uniapp 路由与导航

## 页面路由配置

### pages.json 配置

```json [pages.json]
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页"
      }
    },
    {
      "path": "pages/detail/index",
      "style": {
        "navigationBarTitleText": "详情页"
      }
    },
    {
      "path": "pages/login/index",
      "style": {
        "navigationBarTitleText": "登录"
      }
    }
  ]
}
```

::: tip 提示
pages.json 中第一个页面为应用首页。新增页面时需要在 pages 数组中添加对应配置。
:::

## 导航方式

### uni.navigateTo

保留当前页面，跳转到新页面：

```vue
<script setup>
const goToDetail = (id) => {
  uni.navigateTo({
    url: `/pages/detail/index?id=${id}&title=详情`,
    success: () => {
      console.log('跳转成功')
    },
    fail: (err) => {
      console.error('跳转失败', err)
    }
  })
}
</script>

<template>
  <view>
    <button @click="goToDetail(123)">查看详情</button>
  </view>
</template>
```

### uni.redirectTo

关闭当前页面，跳转到新页面：

```vue
<script setup>
const goToLogin = () => {
  uni.redirectTo({
    url: '/pages/login/index'
  })
}
</script>
```

### uni.reLaunch

关闭所有页面，打开新页面：

```vue
<script setup>
const goHome = () => {
  uni.reLaunch({
    url: '/pages/index/index'
  })
}
</script>
```

### uni.switchTab

跳转到 tabBar 页面：

```vue
<script setup>
const goToTab = () => {
  uni.switchTab({
    url: '/pages/index/index'
  })
}
</script>
```

### uni.navigateBack

返回上一页：

```vue
<script setup>
const goBack = () => {
  uni.navigateBack({
    delta: 1
  })
}

const goBackTwoPages = () => {
  uni.navigateBack({
    delta: 2
  })
}
</script>
```

## 页面传参

### URL 参数传递

```vue [pages/list/index.vue]
<script setup>
const goToDetail = (item) => {
  uni.navigateTo({
    url: `/pages/detail/index?id=${item.id}&name=${encodeURIComponent(item.name)}`
  })
}
</script>
```

```vue [pages/detail/index.vue]
<script setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

const id = ref('')
const name = ref('')

onLoad((options) => {
  id.value = options.id
  name.value = decodeURIComponent(options.name)
})
</script>
```

### 全局数据传递

```javascript [utils/store.js]
const globalData = {}

export function setGlobalData(key, value) {
  globalData[key] = value
}

export function getGlobalData(key) {
  return globalData[key]
}
```

```vue [pages/list/index.vue]
<script setup>
import { setGlobalData } from '@/utils/store.js'

const goToDetail = (item) => {
  setGlobalData('currentItem', item)
  uni.navigateTo({
    url: '/pages/detail/index'
  })
}
</script>
```

```vue [pages/detail/index.vue]
<script setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'
import { getGlobalData } from '@/utils/store.js'

const item = ref(null)

onLoad(() => {
  item.value = getGlobalData('currentItem')
})
</script>
```

## 导航栏配置

### 全局导航栏

```json [pages.json]
{
  "globalStyle": {
    "navigationBarTextStyle": "white",
    "navigationBarTitleText": "我的应用",
    "navigationBarBackgroundColor": "#007AFF",
    "backgroundColor": "#F8F8F8",
    "backgroundTextStyle": "light",
    "enablePullDownRefresh": false
  }
}
```

### 页面级导航栏

```json [pages.json]
{
  "pages": [
    {
      "path": "pages/detail/index",
      "style": {
        "navigationBarTitleText": "详情页",
        "navigationBarBackgroundColor": "#FF6B6B",
        "navigationBarTextStyle": "white"
      }
    }
  ]
}
```

### 动态设置导航栏

```vue
<script setup>
import { onLoad } from '@dcloudio/uni-app'

onLoad(() => {
  uni.setNavigationBarTitle({
    title: '动态标题'
  })

  uni.setNavigationBarColor({
    frontColor: '#ffffff',
    backgroundColor: '#007AFF'
  })
})
</script>
```

## TabBar 配置

### 基础配置

```json [pages.json]
{
  "tabBar": {
    "color": "#7A7E83",
    "selectedColor": "#007AFF",
    "borderStyle": "black",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "iconPath": "static/tab/home.png",
        "selectedIconPath": "static/tab/home-active.png",
        "text": "首页"
      },
      {
        "pagePath": "pages/category/index",
        "iconPath": "static/tab/category.png",
        "selectedIconPath": "static/tab/category-active.png",
        "text": "分类"
      },
      {
        "pagePath": "pages/cart/index",
        "iconPath": "static/tab/cart.png",
        "selectedIconPath": "static/tab/cart-active.png",
        "text": "购物车"
      },
      {
        "pagePath": "pages/mine/index",
        "iconPath": "static/tab/mine.png",
        "selectedIconPath": "static/tab/mine-active.png",
        "text": "我的"
      }
    ]
  }
}
```

### 动态设置 TabBar

```vue
<script setup>
// 设置 TabBar 项文本
uni.setTabBarItem({
  index: 0,
  text: '新首页'
})

// 设置 TabBar 样式
uni.setTabBarStyle({
  color: '#999',
  selectedColor: '#007AFF',
  backgroundColor: '#fff'
})

// 显示/隐藏 TabBar
uni.showTabBar()
uni.hideTabBar()

// 设置 TabBar 红点
uni.showTabBarRedDot({
  index: 2
})

uni.setTabBarBadge({
  index: 2,
  text: '3'
})

uni.removeTabBarBadge({
  index: 2
})
</script>
```

## 路由拦截

```javascript [utils/router.js]
const whiteList = ['/pages/login/index', '/pages/register/index']

export function beforeEach(to, from, next) {
  const token = uni.getStorageSync('token')

  if (token) {
    next()
  } else {
    if (whiteList.includes(to.path)) {
      next()
    } else {
      uni.redirectTo({
        url: '/pages/login/index'
      })
    }
  }
}
```

## 页面栈

```vue
<script setup>
const getPageStack = () => {
  const pages = getCurrentPages()
  console.log('页面栈:', pages)
  console.log('当前页面:', pages[pages.length - 1])
  console.log('上一页:', pages[pages.length - 2])
}

const callPrevPageMethod = () => {
  const pages = getCurrentPages()
  const prevPage = pages[pages.length - 2]
  if (prevPage) {
    prevPage.$vm.refreshData()
  }
}
</script>
```

::: danger 注意
- `navigateTo` 最多打开 10 个页面，超出后需要使用 `redirectTo`
- `switchTab` 只能跳转到 tabBar 页面
- `reLaunch` 会关闭所有页面，包括 tabBar
:::
