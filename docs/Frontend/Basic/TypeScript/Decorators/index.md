# TypeScript 装饰器

## 装饰器基础

装饰器是一种特殊类型的声明，能够被附加到类声明、方法、访问器、属性或参数上。

```typescript [decorator-basic.ts]
// 启用装饰器：tsconfig.json 中设置 "experimentalDecorators": true

// 类装饰器
function sealed(constructor: Function) {
  Object.seal(constructor)
  Object.seal(constructor.prototype)
}

@sealed
class Greeter {
  greeting: string

  constructor(message: string) {
    this.greeting = message
  }

  greet() {
    return `Hello, ${this.greeting}`
  }
}
```

## 装饰器工厂

```typescript [decorator-factory.ts]
// 装饰器工厂
function configurable(value: boolean) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    descriptor.configurable = value
  }
}

class Point {
  private _x: number
  private _y: number

  constructor(x: number, y: number) {
    this._x = x
    this._y = y
  }

  @configurable(false)
  get x() {
    return this._x
  }

  @configurable(false)
  get y() {
    return this._y
  }
}
```

## 类装饰器

```typescript [class-decorator.ts]
// 类装饰器
function logClass(target: Function) {
  console.log('类被创建:', target.name)
}

function addMetadata(metadata: any) {
  return function (target: Function) {
    target.prototype.metadata = metadata
  }
}

@logClass
@addMetadata({ version: '1.0.0' })
class UserService {
  getUsers() {
    return ['张三', '李四']
  }
}

// 替换构造函数
function classDecorator<T extends { new (...args: any[]): {} }>(
  constructor: T
) {
  return class extends constructor {
    newProperty = 'new property'
    hello = 'override'
  }
}

@classDecorator
class MyClass {
  hello = 'hello'
}
```

## 方法装饰器

```typescript [method-decorator.ts]
// 方法装饰器
function logMethod(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor
) {
  const originalMethod = descriptor.value

  descriptor.value = function (...args: any[]) {
    console.log(`调用 ${propertyKey} 前:`, args)
    const result = originalMethod.apply(this, args)
    console.log(`调用 ${propertyKey} 后:`, result)
    return result
  }

  return descriptor
}

class Calculator {
  @logMethod
  add(a: number, b: number) {
    return a + b
  }

  @logMethod
  multiply(a: number, b: number) {
    return a * b
  }
}

const calc = new Calculator()
calc.add(1, 2)
calc.multiply(3, 4)
```

## 访问器装饰器

```typescript [accessor-decorator.ts]
// 访问器装饰器
function enumerable(value: boolean) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    descriptor.enumerable = value
  }
}

class User {
  private _name: string

  constructor(name: string) {
    this._name = name
  }

  @enumerable(false)
  get name() {
    return this._name
  }

  set name(value: string) {
    this._name = value
  }
}

const user = new User('张三')
console.log(Object.keys(user))  // []
```

## 属性装饰器

```typescript [property-decorator.ts]
// 属性装饰器
function formatString(format: string) {
  return function (target: any, propertyKey: string) {
    let value: string

    const getter = function () {
      return value
    }

    const setter = function (newVal: string) {
      value = format.replace('{0}', newVal)
    }

    Object.defineProperty(target, propertyKey, {
      get: getter,
      set: setter,
      enumerable: true,
      configurable: true
    })
  }
}

class Message {
  @formatString('Hello, {0}!')
  greeting: string
}

const msg = new Message()
msg.greeting = '张三'
console.log(msg.greeting)  // Hello, 张三!
```

## 参数装饰器

```typescript [parameter-decorator.ts]
// 参数装饰器
function logParameter(target: any, propertyKey: string, parameterIndex: number) {
  const key = `__parameter_${propertyKey}_${parameterIndex}`
  
  if (!Array.isArray(target[key])) {
    target[key] = []
  }
  target[key].push(parameterIndex)
}

class UserController {
  getUser(
    @logParameter id: number,
    @logParameter fields: string[]
  ) {
    console.log('获取用户:', id, fields)
  }
}

// 读取参数装饰器信息
const controller = new UserController()
const metadata = (controller as any).__parameter_getUser_0
console.log(metadata)  // [0, 1]
```

## 装饰器组合

```typescript [decorator-compose.ts]
// 多个装饰器
function First() {
  console.log('First(): factory evaluated')
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    console.log('First(): called')
  }
}

function Second() {
  console.log('Second(): factory evaluated')
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    console.log('Second(): called')
  }
}

class Demo {
  @First()
  @Second()
  method() {}
}

// 输出顺序：
// First(): factory evaluated
// Second(): factory evaluated
// Second(): called
// First(): called

// 装饰器执行顺序
// 1. 参数装饰器
// 2. 方法装饰器
// 3. 访问器装饰器
// 4. 属性装饰器
// 5. 类装饰器
```

## 元数据反射

```typescript [metadata-reflection.ts]
// 需要安装：npm install reflect-metadata
import 'reflect-metadata'

function logType(target: any, propertyKey: string) {
  const type = Reflect.getMetadata('design:type', target, propertyKey)
  console.log(`${propertyKey} type: ${type.name}`)
}

function logParams(target: any, propertyKey: string) {
  const types = Reflect.getMetadata('design:paramtypes', target, propertyKey)
  console.log(`${propertyKey} param types:`, types.map((t: any) => t.name))
}

class User {
  @logType
  name: string

  @logType
  age: number

  @logParams
  constructor(name: string, age: number) {
    this.name = name
    this.age = age
  }
}

// 输出：
// name type: String
// age type: Number
// constructor param types: ['String', 'Number']
```

::: danger 注意
- 装饰器是实验性功能，需要在 tsconfig.json 中启用
- 装饰器执行顺序：从上到下，从外到内
- 参数装饰器在方法装饰器之前执行
- 装饰器不能用于声明文件
:::
