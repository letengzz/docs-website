# Vue 概述

Vue是一个基于JavaScript实现的框架。

Vue (读音 /vjuː/，类似于 view) 是一套用于构建用户界面的渐进式框架。

Vue 的核心库只关注视图层，不仅易于上手，还便于与第三方库或既有项目整合。另一方面，当与现代化的工具链以及各种支持类库结合使用时，Vue 也完全能够为复杂的单页应用提供驱动。

官方网站：https://cn.vuejs.org

![image-20240130220839296](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401302208831.png)

## Vue 开发方式

### 传统方式

在HTML页面中加入 `https://unpkg.com/vue@3/dist/vue.global.js` (**项目中较少使用**)

### 工程化方式

采用vite脚手架工具创建一个vue工程，然后进行开发 (**项目中广泛使用**)

## 组件化

组件系统是一个抽象的概念；

- 组件：小型、独立、可复用的单元
- 组合：通过组件之间的组合、包含关系构建出一个完整应用

几乎任意类型的应用界面都可以抽象为一个组件树；

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406202046688.png)

## 单文件组件

Vue 的**单文件组件** (即 *.vue 文件，英文 Single-File Component，简称 SFC) 是一种特殊的文件格式，能够将一个 Vue 组件的模板、逻辑与样式封装在单个文件中.

```vue
<script setup>
  //编写脚本
</script>

<template>
  //编写页面模板
</template>

<style scoped>
  //编写样式
</style>
```

