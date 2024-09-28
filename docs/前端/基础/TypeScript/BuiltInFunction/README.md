# TypeScript 内置函数

在 JavaScript 中的这些内置构造函数： Number 、 String 、 Boolean ，用于 创建对应的包装对象， 在日常开发时很少使用，在 TypeScript 中也是同理，所以 在 TypeScript 中进行类型声明时，通常都是用小写的 number 、 string 、 boolean

```typescript
let str1: string
str1 = 'hello'
str1 = new String('hello') //报错

let str2: String
str2 = 'hello'
str2 = new String('hello')

console.log(typeof str1)
console.log(typeof str2)
```

- **原始类型**：如 number 、 string 、 boolean ，在 JavaScript 中是简单数据类型，它们在内存中占用空间少，处理速度快。
- **包装对象**：如 Number 对象、 String 对象、 Boolean 对象，是复杂类型，在 内存中占用更多空间，在日常开发时很少由开发人员自己创建包装对象。 
- **自动装箱**：JavaScript 在必要时会自动将原始类型包装成对象，以便调用方法或访问属性

```typescript
// 原始类型字符串
let str = 'hello';
// 当访问str.length时，JavaScript引擎做了以下⼯作：
let size = (function() {
 // 1. ⾃动装箱：创建⼀个临时的String对象包装原始字符串
 let tempStringObject = new String(str);
 // 2. 访问String对象的length属性
 let lengthValue = tempStringObject.length;
 // 3. 销毁临时对象，返回⻓度值
 // （JavaScript引擎⾃动处理对象销毁，开发者⽆感知）
 return lengthValue;
})();
console.log(size); // 输出: 5
```
