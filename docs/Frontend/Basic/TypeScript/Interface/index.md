# TypeScript 接口

## 接口基础

接口是 TypeScript 的核心特性之一，用于定义对象的结构和类型契约。

```typescript [interface-basic.ts]
// 基础接口
interface User {
  name: string
  age: number
  email: string
}

// 使用接口
function printUser(user: User) {
  console.log(`${user.name}, ${user.age}岁, ${user.email}`)
}

const user: User = {
  name: '张三',
  age: 25,
  email: 'zhangsan@example.com'
}

printUser(user)
```

## 可选属性

```typescript [optional-props.ts]
interface Config {
  required: string
  optional?: string
  readonly readOnly: string
}

const config: Config = {
  required: '必须',
  readOnly: '只读'
}

// config.readOnly = '修改'  // 错误：只读属性
```

## 索引签名

```typescript [index-signature.ts]
// 字符串索引签名
interface StringMap {
  [key: string]: string
}

const map: StringMap = {
  name: '张三',
  age: '25'
}

// 数字索引签名
interface StringArray {
  [index: number]: string
}

const arr: StringArray = ['a', 'b', 'c']

// 混合索引签名
interface Mixed {
  [key: string]: string | number
  length: number
  name: string
}
```

## 函数类型

```typescript [function-interface.ts]
// 函数接口
interface SearchFunc {
  (source: string, subString: string): boolean
}

const mySearch: SearchFunc = (source, sub) => {
  return source.includes(sub)
}

// 构造函数接口
interface ClockConstructor {
  new (hour: number, minute: number): ClockInterface
}

interface ClockInterface {
  tick(): void
}

function createClock(ctor: ClockConstructor, hour: number, minute: number) {
  return new ctor(hour, minute)
}
```

## 接口继承

```typescript [interface-extends.ts]
// 单继承
interface Shape {
  color: string
}

interface Square extends Shape {
  sideLength: number
}

const square: Square = {
  color: 'blue',
  sideLength: 10
}

// 多继承
interface Color {
  color: string
}

interface Stroke {
  strokeWidth: number
}

interface StyledSquare extends Shape, Color, Stroke {
  sideLength: number
}

const styledSquare: StyledSquare = {
  color: 'red',
  strokeWidth: 2,
  sideLength: 5
}
```

## 接口与类

```typescript [class-interface.ts]
// 类实现接口
interface Animal {
  name: string
  makeSound(): void
}

class Dog implements Animal {
  name: string

  constructor(name: string) {
    this.name = name
  }

  makeSound() {
    console.log('汪汪')
  }
}

// 多个接口
interface Eatable {
  eat(): void
}

interface Sleepable {
  sleep(): void
}

class Person implements Eatable, Sleepable {
  eat() {
    console.log('吃饭')
  }

  sleep() {
    console.log('睡觉')
  }
}
```

## 接口与类型别名

```typescript [interface-vs-type.ts]
// 接口
interface UserInterface {
  name: string
  age: number
}

// 类型别名
type UserType = {
  name: string
  age: number
}

// 接口可以继承
interface AdminInterface extends UserInterface {
  role: string
}

// 类型别名可以交叉
type AdminType = UserType & { role: string }

// 接口不能定义联合类型
// interface Status = 'pending' | 'success' | 'error'  // 错误

// 类型别名可以
type Status = 'pending' | 'success' | 'error'

// 接口不能定义元组
// interface Tuple = [string, number]  // 错误

// 类型别名可以
type Tuple = [string, number]
```

## 动态接口

```typescript [dynamic-interface.ts]
// 声明合并
interface Window {
  title: string
}

interface Window {
  size: { width: number; height: number }
}

const win: Window = {
  title: 'My App',
  size: { width: 1920, height: 1080 }
}

// 扩展第三方库
interface ThirdPartyLib {
  existingMethod(): void
}

declare const lib: ThirdPartyLib

interface ThirdPartyLib {
  newMethod(): void
}

lib.existingMethod()
lib.newMethod()
```

::: tip 提示
- 接口用于定义对象结构
- 可选属性使用 `?` 标记
- 只读属性使用 `readonly` 标记
- 接口可以继承多个接口
- 类可以实现一个或多个接口
:::
