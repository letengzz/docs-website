# 微信小程序 页面间通信

如果一个页面通过 `wx.navigateTo` 打开一个新页面，这两个页面间将建立一条数据通道：

1. 在 `wx.navigateTo` 的 `success` 回调中通过 `EventChannel` 对象发射事件。

2. 被打开的页面可以通过 `this.getOpenerEventChannel()` 方法获得一个 `EventChannel` 对象，进行监听、发射事件。

3. `wx.navigateTo` 方法中可以定义 `events` 配置项接收被打开页面发射的事件。

这两个 `EventChannel` 对象间可以使用 `emit` 和 `on` 方法相互发送、监听事件。

<img src="./assets/%E5%B0%8F%E7%A8%8B%E5%BA%8F%E9%A1%B5%E9%9D%A2%E9%97%B4%E9%80%9A%E4%BF%A1.png" style="zoom: 60%;" />

> 页面 .js 文件
>

```js
Page({

  // 点击按钮触发的事件处理函数
  handler () {

    wx.navigateTo({
      url: '/pages/list/list',
      events: {
        // key：被打开页面通过 eventChannel 发射的事件
        // value：回调函数
        // 为事件添加一个监听器，获取到被打开页面传递给当前页面的数据
        currentevent: (res) => {
          console.log(res)
        }
      },
      success (res) {
        // console.log(res)
        // 通过 success 回调函数的形参，可以获取 eventChannel 对象
        // eventChannel 对象给提供了 emit 方法，可以发射事件，同时携带参数
        res.eventChannel.emit('myevent', { name: 'tom' })
      }
    })

  }

})
```

> 被页面 .js 文件
>

```js
Page({

  onLoad () {

    // 通过 this.getOpenerEventChannel() 可以获取 EventChannel 对象
    const EventChannel = this.getOpenerEventChannel()

    // 通过 EventChannel 提供的 on 方法监听页面发射的自定义事件
    EventChannel.on('myevent', (res) => {
      console.log(res)
    })

    // 通过 EventChannel 提供的 emit 方法也可以向上一级页面传递数据
    // 需要使用 emit 定义自定义事件，携带需要传递的数据
    EventChannel.emit('currentevent', { age: 10 })

  },

})
```

## 五种通信方式对比

| 方式 | 方向 | 适用场景 | 注意事项 |
| --- | --- | --- | --- |
| URL 参数 | 上一页 → 下一页 | 少量简单参数（id、来源标记） | 只能传字符串，长度有限；`switchTab` 不支持 |
| `EventChannel` | 双向（navigateTo 通道内） | 传递对象、并接收下级页面回传 | 仅 `navigateTo` 建立通道；`redirectTo` 不建立 |
| `globalData`（`getApp()`） | 任意页面 | 登录态、用户信息等全局数据 | 不会自动刷新界面，需要手动 `setData` |
| `Storage` | 任意页面 | 需要跨启动持久化的数据 | 同步读写有开销，注意清理 |
| 事件总线 / 全局状态 | 任意页面（多对多） | 跨多页的实时通知 | 需要自己实现或引入方案，注意解绑避免泄漏 |

::: tip 一句话选择
**一次性数据用参数，父子页面回传用 EventChannel，全局数据用 globalData，持久化用 Storage，多对多通知用事件总线**。不要用 Storage 传一次性参数，也不要用 globalData 承载需要实时渲染的数据。
:::

::: warning 通信方式用错会带来的问题
1. **用 Storage 传一次性参数**：数据残留、下次进入页面读到脏值。
2. **用 globalData 驱动界面**：数据变了但界面不刷新，表现为"改了没反应"。
3. **事件总线不解绑**：页面销毁后仍在监听，导致同一事件被处理多次。
:::

## EventChannel 的三个注意点

1. **只在 `navigateTo` 建立的通道里有效**：`redirectTo`、`switchTab`、`reLaunch` 都不会建立通道。
2. **`onLoad` 里就要注册监听**：通过 `this.getOpenerEventChannel()` 获取并 `on`，避免错过早期事件。
3. **页面销毁时解绑**：自定义事件总线需要在 `onUnload` 中 `off`，否则可能重复触发或造成内存泄漏。

```js [pages/detail/detail.js（安全写法）]
Page({
  onLoad() {
    this.channel = this.getOpenerEventChannel()
    this.channel.on('myevent', this.handleEvent)
  },

  handleEvent(payload) {
    console.log('收到上一页数据', payload)
  },

  onUnload() {
    // 若使用自定义事件总线，务必在此解绑；EventChannel 随页面销毁自动回收
    if (this.channel && this.channel.off) {
      this.channel.off('myevent', this.handleEvent)
    }
  },
})
```

## 与路由配合的典型场景

| 场景 | 推荐做法 |
| --- | --- |
| 列表 → 详情（只传 id） | URL 参数 |
| 详情修改后返回刷新列表 | EventChannel 回传，或列表页 `onShow` + 脏标记（见 [路由与页面栈](../Router/index.md)） |
| 登录态在任意页面使用 | `globalData` + `Storage`（见 [全局数据共享](../getApp/index.md)） |
| 跨多个页面的实时通知（如购物车角标） | 事件总线 / 全局状态 |

## 验证方式

1. 在 A 页面 `navigateTo` B 页面并 `emit` 数据，确认 B 的 `onLoad` 能收到。
2. 在 B 页面 `emit` 回传数据，确认 A 的 `events` 回调收到并更新界面。
3. 把 `navigateTo` 换成 `redirectTo`，确认 EventChannel 不再可用（理解通道的建立条件）。
4. 在 `onUnload` 中加入日志，确认页面销毁时解绑逻辑被执行。

## 相关专题

- [路由与页面栈](../Router/index.md)：导航方式与页面栈限制
- [全局数据共享（getApp）](../getApp/index.md)：globalData 与 Storage 的使用
- [事件](../Event/index.md)：页面内的交互事件处理
- [生命周期](../Lifecycle/index.md)：onLoad / onUnload 的触发时机

## 参考资料

- 微信小程序官方文档 · EventChannel：https://developers.weixin.qq.com/miniprogram/dev/reference/api/EventChannel.html
- 微信小程序官方文档 · 页面路由：https://developers.weixin.qq.com/miniprogram/dev/framework/app-service/route.html
