# TypeScript 类型推断

## 基础类型推断

TypeScript 会根据上下文自动推断变量类型。

```typescript [basic-inference.ts]
// 变量推断
let x = 3  // 推断为 number
let y = 'hello'  // 推断为 string
let z = true  // 推断为 boolean

// 函数返回值推断
function add(a: number, b: number) {
  return a + b  // 推断返回 number
}

// 数组推断
const arr = [1, 2, 3]  // 推断为 number[]
const mixed = [1, 'hello', true]  // 推断为 (string | number | boolean)[]
```

## 最佳通用类型

```typescript [best-common-type.ts]
// 最佳通用类型推断
const arr1 = [1, 2, null]  // (number | null)[]

// 上下文类型推断
interface User {
  name: string
  age: number
}

const users: User[] = [
  { name: '张三', age: 25 },
  { name: '李四', age: 30 }
]

// 对象字面量推断
const user = {
  name: '张三',
  age: 25,
  email: 'zhangsan@example.com'
}
// 推断为 { name: string; age: number; email: string }
```

## 上下文类型推断

```typescript [contextual-typing.ts]
// 事件处理
window.addEventListener('click', (event) => {
  console.log(event.clientX)  // event 推断为 MouseEvent
})

// 数组方法
const numbers = [1, 2, 3, 4, 5]
const doubled = numbers.map((n) => n * 2)  // n 推断为 number

// 对象方法
const obj = {
  greet(name: string) {
    return `Hello, ${name}`
  }
}

obj.greet('张三')
// obj.greet(123)  // 错误：参数必须是 string
```

## 类型断言与推断

```typescript [type-assertion.ts]
// 类型断言
const input = document.getElementById('input') as HTMLInputElement
input.value = 'test'

// 非空断言
function processValue(value: string | null) {
  console.log(value!.length)  // 断言 value 不为 null
}

// 常量断言
const config = {
  url: 'https://api.example.com',
  timeout: 5000
} as const

// config.url = 'https://other.com'  // 错误：只读属性
```

## 类型守卫

```typescript [type-guards.ts]
// typeof 守卫
function padLeft(value: string, padding: string | number) {
  if (typeof padding === 'number') {
    return ' '.repeat(padding) + value
  }
  if (typeof padding === 'string') {
    return padding + value
  }
  throw new Error('Invalid padding')
}

// instanceof 守卫
class Dog {
  bark() {
    console.log('汪汪')
  }
}

class Cat {
  meow() {
    console.log('喵喵')
  }
}

function makeSound(animal: Dog | Cat) {
  if (animal instanceof Dog) {
    animal.bark()
  } else {
    animal.meow()
  }
}

// in 守卫
interface Fish {
  swim(): void
  name: string
}

interface Bird {
  fly(): void
  name: string
}

function move(animal: Fish | Bird) {
  if ('swim' in animal) {
    animal.swim()
  } else {
    animal.fly()
  }
}
```

## 自定义类型守卫

```typescript [custom-guards.ts]
// 类型谓词
interface User {
  name: string
  email: string
}

interface Admin {
  name: string
  role: string
  permissions: string[]
}

function isAdmin(user: User | Admin): user is Admin {
  return 'role' in user && 'permissions' in user
}

function getPermissions(user: User | Admin) {
  if (isAdmin(user)) {
    return user.permissions
  }
  return []
}

// 类型守卫函数
function isString(value: unknown): value is string {
  return typeof value === 'string'
}

function processValue(value: unknown) {
  if (isString(value)) {
    console.log(value.toUpperCase())
  }
}
```

## 控制流分析

```typescript [control-flow.ts]
// 控制流类型收窄
function process(value: string | number | boolean) {
  if (typeof value === 'string') {
    // value 在这里是 string
    console.log(value.length)
  } else if (typeof value === 'number') {
    // value 在这里是 number
    console.log(value.toFixed(2))
  } else {
    // value 在这里是 boolean
    console.log(value ? 'true' : 'false')
  }
}

// 联合类型收窄
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'square'; side: number }
  | { kind: 'rectangle'; width: number; height: number }

function getArea(shape: Shape) {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2
    case 'square':
      return shape.side ** 2
    case 'rectangle':
      return shape.width * shape.height
  }
}
```

## 推断规则

```typescript [inference-rules.ts]
// 函数参数推断
function createPair<T>(a: T, b: T): [T, T] {
  return [a, b]
}

createPair(1, 2)  // T 推断为 number
createPair('a', 'b')  // T 推断为 string

// 泛型约束推断
function getProperty<T, K extends keyof T>(obj: T, key: K) {
  return obj[key]
}

const user = { name: '张三', age: 25 }
getProperty(user, 'name')  // K 推断为 'name'
getProperty(user, 'age')  // K 推断为 'age'

// 条件类型推断
type Unpack<T> = T extends (infer U)[] ? U : T

type A = Unpack<number[]>  // number
type B = Unpack<string>  // string
```

::: tip 提示
- TypeScript 会自动推断变量类型
- 函数返回值会根据 return 语句推断
- 上下文类型会根据使用场景推断
- 使用类型守卫收窄联合类型
- 控制流分析会跟踪类型变化
:::
