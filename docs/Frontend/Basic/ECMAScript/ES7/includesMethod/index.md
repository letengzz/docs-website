# Array.prototype.includes()方法

在ES7中，`Array.prototype.includes()`方法被引入，用于判断一个数组是否包含一个指定的值。这个方法返回一个布尔值，如果包含指定的值则返回true，否则返回false。这个方法可以代替indexOf()方法，使代码更加简洁和易于阅读。

```javascript
const arr = [1, 2, 3, 4, 5]
console.log(arr.includes(3)) // true
console.log(arr.includes(6)) // false
```
