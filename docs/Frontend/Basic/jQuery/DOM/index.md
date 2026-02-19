# jQuery DOM操作

DOM操作是jQuery最核心的功能之一，它提供了丰富的API来对HTML文档进行遍历、修改属性、插入删除内容等操作。通过jQuery的DOM操作方法，可以轻松地实现对网页内容、样式和结构的动态修改。与原生JavaScript相比，jQuery的DOM操作API更加简洁易用，同时具有良好的跨浏览器兼容性。jQuery的DOM操作可以分为几个主要类别：属性操作、内容操作、样式操作、尺寸位置操作以及节点操作等，每种类别都包含了多个实用的方法，可以满足各种DOM操作需求。

## 属性操作

属性操作主要涉及对HTML元素的属性进行获取、设置和删除。jQuery提供了attr()、prop()和data()等方法来处理不同类型的属性。attr()方法用于处理HTML属性，可以获取或设置元素的任何属性值。prop()方法用于处理DOM属性，特别适合处理布尔类型的属性如checked、disabled、selected等。data()方法用于存取HTML5的data-*自定义数据属性，它会将数据存储在jQuery对象内部，不会实际修改DOM元素的data属性。这三个方法各有适用场景，正确选择使用可以提高代码的可读性和维护性。

```html [index.html]
<a href="https://example.com" id="link" data-user="admin" title="链接标题">访问网站</a>
<input type="checkbox" id="agree" checked disabled>
<img src="image.jpg" alt="示例图片" id="myImage">
```

```javascript [script.js]
// 获取属性值
var href = $('#link').attr('href');
var title = $('#link').attr('title');
console.log('链接地址:', href);
console.log('链接标题:', title);

// 设置属性值
$('#link').attr('href', 'https://newsite.com');
$('#link').attr('target', '_blank');

// 批量设置属性
$('#link').attr({
    href: 'https://example.org',
    title: '新的链接标题',
    rel: 'external'
});

// 使用prop处理布尔属性
var isChecked = $('#agree').prop('checked');
var isDisabled = $('#agree').prop('disabled');
console.log('是否选中:', isChecked);
console.log('是否禁用:', isDisabled);

// 设置布尔属性
$('#agree').prop('checked', true);
$('#agree').prop('disabled', false);

// 使用data方法存取数据
var userData = $('#link').data('user');
console.log('用户数据:', userData);

$('#link').data('role', 'admin');
$('#link').data({
    permissions: ['read', 'write'],
    level: 10
});

// 移除属性
$('#link').removeAttr('target');
$('#agree').removeProp('disabled');
```

::: tip
对于布尔属性（checked、disabled、selected等），应该使用prop()方法来获取和设置，因为HTML属性和DOM属性在这些属性上的表现可能不一致。attr()方法获取的是初始的HTML属性值，而prop()方法获取的是当前的DOM状态。
:::

## 内容操作

内容操作包括对元素内部HTML内容、文本内容和值的获取与设置。html()方法相当于原生JavaScript的innerHTML属性，可以获取或设置元素的HTML内容。text()方法相当于原生JavaScript的textContent属性，可以获取或设置元素的纯文本内容，会自动转义HTML标签。val()方法专门用于获取或设置表单元素的值，包括input、select和textarea等。这些方法在不传入参数时用于获取内容，在传入参数时用于设置内容。

```html [index.html]
<div id="content">
    <p>这是一个<strong>段落</strong>，包含<em>HTML</em>内容。</p>
</div>
<input type="text" id="username" value="默认用户">
<select id="city">
    <option value="bj">北京</option>
    <option value="sh" selected>上海</option>
    <option value="gz">广州</option>
</select>
<textarea id="description"></textarea>
```

```javascript [script.js]
// 获取HTML内容
var html = $('#content').html();
console.log('HTML内容:', html);

// 设置HTML内容
$('#content').html('<p>新的<strong>HTML</strong>内容</p>');

// 获取文本内容（自动去除HTML标签）
var text = $('#content').text();
console.log('文本内容:', text);

// 设置文本内容（HTML标签会被转义）
$('#content').text('<p>这是纯文本，不会被解析为HTML</p>');

// 获取表单值
var username = $('#username').val();
var city = $('#city').val();
console.log('用户名:', username);
console.log('城市:', city);

// 设置表单值
$('#username').val('新用户名');
$('#description').val('多行文本内容');

// 获取多个表单值
var formData = $('#myForm :input').map(function() {
    return {
        name: $(this).attr('name'),
        value: $(this).val()
    };
}).get();

// 清空表单值
$('#myForm :input').val('');
```

## 样式操作

样式操作主要通过css()方法来实现，它可以获取或设置元素的CSS样式。jQuery的css()方法可以同时处理单个或多个样式属性的读写，使用起来比原生JavaScript的style属性方便得多。除了直接操作CSS属性外，jQuery还提供了addClass()、removeClass()、toggleClass()和hasClass()方法来操作元素的class属性，这在实现样式切换时非常有用。通过class来管理样式可以实现样式与行为的分离，使代码更加模块化。

```html [index.html]
<div id="box" class="box basic">样式操作示例</div>
<button id="addBtn">添加样式</button>
<button id="removeBtn">移除样式</button>
<button id="toggleBtn">切换样式</button>
```

```javascript [script.js]
// 获取单个CSS属性值
var color = $('#box').css('color');
var fontSize = $('#box').css('font-size');
console.log('颜色:', color);
console.log('字体大小:', fontSize);

// 获取多个CSS属性值
var styles = $('#box').css(['color', 'font-size', 'background']);
console.log('所有样式:', styles);

// 设置单个CSS属性
$('#box').css('color', 'red');
$('#box').css('background-color', '#f0f0f0');

// 设置多个CSS属性
$('#box').css({
    'color': 'blue',
    'font-size': '18px',
    'border': '2px solid #333',
    'padding': '10px'
});

// 使用数值+单位的方式设置
$('#box').css('width', 300);
$('#box').css('height', function(index, currentValue) {
    return parseInt(currentValue) + 50;
});

// 类操作方法
// 添加类
$('#addBtn').click(function() {
    $('#box').addClass('highlight');
});

// 移除类
$('#removeBtn').click(function() {
    $('#box').removeClass('basic');
});

// 切换类（存在则移除，不存在则添加）
$('#toggleBtn').click(function() {
    $('#box').toggleClass('active');
});

// 切换类（带状态参数）
$('#toggleBtn').click(function() {
    $('#box').toggleClass('active', $(this).prop('checked'));
});

// 判断是否包含某个类
if ($('#box').hasClass('highlight')) {
    console.log('包含highlight类');
}

// 切换类回调函数
$('#box').toggleClass(function(index, className) {
    return 'class-' + (index % 2 === 0 ? 'even' : 'odd');
});
```

::: danger
使用css()方法直接设置样式会导致样式代码散落在JavaScript中，不利于维护和复用。对于复杂的样式，建议使用class来管理，通过addClass()和removeClass()方法来切换样式。
:::

## 尺寸与位置操作

jQuery提供了丰富的方法来获取和设置元素的尺寸和位置信息。width()和height()方法用于获取或设置元素的内容区域的宽高。innerWidth()和innerHeight()方法获取的是包含内边距但不含边框的尺寸。outerWidth()和outerHeight()方法获取的是包含内边距和边框的尺寸，如果传入true参数还会包含外边距。offset()方法用于获取或设置元素相对于文档的位置。position()方法用于获取元素相对于其定位祖先元素的位置。scrollTop()和scrollLeft()方法用于获取或设置元素的滚动位置。这些方法在开发拖拽功能、滚动效果和定位布局时非常有用。

```html [index.html]
<div id="container">
    <div id="box">尺寸与位置示例</div>
</div>
<div id="info"></div>
<button id="getInfo">获取信息</button>
<button id="setSize">设置尺寸</button>
```

```javascript [script.js]
// 获取元素尺寸
var width = $('#box').width();          // 内容区域宽度
var height = $('#box').height();        // 内容区域高度
var innerW = $('#box').innerWidth();    // 内边距内宽度
var innerH = $('#box').innerHeight();   // 内边距内高度
var outerW = $('#box').outerWidth();    // 边框外宽度
var outerH = $('#box').outerHeight();   // 边框外高度
var outerWMargin = $('#box').outerWidth(true); // 含外边距

// 设置元素尺寸
$('#box').width(200);
$('#box').height(150);

// 获取相对于文档的位置
var offset = $('#box').offset();
console.log('相对于文档:', offset.left, offset.top);

// 设置相对于文档的位置
$('#box').offset({
    top: 100,
    left: 50
});

// 获取相对于定位祖先元素的位置
var position = $('#box').position();
console.log('相对于定位祖先:', position.left, position.top);

// 获取滚动位置
var scrollTop = $(window).scrollTop();
var scrollLeft = $(window).scrollLeft();

// 设置滚动位置
$(window).scrollTop(0);
$(window).scrollLeft(0);

// 动画中使用位置
$('#box').animate({
    left: '+=50',
    top: '+=20'
}, 500);

// 显示尺寸信息
$('#getInfo').click(function() {
    var info = $('#info');
    info.html(
        '宽度: ' + $('#box').width() + 'px<br>' +
        '高度: ' + $('#box').height() + 'px<br>' +
        '相对文档左: ' + $('#box').offset().left + 'px<br>' +
        '相对文档顶: ' + $('#box').offset().top + 'px'
    );
});
```

## 节点操作

节点操作是jQuery DOM操作中最灵活的部分，它允许动态地创建、插入、复制和删除DOM元素。创建新元素只需将HTML字符串传递给jQuery函数。插入元素可以使用append()、prepend()、before()、after()等方法，它们之间的区别在于插入的位置不同。删除元素可以使用remove()、detach()或empty()方法，它们之间的区别在于是否保留事件和数据。复制元素可以使用clone()方法，可以选择是否复制元素附带的事件处理器。

```html [index.html]
<ul id="list">
    <li>列表项1</li>
    <li>列表项2</li>
</ul>
<div id="container">
    <p>容器内的段落</p>
</div>
<button id="addFirst">添加到开头</button>
<button id="addLast">添加到最后</button>
<button id="addBefore">添加到此元素前</button>
<button id="addAfter">添加到此元素后</button>
```

```javascript [script.js]
// 创建新元素
var newDiv = $('<div>', {
    class: 'new-item',
    text: '新创建的div',
    click: function() {
        alert('点击了新div');
    }
});

var newLi = $('<li>').text('新列表项').addClass('highlight');

// 插入到元素的子元素末尾（append）
$('#list').append(newLi);
$('#list').append('<li>通过HTML字符串添加</li>');

// 插入到元素的子元素开头（prepend）
$('#list').prepend('<li>插入到开头的项</li>');

// 插入到此元素之前（before）
$('#container').before('<div>插入到container之前</div>');

// 插入到此元素之后（after）
$('#container').after('<div>插入到container之后</div>');

// 移动已有元素
$('#list li:first').appendTo('#list');           // 移动到子元素末尾
$('#list li:last').prependTo('#list');          // 移动到子元素开头
$('#container').insertBefore('#list');          // 移动到list之前
$('#container').insertAfter('#list');           // 移动到list之后

// 删除元素
$('#list li').click(function() {
    $(this).remove();      // 删除并移除事件
    // $(this).detach();   // 删除但保留事件（可重新插入）
    // $('#list').empty(); // 清空内部所有内容
});

// 复制元素
var clonedList = $('#list').clone();            // 浅复制（不复制事件）
var clonedWithEvents = $('#list').clone(true);   // 深复制（复制事件）

// 替换元素
$('#container p').replaceWith('<div>段落被替换了</div>');
$('<div>新内容</div>').replaceAll('#container p');

// 包裹元素
$('p').wrap('<div class="wrapper"></div>');           // 每个p单独包裹
$('p').wrapAll('<div class="wrapper"></div>');        // 所有p一起包裹
$('p').wrapInner('<span class="inner"></span>');      // 包裹内部内容
$('p').unwrap();                                      // 移除父级包裹
```

```javascript [script.js]
// 链式操作示例
$('#list')
    .append('<li>第一项</li>')
    .append('<li>第二项</li>')
    .find('li:first')
    .addClass('first-item')
    .end()
    .find('li:last')
    .addClass('last-item');

// 查找父级和兄弟元素
var $item = $('#list li:first');
var parent = $item.parent();           // 直接父元素
var parents = $item.parents('div');   // 所有父级div元素
var siblings = $item.siblings();      // 所有兄弟元素
var prev = $item.prev();              // 前一个兄弟
var next = $item.next();              // 后一个兄弟
var children = $item.children();      // 所有子元素

// 查找子元素和后代元素
var directChildren = $('#list').children();  // 直接子元素
var allDescendants = $('#list').find('li'); // 所有li后代元素
```

::: tip
在大量DOM操作场景下，使用文档片段（DocumentFragment）可以减少重排次数，提高性能。先将元素添加到片段中，最后将片段添加到DOM中，这样只会触发一次页面重排。
:::
