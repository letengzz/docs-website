# JavaScript 函数详解

## 函数定义

### 函数声明

```javascript [function-declaration.js]
// 函数声明（有提升）
function add(a, b) {
  return a + b
}

console.log(add(2, 3))  // 5

// 函数表达式（无提升）
const subtract = function(a, b) {
  return a - b
}

// 命名函数表达式
const multiply = function mul(a, b) {
  return a * b
}
```

### 箭头函数

```javascript [arrow-function.js]
// 基础箭头函数
const add = (a, b) => a + b

// 单参数可省略括号
const square = x => x * x

// 无参数
const getRandom = () => Math.random()

// 多行语句
const divide = (a, b) => {
  if (b === 0) {
    throw new Error('除数不能为 0')
  }
  return a / b
}

// 返回对象（需要括号）
const createUser = (name, age) => ({ name, age })
```

### Function 构造函数

```javascript [function-constructor.js]
const add = new Function('a', 'b', 'return a + b')
console.log(add(2, 3))  // 5

// 不推荐使用（性能差、安全问题）
```

## 函数参数

### 默认参数

```javascript [default-params.js]
// 基础默认参数
function greet(name = '匿名用户') {
  console.log(`你好，${name}`)
}

greet()           // 你好，匿名用户
greet('张三')     // 你好，张三

// 表达式默认值
function createId(prefix = 'id', timestamp = Date.now()) {
  return `${prefix}_${timestamp}`
}

// 解构默认参数
function fetchUser({ id = 1, fields = ['name', 'email'] } = {}) {
  console.log(id, fields)
}

fetchUser()                    // 1 ['name', 'email']
fetchUser({ id: 2 })           // 2 ['name', 'email']
```

### 剩余参数

```javascript [rest-params.js]
// 剩余参数
function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0)
}

console.log(sum(1, 2, 3, 4, 5))  // 15

// 与普通参数结合
function greet(greeting, ...names) {
  return `${greeting}, ${names.join(' 和 ')}!`
}

console.log(greet('你好', '张三', '李四', '王五'))
// 你好，张三 和 李四 和 王五!
```

### arguments 对象

```javascript [arguments.js]
// arguments 对象（类数组）
function showArgs() {
  console.log(arguments)
  console.log(arguments.length)
  console.log(arguments[0])
  
  // 转为数组
  const args = Array.from(arguments)
  console.log(args)
}

showArgs(1, 2, 3)

// 箭头函数没有 arguments
// 使用剩余参数替代
const arrowFunc = (...args) => {
  console.log(args)
}
```

## this 指向

```javascript [this.js]
// 全局作用域
console.log(this === window)  // true（浏览器）

// 对象方法
const user = {
  name: '张三',
  greet() {
    console.log(this.name)
  }
}

user.greet()  // 张三

// 箭头函数 this
const user2 = {
  name: '李四',
  greet: () => {
    console.log(this.name)  // undefined（箭头函数没有自己的 this）
  }
}

user2.greet()

// 改变 this 指向
const obj = { name: '对象' }

function showName() {
  console.log(this.name)
}

showName.call(obj)       // 对象
showName.apply(obj)      // 对象
const bound = showName.bind(obj)
bound()                  // 对象
```

## 高阶函数

```javascript [higher-order.js]
// 函数作为参数
function forEach(arr, callback) {
  for (let i = 0; i < arr.length; i++) {
    callback(arr[i], i, arr)
  }
}

forEach([1, 2, 3], (item, index) => {
  console.log(`${index}: ${item}`)
})

// 函数作为返回值
function multiplyBy(factor) {
  return function(number) {
    return number * factor
  }
}

const double = multiplyBy(2)
const triple = multiplyBy(3)

console.log(double(5))  // 10
console.log(triple(5))  // 15
```

## 回调函数

```javascript [callback.js]
// 同步回调
function processData(data, callback) {
  const result = data.map(item => item * 2)
  callback(result)
}

processData([1, 2, 3], (result) => {
  console.log(result)  // [2, 4, 6]
})

// 异步回调
function fetchData(callback) {
  setTimeout(() => {
    callback({ name: '张三', age: 25 })
  }, 1000)
}

fetchData((data) => {
  console.log(data)
})

// 回调地狱（避免）
doSomething((result1) => {
  doSomethingElse(result1, (result2) => {
    doThirdThing(result2, (result3) => {
      console.log(result3)
    })
  })
})
```

## 闭包

```javascript [closure.js]
// 基础闭包
function createCounter() {
  let count = 0
  return {
    increment: () => ++count,
    decrement: () => --count,
    getCount: () => count
  }
}

const counter = createCounter()
console.log(counter.increment())  // 1
console.log(counter.increment())  // 2
console.log(counter.getCount())   // 2

// 函数工厂
function createMultiplier(factor) {
  return (number) => number * factor
}

const double = createMultiplier(2)
const triple = createMultiplier(3)

console.log(double(5))  // 10
console.log(triple(5))  // 15

// 防抖函数
function debounce(func, delay) {
  let timer
  return function(...args) {
    clearTimeout(timer)
    timer = setTimeout(() => func.apply(this, args), delay)
  }
}

// 节流函数
function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}
```

## 递归函数

```javascript [recursion.js]
// 阶乘
function factorial(n) {
  if (n <= 1) return 1
  return n * factorial(n - 1)
}

console.log(factorial(5))  // 120

// 斐波那契数列
function fibonacci(n) {
  if (n <= 1) return n
  return fibonacci(n - 1) + fibonacci(n - 2)
}

console.log(fibonacci(10))  // 55

// 优化：记忆化
function memoize(fn) {
  const cache = {}
  return function(...args) {
    const key = JSON.stringify(args)
    if (cache[key]) return cache[key]
    const result = fn.apply(this, args)
    cache[key] = result
    return result
  }
}

const memoFib = memoize(fibonacci)
console.log(memoFib(50))  // 快速计算
```

## 立即执行函数

```javascript [iife.js]
// 基础 IIFE
(function() {
  console.log('立即执行')
})()

// 带参数
(function(name) {
  console.log(`你好，${name}`)
})('张三')

// 箭头函数 IIFE
(() => {
  console.log('箭头函数立即执行')
})()

// 模块化
const module = (function() {
  let privateVar = '私有变量'
  
  return {
    getPrivate: () => privateVar,
    setPrivate: (value) => { privateVar = value }
  }
})()
```

## 生成器函数

```javascript [generator.js]
// 基础生成器
function* countUpTo(max) {
  for (let i = 1; i <= max; i++) {
    yield i
  }
}

const counter = countUpTo(3)
console.log(counter.next())  // { value: 1, done: false }
console.log(counter.next())  // { value: 2, done: false }
console.log(counter.next())  // { value: 3, done: false }
console.log(counter.next())  // { value: undefined, done: true }

// for...of 遍历
for (let num of countUpTo(3)) {
  console.log(num)
}

// 无限序列
function* fibonacci() {
  let [a, b] = [0, 1]
  while (true) {
    yield a
    ;[a, b] = [b, a + b]
  }
}

const fib = fibonacci()
console.log(fib.next().value)  // 0
console.log(fib.next().value)  // 1
console.log(fib.next().value)  // 1
console.log(fib.next().value)  // 2
```

## async/await 函数

```javascript [async-await.js]
// 基础用法
async function fetchData() {
  try {
    const response = await fetch('https://api.example.com/data')
    const data = await response.json()
    return data
  } catch (error) {
    console.error('请求失败:', error)
    throw error
  }
}

// 并行请求
async function fetchMultiple() {
  const [users, posts] = await Promise.all([
    fetch('https://api.example.com/users').then(r => r.json()),
    fetch('https://api.example.com/posts').then(r => r.json())
  ])
  return { users, posts }
}

// 错误处理
async function safeFetch(url) {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('请求失败:', error.message)
    return null
  }
}
```

::: tip 提示
- 优先使用箭头函数，除非需要 this 或 arguments
- 使用默认参数替代 `||` 判断
- 使用剩余参数替代 arguments
- 异步代码优先使用 async/await
:::
