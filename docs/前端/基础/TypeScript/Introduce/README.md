# TypeScript 概述

TypeScript是微软开发的一个开源的编程语言。TypeScript是JavaScript的超集(基于JavaScript**扩展语言**)，通过在JavaScript的基础上添加静态类型定义构建而成，并添加了许多新的特性，对JavaScript进行了扩展。TypeScript通过TypeScript编译器或Babel转译为JavaScript代码，再交由JavaScript解析器执行。可以运行在任何浏览器，任何操作系统。TypeScript完全兼容JavaScript，换言之，任何的JavaScript代码都可以直接当成JavaScript使用。

![image-20240817141032767](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202408171443537.png)

JavaScript中的困扰：

1. 不清不楚的数据类型

   ```js
   let welcome = 'hello'
   welcom() //此行报错：TypeError: welcome is not a function
   ```

2. 有漏洞的逻辑

   ```js
   const str = Date.now() % 2 ? '奇数' : '偶数'
   
   if(str !== '奇数'){
       alert('hello')
   }else if(str === '偶数'){
       alert('world')
   }
   ```

3. 访问不存在的属性

   ```js
   const obj = {width: 10,height: 15}
   const area = obj.width * obj.heigth;
   ```

4. 低级的拼写错误

   ```javascript
   const message = 'hello world'
   message.toUperCase()
   ```

相较于JavaScript而言：

- TypeScript拥有了静态类型，更加严格的语法，更强大的功能
- TypeScript可以在代码执行前就完成代码的检查，减小了运行时异常的出现的几率
- TypeScript不能被JavaScript解析器直接执行，但是TypeScript代码可以编译为任意版本的JavaScript代码，可有效解决不同JavaScript运行环境的兼容问题
- 同样的功能，TypeScript的代码量要大于JavaScript，但由于TypeScript的代码结构更加清晰，变量类型更加明确，在后期代码的维护中TypeScript却远远胜于JavaScript。

![u=3023260295,131125603&fm=253&fmt=auto&app=138&f=PNG](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img202406081213688.webp)
