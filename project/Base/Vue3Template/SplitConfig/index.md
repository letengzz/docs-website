# 拆分配置

在项目中新建config文件夹，用于存放配置。

调整`tsconfig.app.json`：

```json [tsconfig.app.json]
{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "include": ["env.d.ts", "src/**/*", "src/**/*.vue", "config/**/*.ts"], // [!code focus] [!code highlight]
  "exclude": ["src/**/__tests__/*"],
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "module": "ESNext",
    "target": "ES2020",
    "moduleResolution": "Bundler",
    "allowImportingTsExtensions": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## 插件拆分

在config文件夹中新建plugins文件夹，用于存放插件。

新建index.ts，用于插件的入口：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = [] 
  plugins.push(vue(), vueJsx())
  return plugins
}
export default usePlugins
```

调整`vite.config.ts`配置文件：

```typescript [vite.config.ts]
// ...
import useVitePlugins from './config/plugins' // [!code focus] [!code ++]

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // ...
  return {
    // vite 配置
    // ...
    plugins: useVitePlugins(mode), // [!code focus] [!code ++]
    // ...
  }
})
```

### 拆分DevTools

在config/plugins中新建`devTools.ts`：

```typescript
import VueDevTools from 'vite-plugin-vue-devtools'
/**
 *  开启DevTools
 */
const useDevTools = () => {
  return VueDevTools({
    componentInspector: {
      // 如果是windows 'control-shift' , 如果是macOS 'meta-shift'
      toggleComboKey: 'control-shift',
    },
  })
}

export default useDevTools
```

调整`config/plugins/index.ts`，将DevTools根据环境来配置：

```typescript
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = [] 
  plugins.push(vue(), vueJsx())
  if (isDev) {  // [!code focus] [!code ++]
    plugins.push(useDevTools())  // [!code focus] [!code ++]
  }  // [!code focus] [!code ++]
  return plugins
}
export default usePlugins
```

### 拆分自动路由

在config/plugins中新建`autoRouter.ts`：

```typescript
import VueRouter from 'unplugin-vue-router/vite'

/**
 *  自动路由
 */
const useAutoRouter = () => {
  return VueRouter({
    // routesFolder: [
    //   {
    //     src: 'src/views',
    //   },
    // ],
    dts: './types/typed-router.d.ts',
  })
}

export default useAutoRouter
```

调整`config/plugins/index.ts`：

```typescript
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter())  // [!code focus] [!code ++]
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }

  return plugins
}
export default usePlugins
```

### 拆分全局布局

在config/plugins中新建`layout.ts`：

```typescript
import Layouts from 'vite-plugin-vue-layouts'
/**
 *  全局布局
 */
const useLayout = () => {
  return Layouts({
    layoutsDirs: 'src/layouts',
    defaultLayout: 'default',
  })
}

export default useLayout
```

调整`config/plugins/index.ts`：

```typescript
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter' // [!code focus] [!code ++]
import useLayout from './layout' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())  // [!code focus] [!code ++]
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }

  return plugins
}
export default usePlugins
```

### 拆分gzip压缩

在config/plugins中新建`compress.ts`：

```typescript [plugins/compress.ts]
import { compression } from 'vite-plugin-compression2'
/**
 *  开启gzip压缩
 */
const useCompress = () => {
  return compression({
    algorithms: ['gzip'],
    threshold: 10240, // 超过 10KB 的文件才压缩
    deleteOriginalAssets: false, // 不删除原文件
  })
}

export default useCompress
```

在`.env.production`中添加是否压缩：

```properties [.env.production]
# 部署线上 压缩gzip
VITE_BUILD_GZIP = true
```

调整`config/plugins/index.ts`，将压缩根据环境来配置：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter'
import useLayout from './layout'
import useCompress from './compress' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string, env: Record<string, string>) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }
  if (Env.getBoolean('VITE_BUILD_GZIP')) {  // [!code focus] [!code ++]
    plugins.push(useCompress())  // [!code focus] [!code ++]
  }  // [!code focus] [!code ++]

  return plugins
}
export default usePlugins
```

### 拆分自动导入

在config/plugins中新建`autoImport.ts`：

```typescript [config/plugins/autoImport.ts]
// 此插件用于自动导入API和组件
// 可以减少手动import语句，提高开发效率，并提供类型提示
import AutoImport from 'unplugin-auto-import/vite'
import { VueRouterAutoImports } from 'unplugin-vue-router'
/**
 * 配置自动导入功能
 * 支持Vue、Vue Router、Pinia等框架API的自动导入
 * 支持UI组件的自动导入
 * 自动导入src/api和src/utils目录下的函数
 * @returns Vite插件配置
 */
const useAutoImport = () => {
  return AutoImport({
    include: [
      /\.[tj]sx?$/, // .ts, .tsx, .js, .jsx
      /\.vue$/,
      /\.vue\?vue/, // .vue
      /\.md$/, // .md
    ],
    resolvers: [],
    imports: ['vue', 'pinia', VueRouterAutoImports, '@vueuse/core', 'vue-i18n'],
    dts: './types/auto-imports.d.ts',
    dirs: ['src/api/backend/**/*.ts', 'src/utils/**/*.ts'], // 自动导入项目中自定义的API和工具函数
    // eslint 报错解决：'ref' is not defined
    // eslintrc: {
    //   // 默认 false, true 启用生成。生成一次就可以，避免每次工程启动都生成，一旦生成配置文件之后，最好把 enable 关掉，即改成 false。
    //   enabled: true,
    //   // 否则这个文件每次会在重新加载的时候重新生成，这会导致 eslint 有时会找不到这个文件。当需要更新配置文件的时候，再重新打开
    //   filepath: './.eslintrc-auto-import.json' // 默认就是 ./.eslintrc-auto-import.json
    //   // globalsPropValue: true // 默认 true
    // },
  })
}

export default useAutoImport
```

调整`config/plugins/index.ts`，配置自动导入：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter'
import useLayout from './layout'
import useCompress from './compress'
import useAutoImport from './autoImport' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string, env: Record<string, string>) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }
  if (Env.getBoolean('VITE_BUILD_GZIP')) {
    plugins.push(useCompress())
  }
  plugins.push(useAutoImport()) // [!code focus] [!code ++]
  return plugins
}
export default usePlugins
```

### 拆分自动引入组件

在config/plugins中新建`component.ts`：

```typescript
import Components from 'unplugin-vue-components/vite'

/**
 * 自动注册Vue组件的插件配置
 * 该插件可以自动导入组件，无需手动import
 * 提高开发效率并减少样板代码
 */
const useComponents = () => {
  return Components({
    deep: true,
    directoryAsNamespace: false,
    dts: './types/components.d.ts' // 生成组件类型声明文件的路径
  })
}

export default useComponents
```

调整`config/plugins/index.ts`，配置自动导入：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter'
import useLayout from './layout'
import useCompress from './compress'
import useAutoImport from './autoImport'
import useComponents from './component' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string, env: Record<string, string>) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }
  if (Env.getBoolean('VITE_BUILD_GZIP')) {
    plugins.push(useCompress())
  }
  plugins.push(useAutoImport())
  plugins.push(useComponents())  // [!code focus] [!code ++]
  return plugins
}
export default usePlugins
```

### 拆分国际化

在config/plugins中新建`i18n.ts`：

```typescript
import vueI18n from '@intlify/unplugin-vue-i18n/vite'
import path from 'node:path'
/**
 *  自动路由
 */
const useI18n = () => {
  return vueI18n({
    // 语言包目录
    include: path.resolve(__dirname, './src/i18n/locales/**'),
    // 开发模式下也启动编译时处理
    runtimeOnly: false,
    // 仅使用组合式 API
    compositionOnly: true,
    // 完整安装
    fullInstall: true,
  })
}

export default useI18n
```

调整`config/plugins/index.ts`，配置自动导入：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter'
import useLayout from './layout'
import useCompress from './compress'
import useAutoImport from './autoImport'
import useComponents from './component'
import useI18n from './i18n' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string, env: Record<string, string>) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }
  if (Env.getBoolean('VITE_BUILD_GZIP')) {
    plugins.push(useCompress())
  }
  plugins.push(useAutoImport())
  plugins.push(useComponents())
  plugins.push(useI18n()) // [!code focus] [!code ++]
  return plugins
}
export default usePlugins
```

### 拆分兼容性插件

在config/plugins中新建`legacy.ts`：

```typescript
import legacy from '@vitejs/plugin-legacy'
/**
 *  全局布局
 */
const useLegacy = () => {
  return legacy({
    targets: ['defaults', 'not IE 11'],
  })
}

export default useLegacy
```

调整`config/plugins/index.ts`，配置自动导入：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter'
import useLayout from './layout'
import useCompress from './compress'
import useAutoImport from './autoImport'
import useComponents from './component'
import useI18n from './i18n'
import useLegacy from './legacy' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string, env: Record<string, string>) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }
  if (Env.getBoolean('VITE_BUILD_GZIP')) {
    plugins.push(useCompress())
  }
  plugins.push(useAutoImport())
  plugins.push(useComponents())
  plugins.push(useI18n())
  plugins.push(useLegacy()) // [!code focus] [!code ++]
  return plugins
}
export default usePlugins
```

### 拆分图片优化插件

在config/plugins中新建`imageOptimizer.ts`：

```typescript
import { ViteImageOptimizer } from 'vite-plugin-image-optimizer'
/**
 *  全局布局
 */
const useImageOptimizer = () => {
  return ViteImageOptimizer({
    png: {
      quality: 80,
    },
    jpeg: {
      quality: 80,
    },
    webp: {
      quality: 80,
    },
  })
}

export default useImageOptimizer
```

调整`config/plugins/index.ts`，配置自动导入：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter'
import useLayout from './layout'
import useCompress from './compress'
import useAutoImport from './autoImport'
import useComponents from './component'
import useI18n from './i18n'
import useLegacy from './legacy'
import useImageOptimizer from './imageOptimizer' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string, env: Record<string, string>) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }
  if (Env.getBoolean('VITE_BUILD_GZIP')) {
    plugins.push(useCompress())
  }
  plugins.push(useAutoImport())
  plugins.push(useComponents())
  plugins.push(useI18n())
  plugins.push(useLegacy())
  plugins.push(useImageOptimizer()) // [!code focus] [!code ++]
  return plugins
}
export default usePlugins
```

### 拆分构建分析插件

在config/plugins中新建`visualizer.ts`：

```typescript
import visualizer from 'rollup-plugin-visualizer'
/**
 * @description: 代码分析插件，生成可视化报告
 */
const useVisualizer = () => {
  return visualizer({
    filename: 'stats.html',
  })
}

export default useVisualizer
```

调整`config/plugins/index.ts`，配置自动导入：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter'
import useLayout from './layout'
import useCompress from './compress'
import useAutoImport from './autoImport'
import useComponents from './component'
import useI18n from './i18n'
import useLegacy from './legacy'
import useImageOptimizer from './imageOptimizer'
import useVisualizer from './visualizer' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string, env: Record<string, string>) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }
  if (Env.getBoolean('VITE_BUILD_GZIP')) {
    plugins.push(useCompress())
  }
  plugins.push(useAutoImport())
  plugins.push(useComponents())
  plugins.push(useI18n())
  plugins.push(useLegacy())
  plugins.push(useImageOptimizer())
  plugins.push(useVisualizer()) // [!code focus] [!code ++]
  return plugins
}
export default usePlugins
```

### 拆分代码检查插件

在config/plugins中新建`checker.ts`：

```typescript
import checker from 'vite-plugin-checker'
/**
 * @description: 兼容插件，支持旧版浏览器
 */
const useChecker = () => {
  return checker({
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
  })
}

export default useChecker
```

调整`config/plugins/index.ts`，配置自动导入：

```typescript [config/plugins/index.ts]
import type { PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import useDevTools from './devTools'
import useAutoRouter from './autoRouter'
import useLayout from './layout'
import useCompress from './compress'
import useAutoImport from './autoImport'
import useComponents from './component'
import useI18n from './i18n'
import useLegacy from './legacy'
import useImageOptimizer from './imageOptimizer'
import useVisualizer from './visualizer'
import useChecker from './checker' // [!code focus] [!code ++]
/**
 * @description: vite插件列表
 */
const usePlugins = (mode: string, env: Record<string, string>) => {
  const isDev = mode === 'development'
  const plugins: PluginOption[] = []
  plugins.push(useAutoRouter(), useLayout())
  plugins.push(vue(), vueJsx())
  if (isDev) {
    plugins.push(useDevTools())
  }
  if (Env.getBoolean('VITE_BUILD_GZIP')) {
    plugins.push(useCompress())
  }
  plugins.push(useAutoImport())
  plugins.push(useComponents())
  plugins.push(useI18n())
  plugins.push(useLegacy())
  plugins.push(useImageOptimizer())
  plugins.push(useVisualizer())
  plugins.push(useChecker()) // [!code focus] [!code ++]
  return plugins
}
export default usePlugins
```

## 打包拆分

在config中新建`build.ts`：

```typescript [config/build.ts]
const useViteBuild = (viteEnv: Record<string, string>) => {
  const { VITE_BUILD_VENDOR } = viteEnv

  return {
    // 10kb以下，转Base64
    assetsInlineLimit: 1024 * 10,
    // chunkSizeWarningLimit: 1500,//配置文件大小提醒限制，默认500
    rollupOptions: {
      output: {
        // 每个node_modules模块分成一个js文件
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            // return 'vendor'
            return VITE_BUILD_VENDOR
              ? 'vendor'
              : id.toString().split('node_modules/')[2].split('/')[0].toString()
          }
          // return 'vendor'
        },
        // 用于从入口点创建的块的打包输出格式[name]表示文件名,[hash]表示该文件内容hash值
        entryFileNames: 'assets/js/[name].[hash].js', // 用于命名代码拆分时创建的共享块的输出命名
        chunkFileNames: 'assets/js/[name].[hash].js', // 用于输出静态资源的命名，[ext]表示文件扩展名
        assetFileNames: 'assets/[ext]/[name].[hash].[ext]',
      },
    },
  }
}

export default useViteBuild
```

在`.env.production`中添加是否拆分：

```properties [.env.production]
# 生产环境变量

# 网站地址前缀
VITE_BASE_URL = /base/

# 部署线上 第三方库合并为vendor.js
VITE_BUILD_VENDOR = true

# 部署线上 压缩gzip
VITE_BUILD_GZIP = true

# 端口号
VITE_PORT = 5174
```

调整`vite.config.ts`配置文件：

```typescript [vite.config.ts]
// ...
import useViteBuild from './config/build' // [!code focus] [!code ++]

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // ...
  return {
    // vite 配置
    // ...
    build: useViteBuild(env), // [!code focus] [!code ++]
    // ...
  }
})
```

## 预构建拆分

在config中新建`optimizeDeps.ts`：

```typescript [config/optimizeDeps.ts]
import type { DepOptimizationOptions } from 'vite'

/**
 * @description 封装 optimizeDeps 配置
 */
const useOptimizeDeps = (): DepOptimizationOptions => {
  return {
    include: [
      'vue',
      'vue-router',
      'pinia',
      // 'axios',
      // 'echarts',
      // 'vue-i18n'
    ],
  }
}

export default useOptimizeDeps
```

调整`vite.config.ts`配置文件：

```typescript [vite.config.ts]
// ...
import useOptimizeDeps from './config/optimizeDeps' // [!code focus] [!code ++]

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // ...
  return {
    // vite 配置
    // ...
    optimizeDeps: useOptimizeDeps(), // [!code focus] [!code ++]
    // ...
  }
})
```

## 全局变量拆分

在config中新建`define.ts`：

```typescript [config/optimizeDeps.ts]
/**
 * @description: 配置全局变量
 */
const useDefineConfig = (env: Record<string, string>) => ({
  __APP_NAME__: JSON.stringify(env.VITE_APP_TITLE),
  __APP_VERSION__: JSON.stringify(env.VITE_VERSION),
})

export default useDefineConfig
```

调整`vite.config.ts`配置文件：

```typescript [vite.config.ts]
// ...
import useDefineConfig from './config/define' // [!code focus] [!code ++]

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // ...
  return {
    // vite 配置
    // ...
    define: useDefineConfig(env), // [!code focus] [!code ++]
    // ...
  }
})
```

## 配置服务

在config中新建`server.ts`：

```typescript [config/optimizeDeps.ts]
const httpsRE = /^https:\/\//

/**
 * @description 服务器选项
 * @param viteEnv
 * @returns
 */
const useServer = (viteEnv: Record<string, string>) => {
  const apiUrl = viteEnv.VITE_API_URL
  const isHttps = httpsRE.test(apiUrl)
  return {
    // 监听所有公共ip
    host: '0.0.0.0',
    // cors: true,
    hmr: true,
    port: Number(viteEnv.VITE_PORT) || 3000, // 👈 将端口转换为 number，默认 3000
    proxy: {
      '/api': {
        target: apiUrl,
        changeOrigin: true,
        ws: true,
        rewrite: (path: string) => path.replace(/^\/api/, ''),
        ...(isHttps ? { secure: false } : {}),
      },
    },
    // 提前转换和缓存文件以进行预热。可以在服务器启动时提高初始页面加载速度，并防止转换瀑布。
    warmup: {
      // 请注意，只应该预热频繁使用的文件，以免在启动时过载 Vite 开发服务器
      // 可以通过运行 npx vite --debug transform 并检查日志来找到频繁使用的文件
      clientFiles: ['./index.html', './src/{components,api}/*'],
    },
  }
}

export default useServer
```

调整`vite.config.ts`配置文件：

```typescript [vite.config.ts]
// ...
import useServer from './config/server' // [!code focus] [!code ++]

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // ...
  return {
    // vite 配置
    // ...
    server: useServer(env), // [!code focus] [!code ++]
    // ...
  }
})
```

11