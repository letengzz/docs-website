# ES 5

## 模块化开发

传统非模块化开发有如下的缺点：

- 命名冲突
- 文件依赖

模块化规范：

- CommonJS模块化规范（ES5模块化规范）
- ES6模块化规范

每个文件就是一个模块，有自己作用域。在一个文件里定义的变量、函数、类，都是私有的，对其他文件不可见。

### 创建导出模块

创建 common/四则运算.js

```javascript
// 定义成员：
const sum = function(a,b){
    return parseInt(a) + parseInt(b)
}
const subtract = function(a,b){
    return parseInt(a) - parseInt(b)
}
```

导出模块中的成员

```javascript
// 导出成员：
module.exports = {
    sum: sum,
    subtract: subtract
}
```

简写：

```javascript
//简写
module.exports = {
    sum,
    subtract
}
```

### 导入模块

创建 common/引入模块.js

```javascript
//引入模块，注意：当前路径必须写 ./
const m = require('./四则运算.js')
console.log(m)
const result1 = m.sum(1, 2)
const result2 = m.subtract(1, 2)
console.log(result1, result2)
```

### 运行程序

```shell
node common/引入模块.js
```

CommonJS使用 exports 和require 来导出、导入模块。

