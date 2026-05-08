# EventEmitter 事件模块

EventEmitter 是 Node.js 中处理事件的核心模块，许多内置对象都继承了 EventEmitter。

## 基本使用

### 导入模块

```js [event-basic.js]
const EventEmitter = require('events')

// 创建事件发射器实例
const emitter = new EventEmitter()
```

### 监听和触发事件

```js [event-listen.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

// 监听事件
emitter.on('greet', (name) => {
  console.log(`Hello, ${name}!`)
})

// 触发事件
emitter.emit('greet', '张三')
// 输出: Hello, 张三!
```

## 常用方法

### on() / addListener()

注册事件监听器

```js [on.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

// 方式1：使用 on
emitter.on('data', (data) => {
  console.log('收到数据:', data)
})

// 方式2：使用 addListener（等效于 on）
emitter.addListener('data', (data) => {
  console.log('收到数据:', data)
})
```

### emit()

触发事件

```js [emit.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

emitter.on('event1', () => {
  console.log('事件1触发')
})

emitter.on('event2', (arg1, arg2) => {
  console.log('事件2触发:', arg1, arg2)
})

// 触发事件
emitter.emit('event1')
emitter.emit('event2', '参数1', '参数2')
```

### once()

只监听一次

```js [once.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

emitter.once('init', () => {
  console.log('只执行一次')
})

emitter.emit('init') // 输出: 只执行一次
emitter.emit('init') // 不会输出
```

### off() / removeListener()

移除事件监听器

```js [off.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

function handler() {
  console.log('处理事件')
}

emitter.on('data', handler)

// 移除监听器
emitter.off('data', handler)
// 或者
emitter.removeListener('data', handler)
```

### removeAllListeners()

移除所有监听器

```js [removeAll.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

emitter.on('event1', () => {})
emitter.on('event2', () => {})

// 移除所有监听器
emitter.removeAllListeners()

// 移除指定事件的所有监听器
emitter.removeAllListeners('event1')
```

## 事件参数

### 传递多个参数

```js [event-args.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

emitter.on('user:login', (username, timestamp, ip) => {
  console.log(`用户 ${username} 在 ${timestamp} 从 ${ip} 登录`)
})

emitter.emit('user:login', '张三', new Date().toISOString(), '192.168.1.1')
```

### this 指向

```js [event-this.js]
const EventEmitter = require('events')

class MyEmitter extends EventEmitter {
  constructor() {
    super()
    this.count = 0
  }

  increment() {
    this.count++
    this.emit('incremented', this.count)
  }
}

const myEmitter = new MyEmitter()

myEmitter.on('incremented', function(count) {
  console.log(`计数: ${count}`)
  console.log('this 指向:', this === myEmitter) // true
})

myEmitter.increment()
myEmitter.increment()
```

## 错误处理

### error 事件

```js [error-event.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

// 监听 error 事件
emitter.on('error', (err) => {
  console.error('发生错误:', err.message)
})

// 触发错误事件
emitter.emit('error', new Error('Something went wrong'))
```

### 未捕获的错误

```js [uncaught-error.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

// 如果没有监听 error 事件，会抛出未捕获异常
emitter.emit('error', new Error('Unhandled error'))
// 程序会崩溃
```

## 继承 EventEmitter

### 方式1：ES6 Class

```js [inherit-class.js]
const EventEmitter = require('events')

class MyEmitter extends EventEmitter {
  constructor() {
    super()
  }

  doSomething() {
    this.emit('something', '数据')
  }
}

const myEmitter = new MyEmitter()
myEmitter.on('something', (data) => {
  console.log('收到:', data)
})
myEmitter.doSomething()
```

### 方式2：组合

```js [inherit-composition.js]
const EventEmitter = require('events')

class MyEmitter {
  constructor() {
    this.emitter = new EventEmitter()
  }

  on(event, listener) {
    this.emitter.on(event, listener)
  }

  emit(event, ...args) {
    this.emitter.emit(event, ...args)
  }

  doSomething() {
    this.emit('done')
  }
}
```

## 特殊事件

### newListener 事件

当添加新的监听器时触发

```js [newListener.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

emitter.on('newListener', (event, listener) => {
  console.log(`添加了 ${event} 事件的监听器`)
})

emitter.on('data', () => {})
```

### removeListener 事件

当移除监听器时触发

```js [removeListener-event.js]
const EventEmitter = require('events')
const emitter = new EventEmitter()

emitter.on('removeListener', (event, listener) => {
  console.log(`移除了 ${event} 事件的监听器`)
})

function handler() {}
emitter.on('data', handler)
emitter.off('data', handler)
```

## 实际应用

### 自定义事件总线

```js [event-bus.js]
const EventEmitter = require('events')

class EventBus extends EventEmitter {
  static instance = null

  static getInstance() {
    if (!this.instance) {
      this.instance = new EventBus()
    }
    return this.instance
  }
}

// 使用
const bus = EventBus.getInstance()

bus.on('user:created', (user) => {
  console.log('用户创建:', user)
})

bus.on('user:deleted', (userId) => {
  console.log('用户删除:', userId)
})

// 在其他地方触发
bus.emit('user:created', { id: 1, name: '张三' })
```

### 观察者模式实现

```js [observer.js]
const EventEmitter = require('events')

class Subject extends EventEmitter {
  constructor() {
    super()
    this.state = {}
  }

  setState(newState) {
    this.state = { ...this.state, ...newState }
    this.emit('stateChange', this.state)
  }

  getState() {
    return this.state
  }
}

// 使用
const subject = new Subject()

subject.on('stateChange', (state) => {
  console.log('状态变化:', state)
})

subject.setState({ count: 1 })
subject.setState({ count: 2 })
```

::: tip 提示
- EventEmitter 是 Node.js 异步事件驱动架构的核心
- 许多内置模块（如 Stream、HTTP）都继承了 EventEmitter
- 使用 on() 监听事件，使用 emit() 触发事件
- 记得处理 error 事件，避免程序崩溃
:::
