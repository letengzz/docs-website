# 构建工具概述

前端构建工具是将源代码转换为可在浏览器中运行的代码的工具。

## 什么是构建工具

构建工具主要用于：

- **代码转换**：TypeScript → JavaScript、Sass → CSS、JSX → JS
- **代码压缩**：减小文件体积，提升加载速度
- **代码合并**：减少 HTTP 请求数量
- **资源优化**：图片压缩、CSS 前缀添加
- **模块打包**：将多个模块打包成一个或多个文件
- **开发服务器**：提供热更新、代理等功能

## 构建工具发展史

| 阶段 | 工具 | 特点 |
|------|------|------|
| 早期 | Grunt、Gulp | 基于任务流，配置复杂 |
| 中期 | Webpack | 基于模块打包，功能强大 |
| 现代 | Vite、esbuild | 基于 ESM，极速构建 |

## 主流构建工具对比

### Webpack

- **官网**：https://webpack.js.org/
- **特点**：功能强大、生态完善、配置灵活
- **适用场景**：大型项目、复杂构建需求

```javascript [webpack.config.js]
module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  module: {
    rules: [
      { test: /\.css$/, use: ['style-loader', 'css-loader'] }
    ]
  }
}
```

### Vite

- **官网**：https://vitejs.dev/
- **特点**：极速启动、热更新快、开箱即用
- **适用场景**：现代前端项目、快速开发

```javascript [vite.config.js]
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000
  }
})
```

### Rollup

- **官网**：https://rollupjs.org/
- **特点**：专注于库打包、Tree-shaking 优秀
- **适用场景**：JavaScript 库、工具函数库

```javascript [rollup.config.js]
export default {
  input: 'src/index.js',
  output: {
    file: 'dist/bundle.js',
    format: 'es'
  }
}
```

### esbuild

- **官网**：https://esbuild.github.io/
- **特点**：Go 语言编写、构建速度极快
- **适用场景**：需要极速构建的场景

```javascript [esbuild.js]
import * as esbuild from 'esbuild'

await esbuild.build({
  entryPoints: ['src/index.js'],
  bundle: true,
  outfile: 'dist/bundle.js'
})
```

## 构建工具核心概念

### 入口（Entry）

构建的起点，指定从哪个文件开始打包。

```javascript
entry: './src/index.js'
```

### 出口（Output）

打包后的文件输出位置和文件名。

```javascript
output: {
  filename: 'bundle.js',
  path: path.resolve(__dirname, 'dist')
}
```

### Loader

用于处理不同类型的文件。

```javascript
module: {
  rules: [
    { test: /\.css$/, use: ['style-loader', 'css-loader'] },
    { test: /\.ts$/, use: 'ts-loader' }
  ]
}
```

### Plugin

扩展构建工具的功能。

```javascript
plugins: [
  new HtmlWebpackPlugin({ template: './index.html' }),
  new CleanWebpackPlugin()
]
```

### 模式（Mode）

指定构建环境，影响默认配置。

```javascript
mode: 'development' // 或 'production'
```

## 选择构建工具

| 项目类型 | 推荐工具 | 原因 |
|---------|---------|------|
| 大型应用 | Webpack | 生态完善、功能强大 |
| 现代前端 | Vite | 开发体验好、速度快 |
| 工具库 | Rollup | 打包体积小、Tree-shaking |
| 极速构建 | esbuild | 构建速度最快 |

::: tip 提示
- 新项目推荐使用 Vite
- 老项目继续使用 Webpack
- 库开发使用 Rollup
- 追求速度使用 esbuild
:::
