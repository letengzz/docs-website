# Flex 布局

弹性布局 (Flex布局) 是一种现代的CSS布局方式。

弹性布局具有以下特点：

1. **主轴与交叉轴**：弹性容器具有主轴 (main axis) 和交叉轴 (cross axis)。默认情况下，主轴是水平方向，交叉轴是垂直方向。

2. **弹性容器**：通过将父元素的display属性设置为`flex`或`inline-flex`来创建弹性容器。

   子元素的弹性项目：弹性容器中的每个子元素都成为弹性项目。子元素可以指定各自在主轴和交叉轴上的大小、顺序以及对齐方式等。

3. **主轴对齐**：弹性项目可以在主轴上按照一定比例分配空间，也可以使用`justify-content`属性定义主轴的对齐方式。

4. **交叉轴对齐**：弹性项目可以在交叉轴上进行对齐，包括顶部对齐、底部对齐、居中对齐等，使用`align-items`属性定义交叉轴对齐方式。

5. **换行与自动调整**：可控制弹性项目是否换行，并且具备自动调整元素大小的能力。

弹性布局简化了网页布局的开发过程，提供了更灵活、响应式的布局方式。它适用于各种屏幕尺寸和设备类型，并能够快速适应不同的布局需求。

## 创建Flex布局

通过使用`display: flex`属性来创建一个弹性容器，并在其中使用灵活的盒子模型来进行元素的排列和定位。

```css
<body>
    <div class="box">1</div>
    <div class="box">2</div>
    <div class="box">3</div>
    <div class="box">4</div>
    <div class="box">5</div>
</body>
<style>
    body{
        min-width: 800px;
        border: 6px solid black;
        display: flex;
    }
    .box{
        height: 200px;
        width: 200px;
        background-color: #0071FF;
        font-size: 40pt;
        border: 1px solid blue;

    }
</style>
```

![image-20240911211419182](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112114142.png)

## 容器的属性

### justify-content

justify-content属性定义了项目在主轴上的对齐方式。

```css
.box {
    display: flex;
    justify-content: flex-start | flex-end | center | space-between | space-around | space-evenly;
}
```

它可能取5个值，具体对齐方式与轴的方向有关。下面假设主轴为从左到右。

- flex-start (默认值)：左对齐
- flex-end：右对齐
- center： 居中
- space-between：两端对齐，项目之间的间隔都相等
- space-around：每个项目两侧的间隔相等。所以，项目之间的间隔比项目与边框的间隔大一倍
- space-evenly：将子元素沿主轴均匀分布，每个子元素之间的间距相等，同时第一个子元素与容器的起始端和最后一个子元素与容器的末尾端之间的间距也相等。这意味着空白空间将平均分配给所有子元素

![image-20240911223110693](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112231434.png)

### align-items

align-items属性定义项目在交叉轴上如何对齐。

```css
.box {
    display: flex;
    align-items: flex-start | flex-end | center | baseline | stretch;
}
```

它可能取5个值。具体的对齐方式与交叉轴的方向有关，下面假设交叉轴从上到下。

- flex-start：交叉轴的起点对齐
- flex-end：交叉轴的终点对齐
- center：交叉轴的中点对齐
- baseline: 项目的第一行文字的基线对齐
- stretch (默认值)：如果项目未设置高度或设为auto，将占满整个容器的高度

![image-20240911222527537](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112225071.png)

### flex-direction

决定主轴的方向，水平或者垂直

```css
.box {
    display: flex;
    flex-direction: row | row-reverse | column | column-reverse;
}
```

- row (默认值)：主轴为水平方向，起点在左端
- row-reverse：主轴为水平方向，起点在右端
- column：主轴为垂直方向，起点在上沿
- column-reverse：主轴为垂直方向，起点在下沿

![image-20240911224251682](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112242218.png)

### flex-wrap

换行不换行以及换行的方向

```css
.box{
    display: flex;
    flex-wrap: nowrap | wrap | wrap-reverse;
}
```

- nowrap (默认)：不换行
- wrap：换行，第一行在上方
- wrap-reverse：换行，第一行在下方

![image-20240911231616349](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112316241.png)

当小于某宽度则换行：

```css
@media(max-width:575px){
    body{
        flex-wrap: wrap;
    }
}
```

### align-content

align-content属性定义了多根轴线的对齐方式。如果项目只有一根轴线，该属性不起作用。

```css
.box {
    display: flex;
    flex-wrap: wrap | wrap-reverse;
    align-content: flex-start | flex-end | center | space-between | space-around | stretch;
}
```

- flex-start：与交叉轴的起点对齐
- flex-end：与交叉轴的终点对齐
- center：与交叉轴的中点对齐
- space-between：与交叉轴两端对齐，轴线之间的间隔平均分布
- space-around：每根轴线两侧的间隔都相等。所以，轴线之间的间隔比轴线与边框的间隔大一倍
- stretch (默认值)：轴线占满整个交叉轴
- space-evenly：将子元素沿主轴均匀分布，每个子元素之间的间距相等，同时第一个子元素与容器的起始端和最后一个子元素与容器的末尾端之间的间距也相等。这意味着空白空间将平均分配给所有子元素

![image-20240911234439934](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112344790.png)

### gap

gap是CSS3中的新特性，用于设置flex容器中子元素之间的间距。它可以通过设置gap属性来实现，但是在一些旧版本的浏览器中可能不被支持。具体而言，IE11及以下版本的浏览器不支持flex gap属性，而在其他浏览器中，如Chrome、Firefox、Safari等，支持程度也有所不同。为了解决这个问题，可以使用其他方法来实现类似的效果，如使用margin或padding属性来设置子元素之间的间距。另外，也可以使用一些CSS预处理器或后处理器，如Sass、PostCSS等，来实现类似的效果。总之，需要根据具体情况来选择最适合的方法来实现flex容器中子元素之间的间距。

```css
.box{
    display: flex;
    gap: 10px;
}
```

![image-20240911224616877](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112246588.png)

### row-gap

行间距

### column-gap

列间距

### flex-grow

flex-grow属性定义项目的放大比例，默认为0，即如果存在剩余空间，也不放大。

```css
.item {
    display: flex;
    flex-grow: <number>; /* default 0 */
}
```

如果所有项目的flex-grow属性都为1，则它们将等分剩余空间（如果有的话）。如果一个项目的flex-grow属性为2，其他项目都为1，则前者占据的剩余空间将比其他项多一倍。

![image-20240911235955142](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112359506.png)

![image-20240912000333559](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409120003785.png)

### flex-shrink

flex-shrink属性定义了项目的缩小比例，默认为1，即如果空间不足，该项目将缩小。

```css
.item {
    display: flex;
    flex-shrink: <number>; /* default 1 */
}
```

如果所有项目的flex-shrink属性都为1，当空间不足时，都将等比例缩小。如果一个项目的flex-shrink属性为0，其他项目都为1，则空间不足时，前者不缩小。
![image-20240911235542867](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409112355189.png)

负值对该属性无效。

### align-self

align-self属性允许单个项目有与其他项目不一样的对齐方式，可覆盖align-items属性。默认值为auto，表示继承父元素的align-items属性，如果没有父元素，则等同于stretch。

```css
.item {
    display: flex;
    align-self: auto | flex-start | flex-end | center | baseline | stretch;
}
```

该属性可能取6个值，除了auto，其他都与align-items属性完全一致。

![image-20240912001105720](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409120011648.png)

并没有`justify-self`来控制对齐方式，可以使用margin来解决：

```css
    body {
        min-width: 800px;
        min-height: 800px;
        border: 6px solid black;
        display: flex;
        gap: 10px;
        align-items: flex-start;
        justify-content: flex-end;
    }

    #box-1 {
        margin-right: auto;
    }

    .box {
        height: 200px;
        width: 200px;
        background-color: #0071FF;
        font-size: 40pt;
        border: 1px solid blue;
    }
```

### flex-flow

以上两种的简写方式

```css
.box {
  flex-flow: <flex-direction> || <flex-wrap>;
}
```

### order

order属性定义项目的排列顺序。数值越小，排列越靠前，默认为0。

```css
.item {
  order: <integer>;
}
```

![image-20240912001553853](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409120015237.png)

### flex-basis

flex-basis属性定义了在分配多余空间之前，项目占据的主轴空间（main size）。浏览器根据这个属性，计算主轴是否有多余空间。它的默认值为auto，即项目的本来大小。

```css
.item { 
    flex-basis: <length> | auto; /* default auto */
}
```

它可以设为跟width或height属性一样的值（比如350px），则项目将占据固定空间。

### flex

flex属性是flex-grow、flex-shrink 和 flex-basis的简写，默认值为0、1、auto。后两个属性可选。

```css
.item {
  flex: none | [ <'flex-grow'> <'flex-shrink'>? || <'flex-basis'> ]
}
```

该属性有两个快捷值：auto (1 1 auto) 和 none (0 0 auto)。

建议优先使用这个属性，而不是单独写三个分离的属性，因为浏览器会推算相关值。