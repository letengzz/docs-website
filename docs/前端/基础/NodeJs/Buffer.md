# Buffer

Buffer(缓冲区)，是一个类似于Array的**对象**，用于表示固定长度的字节序列

换句话说，Buffer就是一段固定长度的内存空间，用于处理二进制数据。

![image-20231003203709841](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032037073.png)

**特点**：

1. Buffer 大小固定且无法调整

2. Buffer 性能较好，可以直接对计算机内存进行操作

3. 每个元素的大小为 1 字节 (byte) 

   ![image-20231003204111960](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032041629.png)

**说明**：Buffer 是Node.js 中的内置模块。在启动时已经将此模块自动加载，不需要手动导入即可使用，直接使用Buffer模块完成操作即可。

## 创建Buffer

### 使用alloc()创建

创建了一个长度为 10 字节的 Buffer，相当于申请了 10 字节的内存空间，每个字节的值为 0：

```js
// 使用alloc()创建
let buf = Buffer.alloc(10);
console.log(buf);
```

![image-20231003204914520](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032049104.png)

### 使用allocUnsafe()创建

创建了一个长度为 10 字节的 Buffer，buffer 中可能存在旧的数据，不会对旧数据清除，但是创建速度快。可能会影响执行结果，所以叫unsafe(不安全的)

```js
// 使用allocUnsafe()创建
let buf_2 = Buffer.allocUnsafe(10);
console.log(buf_2);
```

![image-20231003205348803](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032053823.png)

```js
let buf_3 = Buffer.allocUnsafe(100000);
console.log(buf_3);
```

![image-20231003205753935](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032057399.png)

### 使用from()创建

可以通过字符串/数组创建Buffer

```js
//通过字符串创建 Buffer
//将字母转换成Unicode 码表 然后存储成Buffer
let buf_4 = Buffer.from('hello');
console.log(buf_4);
//通过数组创建 Buffer
let buf_5 = Buffer.from([105, 108, 111, 118, 101, 121, 111, 117]);
console.log(buf_5);
```

![image-20231003210834305](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032108051.png)

## Buffer的操作

### 与字符串的转换

使用`toString()`将Buffer转换成字符串

**说明**：`toString()`默认按照utf-8编码方式进行转换

```js
let buf_6 = Buffer.from('hi');
console.log(buf_6.toString());
```

![image-20231003212348356](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032123284.png)

### Buffer的读写

Buffer 可以直接通过`[]` 的方式对数据进行处理。

```js
let buf_7 = Buffer.from('hello');

//读取单个字符
console.log(buf_7[0]);
console.log(buf_7.toString());

//修改单个字符
buf_7[0] = 97;
//查看字符串结果
console.log(buf_7.toString());
console.log(buf_7[0].toString());
//进行数字的进制转换
console.log(buf_7[0].toString(2));
```

![image-20231003213524673](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032135348.png)

## 注意

### 溢出问题

如果修改的数值超过 255 ，则超过 8 位数据会被舍弃

```js
let buf_8 = Buffer.from([361]);
console.log(buf_8[0].toString(2));  //舍弃高位的数字 0001 0110 1001 => 0110 1001
```

![image-20231003214047438](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032140695.png)

### 中文问题

一个 utf-8 的字符一般占 3 个字节

```js
let buf_9 = Buffer.from('我');
console.log(buf_9);
```

![image-20231003214249619](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310032142774.png)
