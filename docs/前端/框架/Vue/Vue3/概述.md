# Vue3 概述

2020年9月18日，`Vue.js`发布版`3.0`版本，代号：`One Piece`

经历了：[4800+次提交](https://github.com/vuejs/core/commits/main)、[40+个RFC](https://github.com/vuejs/rfcs/tree/master/active-rfcs)、[600+次PR](https://github.com/vuejs/vue-next/pulls?q=is%3Apr+is%3Amerged+-author%3Aapp%2Fdependabot-preview+)、[300+贡献者](https://github.com/vuejs/core/graphs/contributors)

在Vue3中，编码语言往往搭配TypeScript、推荐使用组合式API、使用语法糖，同时Vue3兼容大部分Vue2语法。

官方在生态系统上逐渐向Vue3倾斜，主流库和插件都在向Vue3迁移。

官方发版地址：[Release v3.0.0 One Piece · vuejs/core](https://github.com/vuejs/core/releases/tag/v3.0.0)

****

相较于Vue2：

1. **性能的提升**：

   - 打包大小减少`41%`。
   
   
      - 初次渲染快`55%`, 更新渲染快`133%`。
   
   
      - 内存减少`54%`。
   
2. **源码的升级**：

   - 响应式使用`Proxy`代替`Object.defineProperty`实现响应式。
   
   
      - 重写虚拟`DOM`的实现和`Tree-Shaking` (ES6推出了tree shaking机制，tree shaking 就是在项目中引入其他模块时，会自动将用不到的代码，或者永远不会执行的代码摇掉)。
   
3. `Vue3`可以更好的支持`TypeScript`。

4. **新的特性**：

   - `Composition API`（组合`API`）：`setup`、`ref`与`reactive`、`computed`与`watch`......

     ![image-20240602205936661](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406022059285.png)

   - 键盘事件不再支持keyCode。例如：`v-on:keyup.enter`支持，`v-on:keyup.13`不支持

   - 新的内置组件：`Fragment`、`Teleport`、`Suspense`......

     ![image-20240602205347515](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406022053537.png)

5. 其他改变：

   - 新的生命周期钩子

     ![image-20240602205320099](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406022053400.png)

   - `data` 选项应始终被声明为一个函数

   - 移除`keyCode`支持作为` v-on` 的修饰符 (例如：v-on:keyup.enter支持，v-on:keyup.13不支持)
   
     ......



