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

## rpx 与多端适配

`rpx`（responsive pixel）是小程序的响应式单位：**规定屏幕宽度为 750rpx**，由运行时按设备宽度换算。

| 设备 | 屏幕宽度 | 1rpx 实际像素 |
| --- | --- | --- |
| iPhone 6/7/8（375px 逻辑宽） | 750rpx | 0.5px |
| iPhone 14 Pro Max（430px） | 750rpx | ≈0.573px |
| 平板 | 750rpx | 更大 |

```css
/* 设计稿按 750px 宽标注时，数值直接写 rpx 即可 */
.card {
  width: 690rpx;      /* 设计稿 690px */
  padding: 24rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
}
```

::: danger 注意
1. **`rpx` 不适合字体以外的极端值**：字号、边框这类需要「感知一致」的尺寸，过大或过小时用 `px` 更可控（例如 1px 的细线，写 `1rpx` 在部分设备上会消失）。
2. **不要在 `calc()` 中混用导致精度问题**：`calc(100% - 30rpx)` 可用，但要意识到换算发生在运行时。
3. **横屏与平板需额外验证**：`rpx` 按屏幕宽度换算，宽屏设备上元素会被等比放大，必要时用媒体查询限定布局。
:::

## 样式隔离

页面样式默认只作用于当前页面，但**自定义组件的样式隔离规则不同**：

| 场景 | 默认行为 |
| --- | --- |
| 页面 wxss | 只作用于当前页面 |
| 组件 wxss | 默认只作用于组件内，也不受页面样式影响 |
| 全局 app.wxss | 对所有页面生效，**但默认不作用于自定义组件内部** |
| 页面使用组件 | 页面样式**不会**影响组件内部节点（除非开启穿透） |

```javascript [custom-component.js]
Component({
  options: {
    // 让 app.wxss 中的样式也能作用于该组件（按需开启）
    addGlobalClass: true,
    // 允许外部类名穿透（配合 externalClasses 使用）
    styleIsolation: 'apply-shared',
  },
})
```

| `styleIsolation` 取值 | 含义 |
| --- | --- |
| `isolated`（默认） | 完全隔离，内外互不影响 |
| `apply-shared` | 外部样式可影响组件内，组件内不影响外部 |
| `shared` | 双向影响（谨慎使用，容易污染） |

::: warning 说明
`shared` 会让组件与页面样式互相污染，组件复用性大幅下降。**优先用 `externalClasses` 显式接收外部类名**，而不是直接打开 `shared`。
:::

## 字体图标

小程序没有 Web 的字体图标加载便利性，通常有两种做法：

| 方式 | 做法 | 特点 |
| --- | --- | --- |
| 字体图标（iconfont） | 下载字体文件，用 `@font-face` 引入 | 体积小、可改色，但需处理字体文件路径 |
| 图片 / SVG 图标 | 用 `<image>` 引用 | 简单，但不易改色、体积相对大 |

```css [app.wxss]
/* 注意：小程序不支持网络字体在部分平台的自动加载，建议使用本地字体文件 */
@font-face {
  font-family: 'iconfont';
  src: url('./assets/iconfont.ttf') format('truetype');
}

.iconfont {
  font-family: 'iconfont';
  font-size: 32rpx;
}
```

```html [使用方式]
<text class="iconfont">&#xe600;</text>
```

::: danger 注意
**小程序不支持 `@import` 跨包引用样式文件**，字体与图标资源必须放在可被打包到的目录中。另外，字体文件会占用主包体积（见 [分包加载](../Subpackage/index.md)），图标较多时优先考虑只引入必要字形。
:::

## 暗黑模式适配

小程序支持通过 `darkmode` 配置跟随系统主题：

```json [app.json]
{
  "darkmode": true,
  "themeLocation": "theme.json"
}
```

```json [theme.json]
{
  "light": {
    "bgColor": "#ffffff",
    "textColor": "#333333"
  },
  "dark": {
    "bgColor": "#1f1f1f",
    "textColor": "#e5e5e5"
  }
}
```

```css
/* 使用主题变量 */
.page {
  background: var(--bgColor);
  color: var(--textColor);
}
```

也可以直接用媒体查询：

```css
@media (prefers-color-scheme: dark) {
  .card { background: #1f1f1f; color: #e5e5e5; }
}
```

::: tip 建议
暗黑模式建议**从一开始就纳入设计**，而不是上线后再补。补做时最容易漏的是：图片背景（白底图在黑底上很刺眼）、阴影（黑底上阴影无效，需改用边框）、状态色（红绿在深色背景上的对比度）。
:::

## 验证方式

1. 在 iPhone 与宽屏设备（或开发者工具切换设备）上对比同一页面的 `rpx` 尺寸表现，确认布局没有明显失衡。
2. 在页面中给组件外层加一个通用类名，确认组件内部样式未被意外影响（验证隔离生效）。
3. 引入一个字体图标并在真机上确认能正常显示（模拟器与真机的字体加载行为可能不同）。
4. 切换系统主题，确认页面颜色随之变化且文字对比度足够。

## 相关专题

- [自定义组件](../CustomComponent/index.md)：组件样式隔离与 `externalClasses`
- [分包加载](../Subpackage/index.md)：字体与图标资源对包体积的影响
- [Skyline 渲染引擎](../Skyline/index.md)：新渲染引擎下的样式差异
- [组件](../Component/index.md)：内置组件的样式定制方式
- [微信小程序 配置文件](../Settings/index.md)：`darkmode` 等全局配置

## 参考资料

- 微信小程序官方文档 · WXSS：https://developers.weixin.qq.com/miniprogram/dev/framework/view/wxss.html
- 微信小程序官方文档 · 尺寸单位：https://developers.weixin.qq.com/miniprogram/dev/framework/view/wxss.html#尺寸单位
- 微信小程序官方文档 · 组件样式隔离：https://developers.weixin.qq.com/miniprogram/dev/framework/custom-component/wxml-wxss.html



