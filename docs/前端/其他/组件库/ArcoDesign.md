# ArcoDesign

![image-20240206210641045](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409281507010.png)

官方网站：https://arco.design/

## 创建项目

官方教程：https://arco.design/vue/docs/pro/start

### 前期准备

本项目的技术栈为 `vue` + `ES2015+` + `TypeScript` + `Arco Design `和 `echarts`等

首先开始开发之前，请确认本地环境中安装好了 `node`， `git` 和 `arco cli`。

其中 `arco cli` 是安装项目模版的工具，请运行以下命令安装：

```bash
npm i -g arco-cli
```

### 创建项目

进入到一个文件夹，新建项目：

```bash
cd someDir
arco init hello-arco-pro
```

选择 技术栈：

```bash
 ? 请选择你希望使用的技术栈
   React
 ❯ Vue
```

选择 `arco-design-pro` 分类：

```bash
 ? 请选择一个分类
   业务组件
   组件库
   Lerna Menorepo 项目
 ❯ Arco Pro 项目
```

等待安装依赖，看到以下输出就是创建成功了

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405082306987.png)

**注意**：安装过程中出现： `arco-init  项目初始化失败！Error: spawnSync pnpm.cmd ENOENT` 说明未安装pnpm：

![image-20240207185521358](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405082306210.png)

安装pnpm：

```
npm install pnpm -g 
```

### 开发

项目创建完成后：

![image-20240207190031153](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405082306551.png)

进入到项目中，运行代码

```lang
cd hello-arco-pro

npm run dev
```

![image-20240207190211102](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405082306103.png)

打开 http://localhost:5174 就能看到如下页面：

![image-20240207190236041](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405082306666.png)