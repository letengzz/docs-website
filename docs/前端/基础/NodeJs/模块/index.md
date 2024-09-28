# 模块化

将一个复杂的程序文件依据一定规则（规范）拆分成多个文件的过程称之为**模块化**

其中拆分出的每个文件就是一个模块，**模块的内部数据是私有的**，不过模块可以暴露内部数据以便其他
模块使用

**模块化项目**：编码时是按照模块一个一个编码的， 整个项目就是一个模块化的项目

**模块化的好处**：

1. 防止命名冲突
2. 高复用性
3. 高维护性

## 模块暴露数据

**模块化**：

1. 创建 me.js

   ```js
   //声明函数
   function tiemo(){
       console.log('贴膜...');
   }
   //暴露数据
   module.exports = tiemo;
   ```

2. 创建 index.js

   ```js
   //导入模块
   const tiemo = require('./me.js');
   //调用函数
   tiemo();
   ```

模块暴露数据的方式有两种：
1. `module.exports = value`
2. `exports.name = value`

**注意**：

- `module.exports` 可以暴露任意数据

- 不能使用 `exports = value` 的形式暴露数据，模块内部 module 与 exports 的隐式关系 `exports = module.exports = {}` ，require 返回的是目标模块中 `module.exports` 的值

  ```js
  console.log(exports === module.exports); //true
  ```


![](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310151144090.jpg)

****

module.exports 暴露多个数据：

```js
function tiemo() {
    console.log('贴膜...');
}

function niejiao() {
    console.log('捏脚...');
}

//暴露数据
module.exports = {
    tiemo,
    niejiao
}
```

```js
//导入模块
const me = require('./me.js');

console.log(me);
//调用函数
me.tiemo();
me.niejiao();
```

![image-20231015121039460](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310151210376.png)

module.exports 可以暴露'任意'数据：

```js
// module.exports = 'i love u';
module.exports = 521;
```

```js
//导入模块
const me = require('./me.js');

console.log(me);
```

![image-20231015121312818](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310151213697.png)

![image-20231015121338489](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310151213835.png)

exports 暴露数据：

```js
//声明函数
function tiemo() {
    console.log('贴膜...');
}

function niejiao() {
    console.log('捏脚...');
}

//exports 暴露数据
exports.niejiao = niejiao;
exports.tiemo = tiemo;
```

```js
//导入模块
const me = require('./me.js');

//调用函数
console.log(me);
me.tiemo();
me.niejiao();
```

![image-20231015121602643](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310151216902.png)

不能使用 `exports = value` 的形式暴露数据：

```js
//不能使用 `exports = value` 的形式暴露数据
exports = 'i love u';
```

```js
//导入模块
const me = require('./me.js');

//调用函数
console.log(me);
```

![image-20231015121855043](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310151218452.png)

## 导入(引入)模块

在模块中使用 require 传入文件路径即可引入文件

```js
const test = require('./me.js');
```

**require 使用注意事项**：

1. 对于自己创建的模块，导入时路径建议写相对路径，且不能省略`./` 和`../`
2. js 和 json 文件导入时可以不用写后缀，c/c++编写的node 扩展文件也可以不写后缀，但是一般用不到
3. 如果导入其他类型的文件，会以 js 文件进行处理
4. 如果导入的路径是个文件夹，则会首先检测该文件夹下 package.json 文件中 main 属性对应的文件，如果存在则导入，反之如果文件不存在会报错。
如果 main 属性不存在，或者 package.json 不存在，则会尝试导入文件夹下的 index.js 和index.json ，如果还是没找到，就会报错
5. 导入 node.js 内置模块时，直接 require 模块的名字即可，无需加`./` 和`../`

## 导入模块的基本流程

**require 导入自定义模块的基本流程**：

1. 将相对路径转为绝对路径，定位目标文件
2. 缓存检测
3. 读取目标文件代码
4. 包裹为一个函数并执行（自执行函数）。通过 `arguments.callee.toString()` 查看自执行函数
5. 缓存模块的值
6. 返回 `module.exports` 的值

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202310251822935.jpg)

## CommonJS 规范

`module.exports` 、`exports` 以及 `require` 这些都是 CommonJS 模块化规范中的内容。

而 Node.js 是实现了 CommonJS 模块化规范，二者关系有点像 JavaScript 与 ECMAScript
