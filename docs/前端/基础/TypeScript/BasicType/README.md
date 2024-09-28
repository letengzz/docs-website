# TypeScript 基本类型

JavaScript 中的数据类型：string 、 number 、 boolean 、 null 、 undefined 、 bigint 、 symbol 、 object(包括：Array、Function、Date...)

TypeScript 中的数据类型：

1. JavaScript 所有数据类型
2. 四个新类型：void、never、unknown、 any、 enum、tuple
3. 自定义类型：type、 interface

![image-20240128233155908](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401282332924.png)

## number

```typescript
let decimal: number = 6;
let hex: number = 0xf00d;
let binary: number = 0b1010;
let octal: number = 0o744;
let big: bigint = 100n;
```

## boolean

```typescript
let isDone: boolean = false;
```

## string

```typescript
let color: string = "blue";
color = 'red';

let fullName: string = `Bob Bobbington`;
let age: number = 37;
let sentence: string = `Hello, my name is ${fullName}.

I'll be ${age + 1} years old next month.`;
```

## 字面量

可以使用字面量去指定变量的类型，通过字面量可以确定变量的取值范围

```typescript
let color: 'red' | 'blue' | 'black';
let num: 1 | 2 | 3 | 4 | 5;
```

## any 

any 表示的是任意类型，一个变量设置类型为any后相当于对该变量关闭了TS的类型检测，使用TS时，不建议使用any类型。

明确的表示a的类型是 any：显式的any

```typescript
let d: any = 4;
// 以下对a的赋值，均⽆警告
d = 'hello';
d = true;
```

声明变量如果不指定类型，则TS解析器会自动判断变量的类型为any：隐式的any

```typescript
let d;
//以下对b的赋值，均⽆警告
d = 10;
d = 'hello';
d = true;
```

**注意**：any类型的变量，可以赋值给任意类型的变量

```typescript
let c:any
c = 9
let x: string
x = c // ⽆警告
```

## unknown

unknown 表示未知类型的值。unknown 可以理解为⼀个类型安全的 any，使用于：起初不确定数据的具体类型，要后期才能确定。

```typescript
// 设置a的类型为unknown
let a: unknown

//以下对a的赋值，均符合规范
a = 100
a = false
a = '你好'

// 设置x的数据类型为string
let x: string
x = a //警告：不能将类型“unknown”分配给类型“string”
```

unknown 会强制开发者在使用之前进行类型检查，从而提供更强的类型安全性：

```typescript
// 设置a的类型为unknown
let a: unknown
a = 'hello'
//第一种方式：加类型判断
if(typeof a === 'string'){
 x = a
 console.log(x)
}
//第二种方式：加断言
x = a as string
//第三种方式：加断言
x = <string>a
```

读取 any 类型数据的任何属性都不会报错，而 unknown 正好与之相反。

```typescript
let str1: string
str1 = 'hello'
str1.toUpperCase() //无警告

let str2: any
str2 = 'hello'
str2.toUpperCase() //无警告

let str3: unknown
str3 = 'hello';
str3.toUpperCase() //警告：“str3”的类型为“未知”

// 使用断言强制指定str3的类型为string
(str3 as string).toUpperCase() //无警告
```

## void

void用来表示空，即：函数不返回任何值，调⽤者也不应依赖其返回值进行任何操作

```typescript
let unusable: void = undefined;
function fn(): void{
}
```

void 通常用于函数返回值声明：

```ts
function fn(): void{
}
```

**注意**：编码者没有编写 return 指定函数返回值，所以 logMessage 函数是没有显式 返回值的，但会有⼀个隐式返回值 ，是 undefined ，虽然函数返回类型为 void ，但 也是可以接受 undefined 的，简单记： undefined 是 void 可以接受的⼀种"空"。

```typescript
// ⽆警告
function logMessage(msg:string):void{
 console.log(msg)
}
// ⽆警告
function logMessage(msg:string):void{
 console.log(msg)
 return;
}
// ⽆警告
function logMessage(msg:string):void{
 console.log(msg)
 return undefined
}
```

限制函数返回值时，undefined 和 void 有区别：返回值类型为 void 的函数，调用者不应依赖其返回值进行任何操作

void 与 undefined void 是⼀个广泛的概念，用来表达"空"，而 undefined 则是这种"空"的具体实现。 因此可以说 undefined 是 void 能接受的⼀种"空"的状态。 也可以理解为： void 包含 undefined ，但 void 所表达的语义超越了 undefined ， void 是⼀种意图上的约定，而不仅仅是特定值的限制。 

如果⼀个函数返回类型为 void ，那么： 

1. 从语法上讲：函数是可以返回 undefined 的，至于显式返回，还是隐式返回，这无所谓
2. 从语义上讲：函数调用者不应关心函数返回的值，也不应依赖返回值进行任何操作！即使知道它返回了 undefined 。

```typescript
function logMessage(msg:string):void{
 console.log(msg)
}
let result = logMessage('你好')
if(result){ // 此⾏报错：⽆法测试 "void" 类型的表达式的真实性
 console.log('logMessage有返回值')
}
```

```typescript
function logMessage(msg:string):undefined{
 console.log(msg)
}
let result = logMessage('你好')
if(result){ // 此⾏⽆警告
 console.log('logMessage有返回值')
}
```

## never

never表示永远不会返回结果，即：不能有值，例如 `undefined` 、 `null` 、 `''` 、`0` 都不行。

几乎不用 never 去直接限制变量，因为没有意义：

```typescript
/* 指定a的类型为never，那就意味着a以后不能存任何的数据了 */
let a: never
// 以下对a的所有赋值都会有警告
a = 1
a = true
a = undefined
a = null
```

never ⼀般是 TypeScript 主动推断出来的：

```typescript
// 指定a的类型为string
let a: string
// 给a设置⼀个值
a = 'hello'
if (typeof a === 'string') {
 console.log(a.toUpperCase())
} else {
 console.log(a) // TypeScript会推断出此处的a是never，因为没有任何⼀个值符合此处的逻辑
}
```

never 也可用于限制函数的返回值：

```typescript
// 限制throwError函数不需要有任何返回值，任何值都不⾏，像undeifned、null都不行
function throwError(str: string): never {
 throw new Error('程序异常退出:' + str)
}
```

## object

object 与 Object 实际开发中用的相对较少，因为范围太大了。

object：所有非原始类型，可存储：对象、函数、数组等，由于限制 的范围比较宽泛，在实际开发中使用的**相对较少**。

```typescript
let a:object //a的值可以是任何【⾮原始类型】，包括：对象、函数、数组等
// 以下代码，是将【⾮原始类型】赋给a，所以均符合要求
a = {}
a = {name:'张三'}
a = [1,3,5,7,9]
a = function(){}
a = new String('123')
class Person {}
a = new Person()
// 以下代码，是将【原始类型】赋给a，有警告
a = 1 // 警告：不能将类型“number”分配给类型“object”
a = true // 警告：不能将类型“boolean”分配给类型“object”
a = '你好' // 警告：不能将类型“string”分配给类型“object” 
a = null // 警告：不能将类型“null”分配给类型“object”
a = undefined // 警告：不能将类型“undefined”分配给类型“object”
```

Object：所有可以调用 Object 方法的类型 (除了 undefined 和 null 的任何值)，由于限制的范围实在太大了！所以实际开发中使用**频率极低**。

```typescript
let b:Object //b的值必须是Object的实例对象（除去undefined和null的任何值）
// 以下代码，均⽆警告，因为给a赋的值，都是Object的实例对象
b = {}
b = {name:'张三'}
b = [1,3,5,7,9]
b = function(){}
b = new String('123')
class Person {}
b = new Person()
b = 1 // 1不是Object的实例对象，但其包装对象是Object的实例
b = true // truue不是Object的实例对象，但其包装对象是Object的实例
b = '你好' // “你好”不是Object的实例对象，但其包装对象是Object的实例
// 以下代码均有警告
b = null // 警告：不能将类型“null”分配给类型“Object”
b = undefined // 警告：不能将类型“undefined”分配给类型“Object
```

## array

```typescript
let arr1: string[]
let arr2: Array<string>
arr1 = ['a','b','c']
arr2 = ['hello','world']
```

## tuple

元组 (Tuple) 是⼀种特殊的**数组类型**，可以存储**固定数量**的元素，并且每个元素的类型是**已知的**且**可以不同**。元组用于精确描述⼀组值的类型， `?` 表示可选元素。

```typescript
// 第⼀个元素必须是 string 类型，第⼆个元素必须是 number 类型。
let arr1: [string,number]
// 第⼀个元素必须是 number 类型，第⼆个元素是可选的，如果存在，必须是 boolean 类型。
let arr2: [number,boolean?]
// 第⼀个元素必须是 number 类型，后⾯的元素可以是任意数量的 string 类型
let arr3: [number,...string[]]
// 可以赋值
arr1 = ['hello',123]
arr2 = [100,false]
arr2 = [200]
arr3 = [100,'hello','world']
arr3 = [100]
// 不可以赋值，arr1声明时是两个元素，赋值的是三个
arr1 = ['hello',123,false]
```

## enum

枚举 (enum ) 可以定义⼀组命名常量，它能增强代码的可读性，也让代码更好维护。

如下代码的功能是：根据调用 walk 时传入的不同参数，执行不同的逻辑，存在的问题是调用 walk 时传参时没有任何提示，编码者很容易写错字符串内容；并且用于判断逻辑的 up 、 down 、 left 、 right 是连续且相关的⼀组值，那此时就特别适合使用 枚举 (enum)。

```typescript
function walk(str:string) {
 if (str === 'up') {
 console.log("向【上】⾛");
 } else if (str === 'down') {
 console.log("向【下】⾛");
 } else if (str === 'left') {
 console.log("向【左】⾛");
 } else if (str === 'right') {
 console.log("向【右】⾛");
 } else {
 console.log("未知⽅向");
 }
}
walk('up')
walk('down')
walk('left')
walk('right')
```

### 数字枚举

数字枚举⼀种最常见的枚举类型，其成员的值会自动递增，且数字枚举还具备**反向映射**的特点，可以通过值来获取对应的枚举成员名称 。

```typescript
// 定义⼀个描述【上下左右】⽅向的枚举Direction
enum Direction {
 Up,
 Down,
 Left,
 Right
}
console.log(Direction) // 打印Direction会看到如下内容
/* 
 {
 0:'Up', 
 1:'Down', 
 2:'Left', 
 3:'Right', 
 Up:0, 
 Down:1, 
 Left:2,
 Right:3
 } 
*/
// 反向映射
console.log(Direction.Up)
console.log(Direction[0])
// 此⾏代码报错，枚举中的属性是只读的
Direction.Up = 'shang'
```

可以指定枚举成员的初始值，其后的成员值会自动递增：

```typescript
enum Direction {
 Up = 6,
 Down,
 Left,
 Right
}
console.log(Direction.Up); // 输出: 6
console.log(Direction.Down); // 输出: 7
```

使用数字枚举完成刚才 walk 函数中的逻辑： 代码更加直观易读，而且类型安全，同时也更易于维护。

```typescript
enum Direction {
 Up,
 Down,
 Left,
 Right,
}
function walk(n: Direction) {
 if (n === Direction.Up) {
 console.log("向【上】⾛");
 } else if (n === Direction.Down) {
 console.log("向【下】⾛");
 } else if (n === Direction.Left) {
 console.log("向【左】⾛");
 } else if (n === Direction.Right) {
 console.log("向【右】⾛");
 } else {
 console.log("未知⽅向");
 }
}
walk(Direction.Up)
walk(Direction.Down)
```

### 字符串枚举

枚举成员的值是字符串

```typescript
enum Direction {
 Up = "up",
 Down = "down",
 Left = "left",
 Right = "right"
}
let dir: Direction = Direction.Up;
console.log(dir); // 输出: "up"
```

### 常量枚举

常量枚举是⼀种特殊枚举类型，它使用 const 关键字定义，在编译时会被 内联，避免生成⼀些额外的代码。

编译时内联？ 所谓“内联”其实就是 TypeScript 在编译时，会将枚举成员引用替换为它们的实际值， 而不是生成额外的枚举对象。这可以减少生成的 JavaScript 代码量，并提高运行时性能。

使⽤普通枚举的 TypeScript 代码如下：

```typescript
enum Directions {
 Up,
 Down,
 Left,
 Right
}
let x = Directions.Up;
```

编译后⽣成的 JavaScript 代码量较大 ：

```typescript
"use strict";
var Directions;
(function (Directions) {
 Directions[Directions["Up"] = 0] = "Up";
 Directions[Directions["Down"] = 1] = "Down";
 Directions[Directions["Left"] = 2] = "Left";
 Directions[Directions["Right"] = 3] = "Right";
})(Directions || (Directions = {}));
let x = Directions.Up
```

使用常量枚举的 TypeScript 代码：

```typescript
const enum Directions {
 Up,
 Down,
 Left,
 Right
}
let x = Directions.Up;
```

编译后生成的 JavaScript 代码量较小：

```typescript
"use strict";
let x = 0 /* Directions.Up */;
```



