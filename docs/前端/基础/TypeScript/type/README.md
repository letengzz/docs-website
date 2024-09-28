# TypeScript 类型别名

type 可以为任意类型创建别名，让代码更简洁、可读性更强，同时能更方便地进行类型复用和扩展。

## 基本用法

类型别名使用 type 关键字定义， type 后跟类型名称。

**例**：代码中 num 是类型别名

```typescript
type num = number;
let price: num
price = 100
```

## 联合类型

联合类型是⼀种高级类型，它表示⼀个值可以是几种不同类型之⼀。

```typescript
type Status = number | string
type Gender = '男' | '女'

function printStatus(status: Status) {
 console.log(status);
}
function logGender(str:Gender){
 console.log(str)
}

printStatus(404);
printStatus('200');
printStatus('501');
logGender('男')
logGender('女')
```

## 交叉类型

交叉类型 (`Intersection Types`) 允许将多个类型合并为⼀个类型。合并后的类型将拥有所有被合并类型的成员。交叉类型通常用于对象类型。 

```typescript
//面积
type Area = {
 height: number; //⾼
 width: number; //宽
};

//地址
type Address = {
 num: number; //楼号
 cell: number; //单元号
 room: string; //房间号
};

// 定义类型House，且House是Area和Address组成的交叉类型
type House = Area & Address;
const house: House = {
 height: 180,
 width: 75,
 num: 6,
 cell: 3,
 room: '702'
};
```

## 特殊情况

代码段1(正常)：在函数定义时，限制函数返回值为 void ，那么函数的返回值就必须是空

```typescript
function demo():void{
 // 返回undefined合法
 return undefined
 // 以下返回均不合法
 return 100
 return false
 return null
 return []
}
demo()
```

代码段2(特殊)：使用 限制函数返回值为 void 时， **TypeScript** 并不会严格要求函数返回空。

```typescript
type LogFunc = () => void
const f1: LogFunc = () => {
 return 100; // 允许返回⾮空值
};

const f2: LogFunc = () => 200; // 允许返回⾮空值

const f3: LogFunc = function () {
 return 300; // 允许返回⾮空值
};
```

官方文档说明：[Assignability of Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html#assignability-of-functions)

为了确保代码成立，`Array.prototype.push` 的返回值是⼀个数字， 而 `Array.prototype.forEach` 方法期望其回调的返回类型是 void 。

```typescript
const src = [1, 2, 3];
const dst = [0];
src.forEach((el) => dst.push(el));
```

