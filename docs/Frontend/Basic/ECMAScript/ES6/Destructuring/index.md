# 解构赋值

解构赋值是一种从数组或对象中提取值并赋值给变量的语法。

## 数组解构

### 基本解构

```javascript [basic.js]
const arr = [1, 2, 3]

const [a, b, c] = arr
console.log(a, b, c)  // 1 2 3
```

### 跳过元素

```javascript [skip.js]
const arr = [1, 2, 3, 4]

const [a, , c] = arr
console.log(a, c)  // 1 3
```

### 默认值

```javascript [default.js]
const arr = [1]

const [a, b = 2] = arr
console.log(a, b)  // 1 2
```

### 剩余元素

```javascript [rest.js]
const arr = [1, 2, 3, 4, 5]

const [first, ...rest] = arr
console.log(first)  // 1
console.log(rest)   // [2, 3, 4, 5]
```

### 交换变量

```javascript [swap.js]
let a = 1, b = 2

[a, b] = [b, a]
console.log(a, b)  // 2 1
```

## 对象解构

### 基本解构

```javascript [object-basic.js]
const person = { name: '张三', age: 25 }

const { name, age } = person
console.log(name, age)  // 张三 25
```

### 重命名

```javascript [rename.js]
const person = { name: '张三', age: 25 }

const { name: userName, age: userAge } = person
console.log(userName, userAge)  // 张三 25
```

### 默认值

```javascript [object-default.js]
const person = { name: '张三' }

const { name, age = 25 } = person
console.log(name, age)  // 张三 25
```

### 剩余属性

```javascript [object-rest.js]
const person = { name: '张三', age: 25, city: '北京' }

const { name, ...rest } = person
console.log(name)   // 张三
console.log(rest)   // { age: 25, city: '北京' }
```

### 嵌套解构

```javascript [nested.js]
const person = {
  name: '张三',
  address: {
    city: '北京',
    district: '朝阳'
  }
}

const { address: { city, district } } = person
console.log(city, district)  // 北京 朝阳
```

## 函数参数解构

### 数组参数解构

```javascript [fn-array.js]
function sum([a, b]) {
  return a + b
}

console.log(sum([1, 2]))  // 3
```

### 对象参数解构

```javascript [fn-object.js]
function greet({ name, age }) {
  console.log(`Hello, ${name}. You are ${age} years old.`)
}

greet({ name: '张三', age: 25 })
```

### 默认值

```javascript [fn-default.js]
function greet({ name = 'Guest', age = 0 } = {}) {
  console.log(`Hello, ${name}. You are ${age} years old.`)
}

greet()  // Hello, Guest. You are 0 years old.
```

## 字符串解构

```javascript [string.js]
const str = 'hello'

const [a, b, c, d, e] = str
console.log(a, b, c, d, e)  // h e l l o
```

## 实际应用场景

### 提取 JSON 数据

```javascript [json.js]
const response = {
  data: {
    user: {
      id: 1,
      name: '张三',
      email: 'zhangsan@example.com'
    }
  }
}

const { data: { user: { name, email } } } = response
console.log(name, email)
```

### 函数返回多个值

```javascript [multiple-return.js]
function getStats(arr) {
  return {
    max: Math.max(...arr),
    min: Math.min(...arr),
    avg: arr.reduce((a, b) => a + b, 0) / arr.length
  }
}

const { max, min, avg } = getStats([1, 2, 3, 4, 5])
console.log(max, min, avg)
```

### 配置对象解构

```javascript [config.js]
function createServer({ port = 3000, host = 'localhost' } = {}) {
  console.log(`Server running at ${host}:${port}`)
}

createServer({ port: 8080 })
```

::: tip 提示
- 解构赋值让代码更简洁
- 对象解构时可以使用重命名
- 函数参数解构可以设置默认值
:::
