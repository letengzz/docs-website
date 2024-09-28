# path 模块

path 模块提供了操作路径的功能。常用的几个 API：

![image-20231004155529861](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041555525.png)

**导入path 模块**：

`require()`是一个全局的函数，可以通过`require()` 导入path模块。

```js
const path = require('path');
```

**获取路径分隔符**：

```js
console.log(path.sep);
```

![image-20231004160240317](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041602421.png)

**拼接绝对路径**：

```js
console.log(path.resolve(__dirname,'test'));
console.log(path.resolve(__dirname,'/test','./index.html'));
console.log(path.resolve(__dirname,'./test'));
```

![image-20231004162251625](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041622002.png)

**解析路径**：

```js
let pathname = 'D:/program file/nodejs/node.exe';
//解析路径
console.log(path.parse(pathname));
```

![image-20231004160658076](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041607064.png)

**获取路径基础名称**：

```js
let pathname = 'D:/program file/nodejs/node.exe';
//获取路径基础名称
console.log(path.basename(pathname));
```

![image-20231004160927593](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041609175.png)

**获取路径的目录名**：

```js
let pathname = 'D:/program file/nodejs/node.exe';
//获取路径的目录名
console.log(path.dirname(pathname));
```

![image-20231004161032477](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041611563.png)

**获取路径的拓展名**：

```js
let pathname = 'D:/program file/nodejs/node.exe';
//获取路径的拓展名
console.log(path.extname(pathname));
```

![image-20231004161130016](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041611156.png)