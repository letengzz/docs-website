# TypeScript 高级类型

## 条件类型

条件类型根据条件判断来选择类型。

```typescript [conditional-types.ts]
// 基础条件类型
type IsString<T> = T extends string ? 'yes' : 'no'

type A = IsString<string>  // 'yes'
type B = IsString<number>  // 'no'

// 类型过滤
type NonNullable<T> = T extends null | undefined ? never : T

type C = NonNullable<string | null | undefined>  // string

// 嵌套条件类型
type DeepReadonly<T> = T extends (...args: any[]) => any
  ? T
  : T extends object
  ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
  : T

interface User {
  name: string
  address: {
    city: string
    zip: string
  }
}

type ReadonlyUser = DeepReadonly<User>
```

## 条件类型推断

```typescript [conditional-infer.ts]
// infer 关键字
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any

function getUser() {
  return { name: '张三', age: 25 }
}

type User = ReturnType<typeof getUser>
// { name: string; age: number }

// 提取数组元素类型
type ElementType<T> = T extends (infer E)[] ? E : T

type A = ElementType<string[]>  // string
type B = ElementType<number[]>  // number

// 提取 Promise 类型
type UnpackPromise<T> = T extends Promise<infer U> ? U : T

type C = UnpackPromise<Promise<string>>  // string
type D = UnpackPromise<Promise<number[]>>  // number[]
```

## 映射类型

映射类型基于旧类型创建新类型。

```typescript [mapped-types.ts]
// 基础映射类型
interface User {
  name: string
  age: number
  email: string
}

// 可选映射
type Partial<T> = {
  [K in keyof T]?: T[K]
}

type PartialUser = Partial<User>
// { name?: string; age?: number; email?: string }

// 只读映射
type Readonly<T> = {
  readonly [K in keyof T]: T[K]
}

type ReadonlyUser = Readonly<User>
// { readonly name: string; readonly age: number; readonly email: string }

// 必填映射
type Required<T> = {
  [K in keyof T]-?: T[K]
}
```

## 映射类型修饰符

```typescript [mapped-modifiers.ts]
// 移除可选修饰符
type Required<T> = {
  [K in keyof T]-?: T[K]
}

// 移除只读修饰符
type Mutable<T> = {
  -readonly [K in keyof T]: T[K]
}

interface ReadonlyUser {
  readonly name: string
  readonly age: number
}

type MutableUser = Mutable<ReadonlyUser>
// { name: string; age: number }

// 添加前缀
type WithPrefix<T, Prefix extends string> = {
  [K in keyof T as `${Prefix}${Capitalize<string & K>}`]: T[K]
}

type ApiUser = WithPrefix<User, 'api'>
// { apiName: string; apiAge: number; apiEmail: string }
```

## 键重映射

```typescript [key-remapping.ts]
// 键重映射
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]
}

interface Person {
  name: string
  age: number
  location: string
}

type LazyPerson = Getters<Person>
// {
//   getName: () => string
//   getAge: () => number
//   getLocation: () => string
// }

// 过滤属性
type RemoveKindField<T> = {
  [K in keyof T as Exclude<K, 'kind'>]: T[K]
}

interface Circle {
  kind: 'circle'
  radius: number
}

type KindlessCircle = RemoveKindField<Circle>
// { radius: number }
```

## 模板字面量类型

```typescript [template-literal.ts]
// 基础模板类型
type World = 'world'
type Greeting = `hello ${World}`
// 'hello world'

// 联合类型组合
type EmailLocale = 'en' | 'fr' | 'de'
type MessageLocale = 'welcome' | 'goodbye'

type EmailLocaleIDs = `${MessageLocale}_${EmailLocale}`
// 'welcome_en' | 'welcome_fr' | 'welcome_de' | 'goodbye_en' | 'goodbye_fr' | 'goodbye_de'

// 事件类型
type EventName = `on${Capitalize<string>}`

const clickEvent: EventName = 'onClick'
const hoverEvent: EventName = 'onHover'
```

## 字符串工具类型

```typescript [string-utilities.ts]
// 内置字符串工具类型
type A = Lowercase<'HELLO'>  // 'hello'
type B = Uppercase<'hello'>  // 'HELLO'
type C = Capitalize<'hello'>  // 'Hello'
type D = Uncapitalize<'Hello'>  // 'hello'

// 自定义字符串操作
type TrimLeft<S extends string> = S extends ` ${infer Rest}` ? TrimLeft<Rest> : S
type TrimRight<S extends string> = S extends `${infer Rest} ` ? TrimRight<Rest> : S
type Trim<S extends string> = TrimLeft<TrimRight<S>>

type E = TrimLeft<'  hello'>  // 'hello'
type F = TrimRight<'hello  '>  // 'hello'
type G = Trim<'  hello  '>  // 'hello'
```

## 递归类型

```typescript [recursive-types.ts]
// 递归类型
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K]
}

interface Config {
  database: {
    host: string
    port: number
    options: {
      timeout: number
      retries: number
    }
  }
}

type PartialConfig = DeepPartial<Config>

// 递归提取
type DeepRequired<T> = T extends (...args: any[]) => any
  ? T
  : T extends object
  ? { [K in keyof T]-?: DeepRequired<T[K]> }
  : T

// 递归只读
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K]
}
```

## 类型操作

```typescript [type-operations.ts]
// keyof 操作符
interface User {
  name: string
  age: number
  email: string
}

type UserKeys = keyof User
// 'name' | 'age' | 'email'

// typeof 操作符
const user = { name: '张三', age: 25 }
type UserType = typeof user
// { name: string; age: number }

// in 操作符
type CreateObj<T> = {
  [K in keyof T]: T[K]
}

type Obj = CreateObj<User>
// { name: string; age: number; email: string }
```

## 高级类型组合

```typescript [advanced-combinations.ts]
// 类型组合
type UnionToIntersection<U> = (U extends any ? (k: U) => void : never) extends (
  k: infer I
) => void
  ? I
  : never

type A = UnionToIntersection<{ a: string } | { b: number }>
// { a: string } & { b: number }

// 最后一个类型
type Last<T extends any[]> = T extends [...any, infer L] ? L : never

type B = Last<[1, 2, 3]>  // 3

// 元组转联合类型
type TupleToUnion<T extends any[]> = T[number]

type C = TupleToUnion<[1, 2, 3]>  // 1 | 2 | 3

// 函数参数转元组
type Parameters<T extends (...args: any) => any> = T extends (
  ...args: infer P
) => any
  ? P
  : never
```

::: tip 提示
- 条件类型实现类型逻辑
- infer 用于类型推断
- 映射类型转换对象结构
- 模板字面量类型处理字符串
- 递归类型处理嵌套结构
:::
