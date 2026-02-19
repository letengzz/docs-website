# CSS3 web字体

可以通过@font-face 指定字体的具体地址，浏览器会自动下载该字体，这样就不依赖用户电脑上的字体了。

## 基本用法

语法 (简写方式)：

```css
@font-face {
  font-family: "情书字体";
  src: url('./方正手迹.ttf');
}
```

语法 (高兼容性写法)：

```css
@font-face {
  font-family: "hjc";
  font-display: swap;
  src: url('webfont.eot'); /* IE9 */
  src: url('webfont.eot?#iefix') format('embedded-opentype'), /* IE6-IE8 */
  url('webfont.woff2') format('woff2'),
  url('webfont.woff') format('woff'), /* chrome、firefox */
  url('webfont.ttf') format('truetype'), /* chrome、firefox、opera、Safari,Android*/
  url('webfont.svg#webfont') format('svg'); /* iOS 4.1- */
}
```

## 定制字体

中文的字体文件很大，使用完整的字体文件不现实，通常针对某几个文字进行单独定制。

可使用阿里Web 字体定制工具： https://www.iconfont.cn/webfont

## 字体图标

- 相比图片更加清晰。
- 灵活性高，更方便改变大小、颜色、风格等。
- 兼容性好， IE 也能支持。

字体图标的具体使用方式，每个平台不尽相同，最好参考平台使用指南，以使用最多的阿里图标库作为演示。

阿里图标官网地址： https://www.iconfont.cn/