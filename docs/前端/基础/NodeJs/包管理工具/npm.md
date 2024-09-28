# npm 包管理工具

npm( `Node Package Manager`，Node 的包管理工具) 是 node.js 官方内置的包管理工具，是必须要掌握住的工具。

**官方网站**：https://npmjs.com

node.js 在安装时会自动安装 npm ，所以如果已经安装了 node.js，可以直接使用 npm

可以通过 `npm -v` 查看版本号测试，如果显示版本号说明安装成功，反之安装失败

```bash
npm -v
```

![image-20231011144704897](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310111447348.png)

## 基本使用

### 初始化

创建一个空目录，然后以此目录作为工作目录启动命令行工具，执行 `npm init`

```shell
npm init
```

如果想直接生成 package.json 文件可以使用命令：

```shell
npm init -y
```

npm init 命令的作用是将文件夹初始化为一个包， **交互式创建 package.json 文件**

![image-20231025205635368](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202310252056527.png)

package.json 是包的配置文件，每个包都必须要有 package.json

package.json 例：

```json
{
	"name": "pro-test",
	"version": "1.0.0",
	"description": "描述",
	"main": "index.js",
	"scripts": {
		"test": "echo \"Error: no test specified\" && exit 1"
	},
	"author": "hjc",
	"license": "ISC"
}
```

属性翻译：

```json
{
	"name": "pro-test", #包的名字
	"version": "1.0.0", #包的版本
	"description": "描述", #包的描述
	"main": "index.js", #包的入口文件
	"scripts": { #脚本配置
		"test": "echo \"Error: no test specified\" && exit 1"
	},
	"author": "hjc", #作者
	"license": "ISC" #开源证书
}
```

**初始化的过程中注意事项**：

1. package name (包名) 不能使用中文、大写。默认值是文件夹的名称，所以文件夹名称也不能使用中文和大写

2. version (版本号)要求 x.x.x 的形式定义， x 必须是数字，默认值是 1.0.0

3. ISC 证书与 MIT 证书功能上是相同的，关于开源证书扩展阅读：<http://www.ruanyifeng.com/bl
    og/2011/05/how_to_choose_free_software_licenses.html>

4. package.json 可以手动创建与修改

5. 使用 `npm init -y` 或者`npm init --yes` 极速创建package.json

### 搜索包

**搜索包命令行**：`npm s/search 关键字`

```bash
npm s 关键字
```

```bash
npm search 关键字
```

**搜索包的网站**：https://www.npmjs.com/

### 下载安装包

可以通过 `npm install` 和`npm i` 命令安装包

**基本格式**：

```shell
npm install <包名>[@版本号]
```

```shell
npm i <包名>[@版本号]
```

**例**：

```shell
npm install uniq

npm i uniq
```

运行之后文件夹下会增加两个资源：

- node_modules：文件夹存放下载的包
- package-lock.json：包的锁文件，用来锁定包的版本

安装 uniq 之后， uniq 就是当前这个包的一个依赖包，有时会简称为**依赖**

比如创建一个包名字为 A，A 中安装了包名字是 B，那么 B 是 A 的一个依赖包，也会说 A 依赖 B

### 导入包

**导入包并使用函数**：

```js
//1. 导入uniq 包
const uniq = require('uniq');
//2. 使用函数
let arr = [1,2,3,4,5,6,4,3,2,1];

const result = uniq(arr);

console.log(result);
```

导入包：

```js
//导入uniq 包
const uniq = require('uniq');
const uniq = require('./node_modules/uniq');
const uniq = require('./node_modules/uniq/uniq.js');
```

**require 导入 npm 包基本流程**：

1. 在当前文件夹下 node_modules 中寻找同名的文件夹

2. 在上级目录中下的 node_modules 中寻找同名的文件夹，直至找到磁盘根目录

## 生产环境与开发环境

**开发环境**是程序员专门用来写代码的环境，一般是指程序员的电脑，开发环境的项目一般只能程序员自己访问

****

**生产环境**是项目代码正式运行的环境，一般是指正式的服务器电脑，生产环境的项目一般每个客户都可以访问

## 生产依赖与开发依赖

可以在安装时设置选项来区分依赖的类型，目前分为两类：

![image-20231025231002720](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202310252312923.png)

- 开发依赖是只在开发阶段使用的依赖包
- 生产依赖是开发阶段和最终上线运行阶段都用到的依赖包

## 全局安装

可以执行安装选项 `-g` 进行全局安装

```shell
npm i -g nodemon
```

全局安装完成之后就可以在命令行的任何位置运行 nodemon 命令 

**nodemon 命令的作用**：自动重启 node 应用程序

执行脚本：

```shell
nodemon 文件名.js
```

**说明**：

-  全局安装的命令不受工作目录位置影响 

- 可以通过 `npm root -g` 可以查看全局安装包的位置 

  ```shell
  npm root -g
  ```

- 不是所有的包都适合全局安装 ， 只有全局类的工具才适合，可以通过 查看包的官方文档来确定 安装方式

**修改 windows 执行策略**：

windows 默认不允许 npm 全局命令执行脚本文件，所以需要修改执行策略

1. 以 管理员身份 打开 powershell 命令行 

2. 键入命令 `set-ExecutionPolicy remoteSigned`

   ```bash
   set-ExecutionPolicy remoteSigned
   ```

3. 键入 A 然后敲回车 

4. 如果不生效，可以尝试重启 vscode 

   ```shell
   npm i -g nodemon 
   ```

## 环境变量 Path

Path 是操作系统的一个环境变量，可以设置一些文件夹的路径，在当前工作目录下找不到可执行文件时，就会在环境变量 Path 的目录中挨个的查找，如果找到则执行，如果没有找到就会报错 

**说明**： 

- 如果希望某个程序在任何工作目录下都能正常运行，就应该将该程序的所在目录配置到环境 变量 Path 中 

- Windows 下查找命令的所在位置：
  - cmd 命令行 中执行 where nodemon 
  - powershell命令行 执行 get-command nodemon

## 安装包依赖

在项目协作中有一个常用的命令就是 `npm i` ，通过该命令可以依据 package.json 和 packagelock.json 的依赖声明安装项目依赖 

```shell
npm i
```

```shell
npm install
```

**注意**：node_modules 文件夹大多数情况都不会存入版本库

## 安装指定版本的包

项目中可能会遇到版本不匹配的情况，有时就需要安装指定版本的包

**使用格式**：

```shell
npm i <包名@版本号> 
```

**例**：

```shell
npm i jquery@1.11.2
```

## 删除依赖

项目中可能需要删除某些不需要的包，可以使用 `npm remove` 删除

**局部删除**：

```shell
npm remove uniq
```

```shell
npm r uniq
```

**全局删除**：

```shell
npm remove -g nodemon
```

```shell
npm r -g nodemon
```

## 卸载包

卸载包：

```shell
npm uninstall 包名
```

全局卸载：

```shell
npm uninstall -g 包名
```

## 更新包

更新包 (更新到最新版本)：

```shell
npm update 包名
```

全局更新：

```shell
npm update -g 包名
```

## 配置命令别名

通过配置命令别名可以更简单的执行命令 

配置 package.json 中的 scripts 属性：

```json
{
	.
	.
	.
	"scripts": {
		"server": "node server.js",
		"start": "node index.js"
	},
	.
	.
}

```

通过配置命令别名可以更简单的执行命令

```shell
npm run server
npm run start
```

配置完成之后，可以使用别名执行命令。

不过 start 别名比较特别，使用时可以省略 run

```shell
npm start
```

**说明**：

- `npm start` 是项目中常用的一个命令，一般用来启动项目 
- `npm run` 有自动向上级目录查找的特性，跟 require 函数也一样 对于陌生的项目，可以通过查看 scripts 属性来参考项目的一些操作

## 配置淘宝镜像

在使用npm命令时，默认是从国外的官方仓库(http://npmjs.com)下载依赖，下载速度可能会比较慢，甚至下载失败，通常使用国内淘宝的npm仓库源，提高下载速度。

用 npm 也可以使用淘宝镜像，配置的方式有两种

### 直接配置

执行命令即可完成配置：

```shell
npm config set registry https://registry.npmmirror.com/
```

查看当前仓库源：

```shell
npm config get registry
```

查看npm配置信息：

```shell
npm config list
```

### 工具配置

使用 `nrm` (npm registry manager)配置 npm 的镜像地址：

1. 安装 nrm：

   ```shell
   npm i -g nrm
   ```

2. 修改镜像：

   ```shell
   nrm use taobao
   ```

3. 检查是否配置成功

   ```shell
   npm config list
   ```

   检查 registry 地址是否为 https://registry.npmmirror.com/ , 如果 **是** 则表明成功 

改回官方镜像：

1. 查看镜像地址：

   ```shell
   nrm ls
   ```

2. ```shell
   nrm use npm
   ```

**说明**：

1. 建议使用第二种方式 进行镜像配置，因为后续修改起来会比较方便
1. 虽然 cnpm 可以提高速度，但是 npm 也可以通过淘宝镜像进行加速，所以 npm 的使用率还是高于 cnpm

## 注意点

默认仓库地址是当前用户目录下，如果当前用户**目录有中文**，需要修改：

![image-20240710213416533](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202407102134268.png)

## 配置全局安装路径

配置全局安装：

```shell
npm config set prefix D:\atguigu\node-global
```

## 配置缓存路径

配置缓存路径：

```shell
npm config set cache D:\hjc\node-cache
```

