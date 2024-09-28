# Electron 构建工具

electron-vite 是一个新型构建工具，旨在为 Electron 提供更快、更精简的体验。主要由五部分

组成：

- 一套构建指令，它使用 [Vite](https://cn.vitejs.dev/) 打包你的代码，并且它能够处理 Electron 的独特环境，包括[Node.js](https://nodejs.org/en) 和浏览器环境。
- 集中配置主进程、渲染器和预加载脚本的 Vite 配置，并针对 Electron 的独特环境进行预配置。
- 为渲染器提供快速模块热替换（HMR）支持，为主进程和预加载脚本提供热重载支持，极大地提高了开发效率。
- 优化 Electron 主进程资源处理。
- 使用 V8 字节码保护源代码。
- electron-vite 快速、简单且功能强大，旨在开箱即用。

官网地址：https://cn-evite.netlify.app/

![image-20240627195555532](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406271955172.png)