# 模板字符串

模板字符串使用反引号 `` ` `` 包裹，支持变量插值和多行字符串。

## 基本用法

```javascript [basic.js]
const name = '张三'
const age = 25

const str = `我叫${name}，今年${age}岁`
console.log(str)  // 我叫张三，今年25岁
```

## 多行字符串

```javascript [multiline.js]
const html = `
  <div>
    <h1>标题</h1>
    <p>内容</p>
  </div>
`

console.log(html)
```

## 表达式

```javascript [expression.js]
const a = 10, b = 20

console.log(`${a} + ${b} = ${a + b}`)  // 10 + 20 = 30
console.log(`${a > b ? 'a 大' : 'b 大'}`)
```

## 嵌套模板

```javascript [nested.js]
const user = { name: '张三' }

const str = `Hello, ${user.name ? `${user.name}!` : 'Guest!'}`
console.log(str)  // Hello, 张三!
```

## 标签模板

```javascript [tagged.js]
function tag(strings, ...values) {
  console.log(strings)  // ['Hello ', '!']
  console.log(values)   // ['张三']
  
  return strings[0] + values[0] + strings[1]
}

const name = '张三'
const result = tag`Hello ${name}!`
console.log(result)  // Hello 张三!
```

## 转义

```javascript [escape.js]
const str = `反引号: \``
const newline = `换行: \n`

console.log(str)
console.log(newline)
```

::: tip 提示
- 模板字符串让字符串拼接更简洁
- 支持多行字符串
- 可以包含任意表达式
:::
