# TypeScript 基本使用

## 类型声明

类型声明是TypeScript非常重要的一个特点，通过类型声明可以指定TypeScript中变量 (参数、形参) 的类型。指定类型后，当为变量赋值时，TypeScript编译器会自动检查值是否符合类型声明，符合则赋值，否则报错。

简而言之，类型声明给变量设置了类型，使得变量只能存储某种类型的值。

语法：使用 `:` 来对变量或函数形参，进行类型声明

```typescript
let 变量: 类型;

let 变量: 类型 = 值;

function fn(参数: 类型, 参数: 类型): 类型{
    ...
}
```

**注意**：在 `:` 后也可以写字面量类型，不过实际开发中用的不多。

```typescript
let a: '你好' //a的值只能为字符串“你好”
let b: 100 //b的值只能为数字100
a = '欢迎'//警告：不能将类型“"欢迎"”分配给类型“"你好"”
b = 200 //警告：不能将类型“200”分配给类型“100”
```

## 自动类型判断

TypeScript拥有自动的类型判断机制。当对变量的声明和赋值是同时进行的，TypeScript编译器会自动判断变量的类型。所以如果变量的声明和赋值时同时进行的，可以省略掉类型声明。

```typescript
let a: string //变量a只能存储字符串
let b: number //变量b只能存储数值
let c: boolean //变量c只能存储布尔值

a = 'hello'
a = 100 //警告：不能将类型“number”分配给类型“string”

b = 666
b = '你好'//警告：不能将类型“string”分配给类型“number”

c = true
c = 666 //警告：不能将类型“number”分配给类型“boolean”

// 参数x必须是数字，参数y也必须是数字，函数返回值也必须是数字
function demo(x:number,y:number):number{
 return x + y
}

demo(100,200)
demo(100,'200') //警告：类型“string”的参数不能赋给类型“number”的参数
demo(100,200,300) //警告：应有 2 个参数，但获得 3 个
demo(100) //警告：应有 2 个参数，但获得 1 个
```

```typescript
let n = 56
n.toFixed(2)
/*
当执行n.toFixed(2) ，底层做了这几件事：
 1.let temp = new Number(42)
 2.value = temp.toFixed(2)
 3.删除value
 4.返回value
*/
```

## 类型断言

有些情况下，变量的类型是很明确，但是TS编译器却并不清楚，此时，可以通过类型断言来告诉编译器变量的类型。

断言有两种形式：

- 第一种：

  ```typescript
  let someValue: unknown = "this is a string";
  let strLength: number = (someValue as string).length;
  ```

- 第二种：

  ```typescript
  let someValue: unknown = "this is a string";
  let strLength: number = (<string>someValue).length;
  ```


## 联合类型

可以使用` | `来连接多个类型

```typescript
let b: "male" | "female";
b = "male";
b = "female";

let c: boolean | string;
c = true;
c = 'hello';
```

