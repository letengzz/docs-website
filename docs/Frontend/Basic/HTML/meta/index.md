# HTML meta元信息

完整的网页元信息，请参考： [文档级元数据元素 | MDN](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/meta)

## 配置字符编码

计算机对数据的操作：

- 存储时，对数据进行：编码。
- 读取时，对数据进行：解码。

编码、解码，会遵循一定的规范：字符集。

字符集有很多中，常见的有：

1. ASCII ：大写字母、小写字母、数字、一些符号，共计128个。
2. ISO 8859-1 ：在 ASCII 基础上，扩充了一些希腊字符等，共计是256个。
3. GB2312 ：继续扩充，收录了 6763 个常用汉字、682个字符。
4. GBK ：收录了的汉字和符号达到 20000+ ，支持繁体中文。
5. UTF-8 ：包含世界上所有语言的：所有文字与符号 (很常用)。

使用原则：

1. 存储时，务必采用合适的字符编码，否则：无法存储，数据会丢失！

2. 存储时，采用哪种方式编码 ，读取时就采用哪种方式解码，否则：数据错乱 (乱码)！

   例如下面文字中，包含有：中文、英文、泰文、缅甸文

   ```text
   我爱你
   I love you!
   ฉันรักเธอนะ
   က
   ```

若使用 ISO8859-1 编码存储，在存入的那一刻，就出问题了，因为ISO8859-1 仅支持英文！

为保证所有的输入，都能正常存储和读取，现在几乎全都采用： UTF-8 编码。UTF-8 包括绝大多数人类书面语言的大多数字符、有了这个设置，页面现在可以处理它可能包含的任何文本内容，如果不加这句话可能会引起乱码。所以编写html 文件时，也都统一用UTF-8 编码。

```html
<meta charset="utf-8" />
```

## 针对IE 浏览器的兼容性配置。

```html
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
```

## 针对移动端的配置

`<meta name="viewport" content="width=device-width, initial- scale=1.0">`
开发者能确保网页在移动设备上以最佳状态呈现 (移动端页面适配)，提升用户浏览体验。

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

## 配置网页关键字

```html
<meta name="keywords" content="8-12个以英文逗号隔开的单词/词语" />
```

## 配置网页描述信息

```html
<meta name="description" content="80字以内的一段话，与网站内容相关" />
```

## 针对搜索引擎爬虫配置

```html
<meta name="robots" content="此处可选值见下表" />
```

| 值        | 描述                               |
| --------- | ---------------------------------- |
| index     | 允许搜索爬虫索引此页面。           |
| noindex   | 要求搜索爬虫不索引此页面。         |
| follow    | 允许搜索爬虫跟随此页面上的链接。   |
| nofollow  | 要求搜索爬虫不跟随此页面上的链接。 |
| all       | 与 index, follow 等价              |
| none      | 与 noindex, nofollow 等价          |
| noarchive | 要求搜索引擎不缓存页面内容。       |
| nocache   | noarchive 的替代名称。             |

## 配置网页作者

```html
<meta name="author" content="tony" />
```

## 配置网页生成工具

```html
<meta name="generator" content="Visual Studio Code" />
```

## 配置定义网页版权信息

```html
<meta name="copyright" content="2023-2027©版权所有" />
```

## 配置网页自动刷新

```html
<meta http-equiv="refresh" content="10;url=http://www.baidu.com" />
```

## 相关专题

- [浏览器原理](../../Browser/index.md)
