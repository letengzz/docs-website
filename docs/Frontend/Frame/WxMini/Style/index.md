# 微信小程序 样式

`WXSS` 则充当的就是类似 `CSS` 的角色，`WXSS` 具有 `CSS` 大部分的特性，小程序在 `WXSS` 也做了一些扩充和修改，新增了尺寸单位 `rpx`、提供了全局的样式和局部样式，另外需要注意的是`WXSS` 仅支持部分 `CSS` 选择器。

小程序样式官方文档：[WXSS](https://developers.weixin.qq.com/miniprogram/dev/framework/view/wxss.html)

## 尺寸单位

随着智能手机的发展，手机设备的宽度也逐渐多元化，这就需要开发者在开发的时候，需要适配不同屏幕宽度的手机。为了解决屏幕适配的问题，微信小程序推出了 rpx 单位。

小程序运行在手机移动端，宿主环境是微信，因为手机尺寸的不一致，在写 `CSS` 样式时，开发者需要考虑到手机设备的屏幕会有不同的宽度和设备像素比，会采用一些技巧来算像素单位从而实现页面的适配。而 `WXSS` 在底层支持新的尺寸单位 `rpx` ，开发者可以免去换算的烦恼，只要交给小程序底层来换算即可。

`rpx `:  小程序新增的拓展单位，可以根据屏幕宽度进行自适应。

小程序规定任何型号手机：**屏幕宽都为 750 rpx**。

:::info 开发建议 

开发微信小程序时设计师可以用 iPhone6 作为视觉稿的标准。

iPhone6 的设计稿一般是 750px，小程序的宽是 750rpx。

在开发小程序页面时，量取多少 px ，直接写多少 rpx，开发起来更方便，也能够适配屏幕的适配。

**原因**：

设计稿宽度是 750px，而 iPhone6 的手机设备宽度是 375px， 设计稿想完整展示到手机中，就需要缩小一倍。

在 iPhone6 下，px 和 rpx 的换算关系是：1rpx = 0.5px， 750rpx = 375px，刚好能够填充满整个屏幕的宽度。

:::

> pages/index/index.wxml
>

```html
<!-- 需求：绘制一个盒子，让盒子的宽度占据屏幕的一半 -->

<!-- view 是小程序提供的组件，是容器组件，类似于 div，也是一个块级元素，占据一行 -->
<!-- 如果想实现需求，不能使用 px，px 使固定单位，不能实现自适应，需要使用小程序提供的 rpx  -->
<!-- 微信小程序规定，不管是什么型号的手机，屏幕的宽度都是 750rpx -->
<!-- rpx 单位能够实现自适应的 -->
<view class="box">Hello World!</view>
```

> pages/index/index.wxss
>

```css
/* 通过演示使用 css 作为单位，px 是不具有响应式的 */

/* image {
  width: 375px;
  height: 600px;
  background-color: lightgreen;
} */

.box {
  width: 375rpx;
  height: 600rpx;
  background-color: lightgreen;
}

```

## 全局样式和局部样式

在进行网页开发时，会经常创建 global.css、base.css 或者 reset.css 作为全局样式文件进行重置样式或者样式统一，然后在每个页面或组件中写当前页面或组件的局部样式，小程序中也存在全局样式和局部样式。

- 全局样式：指在 `app.wxss`中定义的样式规则，作用于每一个页面，例如：设置字号、背景色、宽高等全局样式。

- 局部样式：指在`page.wxss`中定义的样式规则，只作用在对应的页面，并会覆盖 app.wxss 中相同的选择器。


在 `app.wxss` 中定义全局样式，设置 `text` 组件的颜色以及字号大小，这段样式将会作用于任意页面的 `text` 组件。

```css
/* app.wxss */

text {
  color: lightseagreen;
  font-size: 50rpx;
}

```

然后在 `cate.wxss` 中定义局部样式，设置 `text` 组件的颜色以及字号大小，会发现局部样式将全局样式进行了覆盖。

```css
/* pages/index/index.wxss */

text {
  color: red;
  font-size: 30rpx;
}
```



