# CSS3 新增功能

## 新增长度单位

1. rem 根元素字体大小的倍数，只与根元素字体大小有关。

2. vw 视口宽度的百分之多少 10vw 就是视口宽度的 10% 。

3. vh 视口高度的百分之多少 10vh 就是视口高度的 10% 。

4. vmax 视口宽高中大的那个的百分之多少。

5. vmin 视口宽高中小的那个的百分之多少。

## 新增颜色设置方式

CSS3 新增了三种颜色设置方式，分别是： rgba 、 hsl 、 hsla。

## 新增选择器

CSS3 新增的选择器有：动态伪类、目标伪类、语言伪类、 UI 伪类、结构伪类、否定伪类、伪元素。

## 新增盒模型相关属性

### box-sizing 怪异盒模型

使用 box-sizing 属性可以设置盒模型的两种类型：

- content-box：width 和 height 设置的是盒子内容区的大小。（默认值）
- border-box：width 和 height 设置的是盒子总大小。（怪异盒模型）

### resize 调整盒子大小

使用 resize 属性可以控制是否允许用户调节元素尺寸。

| 值         | 含义                          |
| ---------- | ----------------------------- |
| none       | 不允许用户调整元素大小 (默认) |
| both       | 用户可以调节元素的宽度和高度  |
| horizontal | 用户可以调节元素的宽度        |
| vertical   | 用户可以调节元素的高度        |

### box-shadow 盒子阴影

使用 box-shadow 属性为盒子添加阴影。

| 值       | 含义                                 |
| -------- | ------------------------------------ |
| h-shadow | 水平阴影的位置，必须填写，可以为负值 |
| v-shadow | 垂直阴影的位置，必须填写，可以为负值 |
| blur     | 可选，模糊距离                       |
| spread   | 可选，阴影的外延值                   |
| color    | 可选，阴影的颜色                     |
| inset    | 可选，将外部阴影改为内部阴影         |

**语法**：

```css
box-shadow: h-shadow v-shadow blur spread color inset;
```

**默认值**： box-shadow:none 表示没有阴影

例：

```css
/* 写两个值，含义：水平位置、垂直位置 */
box-shadow: 10px 10px;
/* 写三个值，含义：水平位置、垂直位置、颜色 */
box-shadow: 10px 10px red;
/* 写三个值，含义：水平位置、垂直位置、模糊值 */
box-shadow: 10px 10px 10px;
/* 写四个值，含义：水平位置、垂直位置、模糊值、颜色 */
box-shadow: 10px 10px 10px red;
/* 写五个值，含义：水平位置、垂直位置、模糊值、外延值、颜色 */
box-shadow: 10px 10px 10px 10px blue;
/* 写六个值，含义：水平位置、垂直位置、模糊值、外延值、颜色、内阴影 */
box-shadow: 10px 10px 20px 3px blue inset;
```

### opacity 不透明度

opacity 属性能为整个元素添加透明效果， 值是 0 到 1 之间的小数， 0 是完全透明， 1 表示完全不透明。

opacity 与 rgba 的区别：

- opacity 是一个属性，设置的是整个元素（包括元素里的内容）的不透明度。
- rgba 是颜色的设置方式，用于设置颜色，它的透明度，仅仅是调整颜色的透明度。

## 新增背景属性

### background-origin

作用：设置背景图的原点。

语法

1. padding-box (默认值)：从 padding 区域开始显示背景图像。

2. border-box ： 从 border 区域开始显示背景图像。

3. content-box ： 从 content 区域开始显示背景图像。

### background-clip

作用：设置背景图的向外裁剪的区域。

语法

1. border-box (默认值)： 从 border 区域开始向外裁剪背景。

2. padding-box ： 从 padding 区域开始向外裁剪背景。

3. content-box ： 从 content 区域开始向外裁剪背景。

4. text ：背景图只呈现在文字上。

:::danger

若值为 text ，那么 backgroun-clip 要加上 -webkit- 前缀。

:::

### background-size

作用：设置背景图的尺寸。

语法：

1. 用长度值指定背景图片大小，不允许负值。

   ```css
   background-size: 300px 200px;
   ```

2. 用百分比指定背景图片大小，不允许负值。

   ```css
   background-size: 100% 100%;
   ```

3. auto (默认值)： 背景图片的真实大小。 

4. contain ： 将背景图片等比缩放，使背景图片的宽或高，与容器的宽或高相等，再将完整背景图片包含在容器内，但要注意：可能会造成容器里部分区域没有背景图片。

   ```css
   background-size: contain;
   ```

5. cover ：将背景图片等比缩放，直到完全覆盖容器，图片会尽可能全的显示在元素上，但要背景图片有可能显示不完整 (相对比较好的选择)。

   ```css
   background-size: cover;
   ```

### backgorund 复合属性

语法：

```css
background: color url repeat position / size origin clip
```

:::danger

1. origin 和 clip 的值如果一样，如果只写一个值，则 origin 和 clip 都设置；如果设置了两个值，前面的是 origin ，后面的 clip 。

2. size 的值必须写在 position 值的后面，并且用 / 分开。

:::

### 多背景图

CSS3 允许元素设置多个背景图片。

```css
/* 添加多个背景图 */
background: url(../images/bg-lt.png) no-repeat,
   url(../images/bg-rt.png) no-repeat right top,
   url(../images/bg-lb.png) no-repeat left bottom,
   url(../images/bg-rb.png) no-repeat right bottom;
```

## 新增边框属性

### 边框圆角

在 CSS3 中，使用 border-radius 属性可以将盒子变为圆角。

同时设置四个角的圆角：

```css
border-radius:10px;
```

分开设置每个角的圆角：

| 属性名                     | 作用                                                         |
| -------------------------- | ------------------------------------------------------------ |
| border-top-left-radius     | 设置左上角圆角半径：<br />1. 一个值是正圆半径<br />2. 两个值分别是椭圆的 x 半径、 y 半径 |
| border-top-right-radius    | 设置右上角圆角半径：<br />1. 一个值是正圆半径<br />2. 两个值分别是椭圆的 x 半径、 y 半径 |
| border-bottom-right-radius | 设置右下角圆角半径：<br />1. 一个值是正圆半径<br />2. 两个值分别是椭圆的 x 半径、 y 半径 |
| border-bottom-left-radius  | 设置左下角圆角半径：<br />1. 一个值是正圆半径<br />2. 两个值分别是椭圆的 x 半径、 y 半径 |

分开设置每个角的圆角，综合写法（几乎不用）：

```css
border-raidus: 左上角x 右上角x 右下角x 左下角x / 左上y 右上y 右下y 左下y
```

### 边框外轮廓

- outline-width ：外轮廓的宽度。

- outline-color ：外轮廓的颜色。

- outline-style ：外轮廓的风格。

  - none ： 无轮廓

  - dotted ： 点状轮廓

  - dashed ： 虚线轮廓

  - solid ： 实线轮廓

  - double ： 双线轮廓

- outline-offset 设置外轮廓与边框的距离，正负值都可以设置。

:::danger

outline-offset 不是 outline 的子属性，是一个独立的属性。

:::

outline 复合属性：

```css
outline:50px solid blue;
```

## 新增文本属性

### 文本阴影

在 CSS3 中，可以使用 text-shadow 属性给文本添加阴影。

语法：

```css
text-shadow: h-shadow v-shadow blur color;
```

| 值       | 描述                               |
| -------- | ---------------------------------- |
| h-shadow | 必需写，水平阴影的位置。允许负值。 |
| v-shadow | 必需写，垂直阴影的位置。允许负值。 |
| blur     | 可选，模糊的距离。                 |
| color    | 可选，阴影的颜色。                 |

默认值： text-shadow:none 表示没有阴影。

### 文本换行

在 CSS3 中，我们可以使用 white-space 属性设置文本换行方式。

| 值              | 含义                                                         |
| --------------- | ------------------------------------------------------------ |
| normal (默认值) | 文本超出边界自动换行，文本中的换行被浏览器识别为一个空格。   |
| pre             | 原样输出，与 pre 标签的效果相同                              |
| pre-wrap        | 在 pre 效果的基础上，超出元素边界自动换行                    |
| pre-line        | 在 pre 效果的基础上，超出元素边界自动换行，且只识别文本中的换行，空格会忽略 |
| nowrap          | 强制不换行                                                   |

### 文本溢出

在 CSS3 中，可以使用 text-overflow 属性设置文本内容溢出时的呈现模式。

| 值            | 含义                                       |
| ------------- | ------------------------------------------ |
| clip (默认值) | 当内联内容溢出时，将溢出部分裁切掉         |
| ellipsis      | 内联内容溢出块容器时，将溢出部分替换为 ... |

:::danger

要使得 text-overflow 属性生效，块容器必须显式定义 overflow 为非 visible值， white-space 为 nowrap 值。

:::

### 文本修饰

CSS3 升级了 text-decoration 属性，让其变成了复合属性。

```css
text-decoration: text-decoration-line || text-decoration-style || text-decoration-color
```

子属性及其含义：

- text-decoration-line 设置文本装饰线的位置

  - none (默认值)： 指定文字无装饰 

  - underline： 指定文字的装饰是下划线

  - overline ： 指定文字的装饰是上划线

  - line-through ： 指定文字的装饰是贯穿线

- text-decoration-style 文本装饰线条的形状

  - solid (默认)： 实线 

  - double ： 双线

  - dotted ： 点状线条

  - dashed ： 虚线

  - wavy ： 波浪线

- text-decoration-color 文本装饰线条的颜色


### 文本描边

:::danger

文字描边功能仅 webkit 内核浏览器支持。

:::

- -webkit-text-stroke-width ：设置文字描边的宽度，写长度值。
- -webkit-text-stroke-color ：设置文字描边的颜色，写颜色值。
- -webkit-text-stroke ：复合属性，设置文字描边宽度和颜色。

## 新增渐变

### 线性渐变

多个颜色之间的渐变， 默认**从上到下**渐变：

```css
background-image: linear-gradient(red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0.jpg)

使用关键词设置线性**渐变的方向**：

```css
background-image: linear-gradient(to top,red,yellow,green);
background-image: linear-gradient(to right top,red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-17714203329752.jpg)

使用角度设置线性**渐变的方向**：

```css
background-image: linear-gradient(30deg,red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-17714203927226.jpg)

调整开始**渐变的位置**：

```css
background-image: linear-gradient(red 50px,yellow 100px ,green 150px);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-17714204175698.jpg)

### 径向渐变

多个颜色之间的渐变， 默认从圆心四散：

:::danger

不一定是正圆，要看容器本身宽高比

:::

```css
background-image: radial-gradient(red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-177142047290110.jpg)

使用关键词调整渐变圆的圆心位置：

```css
background-image: radial-gradient(at right top,red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-17714760441961.jpg)

使用像素值调整渐变圆的圆心位置：

```css
background-image: radial-gradient(at 100px 50px,red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-17714760726433.jpg)

调整渐变形状为正圆：

```css
background-image: radial-gradient(circle,red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-17714760897605.jpg)

调整形状的半径：

```css
background-image: radial-gradient(100px,red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-17714761106437.jpg)

```css
background-image: radial-gradient(50px 100px,red,yellow,green);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-17714761214669.jpg)

调整开始渐变的位置：

```css
background-image: radial-gradient(red 50px,yellow 100px,green 150px);
```

![](assets/CSS3%E7%AC%94%E8%AE%B0-177147613210311.jpg)

###  重复渐变

无论线性渐变，还是径向渐变，在没有发生渐变的位置，继续进行渐变，就为重复渐变。

- 使用 repeating-linear-gradient 进行重复线性渐变，具体参数同 linear-gradient 。
- 使用 repeating-radial-gradient 进行重复径向渐变，具体参数同 radial-gradient 。

可以利用渐变，做出很多有意思的效果：例如：横格纸、立体球等等。