# CSS3 BFC

W3C 上对 BFC 的定义：

> 原文：Floats, absolutely positioned elements, block containers (such as inline-blocks, tablecells,
> and table-captions) that are not block boxes, and block boxes with 'overflow' other than
> 'visible' (except when that value has been propagated to the viewport) establish new block
> formatting contexts for their contents.
>
> 译文：浮动、绝对定位元素、不是块盒子的块容器（如inline-blocks 、table-cells 和
> table-captions ），以及overflow 属性的值除visible 以外的块盒，将为其内容建立新
> 的块格式化上下文。

MDN 上对 BFC 的描述：

> 块格式化上下文（Block Formatting Context，BFC） 是Web 页面的可视CSS 渲染的一部分，是块盒子的布局过程发生的区域，也是浮动元素与其他元素交互的区域。

更加通俗的描述：

1. BFC 是 Block Formatting Context （块级格式上下文），可以理解成元素的一个"特异功能"。
2. 该 "特异功能"，在默认的情况下处于关闭状态；当元素满足了某些条件后，该“特异功
能”被激活。
3. 所谓激活"特异功能"，专业点说就是：该元素创建了 BFC (又称：开启了 BFC )。

开启了BFC能解决什么问题：

1. 元素开启BFC 后，其子元素不会再产生margin 塌陷问题。
2. 元素开启BFC 后，自己不会被其他浮动元素所覆盖。
3. 元素开启BFC 后，就算其子元素浮动，元素自身高度也不会塌陷。

开启BFC：

- 根元素
- 浮动元素
- 绝对定位、固定定位的元素
- 行内块元素
- 表格单元格： table 、thead 、tbody 、tfoot 、th 、td 、tr 、caption
- overflow 的值不为 visible 的块元素
- 伸缩项目
- 多列容器
- column-span 为 all 的元素（即使该元素没有包裹在多列容器中）
- display 的值，设置为flow-root