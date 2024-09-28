# Electron Preload 脚本

预加载 (Preload) 脚本是运行在渲染进程中的， 但它是在网页内容加载之前执行的，这意味着它具有比普通渲染器代码更高的权限，可以访问 Node.js 的 API，同时又可以与网页内容进行安全的交互。

简单说：它是 Node.js 和 Web API 的桥梁，Preload 脚本可以安全地将部分 Node.js 功能暴露给网页，从而减少安全风险。

**例**：点击按钮后，在页面呈现当前的 Node 版本。

1. 创建预加载脚本preload.js﻿：

   ```js
   const { contextBridge } = require('electron')
   // 暴露数据给渲染进程
   contextBridge.exposeInMainWorld('myAPI', {
       n: 666,
       version: process.version
   })
   ```

2. 在主线程中引入 preload.js﻿

   ```js
   const path = require('path');
   const win = new BrowserWindow({
   	/*******/
   	webPreferences:{
   		preload:path.resolve(__dirname,'./preload.js')
   	}
   	/*******/
   })
   ```

3. 在 html 页面中编写对应按钮，并创建专门编写网页脚本的﻿render.js﻿，随后引入。

   ```html
   <body>
     <h1>你好啊！</h1>
     <button id="btn">在用户的D盘创建一个hello.txt</button>
     <script type="text/javascript" src="./render.js"></script>
   </body>
   ```

4. 在渲染进程中使用 version﻿

   ```js
   const btn1 = document.getElementById('btn1');
   // btn1.onclick = ()=>{
   //     alert('点我了')
   // }
   btn1.addEventListener('click', () => {
       console.log(myAPI.version)
       document.body.innerHTML += `<h2>${myAPI.version}</h2>`
   })
   ```

5. 整体文件结构：

   ![image-20240627235224478](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406272352335.png)

