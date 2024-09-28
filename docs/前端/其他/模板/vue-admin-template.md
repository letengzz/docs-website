# vue-admin-template

vue-admin-template是基于vue-element-admin的一套后台管理系统基础模板（最少精简版），可作为模板进行二次开发。

**GitHub地址：**https://github.com/PanJiaChen/vue-admin-template

**建议：**可以在 `vue-admin-template` 的基础上进行二次开发，把 [`vue-element-admin`](vue-element-admin.md)当做工具箱，想要什么功能或者组件就去 [`vue-element-admin`](vue-element-admin.md) 那里复制过来。

**安装**：

```shell
# 安装依赖
npm install
# 启动。执行后，浏览器自动弹出并访问http://localhost:9528/
npm run dev
```

**源码目录结构**：

> |-dist 生产环境打包生成的打包项目
> |-mock 产生模拟数据
> |-public 包含会被自动打包到项目根路径的文件夹
> 	|-index.html 唯一的页面
> |-src
> 	|-api 包含接口请求函数模块
> 		|-table.js  表格列表mock数据接口的请求函数
> 		|-user.js  用户登陆相关mock数据接口的请求函数
> 	|-assets 组件中需要使用的公用资源
> 		|-404_images 404页面的图片
> 	|-components 非路由组件
> 		|-SvgIcon svg图标组件
> 		|-Breadcrumb 面包屑组件(头部水平方向的层级组件)
> 		|-Hamburger 用来点击切换左侧菜单导航的图标组件
> 	|-icons
> 		|-svg 包含一些svg图片文件
> 		|-index.js 全局注册SvgIcon组件,加载所有svg图片并暴露所有svg文件名的数组
> 	|-layout
> 		|-components 组成整体布局的一些子组件
> 		|-mixin 组件中可复用的代码
> 		|-index.vue 后台管理的整体界面布局组件
> 	|-router
> 		|-index.js 路由器
> 	|-store
> 		|-modules
> 			|-app.js 管理应用相关数据
> 			|-settings.js 管理设置相关数据
> 			|-user.js 管理后台登陆用户相关数据
> 		|-getters.js 提供子模块相关数据的getters计算属性
> 		|-index.js vuex的store
> 	|-styles
> 		|-xxx.scss 项目组件需要使用的一些样式(使用scss)
> 	|-utils 一些工具函数
> 		|-auth.js 操作登陆用户的token cookie
> 		|-get-page-title.js 得到要显示的网页title
> 		|-request.js axios二次封装的模块
> 		|-validate.js 检验相关工具函数
> 		|-index.js 日期和请求参数处理相关工具函数
> 	|-views 路由组件文件夹
> 		|-dashboard 首页
> 		|-login 登陆
> 	|-App.vue 应用根组件
> 	|-main.js 入口js
> 	|-permission.js 使用全局守卫实现路由权限控制的模块
> 	|-settings.js 包含应用设置信息的模块
> |-.env.development 指定了开发环境的代理服务器前缀路径
> |-.env.production 指定了生产环境的代理服务器前缀路径
> |-.eslintignore eslint的忽略配置
> |-.eslintrc.js eslint的检查配置
> |-.gitignore git的忽略配置
> |-.npmrc 指定npm的淘宝镜像和sass的下载地址
> |-babel.config.js babel的配置
> |-jsconfig.json 用于vscode引入路径提示的配置
> |-package.json 当前项目包信息
> |-package-lock.json 当前项目依赖的第三方包的精确信息
> |-vue.config.js webpack相关配置(如: 代理服务器)