# 优化CSS代码技巧

## 避免高消耗属性

分析表明，一些 CSS 属性的渲染速度比其他属性慢，因此应该谨慎使用。包括以下属性：

- box-shadow
- border-radius
- position: fixed
- transform
- :nth-child
- filter

上述属性都是对性能要求比较高的。如果这些属性使用较少，那这就不是问题。但是如果一个页面出现几百次，那么整体的 CSS 可能会受到影响，所以要谨慎使用。

## 使用 `<link>` 代替 @import

@import 规则主要用于导入资源或者 CSS 文件。它会阻止其他文件并行下载，并可能会导致网站速度变慢。

❌ 不要在 CSS 中这样操作：

```css
@import url('header.css');
@import url('slider.css');
@import url('content.css');
@import url('footer.css');
```

可以使用多个 HTML 中的`<link>`标签来代替 @import，它将并行加载 CSS 文件，可以在一定程度上提高应用的加载的速度。

✅ 可以在 HTML 这样操作：

```css
<link rel="stylesheet" href="header.css">
<link rel="stylesheet" href="slider.css">
<link rel="stylesheet" href="content.css">
<link rel="stylesheet" href="footer.css">
```

## 简化选择器

有很多方法可以对 HTML 元素进行样式设置，而最复杂的 CSS 选择器可能需要几毫秒的时间来解析。降低选择器的复杂性就可以减少浏览器的负载并保持代码简洁明了。

❌ 避免这么写：

```css
.container > div.links-container ul li .link {
}
```

✅ 可以这么写：

```css
.container .link {
}
```

## 避免使用 !Important

在一些时候，可以使用 !Important 来提高样式的优先级，以使样式生效。除非没有别的办法，否则不要使用 !Important。

添加 !Important CSS 声明将覆盖掉其他对应的样式声明，如果 CSS 的规则中 !Important 太多，浏览器就必须对代码进行额外的检查，这可能会降低页面的加载速度。所以，尽量避免使用 !Important。在很多情况下我们是可以通过选择器来实现样式重写的，除非是想要对第三方库的 CSS 进行重写。

## CSS实现特效和SVG代替图片

页面中加载图像很可能需要很长的时间，尤其是在图像未针对 web 进行优化的情况下。在实现背景图、渐变、几何图形时，尽量少使用图片，而是使用 CSS 代码实现。使用 CSS 代码实现就会比图片加载速度更快。

还可以使用 SVG 来代替 PNG 或者 JPG 图片：

- 可以给图片添加效果；
- 图像加载速度更快；
- 图像自动适应用户屏幕。

## 压缩 CSS

我们可以通过压缩 CSS 文件来删除文件中所有的空白和不必要的代码来减少文件的大小。CSS 文件变小了，加载的时间自然就变少了，页面的加载速度就会变。

## 使用0而不是0px

当一个属性的值为 0 时，我们可以不添加任何单位。即不要这么写：0rem，0em，0px等。

当然，这么写是没有错的，但是这些单位是没有用的，当处理一个巨大的 CSS 文件时，没有单位会比有单位时文件小一点。

## 使用十六进制而不是颜色名称

当我们将颜色设置为颜色名称时，浏览器就会花费更多时间来找出颜色的十六进制值。假如想使用红色，那设置为 color:red 之后，不同的浏览器显示效果可能是不一样的，作为开发人员，我们不能让浏览器来决定网页将如何显示。

因此，尽量使用使用十六进制（例如红色 #ff0000）来定义颜色，就能确保在所有浏览器中以相同的色调准确得显示想要的颜色。

## 避免过多 font-family

为每个选择器去定义字体并不是一个好的办法，它会导致代码很难维护，假如以后想要更改字体，就不得不在每个选择器中更改它。

因此不要像下面这样来定义字体：

```css
h1 {
  font-family: Arial, Helvetica, sans-serif;
}

p {
  font-family: Arial, Helvetica, sans-serif;
}

.selection {
  font-family: Arial, Helvetica, sans-serif;
}

.footer {
  font-family: 'Times New Roman', Times, serif;
}
```

可以在正文中定义要使用的字体，如果想要在其他选择器中覆盖该字体，就可以通过在该选择器中使用所需的字体来实现：

```css
body{
  font-family: Arial, Helvetica, sans-serif;
}

footer{
  font-family: "Times New Roman", Times, serif";
}
```

如果页面中很多部分的字体都不尽相同，就可以将字体定义在 class 中，然后在需要的 HTML 标签上使用该 class 即可：

```css
.font-helvetica {
  font-family: Arial, Helvetica, sans-serif;
}

.font-times {
  font-family: "Times New Roman", Times, serif";
}
```

## 使用备用字体

有些情况下，应用中使用的字体可能在用户设备上不可用。在这种情况下，可以指定使用其他备用字体：

```css
p {
  font-family: 'Open Sans', Arial, Helvetica, sans-serif;
}
```

这样，浏览器就会按顺序进行解析，直到解析到第一个可用的字体，如果都不可用，就会使用浏览器的默认字体。

## 使用 CSS 重置

每个浏览器都有自己的 HTML 元素默认样式。假如有一个没有任何样式的 H1 元素，那么在默认情况下，在 Firefox 中，会给它一个上下为21.433px，左右为 0 的 margin 值。而在 Safari 中，会给它一个上下为 21px，左右为 0 的 margin 值。

因此，重置 CSS 样式，一个很好的做法就是从头开始定义样式。很多开发人员会使用通用选择器（\*）来执行基本重置：

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

在使用通用选择器 (\*) 进行重置有时会导致性能问题，因为它会针对每个标签去设置其样式。

可以使用一些常用的 CSS 重置代码库，比如 normalize。也可以参考一些 CSS 重置的最佳实践。

## 减少重复代码

当两个元素或选择器具有相同的 CSS 属性时，可以使用逗号来组合这些选择器，而不是重复声明样式，这样它们将共享 CSS 样式。

❌ 避免这样写：

```css
.header {
  background-color: #fefefe;
  padding: 20px 0;
}

.footer {
  background-color: #fefefe;
  padding: 20px 0;
}
```

✅ 建议这样写：

```css
.header,
.footer {
  background-color: #fefefe;
  padding: 20px 0;
}
```
