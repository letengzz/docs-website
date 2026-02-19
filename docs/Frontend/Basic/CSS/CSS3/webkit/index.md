# CSS3 私有前缀

代码中的 -webkit- 就是私有前缀：

```css
div {
  width:400px;
  height:400px;
  -webkit-border-radius: 20px;
}
```

W3C 标准所提出的某个 CSS 特性，在被浏览器正式支持之前，浏览器厂商会根据浏览器的内核，

使用私有前缀来测试该 CSS 特性，在浏览器正式支持该 CSS 特性后，就不需要私有前缀了。

```css
-webkit-border-radius: 20px;
-moz-border-radius: 20px;
-ms-border-radius: 20px;
-o-border-radius: 20px;
border-radius: 20px;
```

查询 CSS3 兼容性的网站：**https://caniuse.com/**

## 常见浏览器私有前缀

- Chrome **浏览器：** `-webkit-`
- Safari **浏览器**： `-webkit-`
- Firefox **浏览器：** `-moz-`
- Edge **浏览器：** `-webkit-`
- 旧 Opera 浏览器： `-o-`
- 旧 IE 浏览器： `-ms-`

:::danger

在编码时，不用过于关注浏览器私有前缀，不用绞尽脑汁的去记忆，也不用每个都去查询，因为常用的 CSS3 新特性，主流浏览器都是支持的，即便是为了老浏览器而加前缀，也可以借助现代的构建工具，去添加私有前缀。

:::