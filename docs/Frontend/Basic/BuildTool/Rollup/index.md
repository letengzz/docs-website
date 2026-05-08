# Rollup

Rollup 是一个 JavaScript 模块打包器，专注于打包 JavaScript 库。

- 官网：https://rollupjs.org/
- 中文文档：https://rollupjs.org/

## Rollup 特点

- **Tree-shaking**：自动移除未使用的代码
- **ESM 优先**：原生支持 ES 模块
- **输出格式多样**：支持 ESM、CommonJS、UMD、IIFE
- **适合库开发**：打包体积小、代码优化好

## 安装 Rollup

```shell [install.sh]
npm install rollup --save-dev
```

## 基本使用

### 命令行

```shell [cli.sh]
# 基本打包
rollup src/index.js -o dist/bundle.js -f es

# 监听模式
rollup src/index.js -o dist/bundle.js -f es -w

# 使用配置文件
rollup -c
```

### 配置文件

```javascript [rollup.config.js]
export default {
  input: 'src/index.js',
  output: {
    file: 'dist/bundle.js',
    format: 'es'
  }
}
```

## 输出格式

### ESM（ES 模块）

```javascript [esm.js]
export default {
  input: 'src/index.js',
  output: {
    file: 'dist/bundle.esm.js',
    format: 'es'
  }
}
```

### CommonJS

```javascript [cjs.js]
export default {
  input: 'src/index.js',
  output: {
    file: 'dist/bundle.cjs.js',
    format: 'cjs'
  }
}
```

### UMD

```javascript [umd.js]
export default {
  input: 'src/index.js',
  output: {
    file: 'dist/bundle.umd.js',
    format: 'umd',
    name: 'MyLibrary'
  }
}
```

### IIFE

```javascript [iife.js]
export default {
  input: 'src/index.js',
  output: {
    file: 'dist/bundle.iife.js',
    format: 'iife',
    name: 'MyLibrary'
  }
}
```

## 多格式输出

```javascript [multi-output.js]
export default {
  input: 'src/index.js',
  output: [
    {
      file: 'dist/bundle.esm.js',
      format: 'es'
    },
    {
      file: 'dist/bundle.cjs.js',
      format: 'cjs'
    },
    {
      file: 'dist/bundle.umd.js',
      format: 'umd',
      name: 'MyLibrary'
    }
  ]
}
```

## 常用插件

### @rollup/plugin-node-resolve

解析 node_modules 中的依赖。

```shell [install-resolve.sh]
npm install @rollup/plugin-node-resolve --save-dev
```

```javascript [resolve.js]
import resolve from '@rollup/plugin-node-resolve'

export default {
  input: 'src/index.js',
  plugins: [
    resolve()
  ]
}
```

### @rollup/plugin-commonjs

将 CommonJS 模块转换为 ES 模块。

```shell [install-commonjs.sh]
npm install @rollup/plugin-commonjs --save-dev
```

```javascript [commonjs.js]
import commonjs from '@rollup/plugin-commonjs'

export default {
  input: 'src/index.js',
  plugins: [
    commonjs()
  ]
}
```

### @rollup/plugin-babel

使用 Babel 转换代码。

```shell [install-babel.sh]
npm install @rollup/plugin-babel @babel/core @babel/preset-env --save-dev
```

```javascript [babel.js]
import babel from '@rollup/plugin-babel'

export default {
  input: 'src/index.js',
  plugins: [
    babel({
      babelHelpers: 'bundled',
      presets: ['@babel/preset-env']
    })
  ]
}
```

### @rollup/plugin-terser

压缩代码。

```shell [install-terser.sh]
npm install @rollup/plugin-terser --save-dev
```

```javascript [terser.js]
import terser from '@rollup/plugin-terser'

export default {
  input: 'src/index.js',
  plugins: [
    terser()
  ]
}
```

### rollup-plugin-typescript2

支持 TypeScript。

```shell [install-ts.sh]
npm install rollup-plugin-typescript2 typescript --save-dev
```

```javascript [typescript.js]
import typescript from 'rollup-plugin-typescript2'

export default {
  input: 'src/index.ts',
  plugins: [
    typescript()
  ]
}
```

## 外部依赖

```javascript [external.js]
export default {
  input: 'src/index.js',
  external: ['lodash', 'axios'],
  output: {
    file: 'dist/bundle.js',
    format: 'es'
  }
}
```

## Tree-shaking

Rollup 默认启用 Tree-shaking，自动移除未使用的代码。

```javascript [tree-shaking.js]
// src/utils.js
export function add(a, b) {
  return a + b
}

export function subtract(a, b) {
  return a - b
}

// src/index.js
import { add } from './utils.js'

console.log(add(1, 2))

// 打包后 subtract 函数会被移除
```

## 完整配置示例

```javascript [full-config.js]
import resolve from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'
import babel from '@rollup/plugin-babel'
import terser from '@rollup/plugin-terser'
import typescript from 'rollup-plugin-typescript2'

export default {
  input: 'src/index.ts',
  output: [
    {
      file: 'dist/bundle.esm.js',
      format: 'es'
    },
    {
      file: 'dist/bundle.cjs.js',
      format: 'cjs'
    },
    {
      file: 'dist/bundle.umd.js',
      format: 'umd',
      name: 'MyLibrary',
      globals: {
        lodash: '_'
      }
    }
  ],
  external: ['lodash'],
  plugins: [
    resolve(),
    commonjs(),
    typescript(),
    babel({
      babelHelpers: 'bundled',
      presets: ['@babel/preset-env']
    }),
    terser()
  ]
}
```

## package.json 配置

```json [package.json]
{
  "name": "my-library",
  "version": "1.0.0",
  "main": "dist/bundle.cjs.js",
  "module": "dist/bundle.esm.js",
  "browser": "dist/bundle.umd.js",
  "scripts": {
    "build": "rollup -c",
    "dev": "rollup -c -w"
  }
}
```

## Rollup vs Webpack

| 特性 | Rollup | Webpack |
|------|--------|---------|
| 定位 | 库打包 | 应用打包 |
| Tree-shaking | 优秀 | 良好 |
| 代码分割 | 支持 | 优秀 |
| 热更新 | 不支持 | 支持 |
| 配置复杂度 | 简单 | 复杂 |
| 生态 | 较小 | 完善 |

::: tip 提示
- Rollup 适合打包 JavaScript 库
- 需要多格式输出时使用 Rollup
- 应用开发推荐使用 Webpack 或 Vite
:::
