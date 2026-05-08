# let 和 const

ES6 新增了 `let` 和 `const` 关键字，用于声明变量和常量。

## let 关键字

### 基本用法

```javascript [let.js]
let a = 1
let b = 2, c = 3
```

### 块级作用域

```javascript [block-scope.js]
{
  let x = 10
  console.log(x)  // 10
}

console.log(x)  // ReferenceError: x is not defined
```

### 不存在变量提升

```javascript [no-hoisting.js]
console.log(a)  // undefined
var a = 1

console.log(b)  // ReferenceError: b is not defined
let b = 2
```

### 暂时性死区

```javascript [temporal-dead-zone.js]
let x = 'global'

function fn() {
  console.log(x)  // ReferenceError
  let x = 'local'
}

fn()
```

### for 循环中的作用域

```javascript [for-loop.js]
for (let i = 0; i < 3; i++) {
  setTimeout(() => {
    console.log(i)  // 0, 1, 2
  }, 100)
}

// 使用 var 会输出 3, 3, 3
```

## const 关键字

### 基本用法

```javascript [const.js]
const PI = 3.14159
const API_URL = 'https://api.example.com'
```

### 常量不可修改

```javascript [const-error.js]
const x = 10
x = 20  // TypeError: Assignment to constant variable
```

### 对象属性可修改

```javascript [const-object.js]
const obj = { name: '张三' }

obj.name = '李四'  // 可以修改
obj.age = 25       // 可以添加新属性

// 但不可重新赋值
obj = {}  // TypeError
```

### 数组元素可修改

```javascript [const-array.js]
const arr = [1, 2, 3]

arr.push(4)      // 可以修改
arr[0] = 10      // 可以修改

// 但不可重新赋值
arr = []  // TypeError
```

## let/const vs var

| 特性 | var | let | const |
|------|-----|-----|-------|
| 作用域 | 函数作用域 | 块级作用域 | 块级作用域 |
| 变量提升 | ✅ | ❌ | ❌ |
| 重复声明 | ✅ | ❌ | ❌ |
| 暂时性死区 | ❌ | ✅ | ✅ |
| 全局变量 | 挂载到 window | 不挂载 | 不挂载 |

## 最佳实践

```javascript [best-practice.js]
// 优先使用 const
const name = '张三'
const age = 25

// 需要重新赋值时使用 let
let count = 0
count++

// 避免使用 var
// var x = 1  // 不推荐
```

::: tip 提示
- 优先使用 const，需要重新赋值时使用 let
- 避免使用 var
- const 声明的对象属性可以修改
:::
