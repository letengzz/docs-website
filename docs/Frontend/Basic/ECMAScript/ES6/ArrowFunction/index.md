# 箭头函数

箭头函数是 ES6 引入的一种新的函数语法，使用 `=>` 符号定义。

## 基本语法

### 无参数

```javascript [no-param.js]
const greet = () => {
  console.log('Hello')
}

greet()
```

### 单个参数

```javascript [single-param.js]
const square = x => x * x

console.log(square(5))  // 25
```

### 多个参数

```javascript [multi-param.js]
const add = (a, b) => a + b

console.log(add(1, 2))  // 3
```

### 多行代码

```javascript [multi-line.js]
const calculate = (a, b) => {
  const sum = a + b
  const product = a * b
  return { sum, product }
}

console.log(calculate(2, 3))  // { sum: 5, product: 6 }
```

## this 指向

### 箭头函数的 this

箭头函数没有自己的 `this`，它会捕获定义时所在上下文的 `this`。

```javascript [this.js]
const person = {
  name: '张三',
  greet: function() {
    setTimeout(() => {
      console.log(`Hello, ${this.name}`)  // Hello, 张三
    }, 100)
  }
}

person.greet()
```

### 对比普通函数

```javascript [compare.js]
const person = {
  name: '张三',
  // 普通函数
  greet1() {
    setTimeout(function() {
      console.log(`Hello, ${this.name}`)  // Hello, undefined
    }, 100)
  },
  // 箭头函数
  greet2() {
    setTimeout(() => {
      console.log(`Hello, ${this.name}`)  // Hello, 张三
    }, 100)
  }
}

person.greet1()
person.greet2()
```

## 使用场景

### 数组方法

```javascript [array.js]
const numbers = [1, 2, 3, 4, 5]

const doubled = numbers.map(n => n * 2)
const even = numbers.filter(n => n % 2 === 0)
const sum = numbers.reduce((acc, curr) => acc + curr, 0)

console.log(doubled)  // [2, 4, 6, 8, 10]
console.log(even)     // [2, 4]
console.log(sum)      // 15
```

### 事件处理

```javascript [event.js]
class Button {
  constructor() {
    this.clicked = false
    this.element = document.createElement('button')
    this.element.addEventListener('click', () => {
      this.clicked = true
      console.log('Button clicked')
    })
  }
}
```

### Promise 链

```javascript [promise.js]
fetch('/api/users')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err))
```

## 注意事项

### 不能作为构造函数

```javascript [no-constructor.js]
const Person = (name) => {
  this.name = name
}

const p = new Person('张三')  // TypeError: Person is not a constructor
```

### 没有 arguments

```javascript [no-arguments.js]
const fn = () => {
  console.log(arguments)  // ReferenceError
}

fn(1, 2, 3)
```

使用剩余参数替代：

```javascript [rest-params.js]
const fn = (...args) => {
  console.log(args)  // [1, 2, 3]
}

fn(1, 2, 3)
```

### 没有 prototype

```javascript [no-prototype.js]
const fn = () => {}

console.log(fn.prototype)  // undefined
```

## 返回值

### 隐式返回

```javascript [implicit-return.js]
const add = (a, b) => a + b

// 等同于
const add2 = (a, b) => {
  return a + b
}
```

### 返回对象

```javascript [return-object.js]
const createPerson = (name, age) => ({ name, age })

const person = createPerson('张三', 25)
console.log(person)  // { name: '张三', age: 25 }
```

::: tip 提示
- 箭头函数适合简短的回调函数
- 箭头函数没有自己的 this
- 不能作为构造函数使用
- 没有 arguments 对象
:::
