# HTML5 兼容性处理

添加元信息，让浏览器处于最优渲染模式：

```html
<!--设置IE总是使用最新的文档模式进行渲染-->
<meta http-equiv="X-UA-Compatible" content="IE=Edge" />
<!--优先使用 webkit ( Chromium ) 内核进行渲染, 针对360等壳浏览器-->
<meta name="renderer" content="webkit" />
```

使用 html5shiv 让低版本浏览器认识 H5 的语义化标签：

```html
<!--[if lt ie 9]>
  <script src="../sources/js/html5shiv.js"></script>
<![endif]-->
```

拓展：

- `lt`：小于。
- `lte`：小于等于。
- `gt`：大于。
- `gte`：大于等于。
- `!`：逻辑非。

```html
<!--[if IE 8]>仅IE8可见<![endif]-->
<!--[if gt IE 8]>仅IE8以上可见<![endif]—>
<!--[if lt IE 8]>仅IE8以下可见<![endif]—>
<!--[if gte IE 8]>IE8及以上可见<![endif]—>
<!--[if lte IE 8]>IE8及以下可见<![endif]—>
<!--[if !IE 8]>非IE8的IE可见<![endif]-->
```
