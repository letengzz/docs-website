# 数组新方法

ES6 为数组添加了多个新方法。

## Array.from()

```javascript [from.js]
// 从类数组对象转换
const str = 'hello'
const arr = Array.from(str)

console.log(arr)  // ['h', 'e', 'l', 'l', 'o']

// 从 Set 转换
const set = new Set([1, 2, 3])
const arr2 = Array.from(set)

console.log(arr2)  // [1, 2, 3]

// 映射函数
const arr3 = Array.from([1, 2, 3], x => x * 2)

console.log(arr3)  // [2, 4, 6]
```

## Array.of()

```javascript [of.js]
console.log(Array.of(1, 2, 3))  // [1, 2, 3]
console.log(Array.of(1))        // [1]
console.log(Array.of())         // []
```

## Array.prototype.find()

```javascript [find.js]
const arr = [1, 2, 3, 4, 5]

const found = arr.find(item => item > 3)
console.log(found)  // 4

const users = [
  { id: 1, name: '张三' },
  { id: 2, name: '李四' }
]

const user = users.find(u => u.id === 2)
console.log(user)  // { id: 2, name: '李四' }
```

## Array.prototype.findIndex()

```javascript [findIndex.js]
const arr = [1, 2, 3, 4, 5]

const index = arr.findIndex(item => item > 3)
console.log(index)  // 3

const notFound = arr.findIndex(item => item > 10)
console.log(notFound)  // -1
```

## Array.prototype.fill()

```javascript [fill.js]
const arr = new Array(5).fill(0)

console.log(arr)  // [0, 0, 0, 0, 0]

const arr2 = [1, 2, 3, 4, 5]
arr2.fill(0, 1, 3)

console.log(arr2)  // [1, 0, 0, 4, 5]
```

## Array.prototype.copyWithin()

```javascript [copyWithin.js]
const arr = [1, 2, 3, 4, 5]

arr.copyWithin(0, 3, 4)

console.log(arr)  // [4, 2, 3, 4, 5]
```

## Array.prototype.entries()

```javascript [entries.js]
const arr = ['a', 'b', 'c']

for (const [index, value] of arr.entries()) {
  console.log(`${index}: ${value}`)
}
// 0: a
// 1: b
// 2: c
```

## Array.prototype.keys()

```javascript [keys.js]
const arr = ['a', 'b', 'c']

for (const index of arr.keys()) {
  console.log(index)  // 0, 1, 2
}
```

## Array.prototype.values()

```javascript [values.js]
const arr = ['a', 'b', 'c']

for (const value of arr.values()) {
  console.log(value)  // a, b, c
}
```

## Array.prototype.includes()

```javascript [includes.js]
const arr = [1, 2, 3]

console.log(arr.includes(2))   // true
console.log(arr.includes(4))   // false
console.log(arr.includes(2, 2)) // false
```

::: tip 提示
- Array.from() 用于转换类数组对象
- find() 返回第一个匹配的元素
- findIndex() 返回第一个匹配元素的索引
- includes() 检查数组是否包含某值
:::
