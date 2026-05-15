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

  }

})
```





