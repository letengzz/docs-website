# JavaScript 错误处理

## 错误类型

```javascript [error-types.js]
// SyntaxError - 语法错误
// eval('let a = ')  // SyntaxError

// ReferenceError - 引用错误
// console.log(undefinedVar)  // ReferenceError

// TypeError - 类型错误
// null.method()  // TypeError

// RangeError - 范围错误
// new Array(-1)  // RangeError

// URIError - URI 错误
// decodeURIComponent('%')  // URIError

// EvalError - eval 错误（已废弃）

// InternalError - 内部错误（递归过深）
```

## Error 对象

```javascript [error-object.js]
// 创建错误
const error = new Error('出错了')
console.log(error.name)     // Error
console.log(error.message)  // 出错了
console.log(error.stack)    // 堆栈信息

// 自定义错误
class ValidationError extends Error {
  constructor(message, field) {
    super(message)
    this.name = 'ValidationError'
    this.field = field
  }
}

class AuthenticationError extends Error {
  constructor(message) {
    super(message)
    this.name = 'AuthenticationError'
    this.code = 401
  }
}

// 使用自定义错误
function validateEmail(email) {
  if (!email) {
    throw new ValidationError('邮箱不能为空', 'email')
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new ValidationError('邮箱格式不正确', 'email')
  }
  return true
}
```

## try...catch...finally

```javascript [try-catch.js]
// 基础用法
try {
  const result = JSON.parse('invalid json')
} catch (error) {
  console.error('解析失败:', error.message)
}

// 带 finally
try {
  console.log('尝试执行')
} catch (error) {
  console.error('捕获错误:', error.message)
} finally {
  console.log('总是执行')
}

// 嵌套 try-catch
try {
  try {
    throw new Error('内部错误')
  } catch (inner) {
    console.error('内部捕获:', inner.message)
    throw new Error('外部错误')
  }
} catch (outer) {
  console.error('外部捕获:', outer.message)
}
```

## 异步错误处理

```javascript [async-error.js]
// Promise 错误
fetch('https://api.example.com/data')
  .then(response => response.json())
  .catch(error => console.error('请求失败:', error))

// async/await 错误
async function fetchData() {
  try {
    const response = await fetch('https://api.example.com/data')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('请求失败:', error.message)
    throw error
  }
}

// 多个异步操作
async function fetchMultiple() {
  try {
    const [users, posts] = await Promise.all([
      fetch('/api/users').then(r => r.json()),
      fetch('/api/posts').then(r => r.json())
    ])
    return { users, posts }
  } catch (error) {
    console.error('批量请求失败:', error)
    return { users: [], posts: [] }
  }
}

// Promise.allSettled
async function fetchAllSettled() {
  const results = await Promise.allSettled([
    fetch('/api/users').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
    fetch('/api/comments').then(r => r.json())
  ])

  results.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      console.log(`请求 ${index} 成功:`, result.value)
    } else {
      console.error(`请求 ${index} 失败:`, result.reason)
    }
  })
}
```

## 全局错误处理

```javascript [global-error.js]
// 浏览器全局错误
window.addEventListener('error', (event) => {
  console.error('全局错误:', event.error)
  // 上报错误
  reportError(event.error)
})

// 未处理的 Promise 拒绝
window.addEventListener('unhandledrejection', (event) => {
  console.error('未处理的 Promise 拒绝:', event.reason)
  event.preventDefault()
})

// Node.js 全局错误
// process.on('uncaughtException', (error) => {
//   console.error('未捕获异常:', error)
//   process.exit(1)
// })

// process.on('unhandledRejection', (reason) => {
//   console.error('未处理的 Promise 拒绝:', reason)
// })
```

## 错误处理模式

```javascript [error-patterns.js]
// 错误码模式
const ErrorCodes = {
  VALIDATION_ERROR: 1001,
  AUTH_ERROR: 1002,
  NETWORK_ERROR: 1003
}

class AppError extends Error {
  constructor(message, code) {
    super(message)
    this.name = 'AppError'
    this.code = code
  }
}

// 错误处理中间件
function errorHandler(error, req, res, next) {
  if (error instanceof AppError) {
    res.status(400).json({
      error: error.message,
      code: error.code
    })
  } else {
    res.status(500).json({
      error: '服务器内部错误'
    })
  }
}

// 重试机制
async function retry(fn, retries = 3, delay = 1000) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (i === retries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
}

// 使用重试
async function fetchWithRetry() {
  return retry(async () => {
    const response = await fetch('https://api.example.com/data')
    return response.json()
  }, 3, 2000)
}
```

## 错误上报

```javascript [error-reporting.js]
function reportError(error) {
  const errorInfo = {
    message: error.message,
    stack: error.stack,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: Date.now()
  }

  // 使用 sendBeacon 确保错误上报
  navigator.sendBeacon('/api/error-report', JSON.stringify(errorInfo))
}

// 错误收集器
class ErrorCollector {
  constructor() {
    this.errors = []
  }

  collect(error) {
    this.errors.push({
      message: error.message,
      stack: error.stack,
      timestamp: Date.now()
    })

    // 达到阈值时上报
    if (this.errors.length >= 10) {
      this.flush()
    }
  }

  flush() {
    if (this.errors.length > 0) {
      navigator.sendBeacon('/api/errors', JSON.stringify(this.errors))
      this.errors = []
    }
  }
}

const collector = new ErrorCollector()

// 页面卸载前上报
window.addEventListener('beforeunload', () => {
  collector.flush()
})
```

## 调试技巧

```javascript [debugging.js]
// debugger 语句
function problematicFunction(data) {
  debugger  // 断点
  // 处理数据
}

// console 方法
console.log('普通日志')
console.info('信息日志')
console.warn('警告日志')
console.error('错误日志')

// 分组日志
console.group('用户操作')
console.log('点击按钮')
console.log('提交表单')
console.groupEnd()

// 表格输出
console.table([
  { name: '张三', age: 25 },
  { name: '李四', age: 30 }
])

// 性能计时
console.time('操作')
// 执行操作
console.timeEnd('操作')

// 计数
console.count('调用次数')
```

::: tip 提示
- 始终捕获异步操作的错误
- 使用自定义错误类区分错误类型
- 实现全局错误处理和上报机制
- 使用 try-catch 包裹可能出错的代码
:::

::: danger 注意
- 不要吞掉错误，至少要记录日志
- catch 块中避免抛出新的错误
- finally 块中的 return 会覆盖 try/catch 的 return
- 生产环境不要暴露详细错误信息
:::
