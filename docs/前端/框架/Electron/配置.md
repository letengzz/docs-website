# Electron 配置

## 窗口配置

**官方文档**：https://www.electronjs.org/zh/docs/latest/api/base-window#%E5%AE%9E%E4%BE%8B%E5%B1%9E%E6%80%A7

创建窗口配置：

```js
/*
main.js运行在应用的主进程上，无法访问Web相关API，主要负责：控制生命周期、显示界面、
控制渲染进程等其他操作。
*/
const {app,BrowserWindow} = require('electron')

//当app准备好，调用回调函数
app.on('ready',()=>{
    //创建窗口
    const win = new BrowserWindow({
        'width': 800,
        'height': 600,
        'autoHideMenuBar':true, //自动隐藏菜单栏
        x: 0, //窗口x轴坐标
        y: 0,  //窗口y轴坐标
        alwaysOnTop: true //一直固定(置顶)
    })
    //在窗口加载页面
    win.loadURL('http://www.baidu.com')
})
```

退出应用配置：

1. Windows 和 Linux 平台窗口特点是：关闭所有窗口时退出应用。

   ```js
   // 当所有窗口都关闭时
   app.on('window-all-closed', () => {
       // 如果所处平台不是mac(darwin)，则退出应用。
       if (process.platform !== 'darwin') app.quit()
   })
   ```

2. mac 应用即使在没有打开任何窗口的情况下也继续运行，并且在没有窗口可用的情况下激活
   应用时会打开新的窗口。

   ```js
   function createWindow(){
        //创建窗口
        const win = new BrowserWindow({
           'width': 800,
           'height': 600,
           'autoHideMenuBar': true, //自动隐藏菜单栏
           x: 0, //窗口x轴坐标
           y: 0,  //窗口y轴坐标
           alwaysOnTop: true //一直固定(置顶)
       })
       //在窗口加载页面
       // win.loadURL('http://www.baidu.com')
       //加载文件
       win.loadFile('./page/index.html')
   }
   
   // 当app准备好后，执行createWindow创建窗口
   app.on('ready', () => {
       createWindow()
       // 当应用被激活时
       app.on('activate', () => {
           //如果当前应用没有窗口，则创建一个新的窗口
           if (BrowserWindow.getAllWindows().length === 0) createWindow()
       })
   })
   ```

## 加载本地页面

在page文件夹中创建index.html：

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document</title>
    <link rel="stylesheet" href="./index.css">
</head>
<body>
    <h1>欢迎 学习Electron</h1>
</body>
</html>
```

> index.css

```css
h1{
    background-color:gray;
    color: orange;
}
```

在main.js配置：

```js
/*
main.js运行在应用的主进程上，无法访问Web相关API，主要负责：控制生命周期、显示界面、
控制渲染进程等其他操作。
*/
const {app,BrowserWindow} = require('electron')

//当app准备好，调用回调函数
app.on('ready',()=>{
    //创建窗口
    const win = new BrowserWindow({
        'width': 800,
        'height': 600,
        'autoHideMenuBar':true, //自动隐藏菜单栏
        x: 0, //窗口x轴坐标
        y: 0,  //窗口y轴坐标
        alwaysOnTop: true //一直固定(置顶)
    })
    //在窗口加载页面
    // win.loadURL('http://www.baidu.com')
    //加载文件
    win.loadFile('./page/index.html')
})
```

打开开发者模式：ctrl+shift+i

出现`Electron Security Warning (Insecure Content-Security-Policy)`：

![image-20240627203916534](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406272039200.png)

解决办法：配置 CSP(Content-Security-Policy)

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
```

说明：

1. default-src 'self'﻿
    default-src﻿：配置加载策略，适用于所有未在其它指令中明确指定的资源类型。
    self﻿：仅允许从同源的资源加载，禁止从不受信任的外部来源加载，提高安全性。
2. style-src 'self' 'unsafe-inline'﻿
    style-src﻿：指定样式表（CSS）的加载策略。
    self﻿：仅允许从同源的资源加载，禁止从不受信任的外部来源加载，提高安全性。
    unsafe-inline﻿：允许在HTML文档内使用内联样式。
3. img-src 'self' data:﻿
    img-src﻿：指定图像资源的加载策略。
    self﻿：表示仅允许从同源加载图像。
    data:﻿：允许使用 ﻿data: URI﻿ 来嵌入图像。这种URI模式允许将图像数据直接嵌
    入到HTML或CSS中，而不是通过外部链接引用。

参考文档：

- https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Content-Security-Policy
- https://www.electronjs.org/docs/latest/tutorial/security

## 配置自动重启

1. 安装 Nodemon

   ```shell
   npm i nodemon -D
   ```

2. 修改 package.json 命令

   ```js
   "scripts": {
     "start": "nodemon --exec electron ."
   },
   ```

3. 配置 nodemon.json 规则

   ```json
   {
       "ignore": [
           "node_modules",
           "dist"
       ],
       "restartable": "r",
       "watch": [
           "*.*"
       ],
       "ext": "html,js,css"
   }
   ```

配置好以后，当代码修改后，应用就会自动重启了，或者在控制台输入`r`重启。
