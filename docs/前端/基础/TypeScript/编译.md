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

2. 使用[npm](../NodeJs/包管理工具/npm.md)全局安装TypeScript：

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

也可以通过使用后接 `-w` ，TS编译器会自动监视文件的变化，并在文件发生变化时对文件进行重新编译。

```shell
tsc xxx.ts -w
```

## 配置文件

tsconfig.json是一个JSON文件，添加配置文件后，只需只需 tsc 命令即可完成对整个项目的编译

配置选项：

- include：定义希望被编译文件所在的目录，默认值：`["\*\*/\*"]`

  所有src目录和tests目录下的文件都会被编译：

  ```json
  "include":["src/**/*", "tests/**/*"]
  ```

- exclude：定义需要排除在外的目录，默认值：`["node_modules", "bower_components", "jspm_packages"]`

  src下hello目录下的文件都不会被编译：

  ```json
  "exclude": ["./src/hello/**/*"]
  ```

- extends：定义被继承的配置文件

  当前配置文件中会自动包含config目录下base.json中的所有配置信息：

  ```json
  "extends": "./configs/base"
  ```

- files：指定被编译文件的列表，只有需要编译的文件少时才会用到

  列表中的文件都会被TS编译器所编译：

  ```json
  "files": [
      "core.ts",
      "sys.ts",
      "types.ts",
      "scanner.ts",
      "parser.ts",
      "utilities.ts",
      "binder.ts",
      "checker.ts",
      "tsc.ts"
    ]
  ```

- compilerOptions：编译选项是配置文件中非常重要也比较复杂的配置选项

  在compilerOptions中包含多个子选项，用来完成对编译的配置

  项目选项：

  - target：设置ts代码编译的目标版本

    可选值：ES3（默认）、ES5、ES6/ES2015、ES7/ES2016、ES2017、ES2018、ES2019、ES2020、ESNext

    s代码将会被编译为ES6版本的js代码：

    ```json
    "compilerOptions": {
        "target": "ES6"
    }
    ```

  - lib：指定代码运行时所包含的库（宿主环境）

    可选值：ES5、ES6/ES2015、ES7/ES2016、ES2017、ES2018、ES2019、ES2020、ESNext、DOM、WebWorker、ScriptHost ......

    ```json
    "compilerOptions": {
        "target": "ES6",
        "lib": ["ES6", "DOM"],
        "outDir": "dist",
        "outFile": "dist/aa.js"
    }
    ```

  - module：设置编译后代码使用的模块化系统

    可选值：CommonJS、UMD、AMD、System、ES2020、ESNext、None

    ```typescript
    "compilerOptions": {
        "module": "CommonJS"
    }
    ```

  - outDir：编译后文件的所在目录

    默认情况下，编译后的js文件会和ts文件位于相同的目录，设置outDir后可以改变编译后文件的位置

    设置后编译后的js文件将会生成到dist目录：

    ```json
    "compilerOptions": {
        "outDir": "dist"
    }
    ```

  - outFile：将所有的文件编译为一个js文件，默认会将所有的编写在全局作用域中的代码合并为一个js文件，如果module制定了None、System或AMD则会将模块一起合并到文件之中

    ```json
    "compilerOptions": {
        "outFile": "dist/app.js"
    }
    ```

  - rootDir：指定代码的根目录，默认情况下编译后文件的目录结构会以最长的公共目录为根目录，通过rootDir可以手动指定根目录

    ```json
    "compilerOptions": {
        "rootDir": "./src"
    }
    ```

  - allowJs：是否对js文件编译

  - checkJs：是否对js文件进行检查

    ```json
    "compilerOptions": {
        "allowJs": true,
        "checkJs": true
    }
    ```

  - removeComments：是否删除注释，默认值：false

  - noEmit：不对代码进行编译，默认值：false

  - sourceMap：是否生成sourceMap，默认值：false


  - 严格检查

    - strict：启用所有的严格检查，默认值为true，设置后相当于开启了所有的严格检查
    - alwaysStrict：总是以严格模式对代码进行编译
    - noImplicitAny：禁止隐式的any类型
    - noImplicitThis：禁止类型不明确的this
    - strictBindCallApply：严格检查bind、call和apply的参数列表
    - strictFunctionTypes：严格检查函数的类型
    - strictNullChecks：严格的空值检查
    - strictPropertyInitialization：严格检查属性是否初始化

  - 额外检查

    - noFallthroughCasesInSwitch：检查switch语句包含正确的break
    - noImplicitReturns：检查函数没有隐式的返回值
    - noUnusedLocals：检查未使用的局部变量
    - noUnusedParameters：检查未使用的参数

  - 高级

    - allowUnreachableCode：检查不可达代码

      可选值：

      - true，忽略不可达代码
      - false，不可达代码将引起错误

    - noEmitOnError：有错误的情况下不进行编译，默认值：false

## webpack

通常情况下，实际开发中我们都需要使用构建工具对代码进行打包，TS同样也可以结合构建工具一起使用，下边以webpack为例介绍一下如何结合构建工具使用TS。

步骤：

1. 初始化项目，创建package.json文件：进入项目根目录，执行命令：

   ```shell
   npm init -y
   ```

2. 下载构建工具

   ```shell
   npm i -D webpack webpack-cli webpack-dev-server typescript ts-loader clean-webpack-plugin
   ```

   共安装了7个包

   - webpack：构建工具webpack
   - webpack-cli：webpack的命令行工具
   - webpack-dev-server：webpack的开发服务器
   - typescript：ts编译器
   - ts-loader：ts加载器，用于在webpack中编译ts文件
   - html-webpack-plugin：webpack中html插件，用来自动创建html文件
   - clean-webpack-plugin：webpack中的清除插件，每次构建都会先清除目录

3. 根目录下创建webpack的配置文件webpack.config.js

   ```js
    const path = require("path");
    const HtmlWebpackPlugin = require("html-webpack-plugin");
    const { CleanWebpackPlugin } = require("clean-webpack-plugin");
    
    module.exports = {
        optimization:{
            minimize: false // 关闭代码压缩，可选
        },
    
        entry: "./src/index.ts",
        
        devtool: "inline-source-map",
        
        devServer: {
            contentBase: './dist'
        },
    
        output: {
            path: path.resolve(__dirname, "dist"),
            filename: "bundle.js",
            environment: {
                arrowFunction: false // 关闭webpack的箭头函数，可选
            }
        },
    
        resolve: {
            extensions: [".ts", ".js"]
        },
        
        module: {
            rules: [
                {
                    test: /\.ts$/,
                    use: {
                       loader: "ts-loader"     
                    },
                    exclude: /node_modules/
                }
            ]
        },
    
        plugins: [
            new CleanWebpackPlugin(),
            new HtmlWebpackPlugin({
                title:'TS测试'
            }),
        ]
    
    }
   ```

4. 根目录下创建tsconfig.json，配置可以根据自己需要

   ```js
    {
        "compilerOptions": {
            "target": "ES2015",
            "module": "ES2015",
            "strict": true
        }
    }
   ```

5. 修改package.json添加如下配置

   ```js
    {
      ...略...
      "scripts": {
        "test": "echo \"Error: no test specified\" && exit 1",
        "build": "webpack",
        "start": "webpack serve --open chrome.exe"
      },
      ...略...
    }
   ```

6. 在src下创建ts文件，并在并命令行执行`npm run build`对代码进行编译，或者执行`npm start`来启动开发服务器

   ```shell
   npm run build
   ```

   ```
   npm start
   ```

## Babel

经过一系列的配置，使得TS和webpack已经结合到了一起，除了webpack，开发中还经常需要结合babel来对代码进行转换以使其可以兼容到更多的浏览器，在上述步骤的基础上，通过以下步骤再将babel引入到项目中。

1. 安装依赖包：

   ```shell
   npm i -D @babel/core @babel/preset-env babel-loader core-js
   ```

   共安装了4个包，分别是：

   - @babel/core：babel的核心工具
   - @babel/preset-env：babel的预定义环境
   - @babel-loader：babel在webpack中的加载器
   - core-js：core-js用来使老版本的浏览器支持新版ES语法

2. 修改webpack.config.js配置文件

   - ```shell
      ...略...
      module: {
          rules: [
              {
                  test: /\.ts$/,
                  use: [
                      {
                          loader: "babel-loader",
                          options:{
                              presets: [
                                  [
                                      "@babel/preset-env",
                                      {
                                          "targets":{
                                              "chrome": "58",
                                              "ie": "11"
                                          },
                                          "corejs":"3",
                                          "useBuiltIns": "usage"
                                      }
                                  ]
                              ]
                          }
                      },
                      {
                          loader: "ts-loader",
      
                      }
                  ],
                  exclude: /node_modules/
              }
          ]
      }
      ...略...
     ```

   - 如此一来，使用ts编译后的文件将会再次被babel处理，使得代码可以在大部分浏览器中直接使用，可以在配置选项的targets中指定要兼容的浏览器版本。
