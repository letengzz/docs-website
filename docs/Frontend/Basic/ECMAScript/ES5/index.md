# ES5

ECMAScript 5（ES5）是 JavaScript 语言的重要版本，于 2009 年发布。

- 官方规范：https://262.ecma-international.org/5.1/
- MDN 文档：https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects

## 严格模式

严格模式是一种限制性更强的 JavaScript 运行模式。

### 启用严格模式

```javascript [strict.js]
// 全局严格模式
'use strict'

// 函数严格模式
function myFunction() {
  'use strict'
  // 严格模式代码
}
```

### 严格模式限制

```javascript [strict-rules.js]
'use strict'

// 变量必须先声明
x = 1  // 报错

// 禁止删除变量
var x = 1
delete x  // 报错

// 禁止使用 with
with (obj) {}  // 报错

// 禁止重复参数名
function fn(a, a) {}  // 报错

// this 指向 undefined
function fn() {
  console.log(this)  // undefined
}
fn()
```

## JSON 对象

ES5 原生支持 JSON 对象。

### JSON.parse()

```javascript [parse.js]
const json = '{"name": "张三", "age": 25}'
const obj = JSON.parse(json)

console.log(obj.name)  // 张三
console.log(obj.age)   // 25
```

### JSON.stringify()

```javascript [stringify.js]
const obj = { name: '张三', age: 25 }
const json = JSON.stringify(obj)

console.log(json)  // {"name":"张三","age":25}

// 格式化输出
console.log(JSON.stringify(obj, null, 2))
```

## 对象方法

### Object.create()

```javascript [create.js]
const person = {
  greet() {
    console.log('Hello')
  }
}

const student = Object.create(person)
student.name = '张三'

student.greet()  // Hello
```

### Object.defineProperty()

```javascript [defineProperty.js]
const obj = {}

Object.defineProperty(obj, 'name', {
  value: '张三',
  writable: false,      // 不可写
  enumerable: true,     // 可枚举
  configurable: false   // 不可配置
})

obj.name = '李四'  // 严格模式报错
```

### Object.defineProperties()

```javascript [defineProperties.js]
const obj = {}

Object.defineProperties(obj, {
  name: {
    value: '张三',
    writable: true
  },
  age: {
    value: 25,
    writable: true
  }
})
```

### Object.keys()

```javascript [keys.js]
const obj = {
  name: '张三',
  age: 25,
  city: '北京'
}

const keys = Object.keys(obj)
console.log(keys)  // ['name', 'age', 'city']
```

### Object.getOwnPropertyDescriptor()

```javascript [getOwnPropertyDescriptor.js]
const obj = { name: '张三' }

const desc = Object.getOwnPropertyDescriptor(obj, 'name')
console.log(desc)
// {
//   value: '张三',
//   writable: true,
//   enumerable: true,
//   configurable: true
// }
```

### Object.getOwnPropertyNames()

```javascript [getOwnPropertyNames.js]
const obj = { name: '张三', age: 25 }

const names = Object.getOwnPropertyNames(obj)
console.log(names)  // ['name', 'age']
```

### Object.preventExtensions()

```javascript [preventExtensions.js]
const obj = { name: '张三' }

Object.preventExtensions(obj)

obj.age = 25  // 严格模式报错
console.log(obj.age)  // undefined
```

### Object.seal()

```javascript [seal.js]
const obj = { name: '张三' }

Object.seal(obj)

// 不能添加新属性
obj.age = 25  // 严格模式报错

// 可以修改现有属性
obj.name = '李四'
```

### Object.freeze()

```javascript [freeze.js]
const obj = { name: '张三' }

Object.freeze(obj)

// 不能添加新属性
obj.age = 25  // 严格模式报错

// 不能修改现有属性
obj.name = '李四'  // 严格模式报错

// 检查是否冻结
console.log(Object.isFrozen(obj))  // true
```

## 数组方法

### Array.isArray()

```javascript [isArray.js]
console.log(Array.isArray([1, 2, 3]))  // true
console.log(Array.isArray({}))         // false
```

### Array.prototype.indexOf()

```javascript [indexOf.js]
const arr = [1, 2, 3, 4, 5]

console.log(arr.indexOf(3))    // 2
console.log(arr.indexOf(6))    // -1
console.log(arr.indexOf(3, 3)) // -1 (从索引 3 开始)
```

### Array.prototype.lastIndexOf()

```javascript [lastIndexOf.js]
const arr = [1, 2, 3, 2, 1]

console.log(arr.lastIndexOf(2))    // 3
console.log(arr.lastIndexOf(2, 2)) // 1 (从索引 2 向前查找)
```

### Array.prototype.forEach()

```javascript [forEach.js]
const arr = [1, 2, 3]

arr.forEach((item, index, array) => {
  console.log(`${index}: ${item}`)
})
// 0: 1
// 1: 2
// 2: 3
```

### Array.prototype.map()

```javascript [map.js]
const arr = [1, 2, 3]

const doubled = arr.map(item => item * 2)
console.log(doubled)  // [2, 4, 6]
```

### Array.prototype.filter()

```javascript [filter.js]
const arr = [1, 2, 3, 4, 5]

const even = arr.filter(item => item % 2 === 0)
console.log(even)  // [2, 4]
```

### Array.prototype.reduce()

```javascript [reduce.js]
const arr = [1, 2, 3, 4, 5]

const sum = arr.reduce((acc, curr) => acc + curr, 0)
console.log(sum)  // 15

// 求最大值
const max = arr.reduce((acc, curr) => Math.max(acc, curr))
console.log(max)  // 5
```

### Array.prototype.reduceRight()

```javascript [reduceRight.js]
const arr = [1, 2, 3]

const result = arr.reduceRight((acc, curr) => acc + curr, '')
console.log(result)  // '321'
```

### Array.prototype.every()

```javascript [every.js]
const arr = [2, 4, 6, 8]

const allEven = arr.every(item => item % 2 === 0)
console.log(allEven)  // true
```

### Array.prototype.some()

```javascript [some.js]
const arr = [1, 2, 3, 4, 5]

const hasEven = arr.some(item => item % 2 === 0)
console.log(hasEven)  // true
```

## Function 方法

### Function.prototype.bind()

```javascript [bind.js]
const person = {
  name: '张三',
  greet() {
    console.log(`Hello, ${this.name}`)
  }
}

const greet = person.greet.bind(person)
greet()  // Hello, 张三

// 绑定参数
function add(a, b) {
  return a + b
}

const add5 = add.bind(null, 5)
console.log(add5(3))  // 8
```

## Date 方法

```javascript [date.js]
const date = new Date()

// ES5 新增方法
console.log(date.toISOString())    // ISO 格式
console.log(date.toJSON())         // JSON 格式
console.log(Date.now())            // 当前时间戳
```

## String 方法

### String.prototype.trim()

```javascript [trim.js]
const str = '  Hello World  '

console.log(str.trim())      // 'Hello World'
console.log(str.trimLeft())  // 'Hello World  '
console.log(str.trimRight()) // '  Hello World'
```

## 模块化开发

### CommonJS 规范

```javascript [commonjs.js]
// 导出模块
module.exports = {
  sum(a, b) { return a + b },
  subtract(a, b) { return a - b }
}

// 导入模块
const math = require('./math')
console.log(math.sum(1, 2))  // 3
```

## ES5 兼容性

ES5 已被所有现代浏览器支持，包括：

- Chrome 23+
- Firefox 21+
- Safari 6+
- Edge 12+
- IE 9+（部分支持）

::: tip 提示
- ES5 是 JavaScript 的重要里程碑
- 严格模式推荐使用
- 数组方法是日常开发常用工具
- 现代项目通常编译到 ES5 以兼容老浏览器
:::
