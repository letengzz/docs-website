# JavaScript 设计模式

## 创建型模式

### 单例模式

```javascript [singleton.js]
// 基础单例
class Singleton {
  constructor(name) {
    if (Singleton.instance) {
      return Singleton.instance
    }
    this.name = name
    Singleton.instance = this
  }
}

const s1 = new Singleton('实例 1')
const s2 = new Singleton('实例 2')
console.log(s1 === s2)  // true

// 闭包单例
const createSingleton = (() => {
  let instance = null
  return (name) => {
    if (!instance) {
      instance = { name }
    }
    return instance
  }
})()

const s3 = createSingleton('实例 3')
const s4 = createSingleton('实例 4')
console.log(s3 === s4)  // true

// 实际应用：全局状态管理
class Store {
  constructor() {
    if (Store.instance) {
      return Store.instance
    }
    this.state = {}
    this.listeners = []
    Store.instance = this
  }

  setState(key, value) {
    this.state[key] = value
    this.notify()
  }

  getState(key) {
    return this.state[key]
  }

  subscribe(listener) {
    this.listeners.push(listener)
  }

  notify() {
    this.listeners.forEach(listener => listener(this.state))
  }
}
```

### 工厂模式

```javascript [factory.js]
// 简单工厂
class Car {
  constructor(brand) {
    this.brand = brand
  }
}

class Bike {
  constructor(brand) {
    this.brand = brand
  }
}

class VehicleFactory {
  static createVehicle(type, brand) {
    switch (type) {
      case 'car':
        return new Car(brand)
      case 'bike':
        return new Bike(brand)
      default:
        throw new Error('未知类型')
    }
  }
}

const car = VehicleFactory.createVehicle('car', 'BMW')
const bike = VehicleFactory.createVehicle('bike', 'Giant')

// 工厂方法
class Notification {
  send(message) {
    throw new Error('必须实现 send 方法')
  }
}

class EmailNotification extends Notification {
  send(message) {
    console.log('发送邮件:', message)
  }
}

class SMSNotification extends Notification {
  send(message) {
    console.log('发送短信:', message)
  }
}

class NotificationFactory {
  static createNotification(type) {
    const types = {
      email: EmailNotification,
      sms: SMSNotification
    }
    return new types[type]()
  }
}

const email = NotificationFactory.createNotification('email')
email.send('你好')
```

### 抽象工厂模式

```javascript [abstract-factory.js]
// UI 组件工厂
class Button {
  render() { throw new Error('必须实现') }
}

class Input {
  render() { throw new Error('必须实现') }
}

// Windows 风格
class WindowsButton extends Button {
  render() { return '<button class="windows-btn">Windows 按钮</button>' }
}

class WindowsInput extends Input {
  render() { return '<input class="windows-input" />' }
}

// Mac 风格
class MacButton extends Button {
  render() { return '<button class="mac-btn">Mac 按钮</button>' }
}

class MacInput extends Input {
  render() { return '<input class="mac-input" />' }
}

// 抽象工厂
class UIFactory {
  createButton() { throw new Error('必须实现') }
  createInput() { throw new Error('必须实现') }
}

class WindowsFactory extends UIFactory {
  createButton() { return new WindowsButton() }
  createInput() { return new WindowsInput() }
}

class MacFactory extends UIFactory {
  createButton() { return new MacButton() }
  createInput() { return new MacInput() }
}

// 使用
function createUI(factory) {
  const button = factory.createButton()
  const input = factory.createInput()
  console.log(button.render())
  console.log(input.render())
}

createUI(new WindowsFactory())
createUI(new MacFactory())
```

### 建造者模式

```javascript [builder.js]
class User {
  constructor(builder) {
    this.name = builder.name
    this.age = builder.age
    this.email = builder.email
    this.phone = builder.phone
    this.address = builder.address
  }
}

class UserBuilder {
  constructor() {
    this.name = null
    this.age = null
    this.email = null
    this.phone = null
    this.address = null
  }

  setName(name) {
    this.name = name
    return this
  }

  setAge(age) {
    this.age = age
    return this
  }

  setEmail(email) {
    this.email = email
    return this
  }

  setPhone(phone) {
    this.phone = phone
    return this
  }

  setAddress(address) {
    this.address = address
    return this
  }

  build() {
    return new User(this)
  }
}

// 使用
const user = new UserBuilder()
  .setName('张三')
  .setAge(25)
  .setEmail('zhangsan@example.com')
  .build()

console.log(user)
```

## 结构型模式

### 适配器模式

```javascript [adapter.js]
// 旧接口
class OldAPI {
  request() {
    return '旧接口数据'
  }
}

// 新接口
class NewAPI {
  fetch() {
    return '新接口数据'
  }
}

// 适配器
class APIAdapter {
  constructor(api) {
    this.api = api
  }

  request() {
    if (this.api instanceof OldAPI) {
      return this.api.request()
    } else if (this.api instanceof NewAPI) {
      return this.api.fetch()
    }
  }
}

// 使用
const oldAPI = new OldAPI()
const newAPI = new NewAPI()

const adapter1 = new APIAdapter(oldAPI)
const adapter2 = new APIAdapter(newAPI)

console.log(adapter1.request())  // 旧接口数据
console.log(adapter2.request())  // 新接口数据

// 实际应用：第三方库适配
class AxiosAdapter {
  constructor(axios) {
    this.axios = axios
  }

  get(url) {
    return this.axios.get(url).then(res => res.data)
  }

  post(url, data) {
    return this.axios.post(url, data).then(res => res.data)
  }
}
```

### 装饰器模式

```javascript [decorator.js]
// 函数装饰器
function log(target, name, descriptor) {
  const original = descriptor.value
  descriptor.value = function(...args) {
    console.log(`调用 ${name} 前:`, args)
    const result = original.apply(this, args)
    console.log(`调用 ${name} 后:`, result)
    return result
  }
  return descriptor
}

class Math {
  @log
  add(a, b) {
    return a + b
  }
}

// 手动装饰
function withLogging(fn) {
  return function(...args) {
    console.log('调用前:', args)
    const result = fn.apply(this, args)
    console.log('调用后:', result)
    return result
  }
}

const add = withLogging((a, b) => a + b)
console.log(add(1, 2))

// 链式装饰
function withCache(fn) {
  const cache = new Map()
  return function(...args) {
    const key = JSON.stringify(args)
    if (cache.has(key)) {
      return cache.get(key)
    }
    const result = fn.apply(this, args)
    cache.set(key, result)
    return result
  }
}

const cachedAdd = withCache(withLogging((a, b) => a + b))
```

### 代理模式

```javascript [proxy.js]
// 基础代理
const target = {
  name: '张三',
  age: 25
}

const handler = {
  get(target, prop) {
    console.log(`访问属性: ${prop}`)
    return target[prop]
  },
  set(target, prop, value) {
    console.log(`设置属性: ${prop} = ${value}`)
    target[prop] = value
    return true
  }
}

const proxy = new Proxy(target, handler)
console.log(proxy.name)  // 访问属性: name
proxy.age = 26           // 设置属性: age = 26

// 验证代理
const validator = {
  set(target, prop, value) {
    if (prop === 'age') {
      if (typeof value !== 'number') {
        throw new TypeError('年龄必须是数字')
      }
      if (value < 0 || value > 150) {
        throw new RangeError('年龄必须在 0-150 之间')
      }
    }
    target[prop] = value
    return true
  }
}

const user = new Proxy({}, validator)
user.age = 25
// user.age = 'abc'  // TypeError

// 缓存代理
function createCacheProxy(fn) {
  const cache = new Map()
  return new Proxy(fn, {
    apply(target, thisArg, args) {
      const key = JSON.stringify(args)
      if (cache.has(key)) {
        return cache.get(key)
      }
      const result = target.apply(thisArg, args)
      cache.set(key, result)
      return result
    }
  })
}

const fibonacci = createCacheProxy((n) => {
  if (n <= 1) return n
  return fibonacci(n - 1) + fibonacci(n - 2)
})
```

### 观察者模式

```javascript [observer.js]
class Subject {
  constructor() {
    this.observers = []
  }

  subscribe(observer) {
    this.observers.push(observer)
  }

  unsubscribe(observer) {
    this.observers = this.observers.filter(obs => obs !== observer)
  }

  notify(data) {
    this.observers.forEach(observer => observer.update(data))
  }
}

class Observer {
  constructor(name) {
    this.name = name
  }

  update(data) {
    console.log(`${this.name} 收到数据:`, data)
  }
}

// 使用
const subject = new Subject()
const observer1 = new Observer('观察者 1')
const observer2 = new Observer('观察者 2')

subject.subscribe(observer1)
subject.subscribe(observer2)
subject.notify('新消息')

// 实际应用：事件总线
class EventBus {
  constructor() {
    this.events = {}
  }

  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = []
    }
    this.events[event].push(callback)
  }

  off(event, callback) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback)
    }
  }

  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(callback => callback(data))
    }
  }
}
```

## 行为型模式

### 策略模式

```javascript [strategy.js]
// 基础策略
class Strategy {
  execute(data) {
    throw new Error('必须实现')
  }
}

class QuickSort extends Strategy {
  execute(arr) {
    if (arr.length <= 1) return arr
    const pivot = arr[Math.floor(arr.length / 2)]
    const left = arr.filter(x => x < pivot)
    const middle = arr.filter(x => x === pivot)
    const right = arr.filter(x => x > pivot)
    return [...this.execute(left), ...middle, ...this.execute(right)]
  }
}

class BubbleSort extends Strategy {
  execute(arr) {
    const result = [...arr]
    for (let i = 0; i < result.length; i++) {
      for (let j = 0; j < result.length - i - 1; j++) {
        if (result[j] > result[j + 1]) {
          [result[j], result[j + 1]] = [result[j + 1], result[j]]
        }
      }
    }
    return result
  }
}

class Sorter {
  constructor(strategy) {
    this.strategy = strategy
  }

  sort(arr) {
    return this.strategy.execute(arr)
  }
}

// 使用
const sorter = new Sorter(new QuickSort())
console.log(sorter.sort([3, 1, 4, 1, 5, 9, 2, 6]))

// 实际应用：表单验证
const validators = {
  required: (value) => value ? null : '必填项',
  email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? null : '邮箱格式错误',
  min: (min) => (value) => value.length >= min ? null : `最少 ${min} 个字符`
}

class FormValidator {
  constructor(rules) {
    this.rules = rules
  }

  validate(data) {
    const errors = {}
    for (const [field, rules] of Object.entries(this.rules)) {
      for (const rule of rules) {
        const error = rule(data[field])
        if (error) {
          errors[field] = error
          break
        }
      }
    }
    return errors
  }
}
```

### 命令模式

```javascript [command.js]
class Command {
  execute() { throw new Error('必须实现') }
  undo() { throw new Error('必须实现') }
}

class LightOnCommand extends Command {
  constructor(light) {
    super()
    this.light = light
  }

  execute() {
    this.light.on()
  }

  undo() {
    this.light.off()
  }
}

class LightOffCommand extends Command {
  constructor(light) {
    super()
    this.light = light
  }

  execute() {
    this.light.off()
  }

  undo() {
    this.light.on()
  }
}

class Light {
  on() { console.log('灯亮了') }
  off() { console.log('灯灭了') }
}

class RemoteControl {
  constructor() {
    this.commands = []
    this.history = []
  }

  setCommand(index, command) {
    this.commands[index] = command
  }

  pressButton(index) {
    const command = this.commands[index]
    if (command) {
      command.execute()
      this.history.push(command)
    }
  }

  pressUndo() {
    const command = this.history.pop()
    if (command) {
      command.undo()
    }
  }
}

// 使用
const light = new Light()
const remote = new RemoteControl()
remote.setCommand(0, new LightOnCommand(light))
remote.setCommand(1, new LightOffCommand(light))
remote.pressButton(0)  // 灯亮了
remote.pressButton(1)  // 灯灭了
remote.pressUndo()     // 灯亮了
```

### 模板方法模式

```javascript [template-method.js]
class Beverage {
  prepare() {
    this.boilWater()
    this.brew()
    this.pourInCup()
    this.addCondiments()
  }

  boilWater() {
    console.log('烧水')
  }

  brew() {
    throw new Error('必须实现')
  }

  pourInCup() {
    console.log('倒入杯中')
  }

  addCondiments() {
    throw new Error('必须实现')
  }
}

class Coffee extends Beverage {
  brew() {
    console.log('冲泡咖啡')
  }

  addCondiments() {
    console.log('加糖和牛奶')
  }
}

class Tea extends Beverage {
  brew() {
    console.log('冲泡茶叶')
  }

  addCondiments() {
    console.log('加柠檬')
  }
}

// 使用
const coffee = new Coffee()
coffee.prepare()

const tea = new Tea()
tea.prepare()
```

### 状态模式

```javascript [state.js]
class State {
  enter() { throw new Error('必须实现') }
  exit() { throw new Error('必须实现') }
}

class IdleState extends State {
  enter() { console.log('进入空闲状态') }
  exit() { console.log('离开空闲状态') }
}

class RunningState extends State {
  enter() { console.log('进入运行状态') }
  exit() { console.log('离开运行状态') }
}

class PausedState extends State {
  enter() { console.log('进入暂停状态') }
  exit() { console.log('离开暂停状态') }
}

class Player {
  constructor() {
    this.state = null
    this.states = {
      idle: new IdleState(),
      running: new RunningState(),
      paused: new PausedState()
    }
    this.setState('idle')
  }

  setState(stateName) {
    if (this.state) {
      this.state.exit()
    }
    this.state = this.states[stateName]
    this.state.enter()
  }

  play() {
    this.setState('running')
  }

  pause() {
    this.setState('paused')
  }

  stop() {
    this.setState('idle')
  }
}

// 使用
const player = new Player()
player.play()   // 进入运行状态
player.pause()  // 进入暂停状态
player.stop()   // 进入空闲状态
```

::: tip 提示
- 单例模式用于全局唯一实例
- 工厂模式用于创建对象
- 观察者模式用于事件系统
- 策略模式用于算法切换
- 代理模式用于访问控制
::: 

## 相关专题

- [后端设计模式](../../../../Backend/DesignPatterns/index.md)：SOLID 原则与 Java 版完整模式体系
- [设计模式实战](../../../../Backend/DesignPatterns/Practice/index.md)：电商场景的坏味道重构案例
