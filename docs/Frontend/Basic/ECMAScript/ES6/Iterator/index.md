# 迭代器

迭代器是一种接口机制，为不同数据结构提供统一的访问方式。

## 基本概念

### 迭代器协议

```javascript [iterator.js]
const iterator = {
  current: 0,
  last: 3,
  
  next() {
    if (this.current < this.last) {
      return { value: this.current++, done: false }
    }
    return { value: undefined, done: true }
  }
}

console.log(iterator.next())  // { value: 0, done: false }
console.log(iterator.next())  // { value: 1, done: false }
console.log(iterator.next())  // { value: 2, done: false }
console.log(iterator.next())  // { value: 3, done: true }
```

## 可迭代对象

### 实现迭代器接口

```javascript [iterable.js]
const myIterable = {
  [Symbol.iterator]() {
    let count = 0
    return {
      next() {
        if (count < 3) {
          return { value: count++, done: false }
        }
        return { value: undefined, done: true }
      }
    }
  }
}

for (const value of myIterable) {
  console.log(value)  // 0, 1, 2
}
```

## 内置可迭代对象

### 数组

```javascript [array.js]
const arr = [1, 2, 3]

for (const item of arr) {
  console.log(item)
}
```

### 字符串

```javascript [string.js]
const str = 'abc'

for (const char of str) {
  console.log(char)  // a, b, c
}
```

### Map

```javascript [map.js]
const map = new Map([
  ['a', 1],
  ['b', 2]
])

for (const [key, value] of map) {
  console.log(key, value)
}
```

### Set

```javascript [set.js]
const set = new Set([1, 2, 3])

for (const item of set) {
  console.log(item)  // 1, 2, 3
}
```

## 自定义迭代器

### 范围迭代器

```javascript [range.js]
class Range {
  constructor(start, end) {
    this.start = start
    this.end = end
  }
  
  [Symbol.iterator]() {
    let current = this.start
    const end = this.end
    
    return {
      next() {
        if (current <= end) {
          return { value: current++, done: false }
        }
        return { value: undefined, done: true }
      }
    }
  }
}

for (const num of new Range(1, 5)) {
  console.log(num)  // 1, 2, 3, 4, 5
}
```

### 链表迭代器

```javascript [linked-list.js]
class Node {
  constructor(value) {
    this.value = value
    this.next = null
  }
}

class LinkedList {
  constructor() {
    this.head = null
  }
  
  add(value) {
    const node = new Node(value)
    if (!this.head) {
      this.head = node
    } else {
      let current = this.head
      while (current.next) {
        current = current.next
      }
      current.next = node
    }
  }
  
  [Symbol.iterator]() {
    let current = this.head
    
    return {
      next() {
        if (current) {
          const value = current.value
          current = current.next
          return { value, done: false }
        }
        return { value: undefined, done: true }
      }
    }
  }
}

const list = new LinkedList()
list.add(1)
list.add(2)
list.add(3)

for (const value of list) {
  console.log(value)  // 1, 2, 3
}
```

## 展开运算符

```javascript [spread.js]
const arr = [1, 2, 3]

console.log(...arr)  // 1 2 3

const combined = [...arr, 4, 5]
console.log(combined)  // [1, 2, 3, 4, 5]
```

::: tip 提示
- 迭代器提供统一的数据访问方式
- 实现 Symbol.iterator 接口使对象可迭代
- for...of 用于遍历可迭代对象
:::
