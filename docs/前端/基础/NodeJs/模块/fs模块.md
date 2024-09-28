# fs 模块

fs(`file system`，文件系统)模块，是 Node.js 中的内置模块，可以对计算机中的磁盘进行操
作，实现与硬盘的交互。例如：文件的创建、删除、重命名、移动还有文件内容的写入、读取以及文件夹的相关操作。

**导入fs 模块**：

`require()`是一个全局的函数，可以通过`require()` 导入fs模块。

```js
const fs = require('fs');
```

****

Node.js 中的磁盘操作是由其他线程完成的，结果的处理有两种模式：

- 同步处理 JavaScript 主线程会等待其他线程的执行结果，然后再继续执行主线程的代码，效率较低
- 异步处理 JavaScript 主线程不会等待其他线程的执行结果，直接执行后续的主线程代码，效率较好

## 文件操作

### 文件写入

文件写入就是将数据保存到文件中。Node.js提供了五种写入方式：

![image-20231004073207045](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040732088.png)

**注意**：使用fs模块写入时，当文件不存在 会自动创建并写入。

**使用场景**：当需要持久化保存数据的时候，会使用到文件写入功能。例如：下载文件、安装软件等。

#### 异步写入

**语法**：

```js
fs.writeFile(file, data[, options], callback)
```

**参数说明**：

- file：文件名
- data：待写入的数据
- options：选项设置 (可选)
- callback：写入回调

**返回值**：`undefined`

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//将 『你好 中国』 写入到当前文件夹下的『1.txt』文件中
fs.writeFile('./1.txt','你好 中国',err =>{
    //如果写入失败，则回调函数调用时，会传入错误对象，如写入成功，会传入 null
    if(err){
        console.log(err);
        return;
    }
    console.log('写入成功');
});
console.log('结束');
```

![image-20231004075310164](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040753423.png)

#### 同步写入

**语法**：

```js
fs.writeFileSync(file, data[, options])
```

**参数说明**：

- file：文件名
- data：待写入的数据
- options：选项设置 (可选)

**返回值**：`undefined`

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//同步写入
fs.writeFileSync('./2.txt','hello world');
console.log('写入成功');
```

![image-20231004080029491](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040800350.png)

#### 追加写入

appendFile 作用是在文件尾部追加内容，appendFile 语法与 writeFile 语法完全相同

**语法**：

```js
fs.appendFile(file, data[, options], callback)
```

```js
fs.appendFileSync(file, data[, options])
```

**返回值**： 二者都为  `undefined`

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//异步追加
fs.appendFile('2.txt','\r\n你好世界',err =>{
    if(err) throw err;
    console.log('追加成功')
});
```

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//同步追加写入
fs.appendFileSync('1.txt','Hello China');
console.log('同步追加成功');
```

![image-20231004081543210](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040815188.png)

![image-20231004081840451](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040818269.png)

使用 writeFile实现追加写入：

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
fs.writeFile('./1.txt','Hello China',{flag: 'a'},err =>{
    if(err){
        console.log(err);
        return;
    }
    console.log('追加成功');
});
console.log('结束');
```

![image-20231004085931329](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040859359.png)

#### 流式写入

**说明**：

程序打开一个文件是需要消耗资源的，流式写入可以减少打开关闭文件的次数。
流式写入方式适用于大文件写入或者频繁写入的场景，writeFile 适合于写入频率较低的场景

**语法**： 

```js
fs.createWriteStream(path[, options])
```

**参数说明**：

- path：文件路径
- options：选项配置 (可选)

**返回值**： `Object`

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

//创建写入流对象
let ws = fs.createWriteStream('./观书有感.txt');
//write
ws.write('半亩方塘一鉴开\r\n');
ws.write('天光云影共徘徊\r\n');
ws.write('问渠那得清如许\r\n');
ws.write('为有源头活水来\r\n');
//关闭通道 使用end()或close()
ws.end();
//close可选 执行完毕 通道也会被断开 可加可不加
//ws.close();
```

![image-20231004090403026](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040904519.png)

### 文件读取

文件读取就是通过程序从文件中取出其中的数据。Node.js提供的读取方式：

![image-20231004091229027](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040912523.png)

#### 异步读取

**语法**：

```js
fs.readFile(path[, options], callback)
```

**参数说明**：

- path：文件路径
- options：选项配置
- callback：回调函数

**返回值**： `undefined`

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

fs.readFile('./1.txt',(err,data) =>{
    if(err){
        console.log(err);
        return;
    }
    console.log(data);
});

fs.readFile('./1.txt','UTF-8',(err,data) =>{
    if(err){
        console.log(err);
        return;
    }
    console.log(data);
});
console.log('读取成功');
```

![image-20231004092950156](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040929020.png)

#### 同步读取

**语法**： 

```js
fs.readFileSync(path[, options])
```

**参数说明**：

- path：文件路径

- options：选项配置

**返回值**： `string` | `Buffer`

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

let data = fs.readFileSync('./1.txt');
console.log('读取成功'+data);

let data2 = fs.readFileSync('./1.txt','UTF-8');
console.log('读取成功'+data2);
```

![image-20231004093326746](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040933773.png)

#### 流式读取

**语法**： 

```js
fs.createReadStream(path[, options])
```

**参数说明**：

- path：文件路径

- options：选项配置 (可选)

**返回值**： `Object`

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

//创建读取流对象
let rs = fs.createReadStream('./1.txt');
//每次取出 64k 数据后执行一次 data 回调
rs.on('data',dunk =>{
    console.log(dunk);
    console.log(dunk.length);
});
//读取完毕后, 执行 end 回调
rs.on('end',()=>{
    console.log("读取成功");
});

//创建读取流对象
let rs2 = fs.createReadStream('./1.txt','utf8');

rs2.on('data',data =>{
    console.log(data);
    console.log(data.length);
});
rs2.on('end',()=>{
    console.log("读取成功");
});

//快速复制
const ws = fs.createWriteStream('./HelloChina.txt');
rs.pipe(ws);
```

![image-20231004094507101](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310040945155.png)

### 文件移动与重命名

在 Node.js 中，可以使用 `rename()` 或 `renameSync()` 来移动或重命名文件或文件夹

**语法**：

```js
fs.rename(oldPath, newPath, callback)
```

```js
fs.renameSync(oldPath, newPath)
```

**参数说明**：

- oldPath：文件当前的路径
- newPath：文件新的路径
- callback：操作后的回调

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

fs.rename('1.txt','你好中国.txt',(err) =>{
    if(err){
        console.log(err);
        return;
    }
    console.log('修改成功');
});
```

![image-20231004095500164](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310040955902.png)

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

fs.renameSync('1.txt','你好中国.txt');
console.log('修改成功');
```

![image-20231004100017834](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041000529.png)

### 文件删除

在 Node.js 中，使用 `unlink()` 或 `unlinkSync()` 来删除文件

**语法**：

```js
fs.unlink(path, callback)
```

```js
fs.unlinkSync(path)
```

**参数说明**：

- path：文件路径
- callback：操作后的回调

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

fs.unlink('./2.txt', (err) => {
    if (err) throw err;
    console.log('删除成功');
});
```

![image-20231004100617338](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041006750.png)

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

fs.unlinkSync('./2.txt');
console.log('删除成功');
```

![image-20231004100805277](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041008703.png)

Node.js在14.4后可以通过 `rm()`、`rmSync()` 来删除文件，使用方法同`unlink()`、`unlinkSync()`

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

fs.rm('./你好中国.txt',err => {
    if (err){
        console.log(err);
        return;
    }
    console.log('删除成功');
});
```

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

fs.rmSync('./你好中国2.txt');
console.log('删除成功');
```

## 文件夹操作

使用Node.js可以对文件夹进行创建 、读取、 删除等操作。

![image-20231004101313943](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041013044.png)

### 创建文件夹

在 Node.js 中，可以使用 `mkdir()` 或 `mkdirSync()` 来创建文件夹

**语法**：

```js
fs.mkdir(path[, options], callback)
```

```js
fs.mkdirSync(path[, options])
```

**参数说明**：

- path：文件夹路径

- options：选项配置（ 可选）
- callback：操作后的回调

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//异步创建文件夹
fs.mkdir('./page',err =>{
    if(err){
        console.log(err);
        return;
    }
    console.log('创建成功');
});
//递归异步创建
fs.mkdir('./a/b/c',{recursive:true},err =>{
    if(err){
        console.log(err);
        return;
    }
    console.log('创建成功');
});
```

![image-20231004102226590](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041022541.png)

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//同步创建文件夹
fs.mkdirSync('./index');
console.log('创建成功');
//递归同步创建
fs.mkdirSync('./aa/bb',{recursive:true});
console.log('创建成功');
```

![image-20231004102536780](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041025909.png)

### 读取文件夹

在 Node.js 中，可以使用 `readdir()` 或 `readdirSync()` 来读取文件夹

**语法**：

```js
fs.readdir(path[, options], callback)
```

```js
fs.readdirSync(path[, options])
```

**参数说明**：

- path：文件夹路径
- options：选项配置（ 可选）
- callback：操作后的回调

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//异步读取
fs.readdir('./page',(data,err) =>{
    if(err){
        console.log(err);
        return;
    }
    console.log(data);
});
```

![image-20231004103413229](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041034273.png)

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//同步读取x
let data = fs.readdirSync('./page');
console.log(data);
```

![image-20231004103645744](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041036230.png)

### 删除文件夹

在 Node.js 中，我们可以使用 rmdir 或 rmdirSync 来删除文件夹

**语法**：

```js
fs.rmdir(path[, options], callback)
```

```js
fs.rmdirSync(path[, options])
```

**参数说明**：

- path：文件夹路径
- options：选项配置（ 可选）
- callback：操作后的回调

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//异步删除文件夹
fs.rmdir('./page',err =>{
    if(err){
        console.log(err);
        return;
    }
    console.log('删除成功');
});

//异步递归删除文件夹
fs.rmdir('./a',{recursive:true},err =>{
    if(err){
        console.log(err);
        return;
    }
    console.log('删除成功');
});
```

![image-20231004104938491](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041049761.png)

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//同步删除文件夹
fs.rmdirSync('./index');

//同步递归删除文件夹
fs.rmdirSync('./aa',{recursive:true});
```

![image-20231004105034151](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041051724.png)

Node.js在14.4后可以通过 `rm()`、`rmSync()` 来删除文件夹，使用方法同`rmdir()`、`rmdirSync()`

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//推荐使用
fs.rm('./你好中国.txt',err => {
    if (err){
        console.log(err);
        return;
    }
    console.log('删除成功');
});
```

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//推荐使用
fs.rmSync('./你好中国2.txt');
console.log('删除成功');
```

## 查看资源状态

在 Node.js 中，可以使用 `stat()` 或 `statSync()` 来查看资源的详细信息

**语法**：

```js
fs.stat(path[, options], callback)
```

```js
fs.statSync(path[, options])
```

**参数说明**：

1. path：文件夹路径
2. options：选项配置（ 可选）
3. callback：操作后的回调

**结果值对象结构**：

1. size 文件体积
2. birthtime 创建时间
3. mtime 最后修改时间
4. isFile 检测是否为文件
5. isDirectory 检测是否为文件夹
6. ....

****

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');

fs.stat('./你好中国.txt',(err,data) =>{
    if(err){
        console.log(err);
        return;
    }
    console.log(data);
    //查看是否是一个文件
    console.log(data.isFile());
    //查看是否是一个文件夹
    console.log(data.isDirectory());
});
```

![image-20231004142323662](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041458387.png)

```js
// require 是 Node.js 环境中的'全局'变量，用来导入模块
const fs = require('fs');
//同步获取状态
let data = fs.statSync('./你好中国.txt');
console.log(data);
```

![image-20231004105732473](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310041057114.png)

## 相对路径问题

fs 模块对资源进行操作时，路径的写法有两种：

- 相对路径
  - `./1.txt`：当前目录下的1.txt
  - `1.txt`：等效于上面的写法
  - `../1.txt`：当前目录的上一级目录中的1.txt
- 绝对路径
  - `D:/Program Files windows`：系统下的绝对路径
  - `/usr/bin`：Linux 系统下的绝对路径

相对路径中所谓的当前目录，**指的是命令行的工作目录，而并非是文件的所在目录**

**注意**：当命令行的工作目录与文件所在目录不一致时，会出现一些 BUG

## __dirname

`__dirname` 与 require 类似，都是 Node.js 环境中的'全局'变量

`__dirname` 保存着**当前文件所在目录的绝对路径**，可以使用 `__dirname` 与文件名拼接成绝对路径

```js
let data = fs.readFileSync(__dirname + '/data.txt');
console.log(data);
```

**说明**：使用 fs 模块的时候，尽量使用 `__dirname` 将路径转化为绝对路径，这样可以避免相对路径产生的
Bug
