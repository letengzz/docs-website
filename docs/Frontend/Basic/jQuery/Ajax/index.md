# jQuery AJAX

AJAX（Asynchronous JavaScript and XML）是一种在不重新加载整个页面的情况下，与服务器交换数据并更新部分网页内容的技术。jQuery提供了简单而强大的AJAX API，大大简化了AJAX开发流程。通过jQuery的AJAX方法，可以轻松实现异步请求、GET/POST请求、JSON数据获取以及错误处理等功能。jQuery的AJAX实现基于XMLHttpRequest对象，但提供了更友好的接口和更好的浏览器兼容性。除了核心的$.ajax()方法外，jQuery还提供了$.get()、$.post()、$.getJSON()和$.getScript()等快捷方法，可以快速实现常见的AJAX请求类型。

## AJAX基本用法

jQuery的AJAX核心是$.ajax()方法，它提供了最完整的配置选项，可以精确控制AJAX请求的各个方面。$.ajax()方法接受一个配置对象作为参数，可以设置请求URL、请求方法、请求头、发送数据、响应处理函数、错误处理函数以及超时时间等。除了$.ajax()方法外，jQuery还提供了几个快捷方法：$.get()用于发起GET请求，$.post()用于发起POST请求，$.getJSON()用于获取JSON数据，$.getScript()用于获取并执行JavaScript脚本。这些快捷方法在日常开发中使用频率很高，可以快速实现常见的AJAX需求。

```html [index.html]
<button id="loadData">加载数据</button>
<button id="postData">提交数据</button>
<button id="getJson">获取JSON</button>
<button id="getScript">加载脚本</button>
<div id="result">结果将显示在这里</div>
<div id="dataDisplay">JSON数据：</div>
```

```javascript [script.js]
// 基本AJAX请求
$('#loadData').click(function() {
    $.ajax({
        url: '/api/data',
        method: 'GET',
        success: function(data) {
            $('#result').html('数据加载成功：' + data.message);
        },
        error: function(xhr, status, error) {
            $('#result').html('请求失败：' + error);
        }
    });
});

// 使用$.get()快捷方法
$('#loadData').click(function() {
    $.get('/api/users', function(data) {
        console.log('用户数据:', data);
        $('#result').html('获取到 ' + data.length + ' 个用户');
    });
});

// 使用$.post()快捷方法
$('#postData').click(function() {
    $.post('/api/submit', {
        name: '张三',
        email: 'zhangsan@example.com'
    }, function(response) {
        console.log('提交结果:', response);
        $('#result').html('数据提交成功');
    });
});

// 使用$.getJSON()获取JSON数据
$('#getJson').click(function() {
    $.getJSON('/api/config', function(data) {
        console.log('配置数据:', data);
        $('#dataDisplay').html(
            '网站名称：' + data.siteName + '<br>' +
            '版本：' + data.version + '<br>' +
            'API地址：' + data.apiUrl
        );
    });
});

// 使用$.getScript()加载并执行脚本
$('#getScript').click(function() {
    $.getScript('/js/util.js', function() {
        // 脚本加载完成后，函数Util已经可用
        console.log('Util对象:', Util);
        $('#result').html('脚本加载完成');
    });
});

// 完整的$.ajax()配置
$.ajax({
    url: '/api/data',
    type: 'POST',           // 请求方法（GET、POST等）
    async: true,            // 是否异步
    cache: true,            // 是否缓存
    data: {                 // 发送到服务器的数据
        page: 1,
        limit: 10
    },
    dataType: 'json',      // 预期服务器返回的数据类型
    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
    timeout: 5000,          // 超时时间（毫秒）
    
    // 请求头
    headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Authorization': 'Bearer token123'
    },
    
    // 请求成功回调
    success: function(data, textStatus, jqXHR) {
        console.log('状态码:', jqXHR.status);
        console.log('响应数据:', data);
        console.log('状态文本:', textStatus);
    },
    
    // 请求错误回调
    error: function(jqXHR, textStatus, errorThrown) {
        console.log('错误状态:', textStatus);
        console.log('错误信息:', errorThrown);
        console.log('状态码:', jqXHR.status);
        console.log('响应文本:', jqXHR.responseText);
    },
    
    // 请求完成回调（无论成功或失败）
    complete: function(jqXHR, textStatus) {
        console.log('请求完成，状态：', textStatus);
    }
});
```

::: tip
$.ajax()的dataType选项用于指定预期服务器返回的数据类型，jQuery会根据这个值自动对响应数据进行解析。如果指定为'json'，jQuery会自动将响应体解析为JSON对象；如果指定为'xml'，则会解析为XML文档；如果不指定或指定为'text'，则返回原始字符串。
:::

## GET与POST请求

GET和POST是最常用的两种HTTP请求方法，它们在使用场景和数据传输方式上有明显的区别。GET请求用于从服务器获取数据，请求参数附加在URL后面，以问号分隔，多个参数用&连接。GET请求有长度限制且会被浏览器缓存，安全性较低，适用于查询操作。POST请求用于向服务器提交数据，请求参数放在请求体中，没有长度限制，不会被浏览器缓存，安全性相对较高，适用于提交表单、上传文件等操作。jQuery提供了$.get()和$.post()两个快捷方法分别处理这两种请求。

```html [index.html]
<form id="searchForm">
    <input type="text" name="keyword" placeholder="搜索关键词">
    <button type="submit">搜索</button>
</form>
<form id="loginForm">
    <input type="text" name="username" placeholder="用户名">
    <input type="password" name="password" placeholder="密码">
    <button type="submit">登录</button>
</form>
<div id="searchResults"></div>
<div id="loginResult"></div>
```

```javascript [script.js]
// GET请求：搜索功能
$('#searchForm').submit(function(e) {
    e.preventDefault();
    var keyword = $(this).find('input[name="keyword"]').val();
    
    $.get('/api/search', { q: keyword }, function(data) {
        console.log('搜索结果:', data);
        
        var html = '<ul>';
        data.results.forEach(function(item) {
            html += '<li>' + item.title + ' - ' + item.url + '</li>';
        });
        html += '</ul>';
        $('#searchResults').html(html);
    }).fail(function() {
        $('#searchResults').html('搜索请求失败');
    });
});

// GET请求带查询参数
$.get('/api/users', {
    page: 1,
    limit: 20,
    sort: 'created_at',
    order: 'desc'
}, function(data) {
    console.log('用户列表:', data);
});

// POST请求：登录表单
$('#loginForm').submit(function(e) {
    e.preventDefault();
    var formData = $(this).serialize();
    
    $.post('/api/login', formData, function(response) {
        if (response.success) {
            $('#loginResult').html('登录成功，欢迎 ' + response.user.name);
            // 保存token
            localStorage.setItem('token', response.token);
        } else {
            $('#loginResult').html('登录失败：' + response.message);
        }
    }).fail(function() {
        $('#loginResult').html('登录请求失败');
    });
});

// 序列化表单数据
$('#loginForm').submit(function(e) {
    e.preventDefault();
    
    // 序列化整个表单
    var serialized = $(this).serialize();
    console.log('序列化数据:', serialized);
    
    // 序列化并转为对象
    var formData = $(this).serializeArray();
    var dataObj = {};
    formData.forEach(function(item) {
        dataObj[item.name] = item.value;
    });
    console.log('对象形式:', dataObj);
});

// GET请求：带请求头
$.ajax({
    url: '/api/protected',
    method: 'GET',
    headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token')
    },
    success: function(data) {
        console.log('受保护数据:', data);
    }
});

// POST请求：发送JSON数据
$.ajax({
    url: '/api/users',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        name: '新用户',
        email: 'new@example.com',
        role: 'admin'
    }),
    success: function(data) {
        console.log('用户创建成功:', data);
    }
});

// GET请求：带回调参数（jQuery 1.12+）
$.get('/api/data', function(data) {
    console.log('数据:', data);
}, 'json');  // 指定返回数据类型
```

## JSON数据处理

JSON（JavaScript Object Notation）是一种轻量级的数据交换格式，在AJAX应用中广泛使用。jQuery提供了$.getJSON()方法专门用于获取JSON数据，它可以自动将服务器返回的JSON字符串解析为JavaScript对象。$.ajax()方法在设置dataType为'json'时也会自动进行JSON解析。对于复杂的JSON数据结构，可以结合使用JSON.parse()和JSON.stringify()来进行手动解析和序列化。在处理JSON数据时，需要注意处理可能出现的解析错误，可以使用try-catch语句或$.ajax()的error回调来捕获这些错误。

```javascript [script.js]
// 使用$.getJSON()获取JSON数据
$.getJSON('/api/config', function(config) {
    console.log('网站配置:', config);
    console.log('版本号:', config.version);
    console.log('功能模块:', config.features);
    
    // 遍历数组
    config.modules.forEach(function(module) {
        console.log('模块:', module.name, '- 状态:', module.enabled);
    });
    
    // 访问嵌套对象
    console.log('数据库配置:', config.database.host, config.database.port);
});

// $.getJSON()的简写形式
var request = $.getJSON('/api/data');
request.done(function(data) {
    console.log('数据:', data);
});
request.fail(function() {
    console.log('请求失败');
});

// 发送JSON POST请求
function createUser(userData) {
    return $.ajax({
        url: '/api/users',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(userData)
    });
}

// 使用Promise处理多个请求
$.when(
    $.getJSON('/api/user/1'),
    $.getJSON('/api/posts/1'),
    $.getJSON('/api/comments/1')
).then(function(userData, postsData, commentsData) {
    console.log('用户信息:', userData[0]);
    console.log('文章列表:', postsData[0]);
    console.log('评论列表:', commentsData[0]);
}).catch(function() {
    console.log('请求失败');
});

// 处理JSONP跨域请求
$.ajax({
    url: 'https://api.example.com/data',
    dataType: 'jsonp',
    jsonp: 'callback',           // JSONP回调参数名
    jsonpCallback: 'myCallback', // 回调函数名
    success: function(data) {
        console.log('JSONP数据:', data);
    },
    error: function() {
        console.log('JSONP请求失败');
    }
});

// 现代JSONP写法
$.ajax({
    url: 'https://api.example.com/data',
    dataType: 'jsonp',
    success: function(data) {
        console.log('数据:', data);
    }
});

// 手动解析JSON（处理特殊字符）
try {
    var obj = JSON.parse('{"name": "测试"}');
    console.log('解析成功:', obj);
} catch (e) {
    console.log('JSON解析错误:', e.message);
}

// 序列化JSON
var jsonStr = JSON.stringify({ name: '张三', age: 25 });
console.log('JSON字符串:', jsonStr);

// 过滤JSON数据
$.getJSON('/api/users', function(users) {
    var activeUsers = users.filter(function(user) {
        return user.status === 'active';
    });
    console.log('活跃用户:', activeUsers);
    
    // 映射数据格式
    var userNames = users.map(function(user) {
        return user.name;
    });
    console.log('用户名称列表:', userNames);
});
```

## 错误处理

在AJAX请求中，错误处理是一个重要的环节。服务器可能因为各种原因返回错误，如网络问题、服务器错误、请求超时、数据格式错误等。jQuery的AJAX方法提供了error回调函数来处理这些错误情况。error回调函数接收三个参数：jqXHR对象、错误状态文本和错误信息。通过jqXHR对象可以获取详细的错误信息，包括状态码、响应头和响应内容。此外，还可以使用$.ajaxSetup()方法来设置全局的AJAX错误处理函数，以及使用ajaxError()方法来绑定全局的AJAX错误事件。

```javascript [script.js]
// 基本错误处理
$.ajax({
    url: '/api/data',
    success: function(data) {
        console.log('成功:', data);
    },
    error: function(jqXHR, textStatus, errorThrown) {
        console.log('错误类型:', textStatus);
        console.log('错误信息:', errorThrown);
        console.log('状态码:', jqXHR.status);
        
        // 根据状态码处理不同错误
        if (jqXHR.status === 404) {
            $('#errorMsg').html('请求的资源不存在');
        } else if (jqXHR.status === 500) {
            $('#errorMsg').html('服务器内部错误');
        } else if (textStatus === 'timeout') {
            $('#errorMsg').html('请求超时，请重试');
        } else if (textStatus === 'abort') {
            $('#errorMsg').html('请求被取消');
        } else {
            $('#errorMsg').html('请求失败：' + textStatus);
        }
    }
});

// 使用jqXHR对象的方法
$.ajax({
    url: '/api/data',
    method: 'POST'
}).done(function(data) {
    console.log('成功:', data);
}).fail(function(jqXHR, textStatus, errorThrown) {
    console.log('失败');
    console.log('状态码:', jqXHR.status);
    console.log('响应头:', jqXHR.getAllResponseHeaders());
    console.log('响应内容:', jqXHR.responseText);
}).always(function() {
    console.log('请求完成');
});

// 使用then()和catch()（jQuery 3+）
$.ajax({
    url: '/api/data'
}).then(
    function(data) {
        console.log('成功:', data);
        return data;
    },
    function(jqXHR, textStatus, errorThrown) {
        console.log('失败:', textStatus);
        throw new Error('请求失败');
    }
).catch(function(error) {
    console.log('捕获错误:', error.message);
});

// 超时处理
$.ajax({
    url: '/api/slow-request',
    timeout: 3000,  // 3秒超时
    success: function(data) {
        console.log('数据:', data);
    },
    error: function(jqXHR, textStatus) {
        if (textStatus === 'timeout') {
            console.log('请求超时');
            $('#result').html('请求超时，请稍后重试');
        } else {
            console.log('其他错误:', textStatus);
        }
    }
});

// 状态码处理
$.ajax({
    url: '/api/data',
    statusCode: {
        200: function(data) {
            console.log('正常响应:', data);
        },
        201: function(data) {
            console.log('创建成功:', data);
        },
        400: function() {
            console.log('请求参数错误');
        },
        401: function() {
            console.log('未授权，请登录');
            // 跳转到登录页
            window.location.href = '/login';
        },
        403: function() {
            console.log('禁止访问');
        },
        404: function() {
            console.log('资源不存在');
        },
        500: function() {
            console.log('服务器错误');
        }
    }
});

// 全局错误处理
$(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
    console.log('全局AJAX错误');
    console.log('状态码:', jqXHR.status);
    console.log('错误信息:', thrownError);
    console.log('请求URL:', ajaxSettings.url);
    
    // 显示全局错误提示
    $('#globalError')
        .text('请求失败，请检查网络连接')
        .show()
        .fadeOut(3000);
});

// 使用Promise的错误处理
function fetchData(url) {
    return $.ajax({
        url: url,
        dataType: 'json'
    });
}

fetchData('/api/data')
    .then(function(data) {
        if (!data.success) {
            return $.Deferred().reject(data.message);
        }
        return data;
    })
    .done(function(data) {
        console.log('处理完成:', data);
    })
    .fail(function(error) {
        console.log('错误:', error);
    });
```

## AJAX高级配置

jQuery的AJAX系统提供了丰富的配置选项，可以满足各种复杂的请求需求。通过$.ajaxSetup()可以设置全局默认配置，避免在每次请求中重复设置相同的选项。发送数据时，可以使用processData和contentType选项来控制数据的处理方式。使用beforeSend回调可以在发送请求前修改请求头或执行其他预处理操作。使用dataFilter可以过滤服务器返回的原始数据。通过设置crossDomain选项可以实现跨域请求的处理。这些高级配置选项使得jQuery的AJAX能够应对各种复杂的网络请求场景。

```javascript [script.js]
// 全局AJAX配置
$.ajaxSetup({
    url: '/api',              // 默认URL
    type: 'GET',              // 默认请求方法
    dataType: 'json',         // 默认数据类型
    timeout: 5000,           // 默认超时时间
    cache: true,             // 默认是否缓存
    
    // 默认请求头
    headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json; charset=utf-8'
    },
    
    // 全局成功处理
    success: function(data) {
        console.log('请求成功:', data);
    },
    
    // 全局错误处理
    error: function(jqXHR, textStatus, errorThrown) {
        console.log('请求失败:', textStatus);
    }
});

// 发送请求前的回调
$.ajax({
    url: '/api/submit',
    method: 'POST',
    beforeSend: function(jqXHR, settings) {
        // 可以修改请求头
        jqXHR.setRequestHeader('X-Custom-Header', 'value');
        
        // 可以验证数据
        if (!settings.data.name) {
            jqXHR.abort();  // 取消请求
            console.log('数据验证失败');
            return false;
        }
        
        console.log('请求即将发送');
        $('#loading').show();
    },
    complete: function() {
        $('#loading').hide();
    }
});

// 数据过滤
$.ajax({
    url: '/api/data',
    dataFilter: function(data, dataType) {
        // 过滤和转换响应数据
        var json = JSON.parse(data);
        // 移除敏感信息
        delete json.password;
        delete json.secretKey;
        // 返回处理后的数据
        return JSON.stringify(json);
    },
    success: function(data) {
        // 这里的数据已经是过滤后的
        console.log('过滤后的数据:', data);
    }
});

// 处理表单数据提交
$('#myForm').submit(function(e) {
    e.preventDefault();
    
    var formData = $(this).serialize();
    
    $.ajax({
        url: '/api/submit',
        method: 'POST',
        data: formData,
        processData: true,  // 默认true，将数据转换为查询字符串
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
            console.log('提交成功:', response);
        }
    });
});

// 发送JSON数据
$.ajax({
    url: '/api/users',
    method: 'POST',
    data: JSON.stringify({
        name: '新用户',
        email: 'user@example.com'
    }),
    processData: false,  // 不处理数据
    contentType: 'application/json',
    success: function(data) {
        console.log('用户创建成功:', data);
    }
});

// 上传文件
$('#uploadForm').submit(function(e) {
    e.preventDefault();
    
    var formData = new FormData(this);
    
    $.ajax({
        url: '/api/upload',
        method: 'POST',
        data: formData,
        processData: false,  // 不处理FormData
        contentType: false,  // 不设置Content-Type，让浏览器自动设置
        xhr: function() {
            var xhr = new XMLHttpRequest();
            // 上传进度
            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    var percent = Math.round(e.loaded / e.total * 100);
                    $('#progress').width(percent + '%');
                    console.log('上传进度:', percent + '%');
                }
            });
            return xhr;
        },
        success: function(data) {
            console.log('上传成功:', data);
        },
        error: function() {
            console.log('上传失败');
        }
    });
});

// 取消AJAX请求
var xhr = $.ajax({
    url: '/api/large-data',
    method: 'GET',
    success: function(data) {
        console.log('数据:', data);
    }
});

// 取消请求
$('#cancelBtn').click(function() {
    xhr.abort();
    console.log('请求已取消');
});

// 跨域请求
$.ajax({
    url: 'https://api.other-domain.com/data',
    crossDomain: true,
    success: function(data) {
        console.log('跨域数据:', data);
    }
});

// 发送数组数据
$.ajax({
    url: '/api/tags',
    method: 'POST',
    traditional: true,  // 传统参数序列化
    data: {
        tags: ['javascript', 'jquery', 'ajax']  // 会被序列化为 tags[]=javascript&tags[]=jquery...
    },
    success: function(response) {
        console.log('标签创建成功:', response);
    }
});
```

::: tip
使用FormData上传文件时，必须设置processData为false和contentType为false，否则jQuery会对FormData进行错误的处理，导致文件无法正确上传。
:::
