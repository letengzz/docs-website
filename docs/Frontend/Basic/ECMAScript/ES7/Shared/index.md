# 共享内存和原子操作

在ES7中，共享内存和原子操作被引入，允许在多个线程之间共享数据，使用原子操作来确保数据的一致性和可靠性。这个特性使JavaScript可以更好地处理并发和多线程编程。

```javascript
const buffer = new SharedArrayBuffer(8)
const view = new Int32Array(buffer)

function increment() {
  Atomics.add(view, 0, 1)
}

increment()
console.log(view[0]) // 1
```
