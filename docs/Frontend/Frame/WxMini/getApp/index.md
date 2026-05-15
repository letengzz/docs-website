# 微信小程序 getApp

`getApp()` 用于获取小程序全局唯一的 `App` 实例，通过小程序应用实例可实现数据或方法的共享。

:::danger 注意

1. 不要在 App() 方法中使用 getApp() ，使用 this 就可以拿到 app 实例。
2. 通过 `getApp()` 获取实例之后，不要私自调用生命周期函数。

:::

```js [app.js]
App({
  // 全局共享的数据
  globalData: {
    token: '',
  },

  // 全局共享的方法
  setToken(token) {
    // 如果想获取 token，可以使用 this 的方式进行获取
    this.globalData.token = token

    // 在 App() 方法中如果想获取 App() 实例，可以通过 this 的方式进行获取
    // 不能通过 getApp() 方法获取
  },
})
```

```js [pages/index/index.js]
// getApp() 方法用来获取全局唯一的 App() 实例
const appInstance = getApp()

Page({
  login() {
    // 不要通过 app 实例调用钩子函数
    console.log(appInstance)

    appInstance.setToken('fghioiuytfghjkoiuytghjoiug')
  },
})
```

<img src="./assets/50-getApp.jpg" style="zoom:70%;" />
