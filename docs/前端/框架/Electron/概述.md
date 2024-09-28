# Electron 概述

Electron是⼀个**跨平台桌面应用**开发框架，开发者可以使用：HTML、CSS、JavaScript等Web技术来构建桌面应用程序，它的本质是结合了Chromium和Node.js，现在广泛用于桌面应用程序开发。

**官方网站**：https://www.electronjs.org/zh/

例如这些桌面应用都用到了 Electron技术：

- Visual Studio Code
- GitHub Desktop
- 1Password
- 新版QQ

**Electron的优势**：

1. 可跨平台：同⼀套代码可以构建出能在：Windows、macOS、Linux上运行的应用程序。
2. 上手容易：使用Web技术就可以轻松完成开发桌面应用程序。
3. 底层权限：允许应用程序访问文件系统、操作系统等底层功能，从而实现复杂的系统交互。
4. 社区支持：拥有⼀个庞大且活跃的社区，开发者可以轻松找到⽂档、教程和开源库。

**Electron技术架构**：Electron = Chromium + Node.js + Native API

![image-20240627124541211](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406271245643.png)

**进程模型**：核心**进程通信**

![image-20240627123514244](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406271235945.png)

