# esbuild

esbuild 是一个使用 Go 语言编写的极速 JavaScript 打包器。

- 官网：https://esbuild.github.io/
- GitHub：https://github.com/evanw/esbuild

## esbuild 特点

- **极速构建**：比 Webpack 快 10-100 倍
- **Go 语言编写**：利用 Go 的并发特性
- **开箱即用**：支持 TypeScript、JSX、CSS
- **Tree-shaking**：自动移除未使用代码
- **代码压缩**：内置压缩功能

## 安装 esbuild

### npm 安装

```shell [install.sh]
npm install esbuild --save-dev
```

### 全局安装

```shell [global.sh]
npm install esbuild -g
```

## 基本使用

### 命令行

```shell [cli.sh]
# 基本打包
esbuild src/index.js --bundle --outfile=dist/bundle.js

# 监听模式
esbuild src/index.js --bundle --outfile=dist/bundle.js --watch

# 开发服务器
esbuild src/index.js --bundle --outfile=dist/bundle.js --serve

# 压缩代码
esbuild src/index.js --bundle --outfile=dist/bundle.js --minify
```

### Node.js API

```javascript [api.js]
import * as esbuild from 'esbuild'

await esbuild.build({
  entryPoints: ['src/index.js'],
  bundle: true,
  outfile: 'dist/bundle.js'
})
```

## 构建选项

### 基本选项

```javascript [options.js]
await esbuild.build({
  entryPoints: ['src/index.js'],    // 入口文件
  bundle: true,                     // 是否打包
  outfile: 'dist/bundle.js',        // 输出文件
  outdir: 'dist',                   // 输出目录
  format: 'esm',                    // 输出格式
  platform: 'browser',              // 目标平台
  target: 'es2020',                 // 目标浏览器
  minify: true,                     // 是否压缩
  sourcemap: true,                  // 是否生成 sourcemap
  external: ['lodash'],             // 外部依赖
  loader: {                         // 文件加载器
    '.png': 'dataurl',
    '.svg': 'dataurl'
  }
})
```

### 多入口

```javascript [multi-entry.js]
await esbuild.build({
  entryPoints: {
    main: 'src/index.js',
    vendor: 'src/vendor.js'
  },
  outdir: 'dist',
  bundle: true
})
```

## 开发服务器

### 基本服务器

```shell [serve.sh]
esbuild src/index.js --bundle --outfile=dist/bundle.js --serve=8000
```

### 带代理的服务器

```javascript [serve-proxy.js]
await esbuild.context({
  entryPoints: ['src/index.js'],
  bundle: true,
  outfile: 'dist/bundle.js'
}).then(ctx => {
  ctx.serve({
    port: 3000,
    servedir: 'dist'
  })
})
```

## 插件系统

### 基本插件

```javascript [plugin.js]
import * as esbuild from 'esbuild'

const myPlugin = {
  name: 'my-plugin',
  setup(build) {
    build.onLoad({ filter: /\.txt$/ }, (args) => {
      const fs = require('fs')
      const text = fs.readFileSync(args.path, 'utf8')
      return {
        contents: `export default ${JSON.stringify(text)}`,
        loader: 'js'
      }
    })
  }
}

await esbuild.build({
  entryPoints: ['src/index.js'],
  bundle: true,
  outfile: 'dist/bundle.js',
  plugins: [myPlugin]
})
```

### 转换插件

```javascript [transform.js]
const transformPlugin = {
  name: 'transform',
  setup(build) {
    build.onLoad({ filter: /\.md$/ }, async (args) => {
      const fs = require('fs')
      const markdown = fs.readFileSync(args.path, 'utf8')
      const html = markdownToHtml(markdown)
      return {
        contents: `export default ${JSON.stringify(html)}`,
        loader: 'js'
      }
    })
  }
}
```

## TypeScript 支持

esbuild 原生支持 TypeScript，无需额外配置。

```shell [ts.sh]
esbuild src/index.ts --bundle --outfile=dist/bundle.js
```

## JSX/TSX 支持

### React

```javascript [react.js]
await esbuild.build({
  entryPoints: ['src/index.jsx'],
  bundle: true,
  outfile: 'dist/bundle.js',
  loader: { '.jsx': 'jsx' },
  jsxFactory: 'React.createElement',
  jsxFragment: 'React.Fragment'
})
```

### Preact

```javascript [preact.js]
await esbuild.build({
  entryPoints: ['src/index.jsx'],
  bundle: true,
  outfile: 'dist/bundle.js',
  loader: { '.jsx': 'jsx' },
  jsxFactory: 'h',
  jsxFragment: 'Fragment'
})
```

## CSS 支持

### 基本 CSS

```shell [css.sh]
esbuild src/style.css --bundle --outfile=dist/style.css
```

### CSS 压缩

```shell [css-minify.sh]
esbuild src/style.css --bundle --outfile=dist/style.css --minify
```

## 代码分割

```javascript [splitting.js]
await esbuild.build({
  entryPoints: ['src/index.js', 'src/other.js'],
  bundle: true,
  outdir: 'dist',
  splitting: true,
  format: 'esm'
})
```

## 完整配置示例

```javascript [full-config.js]
import * as esbuild from 'esbuild'

const isDev = process.env.NODE_ENV === 'development'

const buildOptions = {
  entryPoints: ['src/index.ts'],
  bundle: true,
  outfile: 'dist/bundle.js',
  platform: 'browser',
  target: 'es2020',
  minify: !isDev,
  sourcemap: isDev,
  loader: {
    '.png': 'dataurl',
    '.jpg': 'dataurl',
    '.svg': 'dataurl',
    '.css': 'css'
  },
  define: {
    'process.env.NODE_ENV': isDev ? '"development"' : '"production"'
  }
}

if (isDev) {
  const ctx = await esbuild.context(buildOptions)
  await ctx.watch()
  await ctx.serve({
    port: 3000,
    servedir: 'dist'
  })
} else {
  await esbuild.build(buildOptions)
}
```

## 性能对比

| 工具 | 构建时间 | 说明 |
|------|---------|------|
| esbuild | 0.5s | 极速 |
| Vite | 1s | 基于 esbuild |
| Webpack | 10s | 功能强大 |
| Rollup | 5s | 适合库 |

## esbuild 在 Vite 中的应用

Vite 使用 esbuild 进行：

- TypeScript 转换
- JSX/TSX 转换
- 代码压缩

```javascript [vite-esbuild.js]
// vite.config.js
export default {
  esbuild: {
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
    drop: ['console', 'debugger']
  }
}
```

## 常用命令

```shell [commands.sh]
# 打包
esbuild src/index.js --bundle --outfile=dist/bundle.js

# 监听
esbuild src/index.js --bundle --outfile=dist/bundle.js --watch

# 压缩
esbuild src/index.js --bundle --outfile=dist/bundle.js --minify

# 生成 sourcemap
esbuild src/index.js --bundle --outfile=dist/bundle.js --sourcemap

# 外部依赖
esbuild src/index.js --bundle --outfile=dist/bundle.js --external:lodash

# 定义常量
esbuild src/index.js --bundle --outfile=dist/bundle.js --define:VERSION=1.0.0
```

::: tip 提示
- esbuild 构建速度极快
- 适合需要快速构建的场景
- Vite 底层使用 esbuild
- 库开发可考虑直接使用 esbuild
:::
