# 展开/剩余语法

展开（Spread）和剩余（Rest）语法使用 `...` 操作符。

## 展开语法

### 数组展开

```javascript [array-spread.js]
const arr1 = [1, 2, 3]
const arr2 = [4, 5, 6]

const combined = [...arr1, ...arr2]
console.log(combined)  // [1, 2, 3, 4, 5, 6]
```

### 对象展开

```javascript [object-spread.js]
const obj1 = { a: 1, b: 2 }
const obj2 = { ...obj1, c: 3 }

console.log(obj2)  // { a: 1, b: 2, c: 3 }
```

### 函数参数展开

```javascript [fn-spread.js]
function sum(a, b, c) {
  return a + b + c
}

const args = [1, 2, 3]
console.log(sum(...args))  // 6
```

## 剩余参数

### 函数剩余参数

```javascript [fn-rest.js]
function sum(...args) {
  return args.reduce((acc, curr) => acc + curr, 0)
}

console.log(sum(1, 2, 3))  // 6
console.log(sum(1, 2, 3, 4, 5))  // 15
```

### 数组剩余元素

```javascript [array-rest.js]
const [first, ...rest] = [1, 2, 3, 4, 5]

console.log(first)  // 1
console.log(rest)   // [2, 3, 4, 5]
```

### 对象剩余属性

```javascript [object-rest.js]
const { a, ...rest } = { a: 1, b: 2, c: 3 }

console.log(a)     // 1
console.log(rest)  // { b: 2, c: 3 }
```

::: tip 提示
- 展开语法用于合并数组/对象
- 剩余参数用于收集多余参数
- `...` 在不同位置有不同含义
:::
