# JavaScript 运算符与表达式

## 算术运算符

```javascript [arithmetic.js]
let a = 10
let b = 3

// 基本运算
console.log(a + b)   // 13  加法
console.log(a - b)   // 7   减法
console.log(a * b)   // 30  乘法
console.log(a / b)   // 3.333... 除法
console.log(a % b)   // 1   取余
console.log(a ** b)  // 1000 幂运算

// 自增自减
let x = 5
console.log(x++)     // 5（先返回后加）
console.log(x)       // 6
console.log(++x)     // 7（先加后返回）
console.log(x--)     // 7（先返回后减）
console.log(--x)     // 5（先减后返回）

// 特殊运算
console.log(10 / 0)          // Infinity
console.log(-10 / 0)         // -Infinity
console.log(0 / 0)           // NaN
console.log('10' - 5)        // 5（隐式转换）
console.log('10' + 5)        // '105'（字符串拼接）
```

## 赋值运算符

```javascript [assignment.js]
let x = 10

// 基本赋值
x = 10

// 复合赋值
x += 5    // x = x + 5    → 15
x -= 3    // x = x - 3    → 12
x *= 2    // x = x * 2    → 24
x /= 4    // x = x / 4    → 6
x %= 4    // x = x % 4    → 2
x **= 3   // x = x ** 3   → 8

// 链式赋值
let a, b, c
a = b = c = 100
console.log(a, b, c)  // 100 100 100

// 解构赋值
let [x1, y1] = [1, 2]
let { name, age } = { name: '张三', age: 25 }
```

## 比较运算符

```javascript [comparison.js]
let a = 10
let b = '10'

// 相等比较
console.log(a == b)    // true（宽松相等，类型转换）
console.log(a === b)   // false（严格相等，不转换）
console.log(a != b)    // false
console.log(a !== b)   // true

// 大小比较
console.log(a > 5)     // true
console.log(a < 15)    // true
console.log(a >= 10)   // true
console.log(a <= 10)   // true

// 特殊比较
console.log(NaN == NaN)    // false
console.log(NaN === NaN)   // false
console.log(null == undefined)   // true
console.log(null === undefined)  // false
console.log(0 == false)    // true
console.log(0 === false)   // false
console.log('' == false)   // true
console.log('' === false)  // false
```

## 逻辑运算符

```javascript [logical.js]
// 逻辑与 &&
console.log(true && true)     // true
console.log(true && false)    // false
console.log(false && true)    // false

// 逻辑或 ||
console.log(true || false)    // true
console.log(false || true)    // true
console.log(false || false)   // false

// 逻辑非 !
console.log(!true)            // false
console.log(!false)           // true
console.log(!0)               // true
console.log(!'')              // true
console.log(!null)            // true

// 短路求值
let user = null
let name = user || '匿名用户'
console.log(name)  // 匿名用户

// 空值合并 ??
let value = null ?? '默认值'
console.log(value)  // 默认值

let value2 = 0 ?? '默认值'
console.log(value2)  // 0（0 不是 null/undefined）

// 可选链 ?.
let obj = { user: { name: '张三' } }
console.log(obj?.user?.name)      // 张三
console.log(obj?.address?.city)   // undefined
```

## 位运算符

```javascript [bitwise.js]
// 位与 &
console.log(5 & 3)    // 1 (101 & 011 = 001)

// 位或 |
console.log(5 | 3)    // 7 (101 | 011 = 111)

// 位异或 ^
console.log(5 ^ 3)    // 6 (101 ^ 011 = 110)

// 位非 ~
console.log(~5)       // -6

// 左移 <<
console.log(5 << 1)   // 10 (101 << 1 = 1010)

// 右移 >>
console.log(5 >> 1)   // 2 (101 >> 1 = 10)

// 无符号右移 >>>
console.log(-5 >>> 1) // 2147483645
```

## 三元运算符

```javascript [ternary.js]
let age = 20

// 基础用法
let status = age >= 18 ? '成年' : '未成年'
console.log(status)  // 成年

// 嵌套使用
let score = 85
let grade = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 60 ? 'C' : 'D'
console.log(grade)  // B

// 替代简单 if-else
let isLoggedIn = true
isLoggedIn ? console.log('欢迎回来') : console.log('请登录')
```

## 类型运算符

```javascript [type-operators.js]
// typeof
console.log(typeof 'hello')      // string
console.log(typeof 123)          // number
console.log(typeof true)         // boolean
console.log(typeof undefined)    // undefined
console.log(typeof {})           // object
console.log(typeof [])           // object
console.log(typeof function(){}) // function

// instanceof
class Person {}
const p = new Person()
console.log(p instanceof Person)  // true
console.log([] instanceof Array)  // true

// in
const obj = { name: '张三', age: 25 }
console.log('name' in obj)   // true
console.log('email' in obj)  // false
```

## 逗号运算符

```javascript [comma.js]
// 逗号运算符
let x = (1, 2, 3)
console.log(x)  // 3（返回最后一个值）

// for 循环中使用
for (let i = 0, j = 10; i < j; i++, j--) {
  console.log(i, j)
}

// 变量声明
let a = 1, b = 2, c = 3
```

## 运算符优先级

```mermaid
graph TD
    A[运算符优先级从高到低] --> B[成员访问 . []]
    A --> C[函数调用 ()]
    A --> D[自增 ++ --]
    A --> E[逻辑非 ! 按位非 ~]
    A --> F[乘除 * / %]
    A --> G[加减 + -]
    A --> H[比较 < > <= >=]
    A --> I[相等 == === != !==]
    A --> J[逻辑与 &&]
    A --> K[逻辑或 ||]
    A --> L[三元 ? :]
    A --> M[赋值 = += -=]
    A --> N[逗号 ,]
```

| 优先级 | 运算符 | 说明 |
|--------|--------|------|
| 20 | `()` `[]` `.` | 成员访问 |
| 19 | `?.` | 可选链 |
| 18 | `new` `()` | 函数调用 |
| 17 | `++` `--` | 自增自减 |
| 16 | `!` `~` `+` `-` | 一元运算符 |
| 15 | `**` | 幂运算 |
| 14 | `*` `/` `%` | 乘除取余 |
| 13 | `+` `-` | 加减 |
| 12 | `<<` `>>` `>>>` | 位移 |
| 11 | `<` `<=` `>` `>=` | 比较 |
| 10 | `==` `===` `!=` `!==` | 相等 |
| 9 | `&` | 位与 |
| 8 | `^` | 位异或 |
| 7 | `|` | 位或 |
| 6 | `&&` | 逻辑与 |
| 5 | `||` | 逻辑或 |
| 4 | `??` | 空值合并 |
| 3 | `?:` | 三元 |
| 2 | `=` `+=` `-=` 等 | 赋值 |
| 1 | `,` | 逗号 |

::: tip 提示
- 使用括号明确运算顺序，提高代码可读性
- 优先使用 `===` 而不是 `==` 进行比较
- 使用 `??` 而不是 `||` 处理默认值，避免 0 和 '' 被误判
:::
