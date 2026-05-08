# Stream 流模块

Stream（流）是 Node.js 中处理流式数据的抽象接口。许多内置模块都实现了 Stream 接口。

## 什么是 Stream

Stream 是一种处理连续数据的方式，可以逐块处理数据，而不是一次性加载全部数据到内存。

### Stream 的优势

- **内存效率**：不需要一次性加载大量数据到内存
- **时间效率**：可以立即开始处理数据，无需等待全部数据加载
- **组合性**：可以通过管道连接多个 Stream

## Stream 的类型

### 1. Readable（可读流）

用于读取数据

```js [readable.js]
const fs = require('fs')

// 创建可读流
const readable = fs.createReadStream('./large-file.txt', {
  highWaterMark: 64 * 1024, // 64KB
  encoding: 'utf8'
})

// 监听数据事件
readable.on('data', (chunk) => {
  console.log('收到数据块:', chunk.length)
})

// 监听结束事件
readable.on('end', () => {
  console.log('读取完成')
})

// 监听错误事件
readable.on('error', (err) => {
  console.error('读取错误:', err)
})
```

### 2. Writable（可写流）

用于写入数据

```js [writable.js]
const fs = require('fs')

// 创建可写流
const writable = fs.createWriteStream('./output.txt', {
  flags: 'a', // 追加模式
  encoding: 'utf8'
})

// 写入数据
writable.write('第一行数据\n')
writable.write('第二行数据\n')

// 结束写入
writable.end('最后一行数据', () => {
  console.log('写入完成')
})

// 监听错误
writable.on('error', (err) => {
  console.error('写入错误:', err)
})
```

### 3. Duplex（双工流）

既可读又可写

```js [duplex.js]
const { Duplex } = require('stream')

const duplexStream = new Duplex({
  read(size) {
    // 实现读取逻辑
    this.push('some data')
    this.push(null) // 结束读取
  },
  write(chunk, encoding, callback) {
    // 实现写入逻辑
    console.log('收到数据:', chunk.toString())
    callback()
  }
})
```

### 4. Transform（转换流）

在读写过程中转换数据

```js [transform.js]
const { Transform } = require('stream')

const upperCaseTransform = new Transform({
  transform(chunk, encoding, callback) {
    // 将数据转换为大写
    this.push(chunk.toString().toUpperCase())
    callback()
  }
})

// 使用
const fs = require('fs')
const readable = fs.createReadStream('./input.txt', 'utf8')
const writable = fs.createWriteStream('./output.txt')

readable.pipe(upperCaseTransform).pipe(writable)
```

## pipe() 管道

pipe() 是 Stream 最重要的特性，可以将可读流连接到可写流

### 基本用法

```js [pipe-basic.js]
const fs = require('fs')

// 创建可读流和可写流
const readable = fs.createReadStream('./input.txt')
const writable = fs.createWriteStream('./output.txt')

// 使用管道连接
readable.pipe(writable)

writable.on('finish', () => {
  console.log('文件复制完成')
})
```

### 链式管道

```js [pipe-chain.js]
const fs = require('fs')
const { Transform } = require('stream')

// 创建转换流
const compressTransform = new Transform({
  transform(chunk, encoding, callback) {
    // 模拟压缩处理
    this.push(chunk.toString().replace(/\s+/g, ' '))
    callback()
  }
})

// 链式管道
const readable = fs.createReadStream('./input.txt', 'utf8')
const writable = fs.createWriteStream('./output.txt', 'utf8')

readable
  .pipe(compressTransform)
  .pipe(writable)
  .on('finish', () => {
    console.log('处理完成')
  })
```

## 事件

### Readable 事件

```js [readable-events.js]
const fs = require('fs')
const readable = fs.createReadStream('./file.txt', 'utf8')

// data 事件：收到数据块
readable.on('data', (chunk) => {
  console.log('data:', chunk)
})

// end 事件：数据读取完成
readable.on('end', () => {
  console.log('读取完成')
})

// error 事件：发生错误
readable.on('error', (err) => {
  console.error('错误:', err)
})

// close 事件：流关闭
readable.on('close', () => {
  console.log('流已关闭')
})
```

### Writable 事件

```js [writable-events.js]
const fs = require('fs')
const writable = fs.createWriteStream('./file.txt')

// drain 事件：可以继续写入
writable.on('drain', () => {
  console.log('可以继续写入')
})

// finish 事件：写入完成
writable.on('finish', () => {
  console.log('写入完成')
})

// error 事件：发生错误
writable.on('error', (err) => {
  console.error('错误:', err)
})
```

## 背压（Backpressure）

当写入速度跟不上读取速度时，需要处理背压问题

```js [backpressure.js]
const fs = require('fs')

const readable = fs.createReadStream('./large-file.txt')
const writable = fs.createWriteStream('./output.txt')

// 手动处理背压
readable.on('data', (chunk) => {
  const canContinue = writable.write(chunk)
  
  if (!canContinue) {
    // 暂停读取
    readable.pause()
    console.log('暂停读取')
  }
})

writable.on('drain', () => {
  // 恢复读取
  readable.resume()
  console.log('恢复读取')
})

writable.on('finish', () => {
  console.log('写入完成')
})
```

## 实际应用

### 文件复制

```js [file-copy.js]
const fs = require('fs')

function copyFile(src, dest) {
  const readable = fs.createReadStream(src)
  const writable = fs.createWriteStream(dest)
  
  readable.pipe(writable)
  
  return new Promise((resolve, reject) => {
    writable.on('finish', resolve)
    writable.on('error', reject)
    readable.on('error', reject)
  })
}

// 使用
copyFile('./source.txt', './destination.txt')
  .then(() => console.log('复制完成'))
  .catch(err => console.error('复制失败:', err))
```

### HTTP 流式响应

```js [http-stream.js]
const http = require('http')
const fs = require('fs')

const server = http.createServer((req, res) => {
  const readable = fs.createReadStream('./large-file.txt')
  
  readable.pipe(res)
  
  readable.on('error', (err) => {
    res.statusCode = 500
    res.end('文件读取失败')
  })
})

server.listen(3000, () => {
  console.log('服务器运行在 http://localhost:3000')
})
```

### 数据压缩

```js [compress.js]
const fs = require('fs')
const zlib = require('zlib')

// 创建可读流
const readable = fs.createReadStream('./file.txt')

// 创建压缩流
const gzip = zlib.createGzip()

// 创建可写流
const writable = fs.createWriteStream('./file.txt.gz')

// 管道连接
readable.pipe(gzip).pipe(writable)

writable.on('finish', () => {
  console.log('压缩完成')
})
```

::: tip 提示
- 使用 Stream 处理大文件可以节省大量内存
- pipe() 会自动处理背压问题
- 始终监听 error 事件，避免程序崩溃
- Transform 流适合数据转换场景
:::
