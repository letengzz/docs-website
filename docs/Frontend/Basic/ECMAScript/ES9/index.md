# ES9

ECMAScript 2018（ES9）于 2018 年 6 月发布。

- 官方规范：https://262.ecma-international.org/9.0/

## Rest/Spread 属性

### 对象展开

```javascript [spread.js]
const obj1 = { a: 1, b: 2 }
const obj2 = { ...obj1, c: 3 }

console.log(obj2)  // { a: 1, b: 2, c: 3 }
```

### 对象 Rest

```javascript [rest.js]
const { a, ...rest } = { a: 1, b: 2, c: 3 }

console.log(a)     // 1
console.log(rest)  // { b: 2, c: 3 }
```

## Promise.finally()

```javascript [finally.js]
fetch('/api/users')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err))
  .finally(() => {
    console.log('请求完成')
  })
```

## 异步迭代

### for await...of

```javascript [async-iterator.js]
async function readChunks(reader) {
  for await (const chunk of reader) {
    console.log(chunk)
  }
}
```

## 正则表达式命名捕获组

```javascript [named-groups.js]
const re = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/
const match = re.exec('2024-01-15')

console.log(match.groups.year)   // 2024
console.log(match.groups.month)  // 01
console.log(match.groups.day)    // 15
```

## 正则表达式反向断言

```javascript [lookbehind.js]
// 正向后行断言
const re1 = /(?<=\$)\d+/
console.log('$100'.match(re1)[0])  // 100

// 负向后行断言
const re2 = /(?<!\$)\d+/
console.log('€100'.match(re2)[0])  // 100
```

## 正则表达式 dotAll 模式

```javascript [dotAll.js]
const re = /foo.bar/s
console.log(re.test('foo\nbar'))  // true
```

## 模板字符串修订

```javascript [template.js]
function tag(strings, ...values) {
  return strings.reduce((result, str, i) => {
    return result + str + (values[i] || '')
  }, '')
}

const name = '张三'
const result = tag`Hello, ${name}!`
console.log(result)  // Hello, 张三!
```

::: tip 提示
- 对象展开/Rest 让对象操作更简洁
- Promise.finally() 用于清理操作
- 异步迭代简化异步数据流处理
:::
