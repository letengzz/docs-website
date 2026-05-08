# 类（Class）

ES6 引入了 Class（类）语法，让对象原型继承更加清晰。

## 基本语法

### 定义类

```javascript [class.js]
class Person {
  constructor(name, age) {
    this.name = name
    this.age = age
  }

  greet() {
    console.log(`Hello, ${this.name}`)
  }
}

const person = new Person('张三', 25)
person.greet()  // Hello, 张三
```

## 构造函数

### constructor 方法

```javascript [constructor.js]
class Animal {
  constructor(name) {
    this.name = name
  }
}

const dog = new Animal('Dog')
console.log(dog.name)  // Dog
```

## 实例方法

### 定义方法

```javascript [methods.js]
class Person {
  constructor(name) {
    this.name = name
  }

  greet() {
    console.log(`Hello, ${this.name}`)
  }

  getAge() {
    return this.age
  }
}
```

## 静态方法

### static 关键字

```javascript [static.js]
class MathHelper {
  static add(a, b) {
    return a + b
  }

  static subtract(a, b) {
    return a - b
  }
}

console.log(MathHelper.add(1, 2))        // 3
console.log(MathHelper.subtract(5, 3))   // 2
```

## 继承

### extends 关键字

```javascript [extends.js]
class Animal {
  constructor(name) {
    this.name = name
  }

  speak() {
    console.log(`${this.name} makes a sound`)
  }
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name)
    this.breed = breed
  }

  speak() {
    console.log(`${this.name} barks`)
  }
}

const dog = new Dog('Rex', 'Labrador')
dog.speak()  // Rex barks
```

## Getter 和 Setter

### get 和 set

```javascript [getter-setter.js]
class Person {
  constructor(firstName, lastName) {
    this.firstName = firstName
    this.lastName = lastName
  }

  get fullName() {
    return `${this.firstName} ${this.lastName}`
  }

  set fullName(value) {
    const parts = value.split(' ')
    this.firstName = parts[0]
    this.lastName = parts[1]
  }
}

const person = new Person('张', '三')
console.log(person.fullName)  // 张三

person.fullName = '李 四'
console.log(person.firstName)  // 李
```

## 私有字段

### # 前缀（ES2022）

```javascript [private.js]
class Person {
  #age

  constructor(name, age) {
    this.name = name
    this.#age = age
  }

  getAge() {
    return this.#age
  }
}

const person = new Person('张三', 25)
console.log(person.getAge())  // 25
console.log(person.#age)      // SyntaxError
```

## 实际应用场景

### 数据模型

```javascript [model.js]
class User {
  constructor(data) {
    this.id = data.id
    this.name = data.name
    this.email = data.email
  }

  static fromJSON(json) {
    const data = JSON.parse(json)
    return new User(data)
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      email: this.email
    }
  }
}

const user = new User({ id: 1, name: '张三', email: 'zhangsan@example.com' })
console.log(user.toJSON())
```

### 组件基类

```javascript [component.js]
class Component {
  constructor(props) {
    this.props = props
    this.state = {}
  }

  setState(newState) {
    this.state = { ...this.state, ...newState }
    this.render()
  }

  render() {
    throw new Error('render() must be implemented')
  }
}

class Button extends Component {
  render() {
    console.log(`Button: ${this.props.label}`)
  }
}

const btn = new Button({ label: 'Click Me' })
btn.render()
```

::: tip 提示
- Class 是语法糖，底层仍是原型继承
- 使用 extends 实现继承
- 静态方法通过类名调用
- 私有字段使用 # 前缀
:::
