# 配置自动导入

unplugin-auto-import，是一款强大的自动导入插件。集成该插件后，在 Vue 组件中使用相关 API 时，将无需手动编写 `import`语句。

GitHub 地址：https://github.com/unplugin/unplugin-auto-import

## 安装依赖

安装依赖：

```shell
pnpm add unplugin-auto-import -D
```

## 配置 vite 插件

在 `vite.config.ts`中配置该插件。在配置该插件时，默认导入如下库：vue、vue-router、pinia。 由于集成了自动路由 `unplugin-vue-router`，故默认导入路由也要修改为自动路由。

vite.config.ts配置：

```typescript [vite.config.ts]
// ...
// 自动引入注册
import AutoImport from 'unplugin-auto-import/vite' // [!code focus] [!code ++]
import { VueRouterAutoImports } from 'unplugin-vue-router' // [!code focus] [!code ++]

// https://vite.dev/config/
export default defineConfig({
    // vite 配置
    // ...
    plugins: [
      // ...
      AutoImport({ // [!code focus] [!code ++]
        include: [  // [!code focus] [!code ++]
          /\.[tj]sx?$/, // .ts, .tsx, .js, .jsx  // [!code focus] [!code ++]
          /\.vue$/,  // [!code focus] [!code ++]
          /\.vue\?vue/, // .vue  // [!code focus] [!code ++]
          /\.md$/, // .md  // [!code focus] [!code ++]
        ], // [!code focus] [!code ++]
        resolvers: [], // [!code focus] [!code ++]
        imports: ['vue', 'pinia',VueRouterAutoImports], // [!code focus] [!code ++]
        dts: './types/auto-imports.d.ts', // [!code focus] [!code ++]
        dirs: ['src/api/backend/**/*.ts', 'src/utils/**/*.ts'], // 自动导入项目中自定义的API和工具函数  // [!code focus] [!code ++]
        // eslint 报错解决：'ref' is not defined  // [!code focus] [!code ++]
        // eslintrc: { // [!code focus] [!code ++]
          // [!code focus] [!code ++]
          // 默认 false, true 启用生成。生成一次就可以，避免每次工程启动都生成，一旦生成配置文件之后，最好把 enable 关掉，即改成 false。  // [!code focus] [!code ++]
          // enabled: true,  // [!code focus] [!code ++]
          // 否则这个文件每次会在重新加载的时候重新生成，这会导致 eslint 有时会找不到这个文件。当需要更新配置文件的时候，再重新打开  // [!code focus] [!code ++]
          // filepath: './.eslintrc-auto-import.json' // 默认就是 ./.eslintrc-auto-import.json  // [!code focus] [!code ++]
          // globalsPropValue: true // 默认 true  // [!code focus] [!code ++]
        // }, // [!code focus] [!code ++]
      }), // [!code focus] [!code ++]
    ],
    // ...
})
```

将.gitignore添加：

```tex [.gitignore]
types/auto-imports.d.ts
```

