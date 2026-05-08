# ES12+

ECMAScript 2021+ 包含了 ES12（2021）、ES13（2022）、ES14（2023）及更新版本的特性。

## ES12（2021）

### String.prototype.replaceAll()

```javascript [replaceAll.js]
const str = 'a-b-c-d'

console.log(str.replaceAll('-', '_'))  // 'a_b_c_d'
```

### Promise.any()

```javascript [any.js]
const p1 = Promise.reject('错误1')
const p2 = Promise.reject('错误2')
const p3 = Promise.resolve('成功')

Promise.any([p1, p2, p3]).then(value => {
  console.log(value)  // '成功'
})
```

### WeakRef

```javascript [weakref.js]
const obj = { name: '张三' }
const ref = new WeakRef(obj)

console.log(ref.deref()?.name)  // 张三
```

### FinalizationRegistry

```javascript [finalization.js]
const registry = new FinalizationRegistry(key => {
  console.log(`对象 ${key} 被回收`)
})

const obj = {}
registry.register(obj, 'my-object')
```

### 逻辑赋值操作符

```javascript [logical-assign.js]
let a = 1
let b = 0

a ||= 2  // a = a || 2
b ||= 2  // b = 2

console.log(a, b)  // 1 2

let c = 1
let d = 0

c &&= 2  // c = c && 2
d &&= 2  // d = 0

console.log(c, d)  // 2 0

let e = null
let f = 'value'

e ??= 'default'  // e = e ?? 'default'
f ??= 'default'  // f = f ?? 'default'

console.log(e, f)  // 'default' 'value'
```

### 数字分隔符

```javascript [separator.js]
const num = 1_000_000_000
const big = 1_000_000_000n
const hex = 0xFF_FF_FF_FF

console.log(num)  // 1000000000
```

## ES13（2022）

### 类字段声明

```javascript [class-fields.js]
class Person {
  name = '张三'
  age = 25
  
  static version = '1.0'
}

const p = new Person()
console.log(p.name)  // 张三
console.log(Person.version)  // 1.0
```

### 私有字段和方法

```javascript [private.js]
class Counter {
  #count = 0
  
  increment() {
    this.#count++
    return this.#count
  }
  
  #log() {
    console.log(`Count: ${this.#count}`)
  }
}

const counter = new Counter()
console.log(counter.increment())  // 1
```

### 静态块

```javascript [static-block.js]
class Person {
  static name
  static greeting
  
  static {
    this.name = 'Person'
    this.greeting = 'Hello'
  }
}

console.log(Person.name)      // 'Person'
console.log(Person.greeting)  // 'Hello'
```

### at() 方法

```javascript [at.js]
const arr = [1, 2, 3, 4, 5]

console.log(arr.at(-1))   // 5
console.log(arr.at(-2))   // 4

const str = 'hello'
console.log(str.at(-1))   // 'o'
```

### Object.hasOwn()

```javascript [hasOwn.js]
const obj = { name: '张三' }

console.log(Object.hasOwn(obj, 'name'))  // true
console.log(Object.hasOwn(obj, 'age'))   // false
```

### Error Cause

```javascript [error-cause.js]
async function fetchData() {
  try {
    const response = await fetch('/api/users')
    return await response.json()
  } catch (err) {
    throw new Error('获取数据失败', { cause: err })
  }
}
```

### 正则索引

```javascript [regex.js]
const str = 'abc'
const match = str.match(/b/)

console.log(match.indices)  // [[1, 2]]
```

## ES14（2023）

### Array.findLast() / findLastIndex()

```javascript [findLast.js]
const arr = [1, 2, 3, 4, 5]

console.log(arr.findLast(n => n % 2 === 0))      // 4
console.log(arr.findLastIndex(n => n % 2 === 0)) // 3
```

### Array.toReversed() / toSorted() / toSpliced() / with()

```javascript [array-methods.js]
const arr = [3, 1, 2]

console.log(arr.toReversed())  // [2, 1, 3]
console.log(arr.toSorted())    // [1, 2, 3]
console.log(arr.toSpliced(1, 1))  // [3, 2]
console.log(arr.with(0, 10))   // [10, 1, 2]

// 原数组不变
console.log(arr)  // [3, 1, 2]
```

### Hashbang 语法

```javascript [hashbang.js]
#!/usr/bin/env node

console.log('Hello')
```

### Symbols as WeakMap 键

```javascript [symbol-weakmap.js]
const map = new WeakMap()
const sym = Symbol('key')

const obj = {}
map.set(sym, 'value')
```

### 变更数组副本方法

```javascript [copyWithin.js]
const arr = [1, 2, 3, 4, 5]

// 不改变原数组
const reversed = arr.toReversed()
const sorted = arr.toSorted()
const spliced = arr.toSpliced(0, 1)
const withValue = arr.with(0, 10)
```

::: tip 提示
- ES12+ 持续改进 JavaScript 语言
- 类私有字段提供更好的封装
- 数组副本方法避免副作用
- 逻辑赋值操作符简化代码
:::
