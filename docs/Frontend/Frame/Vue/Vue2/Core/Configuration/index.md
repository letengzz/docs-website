# vue.config.js 配置

`vue.config.js` 是 Vue CLI 项目中的配置文件，它允许开发者自定义配置。以下是一些常用的配置项及其说明：

1. **publicPath**：定义应用的根目录，通常用于部署到非根目录的单页面应用。

   ```javascript
   module.exports = {
     publicPath：process.env.NODE_ENV === "production" ? "/app/" ："/",
   };
   ```

2. **outputDir**：指定编译输出的目录。

   ```javascript
   module.exports = {
     outputDir："dist",
   };
   ```

3. **assetsDir**：指定静态资源的目录。

   ```javascript
   module.exports = {
     assetsDir："static",
   };
   ```

4. **runtimeCompiler**：为 Vue 应用程序启用运行时编译器，这对于使用 Vue 的 `template` 选项的自定义块是必需的。

   ```javascript
   module.exports = {
     runtimeCompiler：true,
   };
   ```

5. **transpileDependencies**：指定需要进行 Babel 转译的依赖。

   ```javascript
   module.exports = {
     transpileDependencies：[
       // 包含所有依赖的路径
       path.resolve(__dirname, "node_modules/some-package"),
     ],
   };
   ```

6. **devServer**：配置开发服务器。

   ```javascript
    productionSourceMap：fasle, //生产环境是否要生成 sourceMap
    devServer：{
        open：true, // 自动打开浏览器
        host：'localhost',
        port：8080,
        https：false,
        // 配置跨域请求头，解决开发环境的跨域问题
        headers：{
            'Access-Control-Allow-Origin'：'*',
        },
        // 代理设置
        proxy：{
            '/api'：{
                target：'http://backend.server.com',
                changeOrigin：true,
                pathRewrite：{
                    "^/api"：""
                }
            }
        }
    } 
   ```

7. **css**：配置 CSS 相关选项。

   ```javascript
   module.exports = {
     css：{
       // 启用 CSS modules
       modules：{
         localIdentName："[name]-[hash]",
       },
       // 扩展名
       requireModuleExtension：false,
     },
   };
   ```

8. **lintOnSave**：是否在开发环境中对 .js, .vue, .ts 文件进行 ESLint 检查。

   ```javascript
   module.exports = {
     lintOnSave：true,
   };
   ```

9. **chainWebpack**：使用 webpack-chain 来修改 webpack 配置。chainWebpack 是链式操作

   ```javascript
   module.exports = {
     chainWebpack：(config) => {
       // 修改 webpack 配置
       // 例如，通过判断运行环境，设置mode
       config.mode = 'production'
       config.module.rule(name).use(name).loader(loader).options(options)
     },
   };
   ```

10. **configureWebpack**：用于添加或修改 webpack 配置。它可以是一个对象：和 webpack 本身配置方式是一致，该对象将会被 webpack-merge 合并入最终的 webpack 配置

    ```javascript
    module.exports = {
      configureWebpack：{
        // webpack 配置
        rules:[],
        plugins：[],
        // 设置别名路径
        resolve：{
          alias：{
            "@"：path.resolve(__dirname, "src"),
          },
        },
        output：{
          // 应用的包名
          library："sub-wechat",
          // 将你的 library 暴露为所有的模块定义下都可运行的方式
          libraryTarget："umd",
          // 按需加载相关，设置为 webpackJsonp_VueApp 即可
          jsonpFunction：`webpackJsonp_sub-wechat`,
        },
      },
    };
    ```

11. **parallel**：是否使用 webpack 的多线程编译。

    ```javascript
    module.exports = {
      parallel：require("os").cpus().length > 1,
    };
    ```

12. **pwa**：配置 PWA 插件。

    ```javascript
    module.exports = {
      pwa：{
        workboxPluginMode："GenerateSW",
        workboxOptions：{
          // Workbox 配置
        },
      },
    };
    ```

13. **pluginOptions**：配置插件选项。

    ```javascript
    module.exports = {
      pluginOptions：{
        // 插件配置
      },
    };
    ```

这些配置项提供了对 Vue CLI 项目构建过程的精细控制，使得开发者可以根据项目需求进行自定义配置。需要注意的是，`vue.config.js` 中的配置可能会根据 Vue CLI 的版本有所不同。
