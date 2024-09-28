# TypeScript 编译

浏览器不能直接运行 TypeScript 代码，需要编译为 JavaScript 再交由浏览器解析器执行。

## 命令行编译

需要`.ts`文件编译为`.js`文件，需要配置TypeScript 编译环境：

1. 创建 `demo.ts`文件：

   ```typescript
   const person = {
       name: '李四',
       age: 18
   }
   console.log(`我叫${person.name}，我今年${person.age}岁了`)
   ```

2. 使用[npm](../../NodeJS/Package/npm/README.md)全局安装TypeScript：

   ```shell
   npm i -g typescript
   ```

3. 使用tsc对ts文件进行编译：

   - 命令行进入ts文件所在目录

   - 执行命令转换成JavaScript：tsc xxx.ts

   ![image-20240608122805910](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img202406081228089.png)

## 自动化编译

1. 创建TypeScript编译控制文件：

   - 工程中会生成一个 `tsconfig.json` 配置文件，其中包括着很多编译时的配置
   - 默认编译的JS版本是ES7，可以手动调整为其他版本

   ```shell
   tsc --init
   ```

2. 监视目录的ts文件变化：

   ```shell
   tsc --watch
   ```

3. 当编译出错时不生成js文件：也可以修改 `tsconfig.json` 中的 `noEmitOnError`配置

   ```shell
   tsc --noEmitOnError --watch
   ```
