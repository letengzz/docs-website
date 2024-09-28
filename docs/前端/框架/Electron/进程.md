# Electron 进程

在 Electron 中主要控制两类进程：主进程、渲染器进程。

## 主进程

每个 Electron 应用都有一个单一的主进程，作为应用程序的入口点。 

主进程在 Node.js 环境中运行，它具有 require 模块和使用所有 Node.js API 的能力。

主进程的核心就是：**使用BrowserWindow来创造和管理窗口**

## 渲染进程

每个 BrowserWindow 实例都对应一个单独的渲染器进程，运行在渲染器进程中的代码，必须遵
守网页标准，这也就意味着：渲染器进程无权直接访问require或使用任何Node.js的API