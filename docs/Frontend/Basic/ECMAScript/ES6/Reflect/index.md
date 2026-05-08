# Reflect

Reflect 是一个内置对象，提供操作对象的方法。

## 基本用法

### 替代 Object 方法

```javascript [basic.js]
const obj = { name: '张三' }

// 替代 Object.defineProperty
Reflect.defineProperty(obj, 'age', { value: 25 })

// 替代 Object.getOwnPropertyDescriptor
const desc = Reflect.getOwnPropertyDescriptor(obj, 'name')

// 替代 Object.keys
const keys = Reflect.ownKeys(obj)
```

## 静态方法

### Reflect.get()

```javascript [get.js]
const obj = { name: '张三' }

console.log(Reflect.get(obj, 'name'))  // 张三
console.log(Reflect.get(obj, 'age', '默认'))  // 默认
```

### Reflect.set()

```javascript [set.js]
const obj = {}

Reflect.set(obj, 'name', '张三')
console.log(obj.name)  // 张三
```

### Reflect.has()

```javascript [has.js]
const obj = { name: '张三' }

console.log(Reflect.has(obj, 'name'))  // true
console.log(Reflect.has(obj, 'age'))   // false
```

### Reflect.deleteProperty()

```javascript [delete.js]
const obj = { name: '张三' }

Reflect.deleteProperty(obj, 'name')
console.log(obj.name)  // undefined
```

### Reflect.construct()

```javascript [construct.js]
class Person {
  constructor(name) {
    this.name = name
  }
}

const person = Reflect.construct(Person, ['张三'])
console.log(person.name)  // 张三
```

### Reflect.apply()

```javascript [apply.js]
function sum(a, b) {
  return a + b
}

console.log(Reflect.apply(sum, null, [1, 2]))  // 3
```

### Reflect.defineProperty()

```javascript [defineProperty.js]
const obj = {}

const success = Reflect.defineProperty(obj, 'name', {
  value: '张三',
  writable: false
})

console.log(success)  // true
```

### Reflect.getPrototypeOf()

```javascript [getPrototypeOf.js]
class Person {}

const person = new Person()

console.log(Reflect.getPrototypeOf(person) === Person.prototype)  // true
```

### Reflect.setPrototypeOf()

```javascript [setPrototypeOf.js]
const obj = {}
const proto = { greet() { console.log('Hello') } }

Reflect.setPrototypeOf(obj, proto)

obj.greet()  // Hello
```

### Reflect.isExtensible()

```javascript [isExtensible.js]
const obj = {}

console.log(Reflect.isExtensible(obj))  // true

Object.preventExtensions(obj)

console.log(Reflect.isExtensible(obj))  // false
```

### Reflect.preventExtensions()

```javascript [preventExtensions.js]
const obj = {}

Reflect.preventExtensions(obj)

console.log(Reflect.isExtensible(obj))  // false
```

### Reflect.getOwnPropertyDescriptor()

```javascript [getOwnPropertyDescriptor.js]
const obj = { name: '张三' }

const desc = Reflect.getOwnPropertyDescriptor(obj, 'name')
console.log(desc)
// { value: '张三', writable: true, enumerable: true, configurable: true }
```

### Reflect.ownKeys()

```javascript [ownKeys.js]
const obj = { name: '张三', [Symbol('id')]: 123 }

console.log(Reflect.ownKeys(obj))  // ['name', Symbol(id)]
```

## 与 Proxy 配合

```javascript [with-proxy.js]
const target = { name: '张三' }

const handler = {
  get(obj, prop, receiver) {
    console.log(`访问: ${prop}`)
    return Reflect.get(obj, prop, receiver)
  },
  set(obj, prop, value, receiver) {
    console.log(`设置: ${prop} = ${value}`)
    return Reflect.set(obj, prop, value, receiver)
  }
}

const proxy = new Proxy(target, handler)

proxy.name = '李四'
console.log(proxy.name)
```

::: tip 提示
- Reflect 提供统一的对象操作 API
- 与 Proxy 方法一一对应
- 推荐优先使用 Reflect 方法
:::
