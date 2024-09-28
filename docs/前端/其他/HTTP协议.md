# HTTP 协议

HTTP协议(`hypertext transport protocol`，中文叫超文本传输协议)是一种基于TCP/IP的应用层通信协议

这个协议详细规定了浏览器和万维网服务器之间互相通信的规则。

协议中主要规定了两个方面的内容：

- 客户端：用来向服务器发送数据，可以被称之为请求报文
- 服务端：向客户端返回数据，可以被称之为响应报文

> 报文：可以简单理解为就是一堆字符串

## 请求报文

**请求报文的组成**：

- 请求行
- 请求头
- 空行
- 请求体

![image-20231004203416274](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310042034524.png)

### 请求行

请求行包括：

- 请求方法 (get、post、put、delete等)
- 请求 URL (统一资源定位器)
  -  http://www.baidu.com:80/index.html?a=100&b=200#logo
    - `http`： 协议 (https、ftp、ssh等)
    - `www.baidu.com`：域名
    - `80`：端口号
    - `/index.html`：路径
    - `a=100&b=200`：查询字符串
    - `#logo`：哈希 (锚点链接)

- HTTP协议版本号

![image-20231004203444848](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310042034282.png)

### 请求头

**请求头格式**：『头名：头值』

**常见的请求头**：

![image-20231004173622719](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409281731694.png)

### 请求体

请求体内容的格式是非常灵活的， **GET请求可以是空，POST请求可以是字符串也可以是JSON**

**例**：

- 字符串：`keywords=手机&price=2000`
- JSON：`{"keywords":"手机","price":2000}`

## 响应报文

### 响应行

`HTTP/1.1 200 OK`

- HTTP/1.1：HTTP协议版本号

- 200：响应状态码 `404 Not Found`、`500 Internal Server Error`

  状态码： https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status

- OK：响应状态描述

**说明**：响应状态码和响应字符串关系是一一对应的。

### 响应头

- Cache-Control：缓存控制 private 私有的，只允许客户端缓存数据
- Connection：链接设置
- Content-Type:text/html;charset=utf-8：设置响应体的数据类型以及字符集,响应体为html，字符集utf-8
- Content-Length：响应体的长度，单位为字节

### 空行

### 响应体

响应体内容的类型是非常灵活的，常见的类型有 HTML、CSS、JS、图片、JSON

## 浏览器查看HTTP报文

使用浏览器右击点击检查，点击Network，之后发送请求，即可看到请求数据：

![image-20231004190414813](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041904049.png)

![image-20231004190554682](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041905272.png)

点击某个请求即可看到请求报文、响应报文：

![image-20231004190749894](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041907307.png)

### 查看请求行、请求头

![image-20231004192840366](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041930763.png)

### 查看请求体

![image-20231011151925737](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310111537460.png)

### 查看URL查询字符串

![image-20231004194738430](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041947095.png)

### 查看响应行与响应头

![image-20231004194026623](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041940664.png)

### 查看响应体

![image-20231004193721988](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041937032.png)