# Element-ui

饿了么团队开发并开源的基于Vue的前端组件库，它可以做出非常整齐美观的页面效果，特别是在一些后台管理系统中应用广泛；像我们项目开发中，需要使用到一些页面的效果 (表单、输入框、表格、按钮、布局、图标等等)，都可以采用element-plus提供的组件。

- Element-UI (基于Vue2.x)：https://element.eleme.cn/
- Element-Plus (基于Vue3.x)：http://element-plus.gitee.io/

## 使用

- `--save`：表示将安装包信息写入package.json的dependencies中，在dependencies中，那么项目打包就会依赖到该模块
- `--save-dev`：表示项目打包时不需要依赖该模块，它会将安装包信息写入devDependencies下，表示项目开发时需要依赖该模块，项目打包发布则不需要依赖该模块；

```shell
npm install element-plus --save
```

### 全局引入

使用element-plus在main.js中：

```javascript
//引入ElementPlus
import ElementPlus from 'element-plus'
//引入样式
import 'element-plus/dist/index.css'
//使用ElementPlus
app.use(ElementPlus)
```

