# 配置组件自动注册

`unplugin-vue-components`插件可以实现组件的自动注册。

GitHub 地址：https://github.com/unplugin/unplugin-vue-components

## 安装依赖

安装开发依赖：

```shell
pnpm add unplugin-vue-components -D
```

## 配置 vite 插件

在 `vite.config.ts`中配置该插件：该插件默认会自动注册 `src/components`目录及子目录下的组件。
关于该插件的更多配置项，自己去查看 GitHub 地址，如 `directoryAsNamespace`、`collapseSamePrefixes`等配置项。

```typescript [vite.config.ts]
// ...
import Components from 'unplugin-vue-components/vite'

export default defineConfig({
  plugins: [
    // ...
    Components({ // [!code focus] [!code ++]
      deep: true, // [!code focus] [!code ++]
      directoryAsNamespace: false, // [!code focus] [!code ++]
      resolvers: [  // [!code focus] [!code ++]
      ], // [!code focus] [!code ++]
      dts: './types/components.d.ts' // 生成组件类型声明文件的路径 // [!code focus] [!code ++]
    }) // [!code focus] [!code ++]
  ],
  // ...
})
```

将.gitignore添加：

```tex [.gitignore]
types/components.d.ts
```

