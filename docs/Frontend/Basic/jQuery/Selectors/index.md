# jQuery 选择器

jQuery选择器是jQuery最核心的功能之一，它基于CSS选择器的语法，并扩展了一些特有的选择器，使得HTML元素的选取变得异常灵活和强大。通过jQuery选择器，可以快速定位到页面中的任何一个元素，然后对其进行各种操作。jQuery选择器完全兼容CSS1到CSS3的选择器规范，这意味着任何有效的CSS选择器都可以在jQuery中使用。此外，jQuery还提供了一些自定义的选择器，这些选择器在原生CSS中并不存在，但在实际开发中非常实用。

## 基本选择器

基本选择器是jQuery中最简单也是最常用的选择器，它们构成了jQuery选择器体系的基础。标签选择器通过元素的名称来选取所有匹配的DOM元素，返回值是一个包含所有匹配元素的jQuery对象。类选择器通过元素的class属性值来选取元素，需要在class名称前加上点号。ID选择器通过元素的id属性值来精确选取单个元素，需要在id名称前加上井号。这三种基本选择器是日常开发中使用频率最高的，熟练掌握它们是使用jQuery的前提条件。

```html [index.html]
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>jQuery选择器示例</title>
</head>
<body>
    <div id="header">页面头部</div>
    <div class="container">
        <p>段落一</p>
        <p class="highlight">高亮段落</p>
        <span>行内元素</span>
    </div>
    <div id="footer">页面底部</div>
</body>
</html>
```

```javascript [script.js]
// 标签选择器：选取所有div元素
$('div').css('border', '1px solid blue');

// 类选择器：选取所有class为container的元素
$('.container').css('padding', '20px');

// ID选择器：选取id为header的元素
$('#header').css('background', 'lightgray');

// 组合选择器：同时选取多种元素
$('p, span').css('color', 'red');

// 通配符选择器：选取所有元素
$('*').css('margin', '0');
```

::: tip
使用ID选择器时需要注意，同一个页面上应该只有一个元素使用特定的ID，因为ID在HTML文档中应该是唯一的。如果页面中存在多个相同ID的元素，使用ID选择器只会返回第一个匹配的元素，而后续的元素将无法被正确选取。
:::

## 层级选择器

层级选择器通过元素之间的层级关系来选取元素，这是处理嵌套元素时最常用的选择器方式。 descendant选择器（空格）会选取指定元素的所有后代元素，包括子元素、孙元素等任何层级的后代。child选择器（大于号）只选取指定元素的直接子元素，不包含孙元素及更深层级的元素。next选择器（加号）选取指定元素后面紧邻的同级元素。siblings选择器（波浪号）选取指定元素后面所有同级兄弟元素。这些层级选择器可以组合使用，构建出非常精准的元素定位表达式。

```html [index.html]
<div class="parent">
    <div class="child">子元素1</div>
    <div class="child">
        <div class="grandchild">孙元素</div>
    </div>
    <span>span元素</span>
</div>
<div class="sibling">兄弟元素1</div>
<div class="sibling">兄弟元素2</div>
```

```javascript [script.js]
// 后代选择器：选取parent内所有div后代
$('.parent div').css('border', '1px solid red');

// 子选择器：选取parent的直接div子元素
$('.parent > div').css('background', 'lightyellow');

// 下一个兄弟选择器：选取parent后紧邻的div兄弟
$('.parent + div').css('margin-top', '20px');

// 所有兄弟选择器：选取parent后所有div兄弟
$('.parent ~ div').css('color', 'blue');

// 组合使用
$('.parent .child').first().css('font-weight', 'bold');
```

## 过滤选择器

过滤选择器是在基本选择器的基础上，通过添加过滤条件来缩小选取范围。jQuery提供了丰富的过滤选择器，包括基于元素位置的过滤、基于元素状态的过滤以及基于元素内容的过滤等。位置过滤选择器如`:first`、`:last`、`:even`、`:odd`、`:eq()`、`:lt()`、`:gt()`等，可以根据元素在匹配集合中的位置来筛选元素。状态过滤选择器如`:visible`、`:hidden`、`:animated`、`:focus`等，可以根据元素的当前状态来选取元素。这些过滤选择器可以与任何基本选择器组合使用，形成强大的元素筛选能力。

```html [index.html]
<ul id="users">
    <li>用户1</li>
    <li>用户2</li>
    <li>用户3</li>
    <li>用户4</li>
    <li>用户5</li>
</ul>
<div>可见的div</div>
<div style="display: none;">隐藏的div</div>
```

```javascript [script.js]
// 第一个和最后一个
$('li:first').css('color', 'red');
$('li:last').css('color', 'blue');

// 奇数项和偶数项（基于0的索引）
$('li:even').css('background', '#f0f0f0');
$('li:odd').css('background', '#ffffff');

// 指定索引位置的元素
$('li:eq(2)').css('font-weight', 'bold');  // 第三项
$('li:lt(2)').css('text-decoration', 'underline'); // 前两项
$('li:gt(2)').css('font-style', 'italic'); // 后两项

// 根据可见性过滤
$('div:visible').show();          // 显示所有可见的div
$('div:hidden').show();           // 显示所有隐藏的div
```

::: danger
在使用`:eq()`、`:lt()`、`:gt()`等索引过滤选择器时，需要特别注意索引是从0开始的。这意味着`:eq(0)`选取的是第一个元素，而不是第二个。此外，这些过滤选择器在大型集合上的性能可能不如原生数组方法（如`slice()`、`first()`、`last()`）高效。
:::

## 属性选择器

属性选择器通过元素的属性或属性值来选取元素，这是处理具有特定属性特征的元素的利器。jQuery支持多种属性选择器语法，包括存在性选择器、精确值选择器、包含选择器、开头选择器和结尾选择器等。存在性选择器`[attribute]`选取具有指定属性的所有元素，无论属性值是什么。精确值选择器`[attribute="value"]`选取属性值完全等于指定值的元素。包含选择器`[attribute*="value"]`选取属性值包含指定字符串的元素。开头选择器`[attribute^="value"]`选取属性值以指定字符串开头的元素。结尾选择器`[attribute$="value"]`选取属性值以指定字符串结尾的元素。

```html [index.html]
<input type="text" name="username" placeholder="用户名">
<input type="password" name="password" placeholder="密码">
<input type="email" name="email" placeholder="邮箱">
<a href="http://example.com">链接1</a>
<a href="https://secure.example.com">链接2</a>
<a href="ftp://files.example.com">链接3</a>
<input type="checkbox" checked>
<input type="checkbox">
```

```javascript [script.js]
// 存在性选择器
$('input[name]').css('border', '1px solid blue');

// 精确值选择器
$('input[type="text"]').val('默认文本');

// 值开头选择器
$('a[href^="http"]').css('color', 'blue');

// 值结尾选择器
$('a[href$=".com"]').css('font-weight', 'bold');

// 值包含选择器
$('input[name*="word"]').css('background', 'lightyellow');

// 多属性选择器
$('input[type="text"][name^="user"]').val('多属性匹配');

// 值不等于选择器
$('input[name!="password"]').css('width', '200px');
```

## 表单选择器

表单选择器是jQuery专门为表单元素设计的一组选择器，它们可以快速选取各种类型的表单元素。表单选择器包括`:input`（选取所有表单元素）、`:text`（选取文本框）、`:password`（选取密码框）、`:radio`（选取单选框）、`:checkbox`（选取复选框）、`:submit`（选取提交按钮）、`:reset`（选取重置按钮）、`:button`（选取普通按钮）、`:file`（选取文件上传框）以及`:hidden`（选取隐藏域）等。这些选择器使得表单操作变得异常简单，无论是表单验证、数据获取还是表单提交处理，都能快速定位到目标元素。

```html [index.html]
<form id="loginForm">
    <input type="text" name="username" id="username">
    <input type="password" name="password" id="password">
    <input type="checkbox" name="remember" id="remember">
    <select name="city" id="city">
        <option value="beijing">北京</option>
        <option value="shanghai">上海</option>
    </select>
    <textarea name="bio" id="bio"></textarea>
    <button type="submit">提交</button>
</form>
```

```javascript [script.js]
// 选取所有表单元素
var allInputs = $('#loginForm :input');

// 选取所有文本类输入框
$(':text').css('border', '1px solid gray');

// 选取所有密码框
$(':password').css('background', '#f9f9f9');

// 选取所有复选框
$(':checkbox').prop('checked', true);

// 选取所有按钮
$(':button').click(function() {
    alert('按钮被点击');
});

// 选取所有已选中的选项
var selectedValues = $(':selected').map(function() {
    return $(this).val();
}).get();

// 获取表单中所有有值的输入项
var filledInputs = $('#loginForm :input').filter(function() {
    return $(this).val() !== '';
});
```

## 可见性过滤选择器

可见性过滤选择器可以根据元素的可见状态来筛选元素，这在表单验证、动态显示隐藏元素等场景中非常有用。`:visible`选择器选取所有可见的元素，这些元素的CSS display属性不是none，visibility属性不是hidden，opacity属性不是0，并且有非零的宽高。`:hidden`选择器选取所有隐藏的元素，包括通过CSS隐藏的元素和type为hidden的表单元素。理解这两种选择器的行为对于正确操作页面元素的显示和隐藏非常重要。

```html [index.html]
<div class="visible-box">可见的盒子</div>
<div class="hidden-box" style="display: none;">通过display隐藏</div>
<div class="hidden-box" style="visibility: hidden;">通过visibility隐藏</div>
<div class="hidden-box" style="opacity: 0;">通过opacity隐藏</div>
<input type="hidden" value="隐藏域的值">
```

```javascript [script.js]
// 选取所有可见元素
$('.visible-box:visible').css('border', '2px solid green');

// 选取所有隐藏元素并显示
$('.hidden-box:hidden').show();

// 隐藏元素显示后再隐藏
$('.hidden-box:visible').hide();

// 针对隐藏域的特殊处理
var hiddenValue = $('input:hidden').val();

// 判断元素是否可见
if ($('.myElement').is(':visible')) {
    console.log('元素是可见的');
} else {
    console.log('元素是隐藏的');
}
```

## 选择器性能优化

在使用jQuery选择器时，性能是一个不可忽视的因素。虽然现代浏览器的选择器执行速度已经很快，但在处理大量元素或频繁执行的情况下，选择器的效率仍然会影响页面的整体性能。ID选择器是最快的选择器类型，因为它直接调用浏览器的`document.getElementById()`方法。标签选择器和类选择器也比较高效，但比ID选择器慢一些。最慢的是复合选择器和复杂的层级选择器，因为它们需要更多的计算来确定匹配关系。为了优化选择器性能，应该尽量使用ID选择器作为起点，避免使用通配符选择器，将复杂选择器拆分为多个简单选择器，以及利用jQuery的链式调用来缓存jQuery对象。

```javascript [script.js]
// 不推荐：使用通配符选择器
$('*').css('margin', '0');

// 推荐：使用ID作为起点
$('#container').find('div');

// 推荐：缓存jQuery对象
var $container = $('#container');
var $divs = $container.find('div');
var $firstDiv = $divs.first();

// 推荐：使用find()代替嵌套选择器
// 不推荐
$('#container div.myClass');
// 推荐
$('#container').find('div.myClass');

// 推荐：使用原生方法获取DOM对象再转为jQuery对象
var nativeElement = document.getElementById('myDiv');
var $jqueryElement = $(nativeElement);
```

::: tip
在处理大量DOM元素时，缓存jQuery对象是一个重要的性能优化手段。每次调用选择器都会创建新的jQuery对象，如果在一个循环中反复使用相同的选择器，会造成不必要的性能开销。将选择器结果存储在变量中，可以避免重复查询DOM。
:::
