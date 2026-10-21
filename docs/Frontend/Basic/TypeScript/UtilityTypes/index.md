# TypeScript 工具类型

## 内置工具类型

TypeScript 提供了许多内置工具类型，用于常见的类型转换操作。

```typescript [utility-types.ts]
// Partial<T> - 将所有属性变为可选
interface User {
  id: string
  name: string
  email: string
  age: number
}

type PartialUser = Partial<User>
// 结果：{
//   id?: string
//   name?: string
//   email?: string
//   age?: number
// }

function updateUser(id: string, updates: Partial<User>) {
  console.log('更新用户:', id, updates)
}

updateUser('1', { name: '李四' })
```

## Required

```typescript [required.ts]
// Required<T> - 将所有属性变为必填
interface Config {
  host?: string
  port?: number
  timeout?: number
}

const defaultConfig: Required<Config> = {
  host: 'localhost',
  port: 3000,
  timeout: 5000
}

// 使用场景：确保配置完整
function initialize(config: Required<Config>) {
  console.log(`连接到 ${config.host}:${config.port}`)
}

initialize(defaultConfig)
```

## Readonly

```typescript [readonly.ts]
// Readonly<T> - 将所有属性变为只读
interface User {
  name: string
  age: number
  email: string
}

const readonlyUser: Readonly<User> = {
  name: '张三',
  age: 25,
  email: 'zhangsan@example.com'
}

// readonlyUser.name = '李四'  // 错误：只读属性

// 使用场景：常量对象
const API_ENDPOINTS: Readonly<Record<string, string>> = {
  users: '/api/users',
  posts: '/api/posts',
  comments: '/api/comments'
}
```

## Record<K, T>

```typescript [record.ts]
// Record<K, T> - 创建对象类型
type Role = 'admin' | 'user' | 'guest'
type Permissions = 'read' | 'write' | 'delete'

const rolePermissions: Record<Role, Permissions[]> = {
  admin: ['read', 'write', 'delete'],
  user: ['read', 'write'],
  guest: ['read']
}

// 使用场景：枚举映射
type Status = 'pending' | 'success' | 'error'
type StatusMessage = string

const statusMessages: Record<Status, StatusMessage> = {
  pending: '处理中...',
  success: '操作成功',
  error: '操作失败'
}
```

## Pick<T, K>

```typescript [pick.ts]
// Pick<T, K> - 选择部分属性
interface User {
  id: string
  name: string
  email: string
  age: number
  password: string
}

// 只选择公开信息
type PublicUser = Pick<User, 'id' | 'name' | 'email'>

function getPublicUser(user: User): PublicUser {
  return {
    id: user.id,
    name: user.name,
    email: user.email
  }
}

// 使用场景：表单数据
type UserFormData = Pick<User, 'name' | 'email' | 'age'>
```

## Omit<T, K>

```typescript [omit.ts]
// Omit<T, K> - 排除部分属性
interface User {
  id: string
  name: string
  email: string
  age: number
  password: string
}

// 排除敏感信息
type SafeUser = Omit<User, 'password'>

function getSafeUser(user: User): SafeUser {
  const { password, ...safeUser } = user
  return safeUser
}

// 使用场景：创建新用户（排除 id）
type CreateUserInput = Omit<User, 'id'>

function createUser(input: CreateUserInput) {
  console.log('创建用户:', input)
}
```

## Exclude<T, U>

```typescript [exclude.ts]
// Exclude<T, U> - 从联合类型中排除
type Status = 'pending' | 'success' | 'error' | 'cancelled'

type ActiveStatus = Exclude<Status, 'cancelled'>
// 'pending' | 'success' | 'error'

type FinalStatus = Exclude<Status, 'pending' | 'success'>
// 'error' | 'cancelled'

// 使用场景：过滤类型
type EventTypes = 'click' | 'hover' | 'scroll' | 'resize'
type MouseEventTypes = Exclude<EventTypes, 'scroll' | 'resize'>
// 'click' | 'hover'
```

## Extract<T, U>

```typescript [extract.ts]
// Extract<T, U> - 从联合类型中提取
type Status = 'pending' | 'success' | 'error' | 'cancelled'

type SuccessStatus = Extract<Status, 'success' | 'pending'>
// 'success' | 'pending'

type ErrorStatus = Extract<Status, 'error' | 'cancelled'>
// 'error' | 'cancelled'

// 使用场景：类型提取
type EventTypes = 'click' | 'hover' | 'scroll' | 'resize'
type MouseEventTypes = Extract<EventTypes, 'click' | 'hover'>
// 'click' | 'hover'
```

## NonNullable

```typescript [nonnullable.ts]
// NonNullable<T> - 排除 null 和 undefined
type Status = 'pending' | 'success' | 'error' | null | undefined

type ValidStatus = NonNullable<Status>
// 'pending' | 'success' | 'error'

// 使用场景：安全类型
type MaybeString = string | null | undefined
type SafeString = NonNullable<MaybeString>
// string

function processValue(value: MaybeString) {
  if (value !== null && value !== undefined) {
    const safeValue: SafeString = value
    console.log(safeValue.toUpperCase())
  }
}
```

## Parameters

```typescript [parameters.ts]
// Parameters<T> - 获取函数参数类型
function createUser(name: string, age: number, email: string) {
  console.log('创建用户:', name, age, email)
}

type CreateUserParams = Parameters<typeof createUser>
// [name: string, age: number, email: string]

// 使用场景：函数包装
function withLogging<T extends (...args: any[]) => any>(
  fn: T,
  ...args: Parameters<T>
): ReturnType<T> {
  console.log('调用函数:', fn.name, args)
  return fn(...args)
}

withLogging(createUser, '张三', 25, 'zhangsan@example.com')
```

## ReturnType

```typescript [returntype.ts]
// ReturnType<T> - 获取函数返回值类型
function createUser(name: string, age: number) {
  return { id: Date.now(), name, age }
}

type User = ReturnType<typeof createUser>
// { id: number; name: string; age: number }

// 使用场景：API 响应类型
async function fetchUser(id: string) {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}

type UserResponse = ReturnType<typeof fetchUser>
// Promise<any>

// 使用场景：组件 props 类型
function UserCard(props: { name: string; age: number }) {
  return `<div>${props.name}, ${props.age}岁</div>`
}

type UserCardProps = Parameters<typeof UserCard>[0]
```

## ConstructorParameters

```typescript [constructor-parameters.ts]
// ConstructorParameters<T> - 获取构造函数参数类型
class User {
  constructor(
    public name: string,
    public age: number,
    public email: string
  ) {}
}

type UserConstructorParams = ConstructorParameters<typeof User>
// [name: string, age: number, email: string]

// 使用场景：工厂函数
function createInstance<T extends new (...args: any[]) => any>(
  ctor: T,
  ...args: ConstructorParameters<T>
): InstanceType<T> {
  return new ctor(...args)
}

const user = createInstance(User, '张三', 25, 'zhangsan@example.com')
```

## InstanceType

```typescript [instancetype.ts]
// InstanceType<T> - 获取实例类型
class User {
  name: string
  age: number

  constructor(name: string, age: number) {
    this.name = name
    this.age = age
  }
}

type UserType = InstanceType<typeof User>
// User

// 使用场景：泛型工厂
class BaseService<T> {
  protected items: T[] = []

  add(item: T) {
    this.items.push(item)
  }

  getAll(): T[] {
    return this.items
  }
}

class UserService extends BaseService<InstanceType<typeof User>> {
  // 继承 BaseService<User>
}
```

## ThisParameterType

```typescript [this-parameter-type.ts]
// ThisParameterType<T> - 获取 this 参数类型
function toHex(this: Number) {
  return this.toString(16)
}

type ThisType = ThisParameterType<typeof toHex>
// Number

// 使用场景：绑定函数
function bindThis<T extends (this: any, ...args: any[]) => any>(
  fn: T,
  thisArg: ThisParameterType<T>
) {
  return fn.bind(thisArg)
}

const num = 255
const boundFn = bindThis(toHex, num)
console.log(boundFn())  // 'ff'
```

## OmitThisParameter

```typescript [omit-this-parameter.ts]
// OmitThisParameter<T> - 移除 this 参数类型
function toHex(this: Number) {
  return this.toString(16)
}

type NoThisType = OmitThisParameter<typeof toHex>
// () => string

// 使用场景：函数转换
function removeThis<T extends (this: any, ...args: any[]) => any>(
  fn: T
): OmitThisParameter<T> {
  return fn as OmitThisParameter<T>
}

const cleanFn = removeThis(toHex)
```

## ThisType

```typescript [this-type.ts]
// ThisType<T> - 标记 this 类型
interface UserMethods {
  getName(): string
  getAge(): number
}

const userMethods: UserMethods & ThisType<{ name: string; age: number }> = {
  getName() {
    return this.name
  },
  getAge() {
    return this.age
  }
}

// 使用场景：对象字面量
function createObject<T extends object>(
  methods: T & ThisType<{ data: string }>
): T {
  return methods
}

const obj = createObject({
  getData() {
    return this.data
  }
})
```

::: tip 提示
- Partial 用于更新操作
- Required 用于配置验证
- Readonly 用于不可变数据
- Pick 和 Omit 用于类型筛选
- Parameters 和 ReturnType 用于函数类型提取

:::

## 与「表单与校验工程」专题的分工（第 182 天补充）
本页讲 **工具类型的语法**：`Partial` / `Pick` / `Omit` / 条件类型 / 映射类型。**用这些类型把 schema 推导成表单类型**的具体做法（`z.infer`、`Path<T>` 约束字段名）由专题回答。

| 问题 | 本页回答 | 专题回答 |
| --- | --- | --- |
| 类型怎么写 | 映射类型、条件类型、`infer` 的语法 | 从运行时 schema 推导表单值类型，做到「改字段名就编译报错」 |
| 字段名怎么约束 | `keyof T` 与模板字面量类型 | `Path<T>` 用于 `setField("a.b.c")` 的嵌套路径 |
| 错误结构怎么建模 | 联合类型与可辨识字段 | `errors` 为什么是 `Partial<Record<keyof T, string>>` |

::: warning 本页特有的一个坑
递归的 `Path<T>`（`${K}.${Path<T[K]>}`）在字段层级深、字段数多时会撞上 TypeScript 的实例化深度上限，报 `Type instantiation is excessively deep and possibly infinite`。三种处置按代价从低到高：把表单结构**压平**（嵌套不超过 2 层）、给递归加深度计数参数（`Path<T, Depth>`，超过 4 层返回 `never`）、或只对「需要路径访问的字段」生成 `Path`（白名单）。不要靠 `// @ts-expect-error` 压掉——那会把真正的字段名错误一起吞掉。
:::

