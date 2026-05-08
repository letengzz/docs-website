# 对象解构的剩余和展开属性

在ES7中，对象解构的剩余和展开属性被引入，允许在对象解构中使用剩余和展开属性。这个特性使代码更加简洁和易于维护。例如：

```javascript
const { a, b, ...rest } = { a: 1, b: 2, c: 3, d: 4 }
console.log(a) // 1
console.log(b) // 2
console.log(rest) // { c: 3, d: 4 }
```
