# JavaScript ES6+ 新特性

## let 和 const

```javascript [let-const.js]
// let - 块级作用域
if (true) {
  let x = 10
  console.log(x)  // 10
}
// console.log(x)  // ReferenceError

// const - 常量
const PI = 3.14159
// PI = 3  // TypeError

// 对象属性可修改
const obj = { name: '张三' }
obj.name = '李四'  // 允许
```

## 解构赋值

```javascript [destructuring.js]
// 数组解构
const [a, b, ...rest] = [1, 2, 3, 4, 5]
console.log(a, b, rest)  // 1 2 [3, 4, 5]

// 对象解构
const { name, age, city = '北京' } = { name: '张三', age: 25 }
console.log(name, age, city)  // 张三 25 北京

// 重命名
const { name: userName } = { name: '张三' }
console.log(userName)  // 张三

// 函数参数解构
function greet({ name, age }) {
  console.log(`你好，${name}，今年${age}岁`)
}

greet({ name: '张三', age: 25 })

// 嵌套解构
const user = {
  name: '张三',
  address: { city: '北京', district: '朝阳' }
}
const { address: { city } } = user
console.log(city)  // 北京
```

## 模板字符串

```javascript [template-literal.js]
const name = '张三'
const age = 25

// 基础用法
console.log(`你好，我是${name}，今年${age}岁`)

// 多行字符串
const html = `
  <div class="user">
    <h1>${name}</h1>
    <p>${age}岁</p>
  </div>
`

// 表达式
console.log(`1 + 2 = ${1 + 2}`)
console.log(`随机数：${Math.random()}`)

// 标签模板
function highlight(strings, ...values) {
  return strings.reduce((result, str, i) => {
    return result + str + (values[i] ? `<mark>${values[i]}</mark>` : '')
  }, '')
}

console.log(highlight`用户${name}年龄${age}`)
```

## 箭头函数

```javascript [arrow-function.js]
// 基础语法
const add = (a, b) => a + b

// 单参数
const square = x => x * x

// 无参数
const getRandom = () => Math.random()

// 返回对象
const createUser = (name, age) => ({ name, age })

// this 绑定
class Timer {
  constructor() {
    this.seconds = 0
    setInterval(() => {
      this.seconds++  // this 指向 Timer 实例
    }, 1000)
  }
}
```

## 类

```javascript [class.js]
// 基础类
class Person {
  constructor(name, age) {
    this.name = name
    this.age = age
  }

  greet() {
    console.log(`你好，我是${this.name}`)
  }

  static create(name, age) {
    return new Person(name, age)
  }
}

// 继承
class Student extends Person {
  constructor(name, age, grade) {
    super(name, age)
    this.grade = grade
  }

  // 重写方法
  greet() {
    console.log(`你好，我是${this.name}，${this.grade}年级`)
  }

  // getter
  get isAdult() {
    return this.age >= 18
  }

  // setter
  set grade(value) {
    if (value < 1 || value > 12) {
      throw new Error('年级必须在 1-12 之间')
    }
    this._grade = value
  }
}

const student = new Student('张三', 15, 9)
student.greet()
console.log(student.isAdult)  // false
```

## 模块

```javascript [modules.js]
// 导出
// math.js
export function add(a, b) { return a + b }
export function subtract(a, b) { return a - b }
export const PI = 3.14159

// 默认导出
export default class Calculator {
  // ...
}

// 导入
// app.js
import Calculator, { add, subtract, PI } from './math.js'

// 重命名导入
import { add as plus } from './math.js'

// 命名空间导入
import * as Math from './math.js'

// 动态导入
async function loadModule() {
  const math = await import('./math.js')
  return math.add(1, 2)
}
```

## Promise

```javascript [promise.js]
// 创建 Promise
const promise = new Promise((resolve, reject) => {
  setTimeout(() => resolve('成功'), 1000)
})

// 使用
promise
  .then(result => console.log(result))
  .catch(error => console.error(error))
  .finally(() => console.log('完成'))

// async/await
async function fetchData() {
  try {
    const response = await fetch('/api/data')
    return await response.json()
  } catch (error) {
    console.error(error)
  }
}
```

## Symbol

```javascript [symbol.js]
// 创建 Symbol
const sym1 = Symbol('description')
const sym2 = Symbol('description')
console.log(sym1 === sym2)  // false

// 对象属性
const user = {
  [Symbol('id')]: 1,
  name: '张三'
}

// 全局 Symbol
const globalSym = Symbol.for('global')
console.log(Symbol.for('global') === globalSym)  // true

// 内置 Symbol
const iterable = {
  *[Symbol.iterator]() {
    yield 1
    yield 2
    yield 3
  }
}

for (const value of iterable) {
  console.log(value)
}
```

## Map 和 Set

```javascript [map-set.js]
// Map
const map = new Map()
map.set('name', '张三')
map.set('age', 25)

console.log(map.get('name'))  // 张三
console.log(map.size)         // 2

for (const [key, value] of map) {
  console.log(key, value)
}

// Set
const set = new Set([1, 2, 3, 3, 4, 5])
console.log(set.size)  // 5

set.add(6)
set.delete(1)
console.log(set.has(2))  // true

// 去重
const arr = [1, 2, 2, 3, 3, 4]
const unique = [...new Set(arr)]
console.log(unique)  // [1, 2, 3, 4]
```

## 展开运算符

```javascript [spread.js]
// 数组展开
const arr1 = [1, 2, 3]
const arr2 = [4, 5, 6]
const merged = [...arr1, ...arr2]
console.log(merged)  // [1, 2, 3, 4, 5, 6]

// 对象展开
const obj1 = { a: 1, b: 2 }
const obj2 = { c: 3, d: 4 }
const mergedObj = { ...obj1, ...obj2 }
console.log(mergedObj)  // { a: 1, b: 2, c: 3, d: 4 }

// 函数参数
function sum(...numbers) {
  return numbers.reduce((a, b) => a + b, 0)
}
console.log(sum(1, 2, 3, 4, 5))  // 15
```

## 可选链和空值合并

```javascript [optional-chaining.js]
// 可选链
const user = {
  profile: {
    name: '张三',
    address: {
      city: '北京'
    }
  }
}

console.log(user?.profile?.address?.city)  // 北京
console.log(user?.profile?.email)          // undefined

// 函数调用
const fn = user?.getInfo?.()

// 空值合并
const value = null ?? '默认值'
console.log(value)  // 默认值

const value2 = 0 ?? '默认值'
console.log(value2)  // 0

// 结合使用
const city = user?.profile?.address?.city ?? '未知城市'
```

## ES2020+ 新特性

```javascript [es2020-plus.js]
// BigInt
const bigInt = 9007199254740991n
console.log(bigInt + 1n)  // 9007199254740992n

// dynamic import
async function loadModule() {
  const module = await import('./module.js')
  module.default()
}

// globalThis
console.log(globalThis === window)  // true (浏览器)

// Promise.allSettled
const results = await Promise.allSettled([
  Promise.resolve(1),
  Promise.reject(new Error('失败')),
  Promise.resolve(3)
])

// 可选链
const obj = { a: { b: { c: 1 } } }
console.log(obj?.a?.b?.c)  // 1

// 空值合并
const value = null ?? 'default'
console.log(value)  // 'default'

// String.matchAll
const str = 'Hello World'
const matches = [...str.matchAll(/[A-Z]/g)]
console.log(matches)

// for...in 顺序保证
const obj2 = { 2: 'a', 1: 'b', 3: 'c' }
for (const key in obj2) {
  console.log(key)  // 1, 2, 3
}
```

::: tip 提示
- 优先使用 const，需要重新赋值时使用 let
- 使用解构赋值简化代码
- 使用模板字符串替代字符串拼接
- 使用可选链和空值合并处理嵌套属性
:::
