# 对象新方法

ES6 为对象添加了多个新方法。

## Object.assign()

```javascript [assign.js]
const target = { a: 1 }
const source1 = { b: 2 }
const source2 = { c: 3 }

Object.assign(target, source1, source2)

console.log(target)  // { a: 1, b: 2, c: 3 }
```

### 浅拷贝

```javascript [clone.js]
const obj = { a: 1, b: { c: 2 } }

const clone = Object.assign({}, obj)

clone.b.c = 3

console.log(obj.b.c)   // 3 (原对象也被修改)
```

### 合并对象

```javascript [merge.js]
const defaults = { timeout: 1000, retries: 3 }
const options = { timeout: 2000 }

const config = Object.assign({}, defaults, options)

console.log(config)  // { timeout: 2000, retries: 3 }
```

## Object.is()

```javascript [is.js]
console.log(Object.is(1, 1))           // true
console.log(Object.is(NaN, NaN))       // true
console.log(Object.is(+0, -0))         // false
console.log(Object.is(1, '1'))         // false
```

## Object.keys()

```javascript [keys.js]
const obj = { a: 1, b: 2, c: 3 }

console.log(Object.keys(obj))  // ['a', 'b', 'c']
```

## Object.values()

```javascript [values.js]
const obj = { a: 1, b: 2, c: 3 }

console.log(Object.values(obj))  // [1, 2, 3]
```

## Object.entries()

```javascript [entries.js]
const obj = { a: 1, b: 2, c: 3 }

console.log(Object.entries(obj))  // [['a', 1], ['b', 2], ['c', 3]]

// 遍历
for (const [key, value] of Object.entries(obj)) {
  console.log(`${key}: ${value}`)
}
```

## Object.getOwnPropertyDescriptors()

```javascript [descriptors.js]
const obj = {
  name: '张三',
  get greeting() {
    return `Hello, ${this.name}`
  }
}

const descriptors = Object.getOwnPropertyDescriptors(obj)

console.log(descriptors.name)
console.log(descriptors.greeting)
```

## Object.setPrototypeOf()

```javascript [setPrototypeOf.js]
const proto = { greet() { console.log('Hello') } }
const obj = {}

Object.setPrototypeOf(obj, proto)

obj.greet()  // Hello
```

## Object.getPrototypeOf()

```javascript [getPrototypeOf.js]
class Person {}

const person = new Person()

console.log(Object.getPrototypeOf(person) === Person.prototype)  // true
```

## Object.freeze()

```javascript [freeze.js]
const obj = { name: '张三' }

Object.freeze(obj)

obj.name = '李四'  // 严格模式报错
obj.age = 25       // 严格模式报错

console.log(Object.isFrozen(obj))  // true
```

## Object.seal()

```javascript [seal.js]
const obj = { name: '张三' }

Object.seal(obj)

obj.name = '李四'  // 可以修改
obj.age = 25       // 严格模式报错

console.log(Object.isSealed(obj))  // true
```

## Object.preventExtensions()

```javascript [preventExtensions.js]
const obj = { name: '张三' }

Object.preventExtensions(obj)

obj.age = 25  // 严格模式报错

console.log(Object.isExtensible(obj))  // false
```

::: tip 提示
- Object.assign() 用于合并对象
- Object.is() 比 === 更严格
- Object.entries() 方便遍历对象
- freeze/seal/preventExtensions 用于限制对象修改
:::
