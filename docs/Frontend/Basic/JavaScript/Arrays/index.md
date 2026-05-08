# JavaScript 数组操作

## 数组创建

```javascript [array-create.js]
// 数组字面量
const arr1 = [1, 2, 3, 4, 5]

// Array 构造函数
const arr2 = new Array(5)        // [empty × 5]
const arr3 = new Array(1, 2, 3)  // [1, 2, 3]

// Array.of
const arr4 = Array.of(1, 2, 3)   // [1, 2, 3]
const arr5 = Array.of(5)         // [5]

// Array.from
const arr6 = Array.from('hello') // ['h', 'e', 'l', 'l', 'o']
const arr7 = Array.from({ length: 5 }, (_, i) => i)  // [0, 1, 2, 3, 4]

// 展开运算符
const arr8 = [...arr1, 6, 7]     // [1, 2, 3, 4, 5, 6, 7]
```

## 数组方法

### 添加/删除元素

```javascript [array-modify.js]
const arr = [1, 2, 3, 4, 5]

// push - 末尾添加
arr.push(6)
console.log(arr)  // [1, 2, 3, 4, 5, 6]

// pop - 末尾删除
arr.pop()
console.log(arr)  // [1, 2, 3, 4, 5]

// unshift - 开头添加
arr.unshift(0)
console.log(arr)  // [0, 1, 2, 3, 4, 5]

// shift - 开头删除
arr.shift()
console.log(arr)  // [1, 2, 3, 4, 5]

// splice - 任意位置操作
arr.splice(2, 1)           // 删除索引 2 的元素
console.log(arr)           // [1, 2, 4, 5]

arr.splice(1, 0, 'a', 'b') // 插入元素
console.log(arr)           // [1, 'a', 'b', 2, 4, 5]

arr.splice(2, 1, 'c')      // 替换元素
console.log(arr)           // [1, 'a', 'c', 2, 4, 5]
```

### 数组转换

```javascript [array-transform.js]
const arr = [1, 2, 3, 4, 5]

// slice - 浅拷贝
const copy = arr.slice()
const partial = arr.slice(1, 3)  // [2, 3]

// concat - 合并
const arr2 = [6, 7]
const merged = arr.concat(arr2)
console.log(merged)  // [1, 2, 3, 4, 5, 6, 7]

// join - 转字符串
console.log(arr.join('-'))  // '1-2-3-4-5'

// toString
console.log(arr.toString())  // '1,2,3,4,5'

// 展开为参数
console.log(Math.max(...arr))  // 5
```

### 查找元素

```javascript [array-find.js]
const arr = [
  { id: 1, name: '张三', age: 25 },
  { id: 2, name: '李四', age: 30 },
  { id: 3, name: '王五', age: 35 }
]

// indexOf / lastIndexOf
const nums = [1, 2, 3, 2, 1]
console.log(nums.indexOf(2))       // 1
console.log(nums.lastIndexOf(2))   // 3

// includes
console.log(nums.includes(3))      // true
console.log(nums.includes(9))      // false

// find - 查找第一个匹配
const user = arr.find(u => u.age > 28)
console.log(user)  // { id: 2, name: '李四', age: 30 }

// findIndex - 查找索引
const index = arr.findIndex(u => u.id === 3)
console.log(index)  // 2

// some / every
console.log(arr.some(u => u.age > 30))   // true
console.log(arr.every(u => u.age > 20))  // true
```

### 遍历方法

```javascript [array-iterate.js]
const arr = [1, 2, 3, 4, 5]

// forEach
arr.forEach((item, index) => {
  console.log(`${index}: ${item}`)
})

// map - 转换
const doubled = arr.map(x => x * 2)
console.log(doubled)  // [2, 4, 6, 8, 10]

// filter - 过滤
const evens = arr.filter(x => x % 2 === 0)
console.log(evens)  // [2, 4]

// reduce - 归并
const sum = arr.reduce((acc, cur) => acc + cur, 0)
console.log(sum)  // 15

// reduceRight - 从右归并
const reversed = arr.reduceRight((acc, cur) => [...acc, cur], [])
console.log(reversed)  // [5, 4, 3, 2, 1]

// flatMap - map + flat
const sentences = ['Hello World', 'JavaScript is great']
const words = sentences.flatMap(s => s.split(' '))
console.log(words)  // ['Hello', 'World', 'JavaScript', 'is', 'great']
```

### 排序方法

```javascript [array-sort.js]
const nums = [3, 1, 4, 1, 5, 9, 2, 6]

// sort - 原地排序
nums.sort((a, b) => a - b)
console.log(nums)  // [1, 1, 2, 3, 4, 5, 6, 9]

// reverse - 反转
nums.reverse()
console.log(nums)  // [9, 6, 5, 4, 3, 2, 1, 1]

// 对象数组排序
const users = [
  { name: '张三', age: 25 },
  { name: '李四', age: 20 },
  { name: '王五', age: 30 }
]

users.sort((a, b) => a.age - b.age)
console.log(users)

// 多条件排序
users.sort((a, b) => {
  if (a.age !== b.age) return a.age - b.age
  return a.name.localeCompare(b.name)
})
```

### 填充方法

```javascript [array-fill.js]
// fill - 填充
const arr1 = new Array(5).fill(0)
console.log(arr1)  // [0, 0, 0, 0, 0]

// copyWithin - 复制
const arr2 = [1, 2, 3, 4, 5]
arr2.copyWithin(0, 3, 4)
console.log(arr2)  // [4, 2, 3, 4, 5]

// at - 负索引访问
const arr3 = [1, 2, 3, 4, 5]
console.log(arr3.at(-1))   // 5
console.log(arr3.at(-2))   // 4
```

## 数组解构

```javascript [array-destructuring.js]
const arr = [1, 2, 3, 4, 5]

// 基础解构
const [a, b] = arr
console.log(a, b)  // 1 2

// 跳过元素
const [first, , third] = arr
console.log(first, third)  // 1 3

// 剩余元素
const [head, ...tail] = arr
console.log(head)   // 1
console.log(tail)   // [2, 3, 4, 5]

// 默认值
const [x = 0, y = 0, z = 0] = [1, 2]
console.log(x, y, z)  // 1 2 0

// 交换变量
let m = 1, n = 2
;[m, n] = [n, m]
console.log(m, n)  // 2 1
```

## 数组去重

```javascript [array-unique.js]
const arr = [1, 2, 2, 3, 3, 4, 5, 5]

// Set 去重
const unique1 = [...new Set(arr)]
console.log(unique1)  // [1, 2, 3, 4, 5]

// filter + indexOf
const unique2 = arr.filter((item, index) => arr.indexOf(item) === index)

// reduce
const unique3 = arr.reduce((acc, cur) => {
  if (!acc.includes(cur)) acc.push(cur)
  return acc
}, [])
```

## 数组合并

```javascript [array-merge.js]
const arr1 = [1, 2]
const arr2 = [3, 4]
const arr3 = [5, 6]

// concat
const merged1 = arr1.concat(arr2, arr3)

// 展开运算符
const merged2 = [...arr1, ...arr2, ...arr3]

// flat
const nested = [[1, 2], [3, 4], [5, 6]]
const flattened = nested.flat()
console.log(flattened)  // [1, 2, 3, 4, 5, 6]

// 深度扁平
const deepNested = [1, [2, [3, [4]]]]
console.log(deepNested.flat(Infinity))  // [1, 2, 3, 4]
```

## 类数组转换

```javascript [array-like.js]
// arguments
function sum() {
  const args = Array.from(arguments)
  return args.reduce((a, b) => a + b, 0)
}

console.log(sum(1, 2, 3, 4, 5))  // 15

// NodeList
const elements = document.querySelectorAll('div')
const arr = Array.from(elements)

// 字符串
const chars = Array.from('hello')
console.log(chars)  // ['h', 'e', 'l', 'l', 'o']
```

## 常用数组算法

```javascript [array-algorithms.js]
// 最大值/最小值
const nums = [3, 1, 4, 1, 5, 9]
const max = Math.max(...nums)
const min = Math.min(...nums)

// 求和
const sum = nums.reduce((a, b) => a + b, 0)

// 平均值
const avg = sum / nums.length

// 分组
const users = [
  { name: '张三', age: 20 },
  { name: '李四', age: 25 },
  { name: '王五', age: 20 }
]

const grouped = users.reduce((acc, user) => {
  const key = user.age
  if (!acc[key]) acc[key] = []
  acc[key].push(user)
  return acc
}, {})

console.log(grouped)
// { 20: [{...}, {...}], 25: [{...}] }

// 扁平化对象数组
const flatUsers = users.flatMap(u => [u.name, u.age])
```

::: tip 提示
- 优先使用 `for...of` 或数组方法遍历
- `map`、`filter`、`reduce` 不会修改原数组
- `sort`、`reverse`、`splice` 会修改原数组
- 使用 `Set` 去重是最简洁的方式
:::
