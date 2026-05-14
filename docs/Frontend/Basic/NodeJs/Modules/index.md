# 模块化

将一个复杂的程序文件依据一定规则（规范）拆分成多个文件的过程称之为**模块化**

其中拆分出的每个文件就是一个模块，**模块的内部数据是私有的**，不过模块可以暴露内部数据以便其他模块使用

## 模块暴露数据

模块暴露数据的方式有两种：

1. `module.exports = value`
2. `exports.name = value`

**注意**：

- `module.exports` 可以暴露任意数据

- 不能使用 `exports = value` 的形式暴露数据

module.exports 暴露多个数据：

```js [m1.js]
function tiemo() {
  console.log('贴膜...')
}

function niejiao() {
  console.log('捏脚...')
}

//暴露数据
module.exports = {
  tiemo,
  niejiao,
}
```

exports 暴露数据：

```js [m2.js]
//声明函数
function tiemo() {
  console.log('贴膜...')
}

function niejiao() {
  console.log('捏脚...')
}

//exports 暴露数据
exports.niejiao = niejiao
exports.tiemo = tiemo
```

## 导入模块

```js [app.js]
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const m1 = require('./m1.js')
const m2 = require('./m2.js')

console.log(m1)
console.log(m2)

m1.tiemo()
m2.niejiao()
```

## CommonJS 规范

Node.js 采用的是 CommonJS 模块化规范

**特点**：

- 所有代码运行在当前模块作用域，不会污染全局作用域
- 模块同步加载，根据读取顺序执行
- 模块可以多次加载，但只会在第一次加载时运行一次，然后运行结果被缓存
- 加载模块时，会按照书写顺序执行

## 模块分类

Node.js 中的模块可以分为三类：

1. **内置模块（核心模块）**：Node.js 官方提供的模块，如 fs、path、http 等
2. **自定义模块**：用户自己创建的模块
3. **第三方模块**：通过 npm 下载的模块

## 模块加载机制

```js [module-loading.js]
// 1. 加载内置模块
const fs = require('fs')

// 2. 加载自定义模块
const myModule = require('./myModule')

// 3. 加载第三方模块
const express = require('express')

// 4. 加载JSON文件
const config = require('./config.json')

// 5. 加载JS文件
const utils = require('./utils.js')
```

## 模块缓存

```js [cache.js]
// a.js
console.log('a.js 被加载')
module.exports = { name: 'a' }

// main.js
const a1 = require('./a')
const a2 = require('./a')

console.log(a1 === a2) // true，模块被缓存
```

## 模块循环引用

```js [circular.js]
// a.js
const b = require('./b')
console.log('a.js 中的 b:', b)
module.exports = { name: 'a' }

// b.js
const a = require('./a')
console.log('b.js 中的 a:', a)
module.exports = { name: 'b' }

// main.js
const a = require('./a')
```

## ES Modules

Node.js 13.2.0 之后支持 ES Modules

### 使用方式

**方式1**：文件使用 `.mjs` 扩展名

```js [module.mjs]
export const name = 'ES Module'
export function hello() {
  console.log('Hello')
}
```

**方式2**：在 package.json 中设置 `"type": "module"`

```json [package.json]
{
  "type": "module"
}
```

```js [index.js]
import { name, hello } from './module.js'

console.log(name)
hello()
```

### CommonJS 与 ES Modules 的区别

| 特性 | CommonJS | ES Modules |
|------|----------|-----------|
| 语法 | require/module.exports | import/export |
| 加载方式 | 同步 | 异步 |
| 动态导入 | 支持 | import() |
| 值拷贝 | 值拷贝 | 实时映射 |
| this 指向 | 指向 module.exports | undefined |

::: tip 提示
- 模块内部数据是私有的，只有通过 exports 暴露的数据才能被外部访问
- 模块会被缓存，多次 require 同一个模块只会加载一次
- 推荐使用 CommonJS 规范，兼容性更好

:::
