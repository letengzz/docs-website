# ES10

ECMAScript 2019（ES10）于 2019 年 6 月发布。

- 官方规范：https://262.ecma-international.org/10.0/

## Array.prototype.flat()

```javascript [flat.js]
const arr = [1, 2, [3, 4, [5, 6]]]

console.log(arr.flat())      // [1, 2, 3, 4, [5, 6]]
console.log(arr.flat(2))     // [1, 2, 3, 4, 5, 6]
console.log(arr.flat(Infinity))  // [1, 2, 3, 4, 5, 6]
```

## Array.prototype.flatMap()

```javascript [flatMap.js]
const arr = ['Hello World', 'Good Morning']

const result = arr.flatMap(str => str.split(' '))
console.log(result)  // ['Hello', 'World', 'Good', 'Morning']
```

## Object.fromEntries()

```javascript [fromEntries.js]
const entries = [
  ['a', 1],
  ['b', 2],
  ['c', 3]
]

const obj = Object.fromEntries(entries)
console.log(obj)  // { a: 1, b: 2, c: 3 }

// Map 转对象
const map = new Map([['name', '张三'], ['age', 25]])
const person = Object.fromEntries(map)
console.log(person)  // { name: '张三', age: 25 }
```

## String.prototype.trimStart() / trimEnd()

```javascript [trim.js]
const str = '  Hello World  '

console.log(str.trimStart())  // 'Hello World  '
console.log(str.trimEnd())    // '  Hello World'
```

## Symbol.prototype.description

```javascript [description.js]
const sym = Symbol('description')

console.log(sym.description)  // 'description'
```

## 可选 Catch 绑定

```javascript [optional-catch.js]
// ES10 之前
try {
  // 代码
} catch (e) {
  console.error('出错了')
}

// ES10 开始
try {
  // 代码
} catch {
  console.error('出错了')
}
```

## JSON 超集

```javascript [json.js]
// ES10 之前，JSON 不能包含未转义的换行符
const json1 = '{"name": "张三"}'

// ES10 开始，JSON 可以包含未转义的换行符
const json2 = `{
  "name": "张三"
}`
```

## Function.prototype.toString()

```javascript [toString.js]
function fn(a, b) {
  return a + b
}

console.log(fn.toString())
// function fn(a, b) {
//   return a + b
// }
```

## 稳定 Array.prototype.sort()

```javascript [sort.js]
const arr = [
  { name: 'A', order: 1 },
  { name: 'B', order: 1 },
  { name: 'C', order: 2 }
]

arr.sort((a, b) => a.order - b.order)
// 相同 order 的元素保持原有顺序
```

::: tip 提示
- flat() 用于扁平化数组
- fromEntries() 是 Object.entries() 的反向操作
- 可选 Catch 绑定让错误处理更简洁
:::
