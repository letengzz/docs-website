# 创建 Vue3 工程

## 基于 vue-cli 创建

官方文档：https://cli.vuejs.org/zh/guide/creating-a-project.html#vue-create

**说明**：目前`vue-cli`已处于维护模式，官方推荐基于 `Vite` 创建项目。

Vue CLI 4.x 需要 [Node.js](https://nodejs.org/) v8.9 或更高版本 (推荐 v10 以上)。可以使用 [n](https://github.com/tj/n)，[nvm](https://github.com/creationix/nvm) 或 [nvm-windows](https://github.com/coreybutler/nvm-windows) 在同一台电脑中管理多个 Node 版本。

可以使用下列任一命令安装这个新的包：

```powershell
npm install -g @vue/cli
# OR
yarn global add @vue/cli
```

安装之后，可以在命令行中访问 `vue` 命令。可以通过简单运行 `vue`，看看是否展示出了一份所有可用命令的帮助信息，来验证它是否安装成功。

可以用这个命令来检查其版本是否正确：

```powershell
## 查看@vue/cli版本，确保@vue/cli版本在4.5.0以上
vue --version
```

![image-20240130223431436](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401302234174.png)

如需升级全局的 Vue CLI 包，请运行：

```powershell
npm update -g @vue/cli
# 或者
yarn global upgrade --latest @vue/cli
```

执行创建命令：

```powershell
vue create vue_test
##  随后选择3.x
##  Choose a version of Vue.js that you want to start the project with (Use arrow keys)
##  > 3.x
##    2.x
```

![image-20240130224142087](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401302241412.png) 

启动：

```powershell
cd vue_test
npm run serve
```

![image-20240130224239693](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401302242475.png)

访问  http://localhost:8080/ ：

![image-20240130224338381](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401302243688.png)

## 基于 vite 创建

**说明**：推荐使用 [Vite](https://vitejs.dev/) 创建。

**官方文档**：https://cn.vuejs.org/guide/quick-start.html#creating-a-vue-application

创建项目：

```powershell
## 创建命令
npm create vue@latest
```

具体配置：

```powershell
## 配置项目名称
√ Project name: vue3_test
## 是否添加TypeScript支持
√ Add TypeScript?  Yes
## 是否添加JSX支持
√ Add JSX Support?  No
## 是否添加路由环境
√ Add Vue Router for Single Page Application development?  No
## 是否添加pinia环境
√ Add Pinia for state management?  No
## 是否添加单元测试
√ Add Vitest for Unit Testing?  No
## 是否添加端到端测试方案
√ Add an End-to-End Testing Solution? » No
## 是否添加ESLint语法检查
√ Add ESLint for code quality?  Yes
## 是否添加Prettiert代码格式化
√ Add Prettier for code formatting?  No
```

![image-20240130231116713](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401302311574.png)

安装所有依赖并启动：

```powershell
cd vue3_test
npm install
npm run dev
```

![image-20240130231455414](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401302314063.png)

访问  http://localhost:5173/ ：

![image-20240130231532887](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202401302315780.png)
