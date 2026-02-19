# jQuery 动画效果

jQuery提供了丰富的动画效果API，可以轻松实现元素的显示隐藏、淡入淡出、滑动效果以及自定义动画等。通过jQuery的动画系统，可以创建流畅平滑的视觉体验，提升用户交互体验。jQuery动画的核心是animate()方法，它可以对元素的任意CSS属性进行平滑过渡。show()、hide()和toggle()方法是最基本的显示隐藏动画。fadeIn()、fadeOut()、fadeTo()和fadeToggle()方法实现淡入淡出效果。slideDown()、slideUp()和slideToggle()方法实现滑动效果。此外，jQuery还提供了动画队列机制，可以将多个动画按顺序执行，或者并行执行动画。掌握这些动画方法，可以实现各种复杂的交互效果。

## 显示与隐藏动画

显示与隐藏动画是jQuery动画中最基础也是最常用的效果。show()方法可以将隐藏的元素以动画方式显示出来，hide()方法可以将显示的元素以动画方式隐藏，toggle()方法可以切换元素的显示状态。这些方法在不传入参数时是立即显示或隐藏，传入参数时可以指定动画的持续时间和缓动效果。默认情况下，这些动画会将元素的display属性在none和其他值之间切换，同时对宽高和透明度进行动画过渡。show()方法会恢复元素被隐藏前的display值，而hide()方法会将元素的display设置为none。

```html [index.html]
<div id="box" class="box">显示隐藏示例</div>
<button id="showBtn">显示</button>
<button id="hideBtn">隐藏</button>
<button id="toggleBtn">切换</button>
<div id="info"></div>
```

```javascript [script.js]
// 基本显示动画
$('#showBtn').click(function() {
    $('#box').show();
});

// 基本隐藏动画
$('#hideBtn').click(function() {
    $('#box').hide();
});

// 切换显示状态
$('#toggleBtn').click(function() {
    $('#box').toggle();
});

// 带时间的显示隐藏动画
// 快速显示（200毫秒）
$('#box').show(200);

// 中速显示（400毫秒）
$('#box').show(400);

// 慢速显示（600毫秒）
$('#box').show(600);

// 指定毫秒数
$('#box').show(1000);

// 带回调函数的显示动画
$('#box').show(500, function() {
    $('#info').text('显示动画完成！');
});

// 带缓动效果的动画
// jQuery默认缓动效果：swing（摇摆）和linear（线性）
$('#box').show(1000, 'linear');
$('#box').hide(1000, 'swing');

// 链式动画
$('#box').hide(500).show(500).hide(500).show(500);

// 切换显示状态并指定时间和缓动
$('#box').toggle(500, 'linear');

// 多元素显示隐藏
$('.boxes').show(300);
$('.boxes').hide(300, function() {
    // 每个元素动画完成都会调用
    console.log('元素动画完成');
});
```

::: tip
show()方法显示元素时会恢复该元素被隐藏前的display值。如果元素原本是inline元素，显示后还是inline；如果是block元素，显示后还是block。如果元素之前是通过CSS设置的display:none，则show()会将其改为block。
:::

## 淡入淡出动画

淡入淡出动画通过改变元素的透明度来实现显示和隐藏效果，这种动画方式比显示隐藏动画更加柔和。fadeIn()方法使元素从透明变为不透明，实现淡入效果。fadeOut()方法使元素从不透明变为透明，实现淡出效果。fadeTo()方法将元素透明度变化到指定值，可以实现半透明效果。fadeToggle()方法在淡入和淡出之间切换。这些方法都可以指定动画持续时间和缓动效果，fadeTo()方法还需要指定目标的透明度值（0到1之间）。淡入淡出动画只影响元素的opacity属性，不会改变元素的display属性和布局空间。

```html [index.html]
<div id="fadeBox" class="box">淡入淡出示例</div>
<button id="fadeInBtn">淡入</button>
<button id="fadeOutBtn">淡出</button>
<button id="fadeToBtn">淡到0.3</button>
<button id="fadeToggleBtn">切换淡入淡出</button>
<div class="overlay">半透明覆盖层</div>
```

```javascript [script.js]
// 淡入动画
$('#fadeInBtn').click(function() {
    $('#fadeBox').fadeIn();
});

// 淡出动画
$('#fadeOutBtn').click(function() {
    $('#fadeBox').fadeOut();
});

// 淡入到指定透明度
$('#fadeToBtn').click(function() {
    $('#fadeBox').fadeTo(500, 0.3);
});

// 切换淡入淡出
$('#fadeToggleBtn').click(function() {
    $('#fadeBox').fadeToggle();
});

// 带时间的淡入淡出
$('#fadeBox').fadeIn(1000);      // 1秒淡入
$('#fadeBox').fadeOut(800);      // 0.8秒淡出
$('#fadeBox').fadeTo(600, 0.5);  // 0.6秒淡到50%透明度

// 带回调函数的淡出
$('#fadeBox').fadeOut(500, function() {
    console.log('淡出动画完成');
    console.log('元素display:', $(this).css('display'));
});

// 渐变效果对比
$('#fadeBox').fadeTo('slow', 0.2);  // 渐变到20%透明度

// 多个元素淡入
$('.boxes').fadeIn(300, function() {
    $(this).css('background', 'lightblue');
});

// 依次执行淡入淡出
$('#fadeBox')
    .fadeOut(300)
    .fadeIn(300)
    .fadeTo(200, 0.5)
    .fadeTo(200, 1);

// 应用半透明样式
$('.overlay').css({
    'background': 'black',
    'opacity': '0.5'
});

// 模拟loading效果
var loading = function() {
    $('#loading').fadeIn(200).fadeOut(200, loading);
};
loading();
```

## 滑动动画

滑动动画通过改变元素的height属性来实现上下滑动的效果，这种动画方式常用于手风琴菜单、折叠面板等交互组件。slideDown()方法使元素从上向下滑动展开，slideUp()方法使元素从下向上滑动收起，slideToggle()方法在滑动展开和滑动收起之间切换。滑动动画会平滑地改变元素的高度，从0变到完整高度或者从完整高度变到0。与淡入淡出不同，滑动动画在收起时会将元素的display属性设置为none，这意味着元素收起后不占用页面空间。

```html [index.html]
<div class="panel">
    <div class="header">点击展开面板</div>
    <div class="content">
        <p>这是面板的内容区域</p>
        <p>可以包含任意HTML元素</p>
        <p>滑动动画会平滑改变高度</p>
    </div>
</div>
<div class="accordion">
    <div class="item">
        <div class="title">标题1</div>
        <div class="body">内容1</div>
    </div>
    <div class="item">
        <div class="title">标题2</div>
        <div class="body">内容2</div>
    </div>
    <div class="item">
        <div class="title">标题3</div>
        <div class="body">内容3</div>
    </div>
</div>
```

```javascript [script.js]
// 初始隐藏内容
$('.content').hide();
$('.body').hide();

// 点击展开面板
$('.header').click(function() {
    $(this).next('.content').slideDown();
});

// 点击收起面板
$('.header').dblclick(function() {
    $(this).next('.content').slideUp();
});

// 切换展开收起
$('.title').click(function() {
    $(this).next('.body').slideToggle();
});

// 带时间的滑动动画
$('.content').slideDown(500);     // 0.5秒展开
$('.content').slideUp(400);       // 0.4秒收起
$('.body').slideToggle(300);       // 0.3秒切换

// 带回调函数的滑动
$('.content').slideDown(500, function() {
    console.log('展开动画完成');
    console.log('元素高度:', $(this).height());
});

// 手风琴效果：点击一个展开，其他收起
$('.title').click(function() {
    var $thisBody = $(this).next('.body');
    
    // 如果当前已经是展开状态，点击则收起
    if ($thisBody.is(':visible')) {
        $thisBody.slideUp();
        return;
    }
    
    // 收起所有其他展开的项
    $('.body').slideUp(300);
    
    // 展开当前项
    $thisBody.slideDown(300);
});

// 平滑高度调整
$('#myElement').slideUp(300, function() {
    $(this).css('height', '200px').slideDown(300);
});

// 链式滑动动画
$('.content')
    .slideUp(300)
    .slideDown(300)
    .slideUp(300)
    .slideDown(300);

// 多个面板同时滑动
$('.panel .content').slideDown();
$('.panel .content').slideUp();
```

::: danger
slideDown()和slideUp()方法在动画开始前会获取元素的完整高度，然后在动画过程中逐步改变height值。如果元素的height设置为auto，这些方法会先将其计算为具体的像素值，然后再进行动画。某些情况下，这可能导致动画性能问题。
:::

## 自定义动画

自定义动画是jQuery动画系统中最强大的功能，通过animate()方法可以对元素的任意CSS属性进行动画处理。animate()方法接受一个CSS属性对象、一个可选的动画持续时间、一个可选的缓动效果和一个可选的回调函数。除了数值类型的CSS属性外，animate()还支持相对值（使用+=或-=前缀）和属性值的计算。animate()方法是构建复杂动画效果的基础，通过组合多个animate()调用和利用动画队列，可以实现各种高级动画效果。CSS属性支持动画的有：width、height、opacity、margin、padding、border-width、font-size、line-height等。

```html [index.html]
<div id="customBox" class="box">自定义动画</div>
<button id="animateBtn">执行动画</button>
<button id="resetBtn">重置</button>
<div id="animateInfo"></div>
```

```javascript [script.js]
// 基本自定义动画
$('#animateBtn').click(function() {
    $('#customBox').animate({
        'width': '300px',
        'height': '200px',
        'background-color': 'lightblue'
    });
});

// 使用相对值
$('#customBox').animate({
    'width': '+=100px',   // 在当前宽度基础上增加100px
    'height': '+=50px'    // 在当前高度基础上增加50px
});

// 动画速度和缓动
$('#customBox').animate({
    'opacity': 0.5,
    'left': '+=50px'
}, 1000, 'swing');  // 1秒，使用摇摆缓动

$('#customBox').animate({
    'opacity': 1,
    'left': '-=50px'
}, 1000, 'linear'); // 1秒，使用线性缓动

// 带回调函数
$('#customBox').animate({
    'width': '200px',
    'height': '150px'
}, 500, 'swing', function() {
    console.log('动画完成！');
    $('#animateInfo').text('动画执行完毕');
});

// 多属性动画
$('#customBox').animate({
    'margin-left': '50px',
    'margin-right': '50px',
    'padding': '20px'
}, {
    duration: 500,
    easing: 'linear',
    complete: function() {
        console.log('所有属性动画完成');
    },
    step: function(now, fx) {
        // 动画每一步都会调用
        console.log('当前值:', now, fx.prop);
    },
    progress: function(promise, progress, remainingMs) {
        // 动画进度回调
        console.log('进度:', progress * 100 + '%');
    }
});

// 颜色动画需要额外插件
// jQuery核心不包括颜色动画
// $.fx.off = true;  // 禁用所有动画

// 使用stop()停止动画
$('#customBox').hover(
    function() {
        $(this).stop().animate({'width': '300px'}, 300);
    },
    function() {
        $(this).stop().animate({'width': '200px'}, 300);
    }
);

// 延迟动画执行
$('#customBox')
    .animate({'left': '100px'}, 300)
    .delay(500)               // 延迟500毫秒
    .animate({'top': '50px'}, 300);

// 队列动画：依次执行
$('#customBox')
    .animate({'width': '300px'}, 300)
    .animate({'height': '200px'}, 300)
    .animate({'opacity': 0.5}, 300);

// 并行动画：同时执行
$('#customBox').animate({'width': '300px'}, 300);
$('#customBox').animate({'height': '200px'}, 300);
// 注意：上面的写法实际上会依次执行，因为动画默认加入队列
// 要实现真正的并行效果，需要使用queue: false
$('#customBox')
    .animate({'width': '300px'}, {queue: false, duration: 300})
    .animate({'height': '200px'}, {queue: false, duration: 300});
```

## 动画队列

jQuery的动画系统使用了队列机制，默认情况下每个元素都有一个动画队列。当多个动画方法被连续调用时，它们会按照调用顺序依次执行，形成动画序列。可以通过queue()方法向队列中添加自定义函数，通过dequeue()方法执行队列中的下一个函数，通过clearQueue()方法清空队列中的所有待执行函数。这种队列机制使得复杂动画序列的编排变得简单直观。除了动画函数外，queue()方法还可以用于执行非动画的函数，这对于在动画序列中执行某些同步操作非常有用。

```html [index.html]
<div id="queueBox" class="box">队列动画示例</div>
<button id="startQueue">开始队列</button>
<button id="stopQueue">停止队列</button>
<button id="clearQueue">清空队列</button>
<button id="addToQueue">添加动画</button>
```

```javascript [script.js]
// 基本队列动画
$('#startQueue').click(function() {
    $('#queueBox')
        .animate({'width': '300px'}, 500)
        .animate({'height': '200px'}, 500)
        .animate({'opacity': 0.5}, 500)
        .animate({'left': '100px'}, 500);
});

// 使用stop()停止当前动画并继续队列中的下一个
$('#stopQueue').click(function() {
    $('#queueBox').stop();      // 停止当前动画
    $('#queueBox').stop(true);  // 停止并清空队列
});

// 清空队列
$('#clearQueue').click(function() {
    $('#queueBox').clearQueue();
});

// 向队列添加自定义函数
$('#queueBox').queue(function(next) {
    console.log('队列中的自定义函数1');
    // 执行某些操作...
    setTimeout(function() {
        console.log('异步操作完成');
        next(); // 调用next()继续执行队列中的下一个函数
    }, 500);
}).queue(function(next) {
    console.log('队列中的自定义函数2');
    next();
});

// 追加到当前队列
$('#addToQueue').click(function() {
    $('#queueBox').append('<div class="new-item">新项目</div>')
        .animate({'width': '+=50px'}, 300);
});

// 使用queue()获取队列长度
var queueLength = $('#queueBox').queue().length;
console.log('队列长度:', queueLength);

// 使用queue()替换队列
$('#queueBox').queue('fx', []); // 清空fx队列（动画队列）

// 延迟动画
$('#queueBox')
    .animate({'left': '100px'}, 1000)
    .delay(2000)  // 延迟2秒
    .animate({'top': '50px'}, 1000);

// 完整的loading动画队列
function showLoading() {
    var $loading = $('<div class="loading">加载中...</div>');
    $('#container').append($loading);
    
    $loading
        .fadeIn(200)
        .animate({'width': '100px'}, 1000)
        .fadeOut(200, function() {
            $(this).remove();
        });
}

// 链式动画与队列结合
function complexAnimation() {
    $('#queueBox')
        .animate({'width': '300px'}, 300)
        .animate({'height': '200px'}, 300)
        .queue(function(next) {
            // 在队列中执行自定义操作
            $(this).css('background', 'green');
            next();
        })
        .animate({'opacity': 0.5}, 300)
        .queue(function(next) {
            $(this).css('border', '3px solid red');
            next();
        })
        .animate({'rotate': '180deg'}, 300); // CSS3变换
}
```

::: tip
queue()方法中的next回调函数非常重要。如果在队列函数中执行了异步操作（如setTimeout、AJAX请求等），必须调用next()函数来继续执行队列中的下一个函数，否则队列会停在那里不再继续执行。
:::

## 动画控制技巧

在实际开发中，动画控制是一个重要的技能。合理使用动画技巧可以提升用户体验，同时避免动画带来的性能问题。stop()方法用于停止当前正在执行的动画，可以选择是否清空队列。finish()方法会立即完成队列中所有待执行的动画。jQuery.fx对象提供了一些全局设置，如禁用所有动画、设置默认动画时长等。对于高频触发的动画（如scroll、resize事件触发的动画），应该使用防抖或节流来控制动画的执行频率，避免造成页面卡顿。

```javascript [script.js]
// 动画控制方法
// 停止当前动画
$('#element').stop();

// 停止当前动画并清空队列
$('#element').stop(true);

// 停止当前动画，清空队列，跳到动画最终状态
$('#element').stop(true, true);

// 停止当前动画，保留在当前状态，清空队列
$('#element').stop(true, false);

// 立即完成所有队列中的动画
$('#element').finish();

// 全局动画设置
// 禁用所有动画
$.fx.off = true;

// 设置默认动画时长
$.fx.speeds._default = 500;
$.fx.speeds.fast = 200;
$.fx.speeds.slow = 600;

// 自定义默认速度
$.fx.speeds.mySpeed = 300;

// 检测动画是否正在进行
if ($('#element').is(':animated')) {
    console.log('元素正在动画中');
    $('#element').stop();
}

// 防抖动画函数
function debounceAnimate(element, properties, duration) {
    if (element.data('animating')) {
        element.stop(true);
    }
    
    element.data('animating', true);
    element.animate(properties, duration, function() {
        element.removeData('animating');
    });
}

// 节流动画函数
var animating = false;
function throttleAnimate(element, properties, duration) {
    if (animating) return;
    animating = true;
    element.animate(properties, duration, function() {
        animating = false;
    });
}

// 鼠标移动动画
var $followBox = $('#followBox');
$(document).on('mousemove', function(e) {
    debounceAnimate($followBox, {
        'left': e.pageX + 10,
        'top': e.pageY + 10
    }, 50);
});

// 点击反馈动画
$('.btn').click(function() {
    var $btn = $(this);
    
    $btn.animate({'transform': 'scale(0.95)'}, 100, function() {
        $(this).animate({'transform': 'scale(1)'}, 100);
    });
});

// 滚动到指定位置动画
function scrollToElement(target) {
    $('html, body').animate({
        'scrollTop': $(target).offset().top
    }, 500);
}

// 平滑滚动到顶部
$('#backToTop').click(function() {
    $('html, body').animate({'scrollTop': 0}, 300);
});

// 数字递增动画
function animateNumber(element, from, to, duration) {
    element.animate({},
        {
            duration: duration,
            step: function(now) {
                $(this).text(Math.round(from + (to - from) * (now / 100)));
            }
        }
    );
}
```

```javascript [script.js]
// 动画性能优化
// 1. 使用transform和opacity进行动画
$('#element').animate({
    'transform': 'translateX(100px)',
    'opacity': 0.5
}, 300);

// 2. 避免动画属性引起重排
// 好的动画属性：transform, opacity
// 不好的动画属性：width, height, margin, padding（会引起重排重绘）

// 3. 使用will-change提示浏览器
$('#element').css('will-change', 'transform, opacity');

// 4. 批量处理DOM操作后再动画
var $container = $('#container');
var $elements = $container.find('.item');
$elements.hide();
$container.addClass('loading');
$elements.fadeIn();

// 5. 使用requestAnimationFrame替代animate（高级用法）
function rafAnimate(element, properties, duration) {
    var start = null;
    var $el = $(element);
    
    function step(timestamp) {
        if (!start) start = timestamp;
        var progress = timestamp - start;
        var percent = Math.min(progress / duration, 1);
        
        // 应用缓动
        var easedPercent = percent; // 可以添加缓动函数
        
        // 应用属性
        $el.css(properties);
        
        if (progress < duration) {
            requestAnimationFrame(step);
        }
    }
    
    requestAnimationFrame(step);
}

// 6. 检测动画是否被禁用
if ($.fx.off) {
    $('#element').show();
} else {
    $('#element').fadeIn();
}
```
