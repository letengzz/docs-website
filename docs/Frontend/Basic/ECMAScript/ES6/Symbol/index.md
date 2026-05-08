# Symbol

Symbol 是 ES6 引入的一种新的原始数据类型，表示独一无二的值。

## 基本用法

```javascript [basic.js]
const s1 = Symbol()
const s2 = Symbol('description')

console.log(typeof s1)  // symbol
console.log(s1 === s2)  // false
```

## Symbol 描述

```javascript [description.js]
const s1 = Symbol('name')
const s2 = Symbol('name')

console.log(s1 === s2)  // false
console.log(s1.toString())  // Symbol(name)
```

## 作为对象键

```javascript [object-key.js]
const name = Symbol('name')
const age = Symbol('age')

const person = {
  [name]: '张三',
  [age]: 25
}

console.log(person[name])  // 张三
```

## 隐藏属性

```javascript [hidden.js]
const obj = {
  [Symbol('id')]: 123,
  name: '张三'
}

console.log(Object.keys(obj))  // ['name']
console.log(Object.getOwnPropertySymbols(obj))  // [Symbol(id)]
```

## Symbol.for()

```javascript [for.js]
const s1 = Symbol.for('name')
const s2 = Symbol.for('name')

console.log(s1 === s2)  // true
```

## Symbol.keyFor()

```javascript [keyFor.js]
const s = Symbol.for('name')

console.log(Symbol.keyFor(s))  // 'name'
```

## 内置 Symbol

### Symbol.iterator

```javascript [iterator.js]
const arr = [1, 2, 3]
const iterator = arr[Symbol.iterator]()

console.log(iterator.next())  // { value: 1, done: false }
console.log(iterator.next())  // { value: 2, done: false }
console.log(iterator.next())  // { value: 3, done: false }
console.log(iterator.next())  // { value: undefined, done: true }
```

### Symbol.hasInstance

```javascript [hasInstance.js]
class MyClass {
  static [Symbol.hasInstance](instance) {
    return Array.isArray(instance)
  }
}

console.log([] instanceof MyClass)  // true
```

### Symbol.toStringTag

```javascript [toStringTag.js]
class Person {
  get [Symbol.toStringTag]() {
    return 'Person'
  }
}

const p = new Person()
console.log(Object.prototype.toString.call(p))  // [object Person]
```

::: tip 提示
- Symbol 值唯一，适合作为对象键
- Symbol.for() 创建共享 Symbol
- 内置 Symbol 用于自定义对象行为
:::
