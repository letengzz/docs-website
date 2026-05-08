# ES8

ECMAScript 2017（ES8）于 2017 年 6 月发布。

- 官方规范：https://262.ecma-international.org/8.0/

## async/await

### async 函数

```javascript [async.js]
async function fetchData() {
  return 'data'
}

fetchData().then(data => console.log(data))
```

### await 表达式

```javascript [await.js]
async function fetchData() {
  const response = await fetch('/api/users')
  const data = await response.json()
  return data
}
```

### 错误处理

```javascript [error.js]
async function fetchData() {
  try {
    const response = await fetch('/api/users')
    const data = await response.json()
    return data
  } catch (error) {
    console.error('请求失败:', error)
  }
}
```

### 并发请求

```javascript [concurrent.js]
async function fetchAll() {
  const [users, posts] = await Promise.all([
    fetch('/api/users').then(res => res.json()),
    fetch('/api/posts').then(res => res.json())
  ])
  
  return { users, posts }
}
```

## Object.values()

```javascript [values.js]
const obj = { a: 1, b: 2, c: 3 }

const values = Object.values(obj)
console.log(values)  // [1, 2, 3]
```

## Object.entries()

```javascript [entries.js]
const obj = { a: 1, b: 2, c: 3 }

const entries = Object.entries(obj)
console.log(entries)  // [['a', 1], ['b', 2], ['c', 3]]

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
console.log(descriptors)
```

## String.prototype.padStart()

```javascript [padStart.js]
console.log('5'.padStart(2, '0'))    // '05'
console.log('123'.padStart(5, '0'))  // '00123'
console.log('abc'.padStart(5))       // '  abc'
```

## String.prototype.padEnd()

```javascript [padEnd.js]
console.log('5'.padEnd(2, '0'))      // '50'
console.log('123'.padEnd(5, '0'))    // '12300'
console.log('abc'.padEnd(5))         // 'abc  '
```

## 尾逗号

```javascript [trailing-comma.js]
// 函数参数
function fn(
  a,
  b,
  c,
) {}

// 数组
const arr = [
  1,
  2,
  3,
]

// 对象
const obj = {
  a: 1,
  b: 2,
  c: 3,
}
```

## SharedArrayBuffer 和 Atomics

```javascript [shared.js]
// 创建共享内存
const buffer = new SharedArrayBuffer(1024)
const array = new Int32Array(buffer)

// 原子操作
Atomics.store(array, 0, 42)
Atomics.load(array, 0)
```

::: tip 提示
- async/await 让异步代码更简洁
- Object.values/entries 方便遍历对象
- padStart/padEnd 用于字符串填充
:::
