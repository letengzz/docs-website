# 配置SCSS

CSS 预处理器可以显著提升样式开发效率，支持变量、循环、嵌套、混合等高级特性，这是使用原生 CSS 无法实现的。

Vite 内置了对 `scss`、`sass`、`less`、`styl`和 `stylus`这些预处理器的支持，无需安装额外的 Vite 插件，只需安装相应的预处理器依赖即可。

## 安装依赖

SCSS 的依赖库为 Sass，安装为开发依赖：

```
pnpm add sass -D
```

## 样式文件组织

为了保持样式管理的清晰性和便捷性，咱们这里就只划分为三层：

- **settings**：样式变量的定义，如颜色值、尺寸、字体大小等基础变量。

  在 UI 设计中有一个很厉害的专业术语：设计令牌，即 Design Tokens。 这一层，也可以叫定义设计令牌。

- **base**：全局通用的定制化样式，如：

  - 覆盖 Element Plus、VXE Table 的默认样式

  - 设置 html、body 的样式

- **components**：自定义的组件的样式，每个组件自行维护，不需要抽取到公共目录中。

在 `src`中按照如下结构建立目录和文件：

```
src/
  |- assets/
      |- scss/
         |- base/
            |- index.scss
         |- settings/
            |- _color.scss
            |- _size.scss
            |- index.scss
         |- index.scss
```

## 实现 settings 层

依次实现 settings 层的三个文件：

1. 存放 SCSS 和 CSS 颜色变量：首先定义一系列 SCSS 变量，包括：品牌与状态色、文字、边框、背景颜色； 然后利用 SCSS 的可编程的特点生成不同色阶的 CSS 颜色变量；最后定义一套暗黑主题的变量值。

   - 使用 `@use "sass:color"`导入 sass 的颜色模块。

   - 通过 `@each`循环批量生成 CSS 变量，减少重复代码。

   - 使用 `color.mix()`函数生成不同亮度的颜色色阶。

   ```scss [scss/settings/_color.scss]
   @use 'sass:color';
   
   // 品牌与状态色
   $wm-color-primary: #1c9399;
   $wm-color-success: #3dbe7d;
   $wm-color-warning: #ffb74d;
   $wm-color-danger: #f1524c;
   $wm-color-info: #5e7ce0;
   
   // 中性色 - 文字
   $wm-color-text-primary: #303133;
   $wm-color-text-regular: #606266;
   $wm-color-text-secondary: #909399;
   $wm-color-text-placeholder: #a8abb2;
   $wm-color-text-disabled: #c0c4cc;
   
   // 中性色 - 边框
   $wm-border-color-base: #dcdfe6;
   $wm-border-color-light: #e4e7ed;
   
   // 中性色 - 背景
   $wm-bg-color-page: #f5f7fa;
   $wm-bg-color-base: #ffffff;
   
   // 默认主题 白天模式
   :root {
     // 品牌/状态色及其色阶
     @each $type, $color in (primary, $wm-color-primary), (success, $wm-color-success),
       (danger, $wm-color-danger), (warning, $wm-color-warning), (info, $wm-color-info)
     {
       --wm-color-#{$type}: #{$color};
   
       // 生成浅色变体 (混合白色)
       @each $i in (1, 2, 3, 5, 7, 8, 9) {
         --wm-color-#{$type}-light-#{$i}: #{color.mix(#fff, $color, $i * 10%)};
       }
   
       // 生成深色变体 (混合黑色)
       @each $i in (1, 2) {
         --wm-color-#{$type}-dark-#{$i}: #{color.mix(#000, $color, $i * 10%)};
       }
     }
   
     // 文字
     --wm-color-text-primary: #{$wm-color-text-primary};
     --wm-color-text-regular: #{$wm-color-text-regular};
     --wm-color-text-secondary: #{$wm-color-text-secondary};
     --wm-color-text-placeholder: #{$wm-color-text-placeholder};
   
     // 边框
     --wm-border-color-base: #{$wm-border-color-base};
     --wm-border-color-light: #{$wm-border-color-light};
   
     // 背景
     --wm-bg-color-base: #{$wm-bg-color-base};
     --wm-bg-color-page: #{$wm-bg-color-page};
   }
   
   // 深色主题覆盖
   [data-theme='dark'] {
     --wm-color-text-primary: rgba(255, 255, 255, 0.95);
     --wm-color-text-regular: rgba(255, 255, 255, 0.75);
     --wm-color-text-secondary: rgba(255, 255, 255, 0.55);
     --wm-color-text-placeholder: rgba(255, 255, 255, 0.35);
   
     --wm-bg-color-page: #121212;
     --wm-bg-color-base: #1a1a1a;
     --wm-border-color-base: rgba(255, 255, 255, 0.12);
   }
   ```

:::danger

Sass 升级后 API 有变化：

1. 不再推荐使用 `@import`，而是使用 `@use`导入模块
2. 颜色混合函数从 `mix()`变为 `color.mix()`

:::

启动服务时的控制台警告信息应认真处理，它们通常提示潜在问题或过时用法。千万不要看见警告信息，觉得不是报错，就不处理。

2. 存放 SCSS 和 CSS 尺寸相关变量：

   ```scss [scss/settings/_size.scss]
   // 间距系统 (以8px为基准)
   $wm-spacing-base: 8px;
   
   :root {
     --wm-spacing-xs: #{$wm-spacing-base * 0.5}; // 4px
     --wm-spacing-sm: #{$wm-spacing-base * 1}; // 8px
     --wm-spacing-md: #{$wm-spacing-base * 1.5}; // 12px
     --wm-spacing-lg: #{$wm-spacing-base * 2}; // 16px
     --wm-spacing-xl: #{$wm-spacing-base * 3}; // 24px
     --wm-spacing-2xl: #{$wm-spacing-base * 4}; // 32px
   }
   
   // ===== 字体系统 =====
   :root {
     --wm-font-size-xs: 12px;
     --wm-font-size-sm: 14px;
     --wm-font-size-base: 16px;
     --wm-font-size-lg: 18px;
     --wm-font-size-xl: 20px;
     --wm-font-size-2xl: 24px;
     --wm-font-size-3xl: 30px;
   
     --wm-font-weight-normal: 400;
     --wm-font-weight-medium: 500;
     --wm-font-weight-semibold: 600;
   
     --wm-line-height-tight: 1.25;
     --wm-line-height-normal: 1.5;
   }
   
   // ===== 圆角 =====
   :root {
     --wm-border-radius-sm: 4px;
     --wm-border-radius-base: 6px;
     --wm-border-radius-lg: 8px;
     --wm-border-radius-full: 9999px;
   }
   ```

3. 导出前两个文件，作为 settings 的入口：

   ```scss [scss/settings/index.scss]
   @use './color';
   @use './size';
   ```

## 实现 base 层

由于目前没有引入第三方组件库，现在无需设置第三方组件库样式。

故 base 层目录只有一个入口文件：设置 body 样式

```scss [scss/base/index.scss]
body {
  margin: 0;
  background-color: var(--wm-bg-color-page);
  color: var(--wm-color-text-primary);
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
```

若后续需要覆盖如 Element Plus 的全局样式时，在这个目录添加文件，并在 index.scss 中导入即可。

## 统一样式入口

全局样式入口文件，分别导入 settings 和 base：

```scss [assets/scss/index.scss]
// 导入变量文件
@use './settings';
@use './base';
```

## 统一资源管理

为了保持 `main.ts`的简洁，创建一个专门的资源管理模块，统一处理所有静态资源的导入：

1. 在 `src`目录下创建 `plugins`目录。

2. 在该目录中创建 `assets.ts`文件：

   ```typescript [src/plugins/assets.ts]
   import'@/assets/scss/index.scss'
   
   /**
    * 空方法，通过调用该方法，导入上面 import 中的样式和资源
    */
   export const useAssets = () => {}
   ```

在 `main.ts`中调用：

```typescript [main.ts]
// ...
import { useAssets } from '@/plugins/assets'

// ...

useAssets()

// ...
```

