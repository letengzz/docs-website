# ES 6

ECMAScript 6.0 (以下简称 ES6) 是 JavaScript 语言的下一代标准，已经在 2015 年 6 月正式发布了。它的目标，是使得 JavaScript 语言可以用来编写复杂的大型应用程序，成为企业级开发语言。

ECMAScript 和 JavaScript 的关系是，前者是后者的规格，后者是前者的一种实现 (另外的 ECMAScript 的实现还有 Jscript 和 ActionScript)

## 模块化开发

传统非模块化开发有如下的缺点：

- 命名冲突
- 文件依赖

模块化规范：

- CommonJS模块化规范（ES5模块化规范）
- ES6模块化规范

ES6使用 export 和 import 来导出、导入模块。

### ES6模块化写法一

#### 导出模块

创建 src/userApi.js

```javascript
export function getList() {
    console.log('获取数据列表')
}
export function save() {
    console.log('保存数据')
}
```

#### 导入模块

创建 src/userComponent.js

```javascript
//只取需要的方法即可，多个方法用逗号分隔
import { getList, save } from "./userApi.js"
getList()
save()
```

**注意：这时程序无法运行，因为ES6的模块化无法在Node.js中执行，需要用Babel编辑成ES5后再执行。**

#### 安装Babel

Babel是一个广泛使用的转码器，可以将ES6代码转为ES5代码，从而在现有环境执行

**安装命令行转码工具**

Babel提供babel-cli工具，用于命令行转码。它的安装命令如下：

```shell
npm install --global babel-cli
#查看是否安装成功
babel --version
```

如果提示以下错误

```shell
babel : 无法加载文件 C:\Users\hjc\AppData\Roaming\npm\babel.ps1，因为在此系统上禁止运行脚本。有关详细信息，请参阅 https:/go.mi
crosoft.com/fwlink/?LinkID=135170 中的 about_Execution_Policies。
所在位置 行:1 字符: 1
+ babel --version
+ ~~~~~
    + CategoryInfo          : SecurityError: (:) []，PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

在电脑中直接搜索PowerShell 以管理员方式运行
执行 `set-ExecutionPolicy RemoteSigned`，输入y敲回车

#### 配置.babelrc

Babel的配置文件是.babelrc，存放在项目的根目录下，该文件用来设置转码规则和插件，presets字段设定转码规则，将es2015规则加入 .babelrc：

```javascript
{
    "presets": ["es2015"],
    "plugins": []
}
```

#### 安装转码器

在项目中安装

```shell
npm install --save-dev babel-preset-es2015
```

#### 转码

```shell
# 整个目录转码
mkdir dist1
# --out-dir 或 -d 参数指定输出目录
babel src -d dist1
```

#### 运行程序 

```shell
node dist1/userComponent.js
```

### ES6模块化写法二

#### 导出模块

创建 es6/userApi2.js

```javascript
export default {
    getList() {
        console.log('获取数据列表2')
    },
    save() {
        console.log('保存数据2')
    }
}
```

#### 导入模块

创建 es6/userComponent2.js

```javascript
import user from "./userApi2.js"
user.getList()
user.save()
```

#### 转码

```shell
# 整个目录转码
mkdir dist2
# --out-dir 或 -d 参数指定输出目录
babel es6 -d dist2
```

#### 运行程序 

```shell
node dist2/userComponent2.js
```

