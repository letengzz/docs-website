# Vue3 新组件

````


## Fragment

在Vue2中每个组件必须有一个根标签。这样性能方面稍微有点问题，如果每一个组件必须有根标签，组件嵌套组件的时候，有很多无用的根标签。

在Vue3中每个组件不需要有根标签。实际上内部实现的时候，最终将所有组件嵌套好之后，最外层会添加一个Fragment，用这个Fragment当做根标签。这是一种性能优化策略。

## Teleport

Teleport 是一种能够将**组件html结构**移动到指定位置的技术(设置组件的显示位置)。

```vue
<teleport to='body' >
    <div class="modal" v-show="isShow">
      <h2>我是一个弹窗</h2>
      <p>我是弹窗中的一些内容</p>
      <button @click="isShow = false">关闭弹窗</button>
    </div>
</teleport>
```

![image-20240210205047256](assets/image-20240210205047256.png)

![image-20240210205051607](assets/image-20240210205051607.png)

![image-20240210205250014](assets/image-20240210205250014.png)

![image-20240210205323077](assets/image-20240210205323077.png)

![image-20240210205350058](assets/image-20240210205350058.png)

![image-20240210205432668](assets/image-20240210205432668.png)

![image-20240210205446851](assets/image-20240210205446851.png)

![image-20240210205501111](assets/image-20240210205501111.png)

![image-20240210205617911](assets/image-20240210205617911.png)

![image-20240210205840852](assets/image-20240210205840852.png)

![image-20240210214917555](assets/image-20240210214917555.png)

![image-20240210214921195](assets/image-20240210214921195.png)

![image-20240210215005707](assets/image-20240210215005707.png)



![image-20240210215012094](assets/image-20240210215012094.png)

蓝色参考红色

![image-20240210215057679](assets/image-20240210215057679.png)

to表示塞在那个地方

![image-20240210215142792](assets/image-20240210215142792.png)

![image-20240210215318772](assets/image-20240210215318772.png)

![image-20240210215324652](assets/image-20240210215324652.png)

Teleport 是一种能够将我们的**组件html结构**移动到指定位置的技术。

```html
<teleport to='body' >
    <div class="modal" v-show="isShow">
      <h2>我是一个弹窗</h2>
      <p>我是弹窗中的一些内容</p>
      <button @click="isShow = false">关闭弹窗</button>
    </div>
</teleport>
```

## Suspense

等待异步组件时渲染一些额外内容，让应用有更好的用户体验。

使用步骤： 

-  异步引入组件
-  使用`Suspense`包裹组件，并配置好`default` 与 `fallback`

```tsx
import { defineAsyncComponent,Suspense } from "vue";
const Child = defineAsyncComponent(()=>import('./Child.vue'))
```

```vue
<template>
    <div class="app">
        <h3>我是App组件</h3>
        <Suspense>
          <template v-slot:default>
            <Child/>
          </template>
          <template v-slot:fallback>
            <h3>加载中.......</h3>
          </template>
        </Suspense>
    </div>
</template>
```

## 全局API转移到应用对象

- 注册全局组件：`app.component`
- 配置对象：`app.config`
- 注册全局指令：`app.directive`
- `app.mount`
- `app.unmount`
- `app.use`

## 其他

**官方文档**：https://v3-migration.vuejs.org/zh/breaking-changes/

- 过渡类名 `v-enter` 修改为 `v-enter-from`、过渡类名 `v-leave` 修改为 `v-leave-from`。


- `keyCode` 作为 `v-on` 修饰符的支持。

- `v-model` 指令在组件上的使用已经被重新设计，替换掉了 `v-bind.sync。`

- `v-if` 和 `v-for` 在同一个元素身上使用时的优先级发生了变化。`v-if`优先级更高

- 移除了`$on`、`$off` 和 `$once` 实例方法。

- 移除了过滤器 `filter`。

- 移除了`$children` 实例 `propert`。

  ......
````

