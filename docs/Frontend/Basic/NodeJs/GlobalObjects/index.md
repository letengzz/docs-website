# Node.js 全局对象

Node.js 提供了一些全局对象和变量，可以在任何地方直接使用。

## global 对象

类似于浏览器中的 window，是 Node.js 的全局对象

```js [global.js]
// 访问全局对象
console.log(global)
console.log(globalThis)
console.log(global === globalThis) // false (Node.js 中)

// 添加全局属性
global.myVar = 'hello'
console.log(global.myVar)
```

## __dirname

当前文件所在目录的绝对路径

```js [dirname.js]
const path = require('path')
const fs = require('fs')

console.log(__dirname)
// 输出: D:\docs-website\docs\Frontend\Basic\NodeJs

// 拼接路径
const filePath = path.join(__dirname, 'data.txt')
console.log(filePath)

// 读取文件
const data = fs.readFileSync(path.join(__dirname, 'data.txt'), 'utf8')
console.log(data)
```

## __filename

当前文件的绝对路径

```js [filename.js]
console.log(__filename)
// 输出: D:\docs-website\docs\Frontend\Basic\NodeJs\GlobalObjects\index.js

// 获取文件名
const path = require('path')
console.log(path.basename(__filename))
// 输出: index.js
```

## module 和 exports

模块系统相关的全局对象

```js [module.js]
// 当前模块信息
console.log(module)

// 模块ID
console.log(module.id)

// 模块是否已加载完成
console.log(module.loaded)

// 模块的父模块
console.log(module.parent)

// 模块路径
console.log(module.paths)
```

## require

用于导入模块

```js [require.js]
// 导入内置模块
const fs = require('fs')
const path = require('path')

// 导入自定义模块
const myModule = require('./myModule')

// 导入JSON文件
const config = require('./config.json')

// 导入Node模块
const express = require('express')
```

## process 对象

提供有关 Node.js 进程的信息和控制

### 基本信息

```js [process-info.js]
// 进程ID
console.log('PID:', process.pid)

// 进程标题
process.title = 'My Node App'

// Node.js 版本
console.log('Node版本:', process.version)

// 平台信息
console.log('平台:', process.platform)
console.log('架构:', process.arch)

// 当前工作目录
console.log('工作目录:', process.cwd())
```

### 环境变量

```js [env.js]
// 访问环境变量
console.log('NODE_ENV:', process.env.NODE_ENV)
console.log('PATH:', process.env.PATH)

// 设置环境变量
process.env.MY_VAR = 'hello'
console.log('MY_VAR:', process.env.MY_VAR)
```

### 命令行参数

```js [argv.js]
// 命令行参数
console.log('参数:', process.argv)

// 示例: node script.js arg1 arg2
// 输出: ['node', 'script.js', 'arg1', 'arg2']

// 获取用户传入的参数
const args = process.argv.slice(2)
console.log('用户参数:', args)
```

### 标准输入输出

```js [stdio.js]
// 标准输出
process.stdout.write('Hello World\n')

// 标准错误
process.stderr.write('Error message\n')

// 标准输入
process.stdin.on('data', (data) => {
  console.log('收到输入:', data.toString())
  process.exit()
})

process.stdin.resume()
```

### 进程事件

```js [process-events.js]
// 退出事件
process.on('exit', (code) => {
  console.log(`进程退出，退出码: ${code}`)
})

// 未捕获异常
process.on('uncaughtException', (err) => {
  console.error('未捕获异常:', err)
  process.exit(1)
})

// 未处理的Promise拒绝
process.on('unhandledRejection', (reason, promise) => {
  console.error('未处理拒绝:', reason)
})

// 信号事件
process.on('SIGINT', () => {
  console.log('收到 SIGINT 信号')
  process.exit()
})
```

### 进程控制

```js [process-control.js]
// 退出进程
process.exit(0)

// 退出码
process.exitCode = 1

// 内存使用
console.log('内存使用:', process.memoryUsage())

// CPU使用
console.log('CPU使用:', process.cpuUsage())

// 下一个tick
process.nextTick(() => {
  console.log('下一个tick执行')
})
```

## console 对象

用于输出信息

```js [console.js]
// 基本输出
console.log('普通日志')
console.info('信息日志')
console.warn('警告日志')
console.error('错误日志')

// 调试输出
console.debug('调试信息')

// 分组
console.group('用户信息')
console.log('姓名: 张三')
console.log('年龄: 25')
console.groupEnd()

// 计时
console.time('操作')
// 执行一些操作
console.timeEnd('操作')

// 表格输出
console.table([
  { name: '张三', age: 25 },
  { name: '李四', age: 30 }
])

// 断言
console.assert(1 === 2, '1不等于2')
```

## 定时器

### setTimeout

```js [settimeout.js]
// 延迟执行
const timerId = setTimeout(() => {
  console.log('2秒后执行')
}, 2000)

// 清除定时器
clearTimeout(timerId)
```

### setInterval

```js [setinterval.js]
// 重复执行
const intervalId = setInterval(() => {
  console.log('每秒执行')
}, 1000)

// 清除定时器
clearInterval(intervalId)
```

### setImmediate

```js [setimmediate.js]
// 在当前事件循环结束时执行
setImmediate(() => {
  console.log('立即执行')
})
```

## URL 和 URLSearchParams

### URL

```js [url.js]
const url = new URL('https://example.com:8080/path?name=张三#section')

console.log(url.href)      // 完整URL
console.log(url.origin)    // 协议+域名+端口
console.log(url.protocol)  // 协议
console.log(url.host)      // 主机名+端口
console.log(url.hostname)  // 主机名
console.log(url.port)      // 端口
console.log(url.pathname)  // 路径
console.log(url.search)    // 查询字符串
console.log(url.hash)      // 哈希
```

### URLSearchParams

```js [urlsearchparams.js]
const params = new URLSearchParams('name=张三&age=25&city=北京')

console.log(params.get('name'))     // 张三
console.log(params.getAll('name'))  // ['张三']
console.log(params.has('age'))      // true

// 遍历
for (const [key, value] of params) {
  console.log(`${key}: ${value}`)
}

// 修改
params.set('age', 26)
params.append('hobby', '读书')
params.delete('city')

console.log(params.toString())
```

## Buffer

Buffer 也是全局可用的

```js [buffer-global.js]
// 创建Buffer
const buf1 = Buffer.from('hello')
const buf2 = Buffer.alloc(10)
const buf3 = Buffer.allocUnsafe(10)

// 转换
console.log(buf1.toString())
console.log(buf1.toJSON())

// 合并
const buf4 = Buffer.concat([buf1, buf2])

// 判断
console.log(Buffer.isBuffer(buf1))
```

::: tip 提示
- `__dirname` 和 `__filename` 是最常用的全局变量
- 使用 `process.env` 管理环境变量
- 始终处理未捕获的异常
- 定时器用完记得清除
:::
