# UmiJS 配置指南

UmiJS 提供了丰富的配置项，可以通过 `.umirc.ts` 或 `config/config.ts` 文件进行配置。本指南将详细介绍常用的配置项。

::: tip UmiJS 4.x 配置变化
UmiJS 4.x 支持 Vite 和 Webpack 双构建引擎，大部分配置项在两种构建方式下保持一致。使用 `vite: {}` 或 `webpack: {}` 可以配置特定构建引擎。
:::

## 配置文件

### 配置文件位置

UmiJS 支持两种配置文件方式（二选一）：

- `.umirc.ts`：项目根目录
- `config/config.ts`：config 目录下

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 配置项
})
```

### 环境变量

可以在配置中使用环境变量：

```typescript
import { defineConfig } from 'umi'

export default defineConfig({
  // 根据环境切换配置
  proxy: process.env.NODE_ENV === 'development' ? {
    '/api': {
      target: 'http://localhost:3000',
      changeOrigin: true,
    },
  } : undefined,
})
```

::: tip 环境变量文件
UmiJS 支持 `.env`、`.env.local`、`.env.development`、`.env.production` 等环境变量文件。
:::

## 基础配置

### npmClient

指定使用的包管理器：

```typescript
export default {
  npmClient: 'npm', // npm | yarn | pnpm
}
```

### base

设置路由前缀：

```typescript
export default {
  // 所有路由都会加上 /app 前缀
  base: '/app',
}
```

### publicPath

设置静态资源的公共路径：

```typescript
export default {
  // 部署到子目录时使用
  publicPath: '/my-app/',
  
  // 或使用 CDN
  publicPath: 'https://cdn.example.com/',
}
```

### output

设置构建输出目录：

```typescript
export default {
  output: 'dist',
}
```

## 路由配置

### routes

配置式路由配置：

```typescript
export default {
  routes: [
    { path: '/', component: 'index' },
    { path: '/about', component: 'about' },
    {
      path: '/users',
      component: 'users/_layout',
      routes: [
        { path: '/users', component: 'users/index' },
        { path: '/users/:id', component: 'users/[id]' },
      ],
    },
  ],
}
```

### exportStatic

配置静态化（SSG）：

```typescript
export default {
  exportStatic: {
    // 额外需要静态化的路径
    extraRoutePaths: ['/404'],
  },
}
```

## 代理配置

### proxy

配置开发服务器代理：

```typescript
export default {
  proxy: {
    '/api': {
      target: 'http://localhost:3000',
      changeOrigin: true,
      pathRewrite: { '^/api': '' },
    },
    '/api/v2': {
      target: 'http://localhost:4000',
      changeOrigin: true,
    },
  },
}
```

#### 代理配置项

| 配置项 | 类型 | 说明 |
|--------|------|------|
| target | string | 代理目标地址 |
| changeOrigin | boolean | 是否修改请求头中的 Origin |
| pathRewrite | object | 路径重写规则 |
| secure | boolean | 是否验证 SSL 证书 |
| ws | boolean | 是否代理 WebSocket |

## 主题配置

### theme

自定义主题变量：

```typescript
export default {
  theme: {
    '@primary-color': '#1890ff',
    '@border-radius-base': '4px',
    '@font-size-base': '14px',
  },
}
```

### lessLoader

配置 Less 加载器：

```typescript
export default {
  lessLoader: {
    modifyVars: {
      '@primary-color': '#1890ff',
    },
    javascriptEnabled: true,
  },
}
```

## CSS 配置

### cssLoader

配置 CSS 加载器：

```typescript
export default {
  cssLoader: {
    modules: {
      localIdentName: '[local]___[hash:base64:5]',
    },
  },
}
```

### styleLoader

配置样式加载器：

```typescript
export default {
  styleLoader: {},
}
```

### sassLoader

配置 Sass 加载器：

```typescript
export default {
  sassLoader: {},
}
```

## 构建配置

### 构建引擎选择

UmiJS 4.x 支持 Vite 和 Webpack 两种构建引擎：

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 使用 Vite 构建（推荐，速度更快）
  vite: {},
  
  // 或使用 Webpack（默认）
  // webpack: {},
})
```

### chainWebpack

自定义 Webpack 配置（仅在使用 Webpack 构建时有效）：

```typescript
import { defineConfig } from 'umi'

export default defineConfig({
  chainWebpack(config) {
    // 使用 webpack-chain 修改配置
    config.resolve.alias.set('@assets', '/src/assets')
    
    // 添加插件
    config.plugin('my-plugin').use(MyPlugin, [])
    
    return config
  },
})
```

### vite

自定义 Vite 配置（仅在使用 Vite 构建时有效）：

```typescript
import { defineConfig } from 'umi'

export default defineConfig({
  vite: {
    // Vite 配置
    server: {
      port: 3000,
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
          },
        },
      },
    },
  },
})
```

### define

定义全局常量：

```typescript
export default {
  define: {
    'process.env.API_URL': 'https://api.example.com',
    'process.env.APP_VERSION': '1.0.0',
  },
}
```

### extraBabelPlugins

添加额外的 Babel 插件：

```typescript
export default {
  extraBabelPlugins: [
    ['import', { libraryName: 'lodash', libraryDirectory: '', camel2DashComponentName: false }],
  ],
}
```

### extraBabelPresets

添加额外的 Babel 预设：

```typescript
export default {
  extraBabelPresets: [
    '@babel/preset-env',
  ],
}
```

## 开发配置

### port

设置开发服务器端口：

```typescript
export default {
  port: 3000,
}
```

### host

设置开发服务器主机：

```typescript
export default {
  host: '0.0.0.0',
}
```

### https

启用 HTTPS：

```typescript
export default {
  https: {
    key: 'path/to/key.pem',
    cert: 'path/to/cert.pem',
  },
}
```

### open

自动打开浏览器：

```typescript
export default {
  open: true,
}
```

## 代码分割

### codeSplitting

配置代码分割策略：

```typescript
export default {
  codeSplitting: {
    jsStrategy: 'granularChunks',
  },
}
```

### dynamicImport

配置动态导入：

```typescript
export default {
  dynamicImport: {
    loading: '@/components/Loading',
  },
}
```

## 优化配置

### terserOptions

配置代码压缩：

```typescript
export default {
  terserOptions: {
    compress: {
      drop_console: true,
      drop_debugger: true,
    },
  },
}
```

### hash

为文件名添加 hash：

```typescript
export default {
  hash: true,
}
```

### devtool

配置 Source Map：

```typescript
export default {
  // 开发环境
  devtool: 'source-map',
  
  // 生产环境
  devtool: false,
}
```

## 分析配置

### analyze

打包分析：

```typescript
export default {
  analyze: {
    analyzerMode: 'server',
    analyzerPort: 8888,
  },
}
```

运行 `ANALYZE=1 umi build` 可以查看打包结果。

## 类型配置

### tsLoader

配置 TypeScript 加载器：

```typescript
export default {
  tsLoader: {
    transpileOnly: true,
  },
}
```

### forkTSChecker

配置类型检查：

```typescript
export default {
  forkTSChecker: {
    enable: true,
  },
}
```

## Mock 配置

### mock

配置 Mock 服务：

```typescript
export default {
  mock: {
    // 排除不需要 Mock 的文件
    exclude: ['**/mock/not-mock.ts'],
  },
}
```

## 部署配置

### favicons

配置网站图标：

```typescript
export default {
  favicons: ['https://example.com/favicon.ico'],
}
```

### metas

配置 meta 标签：

```typescript
export default {
  metas: [
    { name: 'keywords', content: 'umi, react, frontend' },
    { name: 'description', content: '企业级前端框架' },
  ],
}
```

### title

配置页面标题：

```typescript
export default {
  title: '我的 UmiJS 应用',
}
```

### links

配置 link 标签：

```typescript
export default {
  links: [
    { rel: 'stylesheet', href: 'https://example.com/style.css' },
  ],
}
```

### scripts

配置 script 标签：

```typescript
export default {
  scripts: [
    'https://example.com/script.js',
  ],
}
```

## 完整配置示例

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 基础配置
  npmClient: 'npm',
  base: '/app',
  publicPath: '/my-app/',
  output: 'dist',
  
  // 构建引擎选择（UmiJS 4.x）
  vite: {},
  // 或使用 webpack: {},
  
  // 路由配置
  routes: [
    { path: '/', component: 'index' },
    { path: '/about', component: 'about' },
  ],
  
  // 代理配置
  proxy: {
    '/api': {
      target: 'http://localhost:3000',
      changeOrigin: true,
      pathRewrite: { '^/api': '' },
    },
  },
  
  // 主题配置
  theme: {
    '@primary-color': '#1890ff',
  },
  
  // 构建配置
  hash: true,
  devtool: 'source-map',
  
  // 开发配置
  port: 3000,
  open: true,
  
  // 页面配置
  title: '我的 UmiJS 应用',
  metas: [
    { name: 'keywords', content: 'umi, react, frontend' },
    { name: 'description', content: '企业级前端框架' },
  ],
  
  // UmiJS 4.x 插件配置（需要显式配置）
  model: {},
  antd: {},
  request: {},
  access: {},
  initialState: {},
  locale: {
    default: 'zh-CN',
    baseNavigator: true,
  },
  layout: {},
  mock: {},
})
```

## 环境变量

### .env 文件

在项目根目录创建 `.env` 文件：

```bash
# .env
PORT=3000
API_URL=https://api.example.com
```

### 使用环境变量

```typescript
export default {
  proxy: {
    '/api': {
      target: process.env.API_URL,
      changeOrigin: true,
    },
  },
}
```

## 配置优先级

1. 命令行参数（最高优先级）
2. `.umirc.ts` 或 `config/config.ts`
3. 默认配置（最低优先级）

## 最佳实践

1. **开发环境**启用 `devtool` 方便调试
2. **生产环境**启用 `hash` 和代码压缩
3. **使用代理**解决开发环境跨域问题
4. **配置主题**统一项目视觉风格
5. **添加 meta** 优化 SEO
6. **使用环境变量**管理不同环境的配置
7. **启用分析** 优化打包体积

::: tip 提示
- `.umirc.ts` 和 `config/config.ts` 只能存在一个
- 配置修改后需要重启开发服务器
- 使用 `defineConfig` 可以获得类型提示
- 环境变量可以通过 `.env` 文件管理
:::

::: danger 注意事项
- 配置项修改后可能需要重启开发服务器
- 代理配置仅在开发环境生效
- 生产环境不要开启 `devtool`，会暴露源码
- `publicPath` 配置错误会导致静态资源加载失败
- 配置文件中不能使用 CommonJS 语法
:::
