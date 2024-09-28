# Vue 插件

安装官方推荐的`vscode`插件：

<img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202407102112938.png" alt="Snipaste_2023-10-08_20-46-34" style="zoom:50%;" /> 

<img src="https://cdn.jsdelivr.net/gh/letengzz/tc2/img202407102113744.png" alt="image-20231218085906380" style="zoom:42%;" /> 

总结：

- `Vite` 项目中，`index.html` 是项目的入口文件，在项目最外层。
- 加载`index.html`后，`Vite` 解析 `<script type="module" src="xxx">` 指向的`JavaScript`。
- `Vue3`**中是通过 **`createApp` 函数创建一个应用实例。