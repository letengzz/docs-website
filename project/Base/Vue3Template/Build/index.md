# 配置打包构建优化

假设有些配置只在生产环境 prod 生效，如关闭 sourceMap、代码混淆等，在开发 dev 或测试环境 uat 不生效。所以需要定义一个函数来判断是否是指定的环境（这里就假设为生产环境 prod）。

打包构建优化都在 `vite.config.ts`文件中进行，之前为了支持该文件获取环境变量、模式，已经修改为函数。

```typescript [vite.config.ts]
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  // 如果你有其他场景判断，可修改此处，假设只针对生产环境
  const isProd = mode === 'prod'

  return {
    // ...
  }
})
```

## 代码压缩和代码混淆

**代码压缩**就是想办法减小 JavaScript、CSS 和 HTML 文件的体积，从而减少网络传输时间、降低带宽消耗、提高页面加载速度的过程。压缩的是代码的体积 (如移除空白字符、注释、不执行的代码；各种名称替换、折叠常量等等)，不压缩性能。

Vite 可以通过配置 `build.minify`属性来配置代码压缩。该属性支持下列值：

- `'esbuild'`：Vite 4.0+ 的默认压缩工具。压缩速度极快（比 Terser 快 20-40 倍），但压缩率略低于 Terser。如果对构建速度有要求，那默认即可，啥都不配置。
- `'terser'`：这是个超级老牌，压缩效果非常好，支持的压缩选项更多，构建速度较慢，需要安装依赖。适合于对包体积有极致要求的项目。
- `'uglify-js'`：当前 Vite 版本已经不支持，可以不用理会这种太陈旧的玩意儿，被 ESBuild 和 Terser 取代。
- `false`：不代码压缩。

**代码混淆**的目标，就是让别人在浏览器无法看懂或扒拉到代码。

terser 不仅支持压缩，还支持混淆。

安装 Terser 依赖：

```bash
pnpm add terser -D
```

在 vite.config.ts 中配置：除了配置使用 terser 对代码进行压缩和混淆，还配置了生产环境关闭 sourceMap。

```typescript
export default defineConfig(({ mode }) => {
  // ...
  return {
    // ...
    build: {
      minify: 'terser',
      sourcemap: false,
      terserOptions: {
        // 代码压缩配置
        compress: {
          drop_console: true, // 移除 console
          drop_debugger: true, // 移除 debugger
        },
        // 代码混淆配置
        mangle: {
          toplevel: true, // 混淆顶层变量名
          eval: true, // 混淆 eval 中的变量
        },
        // 输出配置
        format: {
          comments: false,
        },
      }
    },
    // ...
  }
})
```

## 资源压缩

除了代码压缩，还可以对构建产物进行 Gzip/Brotli 压缩，进一步减少传输体积。集成 `vite-plugin-compression2`插件可以自动生成压缩文件：`.gz`（Gzip）或`.br`（Brotli），压缩后的文件体积会更小，网络传输更快。

安装依赖：

```text
pnpm add vite-plugin-compression2 -D
```

```typescript
import { compression } from 'vite-plugin-compression2'

export default defineConfig(({ mode }) => {
  // ...
  
  return {
    plugins: [
      // ...
      // Gzip 压缩
      compression({
        algorithms: ['gzip'],
        threshold: 10240, // 超过 10KB 的文件才压缩
        deleteOriginalAssets: false, // 不删除原文件
      }),
    ],
  }
})
```

## 图片优化

可以集成图片优化插件，实现图片的自动压缩和图片格式的转换。

安装依赖：

```text
pnpm add vite-plugin-image-optimizer -D
```

```typescript
import { ViteImageOptimizer } from 'vite-plugin-image-optimizer'

export default defineConfig(({ mode }) => {
  // ...
  return {
    // ...
    plugins: [
      // ...
      ViteImageOptimizer({
        png: {
          quality: 80,
        },
        jpeg: {
          quality: 80,
        },
        webp: {
          quality: 80,
        },
      }),
    ],
    // ...
  }
})
```

## 依赖预构建优化

配置 optimizeDeps 属性，该属性配置依赖项数组。

在开发服务器启动时，Vite 会将配置的依赖项预构建成 ES 模块，避免在开发过程中重复转换模块格式，略微提升开发体验。

```typescript [vite.config.ts]
export default defineConfig(({ mode }) => {
  // ...
  return {
    // ...
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia', '@vueuse/core', 'vue-i18n'],
    },
  }
})
```

## 输出的目录文件配置

规范构建产物目录结构：

```typescript [vite.config.ts]
// vite.config.ts
export default defineConfig({
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    assetsInlineLimit: 4096,
    reportCompressedSize: true,
    // ...
  },
})
```

## css 代码分割

配置 css 代码分割属性 **build.cssCodeSplit**（默认为 true，即开启），将 CSS 代码分割成多个独立的文件，而不是将所有 CSS 都打包到一个大文件中。这样一来，首次访问时只交在当前页面所需的 CSS。

```typescript [vite.config.ts]
export default defineConfig(({ mode }) => {
  // ...
  return {
    // ...
    build: {
      cssCodeSplit: true,
      // ...
    },
  }
})
```

## JS代码分割

通过 **manualChunks** 配置项对 JS 代码进行手动代码分割配置，手动指定如何将代码分割成多个不同的文件：既不将所有 JS 都打包到一个大文件中，也不让 Vite 自动决定分割策略。

官网：https://cn.vitejs.dev/config/build-options.html#build-assetsinlinelimit

```typescript [vite.config.ts]
export default defineConfig(({ mode }) => {
  // ...
  return {
    // ...
    build: {
      // ...
      rollupOptions: {
        output: {
           // vendor 为自定义的文件块名称，可以自己定义，后面的数组为需要打包到这个块中的依赖包。
          //通过这种配置，将 Vue 核心库、路由、状态管理打包到一个独立的文件中，而将应用的业务代码打包到其他独立的文件中，实现业务代码分离。
          // manualChunks: {
          //   vendor: ['vue', 'vue-router', 'pinia'],
          // },
          // 每个node_modules下的文件单独打包
          manualChunks(id: string) {
            if (id.includes('node_modules')) {
              // return 'vendor' //第三方依赖合并在一起
              // 抽离第三方依赖
              // return id.toString().split('node_modules/.pnpm/')[1].split('/')[0].toString()
              return id.toString().split('node_modules/')[1].split('/')[0].toString()
            }
            return undefined
          },
          // 用于从入口点创建的块的打包输出格式[name]表示文件名，[hash]表示该文件hash值
          entryFileNames: 'assets/js/[name].[hash].js', // 用于命名代码拆分时创建的共享的输出命名
          chunkFileNames: 'assets/js/[name].[hash].js', // 用于输出静态资源的命名，[ext]表示文件拓展名
          assetFileNames: 'assets/[ext]/[name].[hash].[ext]',
        },
      },
    },
  }
})
```

##   兼容性处理

可使用 `@vitejs/plugin-legacy`生成兼容旧浏览器的代码，它是 Vite 官方提供的兼容性处理插件，可解决现代前端代码在旧浏览器中运行的问题。

**targets** 配置项指定了要兼容的浏览器目标。默认值为 ['defaults', 'not IE 11']，表示兼容所有现代浏览器和不支持 IE 11 的浏览器 (Vue3 本身就不再支持 IE11)。

'defaults' 表示使用 browserslist 的默认浏览器配置（通常包括主流浏览器的最近几个版本）

首先安装依赖：

```bash
pnpm add @vitejs/plugin-legacy -D
```

```typescript [vite.config.ts]
import legacy from '@vitejs/plugin-legacy'

export default defineConfig(({ mode }) => {
  // ...
  return {
    // ...
    plugins: [
      // ...
      legacy({
        targets: ['defaults', 'not IE 11'],
      }),
    ],
  }
})
```

## 构建分析插件

可集成 `rollup-plugin-visualizer`生成打包分析图。

安装依赖：

```bash
pnpm add rollup-plugin-visualizer -D
```

```typescript [vite.config.ts]
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig(({ mode }) => {
  // ...
  return {
    // ...
    plugins: [
      // ...
      visualizer({
        filename: 'stats.html',
      }),
    ],
  }
})
```

## 代码检查插件

安装：

```[pnpm]
pnpm i vite-plugin-checker -D
```

调整 vite.config.ts：

```typescript [vite.config.ts]
import checker from 'vite-plugin-checker'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    /**
     * vite-plugin-checker 配置
     * 用于在开发环境下进行代码检查
     *
     * @returns {import('vite-plugin-checker').default} checker插件实例
     *
     * 配置说明:
     * - eslint: ESLint配置
     *   - useFlatConfig: 使用扁平配置
     *   - lintCommand: 检查命令
     *   - dev.logLevel: 开发环境日志级别
     * - overlay: 错误覆盖层配置
     *   - initialIsOpen: 初始是否打开
     */
    checker({
      eslint: {
        useFlatConfig: true,
        lintCommand: 'eslint "./src/**/*.{ts,tsx,vue}"',
        dev: {
          logLevel: ['error'],
        },
      },
      overlay: {
        initialIsOpen: true,
      },
    }),
  ],
  // ...
})
```

## 配置全局变量

vite.config.ts配置：

```typescript [vite.config.ts]
// ...

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 根据当前工作目录中的 `mode` 加载 .env 文件
  // 设置第三个参数为 '' 来加载所有环境变量，而不管是否有
  // `VITE_` 前缀。
  const env = loadEnv(mode, process.cwd(), '')

  return {
    // vite 配置
    // ...
    define: {
      __APP_NAME__: JSON.stringify(env.VITE_APP_TITLE), 
      __APP_VERSION__: JSON.stringify(env.VITE_VERSION), 
    }, 
    // ...
  }
})
```

