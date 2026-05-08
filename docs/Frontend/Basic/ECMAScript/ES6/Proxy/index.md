# Proxy

Proxy 用于修改某些操作的默认行为，等同于在语言层面做出修改。

## 基本语法

```javascript [basic.js]
const target = { name: '张三' }

const handler = {
  get(obj, prop) {
    console.log(`访问属性: ${prop}`)
    return obj[prop]
  }
}

const proxy = new Proxy(target, handler)

console.log(proxy.name)  // 访问属性: name \n 张三
```

## 拦截操作

### get

```javascript [get.js]
const person = { name: '张三', age: 25 }

const proxy = new Proxy(person, {
  get(obj, prop) {
    if (prop in obj) {
      return obj[prop]
    }
    return '属性不存在'
  }
})

console.log(proxy.name)   // 张三
console.log(proxy.phone)  // 属性不存在
```

### set

```javascript [set.js]
const person = { age: 25 }

const proxy = new Proxy(person, {
  set(obj, prop, value) {
    if (prop === 'age') {
      if (typeof value !== 'number') {
        throw new TypeError('年龄必须是数字')
      }
      if (value < 0 || value > 150) {
        throw new RangeError('年龄必须在 0-150 之间')
      }
    }
    obj[prop] = value
    return true
  }
})

proxy.age = 30
console.log(person.age)  // 30
```

### has

```javascript [has.js]
const person = { name: '张三', _secret: '密码' }

const proxy = new Proxy(person, {
  has(obj, prop) {
    if (prop.startsWith('_')) {
      return false
    }
    return prop in obj
  }
})

console.log('name' in proxy)    // true
console.log('_secret' in proxy) // false
```

### deleteProperty

```javascript [delete.js]
const person = { name: '张三', age: 25 }

const proxy = new Proxy(person, {
  deleteProperty(obj, prop) {
    if (prop === 'name') {
      throw new Error('不能删除 name 属性')
    }
    delete obj[prop]
    return true
  }
})

delete proxy.age
console.log(person.age)  // undefined
```

### ownKeys

```javascript [ownKeys.js]
const person = { name: '张三', age: 25, _secret: '密码' }

const proxy = new Proxy(person, {
  ownKeys(obj) {
    return Object.keys(obj).filter(key => !key.startsWith('_'))
  }
})

console.log(Object.keys(proxy))  // ['name', 'age']
```

### getOwnPropertyDescriptor

```javascript [descriptor.js]
const person = { name: '张三', _secret: '密码' }

const proxy = new Proxy(person, {
  getOwnPropertyDescriptor(obj, prop) {
    if (prop.startsWith('_')) {
      return undefined
    }
    return Object.getOwnPropertyDescriptor(obj, prop)
  }
})

console.log(Object.getOwnPropertyDescriptor(proxy, 'name'))
console.log(Object.getOwnPropertyDescriptor(proxy, '_secret'))  // undefined
```

## 实际应用

### 数据验证

```javascript [validate.js]
function createValidator(target, validator) {
  return new Proxy(target, {
    set(obj, prop, value) {
      if (validator[prop]) {
        validator[prop](value)
      }
      obj[prop] = value
      return true
    }
  })
}

const person = createValidator(
  { name: '', age: 0 },
  {
    name(value) {
      if (typeof value !== 'string') {
        throw new TypeError('名字必须是字符串')
      }
    },
    age(value) {
      if (typeof value !== 'number' || value < 0 || value > 150) {
        throw new RangeError('年龄无效')
      }
    }
  }
)

person.name = '张三'
person.age = 25
```

### 读取负索引

```javascript [negative-index.js]
const arr = [1, 2, 3, 4, 5]

const proxy = new Proxy(arr, {
  get(obj, prop) {
    const index = Number(prop)
    if (index < 0) {
      return obj[obj.length + index]
    }
    return obj[prop]
  }
})

console.log(proxy[-1])  // 5
console.log(proxy[-2])  // 4
```

### 缓存

```javascript [cache.js]
function createCache() {
  const cache = {}
  
  return new Proxy(cache, {
    get(obj, prop) {
      if (!(prop in obj)) {
        obj[prop] = `缓存: ${prop}`
      }
      return obj[prop]
    }
  })
}

const cache = createCache()

console.log(cache.a)  // 缓存: a
console.log(cache.a)  // 缓存: a
```

::: tip 提示
- Proxy 可以拦截多种操作
- 适合用于数据验证、缓存、响应式系统
- Vue 3 使用 Proxy 实现响应式
:::
