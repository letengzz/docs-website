# path 模块

path 模块提供了操作路径的功能。常用的几个 API：

![path API](../assets/202310041555525.png)

**导入path 模块**：

`require()`是一个全局的函数，可以通过`require()` 导入path模块。

```js [index.js]
const path = require('path')
```

**获取路径分隔符**：

```js [sep.js]
console.log(path.sep)
```

![path.sep](../assets/202310041602421.png)

**拼接绝对路径**：

```js [resolve.js]
console.log(path.resolve(__dirname, 'test'))
console.log(path.resolve(__dirname, '/test', './index.html'))
console.log(path.resolve(__dirname, './test'))
```

![path.resolve](../assets/202310041622002.png)

**解析路径**：

```js [parse.js]
let pathname = 'D:/program file/nodejs/node.exe'
//解析路径
console.log(path.parse(pathname))
```

![path.parse](../assets/202310041607064.png)

**获取路径基础名称**：

```js [basename.js]
let pathname = 'D:/program file/nodejs/node.exe'
//获取路径基础名称
console.log(path.basename(pathname))
```

![path.basename](../assets/202310041609175.png)

**获取路径的目录名**：

```js [dirname.js]
let pathname = 'D:/program file/nodejs/node.exe'
//获取路径的目录名
console.log(path.dirname(pathname))
```

![path.dirname](../assets/202310041611563.png)

**获取路径的拓展名**：

```js [extname.js]
let pathname = 'D:/program file/nodejs/node.exe'
//获取路径的拓展名
console.log(path.extname(pathname))
```

![path.extname](../assets/202310041611156.png)
