# TypeScript 面向对象

## 声明对象类型

实际开发中，限制⼀般对象，通常使用以下形式：

```typescript
// 限制person1对象必须有name属性，age为可选属性
let person1: { name: string, age?: number }

// 含义同上，也能⽤分号做分隔
let person2: { name: string; age?: number }

// 含义同上，也能⽤换⾏做分隔
let person3: {
 name: string
 age?: number
}

// 如下赋值均可以
person1 = {name:'李四',age:18}
person2 = {name:'张三'}
person3 = {name:'王五'}
// 如下赋值不合法，因为person3的类型限制中，没有对gender属性的说明
person3 = {name:'王五',gender:'男'}
```

## 索引签名

允许定义对象可以具有**任意数量的属性**，这些属性的**键**和**类型**是**可变的**， 常用于：描述类型不确定的属性，具有动态属性的对象。

```typescript
// 限制person对象必须有name属性，可选age属性但值必须是数字，同时可以有任意数量、任意类型的其他属性
let person: {
 name: string
 age?: number
 [key: string]: any // 索引签名，完全可以不⽤key这个单词，换成其他的也可以
}
// 赋值合法
person = {
 name:'张三',
 age:18,
 gender:'男'
}
```

## 声明函数类型

 TypeScript 中的 `=>` 在函数类型声明时表示函数类型，描述其参数类型和返回类型。 JavaScript 中的 `=>` 是⼀种定义函数的语法，是具体的函数实现。 函数类型声明还可以使用：接口、自定义类型等方式。

```typescript
let count: (a: number, b: number) => number
count = function (x, y) {
 return x + y
}
```

## 声明函数参数

```typescript
// 参数x必须是数字，参数y也必须是数字，函数返回值也必须是数字
function demo(x:number,y:number):number{
 return x + y
}
demo(100,200)
demo(100,'200') //警告：类型“string”的参数不能赋给类型“number”的参数
demo(100,200,300) //警告：应有 2 个参数，但获得 3 个
demo(100) //警告：应有 2 个参数，但获得 1 个
```

## 类

类 class：

```typescript
class Person {
 // 属性声明
 name: string
 age: number
 // 构造器
 constructor(name: string, age: number) {
 this.name = name
 this.age = age
 }
 // ⽅法
 speak() {
 console.log(`我叫：${this.name}，今年${this.age}岁`)
 }
}
// Person实例
const p1 = new Person('周杰伦', 38)
```

Student 继承 Person ：

```typescript
class Student extends Person {
 grade: string
 // 构造器
 constructor(name: string, age: number, grade: string) {
 super(name, age)
 this.grade = grade
 }
 // 备注本例中若Student类不需要额外的属性，Student的构造器可以省略
 // 重写从⽗类继承的⽅法
 override speak() {
 console.log(`我是学⽣，我叫：${this.name}，今年${this.age}岁，在读${this.grade}
年级`,)
 }
 // ⼦类自己的⽅法
 study() {
 console.log(`${this.name}正在努⼒学习中......`)
 }
}
```

## 属性修饰符

![image-20240820210508382](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202408202105454.png)

### public 修饰符

Person 类 ：

```typescript
class Person {
 // name写了public修饰符，age没写修饰符，最终都是public修饰符
 public name: string
 age: number
 constructor(name: string, age: number) {
 this.name = name
 this.age = age
 }
 speak() {
 // 类的【内部】可以访问public修饰的name和age
 console.log(`我叫：${this.name}，今年${this.age}岁`)
 }
}
const p1 = new Person('张三', 18)
// 类的【外部】可以访问public修饰的属性
console.log(p1.name)
```

Student 继承 Person ：

```typescript
class Student extends Person {
 constructor(name: string, age: number) {
 super(name, age)
 }
 study() {
 // 【⼦类中】可以访问⽗类中public修饰的：name属性、age属性
 console.log(`${this.age}岁的${this.name}正在努⼒学习`)
 }
```

属性的简写形式：

- 完整写法：

  ```typescript
  class Person {
   public name: string;
   public age: number;
   constructor(name: string, age: number) {
     this.name = name;
     this.age = age;
   }
  }
  ```

- 简写形式：

  ```typescript
  class Person {
   constructor(
   public name: string,
   public age: number
   ) { }
  }
  ```

### protected 修饰符

Person类：

```typescript
class Person {
    // name和age是受保护属性，不能在类外部访问，但可以在【类】与【⼦类】中访问
    constructor(
        protected name: string,
        protected age: number
    ) { }
    // getDetails是受保护⽅法，不能在类外部访问，但可以在【类】与【⼦类】中访问
    protected getDetails(): string {
        // 类中能访问受保护的name和age属性
        return `我叫：${this.name}，年龄是：${this.age}`
    }
    // introduce是公开方法，类、⼦类、类外部都能使用
    introduce() {
        // 类中能访问受保护的getDetails⽅法
        console.log(this.getDetails());
    }
}
const p1 = new Person('杨超越', 18)
// 可以在类外部访问introduce
p1.introduce()
// 以下代码均报错
// p1.getDetails()
// p1.name
// p1.age
```

Student 继承 Person 

```typescript
class Student extends Person {
    constructor(name: string, age: number) {
        super(name, age)
    }
    study() {
        // ⼦类中可以访问introduce
        this.introduce()
        // ⼦类中可以访问name
        console.log(`${this.name}正在努⼒学习`)
    }
}
const s1 = new Student('tom', 17)
s1.introduce()
```

### private 修饰符

```typescript
class Person {
 constructor(
 public name: string,
 public age: number,
 // IDCard属性为私有的(private)属性，只能在【类内部】使用
 private IDCard: string
 ) { }
 private getPrivateInfo(){
 // 类内部可以访问私有的(private)属性 —— IDCard
 return `身份证号码为：${this.IDCard}`
 }
 getInfo() {
 // 类内部可以访问受保护的(protected)属性 —— name和age
 return `我叫: ${this.name}, 今年刚满${this.age}岁`;
 }
 getFullInfo(){
 // 类内部可以访问公开的getInfo⽅法，也可以访问私有的getPrivateInfo⽅法
 return this.getInfo() + '，' + this.getPrivateInfo()
 }
}
const p1 = new Person('张三',18,'110114198702034432')
console.log(p1.getFullInfo())
console.log(p1.getInfo())
// 以下代码均报错
// p1.name
// p1.age
// p1.IDCard
// p1.getPrivateInfo()
```

### readonly 修饰符

```typescript
class Car {
 constructor(
 public readonly vin: string, //⻋辆识别码，为只读属性
 public readonly year: number,//出⼚年份，为只读属性
 public color: string,
 public sound: string
 ) { }
 // 打印⻋辆信息
 displayInfo() {
 console.log(`
 识别码：${this.vin},
 出⼚年份：${this.year},
 颜⾊：${this.color},
 ⾳响：${this.sound}
 `);
 }
}
const car = new Car('1HGCM82633A123456', 2018, '⿊⾊', 'Bose⾳响');
car.displayInfo()
// 以下代码均错误：不能修改 readonly 属性
// car.vin = '897WYE87HA8SGDD8SDGHF'; 
// car.year = 2020; 
```

## 抽象类

抽象类是⼀种**无法被实例化**的类，专门用来定义类的**结构和行为**，类中可以写**抽象方法**，也可以写**具体实现**。抽象类主要用来为其派生类提供⼀个**基础结构**，要求其派生类**必须实现**其中的抽象⽅法。 

简记：**抽象类不能实例化，其意义是可以被继承，抽象类里可以有普通方法、也可以有抽象方法**。

抽象类场景：

1. **定义通用接口**：为⼀组相关的类定义通用的行为 (方法或属性)时。 
1. **提供基础实现** ：在抽象类中提供某些方法或为其提供基础实现，这样派生类就可以继承这些实现。
1. **确保关键实现** ：强制派生类实现⼀些关键行为。 
1. **共享代码和逻辑**：当多个类需要共享部分代码时，抽象类可以避免代码重复。

定义⼀个抽象类 Package ，表示所有包裹的基本结构，任何包裹都有重量属性 weight，包裹都需要计算运费。但不同类型的包裹 (如：标准速度、特快专递) 都有不同的运费计算方式，因此用于计算运费的 calculate ⽅法是⼀个抽象方法，必须由具体的子类来实现。

>  Package 类 

```typescript
abstract class Package {
 constructor(public weight: number) { }
 // 抽象方法：用来计算运费，不同类型包裹有不同的计算方式
 abstract calculate(): number
 // 通⽤方法：打印包裹详情
 printPackage() {
 console.log(`包裹重量为: ${this.weight}kg，运费为: ${this.calculate()}元`);
 }
}
```

StandardPackage 类继承了 Package ，实现了 calculate方法：

> StandardPackage 类 (标快包裹)

```typescript
// 标准包裹
class StandardPackage extends Package {
 constructor(
 weight: number,
 public unitPrice: number // 每公⽄的固定费率
 ) { super(weight) }
 // 实现抽象方法：计算运费
 calculate(): number {
 return this.weight * this.unitPrice;
 }
}
// 创建标准包裹实例
const s1 = new StandardPackage(10,5)
s1.printPackage()
```

ExpressPackage 类继承了 Package ，实现了 calculate 方法：

> ExpressPackage 类 (特快包裹)

```typescript
class ExpressPackage extends Package {
 constructor(
 weight: number,
 private unitPrice: number, // 每公⽄的固定费率（快速包裹更⾼）
 private additional: number // 超出10kg以后的附加费
 ) { super(weight) }
 // 实现抽象⽅法：计算运费
 calculate(): number {
 if(this.weight > 10){
 // 超出10kg的部分，每公⽄多收additional对应的价格
 return 10 * this.unitPrice + (this.weight - 10) * this.additional
 }else {
 return this.weight * this.unitPrice;
 }
 }
}
// 创建特快包裹实例
const e1 = new ExpressPackage(13,8,2)
e1.printPackage()
```

## 接口

interface 是⼀种**定义结构**的⽅式，主要作用是为：类、对象、函数等**规定⼀种契约**，这样可以确保代码的⼀致性和类型安全。

**注意**：interface 只能定义格式，不能包含任何实现。

**使用场景**：

1. **定义对象的格式**： 描述数据模型、API 响应格式、配置对象........等等，是开发中用的最多的场景。
2. **类的契约**：规定⼀个类需要实现哪些属性和方法。 
3. **扩展已有接口**：⼀般用于扩展第三方库的类型， 这种特性在大型项⽬中可能会用到。

**定义类结构**：

```typescript
// PersonInterface接口，⽤与限制Person类的格式
interface PersonInterface {
 name: string
 age: number
 speak(n: number): void
}
// 定义⼀个类 Person，实现 PersonInterface 接口
class Person implements PersonInterface {
 constructor(
 public name: string,
 public age: number
 ) { }
 // 实现接口中的 speak 方法
 speak(n: number): void {
 for (let i = 0; i < n; i++) {
 // 打印出包含名字和年龄的问候语句
 console.log(`你好，我叫${this.name}，我的年龄是${this.age}`);
 }
 }
}
// 创建⼀个 Person 类的实例 p1，传⼊名字 'tom' 和年龄 18
const p1 = new Person('tom', 18);
p1.speak(3)
```

**定义对象结构**：

```typescript
interface UserInterface {
 name: string
 readonly gender: string // 只读属性
 age?: number // 可选属性
 run: (n: number) => void
}
const user: UserInterface = {
 name: "张三",
 gender: '男',
 age: 18,
 run(n) {
 console.log(`奔跑了${n}⽶`)
 }
};
```

**定义函数结构**：

```typescript
interface CountInterface {
 (a: number, b: number): number;
}
const count: CountInterface = (x, y) => {
 return x + y
}
```

**接口之间的继承**：⼀个 interface 继承另⼀个 interface ，从而实现代码的复用

```typescript
interface PersonInterface {
 name: string // 姓名
 age: number // 年龄
}
interface StudentInterface extends PersonInterface {
 grade: string // 年级
}
const stu: StudentInterface = {
 name: "张三",
 age: 25,
 grade: '⾼三',
}
```

**接口自动合并 (可重复定义)**：

```typescript
// PersonInterface接口
interface PersonInterface {
 // 属性声明
 name: string
 age: number
}
// 给PersonInterface接口添加新属性
interface PersonInterface {
 // 方法声明
 speak(): void
}
// Person类实现PersonInterface
class Person implements PersonInterface {
 name: string
 age: number
 // 构造器
 constructor(name: string, age: number) {
 this.name = name
 this.age = age
 }
 // 方法
 speak() {
 console.log('你好！我是老师:', this.name)
 }
```

**interface 与 type 的区别**：

- 相同点： interface 和 type 都可以用于定义对象结构，在定义对象结构时两者可以互换。

  ```typescript
  // interface 和 type 都可以定义对象结构
  // 使用 interface 定义 Person 对象
  interface PersonInterface {
   name: string;
   age: number;
   speak(): void;
  }
  // 使用 type 定义 Person 对象
  type PersonType = {
   name: string;
   age: number;
   speak(): void;
  };
  // 使用PersonInterface
  /* let person: PersonInterface = {
   name:'张三',
   age:18,
   speak(){
   console.log(`我叫：${this.name}，年龄：${this.age}`)
   }
  } */
  // 使用PersonType
  let person: PersonType = {
   name:'张三',
   age:18,
   speak(){
   console.log(`我叫：${this.name}，年龄：${this.age}`)
   }
  }
  ```

- 不同点：
  - interface：更专注于定义对象和类的结构，⽀持继承、合并。
  
    ```typescript
    // interface 可以继承、合并
    interface PersonInterface {
     name: string // 姓名
     age: number // 年龄
    }
    interface PersonInterface {
     speak: () => void
    }
    interface StudentInterface extends PersonInterface {
     grade: string // 年级
    }
    const student: StudentInterface = {
     name: '李四',
     age: 18,
     grade: '高二',
     speak() {
     console.log(this.name,this.age,this.grade)
     }
    }
    ```
  
  - type：可以定义类型别名、联合类型、交叉类型，但不⽀持继承和自动合并。
  
    ```typescript
    // type 的交叉类型
    // 使用 type 定义 Person 类型，并通过交叉类型实现属性的合并
    type PersonType = {
     name: string; // 姓名
     age: number; // 年龄
    } & {
     speak: () => void;
    };
    // 使用 type 定义 Student 类型，并通过交叉类型继承 PersonType
    type StudentType = PersonType & {
     grade: string; // 年级
    };
    const student: StudentType = {
     name: '李四',
     age: 18,
     grade: '高二',
     speak() {
     console.log(this.name, this.age, this.grade);
     }
    };
    ```

**interface 与 抽象类的区别**：

- 相同点：都能定义⼀个**类的格式** (定义类应遵循的契约)

- 不相同：

  - 接口：**只能描述结构**，**不能有任何实现代码**，⼀个类可以实现**多个**接口。

    ```typescript
    // ⼀个类可以实现多个接⼝
    // FlyInterface 接⼝
    interface FlyInterface {
     fly(): void;
    }
    // 定义 SwimInterface 接⼝
    interface SwimInterface {
     swim(): void;
    }
    // Duck 类实现了 FlyInterface 和 SwimInterface 两个接⼝
    class Duck implements FlyInterface, SwimInterface {
     fly(): void {
     console.log('鸭子可以飞');
     }
     swim(): void {
     console.log('鸭子可以游泳');
     }
    }
    // 创建⼀个 Duck 实例
    const duck = new Duck();
    duck.fly(); // 输出: 鸭子可以飞
    duck.swim(); // 输出: 鸭子可以游泳
    ```

  - 抽象类：既可以包含**抽象方法**，也可以包含**具体方法**， ⼀个类**只能继承⼀个**抽象类。

## 泛型

泛型允许在定义函数、类或接口时，使用类型参数来表示未指定的类型，这些参数在具体使用时，才被指定具体的类型，泛型能让同⼀段代码适用于多种类型，同时仍然保持类型的安全性。

定义⼀个函数或类时，有些情况下⽆法确定其中要使用的具体类型（返回值、参数、属性的类型不能确定），此时就需要泛型了

 `<T>` 就是泛型 (不⼀定非叫 `T`)，设置泛型后即可在函数中使用 `T` 来表示该类型：

```typescript
function test<T>(arg: T): T{
return arg;
}
// 不指名类型，TS会⾃动推断出来
test(10)
// 指名具体的类型
test<number>(10)
```

泛型可以写多个：

```typescript
function test<T, K>(a: T, b: K): K{
 return b;
}
// 为多个泛型指定具体自值
test<number, string>(10, "hello");
```

类中同样可以使用泛型：

```typescript
class MyClass<T>{
 prop: T;
 constructor(prop: T){
 this.prop = prop;
 }
}
```

也可以对泛型的范围进行约束：

```typescript
interface Demo{
 length: number;
}
// 泛型T必须是MyInter的⼦类，即：必须拥有length属性
function test<T extends Demo>(arg: T): number{
 return arg.length;
}
test(10) // 类型“number”的参数不能赋给类型“Demo”的参数
test({name:'张三'}) // 类型“{ name: string; }”的参数不能赋给类型“Demo”的参数
test('123')
test({name:'张三',length:10})
```

## 类型声明文件

类型声明文件是 TypeScript 中的⼀种特殊文件，通常以 `.d.ts` 作为扩展名。

**主要作用**：是为现有的 JavaScript 代码提供类型信息，使得 TypeScript 能够在使用这些 JavaScript 库 或模块时进行类型检查和提示。

> demo.js 

```javascript
export function add(a, b) {
 return a + b;
}
export function mul(a, b) {
 return a * b;
}
```

> demo.d.ts 

```typescript
declare function add(a: number, b: number): number;
declare function mul(a: number, b: number): number;

export { add, mul };
```

> index.ts

```typescript
// example.ts
import { add, mul } from "./demo.js";

const x = add(2, 3); // x 类型为 number
const y = mul(4, 5); // y 类型为 number

console.log(x,y)
```

