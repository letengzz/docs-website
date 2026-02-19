# jQuery 工具函数

jQuery不仅提供了强大的DOM操作和事件处理功能，还包含了一套丰富的工具函数，这些函数封装了JavaScript开发中常见的实用功能。通过jQuery的工具函数，可以简化数组和对象的操作、字符串处理、类型判断、数据存储等日常工作。这些工具函数位于jQuery命名空间下，可以通过$.xxx的形式直接调用，无需选择任何元素。jQuery工具函数的命名遵循清晰直观的原则，易于理解和使用。掌握这些工具函数可以大大提高开发效率，减少重复代码的编写。这些函数经过多年的优化和测试，在各种浏览器环境下都能稳定运行，是jQuery不可分割的重要组成部分。

## 浏览器与功能检测

jQuery提供了多种浏览器检测和功能检测工具函数，这些函数可以帮助开发者针对不同的浏览器环境编写兼容性代码。$.browser属性可以检测当前浏览器的类型和版本，但它在jQuery 1.9版本后已被标记为移除，推荐使用特性检测来替代浏览器检测。$.support对象包含了一系列布尔值属性，用于检测浏览器是否支持特定的CSS特性或DOM功能。通过这些检测函数，可以在代码中针对不同的浏览器环境执行不同的逻辑，确保网页在各种浏览器中都能正常工作。虽然现代Web开发越来越强调使用特性检测而非浏览器检测，但在某些遗留项目中，浏览器检测仍然有其存在的价值。

```javascript [script.js]
// 浏览器检测（已弃用，但在旧项目中使用）
console.log('浏览器类型:', $.browser.mozilla);
console.log('浏览器版本:', $.browser.version);
console.log('是否为Webkit浏览器:', $.browser.webkit);
console.log('是否为IE浏览器:', $.browser.msie);
console.log('是否为Opera浏览器:', $.browser.opera);

// 检测特定版本的IE
if ($.browser.msie && $.browser.version === '8.0') {
    console.log('正在使用IE8浏览器');
    // 针对IE8的特殊处理
}

// 特性检测（推荐方式）
console.log('支持ajax:', $.support.ajax);
console.log('支持box-sizing:', $.support.boxModel);
console.log('支持opacity:', $.support.opacity);
console.log('支持hrefNormalized:', $.support.hrefNormalized);
console.log('支持submitBubbles:', $.support.submitBubbles);
console.log('支持changeBubbles:', $.support.changeBubbles);

// 检测事件委托支持
if ($.support.submitBubbles) {
    console.log('支持表单提交事件冒泡');
}

// 检测DOM操作支持
if ($.support.appendChecked) {
    console.log('支持appendChecked方法');
}

// 自定义特性检测函数
function supportTest(feature) {
    return $.support[feature] !== undefined;
}

console.log('检测opacity特性:', supportTest('opacity'));
console.log('检测ajax特性:', supportTest('ajax'));

// 检测CSS3特性
var cssTests = {
    'border-radius': function() {
        return 'borderRadius' in document.documentElement.style;
    },
    'transform': function() {
        return 'transform' in document.documentElement.style;
    },
    'transition': function() {
        return 'transition' in document.documentElement.style;
    }
};

for (var feature in cssTests) {
    if (cssTests.hasOwnProperty(feature)) {
        console.log(feature + ':', cssTests[feature]());
    }
}

// 检测移动设备
var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
console.log('是否为移动设备:', isMobile);

// 检测触摸设备
var isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
console.log('是否为触摸设备:', isTouch);
```

::: tip
在现代Web开发中，推荐使用特性检测（feature detection）而非浏览器检测（browser detection）。因为浏览器的版本号并不能完全反映其实际支持的功能，而特性检测可以直接测试浏览器是否支持特定的功能，这种方法更加可靠和准确。
:::

## 数组与对象操作

jQuery提供了丰富的数组和对象操作工具函数，这些函数可以大大简化JavaScript开发中常见的数据处理任务。$.each()函数可以遍历数组或对象，对每个元素执行指定的回调函数。$.map()函数可以创建一个新数组，新数组的元素是对原数组元素应用回调函数后的返回值。$.extend()函数用于合并对象，可以将多个对象的属性合并到一个目标对象中。$.grep()函数用于过滤数组，返回满足条件的元素。$.makeArray()函数可以将类数组对象转换为真正的数组。$.merge()函数可以合并两个数组。这些函数在处理数据时非常实用，掌握它们可以提高代码的可读性和开发效率。

```javascript [script.js]
// $.each()遍历数组
var colors = ['red', 'green', 'blue'];
$.each(colors, function(index, value) {
    console.log('索引:', index, '值:', value);
});

// $.each()遍历对象
var user = { name: '张三', age: 25, city: '北京' };
$.each(user, function(key, value) {
    console.log('键:', key, '值:', value);
});

// $.map()创建新数组
var numbers = [1, 2, 3, 4, 5];
var doubled = $.map(numbers, function(value) {
    return value * 2;
});
console.log('翻倍数组:', doubled); // [2, 4, 6, 8, 10]

// $.map()过滤和转换
var strings = ['10', '20', 'abc', '30'];
var ints = $.map(strings, function(value) {
    var num = parseInt(value);
    return isNaN(num) ? null : num;
});
console.log('转换结果:', ints); // [10, 20, 30]

// $.extend()合并对象
var obj1 = { a: 1, b: 2 };
var obj2 = { b: 3, c: 4 };
var merged = $.extend({}, obj1, obj2);
console.log('合并结果:', merged); // { a: 1, b: 3, c: 4 }

// 深拷贝（jQuery 1.x的深拷贝实现）
var obj1 = { person: { name: '张三' } };
var obj2 = { person: { name: '李四' } };
var deepMerged = $.extend(true, {}, obj1, obj2);
console.log('深拷贝合并:', deepMerged);
deepMerged.person.name = '王五';
console.log('修改后obj1:', obj1.person.name); // 张三（未被修改）

// $.grep()过滤数组
var numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
var evenNumbers = $.grep(numbers, function(value) {
    return value % 2 === 0;
});
console.log('偶数:', evenNumbers); // [2, 4, 6, 8, 10]

// $.grep()带索引参数
var filtered = $.grep(numbers, function(value, index) {
    return value > index;
});
console.log('值大于索引:', filtered);

// $.makeArray()类数组转数组
var nodeList = document.querySelectorAll('div');
var array = $.makeArray(nodeList);
console.log('是否为数组:', Array.isArray(array));

// $.merge()合并数组
var arr1 = [1, 2, 3];
var arr2 = [4, 5, 6];
var merged = $.merge($.makeArray(arr1), $.makeArray(arr2));
console.log('合并数组:', merged); // [1, 2, 3, 4, 5, 6]

// $.unique()去除重复元素（用于DOM元素数组）
var elements = [div1, div2, div1, div3, div2];
var uniqueElements = $.unique(elements);
console.log('去重后的DOM元素');

// $.inArray()查找元素位置
var fruits = ['apple', 'banana', 'orange'];
var index = $.inArray('banana', fruits);
console.log('banana的索引:', index); // 1
var notFound = $.inArray('grape', fruits);
console.log('grape的索引:', notFound); // -1

// 遍历Collection
$('div').each(function(index, element) {
    console.log('索引:', index, '元素:', element.tagName);
});
```

::: danger
$.extend()的深拷贝在jQuery 1.x版本中实现并不完美，存在循环引用和特殊对象（如Date、RegExp、Function）处理不当的问题。在处理复杂的数据结构时，建议使用专门的深拷贝库或JSON.parse(JSON.stringify())方法进行深拷贝。
:::

## 字符串操作

jQuery虽然主要专注于DOM操作，但也提供了一些实用的字符串处理函数。$.trim()函数用于去除字符串两端的空白字符，这是JavaScript开发中非常常用的操作。$.escapeSelector()函数（在jQuery 3.0+中可用）用于转义CSS选择器中的特殊字符，确保选择器的正确性。这些字符串函数虽然简单，但在实际开发中使用频率很高。JavaScript原生也提供了丰富的字符串方法，但在处理用户输入或外部数据时，使用$.trim()进行前后空格去除是一个很好的习惯。

```javascript [script.js]
// $.trim()去除两端空白
var str1 = '   hello world   ';
var trimmed = $.trim(str1);
console.log('原字符串:', '"' + str1 + '"');
console.log('去除空白后:', '"' + trimmed + '"'); // "hello world"

// $.trim()处理各种空白字符
var str2 = ' \t\n\r hello \t\n\r ';
console.log('处理后的字符串:', '"' + $.trim(str2) + '"');

// $.trim()在表单验证中的使用
$('#submitBtn').click(function() {
    var input = $('#username').val();
    if ($.trim(input) === '') {
        alert('用户名不能为空');
        return false;
    }
    // 去除用户输入的两端空格后再处理
    var cleanInput = $.trim(input);
});

// $.escapeSelector()转义选择器（jQuery 3.0+）
var specialId = 'my.id[with-special-chars]';
// 直接使用会出错
try {
    $('#' + specialId);
} catch (e) {
    console.log('直接选择器会出错');
}

// 使用转义
var escaped = $.escapeSelector(specialId);
var $element = $('#' + escaped);
console.log('成功选择元素:', $element.length > 0);

// 动态构建选择器时转义
function escapeSelector(selector) {
    if (typeof $.escapeSelector === 'function') {
        return $.escapeSelector(selector);
    }
    // jQuery 3.0以下的兼容写法
    return selector.replace(/([!"#$%&'()*+,./:;<=>?@[\\\]^`{|}~])/g, '\\$1');
}

var userInput = '<script>alert("xss")</script>';
// 需要先转义HTML实体，再作为选择器
var safeSelector = escapeSelector(userInput.replace(/&/g, '&amp;')
                                            .replace(/</g, '&lt;')
                                            .replace(/>/g, '&gt;'));

// 字符串模板替换
function template(str, data) {
    return str.replace(/\{\{(\w+)\}\}/g, function(match, key) {
        return data[key] !== undefined ? data[key] : match;
    });
}

var tmpl = 'Hello, {{name}}! You have {{count}} messages.';
var result = template(tmpl, { name: '张三', count: 5 });
console.log('模板替换结果:', result); // Hello, 张三! You have 5 messages.

// 字符串截取和填充
function padLeft(str, length, char) {
    str = String(str);
    while (str.length < length) {
        str = char + str;
    }
    return str;
}

console.log('左侧填充:', padLeft('5', 3, '0')); // "005"
```

## 类型检测

jQuery提供了多种类型检测工具函数，这些函数可以帮助开发者准确判断变量的类型。$.type()函数是jQuery提供的核心类型检测函数，它可以返回变量的具体类型名称，如string、number、boolean、array、object、function、null、undefined等。$.isFunction()函数专门用于检测变量是否为函数。$.isArray()函数用于检测变量是否为数组。$.isEmptyObject()函数用于检测对象是否为空。$.isPlainObject()函数用于检测变量是否为纯粹的对象（通过{}或new Object()创建的对象）。$.isNumeric()函数用于检测变量是否为数字或可转换为数字的字符串。这些类型检测函数在编写健壮的代码时非常重要，可以帮助避免因类型不匹配导致的错误。

```javascript [script.js]
// $.type()类型检测
console.log($.type('hello'));        // string
console.log($.type(123));            // number
console.log($.type(true));            // boolean
console.log($.type(null));            // null
console.log($.type(undefined));       // undefined
console.log($.type({}));             // object
console.log($.type([]));             // array
console.log($.type(function(){}));    // function
console.log($.type(new Date()));      // date
console.log($.type(/regex/));        // regexp

// $.isFunction()检测函数
var myFunc = function() {};
console.log('是否为函数:', $.isFunction(myFunc));      // true
console.log('字符串是否为函数:', $.isFunction('func')); // false

// 使用$.isFunction检测回调
$('#btn').click(function() {
    console.log('点击事件已绑定');
});

var callbacks = $.Callbacks();
if ($.isFunction(callbacks.fire)) {
    console.log('Callbacks的fire是函数');
}

// $.isArray()检测数组
var arr = [1, 2, 3];
var obj = { 0: 1, 1: 2 };
console.log('是否为数组:', $.isArray(arr)); // true
console.log('对象是否为数组:', $.isArray(obj)); // false

// 替代方案：Array.isArray()
console.log('Array.isArray结果:', Array.isArray(arr));

// $.isEmptyObject()检测空对象
var emptyObj = {};
var nonEmptyObj = { name: '张三' };
console.log('空对象:', $.isEmptyObject(emptyObj));       // true
console.log('非空对象:', $.isEmptyObject(nonEmptyObj)); // false

// 检测对象是否为空（包含原型链属性）
function isEmptyObject(obj) {
    for (var name in obj) {
        if (obj.hasOwnProperty(name)) {
            return false;
        }
        // 如果需要检查原型链，去掉hasOwnProperty判断
    }
    return true;
}

// $.isPlainObject()检测纯粹对象
var plainObj = {};
var plainObj2 = new Object();
var notPlainObj = new Date();
var notPlainObj2 = new MyClass();

console.log('{}是否为纯粹对象:', $.isPlainObject({}));           // true
console.log('new Object()是否为纯粹对象:', $.isPlainObject(new Object())); // true
console.log('Date对象是否为纯粹对象:', $.isPlainObject(new Date())); // false
console.log('自定义对象是否为纯粹对象:', $.isPlainObject(notPlainObj2)); // false

// $.isNumeric()检测数值（jQuery 1.7+）
console.log('数字:', $.isNumeric(123));           // true
console.log('数字字符串:', $.isNumeric('123'));  // true
console.log('浮点数:', $.isNumeric(3.14));       // true
console.log('十六进制:', $.isNumeric(0xFF));     // true
console.log('科学计数法:', $.isNumeric(1e10));   // true
console.log('空字符串:', $.isNumeric(''));       // false
console.log('普通字符串:', $.isNumeric('abc'));  // false

// 综合类型检测示例
function processData(data) {
    if ($.isArray(data)) {
        console.log('处理数组，共', data.length, '个元素');
        $.each(data, function(index, item) {
            processData(item);
        });
    } else if ($.isPlainObject(data)) {
        console.log('处理对象');
        $.each(data, function(key, value) {
            console.log('属性:', key, '值:', value);
        });
    } else if ($.isFunction(data)) {
        console.log('执行函数');
        data();
    } else {
        console.log('其他数据类型:', $.type(data));
    }
}
```

## 数据存储

jQuery提供了$.data()和$.removeData()方法来在DOM元素上存储和读取数据。这种数据存储机制与HTML5的data-*属性不同，$.data()方法将数据存储在jQuery对象内部，不会实际修改DOM元素的属性。$.data()方法支持存储任何JavaScript数据类型，包括对象、数组、函数等。使用$.data()进行数据存储可以避免使用全局变量，减少命名空间污染，同时数据的生命周期与DOM元素的生命周期绑定，DOM元素被移除时数据也会被自动清理。这在事件处理程序中传递数据、缓存DOM查询结果等场景中非常有用。

```javascript [script.js]
// 在元素上存储数据
$('#myElement').data('name', '张三');
$('#myElement').data('age', 25);
$('#myElement').data('user', { id: 1, city: '北京' });

// 读取存储的数据
var name = $('#myElement').data('name');
console.log('姓名:', name);

var user = $('#myElement').data('user');
console.log('用户对象:', user);
console.log('用户城市:', user.city);

// 存储数组
$('#myElement').data('tags', ['javascript', 'jquery', 'html']);
var tags = $('#myElement').data('tags');
console.log('标签:', tags[0], tags[1]);

// 存储函数
$('#myElement').data('handler', function() {
    console.log('存储的函数被调用');
});
$('#myElement').data('handler')(); // 调用存储的函数

// 使用$.fn.data()在jQuery原型上添加方法
(function($) {
    $.fn.myPlugin = function(options) {
        // 为每个匹配元素存储配置
        return this.each(function() {
            var $this = $(this);
            var settings = $.extend({}, $.fn.myPlugin.defaults, options);
            $this.data('pluginSettings', settings);
        });
    };
    
    $.fn.myPlugin.defaults = {
        color: 'blue',
        size: 'medium'
    };
    
    $.fn.myPlugin.getSettings = function(element) {
        return $(element).data('pluginSettings');
    };
})($);

// 移除数据
$('#myElement').removeData('name'); // 移除指定数据
$('#myElement').removeData();       // 移除所有数据

// 检查数据是否存在
var hasName = $('#myElement').data('name') !== undefined;
console.log('是否存在name数据:', hasName);

// 事件处理中传递数据
$('#btn').on('click', { userId: 123 }, function(event) {
    console.log('用户ID:', event.data.userId);
    // 通过event.data获取传递的数据
});

// 缓存DOM查询结果
(function($) {
    $.fn.cachedFind = function(selector) {
        var $element = this;
        var cacheKey = 'cached_' + selector;
        var $cached = $element.data(cacheKey);
        
        if (!$cached) {
            $cached = $element.find(selector);
            $element.data(cacheKey, $cached);
        }
        
        return $cached;
    };
})($);

// 使用缓存查找
var $container = $('#container');
var $buttons = $container.cachedFind('.btn');
var $inputs = $container.cachedFind('input');

// 使用数据存储管理组件状态
var $tabContainer = $('#tabs');
$tabContainer.data('activeTab', 0);

$('.tab').click(function() {
    var index = $(this).index();
    $tabContainer.data('activeTab', index);
    console.log('切换到标签页:', index);
});
```

::: tip
使用$.data()方法存储数据时，数据是存储在jQuery对象内部的JavaScript对象中，而不是存储在DOM元素的属性上。这意味着即使元素的HTML属性发生变化，通过$.data()存储的数据也不会受到影响。但是，当元素从DOM树中移除时，jQuery会自动清理与其关联的数据。
:::

## 其他常用工具

除了上述的工具函数外，jQuery还提供了许多其他实用的工具函数。$.noop()函数返回一个空函数，在需要回调函数但不需要执行任何操作时非常有用。$.now()函数返回当前时间的毫秒数戳，是一个简单的时间获取方法。$.param()函数可以将对象序列化为URL查询字符串格式，用于AJAX请求的数据编码。$.parseJSON()函数用于解析JSON字符串为JavaScript对象（在jQuery 3.0+中已不推荐使用，推荐使用原生JSON.parse()）。$.parseHTML()函数用于将HTML字符串解析为DOM节点数组。这些工具函数覆盖了Web开发的各个方面，合理使用可以大大提高开发效率。

```javascript [script.js]
// $.noop()空函数
var noop = $.noop;
console.log('空函数:', noop);

// 回调函数不存在时使用空函数
function myCallback(callback) {
    callback = callback || $.noop;
    callback();
}

// $.now()获取当前时间戳
var timestamp = $.now();
console.log('当前时间戳:', timestamp);
console.log('格式化时间:', new Date(timestamp).toLocaleString());

// 性能测试
var start = $.now();
// 执行代码
for (var i = 0; i < 100000; i++) {}
var end = $.now();
console.log('执行时间:', (end - start), '毫秒');

// $.param()序列化对象为查询字符串
var params = { page: 1, limit: 10, category: 'tech' };
var queryString = $.param(params);
console.log('查询字符串:', queryString); // page=1&limit=10&category=tech

// 深层对象序列化
var deepParams = {
    user: { name: '张三', age: 25 },
    hobbies: ['reading', 'gaming']
};
var deepString = $.param(deepParams);
console.log('深层序列化:', deepString);
// user%5Bname%5D=%E5%BC%A0%E4%B8%89&user%5Bage%5D=25&hobbies%5B%5D=reading&hobbies%5B%5D=gaming

// 使用traditional参数禁用深层序列化
var simpleString = $.param(deepParams, true);
console.log('简单序列化:', simpleString); // user=%5Bobject%20Object%5D&hobbies=reading%2Cgaming

// AJAX请求中使用$.param()
$.ajax({
    url: '/api/search',
    method: 'GET',
    data: $.param({ q: 'javascript', type: 'tutorial' }),
    success: function(data) {
        console.log('搜索结果:', data);
    }
});

// $.parseJSON()解析JSON（jQuery 3.0+推荐使用JSON.parse）
try {
    var jsonStr = '{"name": "张三", "age": 25}';
    var obj = $.parseJSON(jsonStr);
    console.log('解析结果:', obj);
} catch (e) {
    console.log('JSON解析错误:', e.message);
}

// $.parseHTML()解析HTML字符串
var htmlStr = '<div><p>段落1</p><p>段落2</p></div>';
var nodes = $.parseHTML(htmlStr);
console.log('解析后的节点数:', nodes.length);
console.log('第一个节点:', nodes[0]);

// 将解析的节点添加到DOM
var $container = $('#container');
$.each(nodes, function(index, node) {
    $container.append(node);
});

// 安全解析HTML（防止XSS）
function safeParseHTML(html) {
    // 只解析body内的内容，过滤危险标签
    var safeHtml = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    return $.parseHTML(safeHtml);
}

// $.contains()检测元素包含关系
var parent = document.getElementById('container');
var child = document.getElementById('child');
console.log('container包含child:', $.contains(parent, child));

// $.globalEval()在全局作用域执行代码
$.globalEval('var globalVar = "我是全局变量";');
console.log('全局变量:', window.globalVar);

// $.holdReady()延迟ready事件
$.holdReady(true);
$('#loading').hide();
$.get('/api/data', function() {
    $.holdReady(false); // 数据加载完成后释放ready
});

// $.clone()复制对象
var original = { a: 1, b: { c: 2 } };
var cloned = $.extend(true, {}, original);
cloned.b.c = 3;
console.log('原对象:', original.b.c); // 2
console.log('克隆对象:', cloned.b.c); // 3

// 工具函数集合
var jQueryUtils = {
    // 检测数组是否包含元素
    inArray: function(array, value) {
        return $.inArray(value, array) !== -1;
    },
    
    // 去重
    unique: function(array) {
        return $.grep(array, function(value, index) {
            return $.inArray(value, array) === index;
        });
    },
    
    // 深拷贝
    deepClone: function(obj) {
        return $.extend(true, {}, obj);
    },
    
    // 格式化URL参数
    buildQuery: function(params) {
        return $.param(params);
    },
    
    // 解析URL参数
    parseQuery: function(url) {
        var queryString = url.split('?')[1] || '';
        var pairs = queryString.split('&');
        var result = {};
        $.each(pairs, function(index, pair) {
            var parts = pair.split('=');
            var key = decodeURIComponent(parts[0]);
            var value = decodeURIComponent(parts[1] || '');
            result[key] = value;
        });
        return result;
    }
};
```

## Callbacks对象

jQuery的Callbacks对象是一个多功能的回调函数管理工具，它提供了强大的函数列表管理功能。Callbacks对象类似于事件监听器的概念，但更加灵活和功能丰富。Callbacks对象可以添加回调函数、移除回调函数、触发回调函数，并支持多种调用模式，如once（只执行一次）、memory（记忆模式）、unique（唯一）、stopOnFalse（遇到返回false时停止）等。通过合理配置Callbacks对象的标志位，可以实现各种复杂的事件管理需求。Callbacks对象在jQuery内部被用于$.Deferred()的实现，也可以直接在开发中使用。

```javascript [script.js]
// 创建Callbacks对象
var callbacks = $.Callbacks();

// 添加回调函数
function fn1(value) {
    console.log('fn1:', value);
}

function fn2(value) {
    console.log('fn2:', value);
}

callbacks.add(fn1);
callbacks.add(fn2);

// 触发回调
callbacks.fire('hello'); // 会输出fn1: hello 和 fn2: hello

// 移除回调函数
callbacks.remove(fn1);
callbacks.fire('world'); // 只输出fn2: world

// 不同的Callbacks标志
var callbacksOnce = $.Callbacks('once');
var callbacksMemory = $.Callbacks('memory');
var callbacksUnique = $.Callbacks('unique');
var callbacksStopOnFalse = $.Callbacks('stopOnFalse');

// once标志：回调函数只执行一次
callbacksOnce.add(function() {
    console.log('这个函数只会执行一次');
});
callbacksOnce.fire();
callbacksOnce.fire(); // 第二次调用不会执行

// memory标志：记住最后的触发参数
callbacksMemory.add(function() {
    console.log('memory回调');
});
callbacksMemory.fire('第一次触发');
callbacksMemory.add(function() {
    console.log('新添加的函数立即执行，使用记忆的参数');
});
// 输出: memory回调 和 新添加的函数立即执行，使用记忆的参数

// unique标志：防止重复添加相同的回调
var fn = function() { console.log('唯一函数'); };
callbacksUnique.add(fn);
callbacksUnique.add(fn); // 不会被重复添加
console.log('回调函数数量:', callbacksUnique.has(fn)); // true

// stopOnFalse标志：遇到返回false时停止执行
function mayStop(value) {
    console.log('mayStop:', value);
    return value !== 'stop';
}

function continueFn() {
    console.log('继续执行');
}

var callbacksStop = $.Callbacks('stopOnFalse');
callbacksStop.add(mayStop);
callbacksStop.add(continueFn);

callbacksStop.fire('继续');  // 两个函数都执行
callbacksStop.fire('stop'); // 只执行mayStop，遇到false后停止

// 组合标志
var callbacksComplex = $.Callbacks('once memory unique stopOnFalse');

// empty()清空所有回调
callbacks.empty();

// has()检查回调是否存在
console.log('fn1是否存在:', callbacks.has(fn1));
```

## Deferred对象

jQuery的Deferred对象是基于Promise规范实现的异步编程工具，它提供了一种更加优雅的方式来处理异步操作。Deferred对象可以表示一个异步操作（如AJAX请求、动画、定时器等）的状态，并提供方法来注册回调函数、传递结果和处理错误。$.Deferred()函数用于创建一个新的Deferred对象。Deferred对象有三种状态：pending（进行中）、resolved（成功）和rejected（失败）。通过then()方法可以链式注册成功和失败的回调，通过done()和fail()方法分别注册成功和失败的回调，通过always()方法注册无论成功还是失败都会执行的回调。Deferred对象可以极大地简化异步代码的复杂度，使代码更加清晰和易于维护。

```javascript [script.js]
// 创建Deferred对象
var deferred = $.Deferred();

// 获取Promise对象
var promise = deferred.promise();

// 监听状态变化
deferred.done(function(value) {
    console.log('成功:', value);
});

deferred.fail(function(reason) {
    console.log('失败:', reason);
});

// 改变状态为已解决
deferred.resolve('操作成功');

// 使用$.when()处理多个异步操作
var request1 = $.ajax('/api/data1');
var request2 = $.ajax('/api/data2');

$.when(request1, request2)
    .done(function(data1, data2) {
        console.log('两个请求都成功');
        console.log('data1:', data1[0]);
        console.log('data2:', data2[0]);
    })
    .fail(function() {
        console.log('至少一个请求失败');
    });

// 创建自定义异步函数
function asyncOperation(data) {
    var deferred = $.Deferred();
    
    // 模拟异步操作
    setTimeout(function() {
        if (data.valid) {
            deferred.resolve({ result: '成功', data: data });
        } else {
            deferred.reject({ error: '数据无效', data: data });
        }
    }, 1000);
    
    return deferred.promise();
}

// 使用异步函数
asyncOperation({ valid: true })
    .done(function(result) {
        console.log('操作成功:', result);
    })
    .fail(function(error) {
        console.log('操作失败:', error);
    });

// then()方法链式调用
asyncOperation({ valid: true })
    .then(
        function(result) {
            console.log('第一步成功:', result);
            return { newData: '处理后的数据' };
        },
        function(error) {
            console.log('第一步失败:', error);
            return $.Deferred().reject(error);
        }
    )
    .then(
        function(newData) {
            console.log('第二步成功:', newData);
        },
        function(error) {
            console.log('第二步失败:', error);
        }
    );

// Promise的简洁写法
var promise = $.ajax('/api/data');
promise.then(
    function(data) {
        console.log('成功:', data);
        return data.id;
    },
    function() {
        console.log('失败');
        return $.Deferred().reject();
    }
).then(function(id) {
    console.log('下一步:', id);
});

// 等待多个Promise完成
function getUsers() {
    return $.ajax('/api/users');
}

function getPosts() {
    return $.ajax('/api/posts');
}

$.when(getUsers(), getPosts())
    .then(function(users, posts) {
        console.log('用户:', users[0]);
        console.log('文章:', posts[0]);
    });

// progress通知
var progressDeferred = $.Deferred();

progressDeferred.progress(function(value) {
    console.log('进度:', value);
});

// 模拟进度更新
setTimeout(function() {
    progressDeferred.notify(25);
}, 500);
setTimeout(function() {
    progressDeferred.notify(50);
}, 1000);
setTimeout(function() {
    progressDeferred.notify(75);
}, 1500);
setTimeout(function() {
    progressDeferred.resolve(100);
}, 2000);

// 封装带有进度的异步操作
function asyncWithProgress() {
    var deferred = $.Deferred();
    
    var progress = 0;
    var interval = setInterval(function() {
        progress += 10;
        deferred.notify(progress + '%');
        
        if (progress >= 100) {
            clearInterval(interval);
            deferred.resolve('完成');
        }
    }, 200);
    
    return deferred.promise();
}

asyncWithProgress()
    .progress(function(p) {
        console.log('当前进度:', p);
    })
    .done(function(result) {
        console.log('最终结果:', result);
    });

// 转换Promise为jQuery Deferred
function toDeferred(promise) {
    var deferred = $.Deferred();
    promise.then(
        function(value) {
            deferred.resolve(value);
        },
        function(reason) {
            deferred.reject(reason);
        }
    );
    return deferred.promise();
}
```

::: tip
jQuery Deferred对象实现的是Promise/A规范，与ES6的Promise规范有一些差异。jQuery Deferred可以使用reject()和resolve()多次调用，而ES6 Promise只能改变一次状态。在混合使用两种Promise时需要注意这些差异。
:::
