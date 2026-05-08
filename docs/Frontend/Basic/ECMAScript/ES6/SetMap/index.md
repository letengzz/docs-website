# Set 和 Map

ES6 新增了 Set 和 Map 两种数据结构。

## Set

### 基本用法

```javascript [basic.js]
const set = new Set([1, 2, 3, 3, 4])

console.log(set)  // Set { 1, 2, 3, 4 }
```

### 添加和删除

```javascript [add-delete.js]
const set = new Set()

set.add(1)
set.add(2)
set.add(2)  // 重复值不会添加

console.log(set)  // Set { 1, 2 }

set.delete(1)
console.log(set)  // Set { 2 }

set.clear()
console.log(set)  // Set {}
```

### 检查元素

```javascript [has.js]
const set = new Set([1, 2, 3])

console.log(set.has(1))  // true
console.log(set.has(4))  // false
console.log(set.size)    // 3
```

### 遍历

```javascript [iterate.js]
const set = new Set([1, 2, 3])

for (const item of set) {
  console.log(item)  // 1, 2, 3
}

set.forEach(item => console.log(item))
```

### 数组去重

```javascript [dedup.js]
const arr = [1, 2, 2, 3, 3, 4]

const unique = [...new Set(arr)]
console.log(unique)  // [1, 2, 3, 4]
```

### 集合运算

```javascript [operations.js]
const a = new Set([1, 2, 3])
const b = new Set([2, 3, 4])

// 并集
const union = new Set([...a, ...b])
console.log(union)  // Set { 1, 2, 3, 4 }

// 交集
const intersection = new Set([...a].filter(x => b.has(x)))
console.log(intersection)  // Set { 2, 3 }

// 差集
const difference = new Set([...a].filter(x => !b.has(x)))
console.log(difference)  // Set { 1 }
```

## Map

### 基本用法

```javascript [map-basic.js]
const map = new Map()

map.set('name', '张三')
map.set('age', 25)

console.log(map.get('name'))  // 张三
console.log(map.get('age'))   // 25
```

### 初始化

```javascript [map-init.js]
const map = new Map([
  ['name', '张三'],
  ['age', 25]
])

console.log(map.get('name'))  // 张三
```

### 添加和删除

```javascript [map-delete.js]
const map = new Map()

map.set('name', '张三')
map.set('age', 25)

console.log(map.size)  // 2

map.delete('name')
console.log(map.has('name'))  // false

map.clear()
console.log(map.size)  // 0
```

### 遍历

```javascript [map-iterate.js]
const map = new Map([
  ['name', '张三'],
  ['age', 25]
])

// 遍历键值对
for (const [key, value] of map) {
  console.log(`${key}: ${value}`)
}

// 遍历键
for (const key of map.keys()) {
  console.log(key)
}

// 遍历值
for (const value of map.values()) {
  console.log(value)
}
```

### 对象作为键

```javascript [object-key.js]
const obj = { id: 1 }
const map = new Map()

map.set(obj, '用户数据')

console.log(map.get(obj))  // 用户数据
```

### Map 与 Object 对比

| 特性 | Map | Object |
|------|-----|--------|
| 键类型 | 任意类型 | 字符串/Symbol |
| 插入顺序 | 保持 | 不保证 |
| 大小 | size 属性 | 手动计算 |
| 遍历 | 直接遍历 | 需要转换 |
| 性能 | 频繁增删更好 | 查找更好 |

## WeakSet 和 WeakMap

### WeakSet

```javascript [weakset.js]
const weakSet = new WeakSet()
const obj = {}

weakSet.add(obj)
console.log(weakSet.has(obj))  // true
```

### WeakMap

```javascript [weakmap.js]
const weakMap = new WeakMap()
const obj = {}

weakMap.set(obj, '数据')
console.log(weakMap.get(obj))  // 数据
```

::: tip 提示
- Set 用于存储唯一值
- Map 用于键值对存储
- WeakSet/WeakMap 用于弱引用
:::
