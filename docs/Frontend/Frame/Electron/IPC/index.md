# Electron 进程通信 IPC

进程通信(IPC﻿、InterProcess Communication)，IPC﻿是﻿Electron﻿中最为核心的内容，它是从﻿UI﻿调用原生 ﻿API﻿的唯一方法。
Electron﻿中，主要使用 ipcMain 和 ipcRenderer 来定义"通道"，进行进程通信。

## 渲染进程到主进程单向通信

在渲染器进程中 ipcRenderer.send 发送消息，在主进程中使用 ipcMain.on 接收消息。常用于在Web中调用主进程的API。

**例**：点击按钮后，在用户的 D 盘创建一个﻿hello.txt﻿文件，文件内容来自于用户输入。

1. 页面中添加相关元素， render.js﻿中添加对应脚本

   > index.html

   ```html
   <input id="content" type="text"><br><br>
   <button id="btn">在用户的D盘创建一个hello.txt</button>
   ```

   >  render.js﻿

   ```js
   const btn = document.getElementById('btn')
   const content = document.getElementById('content')
   
   btn.addEventListener('click',()=>{
     console.log(content.value)
     myAPI.saveFile(content.value)
   })
   ```

2. preload.js﻿中使用 ﻿`ipcRenderer.send('信道',参数)`﻿发送消息，与主进程通信：

   ```js
   const {contextBridge,ipcRenderer} = require('electron')
   contextBridge.exposeInMainWorld('myAPI',{
     	/*******/
     	saveFile(str){
     		// 渲染进程给主进程发送一个消息
     		ipcRenderer.send('create-file',str)
   	}
   })
   ```

3. 主进程中，在加载页面之前，使用 `ipcMain.on('信道',回调)`﻿配置对应回调函数，接收消息

   ```js
   const { app, BrowserWindow,ipcMain } = require('electron')
   const path = require('path');
   const fs = require('fs');
   // 用于创建窗口
   function createWindow() {
   	/**********/
   	// 主进程注册对应回调
   	ipcMain.on('create-file',createFile)
   	// 加载一个本地页面
   	win.loadFile(path.resolve(__dirname,'./pages/index.html'))
   }
   //创建文件
   function createFile(event,data){
   	fs.writeFileSync('D:/hello.txt',data)
   }
   ```

## 渲染进程与主进程双向通信

渲染进程通过ipcRenderer.invoke 发送消息，主进程使用 ipcMain.handle 接收并处理消息。ipcRederer.invoke 的返回值是Promise实例。常用于：从渲染器进程调用主进程方法并等待结果。

**例**：点击按钮从 D 盘读取﻿hello.txt﻿中的内容，并将结果呈现在页面上。

1. 页面中添加相关元素， render.js﻿中添加对应脚本

   > index.html

   ```html
   <button id="btn">读取用户D盘的hello.txt</button>
   ```

   > render.js

   ```js
   const btn = document.getElementById('btn')
   btn.addEventListener('click', async () => {
       let data = await myAPI.readFile('D:/hello.txt')
       document.body.innerHTML += `<h2>${data}</h2>`
   })
   ```

2. preload.js﻿中使用 ﻿`ipcRenderer.invoke('信道',参数)`﻿发送消息，与主进程通信

   ```js
   const {contextBridge,ipcRenderer} = require('electron')
   contextBridge.exposeInMainWorld('myAPI',{
    /*******/
    readFile (path){
    	return ipcRenderer.invoke('read-file',path)
    }
   }
   ```

3. 主进程中，在加载页面之前，使用 `ipcMain.handle('信道',回调)`﻿接收消息，并配置回调函数

   ```js
   // 用于创建窗口
   function createWindow() {
    /**********/
    // 主进程注册对应回调
    ipcMain.handle('read-file',readFile)
    // 加载一个本地页面
    win.loadFile(path.resolve(__dirname,'./pages/index.html'))
   }
   //读取文件
   function readFile(event,path){
    return fs.readFileSync(path).toString()
   }
   ```

## 主进程到渲染进程通信

主进程使用 win.webContents.send 发送消息，渲染进程通过ipcRenderer.on 处理消息。常用于：从主进程主动发送消息给渲染进程。

**例**：应用加载 6 秒钟后，主动给渲染进程发送一个消息，内容是：你好啊！

1. 页面中添加相关元素， render.js﻿中添加对应脚本

   ```js
   window.onload = ()=>{
    myAPI.getMessage(logMessage)
   }
   function logMessage(event,str){
    console.log(event,str)
   }
   ```

2. preload.js﻿中使用 ﻿`ipcRenderer.on ('信道',回调)`﻿接收消息，并配置回调函数

   ```js
   const {contextBridge,ipcRenderer} = require('electron')
   contextBridge.exposeInMainWorld('myAPI',{
    /*******/
    getMessage: (callback) => {
     return ipcRenderer.on('message', callback);
    }
   })
   ```

3. 主进程中，在合适的时候，使用 `win.webContents.send('信道',数据)`﻿发送消息

   ```js
   // 用于创建窗口
   function createWindow() {
    /**********/
    // 加载一个本地页面
    win.loadFile(path.resolve(__dirname,'./pages/index.html'))
    // 创建一个定时器
    setTimeout(() => {
     win.webContents.send('message','你好啊！')
    }, 6000);
   }
   ```

   

