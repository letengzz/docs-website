# Webpack

Webpack 是一个现代 JavaScript 应用程序的静态模块打包器。

- 官网：https://webpack.js.org/
- 中文文档：https://webpack.docschina.org/

## Webpack 核心概念

### 入口（Entry）

指定 Webpack 从哪个文件开始打包。

```javascript [webpack.config.js]
module.exports = {
  entry: './src/index.js'
}
```

### 出口（Output）

指定打包后的文件输出位置和文件名。

```javascript [output.js]
const path = require('path')

module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  }
}
```

### Loader

用于处理不同类型的文件。

```javascript [loader.js]
module.exports = {
  module: {
    rules: [
      // CSS 处理
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      // TypeScript 处理
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      // 图片处理
      {
        test: /\.(png|jpg|gif)$/,
        type: 'asset/resource'
      }
    ]
  }
}
```

### 插件（Plugin）

扩展 Webpack 的功能。

```javascript [plugin.js]
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')

module.exports = {
  plugins: [
    new HtmlWebpackPlugin({
      template: './index.html'
    }),
    new CleanWebpackPlugin()
  ]
}
```

## 安装 Webpack

```shell [install.sh]
# 安装 webpack 和 webpack-cli
npm install webpack webpack-cli --save-dev
```

## 基本配置

### 开发环境配置

```javascript [webpack.dev.js]
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
  mode: 'development',
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  devServer: {
    port: 3000,
    hot: true,
    open: true
  },
  devtool: 'eval-source-map',
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './index.html'
    })
  ]
}
```

### 生产环境配置

```javascript [webpack.prod.js]
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin')
const TerserPlugin = require('terser-webpack-plugin')

module.exports = {
  mode: 'production',
  entry: './src/index.js',
  output: {
    filename: 'bundle.[contenthash].js',
    path: path.resolve(__dirname, 'dist'),
    clean: true
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './index.html'
    }),
    new CleanWebpackPlugin()
  ],
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin(),
      new CssMinimizerPlugin()
    ],
    splitChunks: {
      chunks: 'all'
    }
  }
}
```

## 开发服务器

### 安装

```shell [dev-server.sh]
npm install webpack-dev-server --save-dev
```

### 配置

```javascript [dev-server.js]
module.exports = {
  devServer: {
    port: 3000,        // 端口
    hot: true,         // 热更新
    open: true,        // 自动打开浏览器
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
}
```

## 代码分割

### 入口分割

```javascript [split-entry.js]
module.exports = {
  entry: {
    main: './src/index.js',
    vendor: './src/vendor.js'
  },
  output: {
    filename: '[name].[contenthash].js'
  }
}
```

### 动态导入

```javascript [dynamic-import.js]
// 按需加载模块
import('./module').then(module => {
  module.default()
})
```

### SplitChunks

```javascript [split-chunks.js]
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    }
  }
}
```

## 常用 Loader

### babel-loader

```javascript [babel.js]
module.exports = {
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  }
}
```

### css-loader

```javascript [css.js]
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  }
}
```

### file-loader

```javascript [file.js]
module.exports = {
  module: {
    rules: [
      {
        test: /\.(png|jpg|gif)$/,
        type: 'asset/resource',
        generator: {
          filename: 'images/[name].[hash][ext]'
        }
      }
    ]
  }
}
```

## 常用插件

### HtmlWebpackPlugin

```javascript [html.js]
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
  plugins: [
    new HtmlWebpackPlugin({
      template: './index.html',
      filename: 'index.html',
      minify: {
        removeComments: true,
        collapseWhitespace: true
      }
    })
  ]
}
```

### MiniCssExtractPlugin

```javascript [mini-css.js]
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader']
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css'
    })
  ]
}
```

## 环境变量

```javascript [env.js]
module.exports = (env) => {
  console.log('环境变量:', env)
  
  return {
    mode: env.production ? 'production' : 'development'
  }
}
```

## 完整配置示例

```javascript [full-config.js]
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  entry: './src/index.js',
  output: {
    filename: '[name].[contenthash].js',
    path: path.resolve(__dirname, 'dist'),
    clean: true
  },
  mode: 'development',
  devtool: 'eval-source-map',
  devServer: {
    port: 3000,
    hot: true,
    open: true
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: 'babel-loader'
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.(png|jpg|gif)$/,
        type: 'asset/resource'
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './index.html'
    }),
    new CleanWebpackPlugin()
  ],
  optimization: {
    splitChunks: {
      chunks: 'all'
    }
  }
}
```

::: tip 提示
- Webpack 功能强大但配置复杂
- 大型项目推荐使用 Webpack
- 新项目可考虑使用 Vite
:::
