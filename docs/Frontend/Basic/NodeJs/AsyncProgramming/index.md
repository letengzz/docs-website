# Node.js 异步编程

Node.js 的核心特性之一就是异步编程，这使得它能够高效处理大量并发请求。

## 回调函数

### 基本概念

回调函数是异步编程的最基础形式

```js [callback-basic.js]
const fs = require('fs')

// 异步读取文件
fs.readFile('./file.txt', 'utf8', (err, data) => {
  if (err) {
    console.error('读取失败:', err)
    return
  }
  console.log('读取成功:', data)
})

console.log('这行代码会先执行')
```

### 回调地狱

多个异步操作嵌套会导致回调地狱

```js [callback-hell.js]
const fs = require('fs')

// 回调地狱示例
fs.readFile('./file1.txt', 'utf8', (err, data1) => {
  if (err) throw err
  
  fs.readFile('./file2.txt', 'utf8', (err, data2) => {
    if (err) throw err
    
    fs.readFile('./file3.txt', 'utf8', (err, data3) => {
      if (err) throw err
      
      console.log(data1, data2, data3)
    })
  })
})
```

## Promise

### 基本使用

Promise 是异步编程的更好解决方案

```js [promise-basic.js]
const fs = require('fs').promises

// 使用 Promise
fs.readFile('./file.txt', 'utf8')
  .then(data => {
    console.log('读取成功:', data)
  })
  .catch(err => {
    console.error('读取失败:', err)
  })
```

### Promise 链式调用

```js [promise-chain.js]
const fs = require('fs').promises

fs.readFile('./file1.txt', 'utf8')
  .then(data1 => {
    console.log('文件1:', data1)
    return fs.readFile('./file2.txt', 'utf8')
  })
  .then(data2 => {
    console.log('文件2:', data2)
    return fs.readFile('./file3.txt', 'utf8')
  })
  .then(data3 => {
    console.log('文件3:', data3)
  })
  .catch(err => {
    console.error('错误:', err)
  })
```

### Promise.all()

并行执行多个异步操作

```js [promise-all.js]
const fs = require('fs').promises

Promise.all([
  fs.readFile('./file1.txt', 'utf8'),
  fs.readFile('./file2.txt', 'utf8'),
  fs.readFile('./file3.txt', 'utf8')
])
  .then(([data1, data2, data3]) => {
    console.log('文件1:', data1)
    console.log('文件2:', data2)
    console.log('文件3:', data3)
  })
  .catch(err => {
    console.error('错误:', err)
  })
```

### Promise.race()

返回最先完成的 Promise

```js [promise-race.js]
const fs = require('fs').promises

Promise.race([
  fs.readFile('./fast.txt', 'utf8'),
  fs.readFile('./slow.txt', 'utf8')
])
  .then(data => {
    console.log('最先完成:', data)
  })
  .catch(err => {
    console.error('错误:', err)
  })
```

## async/await

### 基本语法

async/await 是 Promise 的语法糖，让异步代码看起来像同步代码

```js [async-basic.js]
const fs = require('fs').promises

async function readFile() {
  try {
    const data = await fs.readFile('./file.txt', 'utf8')
    console.log('读取成功:', data)
  } catch (err) {
    console.error('读取失败:', err)
  }
}

readFile()
```

### 多个异步操作

```js [async-multiple.js]
const fs = require('fs').promises

async function readMultipleFiles() {
  try {
    const data1 = await fs.readFile('./file1.txt', 'utf8')
    const data2 = await fs.readFile('./file2.txt', 'utf8')
    const data3 = await fs.readFile('./file3.txt', 'utf8')
    
    console.log('文件1:', data1)
    console.log('文件2:', data2)
    console.log('文件3:', data3)
  } catch (err) {
    console.error('错误:', err)
  }
}

readMultipleFiles()
```

### 并行执行

```js [async-parallel.js]
const fs = require('fs').promises

async function readFilesParallel() {
  try {
    // 并行读取，提高效率
    const [data1, data2, data3] = await Promise.all([
      fs.readFile('./file1.txt', 'utf8'),
      fs.readFile('./file2.txt', 'utf8'),
      fs.readFile('./file3.txt', 'utf8')
    ])
    
    console.log('文件1:', data1)
    console.log('文件2:', data2)
    console.log('文件3:', data3)
  } catch (err) {
    console.error('错误:', err)
  }
}

readFilesParallel()
```

## 定时器

### setTimeout

延迟执行

```js [settimeout.js]
// 延迟执行
setTimeout(() => {
  console.log('2秒后执行')
}, 2000)

// 清除定时器
const timerId = setTimeout(() => {
  console.log('这不会执行')
}, 5000)

clearTimeout(timerId)
```

### setInterval

重复执行

```js [setinterval.js]
let count = 0

const intervalId = setInterval(() => {
  count++
  console.log(`执行了 ${count} 次`)
  
  if (count >= 5) {
    clearInterval(intervalId)
    console.log('清除定时器')
  }
}, 1000)
```

### setImmediate

在当前事件循环结束时执行

```js [setimmediate.js]
console.log('首先执行')

setImmediate(() => {
  console.log('在事件循环结束时执行')
})

console.log('然后执行')
```

### process.nextTick

在当前操作完成后立即执行

```js [nexttick.js]
console.log('首先执行')

process.nextTick(() => {
  console.log('在当前操作完成后立即执行')
})

console.log('然后执行')
```

## 事件循环

### 阶段说明

```text
   ┌───────────────────────────┐
┌─>│           timers          │
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │     pending callbacks     │
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │       idle, prepare       │
│  └─────────────┬─────────────┘      ┌───────────────┐
│  ┌─────────────┴─────────────┐      │   incoming:   │
│  │           poll            │<─────┤  connections, │
│  └─────────────┬─────────────┘      │   data, etc.  │
│  ┌─────────────┴─────────────┐      └───────────────┘
│  │           check           │
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
└──┤      close callbacks      │
   └───────────────────────────┘
```

### 执行顺序

```js [event-loop-order.js]
console.log('1. 同步代码')

setTimeout(() => {
  console.log('4. setTimeout')
}, 0)

setImmediate(() => {
  console.log('5. setImmediate')
})

process.nextTick(() => {
  console.log('3. process.nextTick')
})

Promise.resolve().then(() => {
  console.log('2. Promise')
})

console.log('6. 同步代码结束')
```

## 错误处理

### try...catch

```js [error-handling.js]
async function readFile() {
  try {
    const data = await fs.readFile('./not-exist.txt', 'utf8')
    console.log(data)
  } catch (err) {
    console.error('捕获错误:', err.message)
  }
}

readFile()
```

### uncaughtException

捕获未处理的异常

```js [uncaught.js]
process.on('uncaughtException', (err) => {
  console.error('未捕获的异常:', err)
  // 优雅关闭
  process.exit(1)
})

throw new Error('测试错误')
```

### unhandledRejection

捕获未处理的 Promise 拒绝

```js [unhandled-rejection.js]
process.on('unhandledRejection', (reason, promise) => {
  console.error('未处理的 Promise 拒绝:', reason)
})

Promise.reject(new Error('测试拒绝'))
```

## 实际应用

### 封装工具函数

```js [utils.js]
const fs = require('fs').promises

// 读取 JSON 文件
async function readJSON(filePath) {
  const data = await fs.readFile(filePath, 'utf8')
  return JSON.parse(data)
}

// 写入 JSON 文件
async function writeJSON(filePath, data) {
  const json = JSON.stringify(data, null, 2)
  await fs.writeFile(filePath, json, 'utf8')
}

module.exports = { readJSON, writeJSON }
```

### 并发控制

```js [concurrency.js]
async function concurrentLimit(tasks, limit) {
  const results = []
  const executing = []
  
  for (const task of tasks) {
    const promise = task().then(result => {
      executing.splice(executing.indexOf(promise), 1)
      return result
    })
    
    results.push(promise)
    executing.push(promise)
    
    if (executing.length >= limit) {
      await Promise.race(executing)
    }
  }
  
  return Promise.all(results)
}

// 使用
const tasks = Array.from({ length: 10 }, (_, i) => () => 
  fetch(`https://api.example.com/data/${i}`)
)

concurrentLimit(tasks, 3)
  .then(results => console.log('全部完成'))
```

::: tip 提示
- 优先使用 async/await 语法
- 使用 Promise.all() 并行执行独立操作
- 始终处理错误情况
- 注意事件循环的执行顺序
:::
