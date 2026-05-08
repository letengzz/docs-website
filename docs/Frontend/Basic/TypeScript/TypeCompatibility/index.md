# TypeScript 类型兼容性

## 结构子类型

TypeScript 使用结构子类型系统，基于成员结构进行比较。

```typescript [structural-subtyping.ts]
// 基础兼容性
interface Named {
  name: string
}

class Person {
  name: string
}

let p: Named
p = new Person()  // 兼容：Person 有 name 属性

// 函数兼容性
let x = (a: number) => 0
let y = (b: number, s: string) => 0

y = x  // 兼容：x 的参数更少
// x = y  // 不兼容：y 的参数更多
```

## 函数兼容性

```typescript [function-compatibility.ts]
// 参数兼容性
type Handler = (a: number, b: number) => void

function doSomething(handler: Handler) {
  handler(1, 2)
}

// 参数名不重要
doSomething((n, s) => console.log(n, s))

// 返回值兼容性
let f1 = () => ({ name: '张三' })
let f2 = () => ({ name: '李四', age: 25 })

f1 = f2  // 兼容：f2 返回值包含 f1 的所有属性
// f2 = f1  // 不兼容：f1 缺少 age 属性

// 可选参数和 rest 参数
let source = (a: number) => 0
let target = (a?: number) => 0

target = source  // 兼容
// source = target  // 不兼容
```

## 枚举兼容性

```typescript [enum-compatibility.ts]
// 枚举与数字兼容
enum Status {
  Pending,
  Active,
  Completed
}

let status: Status = Status.Pending
let num: number = status  // 兼容

// 不同枚举不兼容
enum Color {
  Red,
  Green,
  Blue
}

// let color: Color = Status.Active  // 不兼容
```

## 类兼容性

```typescript [class-compatibility.ts]
// 实例成员比较
class Animal {
  name: string
}

class Dog extends Animal {
  breed: string
}

let animal: Animal
animal = new Dog()  // 兼容：Dog 有 Animal 的所有属性

// 静态成员和构造函数不比较
class Point {
  x: number
  y: number
}

class Point3D extends Point {
  z: number
}

let point: Point
point = new Point3D(1, 2, 3)  // 兼容

// 私有成员比较
class PrivateClass {
  private id: number
}

class AnotherPrivateClass {
  private id: number
}

// let private: PrivateClass = new AnotherPrivateClass()  // 不兼容
```

## 泛型兼容性

```typescript [generics-compatibility.ts]
// 类型参数影响
interface Empty<T> {}

let x: Empty<number>
let y: Empty<string>

x = y  // 兼容：没有使用类型参数

// 使用类型参数
interface NotEmpty<T> {
  data: T
}

let a: NotEmpty<number>
let b: NotEmpty<string>

// a = b  // 不兼容：类型参数不同

// 泛型函数
function identity<T>(arg: T): T {
  return arg
}

function loggingIdentity<U>(arg: U): U {
  console.log(arg)
  return arg
}

let myIdentity: <T>(arg: T) => T = identity
```

## 高级类型兼容性

```typescript [advanced-compatibility.ts]
// 联合类型
type StringOrNumber = string | number
type NumberOrBoolean = number | boolean

let value: StringOrNumber
value = 42  // 兼容

// 交叉类型
interface A { a: string }
interface B { b: number }
interface C { c: boolean }

type AB = A & B
type ABC = A & B & C

let ab: AB = { a: 'test', b: 123 }
let abc: ABC = { a: 'test', b: 123, c: true }

ab = abc  // 兼容：abc 包含 ab 的所有属性
// abc = ab  // 不兼容：ab 缺少 c 属性

// 条件类型兼容性
type IsString<T> = T extends string ? true : false

type A = IsString<string>  // true
type B = IsString<number>  // false
```

## 类型保护与兼容性

```typescript [type-safety.ts]
// 类型保护
function isNumber(value: unknown): value is number {
  return typeof value === 'number'
}

function process(value: string | number) {
  if (isNumber(value)) {
    console.log(value.toFixed(2))
  } else {
    console.log(value.toUpperCase())
  }
}

// 类型断言
interface User {
  name: string
  age: number
}

function createUser(data: unknown): User {
  return data as User
}

// 类型守卫链
type Shape =
  | { type: 'circle'; radius: number }
  | { type: 'square'; side: number }

function getArea(shape: Shape) {
  if (shape.type === 'circle') {
    return Math.PI * shape.radius ** 2
  }
  return shape.side ** 2
}
```

::: tip 提示
- TypeScript 使用结构子类型
- 函数参数逆变，返回值协变
- 类只比较实例成员
- 泛型类型参数影响兼容性
- 使用类型保护确保安全
:::
