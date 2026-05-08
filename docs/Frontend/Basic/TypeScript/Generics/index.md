# TypeScript 泛型

## 泛型基础

泛型允许在定义函数、接口或类时不预先指定具体类型，而在使用时再指定类型。

```typescript [generics-basic.ts]
// 基础泛型函数
function identity<T>(arg: T): T {
  return arg
}

// 使用
const result1 = identity<string>('hello')
const result2 = identity<number>(42)
const result3 = identity(true)  // 类型推断

// 泛型箭头函数
const identity2 = <T>(arg: T): T => arg
```

## 泛型变量

```typescript [generics-variables.ts]
// 使用泛型变量
function loggingIdentity<T>(arg: T[]): T[] {
  console.log(arg.length)
  return arg
}

// 泛型数组
function createArray<T>(length: number, value: T): T[] {
  return Array(length).fill(value)
}

const strings = createArray<string>(3, 'hello')
const numbers = createArray<number>(3, 0)

// 泛型元组
function swap<T, U>(tuple: [T, U]): [U, T] {
  return [tuple[1], tuple[0]]
}

const result = swap<string, number>(['hello', 42])
```

## 泛型接口

```typescript [generics-interface.ts]
// 泛型接口
interface GenericIdentityFn {
  <T>(arg: T): T
}

function identity<T>(arg: T): T {
  return arg
}

let myIdentity: GenericIdentityFn = identity

// 泛型接口参数化
interface GenericIdentityFn2<T> {
  (arg: T): T
}

let myIdentity2: GenericIdentityFn2<number> = identity

// 泛型接口用于对象
interface KeyValue<K, V> {
  key: K
  value: V
}

const item: KeyValue<string, number> = {
  key: 'age',
  value: 25
}
```

## 泛型类

```typescript [generics-class.ts]
// 泛型类
class GenericNumber<T> {
  zeroValue: T
  add: (x: T, y: T) => T

  constructor(zeroValue: T, add: (x: T, y: T) => T) {
    this.zeroValue = zeroValue
    this.add = add
  }
}

const numberAdder = new GenericNumber<number>(
  0,
  (x, y) => x + y
)

const stringAdder = new GenericNumber<string>(
  '',
  (x, y) => x + y
)

// 泛型类实现接口
interface Container<T> {
  value: T
  getValue(): T
}

class Box<T> implements Container<T> {
  value: T

  constructor(value: T) {
    this.value = value
  }

  getValue(): T {
    return this.value
  }
}
```

## 泛型约束

```typescript [generics-constraint.ts]
// 泛型约束
interface Lengthwise {
  length: number
}

function loggingIdentity<T extends Lengthwise>(arg: T): T {
  console.log(arg.length)
  return arg
}

loggingIdentity('hello')  // 有 length 属性
loggingIdentity([1, 2, 3])  // 数组有 length
// loggingIdentity(42)  // 错误：number 没有 length

// 约束多个类型参数
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}

const user = { name: '张三', age: 25 }
getProperty(user, 'name')
getProperty(user, 'age')
// getProperty(user, 'email')  // 错误：email 不在 user 中
```

## 泛型工具类型

```typescript [generics-utility.ts]
// Partial - 所有属性可选
interface User {
  name: string
  age: number
  email: string
}

function updateUser(id: string, updates: Partial<User>) {
  console.log('更新用户:', id, updates)
}

updateUser('1', { name: '李四' })

// Required - 所有属性必填
interface Config {
  host?: string
  port?: number
}

const requiredConfig: Required<Config> = {
  host: 'localhost',
  port: 3000
}

// Readonly - 所有属性只读
const readonlyUser: Readonly<User> = {
  name: '张三',
  age: 25,
  email: 'zhangsan@example.com'
}

// Record - 创建对象类型
type Role = 'admin' | 'user' | 'guest'
type Permissions = 'read' | 'write' | 'delete'

const rolePermissions: Record<Role, Permissions[]> = {
  admin: ['read', 'write', 'delete'],
  user: ['read', 'write'],
  guest: ['read']
}
```

## 条件类型

```typescript [conditional-types.ts]
// 基础条件类型
type IsString<T> = T extends string ? true : false

type A = IsString<string>  // true
type B = IsString<number>  // false

// 排除类型
type NonNullable<T> = T extends null | undefined ? never : T

type C = NonNullable<string | null | undefined>  // string

// 提取类型
type Extract<T, U> = T extends U ? T : never

type D = Extract<'a' | 'b' | 'c', 'a' | 'b'>  // 'a' | 'b'

// 排除类型
type Exclude<T, U> = T extends U ? never : T

type E = Exclude<'a' | 'b' | 'c', 'a' | 'b'>  // 'c'
```

## 映射类型

```typescript [mapped-types.ts]
// 基础映射类型
interface User {
  name: string
  age: number
  email: string
}

// 将所有属性变为可选
type PartialUser = {
  [K in keyof User]?: User[K]
}

// 将所有属性变为只读
type ReadonlyUser = {
  readonly [K in keyof User]: User[K]
}

// 添加前缀
type WithPrefix<T, Prefix extends string> = {
  [K in keyof T as `${Prefix}${Capitalize<string & K>}`]: T[K]
}

type UserWithApi = WithPrefix<User, 'api'>
// { apiName: string, apiAge: number, apiEmail: string }

// 移除修饰符
type Mutable<T> = {
  -readonly [K in keyof T]: T[K]
}

type Optional<T> = {
  [K in keyof T]?: T[K]
}
```

## 模板字面量类型

```typescript [template-literal-types.ts]
// 基础模板类型
type EventName = `on${Capitalize<string>}`

const clickEvent: EventName = 'onClick'
const hoverEvent: EventName = 'onHover'

// 联合类型组合
type Alignment = 'top' | 'middle' | 'bottom'
type Position = `${Alignment}${'Left' | 'Center' | 'Right'}`

const pos1: Position = 'topLeft'
const pos2: Position = 'middleCenter'
const pos3: Position = 'bottomRight'

// 字符串操作类型
type Greeting = `Hello ${'World' | 'TypeScript'}`
// 'Hello World' | 'Hello TypeScript'

// 内置字符串工具类型
type LowercaseStr = Lowercase<'HELLO'>  // 'hello'
type UppercaseStr = Uppercase<'hello'>  // 'HELLO'
type CapitalizeStr = Capitalize<'hello'>  // 'Hello'
type UncapitalizeStr = Uncapitalize<'Hello'>  // 'hello'
```

::: tip 提示
- 泛型提高代码复用性
- 使用 extends 约束泛型类型
- keyof 获取对象键的联合类型
- 条件类型实现类型逻辑
- 映射类型转换对象结构
:::
