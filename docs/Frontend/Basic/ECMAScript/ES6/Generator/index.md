# 生成器

生成器是 ES6 引入的一种特殊函数，可以暂停和恢复执行。

## 基本语法

### 定义生成器

```javascript [basic.js]
function* generator() {
  yield 1
  yield 2
  yield 3
}

const gen = generator()

console.log(gen.next())  // { value: 1, done: false }
console.log(gen.next())  // { value: 2, done: false }
console.log(gen.next())  // { value: 3, done: false }
console.log(gen.next())  // { value: undefined, done: true }
```

## yield 表达式

### 基本用法

```javascript [yield.js]
function* count() {
  yield 1
  yield 2
  yield 3
}

const gen = count()

for (const value of gen) {
  console.log(value)  // 1, 2, 3
}
```

### 传递参数

```javascript [yield-param.js]
function* greet() {
  const name = yield '请输入名字'
  yield `Hello, ${name}`
}

const gen = greet()

console.log(gen.next().value)       // 请输入名字
console.log(gen.next('张三').value)  // Hello, 张三
```

## 生成器委托

### yield*

```javascript [yield-star.js]
function* inner() {
  yield 2
  yield 3
}

function* outer() {
  yield 1
  yield* inner()
  yield 4
}

const gen = outer()

for (const value of gen) {
  console.log(value)  // 1, 2, 3, 4
}
```

## 实际应用

### 异步流控制

```javascript [async.js]
function* fetchData() {
  const userId = yield fetch('/api/user-id')
  const user = yield fetch(`/api/users/${userId}`)
  return user
}

// 配合 Promise
function run(generatorFn) {
  const gen = generatorFn()
  
  function handle(result) {
    if (result.done) return Promise.resolve(result.value)
    
    return Promise.resolve(result.value)
      .then(res => handle(gen.next(res)))
      .catch(err => handle(gen.throw(err)))
  }
  
  return handle(gen.next())
}
```

### 无限序列

```javascript [infinite.js]
function* fibonacci() {
  let a = 0, b = 1
  
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
console.log(fib.next().value)  // 3
```

### ID 生成器

```javascript [id-generator.js]
function* createIdGenerator(start = 1) {
  let id = start
  
  while (true) {
    yield id++
  }
}

const generateId = createIdGenerator()

console.log(generateId.next().value)  // 1
console.log(generateId.next().value)  // 2
console.log(generateId.next().value)  // 3
```

## 生成器方法

### return()

```javascript [return.js]
function* gen() {
  yield 1
  yield 2
  yield 3
}

const g = gen()

console.log(g.next())     // { value: 1, done: false }
console.log(g.return(10)) // { value: 10, done: true }
console.log(g.next())     // { value: undefined, done: true }
```

### throw()

```javascript [throw.js]
function* gen() {
  try {
    yield 1
  } catch (e) {
    console.log('捕获错误:', e)
  }
}

const g = gen()

console.log(g.next())        // { value: 1, done: false }
console.log(g.throw('错误')) // 捕获错误: 错误
```

::: tip 提示
- 生成器可以暂停和恢复执行
- yield 用于返回值和接收参数
- 适合异步流控制和无限序列
:::
