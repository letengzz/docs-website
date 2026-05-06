# Uniapp 条件编译

## 条件编译简介

条件编译是 Uniapp 的核心特性之一，允许开发者在不同平台使用不同的代码实现，从而实现平台差异化开发。

## 注释条件编译

### 模板条件编译

```vue
<template>
  <view>
    <!-- #ifdef H5 -->
    <web-view src="https://example.com"></web-view>
    <!-- #endif -->

    <!-- #ifdef MP-WEIXIN -->
    <button open-type="getUserInfo">获取用户信息</button>
    <!-- #endif -->

    <!-- #ifdef APP-PLUS -->
    <button @click="callNative">调用原生方法</button>
    <!-- #endif -->

    <!-- #ifndef H5 -->
    <text>非 H5 平台显示</text>
    <!-- #endif -->
  </view>
</template>
```

### 脚本条件编译

```vue
<script setup>
// #ifdef H5
import { useBrowser } from '@/utils/browser.js'
// #endif

// #ifdef MP-WEIXIN
import { useWeixin } from '@/utils/weixin.js'
// #endif

const handleAction = () => {
  // #ifdef H5
  console.log('H5 平台')
  // #endif

  // #ifdef MP-WEIXIN
  console.log('微信小程序')
  // #endif

  // #ifdef APP-PLUS
  console.log('App 平台')
  // #endif

  // #ifndef H5
  console.log('非 H5 平台')
  // #endif
}
</script>
```

### 样式条件编译

```vue
<style>
/* #ifdef H5 */
.container {
  width: 1200px;
  margin: 0 auto;
}
/* #endif */

/* #ifdef MP-WEIXIN */
.container {
  width: 100%;
  padding: 20rpx;
}
/* #endif */

/* #ifdef APP-PLUS */
.container {
  width: 100%;
  padding: 10px;
}
/* #endif */
</style>
```

## 平台标识

| 平台 | 标识 |
|------|------|
| H5 | `H5` |
| 微信小程序 | `MP-WEIXIN` |
| 支付宝小程序 | `MP-ALIPAY` |
| 百度小程序 | `MP-BAIDU` |
| 抖音小程序 | `MP-TOUTIAO` |
| QQ 小程序 | `MP-QQ` |
| 快手小程序 | `MP-KUAISHOU` |
| 京东小程序 | `MP-JD` |
| App | `APP-PLUS` |
| App nvue | `APP-PLUS-NVUE` |
| 快应用 | `QUICKAPP-WEBVIEW` |

## 文件条件编译

### 文件后缀条件编译

```
├── pages/
│   └── index/
│       ├── index.vue          # 通用页面
│       ├── index.h5.vue       # 仅 H5 平台
│       ├── index.mp-weixin.vue # 仅微信小程序
│       └── index.app-plus.vue  # 仅 App 平台
```

### 目录条件编译

```
├── platform/
│   ├── h5/
│   │   └── share.js
│   ├── mp-weixin/
│   │   └── share.js
│   └── app-plus/
│       └── share.js
```

```vue
<script setup>
// #ifdef H5
import { share } from '@/platform/h5/share.js'
// #endif

// #ifdef MP-WEIXIN
import { share } from '@/platform/mp-weixin/share.js'
// #endif

// #ifdef APP-PLUS
import { share } from '@/platform/app-plus/share.js'
// #endif
</script>
```

## 条件编译示例

### 平台差异化分享

```javascript [utils/share.js]
export function shareToPlatform(data) {
  // #ifdef H5
  // H5 平台使用 Web Share API
  if (navigator.share) {
    navigator.share({
      title: data.title,
      text: data.content,
      url: data.url
    })
  }
  // #endif

  // #ifdef MP-WEIXIN
  // 微信小程序使用分享 API
  return {
    title: data.title,
    path: `/pages/detail/index?id=${data.id}`,
    imageUrl: data.imageUrl
  }
  // #endif

  // #ifdef APP-PLUS
  // App 平台使用原生分享
  uni.share({
    provider: 'weixin',
    type: 0,
    title: data.title,
    summary: data.content,
    imageUrl: data.imageUrl,
    href: data.url
  })
  // #endif
}
```

### 平台差异化登录

```javascript [utils/login.js]
export async function login() {
  // #ifdef H5
  // H5 平台使用账号密码登录
  const username = prompt('请输入用户名')
  const password = prompt('请输入密码')
  return await fetch('/api/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  })
  // #endif

  // #ifdef MP-WEIXIN
  // 微信小程序使用微信登录
  const { code } = await uni.login({ provider: 'weixin' })
  return await fetch('/api/weixin/login', {
    method: 'POST',
    body: JSON.stringify({ code })
  })
  // #endif

  // #ifdef APP-PLUS
  // App 平台使用原生登录
  const { code } = await uni.login({ provider: 'apple' })
  return await fetch('/api/apple/login', {
    method: 'POST',
    body: JSON.stringify({ code })
  })
  // #endif
}
```

### 平台差异化支付

```javascript [utils/pay.js]
export async function pay(orderId) {
  // #ifdef H5
  // H5 平台使用网页支付
  window.location.href = `/api/pay/h5?orderId=${orderId}`
  // #endif

  // #ifdef MP-WEIXIN
  // 微信小程序使用微信支付
  const res = await fetch(`/api/pay/weixin?orderId=${orderId}`)
  const data = await res.json()
  await uni.requestPayment({
    provider: 'wxpay',
    timeStamp: data.timeStamp,
    nonceStr: data.nonceStr,
    package: data.package,
    signType: 'MD5',
    paySign: data.paySign
  })
  // #endif

  // #ifdef APP-PLUS
  // App 平台使用原生支付
  const res = await fetch(`/api/pay/app?orderId=${orderId}`)
  const data = await res.json()
  await uni.requestPayment({
    provider: data.provider,
    orderInfo: data.orderInfo
  })
  // #endif
}
```

## manifest.json 条件编译

```json [manifest.json]
{
  "h5": {
    "title": "H5 应用标题",
    "router": {
      "mode": "hash"
    },
    "devServer": {
      "port": 8080
    }
  },
  "mp-weixin": {
    "appid": "wx1234567890",
    "setting": {
      "urlCheck": false
    }
  },
  "app-plus": {
    "usingComponents": true,
    "splashscreen": {
      "alwaysShowBeforeRender": true
    }
  }
}
```

## pages.json 条件编译

```json [pages.json]
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页",
        "app-plus": {
          "titleNView": {
            "buttons": [
              {
                "text": "\ue670",
                "fontSrc": "/static/uni.ttf",
                "fontSize": "22px"
              }
            ]
          }
        }
      }
    }
  ]
}
```

::: tip 提示
- 条件编译注释中 `#` 和关键字之间不能有空格
- 条件编译只在编译时生效，运行时无效
- 使用条件编译时注意代码可维护性
:::

::: danger 注意
- 条件编译注释不能嵌套
- 条件编译区域内的代码在对应平台才会被编译
- 不同平台的代码需要分别维护
:::
