# vue-admin-template

vue-admin-template是基于vue-element-admin的一套后台管理系统基础模板（最少精简版），可作为模板进行二次开发。

**GitHub地址**：https://github.com/PanJiaChen/vue-admin-template

**建议**：可以在 `vue-admin-template` 的基础上进行二次开发，把 [`vue-element-admin`](vue-element-admin.md)当做工具箱，想要什么功能或者组件就去 [`vue-element-admin`](vue-element-admin.md) 那里复制过来。

**安装**：

```shell
# 安装依赖
npm install
# 启动。执行后，浏览器自动弹出并访问http://localhost:9528/
npm run dev
```

**源码目录结构**：

> |-dist 生产环境打包生成的打包项目 <br/>
> |-mock 产生模拟数据 <br/>
> |-public 包含会被自动打包到项目根路径的文件夹 <br/>	|-index.html 唯一的页面 <br/>
> |-src <br/>
> &nbsp;&nbsp;|-api 包含接口请求函数模块 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-table.js  表格列表mock数据接口的请求函数 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-user.js  用户登陆相关mock数据接口的请求函数 <br/>
> &nbsp;&nbsp;|-assets 组件中需要使用的公用资源 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-404_images 404页面的图片 <br/>
> &nbsp;&nbsp;|-components 非路由组件 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-SvgIcon svg图标组件 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-Breadcrumb 面包屑组件(头部水平方向的层级组件) <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-Hamburger 用来点击切换左侧菜单导航的图标组件 <br/>
> &nbsp;&nbsp;|-icons <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-svg 包含一些svg图片文件 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-index.js 全局注册SvgIcon组件,加载所有svg图片并暴露所有svg文件名的数组 <br/>
> &nbsp;&nbsp;|-layout <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-components 组成整体布局的一些子组件 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-mixin 组件中可复用的代码 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-index.vue 后台管理的整体界面布局组件 <br/>
> &nbsp;&nbsp;|-router <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-index.js 路由器 <br/>
> &nbsp;&nbsp;|-store <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-modules <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-app.js 管理应用相关数据 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-settings.js 管理设置相关数据 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-user.js 管理后台登陆用户相关数据 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-getters.js 提供子模块相关数据的getters计算属性 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-index.js vuex的store <br/>
> &nbsp;&nbsp;|-styles <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-xxx.scss 项目组件需要使用的一些样式(使用scss) <br/>
> &nbsp;&nbsp;|-utils 一些工具函数 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-auth.js 操作登陆用户的token cookie <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-get-page-title.js 得到要显示的网页title <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-request.js axios二次封装的模块 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-validate.js 检验相关工具函数 <br/>
> &nbsp;&nbsp;|-index.js 日期和请求参数处理相关工具函数 <br/>
> &nbsp;&nbsp;|-views 路由组件文件夹 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-dashboard 首页 <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;|-login 登陆 <br/>
> &nbsp;&nbsp;|-App.vue 应用根组件 <br/>
> &nbsp;&nbsp;|-main.js 入口js <br/>
> &nbsp;&nbsp;|-permission.js 使用全局守卫实现路由权限控制的模块 <br/>
> &nbsp;&nbsp;|-settings.js 包含应用设置信息的模块 <br/>
> |-.env.development 指定了开发环境的代理服务器前缀路径 <br/>
> |-.env.production 指定了生产环境的代理服务器前缀路径 <br/>
> |-.eslintignore eslint的忽略配置 <br/>
> |-.eslintrc.js eslint的检查配置 <br/>
> |-.gitignore git的忽略配置 <br/>
> |-.npmrc 指定npm的淘宝镜像和sass的下载地址 <br/>
> |-babel.config.js babel的配置 <br/>
> |-jsconfig.json 用于vscode引入路径提示的配置 <br/>
> |-package.json 当前项目包信息 <br/>
> |-package-lock.json 当前项目依赖的第三方包的精确信息 <br/>
> |-vue.config.js webpack相关配置(如: 代理服务器) <br/>