# 配置VueUse工具集

`vueuse`是一个非常实用的 Vue 组合式 API 工具集，提供了大量的 hooks。

vueuse 官网：https://v4-11-2.vueuse.org/

安装 VueUse：

```shell
pnpm add @vueuse/core
```

将 `vueuse`集成到自动导入中，后面在组件中使用到其提供的 hooks 时，也不需要 import，直接使用就行。

在 `vite.config.ts`文件中 `AutoImport`的 `imports`数组中添加 vueuse，如下：

```typescript [vite.config.ts]
// ...
export default defineConfig({
  plugins: [
    // ...
    AutoImport({
      // ...
      imports: ['vue', VueRouterAutoImports, 'pinia', '@vueuse/core', 'vue-i18n'],
    }),
    // ...
  ],
  // ...
})
```